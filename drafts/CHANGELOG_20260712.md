# Draft update log — 12 July 2026

Updates integrate analyses from notebooks dated after the previous drafts (Methodology v11 / Conceptual v6: 03 July; Results v1: 04 July): **eda_3b** (08 July), **eda_9b**, **eda_10**, **eda_11** (05 July), and **eda_12 v3** (06 July).

## Results Chapter v1 → v2

| Section | Change | Source |
| --- | --- | --- |
| Preamble | Roadmap updated: mechanism tree in 4.5; two-resolution benchmark comparison in 4.6; four mechanisms in 4.7. | — |
| 4.3.2 | Added cascade-*definition* sensitivity: same-decile outflows (~0.4× the to-poorer arm, ~17% of out-migration); asymmetric broadening triples Cascade-led as a scale artefact; symmetric broadening retains ~80% but collapses Cross_Decile_Share, erasing Lateral; strict definition retained. | eda_3b |
| **4.5.6 (new)** | Time-symmetric mechanism tree: four leaves; INFLOW_MIN = 0.25 justified by an empirical gap (0.226–0.300 in 2011; 0.159–0.312 in 2021); EXT_MAJ = 0.5 declared as a majority convention with a ±0.05 sensitivity band (0.45/0.50/0.55 → 38→103 / 19→78 / 8→46; ×2.7/×4.1/×5.8); D6 structural exclusion note; Table 4.4 leaf counts (inflow-driven 56→13; external-majority 19→78). | eda_9b |
| 4.6 intro | "The short answer is no" replaced by the two-resolution verdict; concurrent-validation (2011) vs persistence-test (2021) framing stated up front. | eda_12 v3 |
| 4.6.1 | Cramér's V / ARI reported once, then **retired** (Stable-base swamping; meaningless at leaf n = 13–90); enrichment + Fisher exact + BH announced. | eda_12 v3 |
| **4.6.2 (new)** | Leaf-level enrichment: inflow-driven not modal-GEN-enriched (lift 0.86 / 0.00; loose 1.52, p = 0.043, fails BH, does not persist); outflow-internal is the BH-robust cell in both years (modal lift 3.55, p = 4.9e-05; 3.19, p = 1.0e-04); outflow-external GEN-depleted (loose lift 0.43, p = 0.0055); Counter-led depleted both years/aggregations; persistent-8 underpowered, Hillingdon caveat. | eda_12 v3 |
| **4.6.3 (new)** | Class-3 subtype decomposition (any-LSOA flags 94/39/101): SupGen ≈ outflow-internal (lift 2.32, q < 0.01 → 3.37, q < 1e-9); MainGen ≈ inflow-driven, concurrent only (lift 2.25, p = 0.065); MargGen no enrichment. Ladder-ceiling caveat; K&C/Westminster geography; inner-only sharpening (lift 1.94, p = 0.002; inner outflow-internal × modal-GEN lift ≈ 20, p = 3e-13). | eda_12 v3 |
| 4.6.4–4.6.6 | Renumbered (were 4.6.2–4.6.4). 4.6.5: persistent set generalised to the named eight (Camden 024/026, Hillingdon 015/016, Islington 022, Southwark 002/009, Tower Hamlets 010 — all Yee-modal Stable; 2/8 loose-GEN). 4.6.6: triangulation closer rewritten as the two-layered verdict + refined definition ("persistent, inflow-led, inner-London cascade"). | eda_9b, eda_12 v3 |
| 4.7 | **Rewritten as four mechanisms.** Persistent cascade is now 8 MSOAs (Camden 026 / TH 010 as exemplars, not "the only two"); profile 2 exemplars named (Southwark 003, Islington 008, Wandsworth 035); **Harrow 008/029 reassigned from "exodus" to the national-ladder artefact** (ext arm 0.43/0.41, majority of downward outflow stays within London); new literal-exodus exemplars **Croydon 044 / Kingston upon Thames 019** (inflow 0.03/0.04, ext arm 0.72/0.69; Kingston a 2011-baseline member, Croydon emergent by 2021). | eda_9b, eda_10, eda_11 |
| 4.8 | Fourth finding extended with leaf collapse/expansion; fifth finding rewritten as the two-resolution result; closing paragraph: "following the flows does not amount to finding gentrification, but it does amount to finding its mechanisms." | eda_12 v3 |
| Figure table | Added EDA 9b threshold-evidence figures, EDA 10 five-class maps, EDA 11 alluvial Figures A–D, EDA 12 v3 lift dot plot + comparison map, EDA 3b summary; Figure 4.23 source updated EDA 7 → EDA 11. | — |

## Methodology v11 → v12

| Section | Change | Source |
| --- | --- | --- |
| 3.6 | New paragraph defending the strict cross-decile cascade definition against same-decile broadenings (supervisor query), with the broad-displacement robustness variant named. | eda_3b |
| 3.10.3 | Rewritten as a two-resolution design: concurrent/persistence temporal framing; pooled V/ARI reported once then retired; leaf-level enrichment (lift, Fisher exact, BH); Class-3 subtype any-LSOA flags and their rationale (Class-3 GEN never modal at MSOA scale). Two-way convergence test retained. | eda_12 v3 |
| 3.10.5 | Rewritten: the three ad-hoc diagnostics are replaced by the time-symmetric mechanism tree — leaves, both thresholds with their distinct epistemic justifications, D6 exclusion, narrative overlays (genuine cascade / exodus), and leaf-annotated alluvial case decompositions feeding 3.10.3. | eda_9b, eda_11 |
| 3.11 | Threshold Sensitivity extended to cover the tree thresholds and definition sensitivity; new limitation **"Structural Ceilings on the Inflow Arm"** (ladder ceiling; any-LSOA flag MSOA-size sensitivity; small-n leaf tests). | eda_9b, eda_12 v3 |

## Conceptual Framework v6 → v7

| Section | Change | Source |
| --- | --- | --- |
| 2.4 | New paragraph: equivalence between lenses is resolution-dependent; pooled null + mechanism-level alignment is itself a substantive outcome; framework anticipated to discriminate gentrification variants (mainstream vs super-gentrification, Butler & Lees 2006) by migratory mechanism. | eda_12 v3 |
| 2.4 closing | Final paragraph now mentions the time-symmetric mechanism decomposition and two-resolution corroboration. | — |

## Items needing your input

1. **Table 4.4 (Results):** the 2011 counts for the *frame-sensitive inflow* and *outflow: internal-majority* leaves are marked ‡ (they sum to 138). The notebooks in the project carry no saved outputs, so please transcribe them from the EDA 9b leaf-count table when you run it. (2021 is complete: 13 / 14 / 78 / 90.)
2. **Hillingdon 015/016 manual check** (Heathrow employment churn) is flagged in 4.6.5 per eda_12 v3 — resolve before final submission if the persistent-8 anchors a headline claim.
3. **Kingston naming:** eda_9b/10 refer to "Kingston 616"; eda_11 (latest case-study notebook) uses "Kingston upon Thames 019". The drafts follow eda_11 — please confirm the MSOA name/code.
4. **References:** add Butler & Lees (2006) to the bibliography (now cited in Conceptual 2.4 and Results 4.6.3); Benjamini–Hochberg may warrant a citation in 3.10.3.
5. The old Results claim that "only two MSOAs" are persistent cascades has been corrected everywhere to the eight-member inflow-driven-both-years set; check the Discussion chapter (not in this project) for the same claim.
