# The Thirsty Cloud: a step-by-step walkthrough

A plain-language guide to what this project does, which data it uses, how each
stage works, and what the results say. It summarises the other documents
rather than replacing them. Where a number appears here, it comes from
`outputs/tables/headline.csv` (base case) and may change if inputs are changed
and the analysis is rerun.

Related documents: [README.md](README.md) (how to rerun),
[PROJECT_PLAN.md](PROJECT_PLAN.md) (design decisions and open work),
[paper/report_template.md](paper/report_template.md) (the full report text),
[data/manual/README.md](data/manual/README.md) (manually collected sources).

---

## 1. The question in one paragraph

Singapore is approving new data-centre capacity (the 200 MW "DC-CFA2" round, plus
hypothetical larger growth cases). Data centres need heat rejection, which in
Singapore usually means cooling towers that evaporate a lot of water. The
project asks: **for new capacity over 2027-2035, which way of supplying and
using cooling water is best on cost, carbon and wider decision criteria?**

Everything is compared on one basis: **heat rejection for 1 MWh of IT energy,
including the make-up water it needs** (the "functional unit").

## 2. The four alternatives

All four share the same liquid-cooled IT equipment, so no option gets credit for
liquid cooling that the others also have.

| ID | What it is | Plain meaning |
|---|---|---|
| A1 | Conventional wet cooling + desalinated water | Standard towers, water from seawater desalination |
| A2 | Conventional wet cooling + NEWater | Standard towers, water from recycled used water |
| A3 | High-concentration towers + blowdown recovery (NEWater) | Run the water through more cycles and recover the waste stream, so less fresh water is needed |
| A4 | Dry cooling with wet assistance (NEWater for the rest) | Mostly air-cooled; adds water-based cooling only on hot hours. Uses little water but more electricity |

Three capacity scenarios: **S1** = 200 MW IT (the real allocation); **S2** = 500 MW
and **S3** = 700 MW total (hypothetical growth, not confirmed).

## 3. The datasets

Raw files live in `data/raw/` (automatic downloads, listed in
`data/raw/MANIFEST.csv` with hashes) and `data/manual/` (files collected by hand).

