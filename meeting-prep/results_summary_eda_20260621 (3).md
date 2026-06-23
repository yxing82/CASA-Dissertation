# Results & Findings Summary — EDA Phases A–F

**Dissertation:** A Flow-Based Definition of Gentrification: Analyzing Socio-Economic Displacement in London using Census Origin-Destination Data (2011–2021)

**Date:** 21 June 2026  
**Coverage:** `data_preprocess` → `eda_1` → `eda_2` → `eda_3`  
**Universe:** 983 London MSOAs, 2011 and 2021 Census OD data, IMD 2010/2019

---

## 0. Data Preprocessing & Robustness

The analytical pipeline is highly robust to preprocessing choices. Four sensitivity tests confirmed that MSOA-level deprivation aggregations are practically identical whether using 2011 population weights, 2015 weights, or no weights at all (Tests 1–3), and that wealth deciles generated from different IMD baselines (2010 vs 2019) are strongly correlated (Test 4). These results rule out the possibility that downstream findings are artefacts of arbitrary weighting or baseline choices.

The endpoint classification audit ensures that every origin–destination code is labelled with exactly one mutually exclusive category, and the actual data filter uses a positive whitelist so that no unanticipated code can enter the analysis set.

---

## 1. Phase A — Metric Distributions (EDA 1)

**Finding 1.1: Cascade and counter-cascade metrics have structurally similar distributions.**
Both families — cascade (Net_Cascade, CFI_Churn, CFI_Rate, Pct_Inflow_Wealthier) and counter-cascade (Net_Counter, Counter_Churn, Counter_Rate, Pct_Outflow_Wealthier) — display comparable shapes and spread across the 983 MSOAs.

**Finding 1.2: Both families experienced a lower-volume shift from 2011 to 2021.**
Distributions shifted leftward (toward lower absolute volumes) between censuses. This volume decline affects both cascade-direction and counter-cascade-direction flows, consistent with overall lower inter-MSOA migration captured in the 2021 Census (partly attributable to the COVID-era migration snapshot).

---

## 2. Phase B — Correlation Structure & Metric Selection (EDA 1)

**Finding 2.1: Cascade and counter-cascade metrics mirror each other.**
Net_Cascade vs Net_Counter: ρ ≈ 0.94. The two families are largely mirror images of each other, both driven by where an MSOA sits in the deprivation hierarchy relative to its migration partners. This structural mirroring arises because the four base flows form two tightly correlated pairs: the wealthier-connected pair (Inflow_Wealthier ↔ Outflow_Wealthier, ρ ≈ 0.96) and the poorer-connected pair (Outflow_Poorer ↔ Inflow_Poorer, ρ ≈ 0.93), with near-zero cross-pair correlation. Each MSOA acts as a transit node in the hierarchy, making the cascade and counter-cascade dimensions two sides of a single hierarchical position effect.

**Finding 2.2: Only two derived metrics survive the redundancy filter.**
Five candidate balance metrics were tested. Three were dropped: Total_Pressure (ρ = 0.98 with CFI_Churn), Net_Balance (ρ = 0.47 with Wealth_Decile, partly recoding hierarchy position), and Churn_Balance (ρ = 0.92 with Cascade_Dominance, a redundant unnormalised version). The two survivors are:

- **Cascade_Dominance** = CFI_Churn / (CFI_Churn + Counter_Churn), bounded [0, 1] with 0.50 as the natural midline. Captures which direction of deprivation-crossing flow dominates. Max |ρ| = 0.42 against any existing metric.
- **Cross_Decile_Share** = (CFI_Churn + Counter_Churn) / Total_Migration. Captures what proportion of all migration crosses a deprivation decile boundary. Max |ρ| = 0.22 against any existing metric.

These two metrics are genuinely independent of each other (ρ = 0.08) and capture distinct dimensions of the flow regime, supporting their joint use for the typology.

