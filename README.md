# Hierarchy-Crossing Migration and Neighbourhood Change in London

Code and reproducibility materials accompanying an MSc Urban Spatial Science dissertation submitted to the Centre for Advanced Spatial Analysis (CASA), University College London, 2026.

This repository documents the computational workflow used to prepare the data, construct hierarchy-crossing migration measures, compare analytical reference frames, and generate the dissertation's reproducibility outputs. Interpretation of the analysis, substantive discussion, and conclusions are contained in the dissertation itself rather than in this repository.

## Repository structure

```text
CASA-Dissertation/
├── README.md
├── requirements.txt
├── .gitignore
├── research-logbook.xlsx
├── geo_harmonise.py
├── map_utils.py
├── flow_yee_palette_v2.py
├── data/
│   └── README.md
├── notebooks/
│   ├── 01_preprocessing/
│   │   └── 01_geo_harmonisation.ipynb
│   ├── 02_metrics_typology/
│   │   ├── 01_metric_landscape.ipynb
│   │   ├── 02_hierarchy_divergence.ipynb
│   │   ├── 03_typology_validation.ipynb
│   │   ├── 04_same_decile_sensitivity.ipynb
│   │   └── 05_typology_map_refinement.ipynb
│   ├── 03_reference_frames/
│   │   ├── 01_national_frame_preprocessing.ipynb
│   │   └── 02_frame_comparison.ipynb
│   ├── 04_correspondence/
│   │   ├── 01_yee_comparison.ipynb
│   │   └── 02_yee_map_refinement.ipynb
│   ├── 05_mechanisms_cases/
│   │   ├── 01_mechanism_tree_thresholds.ipynb
│   │   ├── 02_case_decomposition.ipynb
│   │   ├── 03_case_locator.ipynb
│   │   ├── 04_mechanism_subtype_map.ipynb
│   │   └── 05_subtype_proportions.ipynb
│   └── 06_robustness/
│       └── 01_imd_baseline_sensitivity.ipynb
├── outputs/
│   └── selected derived/audit tables required by downstream notebooks
├── diagrams/
│   └── final dissertation diagrams and editable Draw.io sources
└── docs/
    ├── reproducibility.md
    └── notebook_index.md
```

The clean submission branch is organised by analytical dependency rather than by the chronology in which exploratory notebooks were created. Superseded scripts, abandoned analyses, dissertation drafts, meeting material and development-only outputs remain recoverable through Git history but are not included in the clean tree.

## Computational workflow

The principal dependency chain is:

```text
Raw/source data
    ↓
01_geo_harmonisation.ipynb + geo_harmonise.py
    ↓
outputs/msoa_cascade_features_20260625.csv
    ↓
01_metric_landscape.ipynb
    ↓
outputs/msoa_cascade_features_enriched_20260625.csv
    ↓
01_national_frame_preprocessing.ipynb + raw O-D data
    ↓
outputs/msoa_cascade_national_frame_20260625.csv
    ↓
02_frame_comparison.ipynb
    ↓
outputs/eda4_results_for_phase3_20260626.csv
    ├── correspondence notebooks
    └── mechanism / case notebooks
```

Some dissertation outputs depend on more than one notebook. All contributing notebooks needed for those dependency chains are retained. See [`docs/reproducibility.md`](docs/reproducibility.md) for the recommended execution order and [`docs/notebook_index.md`](docs/notebook_index.md) for the mapping from the cleaned filenames to the original research filenames.

## Data

Raw/source data are intentionally not committed to the repository. The notebooks expect a local `data/` directory at the repository root. Required filenames and the role of each input are documented in [`data/README.md`](data/README.md).

This includes Census origin-destination data, IMD source files, population data, ONS geography lookups, London MSOA geometry and the independent Yee & Dennett classification data used in the correspondence analysis. Where redistribution is restricted or inappropriate, the original source file must be obtained through the relevant access route and placed locally under the expected filename.

Selected derived CSV outputs are retained in `outputs/` because later stages of the workflow consume them directly. These are generated research outputs rather than substitutes for the raw inputs.

## Environment

Create a Python environment and install the packages listed in `requirements.txt`, for example:

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
pip install -r requirements.txt
```

The notebooks use `pyprojroot.here()` to identify the repository root, so run them from within a cloned copy of this repository.

## Reproducing the analysis

After placing the required source files in `data/`, follow the execution order in [`docs/reproducibility.md`](docs/reproducibility.md). The first preprocessing notebook reads the raw 2011 OA-level and 2021 MSOA-level Census O-D files directly, performs the geographical harmonisation and constructs the base analytical features. Later notebooks either consume those derived outputs, reread raw O-D data where required, or generate figures and sensitivity outputs.

The tracked intermediate CSVs make the dependencies transparent and allow later stages to be inspected without publishing restricted raw source data. The submission notebooks are stored without executed cell outputs; running them regenerates numerical displays and figures locally. A complete raw-to-output execution still requires the original source files listed in `data/README.md`.

## Helper modules

`geo_harmonise.py` contains the shared 2011↔2021 MSOA harmonisation logic. `map_utils.py` contains shared mapping functions. `flow_yee_palette_v2.py` contains the shared colour definitions used by the retained final mapping notebooks. They remain at repository root because the notebooks import them from the project root.

## Outputs retained in this branch

The clean branch retains selected intermediate tables consumed by later notebooks and audit tables generated during preprocessing. Result figures are generated by the retained notebooks but are not tracked in the submission tree, avoiding a parallel results archive alongside the dissertation. Earlier output versions, exploratory interactive graphics and outputs from analyses removed from the dissertation remain in Git history but are omitted from the clean tree.

## Research logbook

`research-logbook.xlsx` provides a chronological record of the research process, including the development of the analytical approach, key methodological decisions, data-processing and analysis milestones, revisions, and reflections made during the dissertation. It is retained alongside the reproducibility materials to document how the final analytical workflow developed over the course of the project.

The logbook complements, but does not replace, the dissertation and the reproducibility documentation. The dissertation remains the authoritative source for the final methodology, results, interpretation and conclusions, while the logbook records the research process through which those final decisions were reached.

## Scope of the repository

This repository is supporting reproducibility material. It is intended to show the computational procedures and file dependencies used for the dissertation. The dissertation is the authoritative source for methodological rationale, interpretation of findings, discussion and conclusions.

## Author

Yujing (Olivia) Xing, supervised by Professor Adam Dennett

MSc Urban Spatial Science  

Centre for Advanced Spatial Analysis (CASA)  

University College London
