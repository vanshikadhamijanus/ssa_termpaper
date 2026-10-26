"""
Source registry for 'The Thirsty Cloud' (DSS5202 Group 29).

Every external data source used in the project is listed here once, so the
downloader, the manifest and the report's reference list all agree.

Kinds
-----
datagovsg : table from data.gov.sg (fetched through the datastore API)
openmeteo : hourly reanalysis weather from the Open-Meteo archive API
csv       : plain CSV over HTTPS
document  : PDF / HTML snapshot kept for citation and number extraction
manual    : cannot be scripted (paywalled, JS-rendered, login, or URL changes
            every year). Download by hand into data/manual/<filename>.
"""

# --------------------------------------------------------------------------
# Study location: the DC-CFA2 awardees will be sited on Jurong Island
# (EDB fact sheet, 21 Aug 2026), so weather is pulled for Jurong Island.
# --------------------------------------------------------------------------
SITE = {"name": "Jurong Island", "lat": 1.2650, "lon": 103.6990}
WEATHER_YEARS = range(2015, 2026)  # 11 full years of hourly data

DATAGOVSG = [
    # id, filename, title, used for
    ("d_3de362b580b2dd2fd50cc1006d4edd4f", "ema_grid_emission_factor.csv",
     "EMA - Electricity Grid Emission Factors (2005-2020)", "LCA: grid EF history"),
    ("d_9db4902c7a47357441dac7d2806032a5", "singstat_water_sales_annual.csv",
     "SingStat - Water Sales, Annual (potable, domestic, non-domestic, NEWater)", "Demand context: DC water as % of national sales"),
    ("d_2eceeb792a0fca1caa74304d47b46060", "pub_newater_sold_annual.csv",
     "PUB - Volume of NEWater sold, Annual", "Supply context: NEWater growth"),
    ("d_cb1d25dd5cfde21bb9fa704af0e3a962", "pub_potable_water_sold_annual.csv",
     "PUB - Volume of Potable Water sold, Annual", "Supply context"),
    # NB: data.gov.sg "Potable Water Tariff" (d_115300b30ad253b0b38b5ecf24ef901f)
    # currently serves potable *sales* volumes, not tariffs, so it is not used.
    # Potable price comes from the PUB 2023 price-increase release instead.
    ("d_50830e6a799ccfd00b1ed0a5294920d7", "pub_newater_tariff.csv",
     "PUB - NEWater Tariff (to 2021)", "LCC: NEWater price"),
    ("d_bab2ba9ae53292abd526f4476bfa4de5", "pub_industrial_water_tariff.csv",
     "PUB - Industrial Water Tariff (to 2021)", "LCC: alternative make-up water"),
    ("d_61eac3cdb086814af485dcc682b75ae9", "singstat_electricity_tariff_monthly.csv",
     "SingStat - Electricity Tariff, Monthly", "LCC: electricity price"),
    ("d_d610f8ed1864daa6c7e790318bbc3323", "singstat_electricity_tariff_annual.csv",
     "SingStat - Electricity Tariff, Annual", "LCC: electricity price"),
    ("d_3745e3aa98ff3c4bcfcb8e1f6dffef42", "singstat_electricity_gen_consumption.csv",
     "SingStat - Electricity Generation and Consumption, Annual", "Context: DC share of electricity"),
    ("d_1b8dcef6bf32ece26deca60e59d99f71", "singstat_ghg_by_sector.csv",
     "SingStat - Greenhouse Gas Emissions by Sector, Annual", "Context: national GHG"),
    ("d_1744ca68dc7ed37221b17c441042405e", "singstat_climate_monthly.csv",
     "SingStat - Air Temperature, Sunshine, Relative Humidity and Rainfall, Monthly", "Cross-check of Open-Meteo weather"),
    ("d_70d247965470ea125814eee0171c1dd1", "singstat_final_energy_by_sector.csv",
     "SingStat - Total Final Energy Consumption by Energy Type and Sector", "Context"),
]

CSV = [
    ("https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv",
     "owid_energy_data.csv",
     "Our World in Data - energy dataset (Ember/EI based)", "LCA: Singapore carbon intensity & fuel mix trend"),
]

