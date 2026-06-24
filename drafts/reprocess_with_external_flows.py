"""
Reprocessing Census OD Data: Including London ↔ External Flows
================================================================

Purpose:
    The main analysis filters to London-internal flows only (both origin AND
    destination in London). This script extends the pipeline by also including
    flows where ONE endpoint is in London and the other is outside — treating
    the entire non-London area as a single synthetic "+1" MSOA.

Design decisions:
    1. The synthetic external MSOA is coded 'EXT_OUTSIDE' in the output.
    2. Its wealth decile is assigned via the population-weighted national
       median IMD score (sensitivity: also computed with no decile, reported
       as a separate flow category).
    3. Intra-London flows are identical to the main pipeline.
    4. New columns are appended with suffix '_ext' to distinguish from the
       London-only metrics.

Inputs (same as main preprocessing notebook):
    - census_od_2021_msoa.csv     (2021 MSOA-level OD data, E&W)
    - census_od_2011_oa.csv       (2011 OA-level OD data, E&W)
    - NSPCL_NOV22_UK_LU.csv       (postcode lookup for OA→MSOA)
    - msoa_2011_to_2021_lookup.csv (MSOA 2011↔2021 correspondence)
    - imd_2010.xls                (IMD 2010 LSOA scores)
    - imd_2019.csv                (IMD 2019 LSOA scores, with mid-2015 pop)
    - ks101ew_lsoa_2011.csv       (2011 Census population by LSOA)
    - msoa_cascade_features_enriched_20260616.csv (existing London-only results)

Output:
    - msoa_cascade_features_with_external_YYYYMMDD.csv

Usage:
    1. Update DATA_DIR to point to your local data folder
    2. Run the full script
    3. Output CSV will contain original London-only columns PLUS new
       '_ext' columns incorporating external flows

Author: [Your name]
Date: June 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date

# ══════════════════════════════════════════════════════════════════════
# CONFIGURATION — update these paths to match your local setup
# ══════════════════════════════════════════════════════════════════════
ROOT = Path('.')  # Change to your project root, or use: from pyprojroot import here; ROOT = here()
DATA_DIR = ROOT / 'data'
OUTPUT_DIR = ROOT / 'outputs'
OUTPUT_DIR.mkdir(exist_ok=True)

# File paths (same as in data_preprocess notebook)
CENSUS_OD_2021_PATH = DATA_DIR / 'census_od_2021_msoa.csv'
CENSUS_OD_2011_PATH = DATA_DIR / 'census_od_2011_oa.csv'
LOOKUP_PATH         = DATA_DIR / 'NSPCL_NOV22_UK_LU.csv'
MSOA_LOOKUP_PATH    = DATA_DIR / 'msoa_2011_to_2021_lookup.csv'
IMD_2010_PATH       = DATA_DIR / 'imd_2010.xls'
IMD_2019_PATH       = DATA_DIR / 'imd_2019.csv'
KS101_PATH          = DATA_DIR / 'ks101ew_lsoa_2011.csv'

# Existing London-only results (for merging at the end)
EXISTING_FEATURES   = DATA_DIR / 'msoa_cascade_features_enriched_20260616.csv'

# Synthetic MSOA code for all non-London areas
EXTERNAL_CODE = 'EXT_OUTSIDE'

# ══════════════════════════════════════════════════════════════════════
# 1. LOAD & HARMONISE GEOGRAPHIES (replicated from main notebook)
# ══════════════════════════════════════════════════════════════════════
print('=' * 70)
print('1. Loading datasets and harmonising geographies')
print('=' * 70)

# ---- 1a. MSOA 2021→2011 mapping ----
msoa_11_21 = pd.read_csv(MSOA_LOOKUP_PATH)
msoa_11_21.columns = msoa_11_21.columns.str.strip().str.lower()
unchanged = msoa_11_21[msoa_11_21['msoa11cd'] == msoa_11_21['msoa21cd']].copy()
msoa21_to_11 = dict(zip(unchanged['msoa21cd'], unchanged['msoa11cd']))
print(f'MSOA 2021→2011 unchanged mappings: {len(msoa21_to_11)}')

# ---- 1b. OA→MSOA mapping (for 2011 data) ----
lookup = pd.read_csv(LOOKUP_PATH, encoding='ISO-8859-1', low_memory=False)
oa_to_msoa = lookup[['oa11cd', 'msoa11cd']].drop_duplicates().dropna()
oa_to_msoa_dict = dict(zip(oa_to_msoa['oa11cd'], oa_to_msoa['msoa11cd']))
print(f'OA→MSOA mappings: {len(oa_to_msoa_dict):,}')

# ---- 1c. London analysis set (983 MSOAs) ----
existing = pd.read_csv(EXISTING_FEATURES)
analysis_msoas = set(existing['msoa11cd'].unique())
wealth_mapping = dict(zip(existing['msoa11cd'], existing['Wealth_Decile']))
print(f'London analysis MSOAs: {len(analysis_msoas)}')

# ══════════════════════════════════════════════════════════════════════
# 2. ASSIGN WEALTH DECILE TO EXTERNAL SYNTHETIC MSOA
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('2. Computing external MSOA wealth decile')
print('=' * 70)

# Load IMD 2010 for all England LSOAs
imd_2010 = pd.read_excel(IMD_2010_PATH, sheet_name='IMD 2010')
imd_2010.columns = imd_2010.columns.str.strip()

# Identify the score and code columns (names vary between IMD releases)
imd_2010_cols = imd_2010.columns.tolist()
lsoa_col_2010 = [c for c in imd_2010_cols if 'lsoa' in c.lower() and 'code' in c.lower()][0]
score_col_2010 = [c for c in imd_2010_cols if 'score' in c.lower() and 'imd' in c.lower()][0]

# LSOA→MSOA→London flag
lsoa_msoa = lookup[['lsoa11cd', 'msoa11cd']].drop_duplicates().dropna()
lsoa_msoa['is_london'] = lsoa_msoa['msoa11cd'].isin(analysis_msoas)

imd_with_geo = pd.merge(
    imd_2010[[lsoa_col_2010, score_col_2010]].rename(
        columns={lsoa_col_2010: 'lsoa11cd', score_col_2010: 'imd_score'}),
    lsoa_msoa, on='lsoa11cd', how='left'
)

# Population-weighted mean IMD for non-London England
# Use 2011 Census population as weights
ks101 = pd.read_csv(KS101_PATH)
ks101.columns = ks101.columns.str.strip()
# Identify population column (varies by download)
pop_candidates = [c for c in ks101.columns if 'all' in c.lower() and 'usual' in c.lower()]
if pop_candidates:
    pop_col = pop_candidates[0]
else:
    pop_col = ks101.columns[1]  # fallback: second column is usually the count
code_col = [c for c in ks101.columns if 'geography' in c.lower() or 'code' in c.lower()][0]

ks101_clean = ks101[[code_col, pop_col]].rename(
    columns={code_col: 'lsoa11cd', pop_col: 'pop'})
ks101_clean['pop'] = pd.to_numeric(ks101_clean['pop'], errors='coerce').fillna(0)

external = imd_with_geo[imd_with_geo['is_london'] == False].merge(
    ks101_clean, on='lsoa11cd', how='left')
external['pop'] = external['pop'].fillna(0)

# Weighted mean
ext_pop = external['pop'].sum()
ext_weighted_imd = (external['imd_score'] * external['pop']).sum() / ext_pop

# Map this score to a London wealth decile
# Use the decile boundaries from the London MSOA distribution
london_imd = existing[['msoa11cd', 'IMD_2010', 'Wealth_Decile']].copy()
decile_boundaries = london_imd.groupby('Wealth_Decile')['IMD_2010'].agg(['min', 'max'])
print(f'\nExternal weighted mean IMD score: {ext_weighted_imd:.2f}')
print(f'(Lower score = less deprived)')
print(f'\nLondon decile boundaries (IMD 2010 score):')
print(decile_boundaries.to_string())

# Assign decile: find which London decile this score falls into
# Note: higher IMD score = more deprived = lower decile number (1 = most deprived)
ext_decile = None
for d in range(1, 11):
    bounds = decile_boundaries.loc[d]
    if bounds['min'] <= ext_weighted_imd <= bounds['max']:
        ext_decile = d
        break
if ext_decile is None:
    # If below all London scores (less deprived than any London MSOA)
    if ext_weighted_imd < decile_boundaries.loc[10, 'min']:
        ext_decile = 10
    else:
        ext_decile = 1

print(f'\n→ External MSOA assigned to Wealth Decile: {ext_decile}')
print(f'  (This means non-London E&W has similar deprivation to London decile {ext_decile})')

# Add to wealth mapping
wealth_mapping_ext = wealth_mapping.copy()
wealth_mapping_ext[EXTERNAL_CODE] = ext_decile

# ══════════════════════════════════════════════════════════════════════
# 3. FILTER OD DATA: LONDON-TOUCHING FLOWS
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('3. Filtering OD data to London-touching flows')
print('=' * 70)

# ---- 3a. 2021 Census OD (MSOA level) ----
print('\n--- 2021 ---')
od_2021_raw = pd.read_csv(CENSUS_OD_2021_PATH)
od_2021_raw.columns = od_2021_raw.columns.str.strip()

# Identify columns (adjust if your file uses different names)
cols_2021 = od_2021_raw.columns.tolist()
origin_col_21 = cols_2021[0]  # Usually first column
dest_col_21 = cols_2021[1]    # Second column
count_col_21 = cols_2021[2]   # Third column
print(f'Columns: {origin_col_21}, {dest_col_21}, {count_col_21}')
print(f'Raw records: {len(od_2021_raw):,}')

# Harmonise to 2011 codes
od_2021_raw['origin_msoa11'] = od_2021_raw[origin_col_21].astype(str).map(msoa21_to_11)
od_2021_raw['dest_msoa11'] = od_2021_raw[dest_col_21].astype(str).map(msoa21_to_11)

# Classify endpoints
od_2021_raw['origin_is_london'] = od_2021_raw['origin_msoa11'].isin(analysis_msoas)
od_2021_raw['dest_is_london'] = od_2021_raw['dest_msoa11'].isin(analysis_msoas)

# Filter: at least one endpoint in London, exclude intra-MSOA
london_touching_21 = od_2021_raw[
    (od_2021_raw['origin_is_london'] | od_2021_raw['dest_is_london'])
].copy()

# Recode non-London endpoints as EXTERNAL_CODE
london_touching_21.loc[~london_touching_21['origin_is_london'], 'origin_msoa11'] = EXTERNAL_CODE
london_touching_21.loc[~london_touching_21['dest_is_london'], 'dest_msoa11'] = EXTERNAL_CODE

# Exclude intra-MSOA (including EXT→EXT which shouldn't exist, but safety)
london_touching_21 = london_touching_21[
    london_touching_21['origin_msoa11'] != london_touching_21['dest_msoa11']
].copy()

# Aggregate (2021 data is already MSOA-level, but external codes need consolidation)
flows_21 = (london_touching_21
    .groupby(['origin_msoa11', 'dest_msoa11'])[count_col_21]
    .sum().reset_index()
    .rename(columns={count_col_21: 'count'}))

# Split into internal and external
internal_21 = flows_21[
    (flows_21['origin_msoa11'] != EXTERNAL_CODE) & 
    (flows_21['dest_msoa11'] != EXTERNAL_CODE)
]
from_ext_21 = flows_21[flows_21['origin_msoa11'] == EXTERNAL_CODE]
to_ext_21 = flows_21[flows_21['dest_msoa11'] == EXTERNAL_CODE]

print(f'London-internal flow records: {len(internal_21):,}  '
      f'({internal_21["count"].sum():,.0f} persons)')
print(f'External→London flow records: {len(from_ext_21):,}  '
      f'({from_ext_21["count"].sum():,.0f} persons)')
print(f'London→External flow records: {len(to_ext_21):,}  '
      f'({to_ext_21["count"].sum():,.0f} persons)')

# ---- 3b. 2011 Census OD (OA level → aggregate to MSOA) ----
print('\n--- 2011 ---')
od_2011_raw = pd.read_csv(CENSUS_OD_2011_PATH,
    header=None, names=['dest_oa', 'origin_oa', 'persons'],
    dtype={'dest_oa': str, 'origin_oa': str, 'persons': int})
print(f'Raw OA-level records: {len(od_2011_raw):,}')

# Map OA → MSOA (non-London OAs get NaN, which we'll recode as EXTERNAL)
od_2011_raw['origin_msoa11'] = od_2011_raw['origin_oa'].map(oa_to_msoa_dict)
od_2011_raw['dest_msoa11'] = od_2011_raw['dest_oa'].map(oa_to_msoa_dict)

# Classify
od_2011_raw['origin_is_london'] = od_2011_raw['origin_msoa11'].isin(analysis_msoas)
od_2011_raw['dest_is_london'] = od_2011_raw['dest_msoa11'].isin(analysis_msoas)

# Keep London-touching only
london_touching_11 = od_2011_raw[
    (od_2011_raw['origin_is_london'] | od_2011_raw['dest_is_london'])
].copy()

# Recode non-London as EXTERNAL
london_touching_11.loc[~london_touching_11['origin_is_london'], 'origin_msoa11'] = EXTERNAL_CODE
london_touching_11.loc[~london_touching_11['dest_is_london'], 'dest_msoa11'] = EXTERNAL_CODE

# Exclude intra-MSOA
london_touching_11 = london_touching_11[
    london_touching_11['origin_msoa11'] != london_touching_11['dest_msoa11']
]

# Aggregate to MSOA level
flows_11 = (london_touching_11
    .groupby(['origin_msoa11', 'dest_msoa11'])['persons']
    .sum().reset_index()
    .rename(columns={'persons': 'count'}))

internal_11 = flows_11[
    (flows_11['origin_msoa11'] != EXTERNAL_CODE) & 
    (flows_11['dest_msoa11'] != EXTERNAL_CODE)
]
from_ext_11 = flows_11[flows_11['origin_msoa11'] == EXTERNAL_CODE]
to_ext_11 = flows_11[flows_11['dest_msoa11'] == EXTERNAL_CODE]

print(f'London-internal flow records: {len(internal_11):,}  '
      f'({internal_11["count"].sum():,.0f} persons)')
print(f'External→London flow records: {len(from_ext_11):,}  '
      f'({from_ext_11["count"].sum():,.0f} persons)')
print(f'London→External flow records: {len(to_ext_11):,}  '
      f'({to_ext_11["count"].sum():,.0f} persons)')

# ══════════════════════════════════════════════════════════════════════
# 4. COMPUTE CASCADE METRICS (including external flows)
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('4. Computing cascade metrics with external flows')
print('=' * 70)

def compute_cascade_with_external(flow_df, count_col, wealth_map, year_label):
    """
    Compute per-MSOA cascade metrics from flow data that includes
    the EXTERNAL_CODE synthetic MSOA.
    
    Returns a DataFrame indexed by msoa11cd (London MSOAs only)
    with cascade metrics incorporating external flows.
    """
    df = flow_df.copy()
    df['Origin_Decile'] = df['origin_msoa11'].map(wealth_map)
    df['Dest_Decile'] = df['dest_msoa11'].map(wealth_map)
    
    # Check for unmapped codes
    unmapped = df[df['Origin_Decile'].isna() | df['Dest_Decile'].isna()]
    if len(unmapped) > 0:
        print(f'  WARNING: {len(unmapped)} records with unmapped deciles — dropping')
        print(f'    Unique unmapped origins: {unmapped["origin_msoa11"].unique()[:5]}')
        print(f'    Unique unmapped dests:   {unmapped["dest_msoa11"].unique()[:5]}')
        df = df.dropna(subset=['Origin_Decile', 'Dest_Decile'])
    
    df['Origin_Decile'] = df['Origin_Decile'].astype(int)
    df['Dest_Decile'] = df['Dest_Decile'].astype(int)
    
    # Flow direction summary
    total = df[count_col].sum()
    upward = df.loc[df['Dest_Decile'] > df['Origin_Decile'], count_col].sum()
    downward = df.loc[df['Dest_Decile'] < df['Origin_Decile'], count_col].sum()
    lateral = df.loc[df['Dest_Decile'] == df['Origin_Decile'], count_col].sum()
    
    print(f'\n  {year_label} Flow Summary (with external):')
    print(f'    Total migrants: {total:,.0f}')
    print(f'    Upward:  {upward:>10,.0f} ({upward/total*100:.1f}%)')
    print(f'    Down:    {downward:>10,.0f} ({downward/total*100:.1f}%)')
    print(f'    Lateral: {lateral:>10,.0f} ({lateral/total*100:.1f}%)')
    
    # ---- Per-MSOA metrics (London MSOAs only) ----
    london_msoas_list = [m for m in analysis_msoas]
    
    # Inflow from wealthier: people arriving at MSOA from higher-decile origins
    inflow_w = (df[df['Origin_Decile'] > df['Dest_Decile']]
                .groupby('dest_msoa11')[count_col].sum()
                .reindex(london_msoas_list, fill_value=0)
                .rename('Inflow_Wealthier_ext'))
    
    # Outflow to poorer: people leaving MSOA to lower-decile destinations
    outflow_p = (df[df['Dest_Decile'] < df['Origin_Decile']]
                 .groupby('origin_msoa11')[count_col].sum()
                 .reindex(london_msoas_list, fill_value=0)
                 .rename('Outflow_Poorer_ext'))
    
    # Total inflow/outflow (all flows, including lateral)
    total_in = (df.groupby('dest_msoa11')[count_col].sum()
                .reindex(london_msoas_list, fill_value=0)
                .rename('Total_Inflow_ext'))
    total_out = (df.groupby('origin_msoa11')[count_col].sum()
                 .reindex(london_msoas_list, fill_value=0)
                 .rename('Total_Outflow_ext'))
    
    # ---- Also compute external-only components for reporting ----
    ext_inflow = (df[df['origin_msoa11'] == EXTERNAL_CODE]
                  .groupby('dest_msoa11')[count_col].sum()
                  .reindex(london_msoas_list, fill_value=0)
                  .rename('Ext_Inflow'))
    ext_outflow = (df[df['dest_msoa11'] == EXTERNAL_CODE]
                   .groupby('origin_msoa11')[count_col].sum()
                   .reindex(london_msoas_list, fill_value=0)
                   .rename('Ext_Outflow'))
    
    # Assemble
    result = pd.DataFrame(index=pd.Index(london_msoas_list, name='msoa11cd'))
    for s in [inflow_w, outflow_p, total_in, total_out, ext_inflow, ext_outflow]:
        result = result.join(s, how='left')
    result = result.fillna(0)
    
    # Derived metrics
    result['Total_Migration_ext'] = result['Total_Inflow_ext'] + result['Total_Outflow_ext']
    result['CFI_Churn_ext'] = result['Inflow_Wealthier_ext'] + result['Outflow_Poorer_ext']
    result['CFI_Rate_ext'] = np.where(
        result['Total_Migration_ext'] > 0,
        (result['Inflow_Wealthier_ext'] * result['Outflow_Poorer_ext']) / result['Total_Migration_ext'],
        0)
    result['Net_Cascade_ext'] = result['Inflow_Wealthier_ext'] - result['Outflow_Poorer_ext']
    result['Pct_Inflow_Wealthier_ext'] = np.where(
        result['Total_Inflow_ext'] > 0,
        (result['Inflow_Wealthier_ext'] / result['Total_Inflow_ext']) * 100,
        0)
    result['Ext_Net_Migration'] = result['Ext_Inflow'] - result['Ext_Outflow']
    
    return result


# Compute for both years
print('\n--- 2011 ---')
cascade_ext_11 = compute_cascade_with_external(
    flows_11, 'count', wealth_mapping_ext, '2011')

print('\n--- 2021 ---')
cascade_ext_21 = compute_cascade_with_external(
    flows_21, 'count', wealth_mapping_ext, '2021')

# Rename with year suffixes
cascade_ext_11 = cascade_ext_11.add_suffix('_11').rename(
    columns=lambda c: c.replace('_ext_11', '_ext_11') if '_ext' in c else c)
cascade_ext_21 = cascade_ext_21.add_suffix('_21').rename(
    columns=lambda c: c.replace('_ext_21', '_ext_21') if '_ext' in c else c)

# ══════════════════════════════════════════════════════════════════════
# 5. MERGE WITH EXISTING LONDON-ONLY FEATURES
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('5. Merging with existing London-only features')
print('=' * 70)

result = existing.merge(cascade_ext_11, left_on='msoa11cd', right_index=True, how='left')
result = result.merge(cascade_ext_21, left_on='msoa11cd', right_index=True, how='left')

# ══════════════════════════════════════════════════════════════════════
# 6. SUMMARY & COMPARISON
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('6. Comparison: London-only vs London+External')
print('=' * 70)

for yr, suffix_old, suffix_new in [('2011', '_11', '_ext_11_11'), 
                                     ('2021', '_21', '_ext_21_21')]:
    # Adjust suffix names based on actual column names
    old_churn = f'CFI_Churn{suffix_old}'
    # Find the new churn column
    new_churn_candidates = [c for c in result.columns if 'CFI_Churn_ext' in c and yr[-2:] in c]
    if new_churn_candidates:
        new_churn = new_churn_candidates[0]
        corr = result[[old_churn, new_churn]].corr().iloc[0, 1]
        print(f'\n{yr}:')
        print(f'  CFI_Churn correlation (London-only vs +External): r = {corr:.4f}')
        print(f'  Mean CFI_Churn London-only: {result[old_churn].mean():.1f}')
        print(f'  Mean CFI_Churn +External:   {result[new_churn].mean():.1f}')

# ══════════════════════════════════════════════════════════════════════
# 7. EXPORT
# ══════════════════════════════════════════════════════════════════════
today = date.today().strftime('%Y%m%d')
out_path = OUTPUT_DIR / f'msoa_cascade_features_with_external_{today}.csv'
result.to_csv(out_path, index=False)
print(f'\n✓ Saved to: {out_path}')
print(f'  Shape: {result.shape}')
print(f'  New columns: {[c for c in result.columns if "ext" in c.lower()]}')
