# The Thirsty Cloud: Execution Plan
**DSS5202 Sustainable Systems Analysis, Group 29** · Aditya Vijindra Pandhari · Apurwa Kumari · Vanshika Dhamija
*Plan v1, 19 Oct 2026*

---

## 0. Where we are

| Done | Where |
|---|---|
| Scope and methods fixed by the proposal: demand model → LCA + LCC → AHP → sensitivity | `DSS5202_Group29_TermPaper_Proposal.docx.pdf` |
| 26 scriptable sources downloaded and logged in a manifest | `data/raw/`, `data/raw/MANIFEST.csv` |
| Raw data cleaned into analysis-ready tables | `data/processed/` |
| Every parameter logged with low/base/high values, source and verification status | `config/assumptions.csv` |
| Demand model checked against PUB's benchmark from first principles (see §1) | `data/processed/wue_heat_balance.csv` |
| List of the 8 sources we have to download by hand | `data/manual/README.md` |

**Reproduce:**
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/01_fetch_data.py      # downloads + MANIFEST (stdlib only)
python src/02_build_inputs.py    # tidy tables + calibration checks
```

---

## 1. Early findings that should shape the paper

1. **Our demand model reproduces PUB's figure from physics.** Evaporative cooling water ≈ (3.6 / latent heat) × heat rejected per IT kWh × evaporative fraction, multiplied by CoC/(CoC−1) for blowdown. This gives **WUE ≈ 2.0–2.3 m³/MWh at CoC 3–4**. PUB's data-centre median is **2.1 m³/MWh** (Sectoral Water Efficiency Benchmark, Dec 2025), and IMDA's 2021 median was 2.2. Because the physics and the benchmark agree, the WUE scenarios can be defended rather than just assumed.
2. **Raising CoC alone stops working below about 1.7 m³/MWh.** WUE only falls from 2.30 to 1.68 as CoC goes from 3 to 12. To reach WUE ≈ 1.4 a site has to *recover blowdown* (on-site reuse). Getting below 1 needs a change of cooling *technology* (liquid cooling with dry or adiabatic heat rejection). This gives us three demand-side alternatives that are clearly different from each other.
3. **Scale.** 200 MW (DC-CFA2), base case: IT = 160 MW, 70 % utilisation, WUE 2.1 → **≈ 2.1 million m³/yr ≈ 5,600 m³/day ≈ 0.31 % of national water sales** (669 million m³ in 2025). A single desalination plant (Tuas, about 137,000 m³/d) is about 25 times larger.
   → **Framing for the paper:** no plant will be built just for the DC-CFA2 sites, so we price *marginal* water (levelised cost and emissions per m³ of an expanding NEWater or desalination system), not a dedicated plant. The stakes grow with **cumulative** growth (Roadmap +300 MW, further calls, AI density), with the **energy–carbon** cost of each m³, and with the **policy precedent** for AI-era data centres. All three capacity scenarios should be presented to show this.
4. **Where the sites are matters.** The fact sheet says all four DC-CFA2 awardees (Digital Realty, Equinix, Keppel DC, STT GDC; 50 MW each) **will be on Jurong Island**. That island already has industrial-water and NEWater supply and the Jurong Island desalination plant. The supply alternatives are therefore realistic, and the weather data is pulled for Jurong Island.
5. **Weather data caveat.** Open-Meteo/ERA5 reanalysis averages over a grid cell, which smooths temperature peaks: it shows only 38 h/yr above 32 °C. Hours when dry coolers cannot cope must be cross-checked against NEA/MSS station data (SingStat monthly data is already downloaded) before we fix `wue_liquid_dry` and `dpue_dry`.

---

## 2. Study design (definitions to put in the Goal & Scope section)

### 2.1 Goal (follows the LCA lecture §3.1 template)
> *Compare the life-cycle cost, GHG emissions and wider sustainability performance of strategies for meeting the additional cooling-water needs of Singapore's new data-centre capacity, 2027–2035. Results are for PUB and IMDA/EDB to use in water planning and in setting data-centre water-efficiency requirements. The study is comparative and will not be used for public product claims.*

### 2.2 Function and functional unit
- **Function:** reject the heat produced by IT load in new Singapore data centres, including supplying all the make-up water.
- **Primary FU:** *heat rejection for 1 MWh of IT energy in a new Singapore DC operating 2027–2035.* Every strategy delivers this same service, so supply-side and demand-side options can be compared on one basis.
- **Secondary metrics:** (a) per m³ of water demand met *or avoided* (levelised cost of water, LCOW, and levelised cost of water saved); (b) system totals for 2027–2035 under each capacity scenario.

### 2.3 Alternatives (strategies)
| ID | Strategy | Cooling at the DC | WUE (m³/MWh_IT) | Make-up water source |
|---|---|---|---|---|
| **A1** | *Supply more:* desalination | Evaporative towers, CoC ≈ 3 | 2.1 | Potable, with the marginal m³ from SWRO |
| **A2** | *Supply more:* NEWater | Evaporative towers, CoC ≈ 3 | 2.1 | NEWater, with the marginal m³ from reclamation |
| **A3** | *Reduce:* efficient evaporative + on-site reuse | High CoC (8) + side-stream treatment + blowdown recovery | ≈ 1.4 | NEWater (residual) |
| **A4** | *Reduce:* liquid cooling + dry/adiabatic rejection | Direct-to-chip (SS 726) + dry coolers with adiabatic trim | ≈ 0.3 | NEWater (residual) |

*Optional A5 "policy portfolio":* a WUE cap of 1.5 plus a NEWater requirement for new DCs. Add it only if time allows.
For A3/A4 the residual source is NEWater in the base case; switch it to desalination in the sensitivity analysis.

### 2.4 System boundary
**Included:** water production (intake → treatment → conveyance to Jurong Island); on-site water treatment and reuse equipment at the DC; **the change in DC cooling electricity** (ΔPUE) between strategies, which is the energy side of the water–energy trade-off; blowdown discharge (waterborne fee, and used-water treatment energy if data allow); simplified embodied emissions and chemicals for plants, using per-m³ factors from the literature.
**Excluded, with reasons:** IT equipment and building shell (the same in every strategy); DC electricity other than the cooling difference; end-of-life (usually <5 % of water-system impacts in the literature; mention it qualitatively).
**Draw this** as the system-boundary diagram (cf. LCA lecture p.22): a foreground DC-cooling system and a background water-supply system, with the electricity grid feeding both.

### 2.5 Scenarios
| Dimension | Levels |
|---|---|
| Capacity (`cap_*`) | **S1** DC-CFA2 200 MW · **S2** + Roadmap 300 MW · **S3** + a further call, 200–500 MW from ~2029 |
| Grid (`ef_grid_*`) | BAU (~0.38 kg/kWh by 2035) · **Low-carbon grid** (~0.25 by 2035: imports, solar, H₂) · Flat (0.40) |
| Perspective | **Social** (3 %, full production cost + externality) · **Operator** (8 %, tariffs + fees + capex) |

**Open item to settle in week 1:** does "200 MW of DC capacity" mean IT load or facility power? We assume facility power, so IT = MW / PUE (`mw_basis_it_share` = 0.8), and we test 1.0. Say this explicitly in the paper.

---

## 3. Methods, module by module

All modules read `config/assumptions.csv`, so one edit there flows through every result.

### 3.1 Demand model (`src/03_demand_model.py`, to build) · answers Q1 and Q2
- Annual IT energy: `E_IT(t) = Σ_tranches MW × it_share × util × ramp(t) × 8760` (MWh).
- Water: `W(t) = E_IT(t) × WUE_strategy`, where WUE for A1–A3 comes from the heat-balance relation (§1.1) and can be modulated monthly with wet-bulb data from `weather_monthly.csv`.
- For A4: water use = trim-hours share × evaporative WUE. Trim hours = hours when dry-bulb is above (supply temperature − approach), from the weather data.
- Outputs: annual demand 2027–2035 for every strategy × scenario, plus a fan chart.
- **Validation:** heat-balance WUE against PUB 2.1 / IMDA 2.2 (done), and against operator-reported Singapore WUE (manual source M5).

### 3.2 Simplified LCA (`src/04_lca.py`) · Q3 (carbon)
- Midpoint category: **climate change, GWP100** (ReCiPe 2016 / IPCC AR6), as in the lecture case studies. Report **electricity use (kWh/MWh_IT)** explicitly, as the LED case study does, and describe **brine and chemical discharge** qualitatively or semi-quantitatively (brine m³). Brine also feeds the AHP.
- Inventory per FU:
  `kWh = WUE × (SEC_source + SEC_distrib) + WUE_recovered × SEC_hicoc + ΔPUE × 1000`
  `GWP = kWh_grid × EF_grid(t) + kWh_DC × EF_grid(t) × (1 − green_share) + WUE × GHG_nonenergy`
- Report a hotspot (contribution) table of water production, conveyance, on-site treatment and the DC energy penalty, set out like the lecture's LED tables.
- **The trade-off to state explicitly:** A4 saves water but may *add* DC energy (dry coolers in the tropics) or *save* it (liquid cooling, −30 %). The net sign is an empirical question, so tell it as a story.

### 3.3 LCC and environmental LCC (`src/05_lcc.py`) · Q3 (cost)
Follows the LCC lecture §2.8, §3 and §4:
- **LCOW** for supply (lecture eq. 6, with m³ in place of kWh): `LCOW = [I + Σ (O&M_k + Elec_k)/(1+i)^k − SV/(1+i)^N] / Σ Q_k/(1+i)^k`.
  Check it two ways: **bottom-up** (Tuas capex S$217 m / 137k m³/d, plus SEC × price, plus O&M) and **top-down** (PPP first-year prices: Keppel Marina East S$1.08/m³ desal, Changi NEWater S$0.28–0.30/m³).
- **Levelised cost of water saved** for A3/A4 = (incremental capex + O&M ± energy-penalty cost) / m³ avoided.
- **NPC and EUAC per MWh_IT** for each strategy (use the capital recovery factor so the 2027–35 window doesn't cut off asset lives).
- **eLCC:** add monetised GHG at (a) the eco-cost of 0.163/kg (lecture) and (b) the Singapore carbon tax path S$45 → S$50–80/t. Follow the lecture warning: **don't add undiscounted environmental cost to discounted economic cost.** Discount both, or compare both undiscounted.
- **Two perspectives:** social (3 %) and operator (8 %, pays tariffs S$3.24 potable or S$1.45 NEWater, plus waterborne fee). Any gap between them is a policy finding: does the price signal reward water efficiency?
- **Cost vs. carbon efficient frontier and dominance analysis** (lecture §3.2): find which strategies are Pareto-efficient, and drop dominated ones before AHP, or flag them.

### 3.4 AHP (`src/06_ahp.py`) · Q4
Use the lecture's `AHPmat` (Algebra/Power method), the RI table and the CR ≤ 0.1 rule, the **3-level+ hierarchy** (cf. the "Sustainable New Energy Technologies" case, §6), and **rainbow-diagram sensitivity** (§3.2).

```
Goal: Best strategy to meet DC cooling-water needs 2027–2035
├── C1 Economic      ├─ C1a Societal life-cycle cost (NPC, social)        [quant]
│                    └─ C1b Cost borne by DC operators (NPC, private)     [quant]
├── C2 Environmental ├─ C2a GHG per MWh_IT (LCA)                          [quant]
│                    ├─ C2b Total electricity use                         [quant]
│                    └─ C2c Marine impact: brine & chemical discharge     [semi-quant / pairwise]
├── C3 Water security├─ C3a Water drawn from national supply (m³)          [quant]
│                    ├─ C3b Weather resilience & source diversification   [pairwise]
│                    └─ C3c Dependence on used-water feedstock / NEWater capacity [pairwise]
└── C4 Implementation├─ C4a Technical maturity & tropical reliability (SS 726) [pairwise]
                     ├─ C4b Policy alignment / enforceability (Roadmap, MWEMP)   [pairwise]
                     └─ C4c Effect on other water users (tariffs, equity)       [pairwise]
