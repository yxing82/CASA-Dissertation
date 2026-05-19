"""
Butterfly chart: Cascade flow structure by wealth decile, 2011 vs 2021
----------------------------------------------------------------------
Compares cascade inflows (from wealthier areas) and cascade outflows
(to poorer areas) across London's 10 MSOA wealth deciles for both
census periods. IMD 2010 fixed baseline, 983 London MSOAs.

Requires: matplotlib, numpy, pandas
Input:    data/msoa_cascade_features_20260518.csv
Output:   outputs/fig_butterfly_cascade.png

Folder structure:
    project/
    ├── data/
    │   └── msoa_cascade_features_20260518.csv
    ├── scripts/
    │   └── butterfly_chart.py          ← this file
    └── outputs/
        └── fig_butterfly_cascade.png   ← generated
"""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ── 0. Paths (script lives in scripts/, outputs go to outputs/) ──────
SCRIPT_DIR = Path(__file__).resolve().parent        # …/scripts
ROOT_DIR   = SCRIPT_DIR.parent                      # …/main folder
DATA_DIR   = ROOT_DIR / 'data'
OUTPUT_DIR = ROOT_DIR / 'outputs'
OUTPUT_DIR.mkdir(exist_ok=True)

# ── 1. Load & aggregate ──────────────────────────────────────────────
df = pd.read_csv(OUTPUT_DIR / 'msoa_cascade_features_20260518.csv')

agg = df.groupby('Wealth_Decile').agg(
    iw11=('Inflow_Wealthier_11', 'sum'),
    op11=('Outflow_Poorer_11',   'sum'),
    iw21=('Inflow_Wealthier_21', 'sum'),
    op21=('Outflow_Poorer_21',   'sum'),
).reset_index()

# ── 2. Plot ──────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 6.5))
fig.patch.set_facecolor('white')
ax.set_facecolor('#fafaf8')

y = np.arange(10)
h = 0.35  # bar half-height

# Cascade inflows (left side — plotted as negative so bars extend left)
ax.barh(y - h/2, -agg['iw11'] / 1000, h,
        label='Cascade inflow 2011', color='#3d9e75', alpha=0.75,
        edgecolor='white', linewidth=0.5)
ax.barh(y + h/2, -agg['iw21'] / 1000, h,
        label='Cascade inflow 2021', color='#3d9e75', alpha=0.35,
        edgecolor='white', linewidth=0.5)

# Cascade outflows (right side — positive values)
ax.barh(y - h/2, agg['op11'] / 1000, h,
        label='Cascade outflow 2011', color='#d85a30', alpha=0.75,
        edgecolor='white', linewidth=0.5)
ax.barh(y + h/2, agg['op21'] / 1000, h,
        label='Cascade outflow 2021', color='#d85a30', alpha=0.35,
        edgecolor='white', linewidth=0.5)

# ── 3. Formatting ────────────────────────────────────────────────────
ax.axvline(0, color='#333', linewidth=1.2)
ax.set_yticks(y)
ax.set_yticklabels([f'Decile {i+1}' for i in range(10)], fontsize=10)
ax.invert_yaxis()
ax.set_xlabel('Migrants (thousands)', fontsize=11)

ax.set_title(
    'Cascade flow structure by wealth decile: 2011 vs 2021\n',
    fontsize=13, fontweight='bold', pad=8,
)
ax.text(
    0.5, 1.02,
    ('Left: inflows from wealthier areas  |  Right: outflows to '
     'poorer areas  |  IMD 2010 baseline  |  983 London MSOAs'),
    transform=ax.transAxes, ha='center', fontsize=9,
    color='#666', style='italic',
)

# Directional annotations
ax.text(-35, -0.8, '← Inflow from wealthier',
        fontsize=9, color='#3d9e75', fontweight='bold', ha='center')
ax.text(25, -0.8, 'Outflow to poorer →',
        fontsize=9, color='#d85a30', fontweight='bold', ha='center')

ax.legend(loc='lower right', fontsize=8.5,
          framealpha=0.9, edgecolor='#ddd')
ax.grid(axis='x', alpha=0.3, linewidth=0.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
save_path = OUTPUT_DIR / 'fig_butterfly_cascade.png'
plt.savefig(save_path, dpi=200, bbox_inches='tight', facecolor='white')
print(f'Saved → {save_path}')
