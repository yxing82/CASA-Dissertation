"""
Three-Column Alluvial: Cascading Displacement in London
---------------------------------------------------------
Generates a self-contained HTML visualisation combining both census
periods into a single 3-column alluvial diagram:

  Column 1  →  IMD Wealth Decile 2010 (baseline)
  Column 2  →  Gentrification classification (cascade + IMD shift)
  Column 3  →  IMD Wealth Decile 2019 (outcome)

Also includes a Decile Breakdown view inspired by the Nomis census
flow tool, showing inflow/outflow bars per decile across both periods.

Requires: pandas, json
Input:    outputs/msoa_cascade_features_20260518.csv
Output:   outputs/cascade_alluvial.html

Folder structure:
    project/
    ├── data/
    │   └── meta data files
    ├── scripts/
    │   └── cascade_alluvial.py          
    └── outputs/
        └── msoa_cascade_features_20260522.csv
        └── cascade_alluvial.html      
"""

from pathlib import Path
import pandas as pd
import json

# ── 0. Paths ──────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR   = SCRIPT_DIR.parent
OUTPUT_DIR = ROOT_DIR / 'outputs'
OUTPUT_DIR.mkdir(exist_ok=True)

# ── 1. Load data ──────────────────────────────────────────────────────
df = pd.read_csv(OUTPUT_DIR / 'msoa_cascade_features_20260518.csv')
print(f'Loaded {len(df)} MSOAs across {df["ladnm"].nunique()} boroughs')

# ── 2. Compute classifications ────────────────────────────────────────
df['decile_shift'] = df['Wealth_Decile_2019'] - df['Wealth_Decile']

def classify(row):
    nc11 = row['Net_Cascade_11']
    nc21 = row['Net_Cascade_21']
    shift = row['decile_shift']
    has_pressure = (nc11 > 0) or (nc21 > 0)
    if shift >= 2 and has_pressure:
        return 'Strong Gentrification'
    elif shift >= 1 and has_pressure:
        return 'Emerging Gentrification'
    elif shift == 0 and nc11 > 0 and nc21 > 0:
        return 'Cascade Pressure'
    elif shift == 0:
        return 'Stable'
    elif shift <= -2:
        return 'Strong Decline'
    elif shift == -1:
        return 'Mild Decline'
    else:
        return 'Transitional'

df['category'] = df.apply(classify, axis=1)
print(f'Classification distribution:\n{df["category"].value_counts()}')

# ── 3. Build flow matrices ────────────────────────────────────────────
CATEGORIES = [
    'Strong Gentrification', 'Emerging Gentrification',
    'Cascade Pressure', 'Transitional', 'Stable',
    'Mild Decline', 'Strong Decline',
]

# Left→Middle flows
lm_flows = (
    df.groupby(['Wealth_Decile', 'category'])
    .size().reset_index(name='count')
)
lm_list = []
for _, r in lm_flows.iterrows():
    lm_list.append([int(r['Wealth_Decile']), r['category'], int(r['count'])])

# Middle→Right flows
mr_flows = (
    df.groupby(['category', 'Wealth_Decile_2019'])
    .size().reset_index(name='count')
)
mr_list = []
for _, r in mr_flows.iterrows():
    mr_list.append([r['category'], int(r['Wealth_Decile_2019']), int(r['count'])])

# Decile aggregate stats
decile_stats = []
for d in range(1, 11):
    sub = df[df['Wealth_Decile'] == d]
    decile_stats.append({
        'd': d,
        'n': len(sub),
        'iw11': round(sub['Inflow_Wealthier_11'].sum()),
        'op11': round(sub['Outflow_Poorer_11'].sum()),
        'nc11': round(sub['Net_Cascade_11'].sum()),
        'tm11': round(sub['Total_Migration_11'].sum()),
        'iw21': round(sub['Inflow_Wealthier_21'].sum()),
        'op21': round(sub['Outflow_Poorer_21'].sum()),
        'nc21': round(sub['Net_Cascade_21'].sum()),
        'tm21': round(sub['Total_Migration_21'].sum()),
    })

