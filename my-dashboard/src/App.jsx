import { useState, useMemo, useRef, useEffect } from "react";

// ── DATA ──────────────────────────────────────────────────────────
const DECILE_DATA = [
  {d:1,n:99,iw11:59204,op11:0,ti11:83975,tm11:172066,nc11:59204,iw21:54253,op21:0,ti21:81986,tm21:170550,nc21:54253},
  {d:2,n:98,iw11:51896,op11:17647,ti11:86487,tm11:176695,nc11:34249,iw21:45147,op21:16251,ti21:82049,tm21:171599,nc21:28896},
  {d:3,n:98,iw11:46380,op11:26572,ti11:88230,tm11:177637,nc11:19808,iw21:40120,op21:22718,ti21:82189,tm21:169987,nc21:17402},
  {d:4,n:98,iw11:40505,op11:31641,ti11:84518,tm11:169160,nc11:8864,iw21:33405,op21:27422,ti21:78621,tm21:159421,nc21:5983},
  {d:5,n:98,iw11:35660,op11:34877,ti11:82129,tm11:166782,nc11:783,iw21:32558,op21:28939,ti21:82832,tm21:166376,nc21:3619},
  {d:6,n:99,iw11:28957,op11:41919,ti11:82120,tm11:163845,nc11:-12962,iw21:25623,op21:37105,ti21:84525,tm21:167808,nc21:-11482},
  {d:7,n:98,iw11:21336,op11:41363,ti11:73760,tm11:148244,nc11:-20027,iw21:18754,op21:36029,ti21:75626,tm21:148873,nc21:-17275},
  {d:8,n:98,iw11:16519,op11:40563,ti11:70908,tm11:138200,nc11:-24044,iw21:14337,op21:37177,ti21:73251,tm21:142856,nc21:-22840},
  {d:9,n:98,iw11:8977,op11:42183,ti11:64512,tm11:126430,nc11:-33206,iw21:8200,op21:37669,ti21:69252,tm21:132130,nc21:-29469},
  {d:10,n:99,iw11:0,op11:32669,ti11:51784,tm11:97787,nc11:-32669,iw21:0,op21:29087,ti21:56171,tm21:103404,nc21:-29087},
];