DOCUMENTS = [
    ("https://www.edb.gov.sg/content/dam/edb-en/about-edb/media-releases/news/four-data-centre-proposals-selected-as-part-of-second-data-centre/Fact%20Sheet%20-Four%20data%20centre%20proposals%20selected%20as%20part%20of%20second%20data%20centre.pdf",
     "edb_imda_2026_dc_cfa2_factsheet.pdf",
     "EDB & IMDA (2026) Four DC proposals selected under DC-CFA2", "Demand: 4 x 50 MW, Jurong Island, liquid cooling"),
    ("https://www.imda.gov.sg/-/media/imda/files/how-we-can-help/green-dc-roadmap/green-dc-roadmap.pdf",
     "imda_2024_green_dc_roadmap.pdf",
     "IMDA (2024) Green Data Centre Roadmap", "Demand: median WUE 2.2 (2021), target <=2.0; cooling towers ~97% of DC water"),
    ("https://www.enterprisesg.gov.sg/-/media/esg/files/media-centre/media-releases/2026/august/mr03826_singapore-launches-worlds-first-liquid-cooling-standard-for-data-centres-in-tropical-climates.pdf",
     "esg_imda_2026_ss726_media_release.pdf",
     "Enterprise SG & IMDA (2026) SS 726:2026 liquid cooling standard", "Demand-side option: liquid cooling (>30% DC energy saving)"),
    ("https://www.nature.com/articles/s41545-021-00101-w.pdf",
     "mytton_2021_dc_water_consumption.pdf",
     "Mytton (2021) Data centre water consumption, npj Clean Water 4:11", "WUE ranges, direct vs indirect water"),
    ("https://arxiv.org/pdf/2304.03271",
     "li_et_al_2023_making_ai_less_thirsty.pdf",
     "Li, Yang, Islam & Ren (2023) Making AI less thirsty", "WUE on-site vs off-site; weather dependence"),
    ("https://www.pub.gov.sg/Public/WaterLoop/Water-Conservation/Resources-on-Water-Efficiency-Measures/Sectoral-Water-Efficiency-Benchmark",
     "pub_sectoral_water_efficiency_benchmark.html",
     "PUB (2025) Sectoral Water Efficiency Benchmark", "Demand: DC median WEI = 2.1 m3/MWh"),
    ("https://www.pub.gov.sg/Resources/News-Room/PressReleases/2023/03/PUB-decarbonisation-strategy",
     "pub_2023_decarbonisation_strategy.html",
     "PUB (2023) PUB's decarbonisation strategy", "Supply: desal 3.5 -> <2 kWh/m3 target; demand doubles by 2065"),
    ("https://www.pub.gov.sg/Resources/News-Room/PressReleases/2024/09/Singapore-NEWater-journey",
     "pub_2024_newater_journey.html",
     "PUB (2024) Singapore's NEWater journey", "Supply: Tuas NEWater 75 mgd; biomimetic -20% energy"),
    ("https://www.pub.gov.sg/Resources/News-Room/PressReleases/2023/09/Water-price-to-rise-from-April-2024-Government-to-provide-support",
     "pub_2023_water_price_increase.html",
     "PUB (2023) Water price to rise from April 2024", "LCC: potable +S$0.50/m3, NEWater +S$0.17/m3 (2024-25)"),
    ("https://www.nccs.gov.sg/singapores-climate-action/mitigation-efforts/carbontax",
     "nccs_carbon_tax.html",
     "NCCS - Carbon Tax", "eLCC: S$25 (2024-25), S$45 (2026-27), S$50-80 (2030)"),
    ("https://www.edb.gov.sg/en/news-and-insights/four-data-centre-proposals-selected-as-part-of-second-data-centre",
     "edb_2026_dc_cfa2_news.html",
     "EDB (2026) DC-CFA2 news page", "Demand"),
    ("https://www.spgroup.com.sg/our-services/utilities/tariff-information",
     "spgroup_tariff_information.html",
     "SP Group - Tariff information", "LCC: current electricity tariff"),
]

# Things a script cannot fetch reliably. Put the file in data/manual/ with the
# given name; 02_build_inputs.py reads it if present and otherwise falls back
# to the values in config/assumptions.csv.
MANUAL = [
    ("EMA Singapore Energy Statistics 2025 - Chapter 2 (grid emission factor 2021-2024) and Chapter 3/4 (electricity consumption by sub-sector incl. Information & Communications)",
     "https://www.ema.gov.sg/resources/singapore-energy-statistics",
     "ema_ses202*_*.xlsx", "Page is JavaScript-rendered; use the 'Download' buttons per chapter."),
    ("EMC - Uniform Singapore Energy Price (USEP) half-hourly/monthly",
     "https://www.emcsg.com/marketdata/priceinformation",
     "emc_usep_*.csv", "Wholesale electricity price for water plants (contestable consumers)."),
    ("SS 726:2026 Liquid Cooling in Tropical Data Centres; SS 697:2023 Tropical Data Centre",
     "https://www.singaporestandardseshop.sg/Product/SSPdtDetail/2b7aa78a-36c9-4656-abc5-eb4dc1a6e431",
     "ss726*.pdf", "Paid standard; check NUS Libraries (Singapore Standards via library e-resources) or cite the media release only."),
    ("LBNL (2024) United States Data Center Energy Usage Report (Shehabi et al.)",
     "https://eta-publications.lbl.gov/sites/default/files/2024-12/lbnl-2024-united-states-data-center-energy-usage-report.pdf",
     "lbnl_2024_dc_energy_report.pdf", "Server blocks scripted download (HTTP 202); open in browser. WUE by cooling type."),
    ("Operator sustainability reports: Equinix, Digital Realty, Keppel DC (Keppel Ltd / Keppel DC REIT), ST Telemedia GDC (the four DC-CFA2 awardees) + Google, Microsoft, AWS",
     "https://sustainability.equinix.com/ ; https://www.digitalrealty.com/about/sustainability ; https://www.keppeldcreit.com/sustainability ; https://www.sttelemediagdc.com/sustainability ; https://sustainability.google/reports/",
     "operator_*.pdf", "Extract site/region WUE, PUE, water withdrawal for Singapore/APAC. URLs change yearly."),
    ("PUB Annual Report (latest) and Keppel Infrastructure Trust annual report (Keppel Marina East Desalination Plant)",
     "https://www.pub.gov.sg/Resources/Publications ; https://www.kepinfratrust.com/",
     "pub_annual_report_*.pdf", "Desal/NEWater capacity, opex, plant energy."),
    ("Peer-reviewed LCA/LCC of SWRO desalination and water reuse (via NUS Libraries / Scopus)",
     "https://libportal.nus.edu.sg/",
     "lit_*.pdf", "Embodied + chemical GHG per m3; capex per m3/d. See plan section 4.4 for search strings."),
    ("Eco-costs (TU Delft / Sustainability Impact Metrics) – supplementary valuation factors",
     "https://www.ecocostsvalue.com/data/",
     "ecocosts_*.xlsx", "Retained workbook carbon dioxide factor: EUR0.15/kg; supplementary valuation, not an extra cash tax."),
]
