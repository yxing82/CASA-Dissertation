# Supervisor Meeting Brief — 22 June 2026

**Project:** A Flow-Based Definition of Gentrification (Census OD Data, London 2011–2021)  
**Status:** Data preprocessing ✓ | EDA 1–3 complete | Phase F validation

---

## Core findings in brief

**1. Cascade displacement is real but it is not the dominant dynamic in London.**
At no point in the deprivation hierarchy does the cascade ("wealthier-in, poorer-out") direction carry the majority of cross-decile flows. Counter-cascade flows outweigh cascade flows in both 2011 and 2021, and the gap widened over the decade (mean Cascade_Dominance dropped from 0.480 to 0.464, p < 0.01). Cascade-led MSOAs nearly halved from 130 to 72.

**2. London has a structural upward-mobility bias that gentrification works against, not with.**
At every single wealth decile, outflows to wealthier destinations exceed inflows from wealthier origins. The excess of upward movers grew from 6% (2011) to 13% (2021). This aligns with Fielding's (1992) "escalator effect." Gentrification-related displacement operates as a localised counter-current against this prevailing flow — consistent with Marcuse's (1985) framework of displacement as neighbourhood-scale, not city-wide.

**3. The typology produces four interpretable flow regimes with distinct spatial logics.**
Using Cascade_Dominance × Cross_Decile_Share, I classify MSOAs into cascade-led, counter-led, symmetric, and lateral types. 58% of MSOAs retained their classification across the decade, confirming structural persistence. Cascade-led clusters in inner south/west London (the gentrification belt); counter-led dominates and spreads outward; symmetric is spatially scattered; lateral concentrates at hierarchy extremes.

**4. Cascade pressure fragmented, not weakened uniformly.**
The cascade-led MSOAs that changed category concentrated in inner West and South London — the areas most actively restructuring in 2011. This suggests some gentrification processes had "completed" by 2021, transitioning from active displacement to settled post-transition neighbourhoods.

**5. Counter-positive divergent MSOAs are the strongest displacement signal.**
~10% of MSOAs have Net_Cascade and Net_Counter pointing in opposite directions. The counter-positive subtype — areas losing population in both hierarchical directions — concentrates in inner-London boroughs (Newham, Hackney, Tower Hamlets). These are pressure points where residents are being squeezed out regardless of direction.

**6. The Typology × Quadrant framework shows volume balance and hierarchical position are independent dimensions.**
Crossing the typology with sign concordance quadrants reveals that cascade-led MSOAs split almost evenly between deprived upward-connected hubs (median D3) and affluent downward-connected hubs (median D8). The same typology label describes very different neighbourhood contexts depending on position.

**7. Ratio-based Cascade_Dominance is the stronger metric design.**
Sensitivity testing confirms the ratio formulation separates direction from intensity, avoids scale confounds, and discriminates IMD trajectories more sharply than the difference-based alternative (both Kruskal-Wallis tests significant, but ratio gives clearer group separation).

---

## Key methodological decisions made

- **Ratio-based Cascade_Dominance** retained over difference-based (§14b sensitivity test).
- **Typology thresholds:** Dominance bandwidth ±0.02 from 0.50; CDS cutoff at 25th percentile.
- **Preprocessing robustness** confirmed across four sensitivity tests (population weights, IMD baselines).

---

## What's left to do

**Immediate (to complete EDA 3):**
- Run the IMD_Pctile_Change validation (Phase F) — code is written, needs execution and interpretation. This connects the flow-based typology to an independent measure of neighbourhood change.
- Partial correlations controlling for Wealth_Decile to test whether cascade metrics carry information beyond hierarchy position.

**Next notebooks:**
- EDA 4: Spatial synthesis (Phase G) — spatial autocorrelation, clustering, borough-level aggregation.
- EDA 5: Case studies — selected MSOAs illustrating each typology with detailed flow narratives.

**For the dissertation write-up:**
- The methodology chapter (§3.8) describes the typology using CFI_Churn × Net_Cascade axes, but the actual analysis evolved to Cascade_Dominance × Cross_Decile_Share. The methodology draft will need updating to reflect this.
- The conceptual framework could benefit from a stronger framing around the escalator effect and the "cascade as counter-current" finding, since this emerged as the central theoretical contribution.

---

## Questions for supervisor

1. The "cascade as localised counter-current" finding is a stronger narrative than what the original proposal assumed (city-wide cascading displacement). Is this reframing appropriate for the dissertation scope, or does it risk undermining the original research question?
2. The Typology × Quadrant framework adds analytical depth but also complexity. How much of this belongs in the main results vs. an appendix?
3. Should I pursue the escalator effect mechanism question (why displaced people move to wealthier deciles), or flag it as out of scope and cite the existing literature?
4. The COVID confound is present throughout the 2021 data. How strongly should I caveat the temporal comparisons?
