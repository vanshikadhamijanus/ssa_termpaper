# Manual downloads

These sources cannot be fetched by `src/01_fetch_data.py`. Download them by hand
and save them here using the file names below. Re-running `01_fetch_data.py` marks
each one as `present` in `data/raw/MANIFEST.csv`.

| # | What | Where | Save as | Why we need it | Owner |
|---|------|-------|---------|----------------|-------|
| M1 | EMA Singapore Energy Statistics 2025: Ch.2 (grid emission factor 2021–24), Ch.3 (electricity consumption by sub-sector, incl. Information & Communications) | https://www.ema.gov.sg/resources/singapore-energy-statistics (JS page, so use each chapter's Download button) | `ema_ses2025_ch2.xlsx`, `ema_ses2025_ch3.xlsx` | Confirm the 2021–22 EF values in `config/grid_ef_ema_2021_2024.csv`; calibrate DC electricity use | LCA lead |
| M2 | EMC USEP monthly averages, 2019–2026 | https://www.emcsg.com/marketdata/priceinformation | `emc_usep_monthly.csv` | Wholesale power price for water plants (LCC `price_elec`) | LCC lead |
| M3 | SS 726:2026 and SS 697:2023 | Singapore Standards eShop, or check NUS Libraries access first | `ss726_2026.pdf` | Water-efficiency clauses for liquid cooling. If you can't get access, cite the ESG media release | Demand lead |
| M4 | LBNL (2024) US Data Center Energy Usage Report | https://eta-publications.lbl.gov/sites/default/files/2024-12/lbnl-2024-united-states-data-center-energy-usage-report.pdf (open in browser) | `lbnl_2024_dc_energy_report.pdf` | WUE by cooling technology | Demand lead |
| M5 | Sustainability reports of the 4 DC-CFA2 awardees (Equinix, Digital Realty, Keppel DC, STT GDC) plus Google, Microsoft, AWS | Company sustainability pages | `operator_<name>_<year>.pdf` | Singapore/APAC WUE, PUE, water withdrawal, use of NEWater | Demand lead |
| M6 | PUB Annual Report (latest); Keppel Infrastructure Trust AR (Keppel Marina East Desalination Plant) | https://www.pub.gov.sg/Resources/Publications ; https://www.kepinfratrust.com/ | `pub_annual_report_<yr>.pdf`, `kit_ar_<yr>.pdf` | Plant capacities, opex, energy; PPP prices | LCC lead |
| M7 | Peer-reviewed LCA/LCC of SWRO and potable/industrial reuse | NUS Libraries / Scopus (see search strings in PROJECT_PLAN §4.4) | `lit_<author>_<year>.pdf` | Non-energy GHG per m³, capex per m³/d | LCA lead |
| M8 | Eco-costs dataset | https://www.ecocostsvalue.com/data/ | `ecocosts_<yr>.xlsx` | Externality monetisation (eLCC), same method as the lecture | LCC lead |
