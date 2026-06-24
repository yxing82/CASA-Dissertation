"""
Yee & Dennett (2022) Typology Aggregation: LSOA → MSOA
=======================================================

Purpose:
    Aggregate Yee & Dennett's LSOA-level neighbourhood change classifications
    to MSOA level for comparison with the flow-based cascade typology.

Source:
    Yee & Dennett (2022) 'Stratifying and predicting patterns of neighbourhood
    change and gentrification: An urban analytics approach', Transactions of
    the Institute of British Geographers, 47(3), 770–790.
    
    GitHub: github.com/jytg17/Unpacking-the-Nuances-of-Londons-Neighbourhood-
    Change-Gentrification-Trajectories-codes

Classification hierarchy:
    Class_1 (broadest):  ASC / DEC / STB
    Class_2 (mid):       GEN / IUP / NRW / DEC / STB
    Class_3 (finest):    SupGen / MargGen / MainGen / IUP / NRW / DEC / STB

    ASC  = Ascending          GEN     = Gentrifying
    DEC  = Declining          IUP     = Incumbent Upgrading
    STB  = Stable             NRW     = Re-urbanisation (New-build)
    SupGen  = Super-gentrification
    MargGen = Marginal gentrification
    MainGen = Mainstream gentrification

Aggregation strategy:
    Each MSOA contains ~4–8 LSOAs. We compute:
    1. Modal (majority) class — the most common LSOA type within the MSOA
    2. Proportional shares — % of LSOAs in each class within each MSOA
    3. Binary flags — whether ANY gentrifying LSOA exists in the MSOA

    The modal approach is used as the primary label; proportional shares
    provide nuance for cross-tabulation with cascade typology.

Temporal note:
    Yee's classifications cover 2001–2011 neighbourhood change, so they
    align with the 2011 cascade metrics, NOT the 2021 metrics.

Inputs:
    - LSOA_labels_forMapping.csv (from Yee's GitHub repo)
    - LSOA-to-MSOA lookup (from NSPCL postcode lookup used in preprocessing)
    - msoa_cascade_features_enriched_20260616.csv (our analysis data)

Output:
    - yee_msoa_comparison_YYYYMMDD.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import date

# ══════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════
ROOT = Path('.')
DATA_DIR = ROOT / 'data'
OUTPUT_DIR = ROOT / 'outputs'
OUTPUT_DIR.mkdir(exist_ok=True)

# Yee's classification labels (clone from GitHub or download manually)
# git clone https://github.com/jytg17/Unpacking-the-Nuances-of-Londons-Neighbourhood-Change-Gentrification-Trajectories-codes.git
YEE_LABELS_PATH = Path('yee_repo/data/LSOA_labels_forMapping.csv')

# LSOA→MSOA lookup: extracted from the NSPCL postcode lookup
# used in data_preprocess_imd_rerank_2015pop_sensitivity_check_20260615.ipynb
# The preprocessing notebook builds `london_lookup` with columns:
#   lsoa11cd, msoa11cd, ladnm
# Export it from that notebook as a CSV, or provide the path to NSPCL:
LOOKUP_PATH = DATA_DIR / 'NSPCL_NOV22_UK_LU.csv'

# Our cascade features
CASCADE_PATH = DATA_DIR / 'msoa_cascade_features_enriched_20260616.csv'

# ══════════════════════════════════════════════════════════════════════
# 1. LOAD DATA
# ══════════════════════════════════════════════════════════════════════
print('=' * 70)
print('1. Loading data')
print('=' * 70)

# ---- Yee's LSOA classifications ----
yee = pd.read_csv(YEE_LABELS_PATH)
yee = yee[['LSOA_Code', 'Class_1_status', 'Class_2_status', 'Class_3_status']].copy()
yee.rename(columns={'LSOA_Code': 'lsoa11cd'}, inplace=True)
print(f'Yee labels loaded: {len(yee)} LSOAs')

# ---- LSOA→MSOA lookup ----
print('Building LSOA→MSOA lookup from postcode directory...')
nspcl = pd.read_csv(LOOKUP_PATH, encoding='ISO-8859-1', low_memory=False)
lsoa_msoa = (nspcl[['lsoa11cd', 'msoa11cd']]
             .drop_duplicates()
             .dropna())
print(f'LSOA→MSOA mappings: {len(lsoa_msoa):,}')

# ---- Our cascade data (for the MSOA whitelist and merge) ----
cascade = pd.read_csv(CASCADE_PATH)
analysis_msoas = set(cascade['msoa11cd'].unique())
print(f'Analysis MSOAs: {len(analysis_msoas)}')

# ══════════════════════════════════════════════════════════════════════
# 2. JOIN YEE LABELS TO MSOA GEOGRAPHY
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('2. Joining Yee labels to MSOA geography')
print('=' * 70)

# Merge Yee → lookup
yee_geo = pd.merge(yee, lsoa_msoa, on='lsoa11cd', how='inner')
print(f'Yee LSOAs matched to an MSOA: {len(yee_geo)}')

# Restrict to our London analysis MSOAs
yee_london = yee_geo[yee_geo['msoa11cd'].isin(analysis_msoas)].copy()
print(f'Yee LSOAs within analysis MSOAs: {len(yee_london)}')
print(f'Covering {yee_london["msoa11cd"].nunique()} of {len(analysis_msoas)} MSOAs')

# Distribution at LSOA level
print('\nLSOA-level distribution (London, all 3 levels):')
for col in ['Class_1_status', 'Class_2_status', 'Class_3_status']:
    print(f'\n  {col}:')
    vc = yee_london[col].value_counts()
    for k, v in vc.items():
        print(f'    {k:>10s}: {v:>5d} ({v/len(yee_london)*100:.1f}%)')

# ══════════════════════════════════════════════════════════════════════
# 3. AGGREGATE TO MSOA: MODAL CLASS + PROPORTIONAL SHARES
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('3. Aggregating to MSOA level')
print('=' * 70)

def aggregate_to_msoa(lsoa_df, class_col, msoa_col='msoa11cd'):
    """
    Aggregate LSOA-level classifications to MSOA using:
    - Modal (most common) class
    - Proportional share of each class
    - Count of LSOAs per MSOA (for confidence weighting)
    """
    grouped = lsoa_df.groupby(msoa_col)
    
    # Modal class
    modal = grouped[class_col].agg(lambda x: x.value_counts().index[0])
    modal.name = f'{class_col}_modal'
    
    # Count of LSOAs
    n_lsoa = grouped[class_col].count()
    n_lsoa.name = 'n_lsoa'
    
    # Proportional shares (pivot)
    shares = (lsoa_df
              .groupby([msoa_col, class_col])
              .size()
              .unstack(fill_value=0))
    shares = shares.div(shares.sum(axis=1), axis=0)
    shares.columns = [f'pct_{c}' for c in shares.columns]
    
    # Modal confidence: proportion of LSOAs matching the modal class
    modal_pct = grouped[class_col].agg(
        lambda x: x.value_counts().iloc[0] / len(x))
    modal_pct.name = 'modal_confidence'
    
    result = pd.concat([modal, n_lsoa, modal_pct, shares], axis=1)
    return result


# Aggregate all three classification levels
agg_1 = aggregate_to_msoa(yee_london, 'Class_1_status')
agg_2 = aggregate_to_msoa(yee_london, 'Class_2_status')
agg_3 = aggregate_to_msoa(yee_london, 'Class_3_status')

# Combine (n_lsoa and modal_confidence are the same across levels for same grouping)
msoa_yee = agg_1[['Class_1_status_modal', 'n_lsoa', 'modal_confidence']].copy()
msoa_yee = msoa_yee.rename(columns={'modal_confidence': 'modal_confidence_c1'})

msoa_yee['Class_2_modal'] = agg_2['Class_2_status_modal']
msoa_yee['modal_confidence_c2'] = agg_2['modal_confidence']

msoa_yee['Class_3_modal'] = agg_3['Class_3_status_modal']
msoa_yee['modal_confidence_c3'] = agg_3['modal_confidence']

# Add proportional shares for Class_2 (the most useful level for comparison)
share_cols_c2 = [c for c in agg_2.columns if c.startswith('pct_')]
for col in share_cols_c2:
    msoa_yee[f'yee_{col}'] = agg_2[col]

# Add binary flag: does this MSOA contain ANY gentrifying LSOA?
gen_lsoas = yee_london[yee_london['Class_2_status'] == 'GEN']
msoas_with_gen = set(gen_lsoas['msoa11cd'].unique())
msoa_yee['has_gentrifying_lsoa'] = msoa_yee.index.isin(msoas_with_gen)

# Add proportional share of gentrifying LSOAs specifically
gen_share = (gen_lsoas.groupby('msoa11cd').size() / 
             yee_london.groupby('msoa11cd').size())
msoa_yee['pct_gentrifying'] = gen_share.reindex(msoa_yee.index, fill_value=0)

# Rename for clarity
msoa_yee = msoa_yee.rename(columns={
    'Class_1_status_modal': 'yee_class1',
    'Class_2_modal': 'yee_class2', 
    'Class_3_modal': 'yee_class3',
})

print(f'\nMSOA-level aggregation complete: {len(msoa_yee)} MSOAs')

print('\nMSOA-level Class_2 distribution (modal):')
vc = msoa_yee['yee_class2'].value_counts()
for k, v in vc.items():
    print(f'  {k:>5s}: {v:>4d} MSOAs ({v/len(msoa_yee)*100:.1f}%)')

print(f'\nMSOAs containing at least one gentrifying LSOA: '
      f'{msoa_yee["has_gentrifying_lsoa"].sum()}')
print(f'Mean modal confidence (Class_2): {msoa_yee["modal_confidence_c2"].mean():.2f}')
print(f'Median modal confidence (Class_2): {msoa_yee["modal_confidence_c2"].median():.2f}')

# ══════════════════════════════════════════════════════════════════════
# 4. MERGE WITH CASCADE FEATURES
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('4. Merging with cascade features')
print('=' * 70)

result = cascade.merge(msoa_yee, left_on='msoa11cd', right_index=True, how='left')
print(f'Merged dataset: {result.shape}')

# Check coverage
matched = result['yee_class2'].notna().sum()
print(f'MSOAs with Yee classification: {matched} / {len(result)}')

# ══════════════════════════════════════════════════════════════════════
# 5. CROSS-TABULATION: CASCADE TYPOLOGY vs YEE TYPOLOGY
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('5. Cross-tabulation analysis')
print('=' * 70)

# ---- 5a. Mean cascade metrics by Yee class ----
print('\n--- Mean cascade metrics (2011) by Yee Class_2 ---')
metrics_11 = ['CFI_Churn_11', 'CFI_Rate_11', 'Net_Cascade_11', 
              'Pct_Inflow_Wealthier_11', 'Total_Migration_11']
profile = result.groupby('yee_class2')[metrics_11].mean().round(2)
print(profile.to_string())

print('\n--- Mean IMD Percentile Change by Yee Class_2 ---')
imd_by_class = result.groupby('yee_class2')['IMD_Pctile_Change'].agg(['mean', 'median', 'std', 'count'])
print(imd_by_class.round(3).to_string())

# ---- 5b. Gentrifying vs non-gentrifying: cascade metric comparison ----
print('\n--- Gentrifying (any LSOA) vs Non-gentrifying MSOAs ---')
for col in metrics_11:
    gen_mean = result.loc[result['has_gentrifying_lsoa'], col].mean()
    non_mean = result.loc[~result['has_gentrifying_lsoa'], col].mean()
    print(f'  {col:>30s}:  Gen = {gen_mean:>8.2f}   Non = {non_mean:>8.2f}   '
          f'Δ = {gen_mean - non_mean:>+8.2f}')

# ── 5c. If cascade typology exists, do the cross-tab ──
# Check if we have a typology column from the typology validation notebook
typology_col = None
for candidate in ['Typology_21', 'Typology_11', 'typology_21', 'typology_11']:
    if candidate in result.columns:
        typology_col = candidate
        break

if typology_col:
    print(f'\n--- Cross-tabulation: {typology_col} × yee_class2 ---')
    ct = pd.crosstab(result[typology_col], result['yee_class2'], margins=True)
    print(ct.to_string())
    
    ct_pct = pd.crosstab(result[typology_col], result['yee_class2'], normalize='index')
    print('\n(Row percentages):')
    print((ct_pct * 100).round(1).to_string())
else:
    print('\nNote: No cascade typology column found in the features file.')
    print('After running eda_3_typology_validation, re-merge and the cross-tab')
    print('will populate automatically.')

# ══════════════════════════════════════════════════════════════════════
# 6. EXPORT
# ══════════════════════════════════════════════════════════════════════
print('\n' + '=' * 70)
print('6. Export')
print('=' * 70)

today = date.today().strftime('%Y%m%d')
out_path = OUTPUT_DIR / f'yee_msoa_comparison_{today}.csv'
result.to_csv(out_path, index=False)
print(f'✓ Saved to: {out_path}')
print(f'  Shape: {result.shape}')
print(f'  New Yee columns: {[c for c in result.columns if "yee" in c.lower() or c in ["has_gentrifying_lsoa", "pct_gentrifying", "n_lsoa"]]}')

# Also export just the Yee MSOA labels for quick use
labels_path = OUTPUT_DIR / f'yee_msoa_labels_{today}.csv'
msoa_yee.to_csv(labels_path)
print(f'✓ Yee MSOA labels also saved to: {labels_path}')
