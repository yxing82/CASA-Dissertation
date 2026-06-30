# Weekly Progress Summary

*A Flow-Based Definition of Gentrification: Socio-Economic Displacement in London using Census OD Data (2011–2021)*

**Week ending 28 June 2026 · Focus: national-frame extension and comparative validation**

---

This week consolidated the analytical framework on the re-harmonised data and tested the flow-based typology against two independent gentrification benchmarks. 

The central result is methodological: 
- **the cascade signal is *decoupled* from attribute-defined gentrification**;
- **2021 cascade pattern is dominated by a pandemic-era exodus rather than gentrification relocating outward**.

## 1. Methodological framework

Migration flows were scored against neighbourhood deprivation under a **three-frame design** that isolates two distinct mechanisms, so their effects can be reported separately rather than confounded:

- **Frame A — London-internal flows on a London-relative decile ladder.** 
    - Captures intra-urban restructuring, retained as the primary lens.
- **Frame B — London-internal flows on the national decile ladder.** 
    - Isolates the reclassification effect of switching reference frame, holding flows fixed.
- **Frame C — London flows plus London-touch external flows on the national ladder.** 
    - Adds the external-flow effect via a synthetic external node fixed at national D6.

Each cross-boundary move is classified as cascade (inflow from wealthier and outflow to poorer) or counter-cascade. 

MSOAs are typed by the balance and intensity of deprivation-crossing flows (Cascade-led, Counter-led, Symmetric, Lateral).

Validation uses IMD percentile change (2010-to-2019) as an independent socio-economic outcome. 

*Two boundary MSOAs (Camden 024/025, merged in 2021)* are analysed as a single best-fit zone, affecting 2 of 982 units and leaving all other deciles unchanged.

## 2. Key quantitative results

| Finding | Verified metric | Value |
|---|---|---|
| London is relatively deprived nationally | Share of London MSOAs below national D6 | 69.1% (679/982) |
| Pandemic-era exodus, not symmetric exchange | Δ external inflow / outflow, 2011→2021 | −17.8% / +51.3% |
| External flows flip the directional balance | Net-exporter MSOAs (national+external frame) | 53 → 116 (+119%) |
| Counter-cascade intensifies | Net-receiver MSOAs (national+external frame) | 25 → 10 (−60%) |
| Affluent-flow signal shifts inner to outer | Cascade-led MSOAs in outer London, 2021 | 166 / 195 (85%) |
<!-- | Structural divergence (hubs) grows after reprocess | Sign-divergent MSOAs, 2021 (London frame) | 101 / 982 | -->

## 3. Comparative validation (EDA 5–6)

The typology was cross-tabulated against Yee & Dennett's (2022) attribute classification (EDA 5) and against an occupational-ascent measure replicating Duncan's method (EDA 6, change in SOC major groups 1–3, used in place of the non-comparable 2011/2021 NS-SeC). 

Both comparisons point the same way:

| Benchmark | Association with cascade typology | Reading |
|---|---|---|
| Yee (2022) attribute typology | Cramér's V = 0.10–0.11; ARI ≈ 0.005–0.02 | No better than chance |
| Occupational ascent (SOC 1–3) | Spearman ρ = +0.02 (national+external frame) | Independent |
| Yee GEN × IMD percentile change | +0.043 without cascade vs +0.017 with cascade | **Cascade does not reinforce gentrification** |

Where the methods do agree, the convergence is specific to 2011 and inner London (i.e. classic inner-London gentrification.)

Notably, the flow method's own IMD signal lives in the counter direction, not the cascade direction.

## 4. Interpretation and next steps

Read together, the results support keeping Frame A (London-only) as the main lens, answering "How is London reshaping itself?" and transitioning with "London is not a vacuum" to Frame C (national + external) as complementary context that exposes boundary effects. 

A working diagnostic emerged from the extreme-tail analysis:

- **Genuine gentrification cascade** — high inflow share, small dominance gap across frames, persistent across years (e.g. inner cores in Camden, Tower Hamlets).
- **Exodus** — low inflow share, large cross-frame gap, episodic (outer high-decile boroughs in 2021: Kingston, Harrow, Richmond, Barnet, Sutton).

Priority for next week: where to investigate?
- e.g. when attribute methods flag an area but the flow typology reads Lateral/Counter are a genuine research contribution worth characterising spatially.