# Category descriptions
cat_descriptions = {
    'Strong Gentrification': 'MSOAs that shifted ≥2 deciles upward with positive net cascade — strong affluent inflow coinciding with significant neighbourhood uplift.',
    'Emerging Gentrification': 'MSOAs that shifted 1 decile upward with positive net cascade — early-stage gentrification where cascade pressure is translating into compositional change.',
    'Cascade Pressure': 'MSOAs with sustained positive net cascade across both periods but no decile shift — gentrification pressure without (yet) tipping the neighbourhood.',
    'Transitional': 'MSOAs with mixed signals — some cascade activity but primarily lateral moves or non-cascade-driven change.',
    'Stable': 'No decile shift and no significant cascade pressure — the neighbourhood hierarchy held across both periods.',
    'Mild Decline': 'MSOAs that shifted 1 decile downward — becoming relatively more deprived, potentially receiving displaced residents.',
    'Strong Decline': 'MSOAs that shifted ≥2 deciles downward — significant relative deprivation increase, often at the receiving end of displacement chains.',
}

# Pack into JSON
data_payload = json.dumps({
    'lm': lm_list,
    'mr': mr_list,
    'cats': CATEGORIES,
    'stats': decile_stats,
    'descs': cat_descriptions,
    'total': len(df),
}, separators=(',', ':'))

print(f'Embedded JSON size: {len(data_payload)/1024:.0f} KB')

# ── 4. HTML template ──────────────────────────────────────────────────
HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cascading Displacement in London — Three-Column Alluvial</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#fafaf7;--card:#fff;--border:#e5e5e2;--t1:#111;--t2:#333;--t3:#666;--t4:#999;--t5:#ccc;
  --blue:#2563eb;--cyan:#0891b2;--violet:#7c3aed;--slate:#64748b;--red:#dc2626;
  --orange:#ea580c;--emerald:#059669;
}
body{font-family:'DM Sans','Helvetica Neue',sans-serif;background:var(--bg);color:var(--t2);
  -webkit-font-smoothing:antialiased}
.app{max-width:1120px;margin:0 auto;padding:24px 20px 40px}
h1{font-family:'DM Serif Display',Georgia,serif;font-size:26px;font-weight:400;color:var(--t1);
  line-height:1.2;margin:0}
.subtitle{font-size:13px;color:var(--t3);margin:6px 0 0;line-height:1.55;max-width:740px}
.controls{display:flex;gap:6px;margin:16px 0}
.controls button{padding:6px 18px;border-radius:6px;border:1.5px solid var(--border);background:transparent;
  color:var(--t3);font-size:12px;font-weight:600;cursor:pointer;font-family:inherit;transition:all .15s}
