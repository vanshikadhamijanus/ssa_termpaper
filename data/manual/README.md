# Manually collected sources

These files were obtained separately from the automated downloads. Keep their
original bytes. Record derived values in `config/assumptions.csv` or a processed
table, with the source location and units.

The inventory below reflects files present on 25 October 2026. Presence does not
mean every parameter attributed to a report has been verified. The assumption
register and `config/evidence_register.json` distinguish verified claims from
proxies, team judgments and unresolved inputs.

| Files | Source and use | Evidence limit |
|---|---|---|
| `ema_ses2026_all_chapters.xlsx` | [EMA Singapore Energy Statistics](https://www.ema.gov.sg/resources/singapore-energy-statistics), including grid-emission factors | Published history does not establish the 2035 grid trajectory |
| `emc_usep_monthly.csv`, `emc_usep_monthly_ema_2005_2026.pdf` | EMA's [monthly USEP series](https://www.ema.gov.sg/content/dam/corporate/resources/statistics/files/pdf/Average%20Monthly%20USEP%20(as%20of%20Aug%2026).pdf.coredownload.pdf), used to inform the electricity-price proxy | Wholesale prices are not a complete social cost of electricity |
| `lbnl_2024_dc_energy_report.pdf` | Shehabi et al., [2024 US Data Center Energy Usage Report](https://eta-publications.lbl.gov/sites/default/files/2024-12/lbnl-2024-united-states-data-center-energy-usage-report.pdf) | US cooling configurations provide context, not validated Singapore dry-cooler performance |
| `operator_equinix_2024.pdf`, `operator_digitalrealty_2024.pdf`, `operator_keppeldc_2024.pdf`, `operator_sttgdc_2024.pdf` | Operator sustainability disclosures | Group or regional metrics are not measurements for the planned facilities |
| `pub_annual_report_2026.pdf` | PUB's [Annual and Sustainability Report 2025/26](https://www.pub.gov.sg/-/media/PUB/Publications/Report/PDF/PUBASR-202526-PDFA.pdf) | System context does not establish a marginal treatment cost |
| `kit_ar_2024.pdf` | Keppel Infrastructure Trust annual report | Historical contract and asset information is not a current equipment quotation |
| `lit_santos_2026.pdf` | Water-reuse LCA review | Review findings need boundary checks before transfer to the model |
| `ecocosts_2026.xlsx` | [Eco-costs data](https://www.ecocostsvalue.com/data/) | The separate valuation scenario uses the retained workbook's EUR0.15/kg CO₂ factor and an assumed currency conversion; it is not an actual extra cash tax |

The full SS 726:2026 standard is absent. The public Enterprise Singapore/IMDA
media release in `data/raw/docs/` supports policy context. It cannot substitute
for the standard's technical requirements or a site performance assessment.
The general liquid-cooling energy claim is not credited exclusively to A4,
because every strategy shares the liquid-cooled IT baseline.

## Inventory and checks

`src/sources.py` records source URLs and filename patterns. Running
`python src/01_fetch_data.py` from the project root keeps existing downloads and
refreshes `data/raw/MANIFEST.csv`, including manual files. It also reports files
that lack a registry mapping. This step may fetch missing public sources and is
not needed for the normal offline numerical run. It changes the manifest's
metadata, which produces a difference against its protected hash. Record and
review that update while retaining the original baseline.

`python src/validate_project.py` writes a fuller source inventory to
`outputs/validation/source_inventory.csv` and checks protected hashes. Keep the
original baseline when investigating a mismatch. The source inventory identifies
unmapped URLs rather than assigning unverified provenance.

## Further evidence work

Prioritise plant-specific non-energy inventories and current treatment costs,
then obtain quotations and operating evidence for tower recovery and dry heat
rejection. A paper or report should only change an input's status to verified
when its scope, units and stated value support that input. Record page or table
references where available. Do not treat additional downloads as validation by
themselves.
