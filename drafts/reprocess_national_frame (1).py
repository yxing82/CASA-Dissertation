"""
External Flows Analysis — Option B: National Deprivation Frame
===============================================================

Purpose:
    Extend the cascade analysis to include flows between London and the rest
    of England by rebuilding the deprivation hierarchy on a NATIONAL frame.
    All ~6,800 England MSOAs are ranked and assigned to deciles based on
    their IMD 2010 scores. Non-London areas are then collapsed into a single
    synthetic MSOA ('EXT_OUTSIDE') whose decile is the population-weighted
    average of all non-London MSOAs' nationally-assigned deciles.

    This allows external flows to be classified as "wealthier inflow" or
    "poorer outflow" within a consistent national hierarchy, testing whether
    including London↔external flows changes the observed cascade/counter-
    cascade balance.

Design:
    ┌──────────────────────────────────────────────────────────────────────┐
    │  Main analysis (existing)         │  This extension (Option B)      │
    │───────────────────────────────────│─────────────────────────────────│
    │  Deciles: 983 London MSOAs only   │  Deciles: ~6,800 England MSOAs  │
    │  Flows:   London ↔ London         │  Flows:   London ↔ anywhere     │
    │  Frame:   London-relative         │  Frame:   National-relative     │
    │  Purpose: Core analysis           │  Purpose: Sensitivity/extension │
    └──────────────────────────────────────────────────────────────────────┘

    The main London-relative analysis remains the primary strategy.
    This script produces a PARALLEL set of metrics (suffix '_nat') that
    can be compared against the London-relative results to assess whether
    external flows change the cascade/counter-cascade balance.

Inputs (same data folder as main preprocessing):
    - census_od_2021_msoa.csv        (2021 MSOA-level OD, all E&W)
    - census_od_2011_oa.csv          (2011 OA-level OD, all E&W)
    - NSPCL_NOV22_UK_LU.csv          (postcode lookup: OA → LSOA → MSOA)
    - msoa_2011_to_2021_lookup.csv   (MSOA 2011 ↔ 2021 correspondence)
    - imd_2010.xls                   (IMD 2010 LSOA scores)
    - imd_2019.csv                   (IMD 2019, for mid-2015 LSOA populations)
    - ks101ew_lsoa_2011.csv          (2011 Census population by LSOA)
    - msoa_cascade_features_enriched_20260616.csv  (existing results to merge)

Output:
    - msoa_cascade_national_frame_YYYYMMDD.csv

Author: [Your name]
Date: June 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date
from scipy import stats

# ══════════════════════════════════════════════════════════════════════
# CONFIGURATION — update paths to match your local setup
# ══════════════════════════════════════════════════════════════════════
ROOT = Path('.')  # or: from pyprojroot import here; ROOT = here()
DATA_DIR = ROOT / 'data'
OUTPUT_DIR = ROOT / 'outputs'
OUTPUT_DIR.mkdir(exist_ok=True)

CENSUS_OD_2021_PATH = DATA_DIR / 'census_od_2021_msoa.csv'
CENSUS_OD_2011_PATH = DATA_DIR / 'census_od_2011_oa.csv'
LOOKUP_PATH         = DATA_DIR / 'NSPCL_NOV22_UK_LU.csv'
MSOA_LOOKUP_PATH    = DATA_DIR / 'msoa_2011_to_2021_lookup.csv'
IMD_2010_PATH       = DATA_DIR / 'imd_2010.xls'
IMD_2019_PATH       = DATA_DIR / 'imd_2019.csv'
KS101_PATH          = DATA_DIR / 'ks101ew_lsoa_2011.csv'
EXISTING_FEATURES   = DATA_DIR / 'msoa_cascade_features_enriched_20260616.csv'

EXTERNAL_CODE = 'EXT_OUTSIDE'


# ══════════════════════════════════════════════════════════════════════
# 1. LOAD & HARMONISE GEOGRAPHIES
# ══════════════════════════════════════════════════════════════════════
print('=' * 70)
print('1. Loading datasets and harmonising geographies')
print('=' * 70)

# ---- 1a. MSOA 2021→2011 correspondence (1:1 only) ----
msoa_11_21 = pd.read_csv(MSOA_LOOKUP_PATH)
msoa_11_21.columns = msoa_11_21.columns.str.strip().str.lower()
unchanged = msoa_11_21[msoa_11_21['msoa11cd'] == msoa_11_21['msoa21cd']].copy()
msoa21_to_11 = dict(zip(unchanged['msoa21cd'], unchanged['msoa11cd']))
print(f'MSOA 2021→2011 unchanged: {len(msoa21_to_11)}')

# ---- 1b. NSPCL postcode lookup → OA/LSOA/MSOA/LAD mappings ----
lookup = pd.read_csv(LOOKUP_PATH, encoding='ISO-8859-1', low_memory=False)
oa_to_msoa_dict = dict(
    lookup[['oa11cd', 'msoa11cd']].drop_duplicates().dropna().values)

lsoa_msoa_lad = (lookup[['lsoa11cd', 'msoa11cd', 'ladnm']]
                 .drop_duplicates().dropna())
print(f'OA→MSOA mappings: {len(oa_to_msoa_dict):,}')
print(f'LSOA→MSOA mappings: {len(lsoa_msoa_lad):,}')

# ---- 1c. London analysis MSOAs (from existing results) ----
existing = pd.read_csv(EXISTING_FEATURES)
analysis_msoas = set(existing['msoa11cd'].unique())
print(f'London analysis MSOAs: {len(analysis_msoas)}')

# ---- 1d. All England MSOAs (from the lookup) ----
# Every unique MSOA in the postcode lookup represents an England/Wales MSOA
all_england_msoas = set(lsoa_msoa_lad['msoa11cd'].unique())
print(f'All England/Wales MSOAs in lookup: {len(all_england_msoas)}')


# ══════════════════════════════════════════════════════════════════════
# 2. BUILD NATIONAL DEPRIVATION HIERARCHY
#    Aggregate IMD 2010 to ALL England MSOAs, then qcut into deciles
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('2. Building national deprivation hierarchy')
print('=' * 70)

# ---- 2a. Load IMD 2010 (LSOA level, all England) ----
imd_2010 = pd.read_excel(IMD_2010_PATH, sheet_name='IMD 2010')
imd_2010.columns = imd_2010.columns.str.strip()

# Identify column names (vary between IMD file versions)
lsoa_col_10 = [c for c in imd_2010.columns
                if 'lsoa' in c.lower() and 'code' in c.lower()][0]
score_col_10 = [c for c in imd_2010.columns
                 if 'score' in c.lower() and 'imd' in c.lower()][0]
print(f'IMD 2010: {len(imd_2010)} LSOAs, score col = "{score_col_10}"')

# ---- 2b. Load population weights (ALL England & Wales LSOAs) ----
#      KS101EW downloaded from Nomis for all LSOAs (not just London).
#      Columns: 'geography code' = LSOA code,
#               'Variable: All usual residents; measures: Value' = population
ks101 = pd.read_csv(KS101_PATH)
ks101.columns = ks101.columns.str.strip()

# Use explicit column names — the auto-detection in the original script
# picks 'geography' (the NAME) instead of 'geography code' (the CODE),
# causing silent merge failures. Explicit is safer.
KS_CODE_COL = 'geography code'
KS_POP_COL = 'Variable: All usual residents; measures: Value'

# Fallback if column names differ in your download
if KS_CODE_COL not in ks101.columns:
    # Try common alternatives
    KS_CODE_COL = [c for c in ks101.columns if 'code' in c.lower()][0]
if KS_POP_COL not in ks101.columns:
    KS_POP_COL = [c for c in ks101.columns if 'all usual' in c.lower()][0]

lsoa_pop = (ks101[[KS_CODE_COL, KS_POP_COL]]
            .rename(columns={KS_CODE_COL: 'lsoa11cd', KS_POP_COL: 'pop'}))
lsoa_pop['pop'] = pd.to_numeric(lsoa_pop['pop'], errors='coerce').fillna(0)
print(f'Population weights: {len(lsoa_pop)} LSOAs, '
      f'total pop = {lsoa_pop["pop"].sum():,.0f}')

# Sanity check: confirm we have non-London LSOAs
n_london = lsoa_pop['lsoa11cd'].str.startswith('E01').sum()  # all are E01
print(f'  (should be ~34,753 for all England & Wales)')

# ---- 2c. Aggregate IMD scores: LSOA → MSOA (population-weighted mean) ----
#      This mirrors the main preprocessing approach exactly, but for ALL
#      England MSOAs rather than London only.
imd_lsoa = (imd_2010[[lsoa_col_10, score_col_10]]
            .rename(columns={lsoa_col_10: 'lsoa11cd', score_col_10: 'imd_score'}))

# Join LSOA → MSOA geography
imd_geo = pd.merge(imd_lsoa, lsoa_msoa_lad[['lsoa11cd', 'msoa11cd']],
                    on='lsoa11cd', how='inner')

# Join population weights
imd_geo = pd.merge(imd_geo, lsoa_pop, on='lsoa11cd', how='left')
imd_geo['pop'] = imd_geo['pop'].fillna(0)

# Population-weighted mean per MSOA
def weighted_mean(group):
    w = group['pop']
    if w.sum() == 0:
        return group['imd_score'].mean()
    return np.average(group['imd_score'], weights=w)

msoa_imd_national = (imd_geo.groupby('msoa11cd')
                     .apply(weighted_mean, include_groups=False)
                     .reset_index()
                     .rename(columns={0: 'IMD_2010_national'}))

print(f'National MSOA IMD scores computed: {len(msoa_imd_national)}')

# ---- 2d. Assign national wealth deciles (1 = most deprived, 10 = least) ----
#      qcut on the FULL national distribution
msoa_imd_national['Wealth_Decile_National'] = pd.qcut(
    msoa_imd_national['IMD_2010_national'],
    q=10, labels=range(1, 11)  # 1 = most deprived (highest score)
).astype(int)

# IMD: higher score = more deprived, so qcut bin 1 = highest scores = most deprived
# Need to REVERSE: qcut with default ascending bins means bin 1 = lowest scores = LEAST deprived
# Let's verify and fix:
d1_mean = msoa_imd_national.loc[
    msoa_imd_national['Wealth_Decile_National'] == 1, 'IMD_2010_national'].mean()
d10_mean = msoa_imd_national.loc[
    msoa_imd_national['Wealth_Decile_National'] == 10, 'IMD_2010_national'].mean()

if d1_mean < d10_mean:
    # qcut assigned 1 to lowest scores (least deprived) — need to flip
    msoa_imd_national['Wealth_Decile_National'] = (
        11 - msoa_imd_national['Wealth_Decile_National'])
    print('Deciles flipped: 1 = most deprived, 10 = least deprived')

# Verification
print('\nNational decile summary:')
for d in range(1, 11):
    subset = msoa_imd_national[msoa_imd_national['Wealth_Decile_National'] == d]
    n_london = subset['msoa11cd'].isin(analysis_msoas).sum()
    print(f'  D{d:>2d}: {len(subset):>4d} MSOAs  '
          f'(IMD {subset["IMD_2010_national"].mean():>6.1f})  '
          f'{n_london:>3d} London')

# ---- 2e. Wealth decile for the EXTERNAL synthetic MSOA ----
#      Population-weighted mean decile of all non-London MSOAs
non_london = msoa_imd_national[~msoa_imd_national['msoa11cd'].isin(analysis_msoas)].copy()

# Get MSOA-level population for weighting
msoa_pop = (imd_geo.groupby('msoa11cd')['pop'].sum()
            .reset_index().rename(columns={'pop': 'msoa_pop'}))
non_london = non_london.merge(msoa_pop, on='msoa11cd', how='left')
non_london['msoa_pop'] = non_london['msoa_pop'].fillna(0)

ext_weighted_decile = np.average(
    non_london['Wealth_Decile_National'],
    weights=non_london['msoa_pop'])
ext_decile = int(round(ext_weighted_decile))

print(f'\nExternal MSOA weighted mean decile: {ext_weighted_decile:.2f} → assigned D{ext_decile}')
print(f'  (Based on {len(non_london)} non-London MSOAs, '
      f'pop = {non_london["msoa_pop"].sum():,.0f})')

# ---- 2f. Build the complete wealth mapping ----
wealth_national = dict(zip(
    msoa_imd_national['msoa11cd'],
    msoa_imd_national['Wealth_Decile_National']))
wealth_national[EXTERNAL_CODE] = ext_decile

# Compare London deciles: national vs London-relative
london_national = msoa_imd_national[
    msoa_imd_national['msoa11cd'].isin(analysis_msoas)].copy()
london_national = london_national.merge(
    existing[['msoa11cd', 'Wealth_Decile']],
    on='msoa11cd', how='left')

print(f'\nLondon MSOAs — national vs London-relative decile comparison:')
ct = pd.crosstab(london_national['Wealth_Decile'],
                 london_national['Wealth_Decile_National'],
                 margins=True)
print(ct.to_string())

rho, p = stats.spearmanr(london_national['Wealth_Decile'],
                          london_national['Wealth_Decile_National'])
print(f'\nSpearman correlation: ρ = {rho:.4f}, p = {p:.2e}')


# ══════════════════════════════════════════════════════════════════════
# 3. FILTER OD DATA: LONDON-TOUCHING FLOWS
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('3. Filtering OD data to London-touching flows')
print('=' * 70)

# ---- 3a. 2021 Census OD (MSOA level, all E&W) ----
print('\n--- 2021 ---')
od_2021 = pd.read_csv(CENSUS_OD_2021_PATH)
od_2021.columns = od_2021.columns.str.strip()
c21 = od_2021.columns.tolist()
origin_21, dest_21, count_21 = c21[0], c21[1], c21[2]
print(f'Raw records: {len(od_2021):,}')

# Harmonise to 2011 MSOA codes
od_2021['origin_msoa11'] = od_2021[origin_21].astype(str).map(msoa21_to_11)
od_2021['dest_msoa11'] = od_2021[dest_21].astype(str).map(msoa21_to_11)

# Classify endpoints
od_2021['o_london'] = od_2021['origin_msoa11'].isin(analysis_msoas)
od_2021['d_london'] = od_2021['dest_msoa11'].isin(analysis_msoas)

# Keep: at least one endpoint in London
lt_21 = od_2021[od_2021['o_london'] | od_2021['d_london']].copy()

# Recode non-London endpoints → EXTERNAL_CODE
lt_21.loc[~lt_21['o_london'], 'origin_msoa11'] = EXTERNAL_CODE
lt_21.loc[~lt_21['d_london'], 'dest_msoa11'] = EXTERNAL_CODE

# Drop intra-MSOA (including EXT→EXT which shouldn't exist)
lt_21 = lt_21[lt_21['origin_msoa11'] != lt_21['dest_msoa11']]

# Aggregate
flows_21 = (lt_21.groupby(['origin_msoa11', 'dest_msoa11'])[count_21]
            .sum().reset_index().rename(columns={count_21: 'count'}))

_int = flows_21[(flows_21['origin_msoa11'] != EXTERNAL_CODE) &
                (flows_21['dest_msoa11'] != EXTERNAL_CODE)]
_from = flows_21[flows_21['origin_msoa11'] == EXTERNAL_CODE]
_to = flows_21[flows_21['dest_msoa11'] == EXTERNAL_CODE]
print(f'Internal:  {len(_int):>7,} records  {_int["count"].sum():>10,.0f} persons')
print(f'Ext→Ldn:   {len(_from):>7,} records  {_from["count"].sum():>10,.0f} persons')
print(f'Ldn→Ext:   {len(_to):>7,} records  {_to["count"].sum():>10,.0f} persons')

# ---- 3b. 2011 Census OD (OA level → MSOA) ----
print('\n--- 2011 ---')
od_2011 = pd.read_csv(CENSUS_OD_2011_PATH,
    header=None, names=['dest_oa', 'origin_oa', 'persons'],
    dtype={'dest_oa': str, 'origin_oa': str, 'persons': int})
print(f'Raw OA records: {len(od_2011):,}')

od_2011['origin_msoa11'] = od_2011['origin_oa'].map(oa_to_msoa_dict)
od_2011['dest_msoa11'] = od_2011['dest_oa'].map(oa_to_msoa_dict)
od_2011['o_london'] = od_2011['origin_msoa11'].isin(analysis_msoas)
od_2011['d_london'] = od_2011['dest_msoa11'].isin(analysis_msoas)

lt_11 = od_2011[od_2011['o_london'] | od_2011['d_london']].copy()
lt_11.loc[~lt_11['o_london'], 'origin_msoa11'] = EXTERNAL_CODE
lt_11.loc[~lt_11['d_london'], 'dest_msoa11'] = EXTERNAL_CODE
lt_11 = lt_11[lt_11['origin_msoa11'] != lt_11['dest_msoa11']]

flows_11 = (lt_11.groupby(['origin_msoa11', 'dest_msoa11'])['persons']
            .sum().reset_index().rename(columns={'persons': 'count'}))

_int = flows_11[(flows_11['origin_msoa11'] != EXTERNAL_CODE) &
                (flows_11['dest_msoa11'] != EXTERNAL_CODE)]
_from = flows_11[flows_11['origin_msoa11'] == EXTERNAL_CODE]
_to = flows_11[flows_11['dest_msoa11'] == EXTERNAL_CODE]
print(f'Internal:  {len(_int):>7,} records  {_int["count"].sum():>10,.0f} persons')
print(f'Ext→Ldn:   {len(_from):>7,} records  {_from["count"].sum():>10,.0f} persons')
print(f'Ldn→Ext:   {len(_to):>7,} records  {_to["count"].sum():>10,.0f} persons')


# ══════════════════════════════════════════════════════════════════════
# 4. COMPUTE CASCADE METRICS (national frame, with external flows)
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('4. Computing cascade metrics — national deprivation frame')
print('=' * 70)

def compute_cascade_national(flow_df, count_col, wealth_map,
                              london_msoas, year_label):
    """
    Compute per-MSOA cascade metrics using NATIONAL wealth deciles
    on a flow table that includes London ↔ External flows.

    Returns DataFrame indexed by msoa11cd (London MSOAs only).
    """
    df = flow_df.copy()
    df['Origin_Decile'] = df['origin_msoa11'].map(wealth_map)
    df['Dest_Decile'] = df['dest_msoa11'].map(wealth_map)

    # Drop any unmapped (shouldn't happen if everything is wired correctly)
    n_unmapped = df[['Origin_Decile', 'Dest_Decile']].isna().any(axis=1).sum()
    if n_unmapped > 0:
        print(f'  ⚠ {n_unmapped} records with unmapped deciles — dropping')
        df = df.dropna(subset=['Origin_Decile', 'Dest_Decile'])

    df['Origin_Decile'] = df['Origin_Decile'].astype(int)
    df['Dest_Decile'] = df['Dest_Decile'].astype(int)

    # Flow summary
    total = df[count_col].sum()
    up = df.loc[df['Dest_Decile'] > df['Origin_Decile'], count_col].sum()
    down = df.loc[df['Dest_Decile'] < df['Origin_Decile'], count_col].sum()
    lat = df.loc[df['Dest_Decile'] == df['Origin_Decile'], count_col].sum()
    print(f'\n  {year_label} — national frame, with external:')
    print(f'    Total:   {total:>10,.0f}')
    print(f'    Upward:  {up:>10,.0f} ({up/total*100:.1f}%)')
    print(f'    Down:    {down:>10,.0f} ({down/total*100:.1f}%)')
    print(f'    Lateral: {lat:>10,.0f} ({lat/total*100:.1f}%)')

    # ---- Per-London-MSOA metrics ----
    idx = sorted(london_msoas)

    # Cascade direction: wealthier in, poorer out
    inflow_w = (df[df['Origin_Decile'] > df['Dest_Decile']]
                .groupby('dest_msoa11')[count_col].sum()
                .reindex(idx, fill_value=0).rename('Inflow_Wealthier_nat'))

    outflow_p = (df[df['Dest_Decile'] < df['Origin_Decile']]
                 .groupby('origin_msoa11')[count_col].sum()
                 .reindex(idx, fill_value=0).rename('Outflow_Poorer_nat'))

    # Counter-cascade: wealthier out, poorer in
    outflow_w = (df[df['Dest_Decile'] > df['Origin_Decile']]
                 .groupby('origin_msoa11')[count_col].sum()
                 .reindex(idx, fill_value=0).rename('Outflow_Wealthier_nat'))

    inflow_p = (df[df['Origin_Decile'] < df['Dest_Decile']]
                .groupby('dest_msoa11')[count_col].sum()
                .reindex(idx, fill_value=0).rename('Inflow_Poorer_nat'))

    # Totals
    total_in = (df.groupby('dest_msoa11')[count_col].sum()
                .reindex(idx, fill_value=0).rename('Total_Inflow_nat'))
    total_out = (df.groupby('origin_msoa11')[count_col].sum()
                 .reindex(idx, fill_value=0).rename('Total_Outflow_nat'))

    # External-specific volumes (for reporting)
    ext_in = (df[df['origin_msoa11'] == EXTERNAL_CODE]
              .groupby('dest_msoa11')[count_col].sum()
              .reindex(idx, fill_value=0).rename('Ext_Inflow'))
    ext_out = (df[df['dest_msoa11'] == EXTERNAL_CODE]
               .groupby('origin_msoa11')[count_col].sum()
               .reindex(idx, fill_value=0).rename('Ext_Outflow'))

    # Assemble
    r = pd.DataFrame(index=pd.Index(idx, name='msoa11cd'))
    for s in [inflow_w, outflow_p, outflow_w, inflow_p,
              total_in, total_out, ext_in, ext_out]:
        r = r.join(s, how='left')
    r = r.fillna(0)

    # Derived cascade metrics
    r['Total_Migration_nat'] = r['Total_Inflow_nat'] + r['Total_Outflow_nat']
    r['CFI_Churn_nat'] = r['Inflow_Wealthier_nat'] + r['Outflow_Poorer_nat']
    r['CFI_Rate_nat'] = np.where(
        r['Total_Migration_nat'] > 0,
        (r['Inflow_Wealthier_nat'] * r['Outflow_Poorer_nat']) / r['Total_Migration_nat'],
        0)
    r['Net_Cascade_nat'] = r['Inflow_Wealthier_nat'] - r['Outflow_Poorer_nat']
    r['Pct_Inflow_Wealthier_nat'] = np.where(
        r['Total_Inflow_nat'] > 0,
        (r['Inflow_Wealthier_nat'] / r['Total_Inflow_nat']) * 100, 0)

    # Derived counter-cascade metrics
    r['Counter_Churn_nat'] = r['Outflow_Wealthier_nat'] + r['Inflow_Poorer_nat']
    r['Counter_Rate_nat'] = np.where(
        r['Total_Migration_nat'] > 0,
        (r['Outflow_Wealthier_nat'] * r['Inflow_Poorer_nat']) / r['Total_Migration_nat'],
        0)
    r['Net_Counter_nat'] = r['Outflow_Wealthier_nat'] - r['Inflow_Poorer_nat']

    # Cascade Dominance (cascade share of total cross-decile churn)
    total_cross = r['CFI_Churn_nat'] + r['Counter_Churn_nat']
    r['Cascade_Dominance_nat'] = np.where(
        total_cross > 0, r['CFI_Churn_nat'] / total_cross, 0.5)

    # External net
    r['Ext_Net_Migration'] = r['Ext_Inflow'] - r['Ext_Outflow']

    return r


cascade_nat_11 = compute_cascade_national(
    flows_11, 'count', wealth_national, analysis_msoas, '2011')

cascade_nat_21 = compute_cascade_national(
    flows_21, 'count', wealth_national, analysis_msoas, '2021')

# Add year suffixes
cascade_nat_11.columns = [f'{c}_11' if not c.startswith('Ext_') else c + '_11'
                           for c in cascade_nat_11.columns]
cascade_nat_21.columns = [f'{c}_21' if not c.startswith('Ext_') else c + '_21'
                           for c in cascade_nat_21.columns]


# ══════════════════════════════════════════════════════════════════════
# 5. MERGE WITH EXISTING LONDON-ONLY FEATURES
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('5. Merging with existing London-only features')
print('=' * 70)

# Add national decile to existing data
nat_deciles = msoa_imd_national[msoa_imd_national['msoa11cd'].isin(analysis_msoas)]
result = existing.merge(
    nat_deciles[['msoa11cd', 'Wealth_Decile_National']],
    on='msoa11cd', how='left')

result = result.merge(cascade_nat_11, left_on='msoa11cd',
                       right_index=True, how='left')
result = result.merge(cascade_nat_21, left_on='msoa11cd',
                       right_index=True, how='left')

print(f'Final dataset: {result.shape}')


# ══════════════════════════════════════════════════════════════════════
# 6. KEY COMPARISON: CASCADE/COUNTER-CASCADE BALANCE
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('6. Key comparison: does including external flows change the')
print('   cascade vs counter-cascade balance?')
print('=' * 70)

for yr in ['11', '21']:
    print(f'\n--- 20{yr} ---')

    # London-only Cascade Dominance (from existing data)
    dom_london = f'Cascade_Dominance_{yr}'
    # National-frame Cascade Dominance
    dom_nat = f'Cascade_Dominance_nat_{yr}'

    if dom_london in result.columns and dom_nat in result.columns:
        ldn_mean = result[dom_london].mean()
        nat_mean = result[dom_nat].mean()
        ldn_below = (result[dom_london] < 0.5).mean() * 100
        nat_below = (result[dom_nat] < 0.5).mean() * 100

        print(f'  Cascade Dominance (mean):')
        print(f'    London-only frame:  {ldn_mean:.4f}  '
              f'({ldn_below:.1f}% of MSOAs below 0.5)')
        print(f'    National frame:     {nat_mean:.4f}  '
              f'({nat_below:.1f}% of MSOAs below 0.5)')
        print(f'    Shift:              {nat_mean - ldn_mean:+.4f}')

        # Correlation between the two
        rho, p = stats.spearmanr(result[dom_london], result[dom_nat])
        print(f'    Spearman ρ:         {rho:.4f} (p={p:.2e})')

    # CFI Churn comparison
    churn_ldn = f'CFI_Churn_{yr}'
    churn_nat = f'CFI_Churn_nat_{yr}'
    if churn_ldn in result.columns and churn_nat in result.columns:
        print(f'  CFI Churn (mean):')
        print(f'    London-only: {result[churn_ldn].mean():>10.1f}')
        print(f'    National:    {result[churn_nat].mean():>10.1f}')

    # External flow volumes
    ext_in_col = f'Ext_Inflow_{yr}'
    ext_out_col = f'Ext_Outflow_{yr}'
    if ext_in_col in result.columns:
        print(f'  External flows:')
        print(f'    Mean inflow from outside:  {result[ext_in_col].mean():>8.1f}')
        print(f'    Mean outflow to outside:   {result[ext_out_col].mean():>8.1f}')
        print(f'    Mean net external:         '
              f'{result[f"Ext_Net_Migration_{yr}"].mean():>+8.1f}')


# ══════════════════════════════════════════════════════════════════════
# 7. EXPORT
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('7. Export')
print('=' * 70)

today = date.today().strftime('%Y%m%d')
out_path = OUTPUT_DIR / f'msoa_cascade_national_frame_{today}.csv'
result.to_csv(out_path, index=False)
print(f'✓ Saved to: {out_path}')
print(f'  Shape: {result.shape}')

nat_cols = [c for c in result.columns if '_nat' in c or 'Ext_' in c
            or c == 'Wealth_Decile_National']
print(f'  New columns ({len(nat_cols)}): {nat_cols[:10]}...')
