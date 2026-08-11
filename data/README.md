# Data directory

The analysis notebooks expect a local `data/` directory at the repository root. Raw/source data are not committed to this repository. Place the required files here using the filenames below before running the preprocessing workflow.

## Source files expected by the retained notebooks

| Expected filename | Role in the workflow |
|---|---|
| `census_od_2011_oa.csv` | 2011 Census origin-destination migration data at OA level. Read directly by the preprocessing notebooks. |
| `census_od_2021_msoa.csv` | 2021 Census origin-destination migration data at MSOA level. Read directly by the preprocessing notebooks. |
| `imd_2010.xls` | IMD 2010 source data used to construct the fixed deprivation hierarchy. |
| `imd_2019.csv` | IMD 2019 source data used for the later deprivation comparison and population fields used in preprocessing. |
| `ks101ew_lsoa_2011.csv` | 2011 Census LSOA population data used to weight the London IMD aggregation. |
| `ks101ew_lsoa_2011_allengland.csv` | England/Wales LSOA population data used by the national-frame preprocessing notebook. |
| `NSPCL_NOV22_UK_LU.csv` | Postcode/geography lookup used for OA→MSOA and LSOA→MSOA translation. |
| `msoa_2011_to_2021_lookup.csv` | 2011↔2021 MSOA correspondence used in preprocessing. |
| `MSOA_2011_to_2021_lookup_for_identification.csv` | ONS identification/change lookup used by the shared harmonisation logic and MSOA-name lookup. |
| `london_msoa_2011.geojson` | London 2011 MSOA geometry used by mapping notebooks. |
| `yee_LSOA_labels_forMapping.csv` | LSOA-level independent neighbourhood-change labels used by the correspondence notebooks. |

The exact acquisition/access route for a source may depend on the original provider and licensing or access conditions. In particular, source data that cannot appropriately be redistributed should be obtained through the same authorised route used for the dissertation rather than committed to this repository.

## Derived compatibility file

`msoa_cascade_national_frame_20260625.csv` is a **derived** file, not raw data. The canonical generated copy is retained under `outputs/`. A duplicate is also tracked here solely because the retained final case-locator notebook reads this historical path. It should not be treated as a source dataset.

## Generated data

The principal generated tables are stored in `outputs/`. They are created by the retained preprocessing and analysis notebooks and are used as explicit inputs to later workflow stages. See `docs/reproducibility.md` for the dependency order.
