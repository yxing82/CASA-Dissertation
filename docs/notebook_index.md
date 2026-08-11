# Retained notebook index

This index maps the cleaned submission filenames to the original research filenames. The cleaned branch preserves all notebooks that contribute to the retained analytical dependency chains, including later figure-refinement notebooks where the calculation and final presentation were produced in separate files.

| Clean path | Original repository path | Role |
|---|---|---|
| `notebooks/01_preprocessing/01_geo_harmonisation.ipynb` | `scripts/data_preprocess_geo_harmonise_2021_msoa_missing_solved_from_20260615version_20260625.ipynb` | Raw-data preprocessing, geographical harmonisation, IMD aggregation and base flow features |
| `notebooks/02_metrics_typology/01_metric_landscape.ipynb` | `scripts/eda_1_rerun_metric_landscape_20260625.ipynb` | Metric landscape and enriched analytical table |
| `notebooks/02_metrics_typology/02_hierarchy_divergence.ipynb` | `scripts/eda_2_rerun_hierarchy_divergence_20260625.ipynb` | Hierarchy/divergence diagnostics |
| `notebooks/02_metrics_typology/03_typology_validation.ipynb` | `scripts/eda_3_rerun_typology_validation_20260625.ipynb` | Flow-regime typology and validation |
| `notebooks/02_metrics_typology/04_same_decile_sensitivity.ipynb` | `scripts/eda_3b_cascade_definition_sensitivity_20260708.ipynb` | Same-decile definition sensitivity |
| `notebooks/02_metrics_typology/05_typology_map_refinement.ipynb` | `scripts/eda_3_figure_refine_typology_map_flow_yee_palette_20260729.ipynb` | Final typology-map presentation refinement |
| `notebooks/03_reference_frames/01_national_frame_preprocessing.ipynb` | `scripts/data_preprocess_rerun_national_frame_20260625.ipynb` | National hierarchy, external node and London-external O-D processing |
| `notebooks/03_reference_frames/02_frame_comparison.ipynb` | `scripts/eda_4_rerun_compare_national_frame_and_london_only_FIXED_20260705.ipynb` | A/B/C reference-frame comparison |
| `notebooks/04_correspondence/01_yee_comparison.ipynb` | `scripts/eda_5_yee_msoa_comparison_20260627.ipynb` | Underlying Yee/MSOA correspondence calculations |
| `notebooks/04_correspondence/02_yee_map_refinement.ipynb` | `scripts/eda_5_v3_yee_flow_agreement_elegant_palette_20260729.ipynb` | Final correspondence-map/palette refinement |
| `notebooks/05_mechanisms_cases/01_mechanism_tree_thresholds.ipynb` | `scripts/eda_9b_threshold_justification_mechanism_tree_20260705.ipynb` | Mechanism tree and threshold diagnostics |
| `notebooks/05_mechanisms_cases/02_case_decomposition.ipynb` | `scripts/eda_7_v4_case_decomposition_palette_and_westminster_no_kingston_20260801.ipynb` | Final case-flow decomposition figures |
| `notebooks/05_mechanisms_cases/03_case_locator.ipynb` | `scripts/eda_10_v8_mechanism_case_locator_no_kingston_20260801.ipynb` | Final case-locator map |
| `notebooks/05_mechanisms_cases/04_mechanism_subtype_map.ipynb` | `scripts/eda_12_v7_comparison_map_black_marker_legend_fix_20260729.ipynb` | Final mechanism × subtype map |
| `notebooks/05_mechanisms_cases/05_subtype_proportions.ipynb` | `scripts/eda_13_proportion_reporting_yee_leaf_correspondence_20260723.ipynb` | Proportion-based subtype reporting and appendix ratios |
| `notebooks/06_robustness/01_imd_baseline_sensitivity.ipynb` | `scripts/sensitivity_imd_baseline_20260526.ipynb` | IMD baseline sensitivity |

## Shared code retained outside the notebook folders

- `geo_harmonise.py` — shared geography harmonisation logic.
- `map_utils.py` — shared mapping utilities, moved from `scripts/map_utils.py` to repository root so imports remain available after notebook reorganisation.
- `flow_yee_palette_v2.py` — shared final colour definitions used by retained mapping/case notebooks.

Superseded notebook versions and analyses that are not part of these retained dependency chains remain available in Git history on the original development history; they are not duplicated in the cleaned submission tree.