**Finding 2.3: ~10% of MSOAs have divergent sign concordance.**
Approximately 90% of MSOAs have concordant signs on Net_Cascade and Net_Counter (both point the same way). The ~10% divergent cases — where the two net metrics point in opposite directions — are flagged as an analytically interesting subpopulation for Phase D investigation.

---

## 3. Phase C — Hierarchy Effects (EDA 2)

**Finding 3.1: Cascade dominance is not the majority flow type at any point in the hierarchy.**
Every decile-mean of Cascade_Dominance sits below 0.5 in both 2011 and 2021. Counter-cascade flows slightly outweigh cascade flows on average throughout the hierarchy. The "wealthier-in, poorer-out" cascade pattern is nowhere the dominant flow direction, even in the most deprived deciles.

**Finding 3.2: The universal drop in Cascade_Dominance from 2011 to 2021 was statistically significant.**
Mean dominance dropped from 0.480 to 0.464 (paired t = −10.6, p < 0.01). Counter-cascade flows gained relative ground across the board. The percentage of MSOAs above the 0.50 midline fell from 32.5% (2011) to 18.7% (2021). The largest drops occurred at the hierarchy extremes.

**Finding 3.3: A structural hierarchy gradient shapes cascade dynamics.**
More deprived areas (D1) have more room "above" them in the hierarchy, so cascade-direction flows are relatively more available. D10 areas can only receive from below, mechanically suppressing their dominance numerator. The mild decline in Cascade_Dominance from poor to wealthy deciles reflects this structural geometry.

**Finding 3.4: Cross_Decile_Share shows a U-shaped pattern by deprivation.**
Both the most deprived and most affluent MSOAs have the lowest cross-decile shares, while mid-tier neighbourhoods (D4–D8) cluster around 0.84–0.87. This arises from boundary effects: areas at the extremes of the hierarchy have fewer available decile boundaries to cross. The 2011-to-2021 decline in cross-decile migration was driven primarily by mid-hierarchy areas becoming more "insular" in their migration patterns, not a uniform retreat. Affluent extremes (D8–D10) maintained or increased their cross-decile exchange rates, consistent with the "segregation of affluence" thesis (Reardon & Bischoff, 2011, 2014).

**Finding 3.5: The asymmetric volume decline complicates the displacement narrative.**
CFI_Churn declined more sharply (12–22%) than Counter_Churn (1–11%), and the Counter_Churn minus CFI_Churn gap roughly doubled between 2011 and 2021. The standard gentrification-based displacement narrative may have become relatively less dominant compared to the reverse (upward-mobility) process.

**Finding 3.6: Cascade dominance and churn intensity are positively coupled, but weakening.**
MSOAs where cascade flows dominate directionally also tend to run at higher absolute intensity (r = 0.53 in 2011, r = 0.41 in 2021). This suggests a self-reinforcing mechanism — where cascade dominates, it also runs harder — but the weakening correlation indicates the coupling became more diffuse, possibly because overall volumes fell unevenly due to COVID.

**Finding 3.7: The heaviest cascade activity concentrates in the deprived-to-middle belt (D2–D6).**
Both Cascade_Dominance and CFI_Churn decline with wealth (ρ = −0.72 for dominance, ρ = −0.65 for churn in 2011). The high-churn tail (top 10%) is dominated by D2–D6 MSOAs, not the extremes. This is consistent with rent-gap theory, where cascading displacement operates most intensely where there is both a deprivation "gap" to exploit and enough wealthier neighbours to generate inflow.

---

## 4. Phase D — Where the Mirror Breaks (EDA 2)

**Finding 4.1: Divergent MSOAs cluster near the dominance midline and avoid the hierarchy extremes.**
Divergent MSOAs — where Net_Cascade and Net_Counter have opposite signs — concentrate in the 0.45–0.55 Dominance band (72% in 2011, 55% in 2021) and span D2–D9, with none at D1 or D10. Their churn is close to the London average, not exceptionally high or low. Divergence is most likely when both flow volumes are roughly equal (near the midline). The absence from boundary deciles reflects edge effects, where local-level processes override the hierarchical gradient (e.g. regeneration schemes attracting wealthier residents while simultaneously exporting poorer ones upward).