const BOROUGH_DATA = [
  {b:"Barking and Dagenham",n:22,ad:3.1,iw11:6753,op11:4749,nc11:2004,ti11:15323,tm11:28989,iw21:5766,op21:3805,nc21:1961,ti21:13920,tm21:27213,ic:-1.7},
  {b:"Barnet",n:41,ad:7.7,iw11:9605,op11:15273,nc11:-5668,ti11:31290,tm11:60920,iw21:7156,op21:13570,nc21:-6414,ti21:29047,tm21:57680,ic:-0.5},
  {b:"Bexley",n:28,ad:7.8,iw11:3542,op11:5768,nc11:-2226,ti11:13198,tm11:24314,iw21:3347,op21:5629,nc21:-2282,ti21:14580,tm21:26605,ic:-0.5},
  {b:"Brent",n:34,ad:4.4,iw11:13903,op11:10293,nc11:3610,ti11:28585,tm11:59839,iw21:12086,op21:9075,nc21:3011,ti21:29173,tm21:62334,ic:-5.0},
  {b:"Bromley",n:39,ad:8.1,iw11:6477,op11:9025,nc11:-2548,ti11:21995,tm11:40864,iw21:5942,op21:8270,nc21:-2328,ti21:23019,tm21:42416,ic:-0.9},
  {b:"Camden",n:28,ad:5.6,iw11:10749,op11:15147,nc11:-4398,ti11:25494,tm11:55344,iw21:8548,op21:11471,nc21:-2923,ti21:24086,tm21:49948,ic:-4.9},
  {b:"City of London",n:1,ad:9.0,iw11:33,op11:785,nc11:-752,ti11:692,tm11:1549,iw21:28,op21:789,nc21:-761,ti21:1296,tm21:2339,ic:3.2},
  {b:"Croydon",n:44,ad:6.2,iw11:11939,op11:10754,nc11:1185,ti11:29065,tm11:54368,iw21:9120,op21:8874,nc21:246,ti21:26181,tm21:50783,ic:-0.6},
  {b:"Ealing",n:39,ad:5.8,iw11:12391,op11:13509,nc11:-1118,ti11:29860,tm11:61497,iw21:10374,op21:11137,nc21:-763,ti21:27378,tm21:56295,ic:-2.2},
  {b:"Enfield",n:36,ad:5.5,iw11:9887,op11:10619,nc11:-732,ti11:26415,tm11:49943,iw21:6988,op21:8743,nc21:-1755,ti21:21879,tm21:43715,ic:-0.7},
  {b:"Greenwich",n:33,ad:3.8,iw11:11625,op11:7938,nc11:3687,ti11:23485,tm11:46327,iw21:8117,op21:5103,nc21:3014,ti21:19225,tm21:37980,ic:-8.0},
  {b:"Hackney",n:28,ad:1.8,iw11:13553,op11:6279,nc11:7274,ti11:27643,tm11:55503,iw21:12110,op21:5165,nc21:6945,ti21:24491,tm21:50466,ic:-10.0},
  {b:"Hammersmith and Fulham",n:25,ad:4.9,iw11:12025,op11:8645,nc11:3380,ti11:23225,tm11:47785,iw21:11091,op21:8277,nc21:2814,ti21:25093,tm21:50777,ic:-4.9},
  {b:"Haringey",n:36,ad:3.4,iw11:13050,op11:9514,nc11:3536,ti11:29636,tm11:59943,iw21:11358,op21:8253,nc21:3105,ti21:27316,tm21:57290,ic:-8.3},
  {b:"Harrow",n:30,ad:8.0,iw11:4867,op11:9056,nc11:-4189,ti11:17633,tm11:34918,iw21:4848,op21:8771,nc21:-3923,ti21:19348,tm21:37704,ic:-0.6},
  {b:"Havering",n:30,ad:7.7,iw11:3668,op11:5143,nc11:-1475,ti11:13133,tm11:23690,iw21:3931,op21:5319,nc21:-1388,ti21:17074,tm21:29710,ic:-0.3},
  {b:"Hillingdon",n:32,ad:6.9,iw11:8522,op11:8836,nc11:-314,ti11:21656,tm11:39969,iw21:7505,op21:7457,nc21:48,ti21:23087,tm21:42300,ic:-1.9},
  {b:"Hounslow",n:28,ad:6.2,iw11:8791,op11:9650,nc11:-859,ti11:22372,tm11:44087,iw21:6903,op21:8117,nc21:-1214,ti21:21960,tm21:43746,ic:-0.7},
  {b:"Islington",n:23,ad:2.8,iw11:13340,op11:9016,nc11:4324,ti11:24433,tm11:52173,iw21:13805,op21:8864,nc21:4941,ti21:28688,tm21:58393,ic:-8.3},
  {b:"Kensington and Chelsea",n:21,ad:6.0,iw11:6395,op11:8989,nc11:-2594,ti11:16877,tm11:35330,iw21:5424,op21:6962,nc21:-1538,ti21:16824,tm21:33210,ic:-1.3},
  {b:"Kingston upon Thames",n:20,ad:9.1,iw11:4399,op11:6324,nc11:-1925,ti11:14681,tm11:27748,iw21:3482,op21:5089,nc21:-1607,ti21:14088,tm21:26252,ic:-0.2},
  {b:"Lambeth",n:35,ad:4.0,iw11:17914,op11:12729,nc11:5185,ti11:36757,tm11:75562,iw21:18540,op21:13256,nc21:5284,ti21:39688,tm21:82772,ic:-5.2},
  {b:"Lewisham",n:36,ad:3.9,iw11:12225,op11:9984,nc11:2241,ti11:27466,tm11:54682,iw21:10266,op21:8235,nc21:2031,ti21:24557,tm21:49792,ic:-4.3},
  {b:"Merton",n:25,ad:8.1,iw11:4075,op11:9509,nc11:-5434,ti11:17441,tm11:34611,iw21:3603,op21:8876,nc21:-5273,ti21:18797,tm21:36945,ic:-0.1},
  {b:"Newham",n:37,ad:1.7,iw11:14345,op11:7334,nc11:7011,ti11:30621,tm11:64722,iw21:10640,op21:5630,nc21:5010,ti21:24420,tm21:54401,ic:-12.6},
  {b:"Redbridge",n:31,ad:6.6,iw11:4703,op11:10105,nc11:-5402,ti11:20785,tm11:39646,iw21:3790,op21:9189,nc21:-5399,ti21:18572,tm21:36806,ic:-3.1},
  {b:"Richmond upon Thames",n:23,ad:9.5,iw11:2210,op11:7269,nc11:-5059,ti11:16127,tm11:30255,iw21:1793,op21:6268,nc21:-4475,ti21:16695,tm21:31371,ic:-0.8},
  {b:"Southwark",n:33,ad:4.1,iw11:14776,op11:14431,nc11:345,ti11:33170,tm11:67941,iw21:12840,op21:13370,nc21:-530,ti21:32664,tm21:67970,ic:-3.9},
  {b:"Sutton",n:24,ad:8.1,iw11:4177,op11:5133,nc11:-956,ti11:12359,tm11:23024,iw21:4085,op21:4697,nc21:-612,ti21:14089,tm21:25633,ic:-1.5},
  {b:"Tower Hamlets",n:32,ad:2.2,iw11:14838,op11:8231,nc11:6607,ti11:30051,tm11:63356,iw21:17025,op21:8007,nc21:9018,ti21:37678,tm21:76269,ic:-11.6},
  {b:"Waltham Forest",n:28,ad:3.0,iw11:9876,op11:7887,nc11:1989,ti11:23657,tm11:47535,iw21:9381,op21:6747,nc21:2634,ti21:23556,tm21:46460,ic:-10.0},
  {b:"Wandsworth",n:37,ad:6.2,iw11:15379,op11:18028,nc11:-2649,ti11:39324,tm11:78478,iw21:14122,op21:18244,nc21:-4122,ti21:42442,tm21:84851,ic:-5.3},
  {b:"Westminster",n:24,ad:5.9,iw11:9402,op11:13482,nc11:-4080,ti11:23974,tm11:51934,iw21:8383,op21:11138,nc21:-2755,ti21:25591,tm21:52578,ic:-4.0},
];