.controls button.active{border-color:var(--t1);background:var(--t1);color:#fff}
.controls button:hover:not(.active){border-color:#bbb;color:var(--t2)}

/* Legend */
.legend{display:flex;flex-wrap:wrap;gap:14px;margin:0 0 12px 4px}
.legend-item{display:flex;align-items:center;gap:6px;cursor:pointer;transition:opacity .15s;user-select:none}
.legend-item.dim{opacity:.3}
.legend-dot{width:12px;height:12px;border-radius:3px}
.legend-label{font-size:11.5px;font-weight:500;color:var(--t2)}
.legend-count{font-size:10px;color:var(--t4)}

/* SVG */
.svg-wrap{position:relative;overflow-x:auto}
.svg-wrap svg{display:block;margin:0 auto}
.hint{text-align:center;color:var(--t4);font-size:12px;margin-top:12px}

/* Detail panel */
.detail{background:var(--card);border:1px solid var(--border);border-radius:10px;
  padding:16px 20px;margin-top:16px;box-shadow:0 1px 4px rgba(0,0,0,.04)}
.detail-header{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.detail-dot{width:14px;height:14px;border-radius:4px}
.detail-title{font-size:16px;font-weight:700;color:var(--t1);font-family:'DM Serif Display',serif}
.detail-count{font-size:13px;color:var(--t4)}
.detail-desc{font-size:12.5px;color:var(--t3);line-height:1.55;margin-bottom:14px}
.detail-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.detail-col-title{font-size:11px;font-weight:700;color:var(--t2);text-transform:uppercase;
  letter-spacing:.04em;margin-bottom:6px}
.bar-row{display:flex;align-items:center;gap:8px;padding:3px 0;font-size:11px}
.bar-label{width:28px;color:var(--t3);font-weight:500}
.bar-track{flex:1;height:14px;background:#f0f0ed;border-radius:3px;overflow:hidden}
.bar-fill{height:100%;border-radius:3px;min-width:3px}
.bar-val{width:36px;text-align:right;color:var(--t3);font-weight:500}

/* Breakdown view */
.breakdown-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(490px,1fr));gap:14px}
.decile-card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 16px}
.decile-head{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px}
.decile-badge{width:28px;height:28px;border-radius:6px;display:flex;align-items:center;
  justify-content:center;color:#fff;font-size:12px;font-weight:700}
.decile-info{margin-left:8px}
.decile-name{font-size:13px;font-weight:700;color:var(--t1)}
.decile-sub{font-size:10px;color:var(--t4)}
.decile-delta-label{font-size:10px;color:var(--t4);text-transform:uppercase;letter-spacing:.04em;text-align:right}
.decile-delta-val{font-size:14px;font-weight:700;text-align:right}
.flow-row{display:grid;grid-template-columns:36px 1fr 56px 1fr 80px;align-items:center;gap:4px;
  margin-bottom:3px;font-size:10px}
.flow-year{font-weight:600;color:var(--t3)}
.flow-in{display:flex;justify-content:flex-end;align-items:center;gap:4px}
.flow-out{display:flex;justify-content:flex-start;align-items:center;gap:4px}
.flow-bar{height:14px;border-radius:3px}
.flow-center{text-align:center;font-size:8px;color:#bbb;text-transform:uppercase}
.flow-net{text-align:right;font-weight:600;font-size:10px}
.decile-footer{margin-top:6px;padding-top:6px;border-top:1px solid #f0f0ed;font-size:9.5px;color:var(--t4)}

.insight-box{margin-top:16px;background:var(--card);border:1px solid var(--border);border-radius:10px;
  padding:14px 18px}
.insight-title{font-size:13px;font-weight:700;color:var(--t1);margin-bottom:6px;
  font-family:'DM Serif Display',serif}
.insight-text{font-size:12px;color:var(--t3);line-height:1.6}

.source{max-width:1120px;margin:20px auto 0;padding-top:12px;border-top:1px solid var(--border);
  font-size:10px;color:var(--t4);line-height:1.6}
</style>
</head>
<body>
<div class="app">
  <h1>Cascading Displacement in London</h1>
  <p class="subtitle">
    Three-column alluvial showing how 983 London MSOAs flow from their <strong>2010 IMD decile</strong>
    through a <strong>gentrification classification</strong> to their <strong>2019 IMD decile</strong>.
    Census O-D data from 2011 &amp; 2021 defines cascade flows; IMD percentile change validates the
    classification.
  </p>
  <div class="controls">
    <button id="btnAlluvial" class="active" onclick="switchView('alluvial')">Alluvial Flow</button>
    <button id="btnBreakdown" onclick="switchView('breakdown')">Decile Breakdown</button>
  </div>

  <div id="viewAlluvial">
    <div class="legend" id="legend"></div>
    <div class="svg-wrap"><svg id="alluvialSvg"></svg></div>
    <div id="detailPanel"></div>
    <p class="hint" id="hintText">Hover or click a category in the middle column to see inflow / outflow breakdown</p>
  </div>

  <div id="viewBreakdown" style="display:none">
    <p style="font-size:12.5px;color:var(--t3);margin:0 0 16px;line-height:1.5">
      Aggregate cascade flows by wealth decile — showing inflow from wealthier areas and outflow to
      poorer areas, across both census periods. Inspired by the
      <a href="https://www.nomisweb.co.uk/census/2011/wu01uk/chart" target="_blank"
         style="color:var(--blue)">Nomis census flow tool</a>.
    </p>
    <div class="breakdown-grid" id="breakdownGrid"></div>
    <div class="insight-box">
      <div class="insight-title">Reading the pattern</div>
      <p class="insight-text">
        Deciles 1–5 (most deprived) show net positive cascade — more people arriving from wealthier areas
        than leaving to poorer ones. This is the gentrification signal. Deciles 6–10 show the mirror: net
        negative cascade, as outflows to poorer areas exceed inflows from wealthier. The pattern persists
        across both census periods, though cascade volumes decreased slightly between 2011 and 2021. The
        symmetry pivot around Decile 5 is the clearest fingerprint of the cascading displacement mechanism.
      </p>
    </div>
  </div>
</div>

<div class="source">
  Data: ONS Census Origin-Destination 2011 &amp; 2021 · IMD 2010 &amp; 2019 (MHCLG) ·
  983 London MSOAs · Wealth deciles from mean LSOA-to-MSOA IMD scores ·
  Classification: cascade direction (Net Cascade) × IMD decile shift (2010→2019)
</div>

<script>
// ── DATA (injected by Python) ────────────────────────────────────────
const D = DATA_PLACEHOLDER;

// ── CONSTANTS ────────────────────────────────────────────────────────
const CAT_COLORS = {
  'Strong Gentrification':'#1d4ed8','Emerging Gentrification':'#2563eb',
  'Cascade Pressure':'#0891b2','Transitional':'#7c3aed',
  'Stable':'#64748b','Mild Decline':'#ea580c','Strong Decline':'#dc2626'
};
const DECILE_COLORS = [
  '#991b1b','#b91c1c','#dc2626','#ef4444','#f87171',
  '#86efac','#4ade80','#22c55e','#16a34a','#15803d'
];

let currentView = 'alluvial';
let selectedCat = null;
let hoveredCat = null;

// ── UTILITIES ────────────────────────────────────────────────────────
function fmt(n){ return Math.abs(n)>=1000?(n/1000).toFixed(1)+'k':n.toLocaleString() }
function fmtS(n){ return (n>0?'+':'')+fmt(n) }

// ── VIEW SWITCHING ───────────────────────────────────────────────────
function switchView(v){
  currentView = v;
  document.getElementById('btnAlluvial').classList.toggle('active', v==='alluvial');
  document.getElementById('btnBreakdown').classList.toggle('active', v==='breakdown');
  document.getElementById('viewAlluvial').style.display = v==='alluvial'?'':'none';
  document.getElementById('viewBreakdown').style.display = v==='breakdown'?'':'none';
}

// ── ALLUVIAL LAYOUT ──────────────────────────────────────────────────
function computeLayout(){
  const W = Math.min(window.innerWidth - 60, 1080);
  const H = 680;
  const pad = {top:58, bottom:28, left:18, right:18};
  const colW = Math.min(130, W * 0.13);
  const gap = (W - pad.left - pad.right - colW*3) / 2;
  const usableH = H - pad.top - pad.bottom;
  const nodeGap = 3;

  // Left column totals
  const leftTotals = [];
  for(let d=1;d<=10;d++){
    leftTotals.push(D.lm.filter(f=>f[0]===d).reduce((s,f)=>s+f[2],0));
  }
  const total = leftTotals.reduce((s,v)=>s+v,0);
  const scale = (usableH - 9*nodeGap) / total;

  // Left nodes
  const leftNodes = [];
  let cy = pad.top;
  for(let i=0;i<10;i++){
    const h = leftTotals[i]*scale;
    leftNodes.push({d:i+1, x:pad.left, y:cy, w:colW, h, count:leftTotals[i]});
    cy += h + nodeGap;
  }

  // Mid totals
  const midTotals = {};
  D.cats.forEach(c=>{ midTotals[c]=D.lm.filter(f=>f[1]===c).reduce((s,f)=>s+f[2],0) });
  const midNodes = [];
  cy = pad.top;
  D.cats.forEach(c=>{
    const h = midTotals[c]*scale;
    midNodes.push({cat:c, x:pad.left+colW+gap, y:cy, w:colW, h, count:midTotals[c]});
    cy += h + nodeGap;
  });

  // Right totals
  const rightTotals = [];
  for(let d=1;d<=10;d++){
    rightTotals.push(D.mr.filter(f=>f[1]===d).reduce((s,f)=>s+f[2],0));
  }
  const rightNodes = [];
  cy = pad.top;
  for(let i=0;i<10;i++){
    const h = rightTotals[i]*scale;
    rightNodes.push({d:i+1, x:pad.left+colW*2+gap*2, y:cy, w:colW, h, count:rightTotals[i]});
    cy += h + nodeGap;
  }

  // Left→Mid bands
  const lmBands = [];
  const lOff = new Array(10).fill(0);
  const mLOff = {};
  D.cats.forEach(c=>mLOff[c]=0);
  for(const [fromD,cat,count] of D.lm){
    const li = fromD-1;
    const mn = midNodes.find(n=>n.cat===cat);
    if(!mn) continue;
    const h = count*scale;
    lmBands.push({fromD, cat, count, sx:pad.left+colW, sy:leftNodes[li].y+lOff[li],
      dx:mn.x, dy:mn.y+mLOff[cat], h:Math.max(h,.5)});
    lOff[li] += h;
    mLOff[cat] += h;
  }

  // Mid→Right bands
  const mrBands = [];
  const mROff = {};
  D.cats.forEach(c=>mROff[c]=0);
  const rOff = new Array(10).fill(0);
  for(const [cat,toD,count] of D.mr){
    const mn = midNodes.find(n=>n.cat===cat);
    const ri = toD-1;
    if(!mn) continue;
    const h = count*scale;
    mrBands.push({cat, toD, count, sx:mn.x+colW, sy:mn.y+mROff[cat],
      dx:rightNodes[ri].x, dy:rightNodes[ri].y+rOff[ri], h:Math.max(h,.5)});
    mROff[cat] += h;
    rOff[ri] += h;
  }

  return {W, H, pad, colW, leftNodes, midNodes, rightNodes, lmBands, mrBands};
}

function bandPath(sx,sy,dx,dy,h){
  const mx=(sx+dx)/2;
  return `M${sx},${sy} C${mx},${sy} ${mx},${dy} ${dx},${dy} L${dx},${dy+h} C${mx},${dy+h} ${mx},${sy+h} ${sx},${sy+h} Z`;
}

// ── DRAW ALLUVIAL ────────────────────────────────────────────────────
function drawAlluvial(){
  const L = computeLayout();
  const svg = document.getElementById('alluvialSvg');
  svg.setAttribute('width', L.W);
  svg.setAttribute('height', L.H);
  svg.setAttribute('viewBox', `0 0 ${L.W} ${L.H}`);

  let html = '';

  // Column headers
  const lCx = L.pad.left + L.colW/2;
  const mCx = L.midNodes[0].x + L.colW/2;
  const rCx = L.rightNodes[0].x + L.colW/2;
  html += `<text x="${lCx}" y="24" text-anchor="middle" font-size="13" font-weight="700" fill="#333" font-family="DM Sans">IMD Decile 2010</text>`;
  html += `<text x="${lCx}" y="40" text-anchor="middle" font-size="10" fill="#999" font-family="DM Sans">(baseline)</text>`;
  html += `<text x="${mCx}" y="24" text-anchor="middle" font-size="13" font-weight="700" fill="#333" font-family="DM Sans">Classification</text>`;
  html += `<text x="${mCx}" y="40" text-anchor="middle" font-size="10" fill="#999" font-family="DM Sans">(cascade + IMD shift)</text>`;
  html += `<text x="${rCx}" y="24" text-anchor="middle" font-size="13" font-weight="700" fill="#333" font-family="DM Sans">IMD Decile 2019</text>`;
  html += `<text x="${rCx}" y="40" text-anchor="middle" font-size="10" fill="#999" font-family="DM Sans">(outcome)</text>`;

  // Deprivation labels
  html += `<text x="${L.pad.left-4}" y="${L.leftNodes[0].y+8}" text-anchor="end" font-size="8" fill="#b91c1c" font-weight="600" font-family="DM Sans">Most deprived ↑</text>`;
  html += `<text x="${L.pad.left-4}" y="${L.leftNodes[9].y+L.leftNodes[9].h-2}" text-anchor="end" font-size="8" fill="#15803d" font-weight="600" font-family="DM Sans">Least deprived ↓</text>`;

  // LM bands
  L.lmBands.forEach((b,i)=>{
    const active = selectedCat ? b.cat===selectedCat : (!hoveredCat || b.cat===hoveredCat);
    html += `<path d="${bandPath(b.sx,b.sy,b.dx,b.dy,b.h)}" fill="${CAT_COLORS[b.cat]}"
      opacity="${active?0.38:0.04}" class="band" data-cat="${b.cat}"
      onmouseenter="hoverCat('${b.cat}')" />`;
  });

  // MR bands
  L.mrBands.forEach((b,i)=>{
    const active = selectedCat ? b.cat===selectedCat : (!hoveredCat || b.cat===hoveredCat);
    html += `<path d="${bandPath(b.sx,b.sy,b.dx,b.dy,b.h)}" fill="${CAT_COLORS[b.cat]}"
      opacity="${active?0.38:0.04}" class="band" data-cat="${b.cat}"
      onmouseenter="hoverCat('${b.cat}')" />`;
  });

  // Left nodes
  L.leftNodes.forEach((n,i)=>{
    html += `<rect x="${n.x}" y="${n.y}" width="${n.w}" height="${Math.max(n.h,2)}" rx="4"
      fill="${DECILE_COLORS[i]}" opacity="0.88"/>`;
    if(n.h>14){
      html += `<text x="${n.x+n.w/2}" y="${n.y+n.h/2+1}" text-anchor="middle"
        dominant-baseline="central" font-size="10.5" font-weight="600" fill="#fff"
        font-family="DM Sans" style="pointer-events:none">D${n.d} — ${n.count}</text>`;
    }
  });

  // Mid nodes
  L.midNodes.forEach((n,i)=>{
    const active = selectedCat ? n.cat===selectedCat : (!hoveredCat || n.cat===hoveredCat);
    html += `<rect x="${n.x}" y="${n.y}" width="${n.w}" height="${Math.max(n.h,2)}" rx="4"
      fill="${CAT_COLORS[n.cat]}" opacity="${active?0.88:0.25}" class="mid-node" data-cat="${n.cat}"
      style="cursor:pointer" onmouseenter="hoverCat('${n.cat}')" onclick="clickCat('${n.cat}')"/>`;
    if(n.h>28){
      // Split long labels
      const label = n.cat;
      const words = label.split(' ');
      if(words.length > 1 && n.h > 36){
        html += `<text x="${n.x+n.w/2}" y="${n.y+n.h/2-8}" text-anchor="middle"
          dominant-baseline="central" font-size="10" font-weight="700" fill="#fff"
          font-family="DM Sans" style="pointer-events:none">${words[0]}</text>`;
        html += `<text x="${n.x+n.w/2}" y="${n.y+n.h/2+4}" text-anchor="middle"
          dominant-baseline="central" font-size="10" font-weight="700" fill="#fff"
          font-family="DM Sans" style="pointer-events:none">${words.slice(1).join(' ')}</text>`;
        html += `<text x="${n.x+n.w/2}" y="${n.y+n.h/2+17}" text-anchor="middle"
          dominant-baseline="central" font-size="9" fill="rgba(255,255,255,.7)"
          font-family="DM Sans" style="pointer-events:none">${n.count} MSOAs</text>`;
      } else {
        html += `<text x="${n.x+n.w/2}" y="${n.y+n.h/2-4}" text-anchor="middle"
          dominant-baseline="central" font-size="10" font-weight="700" fill="#fff"
          font-family="DM Sans" style="pointer-events:none">${label}</text>`;
        html += `<text x="${n.x+n.w/2}" y="${n.y+n.h/2+10}" text-anchor="middle"
          dominant-baseline="central" font-size="9" fill="rgba(255,255,255,.7)"
          font-family="DM Sans" style="pointer-events:none">${n.count} MSOAs</text>`;
      }
    } else if(n.h>14){
      html += `<text x="${n.x+n.w/2}" y="${n.y+n.h/2+1}" text-anchor="middle"
        dominant-baseline="central" font-size="9" font-weight="600" fill="#fff"
        font-family="DM Sans" style="pointer-events:none">${n.cat} (${n.count})</text>`;
    }
  });

  // Right nodes
  L.rightNodes.forEach((n,i)=>{
    html += `<rect x="${n.x}" y="${n.y}" width="${n.w}" height="${Math.max(n.h,2)}" rx="4"
      fill="${DECILE_COLORS[i]}" opacity="0.88"/>`;
    if(n.h>14){
      html += `<text x="${n.x+n.w/2}" y="${n.y+n.h/2+1}" text-anchor="middle"
        dominant-baseline="central" font-size="10.5" font-weight="600" fill="#fff"
        font-family="DM Sans" style="pointer-events:none">D${n.d} — ${n.count}</text>`;
    }
  });

  svg.innerHTML = html;
}

// ── HOVER / CLICK ────────────────────────────────────────────────────
function hoverCat(cat){
  if(selectedCat) return;
  hoveredCat = cat;
  updateBandOpacity();
  showDetail(cat);
}

function clearHover(){
  if(selectedCat) return;
  hoveredCat = null;
  updateBandOpacity();
  document.getElementById('detailPanel').innerHTML = '';
  document.getElementById('hintText').style.display = '';
}

function clickCat(cat){
  selectedCat = selectedCat===cat ? null : cat;
  hoveredCat = null;
  updateBandOpacity();
  updateLegend();
  if(selectedCat){
    showDetail(selectedCat);
  } else {
    document.getElementById('detailPanel').innerHTML = '';
    document.getElementById('hintText').style.display = '';
  }
}

function updateBandOpacity(){
  const active = selectedCat || hoveredCat;
  document.querySelectorAll('.band').forEach(el=>{
    const cat = el.getAttribute('data-cat');
    el.setAttribute('opacity', !active || cat===active ? 0.38 : 0.04);
  });
  document.querySelectorAll('.mid-node').forEach(el=>{
    const cat = el.getAttribute('data-cat');
    el.setAttribute('opacity', !active || cat===active ? 0.88 : 0.25);
  });
}

// ── DETAIL PANEL ─────────────────────────────────────────────────────
function showDetail(cat){
  document.getElementById('hintText').style.display = 'none';
  const total = D.lm.filter(f=>f[1]===cat).reduce((s,f)=>s+f[2],0);
  const fromD = {};
  D.lm.filter(f=>f[1]===cat).forEach(f=>{ fromD[f[0]]=f[2] });
  const toD = {};
  D.mr.filter(f=>f[0]===cat).forEach(f=>{ toD[f[1]]=f[2] });

  let html = `
    <div class="detail-header">
      <div class="detail-dot" style="background:${CAT_COLORS[cat]}"></div>
      <span class="detail-title">${cat}</span>
      <span class="detail-count">— ${total} MSOAs (${(total/D.total*100).toFixed(1)}%)</span>
    </div>
    <p class="detail-desc">${D.descs[cat]||''}</p>
    <div class="detail-grid">
      <div>
        <div class="detail-col-title">← Origin: 2010 IMD Decile</div>`;

  for(let d=1;d<=10;d++){
    const v = fromD[d]||0;
    if(!v) continue;
    const pct = v/total*100;
    html += `<div class="bar-row">
      <span class="bar-label">D${d}</span>
      <div class="bar-track"><div class="bar-fill" style="width:${pct}%;background:${DECILE_COLORS[d-1]};opacity:.7"></div></div>
      <span class="bar-val">${v}</span>
    </div>`;
  }

  html += `</div><div><div class="detail-col-title">Destination: 2019 IMD Decile →</div>`;

  for(let d=1;d<=10;d++){
    const v = toD[d]||0;
    if(!v) continue;
    const pct = v/total*100;
    html += `<div class="bar-row">
      <span class="bar-label">D${d}</span>
      <div class="bar-track"><div class="bar-fill" style="width:${pct}%;background:${DECILE_COLORS[d-1]};opacity:.7"></div></div>
      <span class="bar-val">${v}</span>
    </div>`;
  }

  html += '</div></div>';
  document.getElementById('detailPanel').innerHTML = html;
}

// ── LEGEND ───────────────────────────────────────────────────────────
function buildLegend(){
  const el = document.getElementById('legend');
  let html = '';
  D.cats.forEach(c=>{
    const n = D.lm.filter(f=>f[1]===c).reduce((s,f)=>s+f[2],0);
    html += `<div class="legend-item" id="leg_${c.replace(/\s/g,'_')}" onclick="clickCat('${c}')"
      onmouseenter="hoverCat('${c}')" onmouseleave="clearHover()">
      <div class="legend-dot" style="background:${CAT_COLORS[c]}"></div>
      <span class="legend-label">${c}</span>
      <span class="legend-count">(${n})</span>
    </div>`;
  });
  el.innerHTML = html;
}

function updateLegend(){
  D.cats.forEach(c=>{
    const el = document.getElementById('leg_'+c.replace(/\s/g,'_'));
    if(!el) return;
    el.classList.toggle('dim', selectedCat && selectedCat!==c);
  });
}

// ── BREAKDOWN VIEW ───────────────────────────────────────────────────
function drawBreakdown(){
  const grid = document.getElementById('breakdownGrid');
  let html = '';
  D.stats.forEach(ds=>{
    const maxBar = Math.max(ds.iw11, ds.op11, ds.iw21, ds.op21);
    const barScale = 180 / (maxBar||1);
    const delta = ds.nc21 - ds.nc11;
    const dcol = delta>0?'var(--blue)':delta<0?'var(--red)':'var(--t4)';

    html += `<div class="decile-card">
      <div class="decile-head">
        <div style="display:flex;align-items:center">
          <div class="decile-badge" style="background:${DECILE_COLORS[ds.d-1]}">${ds.d}</div>
          <div class="decile-info">
            <div class="decile-name">Decile ${ds.d}</div>
            <div class="decile-sub">${ds.d<=3?'Most deprived':ds.d<=7?'Mid-range':'Least deprived'} · ${ds.n} MSOAs</div>
          </div>
        </div>
        <div>
          <div class="decile-delta-label">Net Cascade Δ</div>
          <div class="decile-delta-val" style="color:${dcol}">${fmtS(delta)}</div>
        </div>
      </div>`;

    [{y:'2011',iw:ds.iw11,op:ds.op11,nc:ds.nc11,tm:ds.tm11},
     {y:'2021',iw:ds.iw21,op:ds.op21,nc:ds.nc21,tm:ds.tm21}].forEach(r=>{
      const ncCol = r.nc>=0?'var(--blue)':'var(--red)';
      const opac = r.y==='2011'?0.75:0.4;
      html += `<div class="flow-row">
        <span class="flow-year">${r.y}</span>
        <div class="flow-in">
          <span style="color:var(--blue);font-size:9px;font-weight:500">${fmt(r.iw)}</span>
          <div class="flow-bar" style="width:${r.iw*barScale}px;background:var(--blue);opacity:${opac}"></div>
        </div>
        <div class="flow-center">← in | out →</div>
        <div class="flow-out">
          <div class="flow-bar" style="width:${r.op*barScale}px;background:var(--red);opacity:${opac}"></div>
          <span style="color:var(--red);font-size:9px;font-weight:500">${fmt(r.op)}</span>
        </div>
        <div class="flow-net" style="color:${ncCol}">Net: ${fmtS(r.nc)}</div>
      </div>`;
    });

    html += `<div class="decile-footer">Total migration: ${fmt(ds.tm11)} (2011) → ${fmt(ds.tm21)} (2021)</div>
    </div>`;
  });
  grid.innerHTML = html;
}

// ── INIT ─────────────────────────────────────────────────────────────
function init(){
  buildLegend();
  drawAlluvial();
  drawBreakdown();

  // Clear hover when leaving SVG
  document.getElementById('alluvialSvg').addEventListener('mouseleave', clearHover);

  // Redraw on resize
  let resizeTimer;
  window.addEventListener('resize', ()=>{
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(()=>{ drawAlluvial(); }, 150);
  });
}

init();
</script>
</body>
</html>'''

# ── 5. Inject data & write ────────────────────────────────────────────
html_out = HTML_TEMPLATE.replace('DATA_PLACEHOLDER', data_payload)

out_path = OUTPUT_DIR / 'cascade_alluvial.html'
out_path.write_text(html_out, encoding='utf-8')

print(f'\nSaved → {out_path}')
print(f'File size: {out_path.stat().st_size / 1024:.0f} KB')