**Finding 4.2: Divergence persistence is well above chance.**
42 of 97 divergent MSOAs in 2021 were also divergent in 2011 (~49% persistence rate). If divergence were random, only ~8–9 of the 97 would persist by coincidence. For roughly half of divergent MSOAs, divergence is a stable structural feature rather than census-period noise.

**Finding 4.3: Divergent subtypes became more spatially polarised by 2021.**
In 2011, cascade-positive (net receivers) and counter-positive (net exporters) divergent MSOAs were spatially intermixed. By 2021, the two subtypes had separated: counter-positive MSOAs consolidated in the inner-east and central belt (predominantly D2–D5), while cascade-positive MSOAs consolidated along the outer ring (D5–D9). This increasing spatial polarisation suggests the cascade mechanism itself became more spatially stratified over the decade.

**Finding 4.4: Sign concordance captures a structural property that volume-based metrics miss.**
Dominance measures volume share; concordance measures directional consistency. Since the volume balance of divergent MSOAs is similar to concordant areas, divergent MSOAs are not distinguishable on the dominance map alone. The two maps capture genuinely independent dimensions of cascade behaviour.

---

## 5. Phase E — Typology Construction (EDA 3)

**Typology Design:**
The typology is constructed on two axes — Cascade_Dominance (x-axis) and Cross_Decile_Share (y-axis) — using the following thresholds:

- **Cascade-led:** Dominance > 0.52, CDS ≥ 25th percentile
- **Counter-led:** Dominance < 0.48, CDS ≥ 25th percentile
- **Symmetric:** 0.48 ≤ Dominance ≤ 0.52, CDS ≥ 25th percentile
- **Lateral:** CDS < 25th percentile (regardless of dominance)

**Finding 5.1: Massive shift toward counter-cascade dominance between 2011 and 2021.**
Cascade-led MSOAs nearly halved (130 → 72). Counter-led MSOAs grew substantially (340 → 423). Symmetric MSOAs declined modestly (267 → 242). Lateral MSOAs grew slightly (246 → 246). The entire typology cloud drifts leftward over the decade.

**Finding 5.2: Cross-Decile Share distribution became more dispersed by 2021.**
In 2011, virtually every MSOA sat above 0.5 on CDS. By 2021, points dropped well below 0.4, even approaching 0. A larger share of MSOAs had their migration become predominantly within the same deprivation band by 2021, partly attributable to COVID-era migration patterns suppressing longer-distance cross-tier moves. Emergence of low-CDS areas across the deprivation spectrum (scattered D1–D7 and D10) compared to 2011 where all low-CDS MSOAs were in D10 only.

**Finding 5.3: Typology categories have distinct spatial logics.**
Cascade-led MSOAs cluster due to gentrification pressure operating in identifiable zones (inner south and west in 2011). Counter-led MSOAs cluster in outer boroughs where wealthier residents leave and poorer ones arrive. Symmetric MSOAs are spatially scattered, representing a residual condition wherever opposing pressures cancel out. Lateral MSOAs are predominantly at the hierarchy extremes (D1, D10) where low CDS reflects mechanical ceiling/floor effects.

**Finding 5.4: The typology captures structurally persistent features.**
58% of MSOAs (583/983) had no typology change across the decade, indicating the classification captures something durable about how neighbourhoods sit within the migration system, not just census-period noise.

**Finding 5.5: Cascade pressure fragmented specifically in the most actively restructuring areas.**
Cascade-led MSOAs that changed category between 2011 and 2021 split roughly evenly between becoming counter-led and symmetric. These transitions concentrated in inner West and inner South London — the classic gentrification belt. Cascade pressure did not weaken uniformly; it fragmented in areas that were the most actively restructuring in 2011, suggesting some gentrification-via-displacement processes had by 2021 already "completed" or exhausted themselves.