const fmt = (n) => {
  if (Math.abs(n) >= 1000) return (n/1000).toFixed(1) + "k";
  return n.toLocaleString();
};
const fmtSigned = (n) => (n > 0 ? "+" : "") + fmt(n);

// Deprivation tier labels
const DECILE_LABELS = {
  1: "Most Deprived", 2: "", 3: "", 4: "",
  5: "Mid", 6: "", 7: "", 8: "",
  9: "", 10: "Least Deprived"
};

// Color palette
const C = {
  inflow: "#4ecdc4",    // teal for inflow from wealthier
  outflow: "#ff6b6b",   // coral for outflow to poorer
  inflow11: "#4ecdc4",
  outflow11: "#ff6b6b",
  inflow21: "#1a9e93",
  outflow21: "#c0392b",
  pos: "#4ecdc4",
  neg: "#ff6b6b",
  neutral: "#8a8a8a",
  bg: "#0d1117",
  card: "#161b22",
  border: "#21262d",
  t1: "#e6edf3",
  t2: "#b1bac4",
  t3: "#7d8590",
};

const DECILE_COLORS = [
  "#d73027","#f46d43","#fdae61","#fee08b","#ffffbf",
  "#d9ef8b","#a6d96a","#66bd63","#1a9850","#006837"
];

