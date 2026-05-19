"""
Interactive Cascade Explorer: Borough & MSOA flow profiles
-----------------------------------------------------------
Generates a self-contained HTML app that lets users:
  - Toggle between Borough-level and MSOA-level views
  - Select any London borough from a dropdown
  - Drill into individual MSOAs (with borough context)
  - Switch between 2011 and 2021 census data
  - See Sankey-style flow diagrams + key metrics

Requires: pandas, json
Input:    data/msoa_cascade_features_20260518.csv
Output:   outputs/cascade_explorer.html

Folder structure:
    project/
    ├── data/
    │   └── meta data files
    ├── scripts/
    │   └── cascade_explorer.py          
    └── outputs/
        └── msoa_cascade_features_20260518.csv
        └── cascade_explorer.html        
"""

from pathlib import Path
import pandas as pd
import json

# ── 0. Paths ─────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR   = SCRIPT_DIR.parent
DATA_DIR   = ROOT_DIR / 'data'
OUTPUT_DIR = ROOT_DIR / 'outputs'
OUTPUT_DIR.mkdir(exist_ok=True)

# ── 1. Load & compact ───────────────────────────────────────────────
df = pd.read_csv(OUTPUT_DIR / 'msoa_cascade_features_20260518.csv')

records = []
for _, r in df.iterrows():
    records.append({
        'id': r['msoa11cd'],
        'b':  r['ladnm'],
        'd':  int(r['Wealth_Decile']),
        'iw11': round(r['Inflow_Wealthier_11'], 1),
        'op11': round(r['Outflow_Poorer_11'], 1),
        'ti11': int(r['Total_Inflow_11']),
        'to11': int(r['Total_Outflow_11']),
        'tm11': int(r['Total_Migration_11']),
        'ch11': round(r['CFI_Churn_11'], 1),
        'cr11': round(r['CFI_Rate_11'], 2),
        'nc11': round(r['Net_Cascade_11'], 1),
        'pi11': round(r['Pct_Inflow_Wealthier_11'], 1),
        'iw21': round(r['Inflow_Wealthier_21'], 1),
        'op21': round(r['Outflow_Poorer_21'], 1),
        'ti21': round(r['Total_Inflow_21'], 1),
        'to21': round(r['Total_Outflow_21'], 1),
        'tm21': round(r['Total_Migration_21'], 1),
        'ch21': round(r['CFI_Churn_21'], 1),
        'cr21': round(r['CFI_Rate_21'], 2),
        'nc21': round(r['Net_Cascade_21'], 1),
        'pi21': round(r['Pct_Inflow_Wealthier_21'], 1),
        'imd10': round(r['IMD_2010'], 2),
        'imd19': round(r['IMD_2019'], 2),
        'imdc': round(r['IMD_Pctile_Change'], 4),
    })

data_json = json.dumps(records, separators=(',', ':'))
print(f'Loaded {len(records)} MSOAs across {df["ladnm"].nunique()} boroughs')
print(f'Embedded JSON size: {len(data_json)/1024:.0f} KB')

# ── 2. HTML template ─────────────────────────────────────────────────
# The template is a single self-contained HTML file with:
#   - All CSS inline
#   - All JS inline
#   - The MSOA data embedded as a JS constant
#
# DATA_PLACEHOLDER is replaced with the actual JSON at build time.

HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cascading Displacement Explorer — London MSOAs</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0c0f14;--bg2:#12151c;--bg3:#181c24;--border:#222830;--t1:#f0ede5;
  --t2:#c0bdb5;--t3:#8a8780;--t4:#5a5850;--green:#3d9e75;--green2:#2a7555;
  --orange:#d85a30;--orange2:#a04520;--blue:#4a90d9;--purple:#8b6cc1}