**Finding 5.6: Limitation — the "Other change" category.**
209 MSOAs with miscellaneous transitions (e.g. symmetric → counter-led, counter-led → symmetric) dominate the outer North and East London. These outer areas have unstable flow regimes that shift between balanced and counter-cascade states without following the cascade-centric narrative. The typology is most analytically powerful for inner-London areas where cascade dynamics are strongest; outer ring areas experience lower-volume and more volatile cross-decile flows.

**Finding 5.7: The Typology × Concordance Quadrant framework reveals that typology and hierarchical position capture independent dimensions (EDA 3, §15d).**
Crossing the four-category typology (cascade-led, counter-led, symmetric, lateral) with a four-quadrant classification from the Net_Cascade × Net_Counter sign matrix (upward-connected hub, downward-connected hub, net receiver, net exporter) produces a richer characterisation of neighbourhood flow regimes. Key results:

- The typology is a volume-balance classification; the quadrant is a directional-position classification determined largely by where the MSOA sits in the deprivation hierarchy. The two are analytically independent — the same typology label appears across multiple quadrants.
- **Cascade-led** splits almost evenly in 2021: 32 are upward-connected hubs (median D3, deprived areas where cascade volume dominates but net connections face wealthier areas) and 35 are downward-connected hubs (median D8, affluent areas where cascade volume dominates but net connections face poorer areas). This is the most transitional typology (N = 130 → 72, only 19% stability).
- **Counter-led** is the dominant and growing typology (N = 340 → 423). In 2021 it splits into 226 downward-connected hubs and 144 upward-connected hubs, plus 39 net receivers and 14 net exporters.
- **Symmetric** is the most evenly divided typology (109 upward-connected vs 117 downward-connected hubs in 2021), because neither flow direction dominates in volume, leaving quadrant placement determined entirely by hierarchical position.
- **Lateral** is the most stable typology (84% retention across the decade).
- The distinction between counter-led concordant and counter-positive divergent is critical: a counter-led concordant MSOA is a suburban absorption zone receiving migrants from all directions with slightly more via the counter-cascade channel; a counter-positive divergent MSOA is haemorrhaging residents in both hierarchical directions — arguably the strongest displacement signal in the dataset. These concentrate in inner-London boroughs (Newham, Hackney, Tower Hamlets).

---

## 6. Metric Design Decision: Ratio vs Difference (EDA 3, §14b)

**Decision: Stick with ratio-based Cascade_Dominance.**

Rationale:

- The ratio and difference can never disagree on direction (mathematically guaranteed — no directional flips).
- There is 7.9% disagreement on bandwidth, with every disagreement being a Symmetric ↔ Counter-led swap. 34 MSOAs shifted from Symmetric (ratio) to Counter-led (difference); 8 shifted the other way. The asymmetric swap occurs because most MSOAs lean counter-cascade, pushing more Symmetric cases into Counter-led.
- **The ratio-based typology separates direction from intensity**, treating a 60/40 split the same whether total churn is 100 or 2,000. The difference-based typology is scale-dependent: high-churn MSOAs get systematically reclassified (confirmed by Mann-Whitney U test showing disagreeing MSOAs have statistically significantly higher total churn).
- **The ratio version discriminates IMD trajectories more sharply.** Kruskal-Wallis tests are significant for both formulations, but the ratio-based boxplot shows clearer separation between groups — particularly, Counter-led median sits more distinctly below Symmetric and Cascade-led. The difference-based version dilutes the Counter-led group with misclassified high-churn Symmetric MSOAs.
- **Difference-based dominance reinforces the finding** of prevalent counter-cascade dominance in London. Both formulations agree that cascade flows are not a city-wide phenomenon.

---

## 7. Structural Explanation: Why Counter-Cascade Dominates (EDA 3, §15c)