// ── FLOW DIAGRAM COMPONENT ──────────────────────────────────────
function FlowDiagram({ data, maxVal, width, height, year, label }) {
  const pad = { top: 30, bottom: 10, left: 0, right: 0 };
  const nodeW = 28;
  const gap = 8;
  const usableH = height - pad.top - pad.bottom;
  const nodeH = (usableH - gap * 9) / 10;
  const centerX = width / 2;

  return (
    <svg width={width} height={height} style={{ display: "block" }}>
      <text x={centerX} y={16} textAnchor="middle" fill={C.t2}
        style={{ fontSize: 13, fontWeight: 600, letterSpacing: "0.05em" }}>{label}</text>
      {data.map((r, i) => {
        const y = pad.top + i * (nodeH + gap);
        const iw = r[`iw${year}`];
        const op = r[`op${year}`];
        const nc = r[`nc${year}`];
        const maxFlow = maxVal;
        const barMaxW = (width - nodeW) / 2 - 12;

        const iwW = maxFlow > 0 ? (iw / maxFlow) * barMaxW : 0;
        const opW = maxFlow > 0 ? (op / maxFlow) * barMaxW : 0;

        const iwColor = year === "11" ? C.inflow11 : C.inflow21;
        const opColor = year === "11" ? C.outflow11 : C.outflow21;

        return (
          <g key={i}>
            {/* Decile node */}
            <rect x={centerX - nodeW/2} y={y} width={nodeW} height={nodeH}
              rx={4} fill={DECILE_COLORS[i]} opacity={0.85} />
            <text x={centerX} y={y + nodeH/2 + 1} textAnchor="middle"
              dominantBaseline="middle" fill="#fff"
              style={{ fontSize: 11, fontWeight: 700 }}>D{r.d}</text>

            {/* Inflow bar (left of node) */}
            <rect x={centerX - nodeW/2 - 4 - iwW} y={y + 2}
              width={iwW} height={nodeH - 4} rx={3}
              fill={iwColor} opacity={0.7} />
            {iwW > 30 && (
              <text x={centerX - nodeW/2 - 8 - iwW} y={y + nodeH/2 + 1}
                textAnchor="end" dominantBaseline="middle"
                fill={iwColor} style={{ fontSize: 9, fontWeight: 500 }}>
                {fmt(iw)}
              </text>
            )}

            {/* Outflow bar (right of node) */}
            <rect x={centerX + nodeW/2 + 4} y={y + 2}
              width={opW} height={nodeH - 4} rx={3}
              fill={opColor} opacity={0.7} />
            {opW > 30 && (
              <text x={centerX + nodeW/2 + 8 + opW} y={y + nodeH/2 + 1}
                textAnchor="start" dominantBaseline="middle"
                fill={opColor} style={{ fontSize: 9, fontWeight: 500 }}>
                {fmt(op)}
              </text>
            )}
          </g>
        );
      })}
      {/* Axis labels */}
      <text x={12} y={pad.top - 6} fill={C.t3}
        style={{ fontSize: 9, textTransform: "uppercase", letterSpacing: "0.08em" }}>
        ← Inflow from wealthier
      </text>
      <text x={width - 12} y={pad.top - 6} textAnchor="end" fill={C.t3}
        style={{ fontSize: 9, textTransform: "uppercase", letterSpacing: "0.08em" }}>
        Outflow to poorer →
      </text>
    </svg>
  );
}

