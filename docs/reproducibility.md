# Reproducibility guide

This document records the computational order of the cleaned submission branch. It describes file dependencies and execution order only; interpretation of results belongs in the dissertation.

## Before running

1. Clone the repository and work from within the repository directory.
2. Create a Python environment and install `requirements.txt`.
3. Create/populate `data/` using the filenames listed in `data/README.md`.
4. Keep the repository folder structure unchanged while running the notebooks. The retained notebooks use `pyprojroot.here()` to locate the project root and write/read intermediate files under `outputs/`.
5. The submission notebooks are intentionally stored with execution counts and cell outputs cleared. Run them to regenerate numerical displays and figures locally.

## Recommended execution order

### Stage 1 — common geography and London-frame preprocessing

Run:

`notebooks/01_preprocessing/01_geo_harmonisation.ipynb`

Shared module:

`geo_harmonise.py`

Principal generated files consumed later include:

- `outputs/msoa_cascade_features_20260625.csv`
- `outputs/lsoa11_to_msoa11.csv`
- `outputs/geo_harmonisation_remap_audit.csv`
- exclusion/audit CSVs under `outputs/`

### Stage 2 — metric construction, typology and supporting diagnostics

Run the retained notebooks under `notebooks/02_metrics_typology/` in numerical order.

The first notebook consumes `outputs/msoa_cascade_features_20260625.csv` and produces the enriched analytical table used by later stages:

- `outputs/msoa_cascade_features_enriched_20260625.csv`

The typology/diagnostic notebooks use this analytical table and retain the robustness and figure-generation steps associated with the final workflow.

### Stage 3 — national reference frame and frame comparison

Run:

1. `notebooks/03_reference_frames/01_national_frame_preprocessing.ipynb`
2. `notebooks/03_reference_frames/02_frame_comparison.ipynb`

The national-frame preprocessing notebook rereads the raw 2011 and 2021 O-D data and also consumes the enriched London analytical output from Stage 2. Its principal generated output is:

- `outputs/msoa_cascade_national_frame_20260625.csv`

The frame-comparison notebook combines the London and national representations and generates:

- `outputs/eda4_results_for_phase3_20260626.csv`

This table is a major downstream interface for the correspondence and mechanism notebooks.

### Stage 4 — independent correspondence analysis

Run the notebooks under `notebooks/04_correspondence/` in numerical order.

The first notebook contains the underlying Yee/MSOA comparison calculations. The second retains the final map/palette refinement used for the corresponding figure. Both are retained because the final output lineage includes the calculation stage and a later presentation/refinement stage.

Principal retained derived output:

- `outputs/yee_cascade_comparison_20260627.csv`

### Stage 5 — mechanism decomposition, cases and subtype comparison

Run the notebooks under `notebooks/05_mechanisms_cases/` in numerical order where their outputs are required.

The mechanism-tree notebook consumes the frame-comparison and national-frame outputs and generates:

- `outputs/eda9_mechanism_tree_20260705.csv`

The case and mapping notebooks use the mechanism output plus the shared palette module and relevant local geometry/label data. The subtype-proportion notebook is retained alongside the final subtype map because both contribute to the reported comparison workflow.

### Stage 6 — additional IMD robustness

`notebooks/06_robustness/01_imd_baseline_sensitivity.ipynb` retains the separate IMD-baseline sensitivity workflow used during the dissertation analysis.

## Shared modules

Do not move these modules without updating imports in the notebooks:

- `geo_harmonise.py`
- `map_utils.py`
- `flow_yee_palette_v2.py`

They are placed at repository root in the cleaned branch so that the retained notebooks can import them consistently after being reorganised into `notebooks/` subdirectories.

## Tracked intermediate outputs

Selected generated CSVs are intentionally tracked. This serves two purposes: it makes the interfaces between analytical stages visible, and it allows downstream notebooks to be inspected when restricted/raw source data cannot be redistributed. Generated result figures are not tracked in the submission tree; the figure-producing notebooks recreate them locally. These derived files do not replace the raw-data preprocessing workflow: Stage 1 and the national-frame preprocessing notebook both read the raw Census O-D source files directly.

## Historical filenames

The cleaned notebook names are designed for execution order rather than development chronology. `docs/notebook_index.md` records the original repository filename for every retained notebook so that Git history remains easy to trace.