**Finding 7.1: The "escalator effect" (Fielding, 1992) explains the structural upward-mobility bias.**
People who move within London tend, on average, to move toward less deprived areas. This is a well-documented feature of the city's internal migration system driven by aspirational mobility (households trading up), lifecycle progression (young renters in deprived inner areas buying in less deprived suburbs), and social housing allocation patterns.

**Finding 7.2: There is a noticeable and growing excess of upward movers.**
In 2011, there was a 6% excess of upward (counter-cascade direction) movers over downward (cascade direction) movers. By 2021, this grew to 13%. The counter/cascade ratio rose from 1.06 to 1.13 between censuses. At every single decile, the share of outflows going to wealthier destinations exceeds the share of inflows from wealthier origins.

**Finding 7.3: Gentrification-related displacement is a localised perturbation against the prevailing current.**
The background rate of upward mobility exceeds the rate of downward displacement on average across the city. The cascade signal is real, but it concentrates in a specific subset of MSOAs while the majority of London runs on the reverse (upward-mobility) dynamic. Rather than "cascading displacement is the dominant force reshaping London", the findings align with Marcuse's (1985) framework of displacement as a localised, relational process embedded within a broader urban system.

**Finding 7.4: The widening counter-dominance gap has two plausible explanations.**
First, the 2021 census captured COVID-era migration where "flight to the suburbs" amplified upward moves while cascade-direction moves were suppressed (pandemic reduced short-distance gentrification-related relocations). Second, a decade of inner-London gentrification had by 2021 already "completed" in many areas — active cascade zones in 2011 had become settled, post-transition neighbourhoods.

**Finding 7.5: Counter-positive divergence is the strongest signal of displacement.**
Counter-positive divergent MSOAs (Net_Cascade < 0 and Net_Counter > 0 simultaneously) are net exporters in both directions of the hierarchy — more leave to poorer areas than arrive from wealthier ones, and simultaneously more leave to wealthier areas than arrive from poorer ones. These represent areas experiencing population loss across the board, a signature consistent with active displacement pressure.

---

## 8. Spatial Logic: Net Exporters and Net Absorbers (EDA 2 + 3)

The combined findings from EDA 2 and EDA 3 reveal the spatial logic of a cascading system with net exporters and net absorbers. Inner-city restructuring generates outward displacement, and the suburbs absorb it. The city-wide average tilts counter-cascade-led because the displacement has to go somewhere, and "somewhere" is the numerical majority of London MSOAs. This produces a system where a subset of neighbourhoods experiences cascade-direction pressure while the rest of the city absorbs the displaced population through counter-cascade flows.

---

## 9. Phase F — IMD Validation (EDA 3, §17)

### 9a. Bivariate and Partial Correlations (Fig 16)

**Finding 9.1: Raw correlations between individual cascade metrics and IMD_Pctile_Change are weak, and this holds in both 2011 and 2021.**
Net directional metrics show effectively zero raw association in both periods (Net_Cascade: ρ = −0.039 in 2011, −0.049 in 2021; Net_Counter: +0.010 and −0.000). The churn metrics are the strongest raw predictors in both years: CFI_Churn (ρ = +0.270 in 2011, +0.259 in 2021) and Counter_Churn (+0.287, +0.253). Cascade_Dominance is non-significant in 2011 (ρ = +0.047, p = 0.14) and only weakly significant in 2021 (+0.089, p = 0.006). Cross_Decile_Share is modestly negative in both (ρ ≈ −0.18).

**Finding 9.2: Partial correlations controlling for Wealth_Decile reveal a hidden hierarchy confound — consistent across both census periods.**
Once baseline deprivation is held constant, the net directional metrics flip to moderately negative in both years: Net_Cascade (partial ρ = −0.229 in 2011, −0.238 in 2021) and Net_Counter (−0.179, −0.215), all highly significant. Within any given decile, MSOAs with stronger net inflows from either hierarchical direction tend to experience relative deprivation decline. The churn metrics retain positive partials in both periods (CFI_Churn: +0.233 and +0.232; Counter_Churn: +0.257 and +0.229). Cascade_Dominance remains negligible after controlling (partial ρ = +0.024 non-significant in 2011, +0.065 barely significant in 2021).

