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
| `DSS5202_Group29_TermPaper.docx` and `.pdf` | Final report (7 November build), references and supplementary material |
| `DSS5202_Group29_Poster.pptx` | One-page poster using the module template |
| `DSS5202_Group29_Video_Slides.pptx` | Twenty slides for the ten-minute recording, prepared in PowerPoint from the report figures; the notes carry the narration and a suggested timing per slide |
| `DSS5202_Group29_Submission.zip` | Prepared submission files for the team's final review |

The team still needs to record the ten-minute MP4 in their own voices and add
it to `deliverables/` before packaging. The slides do not replace the recording. The
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
python src/12_validation_extras.py
python -m unittest discover -s tests
python src/validate_project.py
```

`12_validation_extras.py` adds the checks used in the final report. It compares
the Open-Meteo record with the SingStat station series, reruns A4 under warmer
conditions, tests the AHP scoring rule, separates calibration from validation
in one table, and draws the tornado figure with the five largest drivers.

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

Everything below runs in the Python environment alone:

```bash
python src/13_build_paper_final.py      # report_final.md + outputs -> deliverables/DSS5202_Group29_TermPaper.docx
python src/17_edit_video_deck.py        # re-applies the review wording edits to the 20-slide deck
python src/14_edit_presentations.py     # re-applies the hand edits to the pre-built poster
python src/validate_deliverables.py     # tables, citations, poster and slide checks
python src/package_submission.py        # submission ZIP
```

`13_build_paper_final.py` reads `report_final.md` in the project root, fills every number and
generated table from `outputs/tables` through `src/report_data_final.py`, and
writes the Word file. The PDF is not produced by the Python build. After
rebuilding the Word file, export it with Microsoft Word (File > Save As > PDF,
or on macOS the AppleScript `save as active document file name ... file format
format PDF`) and save it as `deliverables/DSS5202_Group29_TermPaper.pdf`;
`validate_deliverables.py` checks that the PDF is the final build. Figure 1 is drawn by `16_draw_options_figure.py`. Figures 1, 2, 3 and 6 are
diagrams kept as image files in `outputs/figures/fig_report_*.png`; the script
that drew them was not retained.

The poster was generated on 25 October with a presentation toolchain that is
not part of this environment and is supplied as an editable PowerPoint file on
the module template. Every later hand edit is recorded in
`src/14_edit_presentations.py`, which only needs python-pptx and matplotlib; it
also redraws the poster's AHP figure from the current scores. The 20-slide
video deck was prepared in PowerPoint; `src/17_edit_video_deck.py` records the
wording edits made after the 7 November review. The earlier generated 17-slide
deck (`src/15_build_video_slides.py`) is kept in `.build/` and is not a deliverable. Packaging
excludes the proposal, supplied style reference, Office lock files and private
`.build/` files, and reruns the numerical validation first.

## Project files

| Location | Contents |
|---|---|
| `config/` | Assumption and evidence registers, grid factors, source-change record |
| `data/raw/`, `data/manual/` | Original public sources and download inventory |
| `data/processed/` | Derived input tables |
| `src/` | Analysis code and document builders, with validation checks |
| `outputs/tables/`, `outputs/figures/` | Results used in the deliverables |
| `report_final.md`, `references.md` | Report source and APA reference list (project root) |
| `assets/` | NUS logo used on the report title page |
| `PROJECT_PLAN.md` | Current design decisions and remaining work |

The LCA covers water supply and incremental heat rejection. It omits common IT
and liquid-loop burdens, upstream wastewater treatment, and several embodied
and indirect-water impacts. Main resource costs exclude carbon monetisation.
Carbon-price and eco-cost cases are separate sensitivities. Simulation rank
frequencies depend on the stated distributions and are not forecasts of which
technology will perform best at a future site.
