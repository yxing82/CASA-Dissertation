from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_ROOT = ROOT / "notebooks"

# Markdown headings that contain interpretation/research-process notes rather than
# instructions needed to reproduce the computational workflow.
DROP_HEADING = re.compile(
    r"^\s*#{1,6}\s*(?:takeaways?|observations?|interpretation|discussion|conclusions?|"
    r"notes?\s+for\s+(?:the\s+)?write[- ]?up|writing\s+notes?)\b",
    re.IGNORECASE,
)

# Individual prose lines that are clearly development/supervision commentary.
DROP_LINE_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"^\s*supervisor\s+comment\b",
        r"^\s*\*\*headline\s*\(computed below\)\s*:\*\*",
        r"where this lives in the write[- ]?up",
        r"to hand to the supervisor",
        r"\bi don['’]t think\b",
        r"\badam is right\b",
        r"^\s*\*\*removed kingston case\b",
    ]
]


def clean_markdown(source: str) -> tuple[str, bool]:
    """Remove only explicit interpretation/process commentary.

    Methodological descriptions, equations, input/output documentation and neutral
    section headings are retained. Cells headed as Takeaways/Observation/etc. are
    dropped because their purpose is interpretation rather than reproducibility.
    """
    lines = source.splitlines(keepends=True)
    first_nonblank = next((line for line in lines if line.strip()), "")
    if DROP_HEADING.match(first_nonblank):
        return "", True

    kept = []
    changed = False
    for line in lines:
        if any(p.search(line) for p in DROP_LINE_PATTERNS):
            changed = True
            continue
        kept.append(line)
    return "".join(kept), changed


def clean_notebook(path: Path) -> dict[str, int]:
    nb = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    outputs_removed = 0
    markdown_cells_removed = 0
    markdown_lines_removed = 0
    new_cells = []

    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            if cell.get("outputs"):
                outputs_removed += len(cell["outputs"])
                cell["outputs"] = []
                changed = True
            if cell.get("execution_count") is not None:
                cell["execution_count"] = None
                changed = True
            metadata = cell.setdefault("metadata", {})
            if "execution" in metadata:
                metadata.pop("execution", None)
                changed = True

        elif cell.get("cell_type") == "markdown":
            original = "".join(cell.get("source", []))
            cleaned, md_changed = clean_markdown(original)
            if md_changed:
                changed = True
                if not cleaned.strip():
                    markdown_cells_removed += 1
                    continue
                markdown_lines_removed += max(0, len(original.splitlines()) - len(cleaned.splitlines()))
                cell["source"] = cleaned.splitlines(keepends=True)

        new_cells.append(cell)

    if new_cells != nb.get("cells", []):
        nb["cells"] = new_cells
        changed = True

    if changed:
        path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    return {
        "changed": int(changed),
        "outputs_removed": outputs_removed,
        "markdown_cells_removed": markdown_cells_removed,
        "markdown_lines_removed": markdown_lines_removed,
    }


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Expected text for {label!r} not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def fix_case_locator_path() -> None:
    path = NOTEBOOK_ROOT / "05_mechanisms_cases" / "03_case_locator.ipynb"
    text = path.read_text(encoding="utf-8")
    old = "NATF       = DATA_DIR / 'msoa_cascade_national_frame_20260625.csv'"
    new = "NATF       = ROOT / 'outputs' / 'msoa_cascade_national_frame_20260625.csv'"
    if old not in text:
        raise RuntimeError("Historical case-locator NATF path was not found")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def clean_data_readme() -> None:
    path = ROOT / "data" / "README.md"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"\n## Derived compatibility file\n.*?(?=\n## Generated data\n)",
        re.DOTALL,
    )
    text2, n = pattern.subn("\n", text, count=1)
    if n != 1:
        raise RuntimeError("Expected derived-compatibility section not found in data/README.md")
    path.write_text(text2, encoding="utf-8")


