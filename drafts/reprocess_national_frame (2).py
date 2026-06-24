"""
National-Frame Reprocessing: External Flows with National Deciles
=================================================================

This script extends the cascade analysis by:
  1. Aggregating IMD 2010 to ALL England MSOAs (not just London)
  2. Assigning wealth deciles on the national distribution
  3. Including London ↔ external flows in the cascade computation
  4. Comparing results against the London-relative baseline

The aggregation strategy (population-weighted mean of LSOA IMD scores,
then re-rank at MSOA level) is identical to the main preprocessing
notebook. The only difference is scope: national instead of London-only.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date
from scipy import stats

# ══════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════
from pyprojroot import here
ROOT = here()
DATA_DIR = ROOT / 'data'
OUTPUT_DIR = ROOT / 'outputs'
OUTPUT_DIR.mkdir(exist_ok=True)

# Input files (same as main preprocessing)
imd_2010_path       = DATA_DIR / 'imd_2010.xls'
census_od_2021_path = DATA_DIR / 'census_od_2021_msoa.csv'
census_od_2011_path = DATA_DIR / 'census_od_2011_oa.csv'
lookup_path         = DATA_DIR / 'NSPCL_NOV22_UK_LU.csv'
msoa_lookup_path    = DATA_DIR / 'msoa_2011_to_2021_lookup.csv'
existing_path       = DATA_DIR / 'msoa_cascade_features_enriched_20260616.csv'

# NEW: all-England KS101 population file
ks101_allengland_path = DATA_DIR / 'ks101ew_lsoa_2011_allengland.csv'

# Synthetic code for all non-London areas
EXTERNAL_CODE = 'EXT_OUTSIDE'

# IMD 2010 column names
IMD_2010_LSOA_COL  = 'LSOA CODE'
IMD_2010_SCORE_COL = 'IMD SCORE'


# ══════════════════════════════════════════════════════════════════════
# 1. LOAD RAW DATA
# ══════════════════════════════════════════════════════════════════════
print('=' * 70)
print('1. Loading raw data')
print('=' * 70)

# ---- IMD 2010 (LSOA level, all England) ----
imd_2010 = pd.read_excel(imd_2010_path, sheet_name='IMD 2010')
imd_2010.columns = imd_2010.columns.str.strip()
print(f'IMD 2010: {len(imd_2010)} LSOAs')

# ---- KS101EW population (all England & Wales LSOAs) ----
ks101 = pd.read_csv(ks101_allengland_path)
# Detect LSOA code column: find column where values match E01/W01 pattern
_ks_code_col = next(
    c for c in ks101.columns
    if ks101[c].astype(str).str.match(r'^[EW]01\d{6}$').mean() > 0.9
)
_ks_pop_col = next(c for c in ks101.columns if 'all usual residents' in c.lower())
lsoa_pop = (ks101[[_ks_code_col, _ks_pop_col]]
            .rename(columns={_ks_code_col: 'lsoa11cd', _ks_pop_col: 'pop'}))
lsoa_pop['pop'] = pd.to_numeric(lsoa_pop['pop'], errors='coerce').fillna(0)
print(f'KS101EW: {len(lsoa_pop)} LSOAs, total pop = {lsoa_pop["pop"].sum():,.0f}')

# ---- NSPCL postcode lookup (LSOA → MSOA mapping) ----
nspcl = pd.read_csv(lookup_path, encoding='ISO-8859-1', low_memory=False)
lsoa_to_msoa = nspcl[['lsoa11cd', 'msoa11cd']].drop_duplicates().dropna()
oa_to_msoa = nspcl[['oa11cd', 'msoa11cd']].drop_duplicates().dropna()
oa_to_msoa_dict = dict(zip(oa_to_msoa['oa11cd'], oa_to_msoa['msoa11cd']))
print(f'LSOA→MSOA: {len(lsoa_to_msoa)} | OA→MSOA: {len(oa_to_msoa_dict):,}')

# ---- MSOA 2021→2011 correspondence ----
msoa_11_21 = pd.read_csv(msoa_lookup_path)
msoa_11_21.columns = msoa_11_21.columns.str.strip().str.lower()
unchanged = msoa_11_21[msoa_11_21['msoa11cd'] == msoa_11_21['msoa21cd']]
msoa21_to_11 = dict(zip(unchanged['msoa21cd'], unchanged['msoa11cd']))
print(f'MSOA 2021→2011 (1:1 only): {len(msoa21_to_11)}')

# ---- Existing London-only results (for comparison at the end) ----
existing = pd.read_csv(existing_path)
london_msoas = set(existing['msoa11cd'].unique())
print(f'London analysis MSOAs: {len(london_msoas)}')


# ══════════════════════════════════════════════════════════════════════
# 2. NATIONAL IMD AGGREGATION: LSOA → MSOA (all England)
#
#    Same logic as the main preprocessing:
#    - Population-weighted mean of LSOA IMD scores per MSOA
#    - Re-rank MSOAs on the aggregated score
#    - Assign deciles via qcut on the national distribution
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('2. Aggregating IMD 2010 to MSOA level (all England)')
print('=' * 70)

# ---- 2a. Join IMD scores → MSOA geography → population weights ----
imd_lsoa = imd_2010[[IMD_2010_LSOA_COL, IMD_2010_SCORE_COL]].rename(
    columns={IMD_2010_LSOA_COL: 'lsoa11cd', IMD_2010_SCORE_COL: 'imd_score'})

# LSOA → MSOA
imd_with_msoa = pd.merge(imd_lsoa, lsoa_to_msoa, on='lsoa11cd', how='inner')
print(f'IMD LSOAs matched to MSOA: {len(imd_with_msoa)} / {len(imd_lsoa)}')

# Add population weights
imd_with_msoa = pd.merge(imd_with_msoa, lsoa_pop, on='lsoa11cd', how='left')
imd_with_msoa['pop'] = imd_with_msoa['pop'].fillna(0)

# ---- 2b. Population-weighted mean per MSOA ----
# (Same fallback as main notebook: if all weights are zero, use simple mean)
def pop_weighted_mean(group):
    total_pop = group['pop'].sum()
    if total_pop > 0:
        return np.average(group['imd_score'], weights=group['pop'])
    else:
        return group['imd_score'].mean()

msoa_imd = (imd_with_msoa
            .groupby('msoa11cd')
            .apply(pop_weighted_mean, include_groups=False)
            .reset_index(name='IMD_2010_national'))

print(f'MSOAs with aggregated IMD: {len(msoa_imd)}')
print(f'  London MSOAs:     {msoa_imd["msoa11cd"].isin(london_msoas).sum()}')
print(f'  Non-London MSOAs: {(~msoa_imd["msoa11cd"].isin(london_msoas)).sum()}')

# ---- 2c. Assign national wealth deciles ----
# qcut splits into 10 bins by score. Higher IMD score = more deprived.
# pd.qcut with labels=False gives bin 0 = lowest scores = LEAST deprived.
# We want Decile 1 = most deprived, so: Decile = 11 - (bin + 1)
msoa_imd['Wealth_Decile_National'] = (
    11 - (pd.qcut(msoa_imd['IMD_2010_national'], 10, labels=False) + 1)
)

# Verify direction: D1 should have highest IMD scores (most deprived)
d1_score = msoa_imd.loc[msoa_imd['Wealth_Decile_National'] == 1,
                         'IMD_2010_national'].mean()
d10_score = msoa_imd.loc[msoa_imd['Wealth_Decile_National'] == 10,
                          'IMD_2010_national'].mean()
assert d1_score > d10_score, \
    f'Decile direction wrong: D1 mean={d1_score:.1f}, D10 mean={d10_score:.1f}'
print(f'\nDecile direction verified: D1 (most deprived, mean={d1_score:.1f}) > '
      f'D10 (least deprived, mean={d10_score:.1f})')

# ---- 2d. Summary: national decile composition ----
print(f'\nNational decile distribution:')
print(f'{"Decile":>6s} {"N_total":>8s} {"N_London":>9s} {"Mean IMD":>9s}')
for d in range(1, 11):
    mask = msoa_imd['Wealth_Decile_National'] == d
    n_total = mask.sum()
    n_london = (mask & msoa_imd['msoa11cd'].isin(london_msoas)).sum()
    mean_imd = msoa_imd.loc[mask, 'IMD_2010_national'].mean()
    print(f'  D{d:>2d}   {n_total:>7d}  {n_london:>8d}  {mean_imd:>9.2f}')

# ---- 2e. External MSOA decile ----
# Population-weighted mean decile of all non-London MSOAs
non_london_imd = msoa_imd[~msoa_imd['msoa11cd'].isin(london_msoas)].copy()

# Get MSOA-level population for weighting
msoa_pop = (imd_with_msoa.groupby('msoa11cd')['pop'].sum()
            .reset_index(name='msoa_pop'))
non_london_imd = non_london_imd.merge(msoa_pop, on='msoa11cd', how='left')
non_london_imd['msoa_pop'] = non_london_imd['msoa_pop'].fillna(0)

# Safety check
total_ext_pop = non_london_imd['msoa_pop'].sum()
print(f'\nExternal MSOA calculation:')
print(f'  Non-London MSOAs: {len(non_london_imd)}, total pop: {total_ext_pop:,.0f}')
assert total_ext_pop > 0, 'External population is zero — check KS101 file coverage'

ext_weighted_decile = np.average(
    non_london_imd['Wealth_Decile_National'],
    weights=non_london_imd['msoa_pop'])
ext_decile = int(round(ext_weighted_decile))
print(f'  Weighted mean decile: {ext_weighted_decile:.2f} → assigned D{ext_decile}')

# ---- 2f. Build wealth mapping (all MSOAs + external) ----
wealth_national = dict(zip(msoa_imd['msoa11cd'],
                            msoa_imd['Wealth_Decile_National']))
wealth_national[EXTERNAL_CODE] = ext_decile

# ---- 2g. Compare national vs London-relative deciles ----
print(f'\nLondon MSOA decile comparison (London-relative vs National):')
london_comparison = msoa_imd[msoa_imd['msoa11cd'].isin(london_msoas)].merge(
    existing[['msoa11cd', 'Wealth_Decile']], on='msoa11cd')

ct = pd.crosstab(london_comparison['Wealth_Decile'],
                 london_comparison['Wealth_Decile_National'], margins=True)
print(ct.to_string())

rho, p = stats.spearmanr(london_comparison['Wealth_Decile'],
                          london_comparison['Wealth_Decile_National'])
print(f'\nSpearman ρ = {rho:.4f}, p = {p:.2e}')


# ══════════════════════════════════════════════════════════════════════
# 3. FILTER OD DATA: LONDON-TOUCHING FLOWS
#
#    Keep flows where at least one endpoint is a London MSOA.
#    Non-London endpoints → recode as EXTERNAL_CODE.
#    Exclude intra-MSOA moves.
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('3. Filtering OD data to London-touching flows')
print('=' * 70)

# ---- 3a. 2021 Census OD (MSOA-level, 2021 codes) ----
print('\n--- 2021 ---')
ORIGIN_COL_2021 = 'Migrant MSOA one year ago code'
DEST_COL_2021   = 'Middle layer Super Output Areas code'

od_2021 = pd.read_csv(census_od_2021_path)
od_2021[ORIGIN_COL_2021] = od_2021[ORIGIN_COL_2021].astype(str).str.strip()
od_2021[DEST_COL_2021]   = od_2021[DEST_COL_2021].astype(str).str.strip()

# Detect count column
count_cols = [c for c in od_2021.columns
              if 'observation' in c.lower() or 'count' in c.lower()]
COUNT_COL_2021 = count_cols[0] if count_cols else od_2021.columns[-1]
print(f'Count column: {COUNT_COL_2021!r}')
print(f'Raw records: {len(od_2021):,}')

# Harmonise 2021→2011 codes
od_2021['origin_msoa11'] = od_2021[ORIGIN_COL_2021].map(msoa21_to_11)
od_2021['dest_msoa11']   = od_2021[DEST_COL_2021].map(msoa21_to_11)

# Classify & filter
od_2021['o_ldn'] = od_2021['origin_msoa11'].isin(london_msoas)
od_2021['d_ldn'] = od_2021['dest_msoa11'].isin(london_msoas)
lt_21 = od_2021[od_2021['o_ldn'] | od_2021['d_ldn']].copy()

# Recode non-London → EXTERNAL
lt_21.loc[~lt_21['o_ldn'], 'origin_msoa11'] = EXTERNAL_CODE
lt_21.loc[~lt_21['d_ldn'], 'dest_msoa11']   = EXTERNAL_CODE

# Drop intra-MSOA
lt_21 = lt_21[lt_21['origin_msoa11'] != lt_21['dest_msoa11']]

# Aggregate
flows_21 = (lt_21.groupby(['origin_msoa11', 'dest_msoa11'])[COUNT_COL_2021]
            .sum().reset_index().rename(columns={COUNT_COL_2021: 'count'}))

_i = flows_21[(flows_21['origin_msoa11'] != EXTERNAL_CODE) &
              (flows_21['dest_msoa11'] != EXTERNAL_CODE)]
_f = flows_21[flows_21['origin_msoa11'] == EXTERNAL_CODE]
_t = flows_21[flows_21['dest_msoa11'] == EXTERNAL_CODE]
print(f'Internal:  {len(_i):>7,} records  {_i["count"].sum():>10,.0f} persons')
print(f'Ext→Ldn:   {len(_f):>7,} records  {_f["count"].sum():>10,.0f} persons')
print(f'Ldn→Ext:   {len(_t):>7,} records  {_t["count"].sum():>10,.0f} persons')

# ---- 3b. 2011 Census OD (OA-level) ----
print('\n--- 2011 ---')
od_2011 = pd.read_csv(
    census_od_2011_path, header=None,
    names=['dest_oa', 'origin_oa', 'persons'],
    dtype={'dest_oa': str, 'origin_oa': str, 'persons': int})
od_2011['origin_oa'] = od_2011['origin_oa'].str.strip()
od_2011['dest_oa']   = od_2011['dest_oa'].str.strip()
print(f'Raw OA records: {len(od_2011):,}')

# OA → MSOA
od_2011['origin_msoa11'] = od_2011['origin_oa'].map(oa_to_msoa_dict)
od_2011['dest_msoa11']   = od_2011['dest_oa'].map(oa_to_msoa_dict)

# Classify & filter
od_2011['o_ldn'] = od_2011['origin_msoa11'].isin(london_msoas)
od_2011['d_ldn'] = od_2011['dest_msoa11'].isin(london_msoas)
lt_11 = od_2011[od_2011['o_ldn'] | od_2011['d_ldn']].copy()

# Recode non-London → EXTERNAL
lt_11.loc[~lt_11['o_ldn'], 'origin_msoa11'] = EXTERNAL_CODE
lt_11.loc[~lt_11['d_ldn'], 'dest_msoa11']   = EXTERNAL_CODE

# Drop intra-MSOA
lt_11 = lt_11[lt_11['origin_msoa11'] != lt_11['dest_msoa11']]

# Aggregate to MSOA level
flows_11 = (lt_11.groupby(['origin_msoa11', 'dest_msoa11'])['persons']
            .sum().reset_index().rename(columns={'persons': 'count'}))

_i = flows_11[(flows_11['origin_msoa11'] != EXTERNAL_CODE) &
              (flows_11['dest_msoa11'] != EXTERNAL_CODE)]
_f = flows_11[flows_11['origin_msoa11'] == EXTERNAL_CODE]
_t = flows_11[flows_11['dest_msoa11'] == EXTERNAL_CODE]
print(f'Internal:  {len(_i):>7,} records  {_i["count"].sum():>10,.0f} persons')
print(f'Ext→Ldn:   {len(_f):>7,} records  {_f["count"].sum():>10,.0f} persons')
print(f'Ldn→Ext:   {len(_t):>7,} records  {_t["count"].sum():>10,.0f} persons')


# ══════════════════════════════════════════════════════════════════════
# 4. COMPUTE CASCADE METRICS (national deciles, with external flows)
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('4. Computing cascade metrics — national frame')
print('=' * 70)

def compute_cascade(flow_df, wealth_map, year_label):
    """
    Per-London-MSOA cascade & counter-cascade metrics.
    Identical formulas to the main preprocessing, just different
    wealth_map (national deciles) and flow table (includes external).
    """
    df = flow_df.copy()
    df['o_dec'] = df['origin_msoa11'].map(wealth_map)
    df['d_dec'] = df['dest_msoa11'].map(wealth_map)

    # Drop unmapped
    before = len(df)
    df = df.dropna(subset=['o_dec', 'd_dec'])
    dropped = before - len(df)
    if dropped:
        print(f'  ⚠ {dropped} records dropped (unmapped decile)')
    df['o_dec'] = df['o_dec'].astype(int)
    df['d_dec'] = df['d_dec'].astype(int)

    # Summary
    total = df['count'].sum()
    up   = df.loc[df['d_dec'] > df['o_dec'], 'count'].sum()
    down = df.loc[df['d_dec'] < df['o_dec'], 'count'].sum()
    lat  = df.loc[df['d_dec'] == df['o_dec'], 'count'].sum()
    print(f'\n  {year_label}:')
    print(f'    Total:   {total:>10,.0f}')
    print(f'    Upward:  {up:>10,.0f} ({up/total*100:.1f}%)')
    print(f'    Down:    {down:>10,.0f} ({down/total*100:.1f}%)')
    print(f'    Lateral: {lat:>10,.0f} ({lat/total*100:.1f}%)')

    # ---- Per-London-MSOA metrics ----
    idx = sorted(london_msoas)

    # Cascade: wealthier in, poorer out
    inflow_w  = (df[df['o_dec'] > df['d_dec']].groupby('dest_msoa11')['count']
                 .sum().reindex(idx, fill_value=0))
    outflow_p = (df[df['d_dec'] < df['o_dec']].groupby('origin_msoa11')['count']
                 .sum().reindex(idx, fill_value=0))

    # Counter-cascade: wealthier out, poorer in
    outflow_w = (df[df['d_dec'] > df['o_dec']].groupby('origin_msoa11')['count']
                 .sum().reindex(idx, fill_value=0))
    inflow_p  = (df[df['o_dec'] < df['d_dec']].groupby('dest_msoa11')['count']
                 .sum().reindex(idx, fill_value=0))

    # Totals
    total_in  = df.groupby('dest_msoa11')['count'].sum().reindex(idx, fill_value=0)
    total_out = df.groupby('origin_msoa11')['count'].sum().reindex(idx, fill_value=0)

    # External-specific
    ext_in  = (df[df['origin_msoa11'] == EXTERNAL_CODE]
               .groupby('dest_msoa11')['count'].sum().reindex(idx, fill_value=0))
    ext_out = (df[df['dest_msoa11'] == EXTERNAL_CODE]
               .groupby('origin_msoa11')['count'].sum().reindex(idx, fill_value=0))

    # Assemble
    r = pd.DataFrame({'msoa11cd': idx})
    r = r.set_index('msoa11cd')
    r['Inflow_Wealthier']  = inflow_w.values
    r['Outflow_Poorer']    = outflow_p.values
    r['Outflow_Wealthier'] = outflow_w.values
    r['Inflow_Poorer']     = inflow_p.values
    r['Total_Inflow']      = total_in.values
    r['Total_Outflow']     = total_out.values
    r['Ext_Inflow']        = ext_in.values
    r['Ext_Outflow']       = ext_out.values

    # Derived metrics (same formulas as main notebook)
    r['Total_Migration'] = r['Total_Inflow'] + r['Total_Outflow']
    r['CFI_Churn']   = r['Inflow_Wealthier'] + r['Outflow_Poorer']
    r['CFI_Rate']    = np.where(r['Total_Migration'] > 0,
        (r['Inflow_Wealthier'] * r['Outflow_Poorer']) / r['Total_Migration'], 0)
    r['Net_Cascade'] = r['Inflow_Wealthier'] - r['Outflow_Poorer']
    r['Pct_Inflow_Wealthier'] = np.where(r['Total_Inflow'] > 0,
        r['Inflow_Wealthier'] / r['Total_Inflow'] * 100, 0)

    r['Counter_Churn'] = r['Outflow_Wealthier'] + r['Inflow_Poorer']
    r['Counter_Rate']  = np.where(r['Total_Migration'] > 0,
        (r['Outflow_Wealthier'] * r['Inflow_Poorer']) / r['Total_Migration'], 0)
    r['Net_Counter']   = r['Outflow_Wealthier'] - r['Inflow_Poorer']

    # Cascade Dominance
    total_cross = r['CFI_Churn'] + r['Counter_Churn']
    r['Cascade_Dominance'] = np.where(total_cross > 0,
        r['CFI_Churn'] / total_cross, 0.5)

    r['Ext_Net'] = r['Ext_Inflow'] - r['Ext_Outflow']
    return r


# Compute both periods
print('\n--- 2011 ---')
nat_11 = compute_cascade(flows_11, wealth_national, '2011 national frame')
print('\n--- 2021 ---')
nat_21 = compute_cascade(flows_21, wealth_national, '2021 national frame')

# Add _nat suffix + year suffix
nat_11.columns = [f'{c}_nat_11' for c in nat_11.columns]
nat_21.columns = [f'{c}_nat_21' for c in nat_21.columns]


# ══════════════════════════════════════════════════════════════════════
# 5. MERGE & COMPARE
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('5. Merging and comparing London-only vs national frame')
print('=' * 70)

# Add national decile
nat_deciles = msoa_imd[msoa_imd['msoa11cd'].isin(london_msoas)][
    ['msoa11cd', 'Wealth_Decile_National']]

result = existing.merge(nat_deciles, on='msoa11cd', how='left')
result = result.merge(nat_11, left_on='msoa11cd', right_index=True, how='left')
result = result.merge(nat_21, left_on='msoa11cd', right_index=True, how='left')
print(f'Final shape: {result.shape}')

# ---- Key comparison: Cascade Dominance ----
print('\n' + '-' * 50)
print('CASCADE DOMINANCE COMPARISON')
print('-' * 50)

for yr in ['11', '21']:
    dom_ldn = f'Cascade_Dominance_{yr}'
    dom_nat = f'Cascade_Dominance_nat_{yr}'

    if dom_ldn in result.columns and dom_nat in result.columns:
        ldn_mean   = result[dom_ldn].mean()
        nat_mean   = result[dom_nat].mean()
        ldn_below  = (result[dom_ldn] < 0.5).mean() * 100
        nat_below  = (result[dom_nat] < 0.5).mean() * 100

        print(f'\n20{yr}:')
        print(f'  London-only:   mean = {ldn_mean:.4f}  '
              f'({ldn_below:.1f}% of MSOAs < 0.5)')
        print(f'  National+ext:  mean = {nat_mean:.4f}  '
              f'({nat_below:.1f}% of MSOAs < 0.5)')
        print(f'  Shift:         {nat_mean - ldn_mean:+.4f}')

        rho, p = stats.spearmanr(result[dom_ldn], result[dom_nat])
        print(f'  Spearman ρ:    {rho:.4f} (p={p:.2e})')

# ---- CFI Churn comparison ----
print('\n' + '-' * 50)
print('CFI CHURN COMPARISON')
print('-' * 50)
for yr in ['11', '21']:
    c_ldn = f'CFI_Churn_{yr}'
    c_nat = f'CFI_Churn_nat_{yr}'
    if c_ldn in result.columns and c_nat in result.columns:
        print(f'\n20{yr}:')
        print(f'  London-only mean: {result[c_ldn].mean():>10.1f}')
        print(f'  National mean:    {result[c_nat].mean():>10.1f}')
        print(f'  Increase:         {result[c_nat].mean() - result[c_ldn].mean():>+10.1f}')

# ---- External flow volumes ----
print('\n' + '-' * 50)
print('EXTERNAL FLOW VOLUMES')
print('-' * 50)
for yr in ['11', '21']:
    ei = f'Ext_Inflow_nat_{yr}'
    eo = f'Ext_Outflow_nat_{yr}'
    en = f'Ext_Net_nat_{yr}'
    if ei in result.columns:
        print(f'\n20{yr}:')
        print(f'  Mean inflow from outside:  {result[ei].mean():>8.1f}')
        print(f'  Mean outflow to outside:   {result[eo].mean():>8.1f}')
        print(f'  Mean net external:         {result[en].mean():>+8.1f}')


# ══════════════════════════════════════════════════════════════════════
# 6. EXPORT
# ══════════════════════════════════════════════════════════════════════
today = date.today().strftime('%Y%m%d')
out_path = OUTPUT_DIR / f'msoa_cascade_national_frame_{today}.csv'
result.to_csv(out_path, index=False)
print(f'\n✓ Saved: {out_path}')
print(f'  Shape: {result.shape}')
