# The Thirsty Cloud: study design and remaining work

DSS5202 Group 29. Updated 7 November 2026.

This document records the implemented comparison and the work still needed
before submission. The submitted proposal defines the study's scope. The project keeps
its three assessment methods: simplified LCA, LCC and AHP, supported by a demand
model and sensitivity analysis. Reproduction commands are in [README.md](README.md).

## Decision and comparison basis

The study asks how Singapore can meet additional cooling-water demand from new
data centres during **2027–2035**. The functional unit is heat rejection for
1 MWh of IT energy, including the required make-up water.

All alternatives share liquid-cooled IT equipment. This common baseline prevents
the dry-rejection alternative from receiving an energy or capital credit for
liquid cooling that the other alternatives also use.

| ID | Heat rejection and water supply |
|---|---|
| A1 | Conventional wet rejection supplied by desalination |
| A2 | Conventional wet rejection supplied by NEWater |
| A3 | Higher-concentration towers with blowdown recovery, supplied by NEWater |
| A4 | Dry rejection with wet assistance, supplied by NEWater for remaining demand |

The 200 MW DC-CFA2 allocation is treated as IT capacity, following the official
clarification recorded in `config/evidence_register.json`. It is not divided by
PUE. The 500 and 700 MW cases are hypothetical, non-overlapping growth scenarios.
They do not treat the Green Data Centre Roadmap headline as a confirmed addition
to CFA2. Commissioning dates and load ramps are assumptions.

## Implemented methods

| Stage | Calculation and principal outputs |
|---|---|
| Inputs and demand | Hourly weather calculations and a tower mass balance feed annual and cumulative water demand |
| Simplified LCA | Electricity and screening greenhouse-gas emissions per MWh of IT, with component contributions |
| LCC | Water-production costs, operator bills, equipment service costs and discounted 2027–2035 totals |
| AHP | Five illustrative main-weight scenarios with consistency checks and sensitivity to subordinate judgments |
| Uncertainty | Parameter draws, separate preference trials, structural cases and break-even thresholds |

The primary LCA uses full-grid emissions for incremental electricity. A policy
requirement for green electricity does not imply zero emissions. Explicit
low-carbon supply cases use stated non-zero emission factors.

Resource cost and operator cost are reported separately. Main resource cost
excludes carbon monetisation. Carbon-price-equivalent and eco-cost valuations
are supplementary scenarios. Operator water prices include the relevant taxes
before GST, including the corrected NEWater total of S$2.50/m³. The waterborne
tax is not added again as a second operator charge.

Equipment costs begin when capacity is commissioned, even during the load ramp.
The model uses annual capital-service charges over the assumed equipment life.
The remaining service value after 2035 is not represented as an estimated resale
price. Incremental dry-rejection capital excludes common liquid-cooling equipment.

The AHP uses illustrative judgments. No stakeholder survey or independent team
elicitation is claimed. Quantitative scoring floors and related criteria can
affect rankings, so the analysis varies the floors and tests a hierarchy with
less overlap. Consistency ratios assess judgment consistency, not evidence quality.

Parameter uncertainty uses 10,000 draws with seed 29. Preference uncertainty uses
2,000 trials with seed 2901. These trials vary main weights, subordinate judgments
and scoring floors, and evaluate both the full and reduced-overlap hierarchies.
Rank frequencies describe this sampling design. Structural assumptions, including
the residual water source and low-carbon electricity pathway, are tested separately.

## Interpretation of the current results

A2 has the lowest base resource cost. A3 reduces water use and modelled emissions
relative to A2, with a resource-cost premium and a modest operator saving at the
assumed tariff and equipment cost. A3 also ranks first under the balanced AHP
scenario. A4 saves the most site water, but its assumed dry-rejection electricity
penalty raises cost and emissions. The preferred option therefore depends on
measured equipment performance and the decision priorities.

Use `outputs/tables/headline.csv` and the generated report for numerical results.
Changing the inputs can change these conclusions; rerun all deliverable builders
after any model revision.

## Evidence still needed

| Evidence gap | Why it matters | Next useful check |
|---|---|---|
| Dry-rejection electricity and capacity under tropical conditions | Determines A4's main cost and carbon penalty | Obtain equipment curves and a site heat-load assessment |
| Recovery and dry-equipment capital and maintenance costs | Determines financial thresholds | Compare quotations on the same IT-capacity basis |
| Water quality, cycles of concentration and recovery yield | Constrains the achievable A3 water saving | Check treatment requirements and operating records |
| Independent weather and future warming | Historical reanalysis can miss local extremes | Compare station observations and test warmer conditions |
| Water-system inventories and marginal costs | Limits plant-specific LCA and resource-cost claims | Verify boundaries and page-level evidence for treatment inputs |
| Stakeholder priorities | Current AHP judgments are illustrative | Elicit and document preferences if the team can obtain them |

The existing wet-cooling benchmark is a proxy for the new facilities. Historical
weather provides a screening estimate for wet assistance; it does not validate a
dry cooler. The LCA omits upstream wastewater treatment, differential cooling
equipment embodied impacts and water used in electricity generation. Independent
triangular inputs also omit possible correlations between weather, water use and
power demand. These limits remain in the report.

## Validation and submission

`src/validate_project.py` checks saved results against the model and tests the
accounting balances. It also checks AHP consistency and source preservation.
Its reports retain the original source-hash baseline and
any explicitly acknowledged external changes. Source hashes establish byte
preservation, not whether a claim is supported.

The report, poster and video deck use the corrected model outputs. The poster
keeps the official one-page template. On 7 November the report was rebuilt
from `report_final.md` with four additions: a comparison of the
Open-Meteo record with the SingStat station series (the gridded record is
about 1.4 degC cooler, which would lift A4's water use from 0.50 to about 0.74
m3/MWh), a decomposition showing that 85% of A4's water comes from the assumed
20% wet share rather than from hot-hour trim, an AHP scoring-rule test (the
ratio rule turns the operator viewpoint into an A2/A3 tie), and a table that
separates calibration from independent validation. The poster was edited to say
"resource cost" and to show the viewpoint result and the carbon break-even; the
video deck was rebuilt from the report figures (`15_build_video_slides.py`). The supplied DSA5208 report informs the
report's structure and language; it is a style reference, not a source for the
water model.

After the 7 November review the report was revised again: a shorter abstract;
bounded robustness wording with two verified joint boundary cases; the three
separate A4 break-evens (resource cost, operator cost, carbon); the horizon
maintenance allowance of about S$1,200 per commissioned MW-year; separately
costed towers at 8 cycles without recovery (Table 12); the per-year hot-hour
share of the unpinned Open-Meteo record (Table S6b); a feasibility gate before
the recommendations; a source column in Table S1; and the withdrawal-versus-
consumption distinction. The poster's straight-line chart was replaced by a
fresh AHP viewpoint figure and the 20-slide PowerPoint deck replaced the
generated 17-slide deck.

Before the **13 November 2026** deadline in the
[module brief](https://klpoh.github.io/courses/dss5202/termpaper.html):

1. Review the conclusions and unresolved assumptions as a team.
2. Rehearse the 20-slide deck; the notes give the narration and a suggested time per slide (about 9.5 minutes in total).
3. Record the required ten-minute MP4 in the team's own voices over the
   20-slide deck and check sound, legibility and duration.
4. Add the recording to the submission ZIP and verify that the report, code and
   one-page poster are present.

The current package prepares the slides. The team recording remains
outstanding. No additional assessment method is needed to finish the agreed scope.