def update_docs() -> None:
    readme = ROOT / "README.md"
    replace_once(
        readme,
        "│   ├── selected derived tables used by downstream notebooks\n│   └── selected final/appendix figures",
        "│   └── selected derived/audit tables required by downstream notebooks",
        "README output-tree description",
    )
    replace_once(
        readme,
        "The tracked intermediate CSVs make the dependencies transparent and allow later stages to be inspected without publishing restricted raw source data. A complete raw-to-output execution still requires the original source files listed in `data/README.md`.",
        "The tracked intermediate CSVs make the dependencies transparent and allow later stages to be inspected without publishing restricted raw source data. The submission notebooks are stored without executed cell outputs; running them regenerates numerical displays and figures locally. A complete raw-to-output execution still requires the original source files listed in `data/README.md`.",
        "README unexecuted-notebook note",
    )
    replace_once(
        readme,
        "The clean branch retains selected intermediate tables that are consumed by later notebooks, audit tables generated during preprocessing, and the final/appendix graphics associated with the retained workflow. Earlier output versions, exploratory interactive graphics and outputs from analyses removed from the dissertation are omitted from the clean tree but remain in Git history.",
        "The clean branch retains selected intermediate tables consumed by later notebooks and audit tables generated during preprocessing. Result figures are generated by the retained notebooks but are not tracked in the submission tree, avoiding a parallel results archive alongside the dissertation. Earlier output versions, exploratory interactive graphics and outputs from analyses removed from the dissertation remain in Git history but are omitted from the clean tree.",
        "README retained-output policy",
    )

    repro = ROOT / "docs" / "reproducibility.md"
    replace_once(
        repro,
        "4. Keep the repository folder structure unchanged while running the notebooks. The retained notebooks use `pyprojroot.here()` to locate the project root and write/read intermediate files under `outputs/`.",
        "4. Keep the repository folder structure unchanged while running the notebooks. The retained notebooks use `pyprojroot.here()` to locate the project root and write/read intermediate files under `outputs/`.\n5. The submission notebooks are intentionally stored with execution counts and cell outputs cleared. Run them to regenerate numerical displays and figures locally.",
        "reproducibility unexecuted-notebook note",
    )
    replace_once(
        repro,
        "Selected generated CSVs are intentionally tracked. This serves two purposes: it makes the interfaces between analytical stages visible, and it allows downstream notebooks to be inspected when restricted/raw source data cannot be redistributed. These derived files do not replace the raw-data preprocessing workflow: Stage 1 and the national-frame preprocessing notebook both read the raw Census O-D source files directly.",
        "Selected generated CSVs are intentionally tracked. This serves two purposes: it makes the interfaces between analytical stages visible, and it allows downstream notebooks to be inspected when restricted/raw source data cannot be redistributed. Generated result figures are not tracked in the submission tree; the figure-producing notebooks recreate them locally. These derived files do not replace the raw-data preprocessing workflow: Stage 1 and the national-frame preprocessing notebook both read the raw Census O-D source files directly.",
        "reproducibility output policy",
    )


def remove_generated_result_figures() -> list[str]:
    removed = []
    for rel in [Path("outputs/case_study"), Path("outputs/comparison_figs")]:
        root = ROOT / rel
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg", ".pdf", ".html"}:
                removed.append(path.relative_to(ROOT).as_posix())
                path.unlink()
    return removed


def main() -> None:
    fix_case_locator_path()
    clean_data_readme()
    update_docs()

    totals = {
        "notebooks_changed": 0,
        "outputs_removed": 0,
        "markdown_cells_removed": 0,
        "markdown_lines_removed": 0,
    }
    notebooks = sorted(NOTEBOOK_ROOT.rglob("*.ipynb"))
    for path in notebooks:
        stats = clean_notebook(path)
        totals["notebooks_changed"] += stats["changed"]
        totals["outputs_removed"] += stats["outputs_removed"]
        totals["markdown_cells_removed"] += stats["markdown_cells_removed"]
        totals["markdown_lines_removed"] += stats["markdown_lines_removed"]

    removed_figures = remove_generated_result_figures()

    print(f"Cleaned {totals['notebooks_changed']} / {len(notebooks)} notebooks")
    print(f"Removed {totals['outputs_removed']} stored cell outputs")
    print(f"Removed {totals['markdown_cells_removed']} interpretation/process markdown cells")
    print(f"Removed {totals['markdown_lines_removed']} additional process-commentary lines")
    print(f"Removed {len(removed_figures)} generated result figure files")
    for rel in removed_figures:
        print(f"  - {rel}")


if __name__ == "__main__":
    main()