Alternatives: A1 Desal · A2 NEWater · A3 High-CoC+reuse · A4 Liquid+dry
```
- **Quantitative leaves:** turn model outputs into local priorities by ratio scaling (`w_i ∝ 1/x_i` for "less is better"; CR = 0 by construction). Alternatively use the **AHP ratings method** (lecture §7). Keep a note of which we used and why.
- **Qualitative leaves:** each member fills in the pairwise matrices independently. Combine them by **element-wise geometric mean** (standard group-AHP practice) and keep CR < 0.1. Write a one-line evidence note for each judgement (e.g. "SWRO brine to the Singapore Strait; PUB EIA ...").
- **Weighting scenarios** (based on published stakeholder positions, not treated as their real preferences, as the proposal says): **W1 Balanced** · **W2 PUB / water security** · **W3 Operator / economic** · **W4 Climate (EMA/NGO)** · **W5 Growth (IMDA/EDB)**. Report the ranking under each, and the rainbow diagram for each main criterion.

### 3.5 Sensitivity and uncertainty (`src/07_sensitivity.py`) · Q5
Follows the LCC lecture's solar PV case (tornado + Monte Carlo + risk profile):
1. **One-way tornado** on NPC/MWh_IT and GWP/MWh_IT for each strategy, using the low/high columns of `assumptions.csv`. Expected drivers: WUE, SEC_desal, EF_grid, electricity price, ΔPUE, capex, discount rate.
2. **Scenario matrix:** capacity S1–S3 × grid (BAU / low-carbon / flat) × perspective.
3. **Break-even analysis:** the grid EF at which A4 beats A2 on carbon; the water tariff at which A3 pays back for the operator; the SEC_desal at which desal and NEWater are equal.
4. **Monte Carlo** (10,000 draws, triangular distributions from low/base/high): cost and GWP distributions, **P(each strategy ranks 1st)**, and the probability that the cost difference is ≤ 0 (cf. the lecture's VaR / P(NPV ≤ 0)).
5. AHP: rainbow diagrams. Optional: Dirichlet-perturbed weights → rank-reversal probability.

### 3.6 Optional extension, only if ahead of schedule: MODM
A small bi-objective LP choosing the share of each new-capacity tranche assigned to A1–A4, to minimise NPC and GWP subject to a cap on water drawn. Solve by weighted sum or ε-constraint to trace the Pareto front (MODM lecture §2.3). This links the course methods together, but it is **not required** by the proposal.

---

## 4. Data sources

### 4.1 Downloaded by script (`src/01_fetch_data.py`): all 26 fetched OK on 19 Oct 2026
| # | Source | Link | File in `data/raw/` | Used for |
|---|---|---|---|---|
| D1 | EMA grid emission factors 2005–2020 (data.gov.sg) | [d_3de362b5…](https://data.gov.sg/datasets/d_3de362b580b2dd2fd50cc1006d4edd4f/view) | `datagovsg/ema_grid_emission_factor.csv` | LCA EF history and trend |
| D2 | SingStat water sales (potable, domestic/non-domestic, NEWater) | [d_9db4902c…](https://data.gov.sg/datasets/d_9db4902c7a47357441dac7d2806032a5/view) | `datagovsg/singstat_water_sales_annual.csv` | Scale and context |
| D3 | PUB NEWater sold 2007– | [d_2eceeb79…](https://data.gov.sg/datasets/d_2eceeb792a0fca1caa74304d47b46060/view) | `datagovsg/pub_newater_sold_annual.csv` | NEWater growth |
| D4 | PUB potable water sold | [d_cb1d25dd…](https://data.gov.sg/datasets/d_cb1d25dd5cfde21bb9fa704af0e3a962/view) | `datagovsg/pub_potable_water_sold_annual.csv` | Context |
| D5 | PUB NEWater tariff + waterborne fee | [d_50830e6a…](https://data.gov.sg/datasets/d_50830e6a799ccfd00b1ed0a5294920d7/view) | `datagovsg/pub_newater_tariff.csv` | Operator LCC |
| D6 | PUB industrial water tariff | [d_bab2ba9a…](https://data.gov.sg/datasets/d_bab2ba9ae53292abd526f4476bfa4de5/view) | `datagovsg/pub_industrial_water_tariff.csv` | Operator LCC |
| D7 | SingStat electricity tariff (monthly, annual) | [d_61eac3cd…](https://data.gov.sg/datasets/d_61eac3cdb086814af485dcc682b75ae9/view), [d_d610f8ed…](https://data.gov.sg/datasets/d_d610f8ed1864daa6c7e790318bbc3323/view) | `datagovsg/singstat_electricity_tariff_*.csv` | Electricity price |
| D8 | SingStat electricity generation & consumption | [d_3745e3aa…](https://data.gov.sg/datasets/d_3745e3aa98ff3c4bcfcb8e1f6dffef42/view) | `datagovsg/singstat_electricity_gen_consumption.csv` | Context |
| D9 | SingStat GHG by sector | [d_1b8dcef6…](https://data.gov.sg/datasets/d_1b8dcef6bf32ece26deca60e59d99f71/view) | `datagovsg/singstat_ghg_by_sector.csv` | Context |
| D10 | SingStat monthly temperature, RH, rainfall (station) | [d_1744ca68…](https://data.gov.sg/datasets/d_1744ca68dc7ed37221b17c441042405e/view) | `datagovsg/singstat_climate_monthly.csv` | Cross-check of reanalysis |
| D11 | SingStat final energy by sector | [d_70d24796…](https://data.gov.sg/datasets/d_70d247965470ea125814eee0171c1dd1/view) | `datagovsg/singstat_final_energy_by_sector.csv` | Context |
| D12 | **Open-Meteo hourly weather, Jurong Island, 2015–2025** (T, RH, dew point, **wet-bulb**) | [archive-api.open-meteo.com](https://open-meteo.com/en/docs/historical-weather-api) | `weather/openmeteo_jurong_island_hourly_2015_2025.csv` (96k rows) | Monthly WUE; dry-cooler hours |
| D13 | Our World in Data energy dataset | [owid/energy-data](https://github.com/owid/energy-data) | `csv/owid_energy_data.csv` | Fuel mix, life-cycle carbon intensity |
| D14 | EDB & IMDA (2026) DC-CFA2 fact sheet | [PDF](https://www.edb.gov.sg/content/dam/edb-en/about-edb/media-releases/news/four-data-centre-proposals-selected-as-part-of-second-data-centre/Fact%20Sheet%20-Four%20data%20centre%20proposals%20selected%20as%20part%20of%20second%20data%20centre.pdf) | `docs/edb_imda_2026_dc_cfa2_factsheet.pdf` | 4 × 50 MW, Jurong Island, ≥50 % green, liquid cooling |
| D15 | IMDA (2024) Green DC Roadmap | [PDF](https://www.imda.gov.sg/-/media/imda/files/how-we-can-help/green-dc-roadmap/green-dc-roadmap.pdf) | `docs/imda_2024_green_dc_roadmap.pdf` | Median WUE 2.2; target ≤ 2.0; cooling towers ≈ 97 % of DC water; CoC |
| D16 | ESG & IMDA (2026) SS 726:2026 media release | [PDF](https://www.enterprisesg.gov.sg/-/media/esg/files/media-centre/media-releases/2026/august/mr03826_singapore-launches-worlds-first-liquid-cooling-standard-for-data-centres-in-tropical-climates.pdf) | `docs/esg_imda_2026_ss726_media_release.pdf` | Liquid cooling saves >30 % energy; water-efficiency guidance |
| D17 | PUB Sectoral Water Efficiency Benchmark | [page](https://www.pub.gov.sg/Public/WaterLoop/Water-Conservation/Resources-on-Water-Efficiency-Measures/Sectoral-Water-Efficiency-Benchmark) | `docs/pub_sectoral_water_efficiency_benchmark.html` | **DC median 2.1 m³/MWh** |
| D18 | PUB (2023) decarbonisation strategy | [page](https://www.pub.gov.sg/Resources/News-Room/PressReleases/2023/03/PUB-decarbonisation-strategy) | `docs/pub_2023_decarbonisation_strategy.html` | Desal 3.5 → <2 kWh/m³; demand doubles by 2065 |
| D19 | PUB (2024) NEWater journey | [page](https://www.pub.gov.sg/Resources/News-Room/PressReleases/2024/09/Singapore-NEWater-journey) | `docs/pub_2024_newater_journey.html` | Tuas NEWater 75 mgd; biomimetic −20 % energy |
| D20 | PUB (2023) water price increase | [page](https://www.pub.gov.sg/Resources/News-Room/PressReleases/2023/09/Water-price-to-rise-from-April-2024-Government-to-provide-support) | `docs/pub_2023_water_price_increase.html` | Potable +S$0.50, NEWater +S$0.17 /m³ |
| D21 | NCCS carbon tax | [page](https://www.nccs.gov.sg/singapores-climate-action/mitigation-efforts/carbontax) | `docs/nccs_carbon_tax.html` | S$25 → 45 → 50–80 /t |
| D22 | Mytton (2021) *npj Clean Water* 4:11 | [PDF](https://www.nature.com/articles/s41545-021-00101-w.pdf) | `docs/mytton_2021_dc_water_consumption.pdf` | WUE ranges; direct vs indirect water |
| D23 | Li et al. (2023) *Making AI less "thirsty"* | [arXiv](https://arxiv.org/abs/2304.03271) | `docs/li_et_al_2023_making_ai_less_thirsty.pdf` | On-site vs off-site water; weather dependence |
| D24 | SP Group tariff page, EDB news page | [SP](https://www.spgroup.com.sg/our-services/utilities/tariff-information) | `docs/*.html` | Current tariff; citation snapshot |

*Note:* the data.gov.sg dataset labelled "Potable Water Tariff" (d_115300b3…) actually serves sales volumes, so we excluded it. The potable price comes from D20 instead.

### 4.2 Manual downloads (details and filenames in `data/manual/README.md`)
| # | Source | Link | Why it can't be scripted |
|---|---|---|---|
| M1 | **EMA Singapore Energy Statistics 2025**, Ch.2 (EF 2021–24) and Ch.3 (electricity by sub-sector, incl. Info & Comms) | https://www.ema.gov.sg/resources/singapore-energy-statistics | JS-rendered page |
| M2 | EMC USEP wholesale prices | https://www.emcsg.com/marketdata/priceinformation | JS / interactive |
| M3 | SS 726:2026; SS 697:2023 | [SS eShop](https://www.singaporestandardseshop.sg/Product/SSPdtDetail/2b7aa78a-36c9-4656-abc5-eb4dc1a6e431) | Paid; check NUS Libraries |
| M4 | LBNL (2024) US Data Center Energy Usage Report | [PDF](https://eta-publications.lbl.gov/sites/default/files/2024-12/lbnl-2024-united-states-data-center-energy-usage-report.pdf) | Server blocks scripts |
| M5 | Sustainability reports: **Equinix, Digital Realty, Keppel DC, STT GDC** (the awardees) + Google, Microsoft, AWS | company sites | URLs change every year |
| M6 | PUB Annual Report; Keppel Infrastructure Trust AR (Keppel Marina East Desalination Plant) | pub.gov.sg / kepinfratrust.com | Annual PDFs |
| M7 | Peer-reviewed LCA/LCC literature | NUS Libraries / Scopus | Paywalled |
| M8 | Eco-costs dataset | https://www.ecocostsvalue.com/data/ | Registration |

### 4.3 Values already in `config/assumptions.csv` that come from these sources
EDB 200 MW (4 × 50) · PUE ≤ 1.25 · ≥ 50 % green energy · WUE 2.1 (PUB) / 2.2 (IMDA 2021) / ≤ 2.0 target · desal 3.5 kWh/m³ (target < 2) · NEWater 0.6–0.8 kWh/m³ · grid EF 0.412 (2023), 0.402 (2024) · Tuas desal plant S$217 m for 137k m³/d · Keppel Marina East PPP S$1.08/m³ · NEWater PPP S$0.276–0.30/m³ · potable S$3.24, NEWater ≈ S$1.45/m³ · carbon tax S$45 → 50–80 · eco-cost 0.163/kg.
**29 of the 50 parameters are marked `to-verify`.** Week 1 should move as many as possible to `verified`, citing the page number.

### 4.4 Literature search strings (Scopus / Web of Science via NUS Libraries)
- `"seawater reverse osmosis" AND "life cycle assessment" AND (GHG OR "carbon footprint")`: non-energy kgCO₂e/m³
- `("water reuse" OR "water reclamation" OR "potable reuse") AND "life cycle" AND (cost OR GHG)`
- `("data center" OR "data centre") AND ("water usage effectiveness" OR WUE OR "cooling tower")`
- `"cooling tower" AND ("cycles of concentration" OR blowdown) AND (reuse OR recovery)`
- `("direct-to-chip" OR "liquid cooling") AND (water OR WUE) AND (tropical OR "hot humid")`
- `Singapore AND (desalination OR NEWater) AND (cost OR energy)`

### 4.5 Data gaps and how we handle them
| Gap | Handling |
|---|---|
| No site-level WUE for the new DCs (not built yet) | Physics-based WUE calibrated to PUB/IMDA medians, with ranges tested |
| Marginal (not average) cost and carbon of water | Use PPP prices + bottom-up LCOW and treat the spread as uncertainty |
| ΔPUE of dry cooling in the tropics | Weather-driven estimate + literature range; break-even analysis |
| Non-energy LCA factors | Literature range; show in the tornado that they're second-order (expected) |
| Future grid EF | Three explicit trajectories, including the low-carbon grid case |

---

## 5. Code layout

```
Term Paper/
├── PROJECT_PLAN.md            ← this file
├── requirements.txt
├── config/
│   ├── assumptions.csv        ← single source of truth for every parameter (low/base/high, source, status)
│   └── grid_ef_ema_2021_2024.csv
├── data/
│   ├── raw/                   ← written by 01 (never edit by hand) + MANIFEST.csv
│   ├── manual/                ← hand downloads (README lists them)
│   └── processed/             ← written by 02
├── src/
│   ├── sources.py             ← registry of every source (feeds the manifest + reference list)
│   ├── 01_fetch_data.py       ✅ built and run
│   ├── 02_build_inputs.py     ✅ built and run
│   ├── 03_demand_model.py     ☐ (week 2)
│   ├── 04_lca.py              ☐ (week 2)
│   ├── 05_lcc.py              ☐ (week 3)
│   ├── 06_ahp.py              ☐ (week 3), reuse the lecture's AHPmat / renorm_wt / rainbow_diagram
│   ├── 07_sensitivity.py      ☐ (week 4)
│   └── 08_figures.py          ☐ (week 4): every paper/poster figure from one script
└── outputs/{tables,figures}/
```
Conventions: SGD in 2026 prices · m³ and MWh_IT · years as int · every number in the paper traceable to `assumptions.csv` or an `outputs/` table.

---

## 6. Work plan and roles

*Suggested split, aligned with the methods. Swap freely. Everyone reviews everyone else's module.*

| Member | Lead on | Also |
|---|---|---|
| **Vanshika** | Data pipeline, demand model (3.1), sensitivity and Monte Carlo (3.5), integration, figures | Scenario design |
| **Aditya** | LCC/eLCC (3.3): capex/opex, PPP prices, tariffs, operator vs social view | Policy recommendations (pricing) |
| **Apurwa** | LCA (3.2), AHP (3.4): hierarchy, weighting scenarios, stakeholder evidence | Policy recommendations (standards) |

**Timeline.** Starts Mon 20 Oct; **shift it to match the actual submission deadline.**

| Week | Dates | Goals | Exit criterion |
|---|---|---|---|
| 1 | 20–26 Oct | Confirm the MW basis, FU, strategies and AHP hierarchy as a team. Do manual downloads M1–M8 and verify `to-verify` parameters. Literature review (≥ 15 sources). | `assumptions.csv` ≥ 80 % verified; boundary diagram drafted |
| 2 | 27 Oct–2 Nov | `03_demand_model.py` and `04_lca.py`. First results for Q1, Q2, Q3-carbon. | Demand fan chart + GWP/MWh table |
| 3 | 3–9 Nov | `05_lcc.py` (LCOW, NPC, eLCC, frontier). Individual AHP judgements, then combine them; `06_ahp.py`. | LCC table, efficient frontier, AHP ranking with CR < 0.1 |
| 4 | 10–16 Nov | `07_sensitivity.py` (tornado, scenario matrix, break-evens, Monte Carlo), `08_figures.py`. Full first draft of the paper. | All figures generated; draft v1 |
| 5 | 17–23 Nov | Revise, write recommendations, poster, video script and recording. Final consistency check (numbers in text = output tables). | Submission |

**Weekly 30-min check-in:** what moved from `to-verify` to `verified`, blockers, and figure review.

---

## 7. Paper outline (mirrors the systems-modelling process in the Intro lecture §5.2)

1. **Introduction:** AI-driven DC growth; DC-CFA2; the water–energy nexus in Singapore; research questions Q1–Q5.
2. **Background and literature:** DC water use (Mytton; Li et al.; LBNL); Singapore's Four National Taps; NEWater/desal energy; policy (Green DC Roadmap, MWEMP, SS 726, Green Mark DC).
3. **Problem definition and stakeholders:** PUB, IMDA/EDB, operators, EMA, other users, environment. A stakeholder–criteria map that feeds the AHP.
4. **Methodology:** goal, scope, FU, boundary diagram; strategies; scenarios; demand model; LCA; LCC/eLCC; AHP; sensitivity design.
5. **Data and assumptions:** summary table (full register in the appendix); data gaps.
6. **Results:** 6.1 demand (Q1–Q2) · 6.2 LCA hotspots · 6.3 LCC/eLCC and efficient frontier (Q3) · 6.4 AHP rankings across weighting scenarios (Q4) · 6.5 tornado, scenarios, break-evens, Monte Carlo (Q5).
7. **Discussion:** the supply-vs-reduce trade-off; water–energy coupling (A4); price-signal misalignment (social vs operator); limitations (attributional, marginal vs average, reanalysis weather, no site data).
8. **Recommendations:** for PUB (e.g. a WUE benchmark for new DCs and a NEWater-first make-up policy) and for IMDA/EDB (e.g. a WUE criterion in future calls; credit for blowdown recovery). These are illustrative; final ones will come from the results.
9. **Conclusion.** **Appendices:** assumptions register, AHP matrices with CRs, code and data manifest.

**Poster:** one-line question → boundary diagram → demand fan chart → cost-vs-carbon frontier → AHP rainbow → three recommendations.
**Video:** problem (30 s) → approach (60 s) → three key results (90 s) → recommendations (30 s).

---

## 8. Risks

| Risk | Mitigation |
|---|---|
| Key costs unavailable (capex of reuse or liquid cooling) | Use wide ranges + break-even analysis (what capex makes A3 worthwhile?) |
| Result seems "too small to matter" (0.3 %) | Frame around cumulative scenarios, per-MWh intensity and policy precedent (§1.3) |
| AHP judgements look arbitrary | Evidence note per judgement, combine members' matrices, test 5 weighting scenarios + rainbow diagrams |
| Double counting the green share of DC energy | Report GWP with and without the green share; water plants always on the grid EF |
| Scope creep | MODM stays optional; no new methods after week 3 |

## 9. Decisions needed from the team (week 1)
1. MW basis for DC-CFA2 (facility vs IT): currently 0.8 IT share.
2. Keep 4 strategies, or add A5 (policy portfolio)?
3. Residual source for A3/A4 (NEWater base, desal sensitivity): agree?
4. Confirm the **submission deadline, page limit and poster/video specs** from the module brief, then adjust §6.
5. Who has NUS Library access to SS 726 / Scopus papers?

---

### Key references (to expand)
- EDB & IMDA (2026). *Four data centre proposals selected as part of second Data Centre – Call for Application* (fact sheet, 21 Aug).
- Enterprise Singapore & IMDA (2026). *Singapore launches world's first liquid cooling standard for data centres in tropical climates (SS 726:2026)*.
- IMDA (2024). *Green Data Centre Roadmap*.
- PUB (2025). *Sectoral Water Efficiency Benchmark*. PUB (2023). *PUB's decarbonisation strategy*. PUB (2024). *Singapore's NEWater journey*.
- EMA (2025). *Singapore Energy Statistics 2025*.
- Mytton, D. (2021). Data centre water consumption. *npj Clean Water*, 4, 11.
- Li, P., Yang, J., Islam, M. A., & Ren, S. (2023). Making AI less "thirsty". arXiv:2304.03271.
- Shehabi, A., et al. (2024). *2024 United States Data Center Energy Usage Report*. LBNL.
- Saaty, T. L. (1980). *The Analytic Hierarchy Process*. McGraw-Hill.
- Poh, K. L. (2026). DSS5202 lecture notes: LCA, LCC, AHP, MODM.