**Finding 9.3: The relationship structure is remarkably stable across census periods.**
The near-identical correlation profiles in 2011 and 2021 demonstrate that the metrics' relationship with neighbourhood change is a durable structural feature of London's migration system, not an artefact of either census snapshot. The churn-IMD association in 2011 (ρ ≈ 0.27–0.29) slightly exceeds 2021 (ρ ≈ 0.25–0.26), likely reflecting COVID-era volume suppression compressing the 2021 range, but the ordering and significance levels are unchanged.

**Finding 9.4: Volume matters more than direction.**
The strongest predictors of IMD change are the total churn metrics, not the directional balance — and this is true whether measured at the start or end of the deprivation change period. A neighbourhood that is heavily "churning" across decile boundaries, regardless of whether cascade or counter-cascade flows dominate, tends to move up in the deprivation rankings. This aligns with the view that migration-driven restructuring itself is the engine of neighbourhood change, with direction being secondary to intensity.

### 9b. Typological Validation (Fig 17)

**Finding 9.5: The typology significantly predicts IMD_Pctile_Change in both census periods.**
2011 classification: Kruskal-Wallis H = 36.1, p = 6.97e-08. 2021 classification: H = 31.9, p = 5.55e-07. Both are highly significant, confirming the typology captures real differences in neighbourhood change regardless of which census period defines the grouping.

**Finding 9.6: The ordering of typology groups is consistent across periods and complicates the cascade-as-gentrification narrative.**
In both 2011 and 2021 panels, the same pattern holds: counter-led MSOAs show the most negative IMD trajectories, cascade-led sits near zero, symmetric is slightly positive, and lateral is the most positive. The 2011 panel confirms this with a larger cascade-led sample (N = 130 vs 72), ruling out small-sample artefact as an explanation for the near-zero cascade-led median. This is the opposite of what a naive "cascade = gentrification = neighbourhood ascent" model would predict.

**Finding 9.7: The consistent ordering across periods tells us this is structural, not cyclical.**
If the validation pattern differed between 2011 and 2021 — say, cascade-led showing positive IMD change when classified at the start of the period but near-zero when classified at the end — that would suggest the relationship changes depending on where in a gentrification cycle the snapshot falls. Instead, the identical ordering in both panels indicates the relationship between flow regime type and deprivation trajectory is a stable structural property of London's migration system. Counter-led areas systematically decline regardless of when you measure the flow structure.

**Finding 9.8: The pattern is interpretable within the framework.**
Counter-led MSOAs are areas where the dominant flow direction is residents leaving for wealthier destinations. This outflow of upwardly-mobile residents mechanically drains the neighbourhood of its higher-income population, pulling its relative deprivation position downward. Conversely, lateral MSOAs — where most migration stays within the same deprivation band — are insulated from hierarchical reshuffling and show the most stable or positive trajectories. Cascade-led MSOAs sit near zero because they experience competing forces: wealthier inflows pushing toward ascent, but poorer outflows pulling the other way.

**Finding 9.9: This validates the framework but reframes the theoretical contribution.**
The typology works — it discriminates deprivation trajectories significantly in both periods. But the validation tells a story about outflow-driven decline rather than inflow-driven ascent. The strongest neighbourhood change signal is not "wealthy people arrive and the area improves," but rather "upwardly-mobile residents leave and the area declines." This is consistent with the selective out-migration literature and further supports the view that cascading displacement is embedded within a broader system of residential sorting, rather than being the primary driver of neighbourhood change.

---

## 10. Open Questions & Flagged Limitations