| Group | Files / source | What it is used for |
|---|---|---|
| Weather | Open-Meteo hourly data, Jurong Island, 2015-2025 | Counts how many hours are too hot for dry cooling (drives A4's wet-assist share) |
| Water | data.gov.sg / SingStat / PUB water sales and tariffs; PUB annual report | National scale check, operator water prices (potable S$3.24/m³, NEWater S$2.50/m³ before GST) |
| Electricity and grid | EMA Singapore Energy Statistics 2026 (`ema_ses2026_all_chapters.xlsx`), EMC monthly USEP prices, SingStat tariffs | Grid emission factor (0.404 kg CO₂/kWh in 2025), electricity price proxy |
| Policy | EDB/IMDA DC-CFA2 fact sheet, IMDA Green DC Roadmap, SS 726:2026 media release | Capacity definition (200 MW is IT load, not divided by PUE), WUE targets, context |
| Benchmarks | PUB water-efficiency benchmark (2.1 m³/MWh), LBNL 2024 US data-centre report, operator sustainability reports (Equinix, Digital Realty, Keppel DC, STT GDC) | Calibrating wet-cooling water use; context for cooling configurations |
| Cost context | Keppel Infrastructure Trust annual report, Eco-costs workbook | Cross-checks on water-plant prices; carbon valuation scenario |
| Literature | Mytton (2021), Li et al. (2023), Santos (2026) water-reuse LCA review | Boundaries and context (not site measurements) |

All numeric inputs are in **`config/assumptions.csv`**: one row per parameter with
low / base / high values, a distribution, a source, a status
(`verified`, `to-verify`, `team-judgement`, `proxy`, ...) and a role
(`model`, `context`, `calibration-check`, `scenario-definition`). Provenance
claims are tracked in `config/evidence_register.json`.

**Important caveat:** many cost and performance inputs (dry-cooler electricity
penalty, recovery equipment capex, NEWater energy, non-energy emission factors)
are team assumptions or proxies, not quotations. The report says so openly.

## 4. The pipeline, stage by stage

Run order is `src/run_all.py` (stages 02-08), then the builders (09-11).

| Stage | Script | What it does | Key outputs |
|---|---|---|---|
| 1 | `01_fetch_data.py` | Downloads public sources, writes the manifest | `data/raw/MANIFEST.csv` |
| 2 | `02_build_inputs.py` | Cleans raw data into tidy tables: grid factor, water prices, hourly-weather statistics, dry-cooler feasible hours, a scale check against national water sales | `data/processed/*.csv` |
| 3 | `03_demand_model.py` | **Demand model.** Annual IT energy = capacity × utilisation × commissioning ramp × 8,760 h. Water = IT energy × WUE (water-use effectiveness). Wet WUE comes from an evaporation + blowdown mass balance, calibrated to the PUB 2.1 m³/MWh benchmark | `demand_annual.csv`, `demand_summary.csv`, `wue_derivation.csv`, demand and WUE figures |
| 4 | `04_lca.py` | **Simplified LCA.** Climate impact per MWh IT: water-production electricity + conveyance + recovery energy + extra dry-cooler electricity + non-energy proxies, times a grid emission factor path | `lca_inventory.csv`, `lca_by_grid.csv`, `lca_totals.csv`, hotspot figures |
| 5 | `05_lcc.py` | **Life cycle costing.** Levelised water cost (capital recovery + O&M + electricity), net present cost 2027-2035, from a social (3 %) and an operator (8 %) viewpoint, plus a cost-vs-carbon frontier | `lcc_per_mwh.csv`, `lcow.csv`, `npc_by_scenario.csv`, `frontier.csv` |
| 6 | `06_ahp.py` | **AHP.** Four-level hierarchy of economic / environmental / water-security / implementation criteria, five weighting scenarios, consistency checks | `ahp_*.csv`, hierarchy and score figures |
| 7 | `07_sensitivity.py` | **Uncertainty.** 10,000 parameter draws (seed 29), 2,000 preference trials (seed 2901), structural cases (swap NEWater for desal, low-carbon grid, discharge cost), tornado charts, break-even thresholds | `mc_*.csv`, `tornado.csv`, `breakeven.csv`, `structural_sensitivity.csv` |
| 8 | `08_summary.py` | Collects the headline numbers into one table | `headline.csv` |
| 9-11 | `09_build_paper.py`, `10_build_poster.py`, `11_build_video_slides.py` | Fill the report template with the latest tables and build the Word/PDF report, poster and slides | `deliverables/` |

Supporting code: `model.py` (all core calculations), `ahp.py` (AHP maths),
`validate_project.py` / `validate_deliverables.py` (consistency checks),
`tests/` (unit tests), `package_submission.py` (the ZIP).

### How the key calculations work

- **Wet cooling water (WUE):** evaporation is 3.6 / latent heat × heat rejected
  × evaporative fraction; blowdown adds a factor CoC/(CoC-1), where CoC is
  "cycles of concentration". The curve is scaled to the PUB benchmark. This is
  calibration, not independent validation.
- **A3:** raising CoC cuts blowdown; recovering part of what remains returns
  water. Treatment electricity is charged only on the recovered water.
- **A4:** the dry loop handles most heat. Tower-equivalent water is used only in
  hours above a temperature threshold, counted from the real hourly weather
  file. Its extra fan/pump electricity is the difference in PUE × 1,000
  (base: 0.05 PUE, so about 50 kWh/MWh).
- **Grid emissions:** the primary case uses the full grid factor. A "50 % green
  electricity" rule is not treated as zero emissions.
- **Costs:** "resource (social) cost" excludes water taxes and carbon pricing;
  "operator cost" uses the real water bill. Carbon-price and eco-cost values are
  separate sensitivities.
- **AHP:** quantitative criteria are scored from the model; qualitative ones use
  illustrative pairwise judgments. No stakeholder survey was done. The
  consistency ratio must be 0.10 or less.

## 5. The results (base case)

Per MWh of IT energy, from `headline.csv`:

| | WUE (m³/MWh) | Extra electricity (kWh/MWh) | CO₂e (kg/MWh) | Resource cost (S$/MWh) | Operator cost (S$/MWh) | AHP rank (balanced) |
|---|---|---|---|---|---|---|
| A1 Wet + desal | 2.10 | 8.0 | 3.42 | 2.60 | 6.80 | 3 |
| A2 Wet + NEWater | 2.10 | 2.1 | 0.99 | **1.00** (lowest) | 5.25 | 2 |
| A3 High-CoC + reuse | 1.46 | 1.6 | **0.74** (lowest) | 1.54 | **4.83** (lowest) | **1** |
| A4 Dry + trim | **0.50** (lowest) | 50.5 | 19.71 | 11.60 | 15.64 | 4 |

What this means:

1. **A2 is cheapest from a resource view.** NEWater is cheaper and lower-carbon
   than desalination at the assumed energy use.
2. **A3 cuts water about 30 % and emissions about 25 % versus A2.** It costs more
   in resource terms but saves the operator money at today's water price. It
   breaks even against A2 for the operator at a NEWater price of about
   S$1.84/m³, below the current S$2.50. It ranks first in the balanced AHP.
3. **A4 saves the most site water but pays heavily in electricity** under the
   assumed 0.05 PUE penalty, so its cost and emissions are far higher. The
   break-even analysis shows A4 only matches A2 if the penalty is near zero
   (about 0.002-0.003 PUE).
4. **Scale:** at 200 MW, A2 needs about 2.6 million m³/year by 2035 (A3 about 1.8,
   A4 about 0.6). The 700 MW case reaches about 9.0 million m³/year for A2.

### How firm are these results?

- In the 10,000-draw parameter simulation (with base AHP judgments fixed), A2 has
  the lowest resource cost in every draw and A3 ranks first in AHP in every
  draw. These are conditional on the stated distributions; they are not
  forecasts. The operator-cost winner is split (A3 in about 60 % of draws, A2 in
  about 40 %).
- Preference trials and structural cases (desal instead of NEWater, low-carbon
  grid, different discharge costs) are reported separately; see the report's
  Section 8.4 and `structural_sensitivity.csv`.
- The conclusions hinge on the weakest inputs: dry-cooler performance, recovery
  capex and the illustrative AHP judgments.

## 6. What is deliberately out of scope

Common IT and liquid-cooling equipment, upstream wastewater treatment,
embodied impacts of cooling equipment, water used in electricity generation, and
a full multi-impact or ISO-conformant LCA. Carbon is not monetised in the main
cost. The AHP is not a stakeholder survey. The report frames everything as
**conditional screening**, not a site decision.

## 7. Checks that back the numbers

- `python -m unittest discover -s tests` tests the AHP maths and model
  invariants (unit consistency, balances, scaling).
- `python src/validate_project.py` compares saved outputs to fresh model calls,
  checks accounting balances and AHP consistency, and verifies source-file hashes
  (`outputs/validation/`).
- `src/validate_deliverables.py` checks that the report, poster and slides match
  the saved tables.

These show the arithmetic is consistent. They do not validate the assumptions.

## 8. What is left to do

From `PROJECT_PLAN.md`: the team still needs to review the conclusions together,
rehearse the three-speaker script, **record the ten-minute MP4**, and add it to
the submission ZIP. The deadline is **13 November 2026**. The ZIP must contain the
report, code, poster and video.

## 9. Suggested reading order for a newcomer

1. This file, for the overall picture.
2. `deliverables/DSS5202_Group29_TermPaper.pdf` (or `paper/report_template.md`),
   Sections 1, 5, 7 and 8.
3. `config/assumptions.csv`, to see every input and how well it is supported.
4. `src/model.py`, then stages 03 to 06 in order, to see the calculations.
5. `outputs/tables/` and `outputs/figures/`, to see the results.
