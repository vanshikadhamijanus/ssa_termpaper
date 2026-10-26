# The Thirsty Cloud

DSS5202 Sustainable Systems Analysis, Group 29. Aditya Vijindra Pandhari,
Apurwa Kumari and Vanshika Dhamija. November 2026.

This project compares water supply and heat-rejection choices for Singapore's
new data-centre capacity during **2027–2035**. All four alternatives share
liquid-cooled IT equipment: wet rejection with desalination (A1), wet rejection
with NEWater (A2), higher-concentration towers with blowdown recovery (A3), and
dry rejection with wet assistance (A4).

The demand model feeds a simplified LCA, LCC and AHP. The current base case gives
A2 the lowest resource cost, A3 lower water use and emissions than A2, and A4 the
lowest site water use. A4's assumed electricity penalty makes its cost and
emissions higher. These are conditional screening results. The equipment costs,
dry-cooler performance and AHP judgments still need site or stakeholder evidence.

## Deliverables

| File in `deliverables/` | Purpose |
|---|---|
| `DSS5202_Group29_TermPaper.docx` and `.pdf` | Report, references and appendices |
| `DSS5202_Group29_Poster.pptx` | One-page poster using the module template |
| `DSS5202_Group29_Poster_preview.pdf` | Poster preview |
| `DSS5202_Group29_Video_Slides.pptx` and `_preview.pdf` | Ten slides with speaker notes |
| `DSS5202_Group29_Video_Script.md` | Three-speaker script with timing and recording instructions |
| `DSS5202_Group29_Submission.zip` | Prepared submission files for the team's final review |

The team still needs to record the ten-minute MP4 and add it to the submission
ZIP. The slides and script do not replace the recording. The
[module brief](https://klpoh.github.io/courses/dss5202/termpaper.html) requires one
ZIP per team containing the report, code, poster and video, due 13 November 2026.

## Rerun the numerical analysis

Run commands from this directory. The existing source files support an offline
analysis run.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/run_all.py
python -m unittest discover -s tests
python src/validate_project.py
```

`run_all.py` runs stages 02–08 and rewrites processed data, result tables and
figures. It includes 10,000 parameter draws and 2,000 preference trials.
`validate_project.py` checks saved results against the model, accounting balances,
AHP consistency and protected-source hashes. Its reports are in
`outputs/validation/`. Passing these checks establishes calculation consistency.
It does not validate unmeasured assumptions. The ZIP's protected-source manifest
covers the files included in the archive. Its separate workspace manifest retains
the full original baseline, including the omitted proposal and style reference.

The numerical input register, `config/assumptions.csv`, records sources and
verification status. Its role field distinguishes model inputs from context
and calibration checks. AHP judgments are in `src/ahp.py`. Simulation settings
are in `src/07_sensitivity.py`. After changing inputs, rerun the analysis
and checks before rebuilding the documents.

To fetch missing registered public sources, run `python src/01_fetch_data.py`.
It keeps existing downloads and refreshes `data/raw/MANIFEST.csv`. A normal
reproduction run does not need this step. The manifest is protected by the
original audit, so refreshing it creates a hash difference that must be recorded
and reviewed. Keep the original baseline. Preserve the supplied source files,
proposal, style-reference PDF and original poster template.

## Rebuild the deliverables

```bash
python src/build_deliverables.py
```

This rebuilds the report, PDF, presentations and submission ZIP from current
outputs. Use `--skip-presentations` to rebuild the report and package while
retaining the existing slides. To run individual stages:

```bash
python src/09_build_paper.py
python src/10_build_poster.py
python src/11_build_video_slides.py
python src/package_submission.py
```

The report combines `paper/report_template.md` with current result tables.
Stage 09 writes the Word document. The full build command also renders its PDF.
Presentation builders read the same outputs and create editable PowerPoint
tables and charts, PDF previews, and the video script. Review the rendered pages
after any content change. Packaging excludes the proposal, supplied style
reference and private `.build/` files.

The full build also runs `src/validate_deliverables.py`, which compares report
tables and presentation values with the saved outputs and checks PDF page counts.
It records the results in `outputs/validation/deliverable_checks.json`.

The PowerPoint builders require the Codex primary runtime with
`@oai/artifact-tool`, bundled LibreOffice, and the installed presentation skill's
validation helpers. Python requirements alone do not install these tools. The
default runtime location is `~/.cache/codex-runtimes/codex-primary-runtime`.
If it is elsewhere, set its root before running the builders:

```bash
export DSS5202_PRESENTATION_RUNTIME="/path/to/codex-primary-runtime"
```

The full build command also uses the bundled Python and the documents skill's
`render_docx.py`. It searches the installed skills automatically. If the renderer
is elsewhere, set `DSS5202_DOCX_RENDERER` to that script's full path.

Build intermediates and private presentation validation reports go in `.build/`.
The supplied PPTX and PDF files can be opened without this generation runtime.

## Project files

| Location | Contents |
|---|---|
| `config/` | Assumption and evidence registers, grid factors, source-change record |
| `data/raw/`, `data/manual/` | Original public sources and download inventory |
| `data/processed/` | Derived input tables |
| `src/` | Analysis code and document builders, with validation checks |
| `outputs/tables/`, `outputs/figures/` | Results used in the deliverables |
| `paper/` | Report source and references, plus the poster template |
| `PROJECT_PLAN.md` | Current design decisions and remaining work |

The LCA covers water supply and incremental heat rejection. It omits common IT
and liquid-loop burdens, upstream wastewater treatment, and several embodied
and indirect-water impacts. Main resource costs exclude carbon monetisation.
Carbon-price and eco-cost cases are separate sensitivities. Simulation rank
frequencies depend on the stated distributions and are not forecasts of which
technology will perform best at a future site.
