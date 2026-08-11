# Dissertation-to-code audit

**Audit basis:** `final-draft-20260809.docx` is treated as the specification for the submission repository.

**Branch policy:** this audit is being carried out on `dissertation-submission-cleanup`. Nothing in this audit is merged into `main`, and no analysis notebook has yet been moved, renamed, or deleted.

## Scope and audit standard

This is a provenance and reproducibility audit of the current repository against the numerical and methodological claims in the dissertation. The audit checks current notebook source, stored executed notebook outputs, persisted repository outputs, and cross-file dependencies.

It is **not yet a clean-room end-to-end rerun from raw data**. Several raw inputs referenced by the notebooks are not stored in the repository, including restricted/safeguarded Census O-D material, and the repository currently lacks a root dependency/environment file. These issues are recorded below and must be documented or resolved before the repository is presented as fully reproducible from scratch.

## Audit status

| Dissertation component | Principal current source | Status | Audit finding |
|---|---|---|---|
| Spatial harmonisation and IMD processing (Sections 3.4-3.5; Appendix A.1-A.5) | `scripts/data_preprocess_geo_harmonise_2021_msoa_missing_solved_from_20260615version_20260625.ipynb` + `geo_harmonise.py` | PASS WITH CLEANUP | Stored final outputs support 982 analytical zones; 32 unresolved 2011 OA codes; 2,001 O-D rows; 3,472 person-moves (about 0.051%); zero unresolved 2021 endpoints; and the reported IMD sensitivity/fixed-hierarchy diagnostics. However, early notebook markdown still describes an obsolete 983-zone/exclusion plan and must be rewritten to match the final executed workflow. |
| England-wide hierarchy and external-node assignment (Sections 3.5, 3.10; Appendix A.6-A.8) | `scripts/data_preprocess_rerun_national_frame_20260625.ipynb` | PASS | Stored outputs match the dissertation: 6,777 England MSOAs, 5,795 non-London; London national-decile distribution; London-vs-national rho about 0.9888; population-weighted external position 5.67 -> Decile 6; flow-weighted diagnostics about 6.37/6.39 (2011) and 6.28/6.40 (2021). |
| Wider metric family and metric selection (Section 3.7; Appendix B) | `scripts/eda_1_rerun_metric_landscape_20260625.ipynb` | PASS / ONE ROUNDING CHECK | Stored outputs support the main correlation/redundancy results. One tiny version/rounding discrepancy needs resolution: the notebook output gives the largest reference-set absolute correlation for `Cascade_Dominance` as about 0.493, whereas Table B.2 reports 0.492. |
| Typology construction and ratio-vs-difference validation (Section 3.8; Appendix C.1) | `scripts/eda_3_rerun_typology_validation_20260625.ipynb` | PARTIAL PASS | The source supports the final ratio-based typology and validation design. The exact final Appendix C.1 disagreement table (904/982 agreement; kappa 0.885; +/-49-person difference threshold; 12/25/8/33 disagreement cells) still needs a final provenance check against a current persisted output or rerun. |
| Same-decile sensitivity (Section 3.8; Appendix C.2) | `scripts/eda_3b_cascade_definition_sensitivity_20260708.ipynb` | PASS | Current source/outputs support the strict specification, the published 129/76 Frame-A Cascade-led counts, and the conclusion that adding same-decile flows changes the construct rather than merely tuning a parameter. |
| Reference frames and temporal comparison (Sections 3.10, 4.1-4.3; Tables 4.1-4.2) | `scripts/eda_4_rerun_compare_national_frame_and_london_only_FIXED_20260705.ipynb` | PASS | Stored outputs match all reported A/B/C regime counts. They also match the reported boundary effects: external inflow -17.8%, external outflow +51.3%, and the component changes used to explain the stronger Frame-C shift. |
| Aggregate comparison with Yee & Dennett / modal GEN (Section 3.9.2; Section 4.4; Figure 4.4) | `scripts/eda_5_yee_msoa_comparison_20260627.ipynb` + `outputs/yee_cascade_comparison_20260627.csv` | NEEDS REPAIR / PROVENANCE CHECK | The historical commit and persisted CSV show that this analysis was completed and the CSV contains the final frame variables plus `yee_modal`, `has_gen`, and divergence labels. However, the current notebook is not reliably retrievable as a usable current source through the connected repository, and the final binary statistics (15 both / 26 GEN-only / 198 Cascade-only / 743 neither; Cramer's V 0.075; ARI 0.036) need to be tied to a clearly retained executable script. This is the most important code-provenance gap before submission. |
| IMD correspondence tests (Section 3.9.1; Section 4.4) | EDA comparison/validation chain | NEEDS FINAL PROVENANCE CHECK | The dissertation reports `Cascade_Dominance` correlations of 0.049 and 0.093, Kruskal-Wallis H of 34.5 and 28.9, and small epsilon-squared effects. These values are internally consistent with the stored analysis lineage, but the final submission repo should contain one clearly identified script/output that reproduces all of them. |
| Mechanism tree and threshold justification (Section 3.11; Section 4.5; Appendix C.3-C.4) | `scripts/eda_9b_threshold_justification_mechanism_tree_20260705.ipynb` | PASS WITH TERMINOLOGY CLEANUP | Stored outputs match the mechanism counts (2011: 56/57/19/81; 2021: 13/14/78/90), the shared 0.25-gap logic, and the 0.45/0.50/0.55 external-arm sensitivity. Some notebook markdown still uses stronger development-stage terms such as "genuine cascade"/"exodus"; these should be replaced by the final dissertation's descriptive mechanism terminology without changing the analysis. |
| Case decomposition and Appendix D | `scripts/eda_7_v4_case_decomposition_palette_and_westminster_no_kingston_20260801.ipynb` | PASS | Current case selection matches the final dissertation, including Camden 026, Tower Hamlets 010, Southwark 003, Islington 008, Wandsworth 035, Westminster 019, Harrow 008 and Croydon 044. Kingston is no longer part of the final analysis. |
| Mechanism-subtype comparison (Section 4.6; Figure 4.7; Table 4.4) | `scripts/eda_12_v7_comparison_map_black_marker_legend_fix_20260729.ipynb` | PASS WITH ONE LINE TO TRACE | Stored outputs support the mechanism counts and the key subtype results: 18/81 and 29/90 super-gentrification in internal-majority profiles; 5/56 mainstream in the 2011 frame-robust inflow profile; and 2/78 marginal in the 2021 external-majority profile. The `7/78` any-gentrification line should be explicitly traced to the retained final calculation before cleanup is considered complete. |
| Occupational comparison | `scripts/eda_6_occupational_comparison_20260627.ipynb` | OUT OF SCOPE | The final dissertation research log records the decision on 27 July to remove occupational-ascent analysis. It should not appear in the final submission workflow. It can remain in Git history rather than the clean submission tree. |
| Earlier missing-MSOA repair notebook | `scripts/datat_preprocess_20_missing_msoas_only_in_2021_20260625.ipynb` (or equivalent historical path) | SUPERSEDED / BROKEN | Stored execution contains a `KeyError: 'CHNGIND'`. It is superseded by the final harmonisation route and should not be presented as part of the reproducible workflow. |

## Headline numerical cross-checks already matched

The audited current/stored outputs reproduce the major headline quantities used in the dissertation, including:

- 982 harmonised analytical zones.
- Frame A regime counts: 2011 = 129 Cascade-led, 339 Counter-led, 268 Symmetric, 246 Lateral; 2021 = 76, 416, 244, 246.
- Frame B regime counts: 2011 = 125, 349, 262, 246; 2021 = 70, 440, 226, 246.
- Frame C regime counts: 2011 = 213, 280, 243, 246; 2021 = 195, 452, 89, 246.
- Mechanism counts: 2011 = 56 inflow-driven frame-robust, 57 frame-sensitive inflow, 19 outflow-external-majority, 81 outflow-internal-majority; 2021 = 13, 14, 78, 90.
- External-node population-weighted position = 5.67, rounded to national Decile 6.
- External-flow temporal change: inflows about -17.8%; outflows about +51.3%.
- Mechanism threshold sensitivity: external-majority counts at 0.45/0.50/0.55 = 38/19/8 in 2011 and 103/78/46 in 2021.
- Subtype examples: super-gentrification = 18/81 (22.2%) in the 2011 internal-majority profile and 29/90 (32.2%) in 2021; mainstream = 5/56 (8.9%) in the 2011 frame-robust inflow profile.

## Reproducibility blockers before final submission

### 1. Raw inputs are not all present in the repository

Current notebooks reference inputs such as `data/imd_2010.xls`, `data/imd_2019.csv`, Census O-D files, correspondence/look-up files, Yee-label data and London geometry. Several of these paths are absent from the current repository. This is understandable for restricted/safeguarded data, especially the 2011 O-D source, but the final repository must distinguish:

- files that cannot legally/appropriately be redistributed;
- public files that should be downloaded by the user;
- intermediate files generated by the preprocessing pipeline;
- any small derived files that can safely be retained.

A `data/README.md` with source URLs/names, access conditions and expected filenames is required.

### 2. No root environment/dependency specification is currently available

A root `requirements.txt` is not present at the audited path. The final repository should contain a reproducible environment specification (`requirements.txt`, `environment.yml`, or equivalent) and a documented Python version.

### 3. Aggregate correspondence needs a clearly retained final script

The output CSV exists, and the historical EDA5 commit demonstrates that the analysis was conducted, but the final submission version must make the exact Figure 4.4/Table/Section 4.4 calculation directly reproducible from a retained current notebook/script. This should be repaired before any old versions are removed from the clean tree.

### 4. Development-stage markdown should be aligned with the submitted method

At least the harmonisation and mechanism notebooks contain stale development-stage descriptions that do not match the final dissertation even though their final executed outputs do. These should be edited only at the documentation/comment level; analytical logic and numerical outputs should not be silently changed during repository cleanup.

### 5. Minor numerical/version checks remain

Before declaring the audit closed, explicitly resolve:

- Appendix B.2: 0.492 in the dissertation versus approximately 0.493 in the stored EDA1 output.
- Appendix C.1: confirm the final 904/982, kappa 0.885 and 12/25/8/33 disagreement table from a retained current source/output.
- Section 4.4: bind the final IMD and modal-GEN statistics to a retained executable source.
- Table 4.4: explicitly trace the 2021 external-majority `7/78` any-gentrification calculation.

## Files that should not be removed yet

Until the unresolved provenance checks above are closed, no historical notebook that may contain the only executable version of a reported result should be deleted from the cleanup branch. In particular, the EDA5/aggregate-comparison lineage must be preserved until its final replacement is verified.

## Proposed completion criterion

The repository should be considered audit-ready for reorganisation only when:

1. every main-text figure/table/result family has one identified retained source;
2. every Appendix A-C robustness result has one identified retained source;
3. all reported headline numbers either match exactly or have an explained rounding convention;
4. restricted/missing data are documented with acquisition and expected-path instructions;
5. the computational environment is specified; and
6. development-only/superseded analyses can be removed from the clean tree without breaking any retained dependency.

Only after these conditions are met should the final folder reorganisation, filename cleanup and definitive README crosswalk be performed.