**10.1 Escalator effect and upward mobility:** Given London's escalator dynamics, how could displaced people move up to wealthier deciles? The excess of upward movers at every decile suggests a structural mechanism beyond simple displacement. Lifecycle progression, aspirational mobility, and housing market filtering are candidate explanations, but the precise mechanism may be outside this study's scope.

**10.2 Typology threshold sensitivity:** The classification depends on the dominance bandwidth (±0.02 from 0.50) and the CDS percentile cutoff (25th). These should be tested for robustness in further analysis.

**10.3 COVID confound:** The 2021 Census captured a specific and unusual migration moment. It is difficult to disentangle secular trends (completion of gentrification cycles) from pandemic-specific effects (suppressed short-distance moves, flight to suburbs).

**10.4 Outer-London volatility:** The typology is most analytically powerful for inner-London areas. Outer ring MSOAs display lower-volume, more volatile flow regimes that shift between categories without following the cascade-centric narrative.

**10.5 Validation reframes the theoretical contribution.** The typology discriminates deprivation trajectories significantly, but the pattern is driven by outflow-based decline (counter-led) rather than inflow-based ascent (cascade-led). The methodology chapter's framing of "ascent-dominated restructuring" may need reworking to reflect this finding.

---

## 11. Key Figures Reference

| Figure | Content | Key Finding |
|--------|---------|-------------|
| Fig 01 | Distribution cascades (2011 vs 2021) | Structurally similar distributions; lower-volume shift |
| Fig 02 | Full Spearman correlation matrix | Mirror structure; churn cluster; hierarchy effect |
| Fig 03 | Four base flows pairplot | Two correlated pairs explain the mirror |
| Fig 04 | Derived metrics distributions | Cascade_Dominance median below 0.50; CDS ~0.85 |
| Fig 05 | Wealth decile map | Baseline spatial deprivation geography |
| Fig 06 | Decile profiles — all metrics | Structural hierarchy gradient |
| Fig 07 | Derived metrics by decile | Dominance below 0.5 everywhere; CDS inverted-U |
| Fig 08 | Temporal delta by decile | Asymmetric volume decline; cascade dropped more |
| Fig 09a/b | Sign concordance maps (2011 & 2021) | Spatial polarisation of divergent subtypes |
| Fig 10 | Dominance scatter refined | Cascade mechanism concentrated in D2–D6 |
| Fig 11 | Dominance map (2011 vs 2021) | London-wide shift toward blue (counter-cascade) |
| Fig 11a/b | Dominance × concordance overlay | Two independent dimensions; divergent not distinguishable by volume |
| Fig 12 | Typology scatter exploration | Dense cloud; leftward shift; uncorrelated axes (ρ = 0.08) |
| Fig 13 | Typology scatter classified | Cascade-led halves (130 → 72); counter-led grows (340 → 423) |
| Fig 13b | Ratio vs difference scatter | Fan shape; scale dependence of difference metric |
| Fig 13c | IMD validation: ratio vs difference | Ratio discriminates IMD trajectories more sharply |
| Fig 14 | Typology map (2011 vs 2021) | Cascade-led inner; counter-led spreads to outer |
| Fig 14b | Typology transition map | 58% stable; cascade fragmentation in gentrification belt |
| Fig 14c | Cascade–counter volume breakdown | Structural upward-mobility bias at every decile |
| Fig 14d | Typology × Quadrant map (2×2, 2011 vs 2021) | Typology and hierarchical position are independent dimensions; cascade-led splits by hierarchy |
| Fig 15 | Typology decile composition | Cascade-led concentrates in D3–D7 (rent-gap zone) |
| Fig 16 | Validation scatterplots (6 metrics vs IMD change) | Churn metrics strongest (ρ ≈ 0.25); directional metrics near zero raw, negative partial |
| Fig 17 | IMD change by typology boxplot | KW H=31.9, p<0.001; counter-led most negative, lateral most positive |