// ── DELTA COLUMN ────────────────────────────────────────────────
function DeltaColumn({ data, height }) {
  const pad = { top: 30, bottom: 10 };
  const gap = 8;
  const usableH = height - pad.top - pad.bottom;
  const nodeH = (usableH - gap * 9) / 10;
  const w = 100;

  return (
    <svg width={w} height={height} style={{ display: "block" }}>
      <text x={w/2} y={16} textAnchor="middle" fill={C.t2}
        style={{ fontSize: 11, fontWeight: 600, letterSpacing: "0.04em" }}>Δ Net Cascade</text>
      {data.map((r, i) => {
        const y = pad.top + i * (nodeH + gap);
        const delta = r.nc21 - r.nc11;
        const color = delta > 0 ? C.pos : delta < 0 ? C.neg : C.neutral;
        const arrow = delta > 0 ? "▲" : delta < 0 ? "▼" : "–";
        return (
          <g key={i}>
            <text x={w/2} y={y + nodeH/2 - 2} textAnchor="middle"
              dominantBaseline="middle" fill={color}
              style={{ fontSize: 11, fontWeight: 700 }}>
              {fmtSigned(delta)}
            </text>
            <text x={w/2} y={y + nodeH/2 + 12} textAnchor="middle"
              dominantBaseline="middle" fill={color} opacity={0.6}
              style={{ fontSize: 9 }}>
              {arrow}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

// ── BOROUGH BAR CHART ───────────────────────────────────────────
function BoroughChart({ data, sort }) {
  const sorted = [...data].sort((a, b) => {
    if (sort === "nc11") return b.nc11 - a.nc11;
    if (sort === "nc21") return b.nc21 - a.nc21;
    return (b.nc21 - b.nc11) - (a.nc21 - a.nc11);
  });

  const maxAbs = Math.max(...sorted.map(r => Math.max(Math.abs(r.nc11), Math.abs(r.nc21))));

  return (
    <div style={{ overflowX: "auto" }}>
      {sorted.map((r, i) => {
        const barMax = 180;
        const w11 = Math.abs(r.nc11) / maxAbs * barMax;
        const w21 = Math.abs(r.nc21) / maxAbs * barMax;
        const delta = r.nc21 - r.nc11;
        return (
          <div key={i} style={{
            display: "grid",
            gridTemplateColumns: "160px 1fr 70px",
            alignItems: "center",
            padding: "3px 0",
            borderBottom: `1px solid ${C.border}`,
            gap: 8,
          }}>
            <div style={{ fontSize: 11, color: C.t2, overflow: "hidden",
              textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {r.b}
              <span style={{ color: C.t3, fontSize: 9, marginLeft: 4 }}>D{r.ad.toFixed(0)}</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 4, height: 20 }}>
              {/* 2011 bar */}
              <div style={{
                width: w11,
                height: 8,
                borderRadius: 4,
                background: r.nc11 >= 0 ? C.inflow11 : C.outflow11,
                opacity: 0.5,
                marginLeft: r.nc11 < 0 ? "auto" : 0,
              }} />
              {/* 2021 bar overlaid */}
              <div style={{
                width: w21,
                height: 8,
                borderRadius: 4,
                background: r.nc21 >= 0 ? C.inflow21 : C.outflow21,
                opacity: 0.9,
                position: "relative",
                left: r.nc21 >= 0 ? -w11 - 4 : 0,
                marginLeft: r.nc21 < 0 ? "auto" : 0,
              }} />
            </div>
            <div style={{
              fontSize: 10,
              fontWeight: 600,
              textAlign: "right",
              color: delta > 0 ? C.pos : delta < 0 ? C.neg : C.t3,
            }}>
              {fmtSigned(delta)}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ── MAIN APP ────────────────────────────────────────────────────
export default function App() {
  const [view, setView] = useState("combined"); // combined | borough
  const [boroSort, setBoroSort] = useState("nc21");
  const [hovered, setHovered] = useState(null);

  const maxFlow = useMemo(() => {
    let m = 0;
    DECILE_DATA.forEach(r => {
      m = Math.max(m, r.iw11, r.op11, r.iw21, r.op21);
    });
    return m;
  }, []);

  const totals = useMemo(() => {
    const s = (key) => DECILE_DATA.reduce((a, r) => a + r[key], 0);
    return {
      iw11: s("iw11"), op11: s("op11"), tm11: s("tm11"),
      iw21: s("iw21"), op21: s("op21"), tm21: s("tm21"),
    };
  }, []);

  const flowH = 440;
  const flowW = 290;

  return (
    <div style={{
      fontFamily: "'JetBrains Mono', 'SF Mono', 'Fira Code', monospace",
      background: C.bg,
      color: C.t1,
      minHeight: "100vh",
      padding: "24px 20px",
    }}>
      {/* Header */}
      <div style={{ maxWidth: 900, margin: "0 auto" }}>
        <h1 style={{
          fontSize: 20, fontWeight: 700, letterSpacing: "-0.02em",
          margin: 0, lineHeight: 1.3,
          fontFamily: "'IBM Plex Sans', 'Helvetica Neue', sans-serif",
        }}>
          Cascading Displacement Flows
        </h1>
        <p style={{
          fontSize: 12, color: C.t3, marginTop: 4, lineHeight: 1.6,
          maxWidth: 640,
        }}>
          Combined 2011 &amp; 2021 census migration across London's deprivation gradient.
          983 MSOAs · IMD 2010 fixed baseline · Wealth deciles D1 (most deprived) → D10 (least deprived).
        </p>

        {/* Summary metrics */}
        <div style={{
          display: "flex", gap: 16, flexWrap: "wrap", marginTop: 16, marginBottom: 20,
        }}>
          {[
            { label: "Cascade inflow 2011", val: fmt(totals.iw11), color: C.inflow11 },
            { label: "Cascade inflow 2021", val: fmt(totals.iw21), color: C.inflow21 },
            { label: "Cascade outflow 2011", val: fmt(totals.op11), color: C.outflow11 },
            { label: "Cascade outflow 2021", val: fmt(totals.op21), color: C.outflow21 },
          ].map((m, i) => (
            <div key={i} style={{
              background: C.card, border: `1px solid ${C.border}`,
              borderRadius: 8, padding: "10px 14px", flex: "1 1 140px",
              minWidth: 130,
            }}>
              <div style={{ fontSize: 18, fontWeight: 700, color: m.color, letterSpacing: "-0.02em" }}>
                {m.val}
              </div>
              <div style={{ fontSize: 9, color: C.t3, marginTop: 2, textTransform: "uppercase",
                letterSpacing: "0.06em" }}>{m.label}</div>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div style={{ display: "flex", gap: 4, marginBottom: 16 }}>
          {[
            { id: "combined", label: "Decile Flow Comparison" },
            { id: "borough", label: "Borough Breakdown" },
          ].map(t => (
            <button key={t.id} onClick={() => setView(t.id)} style={{
              padding: "6px 14px", borderRadius: 6, border: `1px solid ${C.border}`,
              background: view === t.id ? "#1a3a2e" : C.card,
              color: view === t.id ? C.pos : C.t2,
              cursor: "pointer", fontSize: 11, fontWeight: 500,
              fontFamily: "inherit",
              borderColor: view === t.id ? "#2d7a5a" : C.border,
            }}>{t.label}</button>
          ))}
        </div>

        {/* ── COMBINED FLOW VIEW ──────────────────── */}
        {view === "combined" && (
          <div>
            {/* Legend */}
            <div style={{
              display: "flex", gap: 20, flexWrap: "wrap", marginBottom: 12,
              fontSize: 10, color: C.t3,
            }}>
              <span><span style={{
                display: "inline-block", width: 12, height: 8, borderRadius: 3,
                background: C.inflow11, opacity: 0.7, marginRight: 4, verticalAlign: "middle",
              }} />2011 inflow from wealthier</span>
              <span><span style={{
                display: "inline-block", width: 12, height: 8, borderRadius: 3,
                background: C.inflow21, opacity: 0.9, marginRight: 4, verticalAlign: "middle",
              }} />2021 inflow from wealthier</span>
              <span><span style={{
                display: "inline-block", width: 12, height: 8, borderRadius: 3,
                background: C.outflow11, opacity: 0.7, marginRight: 4, verticalAlign: "middle",
              }} />2011 outflow to poorer</span>
              <span><span style={{
                display: "inline-block", width: 12, height: 8, borderRadius: 3,
                background: C.outflow21, opacity: 0.9, marginRight: 4, verticalAlign: "middle",
              }} />2021 outflow to poorer</span>
            </div>

            {/* Three-column layout: 2011 | delta | 2021 */}
            <div style={{
              display: "flex", justifyContent: "center", alignItems: "flex-start",
              gap: 0, overflowX: "auto",
              background: C.card, border: `1px solid ${C.border}`,
              borderRadius: 12, padding: "12px 8px",
            }}>
              <FlowDiagram data={DECILE_DATA} maxVal={maxFlow}
                width={flowW} height={flowH} year="11" label="2011 Census" />
              <DeltaColumn data={DECILE_DATA} height={flowH} />
              <FlowDiagram data={DECILE_DATA} maxVal={maxFlow}
                width={flowW} height={flowH} year="21" label="2021 Census" />
            </div>

            {/* Interpretation panel */}
            <div style={{
              marginTop: 16, padding: "14px 16px",
              background: C.card, border: `1px solid ${C.border}`, borderRadius: 10,
            }}>
              <div style={{ fontSize: 11, fontWeight: 600, color: C.t2, marginBottom: 8 }}>
                Reading the diagram
              </div>
              <div style={{ fontSize: 10, color: C.t3, lineHeight: 1.7 }}>
                Each row is a wealth decile (D1 = most deprived 10% of MSOAs, D10 = least deprived).
                <strong style={{ color: C.inflow11 }}> Left bars</strong> show inflow from wealthier areas (cascade pressure).
                <strong style={{ color: C.outflow11 }}> Right bars</strong> show outflow to poorer areas (displacement).
                The centre column shows the <strong style={{ color: C.t2 }}>change in net cascade</strong> between
                census periods — positive (teal ▲) means intensifying gentrification pressure,
                negative (red ▼) means easing.
              </div>
            </div>

            {/* Decile detail table */}
            <div style={{
              marginTop: 16, overflowX: "auto",
              background: C.card, border: `1px solid ${C.border}`, borderRadius: 10,
              padding: "12px 0",
            }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 10 }}>
                <thead>
                  <tr style={{ color: C.t3, textTransform: "uppercase", letterSpacing: "0.06em", fontSize: 9 }}>
                    <th style={{ padding: "4px 10px", textAlign: "left" }}>Decile</th>
                    <th style={{ padding: "4px 8px", textAlign: "right" }}>MSOAs</th>
                    <th style={{ padding: "4px 8px", textAlign: "right", color: C.inflow11 }}>Inflow W. '11</th>
                    <th style={{ padding: "4px 8px", textAlign: "right", color: C.inflow21 }}>Inflow W. '21</th>
                    <th style={{ padding: "4px 8px", textAlign: "right", color: C.outflow11 }}>Outflow P. '11</th>
                    <th style={{ padding: "4px 8px", textAlign: "right", color: C.outflow21 }}>Outflow P. '21</th>
                    <th style={{ padding: "4px 8px", textAlign: "right" }}>Net '11</th>
                    <th style={{ padding: "4px 8px", textAlign: "right" }}>Net '21</th>
                    <th style={{ padding: "4px 8px", textAlign: "right" }}>Δ</th>
                  </tr>
                </thead>
                <tbody>
                  {DECILE_DATA.map((r, i) => {
                    const delta = r.nc21 - r.nc11;
                    return (
                      <tr key={i} style={{
                        borderTop: `1px solid ${C.border}`,
                        background: hovered === i ? "rgba(78,205,196,0.05)" : "transparent",
                      }}
                        onMouseEnter={() => setHovered(i)}
                        onMouseLeave={() => setHovered(null)}>
                        <td style={{ padding: "6px 10px", fontWeight: 600 }}>
                          <span style={{
                            display: "inline-block", width: 10, height: 10,
                            borderRadius: 2, background: DECILE_COLORS[i],
                            marginRight: 6, verticalAlign: "middle",
                          }} />
                          D{r.d}
                          {DECILE_LABELS[r.d] && (
                            <span style={{ color: C.t3, fontWeight: 400, marginLeft: 4, fontSize: 9 }}>
                              {DECILE_LABELS[r.d]}
                            </span>
                          )}
                        </td>
                        <td style={{ padding: "6px 8px", textAlign: "right", color: C.t3 }}>{r.n}</td>
                        <td style={{ padding: "6px 8px", textAlign: "right", color: C.inflow11 }}>{fmt(r.iw11)}</td>
                        <td style={{ padding: "6px 8px", textAlign: "right", color: C.inflow21 }}>{fmt(r.iw21)}</td>
                        <td style={{ padding: "6px 8px", textAlign: "right", color: C.outflow11 }}>{fmt(r.op11)}</td>
                        <td style={{ padding: "6px 8px", textAlign: "right", color: C.outflow21 }}>{fmt(r.op21)}</td>
                        <td style={{ padding: "6px 8px", textAlign: "right",
                          color: r.nc11 >= 0 ? C.pos : C.neg, fontWeight: 600 }}>{fmt(r.nc11)}</td>
                        <td style={{ padding: "6px 8px", textAlign: "right",
                          color: r.nc21 >= 0 ? C.pos : C.neg, fontWeight: 600 }}>{fmt(r.nc21)}</td>
                        <td style={{ padding: "6px 8px", textAlign: "right",
                          color: delta > 0 ? C.pos : delta < 0 ? C.neg : C.t3, fontWeight: 700 }}>
                          {fmtSigned(delta)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ── BOROUGH VIEW ─────────────────────────── */}
        {view === "borough" && (
          <div>
            <div style={{
              display: "flex", gap: 4, marginBottom: 12, alignItems: "center",
            }}>
              <span style={{ fontSize: 10, color: C.t3, marginRight: 4 }}>Sort by:</span>
              {[
                { id: "nc21", label: "Net Cascade 2021" },
                { id: "nc11", label: "Net Cascade 2011" },
                { id: "delta", label: "Change Δ" },
              ].map(s => (
                <button key={s.id} onClick={() => setBoroSort(s.id)} style={{
                  padding: "4px 10px", borderRadius: 5,
                  border: `1px solid ${boroSort === s.id ? "#2d7a5a" : C.border}`,
                  background: boroSort === s.id ? "#1a3a2e" : "transparent",
                  color: boroSort === s.id ? C.pos : C.t3,
                  cursor: "pointer", fontSize: 10, fontFamily: "inherit",
                }}>{s.label}</button>
              ))}
            </div>

            {/* Borough comparison */}
            <div style={{
              background: C.card, border: `1px solid ${C.border}`,
              borderRadius: 10, padding: "12px 14px",
            }}>
              <div style={{
                display: "grid",
                gridTemplateColumns: "160px 1fr 70px",
                padding: "4px 0 8px", borderBottom: `1px solid ${C.border}`,
                fontSize: 9, color: C.t3, textTransform: "uppercase",
                letterSpacing: "0.06em",
              }}>
                <div>Borough</div>
                <div style={{ textAlign: "center" }}>Net Cascade (lighter = 2011, darker = 2021)</div>
                <div style={{ textAlign: "right" }}>Δ</div>
              </div>
              <BoroughChart data={BOROUGH_DATA} sort={boroSort} />
            </div>

            {/* Top gentrifiers & receivers */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 14 }}>
              {/* Top gentrification pressure */}
              <div style={{
                background: C.card, border: `1px solid ${C.border}`,
                borderRadius: 10, padding: "12px 14px",
              }}>
                <div style={{ fontSize: 11, fontWeight: 600, color: C.pos, marginBottom: 8 }}>
                  ▲ Top cascade pressure (2021)
                </div>
                {[...BOROUGH_DATA].sort((a,b) => b.nc21 - a.nc21).slice(0, 8).map((r, i) => (
                  <div key={i} style={{
                    display: "flex", justifyContent: "space-between",
                    padding: "3px 0", borderBottom: `1px solid ${C.border}`,
                    fontSize: 10,
                  }}>
                    <span style={{ color: C.t2 }}>{r.b}</span>
                    <span style={{ color: C.pos, fontWeight: 600 }}>+{fmt(r.nc21)}</span>
                  </div>
                ))}
              </div>
              {/* Top displacement sinks */}
              <div style={{
                background: C.card, border: `1px solid ${C.border}`,
                borderRadius: 10, padding: "12px 14px",
              }}>
                <div style={{ fontSize: 11, fontWeight: 600, color: C.neg, marginBottom: 8 }}>
                  ▼ Top displacement sinks (2021)
                </div>
                {[...BOROUGH_DATA].sort((a,b) => a.nc21 - b.nc21).slice(0, 8).map((r, i) => (
                  <div key={i} style={{
                    display: "flex", justifyContent: "space-between",
                    padding: "3px 0", borderBottom: `1px solid ${C.border}`,
                    fontSize: 10,
                  }}>
                    <span style={{ color: C.t2 }}>{r.b}</span>
                    <span style={{ color: C.neg, fontWeight: 600 }}>{fmt(r.nc21)}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Notable shifts */}
            <div style={{
              marginTop: 14, background: C.card, border: `1px solid ${C.border}`,
              borderRadius: 10, padding: "12px 14px",
            }}>
              <div style={{ fontSize: 11, fontWeight: 600, color: C.t2, marginBottom: 8 }}>
                Biggest shifts 2011 → 2021
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div>
                  <div style={{ fontSize: 9, color: C.pos, marginBottom: 6, textTransform: "uppercase",
                    letterSpacing: "0.06em" }}>Intensifying pressure ▲</div>
                  {[...BOROUGH_DATA].sort((a,b) => (b.nc21-b.nc11)-(a.nc21-a.nc11)).slice(0,5).map((r,i) => {
                    const d = r.nc21 - r.nc11;
                    return d > 0 ? (
                      <div key={i} style={{
                        display: "flex", justifyContent: "space-between",
                        padding: "3px 0", fontSize: 10, borderBottom: `1px solid ${C.border}`,
                      }}>
                        <span style={{ color: C.t2 }}>{r.b}</span>
                        <span style={{ color: C.pos, fontWeight: 600 }}>+{fmt(d)}</span>
                      </div>
                    ) : null;
                  })}
                </div>
                <div>
                  <div style={{ fontSize: 9, color: C.neg, marginBottom: 6, textTransform: "uppercase",
                    letterSpacing: "0.06em" }}>Increasing displacement ▼</div>
                  {[...BOROUGH_DATA].sort((a,b) => (a.nc21-a.nc11)-(b.nc21-b.nc11)).slice(0,5).map((r,i) => {
                    const d = r.nc21 - r.nc11;
                    return d < 0 ? (
                      <div key={i} style={{
                        display: "flex", justifyContent: "space-between",
                        padding: "3px 0", fontSize: 10, borderBottom: `1px solid ${C.border}`,
                      }}>
                        <span style={{ color: C.t2 }}>{r.b}</span>
                        <span style={{ color: C.neg, fontWeight: 600 }}>{fmt(d)}</span>
                      </div>
                    ) : null;
                  })}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div style={{
          marginTop: 20, paddingTop: 12, borderTop: `1px solid ${C.border}`,
          fontSize: 9, color: C.t3, lineHeight: 1.6,
        }}>
          Data: ONS Census Origin-Destination 2011 &amp; 2021 · IMD 2010 fixed baseline ·
          Wealth deciles derived from mean LSOA-to-MSOA IMD scores ·
          Net Cascade = Σ(Inflow from wealthier) − Σ(Outflow to poorer)
        </div>
      </div>
    </div>
  );
}