body{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--t2);min-height:100vh}
.app{max-width:1100px;margin:0 auto;padding:1.5rem}
h1{font-size:1.4rem;font-weight:600;color:var(--t1);letter-spacing:-0.02em}
.subtitle{font-size:0.8rem;color:var(--t3);margin-top:4px;line-height:1.5}
.controls{display:flex;gap:0.5rem;margin:1.2rem 0;flex-wrap:wrap;align-items:center}
.control-group{display:flex;align-items:center;gap:0.4rem}
.control-group label{font-size:0.75rem;color:var(--t3);text-transform:uppercase;letter-spacing:0.05em;white-space:nowrap}
select{padding:6px 28px 6px 10px;background:var(--bg2);color:var(--t2);border:1px solid var(--border);
  border-radius:6px;font-size:0.82rem;cursor:pointer;appearance:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%238a8780'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 8px center;min-width:140px}
select:focus{outline:none;border-color:var(--green)}
.toggle{display:flex;border:1px solid var(--border);border-radius:6px;overflow:hidden}
.toggle button{padding:6px 14px;background:var(--bg2);color:var(--t3);border:none;font-size:0.8rem;
  cursor:pointer;transition:all .15s;white-space:nowrap}
.toggle button:not(:last-child){border-right:1px solid var(--border)}
.toggle button.active{background:var(--green2);color:#b8f0d4}
.toggle button:hover:not(.active){background:var(--bg3);color:var(--t2)}
.main{display:grid;grid-template-columns:1fr;gap:1rem}
.card{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:1.2rem}
.card-title{font-size:0.72rem;text-transform:uppercase;letter-spacing:0.06em;color:var(--t3);margin-bottom:0.8rem}
.sankey-wrap{position:relative}
.sankey-wrap svg{display:block;width:100%}
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:0.6rem;margin-top:0.8rem}
.metric{background:var(--bg3);border-radius:8px;padding:0.7rem 0.8rem;text-align:center}
.metric-val{font-size:1.3rem;font-weight:600;letter-spacing:-0.02em;line-height:1.2}
.metric-label{font-size:0.68rem;color:var(--t4);margin-top:3px;line-height:1.3}
.metric-delta{font-size:0.7rem;margin-top:2px}
.context{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:0.8rem;margin-top:0.8rem}
.context-item{background:var(--bg3);border-radius:8px;padding:0.6rem 0.8rem;font-size:0.78rem}
.context-item .label{color:var(--t4);font-size:0.68rem;margin-bottom:2px}
.context-item .value{color:var(--t1);font-weight:500}
.msoa-list{margin-top:0.8rem;max-height:260px;overflow-y:auto;border:1px solid var(--border);border-radius:8px}
.msoa-row{display:grid;grid-template-columns:120px 1fr 70px 70px 80px;gap:4px;padding:6px 10px;
  font-size:0.75rem;align-items:center;cursor:pointer;transition:background .1s;border-bottom:1px solid var(--border)}
.msoa-row:last-child{border-bottom:none}
.msoa-row:hover{background:var(--bg3)}
.msoa-row.active{background:rgba(61,158,117,0.12);border-left:3px solid var(--green)}
.msoa-row.header{font-weight:600;color:var(--t3);cursor:default;position:sticky;top:0;background:var(--bg2);
  z-index:1;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.03em}
.msoa-row.header:hover{background:var(--bg2)}
.badge{display:inline-block;padding:1px 6px;border-radius:4px;font-size:0.7rem;font-weight:500}
.badge-pos{background:rgba(61,158,117,0.15);color:var(--green)}
.badge-neg{background:rgba(216,90,48,0.15);color:var(--orange)}
.tip{position:absolute;background:var(--bg3);border:1px solid var(--border);padding:8px 12px;
  border-radius:6px;font-size:0.75rem;pointer-events:none;opacity:0;transition:opacity .12s;
  z-index:20;white-space:nowrap;color:var(--t2);max-width:300px}
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:var(--bg2)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
.note{font-size:0.7rem;color:var(--t4);margin-top:1rem;line-height:1.5;border-top:1px solid var(--border);padding-top:0.8rem}
</style>
</head>
<body>
<div class="app">
  <h1>Cascading displacement explorer</h1>
  <p class="subtitle">Interactive cascade flow profiles for London boroughs and MSOAs.
    Select a borough to see aggregate flows, then drill into individual MSOAs.
    IMD 2010 fixed baseline, 983 London MSOAs.</p>

  <div class="controls">
    <div class="control-group">
      <label>View</label>
      <div class="toggle" id="viewToggle">
        <button class="active" onclick="setView('borough')">Borough</button>
        <button onclick="setView('msoa')">MSOA</button>
      </div>
    </div>
    <div class="control-group">
      <label>Borough</label>
      <select id="boroughSelect" onchange="onBoroughChange()"></select>
    </div>
    <div class="control-group" id="msoaGroup" style="display:none">
      <label>MSOA</label>
      <select id="msoaSelect" onchange="onMsoaChange()"></select>
    </div>
    <div class="control-group">
      <label>Year</label>
      <div class="toggle" id="yearToggle">
        <button class="active" onclick="setYear('11')">2011</button>
        <button onclick="setYear('21')">2021</button>
      </div>
    </div>
  </div>

  <div class="main">
    <div class="card">
      <div class="card-title" id="sankeyTitle">Cascade flow profile</div>
      <div class="sankey-wrap">
        <div class="tip" id="tip"></div>
        <svg id="sankey" viewBox="0 0 900 320"></svg>
      </div>
      <div class="metrics" id="metricsPanel"></div>
    </div>
    <div class="card" id="contextCard">
      <div class="card-title" id="contextTitle">Borough MSOAs</div>
      <div id="contextContent"></div>
    </div>
  </div>

  <p class="note">
    <strong>How to read:</strong> Green = inflows from wealthier deciles (gentrification
    pressure). Orange = outflows to poorer deciles (displacement). Grey = other migration.
    Net Cascade = inflow from wealthier − outflow to poorer.<br>
    <strong>Data:</strong> Census O-D (2011 WICID; 2021 ODMG01EW). IMD 2010 fixed baseline.
  </p>
</div>

<script>
const DATA = DATA_PLACEHOLDER;

const BOROUGHS = [...new Set(DATA.map(r=>r.b))].sort();
let currentView='borough', currentBorough=BOROUGHS[0], currentMsoa=null, currentYear='11';

function fmt(n){return Math.round(n).toLocaleString('en-GB')}
function pct(n,d){return d>0?(n/d*100).toFixed(1)+'%':'—'}
function sign(n){return n>0?'+'+fmt(n):fmt(n)}

function init(){
  const bs=document.getElementById('boroughSelect');
  bs.innerHTML=BOROUGHS.map(b=>`<option value="${b}">${b}</option>`).join('');
  bs.value=currentBorough;
  populateMsoas();
  render();
}

function populateMsoas(){
  const ms=document.getElementById('msoaSelect');
  const msoas=DATA.filter(r=>r.b===currentBorough).sort((a,b)=>a.id.localeCompare(b.id));
  ms.innerHTML=msoas.map(m=>`<option value="${m.id}">${m.id} (D${m.d})</option>`).join('');
  currentMsoa=msoas.length>0?msoas[0].id:null;
}

function setView(v){
  currentView=v;
  document.querySelectorAll('#viewToggle button').forEach((b,i)=>b.classList.toggle('active',i===(v==='borough'?0:1)));
  document.getElementById('msoaGroup').style.display=v==='msoa'?'flex':'none';
  render();
}

function setYear(y){
  currentYear=y;
  document.querySelectorAll('#yearToggle button').forEach((b,i)=>b.classList.toggle('active',i===(y==='11'?0:1)));
  render();
}

function onBoroughChange(){
  currentBorough=document.getElementById('boroughSelect').value;
  populateMsoas();
  render();
}

function onMsoaChange(){
  currentMsoa=document.getElementById('msoaSelect').value;
  render();
}

function getAgg(records){
  const y=currentYear;
  const a={
    iw:records.reduce((s,r)=>s+r['iw'+y],0),
    op:records.reduce((s,r)=>s+r['op'+y],0),
    ti:records.reduce((s,r)=>s+r['ti'+y],0),
    to:records.reduce((s,r)=>s+r['to'+y],0),
    tm:records.reduce((s,r)=>s+r['tm'+y],0),
    ch:records.reduce((s,r)=>s+r['ch'+y],0),
    nc:records.reduce((s,r)=>s+r['nc'+y],0),
    pi:0, n:records.length,
    meanDecile:records.reduce((s,r)=>s+r.d,0)/records.length,
    meanImdC:records.reduce((s,r)=>s+r.imdc,0)/records.length,
  };
  a.pi=a.ti>0?a.iw/a.ti*100:0;
  const y2=y==='11'?'21':'11';
  a.nc_other=records.reduce((s,r)=>s+r['nc'+y2],0);
  a.iw_other=records.reduce((s,r)=>s+r['iw'+y2],0);
  a.op_other=records.reduce((s,r)=>s+r['op'+y2],0);
  return a;
}

function render(){
  let records,label,sublabel;
  if(currentView==='borough'){
    records=DATA.filter(r=>r.b===currentBorough);
    label=currentBorough;
    sublabel=`${records.length} MSOAs`;
  } else {
    records=DATA.filter(r=>r.id===currentMsoa);
    label=currentMsoa;
    sublabel=currentBorough;
  }
  if(records.length===0) return;
  const a=getAgg(records);
  const yearLabel=currentYear==='11'?'2011':'2021';
  document.getElementById('sankeyTitle').textContent=`Cascade flow profile — ${label} (${yearLabel})`;
  drawSankey(a,label,sublabel);
  drawMetrics(a,records);
  drawContext(records,a);
}

function drawSankey(a,label,sublabel){
  const svg=document.getElementById('sankey');
  const W=900,H=320;
  svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
  const nodeW=16,padY=30;
  const leftX=160,rightX=W-160,midX=W/2;
  const barTop=padY+10,barBot=H-padY-10,barH=barBot-barTop;
  const totalIn=Math.max(a.ti,1),totalOut=Math.max(a.to,1);
  const maxFlow=Math.max(totalIn,totalOut);
  const leftH=(totalIn/maxFlow)*barH,rightH=(totalOut/maxFlow)*barH;
  const leftTop=barTop+(barH-leftH)/2,rightTop=barTop+(barH-rightH)/2;
  const iwH=(a.iw/totalIn)*leftH,otherInH=leftH-iwH;
  const opH=(a.op/totalOut)*rightH,otherOutH=rightH-opH;
  let html='';

  function band(x1,y1,h1,x2,y2,h2,fill,opacity,tipText){
    const cp=(x2-x1)*0.42;
    return `<path d="M${x1} ${y1} C${x1+cp} ${y1},${x2-cp} ${y2},${x2} ${y2} L${x2} ${y2+h2} C${x2-cp} ${y2+h2},${x1+cp} ${y1+h1},${x1} ${y1+h1} Z" fill="${fill}" opacity="${opacity}"
      onmouseenter="showTip(event,\`${tipText}\`)" onmouseleave="hideTip()"/>`;
  }

  if(iwH>0.5) html+=band(leftX+nodeW,leftTop,iwH,midX-60,barTop+(barH-leftH)/2,iwH*0.9,'#3d9e75',0.4,
    `Cascade inflow: ${fmt(a.iw)} from wealthier deciles (${pct(a.iw,totalIn)} of total inflow)`);
  if(otherInH>0.5){const o=totalIn-a.iw; html+=band(leftX+nodeW,leftTop+iwH,otherInH,midX-60,barTop+(barH-leftH)/2+iwH*0.9,otherInH*0.95,'#4a4d54',0.2,
    `Other inflows: ${fmt(o)} (lateral/same-decile moves)`);}
  if(opH>0.5) html+=band(midX+60,barTop+(barH-rightH)/2,opH*0.9,rightX,rightTop,opH,'#d85a30',0.4,
    `Cascade outflow: ${fmt(a.op)} to poorer deciles (${pct(a.op,a.to)} of total outflow)`);
  if(otherOutH>0.5){const o=a.to-a.op; html+=band(midX+60,barTop+(barH-rightH)/2+opH*0.9,otherOutH*0.95,rightX,rightTop+opH,otherOutH,'#4a4d54',0.2,
    `Other outflows: ${fmt(o)} (lateral/same-decile moves)`);}

  if(iwH>0.5) html+=`<rect x="${leftX}" y="${leftTop}" width="${nodeW}" height="${iwH}" rx="3" fill="#3d9e75" opacity="0.8"/>`;
  if(otherInH>0.5) html+=`<rect x="${leftX}" y="${leftTop+iwH}" width="${nodeW}" height="${otherInH}" rx="3" fill="#4a4d54" opacity="0.5"/>`;
  if(opH>0.5) html+=`<rect x="${rightX}" y="${rightTop}" width="${nodeW}" height="${opH}" rx="3" fill="#d85a30" opacity="0.8"/>`;
  if(otherOutH>0.5) html+=`<rect x="${rightX}" y="${rightTop+opH}" width="${nodeW}" height="${otherOutH}" rx="3" fill="#4a4d54" opacity="0.5"/>`;

  const cw=120,ch=70,cx=midX-cw/2,cy=H/2-ch/2;
  const ncCol=a.nc>=0?'#3d9e75':'#d85a30';
  html+=`<rect x="${cx}" y="${cy}" width="${cw}" height="${ch}" rx="10" fill="${ncCol}" opacity="0.12" stroke="${ncCol}" stroke-width="1" stroke-opacity="0.3"/>`;
  html+=`<text x="${midX}" y="${cy+22}" text-anchor="middle" fill="#f0ede5" font-size="13" font-weight="600">${label.length>16?label.slice(0,14)+'…':label}</text>`;
  html+=`<text x="${midX}" y="${cy+38}" text-anchor="middle" fill="#8a8780" font-size="10">${sublabel}</text>`;
  html+=`<text x="${midX}" y="${cy+56}" text-anchor="middle" fill="${ncCol}" font-size="12" font-weight="600">Net: ${sign(a.nc)}</text>`;

  html+=`<text x="${leftX-8}" y="${leftTop+leftH/2-8}" text-anchor="end" fill="#c0bdb5" font-size="12" font-weight="500">Total inflow</text>`;
  html+=`<text x="${leftX-8}" y="${leftTop+leftH/2+8}" text-anchor="end" fill="#8a8780" font-size="11">${fmt(a.ti)}</text>`;
  html+=`<text x="${rightX+nodeW+8}" y="${rightTop+rightH/2-8}" fill="#c0bdb5" font-size="12" font-weight="500">Total outflow</text>`;
  html+=`<text x="${rightX+nodeW+8}" y="${rightTop+rightH/2+8}" fill="#8a8780" font-size="11">${fmt(a.to)}</text>`;

  if(iwH>15) html+=`<text x="${leftX+nodeW+12}" y="${leftTop+iwH/2+1}" fill="#3d9e75" font-size="10" dominant-baseline="central">${fmt(a.iw)}</text>`;
  if(opH>15) html+=`<text x="${rightX-12}" y="${rightTop+opH/2+1}" text-anchor="end" fill="#d85a30" font-size="10" dominant-baseline="central">${fmt(a.op)}</text>`;

  html+=`<circle cx="30" cy="14" r="5" fill="#3d9e75" opacity="0.6"/><text x="40" y="18" fill="#8a8780" font-size="9.5">Inflow from wealthier</text>`;
  html+=`<circle cx="180" cy="14" r="5" fill="#d85a30" opacity="0.6"/><text x="190" y="18" fill="#8a8780" font-size="9.5">Outflow to poorer</text>`;
  html+=`<circle cx="320" cy="14" r="5" fill="#4a4d54" opacity="0.5"/><text x="330" y="18" fill="#8a8780" font-size="9.5">Other flows</text>`;

  svg.innerHTML=html;
}

function drawMetrics(a,records){
  const y=currentYear;
  const ncCol=a.nc>=0?'var(--green)':'var(--orange)';
  const delta_nc=a.nc-a.nc_other;
  const deltaCol=delta_nc>0?'var(--green)':delta_nc<0?'var(--orange)':'var(--t3)';
  const otherYearLabel=y==='11'?'2021':'2011';
  document.getElementById('metricsPanel').innerHTML=`
    <div class="metric"><div class="metric-val" style="color:${ncCol}">${sign(a.nc)}</div><div class="metric-label">Net Cascade</div><div class="metric-delta" style="color:${deltaCol}">Δ ${sign(delta_nc)} vs ${otherYearLabel}</div></div>
    <div class="metric"><div class="metric-val" style="color:var(--green)">${fmt(a.iw)}</div><div class="metric-label">Cascade inflow</div><div class="metric-delta" style="color:var(--t4)">${pct(a.iw,a.ti)} of total</div></div>
    <div class="metric"><div class="metric-val" style="color:var(--orange)">${fmt(a.op)}</div><div class="metric-label">Cascade outflow</div><div class="metric-delta" style="color:var(--t4)">${pct(a.op,a.to)} of total</div></div>
    <div class="metric"><div class="metric-val" style="color:var(--t1)">${fmt(a.ch)}</div><div class="metric-label">CFI Churn</div><div class="metric-delta" style="color:var(--t4)">iw + op</div></div>
    <div class="metric"><div class="metric-val" style="color:var(--t1)">${fmt(a.tm)}</div><div class="metric-label">Total migration</div><div class="metric-delta" style="color:var(--t4)">${fmt(a.ti)} in / ${fmt(a.to)} out</div></div>
    <div class="metric"><div class="metric-val" style="color:var(--blue)">${(a.meanImdC*100).toFixed(1)}%</div><div class="metric-label">Mean IMD pctile Δ</div><div class="metric-delta" style="color:var(--t4)">2010→2019</div></div>`;
}

function drawContext(records,a){
  const title=document.getElementById('contextTitle');
  const content=document.getElementById('contextContent');
  const y=currentYear;

  if(currentView==='borough'){
    title.textContent=`MSOAs in ${currentBorough} (${records.length})`;
    const sorted=[...records].sort((a,b)=>b['nc'+y]-a['nc'+y]);
    let html=`<div class="msoa-list"><div class="msoa-row header"><span>MSOA code</span><span>Borough</span><span>Decile</span><span>Net Casc.</span><span>Cascade in</span></div>`;
    for(const r of sorted){
      const nc=r['nc'+y];
      const ncB=nc>=0?`<span class="badge badge-pos">+${fmt(nc)}</span>`:`<span class="badge badge-neg">${fmt(nc)}</span>`;
      html+=`<div class="msoa-row${r.id===currentMsoa?' active':''}" onclick="selectMsoa('${r.id}')">
        <span style="color:var(--t1);font-weight:500;font-size:0.73rem">${r.id}</span>
        <span style="color:var(--t3)">${r.b}</span><span>D${r.d}</span><span>${ncB}</span>
        <span style="color:var(--green)">${fmt(r['iw'+y])}</span></div>`;
    }
    content.innerHTML=html+'</div>';
  } else {
    const msoa=records[0];
    if(!msoa) return;
    title.textContent=`${msoa.id} — context`;
    const boroughRecords=DATA.filter(r=>r.b===currentBorough);
    const ba=getAgg(boroughRecords);
    const ncRank=[...boroughRecords].sort((a,b)=>b['nc'+y]-a['nc'+y]).findIndex(r=>r.id===msoa.id)+1;
    content.innerHTML=`
      <div class="context">
        <div class="context-item"><div class="label">Borough</div><div class="value">${currentBorough}</div></div>
        <div class="context-item"><div class="label">Wealth decile (IMD 2010)</div><div class="value">D${msoa.d} ${msoa.d<=3?'(deprived)':msoa.d>=8?'(affluent)':'(mid-range)'}</div></div>
        <div class="context-item"><div class="label">IMD score</div><div class="value">${msoa.imd10.toFixed(1)} (2010) → ${msoa.imd19.toFixed(1)} (2019)</div></div>
        <div class="context-item"><div class="label">IMD percentile change</div><div class="value" style="color:${msoa.imdc>0?'var(--green)':'var(--orange)'}">${(msoa.imdc*100).toFixed(2)}%</div></div>
        <div class="context-item"><div class="label">Rank in borough (Net Cascade)</div><div class="value">#${ncRank} of ${boroughRecords.length}</div></div>
        <div class="context-item"><div class="label">Borough avg Net Cascade</div><div class="value" style="color:${ba.nc>=0?'var(--green)':'var(--orange)'}">${sign(Math.round(ba.nc/ba.n))}/MSOA</div></div>
      </div>
      <div style="margin-top:0.8rem"><div class="card-title">Other MSOAs in ${currentBorough}</div></div>`;
    const sorted=[...boroughRecords].sort((a,b)=>b['nc'+y]-a['nc'+y]);
    let list=`<div class="msoa-list" style="max-height:180px"><div class="msoa-row header"><span>MSOA</span><span>Borough</span><span>Decile</span><span>Net Casc.</span><span>Cascade in</span></div>`;
    for(const r of sorted){
      const nc=r['nc'+y];
      const ncB=nc>=0?`<span class="badge badge-pos">+${fmt(nc)}</span>`:`<span class="badge badge-neg">${fmt(nc)}</span>`;
      list+=`<div class="msoa-row${r.id===currentMsoa?' active':''}" onclick="selectMsoa('${r.id}')">
        <span style="color:var(--t1);font-weight:500;font-size:0.73rem">${r.id}</span>
        <span style="color:var(--t3)">${r.b}</span><span>D${r.d}</span><span>${ncB}</span>
        <span style="color:var(--green)">${fmt(r['iw'+y])}</span></div>`;
    }
    content.innerHTML+=list+'</div>';
  }
}

function selectMsoa(id){
  const rec=DATA.find(r=>r.id===id);
  if(!rec) return;
  currentView='msoa'; currentBorough=rec.b; currentMsoa=id;
  document.querySelectorAll('#viewToggle button').forEach((b,i)=>b.classList.toggle('active',i===1));
  document.getElementById('msoaGroup').style.display='flex';
  document.getElementById('boroughSelect').value=currentBorough;
  populateMsoas();
  document.getElementById('msoaSelect').value=id;
  render();
}

function showTip(e,text){
  const tip=document.getElementById('tip');
  tip.textContent=text; tip.style.opacity='1';
  const rect=document.querySelector('.sankey-wrap').getBoundingClientRect();
  tip.style.left=(e.clientX-rect.left+12)+'px';
  tip.style.top=(e.clientY-rect.top-30)+'px';
}
function hideTip(){document.getElementById('tip').style.opacity='0'}

init();
</script>
</body>
</html>'''

# ── 3. Inject data & write ───────────────────────────────────────────
html_out = HTML_TEMPLATE.replace('DATA_PLACEHOLDER', data_json)

out_path = OUTPUT_DIR / 'cascade_explorer.html'
out_path.write_text(html_out, encoding='utf-8')

print(f'Saved → {out_path}')
print(f'File size: {out_path.stat().st_size / 1024:.0f} KB')
