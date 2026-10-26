%title The Thirsty Cloud
%subtitle Meeting the water needs of Singapore's data-centre growth
%course DSS5202 Sustainable Systems Analysis | Term Paper | Group 29
%authors Aditya Vijindra Pandhari | A0328872R; Apurwa Kumari | A0333260R; Vanshika Dhamija | A0333989H
%date November 2026

%abstract We compare ways to meet the cooling-water needs of new data-centre capacity in Singapore from 2027 to 2035. The study combines a demand model with simplified Life Cycle Assessment, Life Cycle Costing and Analytic Hierarchy Process. All four alternatives share liquid-cooled IT equipment. They differ in water source, cooling-tower operation and heat rejection. For the 200 MW IT allocation, conventional wet rejection requires {{water_A2}} million m³ annually at the assumed {{util}}% utilisation after the commissioning ramp. Higher-concentration towers with blowdown recovery reduce this to {{water_A3}} million m³; dry rejection with wet assistance reduces it to {{water_A4}} million m³. NEWater with conventional wet rejection has the lowest modelled resource cost. Recovery lowers water use and emissions at an additional resource cost, while dry rejection incurs a substantial electricity penalty in the illustrative base case. We examine these trade-offs through parameter uncertainty, alternative stakeholder judgments and structural scenarios. The results support conditional water-efficiency decisions and identify the measurements needed before selecting equipment.

# 1. Executive summary

This project examines the additional cooling-water requirement associated with Singapore's data-centre growth. The starting case is the 200 MW IT allocation under the second Data Centre Call for Application, DC-CFA2. Two larger cases test total additions of 500 and 700 MW IT. These are hypothetical growth scenarios, rather than confirmed allocations or an assumption that the Green Data Centre Roadmap is additive to CFA2.

The comparison has two parts. First, we estimate how much water different heat-rejection arrangements require. Second, we assess the cost, greenhouse-gas emissions and wider decision factors associated with supplying that water. A common basis of 1 MWh of IT energy allows the supply and demand-reduction options to be compared consistently.

{{table_summary}}

Table 1. Base-case comparison per MWh of IT energy. Costs are steady-operation estimates before GST. Emissions cover the modelled water and additional heat-rejection components, not the whole data centre.

NEWater with wet rejection, A2, is the least expensive option from the resource-cost perspective. High-concentration towers with recovery, A3, reduce make-up water by {{a3_water_saving}}% and modelled emissions by {{a3_carbon_saving}}% relative to A2. Their additional resource cost is S${{a3_social_premium}}/MWh, while the operator saves S${{a3_operator_saving}}/MWh at the assumed equipment cost and current water price. The distinction matters: an operator's bill includes water taxes, whereas resource costing estimates the inputs used to provide the service.

Dry rejection with wet assistance, A4, reduces water demand by {{a4_water_saving}}%. Its additional fan and pump electricity is assumed to be {{dry_kwh}} kWh/MWh. That assumption makes it more costly and more carbon-intensive than A2 in the base case. Its value therefore depends on the importance assigned to water savings and on measured dry-cooler performance. The analysis does not credit A4 with adopting liquid cooling, since that technology is common to the alternatives.

# 2. Problem statement and assessment criteria

The submitted proposal asks how Singapore can meet additional cooling-water demand while accounting for cost, carbon emissions and water security. The decision concerns the new capacity's water supply and heat-rejection arrangements. It is not a choice between building an entire desalination plant and installing cooling equipment at one site: water-supply costs are allocated per cubic metre of output.

{{table_questions}}

Table 2. Research questions and the evidence used to answer them.

PUB is concerned with water-system demand and supply resilience. IMDA and EDB set conditions for data-centre growth. Operators face equipment costs, utility bills and reliability requirements. EMA's interest includes the electricity used by both water treatment and cooling. Other users share the same water infrastructure. The AHP represents these concerns through illustrative weighting scenarios; it does not claim to measure these organisations' preferences.

Water-use effectiveness, WUE, is expressed as m³/MWh of IT energy, numerically equivalent to L/kWh. A lower WUE reduces water drawn at the site, but does not by itself establish lower emissions or cost. Electricity use and water use are therefore reported separately before aggregation through AHP.

# 3. Data sources and assumptions

The source base includes PUB's water benchmarks and tariff announcement (2023b, 2025), the IMDA Green Data Centre Roadmap (2024), EMA electricity statistics (2026), and hourly Open-Meteo weather for Jurong Island (n.d.). Published studies provide context on cooling technologies and water accounting. Mytton (2021) distinguishes site water use from the water associated with electricity generation. Shehabi et al. (2024) describe the variation across US cooling configurations. These studies do not provide site-specific performance measurements for the new Singapore facilities.

The 200 MW allocation is treated as IT capacity. MDDI (2026, paragraph 28) explicitly includes it in Singapore's maximum IT-load capacity. We therefore do not divide the allocation by PUE. Commissioning from 2027 and the subsequent utilisation ramp are modelling assumptions, not verified opening dates. The 500 and 700 MW cases explore higher demand without interpreting the Roadmap's near-term ambition as a separate confirmed tranche (IMDA, 2024).

{{table_parameters}}

Table 3. Inputs that govern the main comparison. Ranges are sensitivity assumptions unless identified as published observations. The full register records units, sources, status and whether each input is active, contextual or used for calibration.

The register contains {{n_parameters}} entries, including {{n_verified}} marked verified, {{n_unverified}} awaiting further verification and {{n_judgment}} identified as team judgments. Other entries are marked as contextual, benchmark-derived, scenarios or proxies. A verified central observation does not validate its future range or its transfer to a new facility. The incremental dry-rejection capital allowance is an illustrative assumption rather than a vendor quotation. The same qualification applies to recovery equipment and non-energy emissions factors.

PUB's April 2025 total NEWater price is S${{newater_tariff}}/m³ before GST, including the water conservation and waterborne taxes. The non-domestic potable price is S${{potable_tariff}}/m³ (PUB, 2023b, Annexes A and B). Those prices enter the operator calculation. A1 uses the potable price as a bill proxy; it is not a dedicated desalinated-water tariff. Neither price is substituted for marginal treatment resource costs in the social comparison.

# 4. Data preparation and verification

The weather file contains {{weather_rows}} hourly records covering 2015–2025. Timestamps and temperatures are checked for missing values, duplicates and expected coverage. For each assumed dry-cooler threshold, we count actual archived hours above that threshold. This avoids interpolating between a few stored temperature cut-offs. The original request did not pin a weather model, so the record is not described as ERA5-only (Open-Meteo, n.d.). Gridded weather represents conditions near the site rather than an on-site sensor, and the resulting share is an exposure estimate, not a verified equipment operating schedule.

The water balance is checked separately from the cost model. At the base settings, the calibrated evaporation term is {{evap}} m³/MWh. Raising cycles of concentration from {{coc_current}} to {{coc_best}} reduces blowdown before recovery to {{blowdown_before}} m³/MWh. Recovering {{recovery}}% returns {{recovered}} m³/MWh and leaves {{discharge}} m³/MWh for discharge. Treatment electricity is charged only to recovered water, rather than all water avoided relative to the conventional tower.

Model checks also cover demand scaling, unit consistency, the timing of equipment charges and the separation of resource costs from tariffs. AHP checks compare priority vectors with an independent eigenvector calculation, verify normalisation and enforce the consistency criterion for judgment matrices. Saved base tables are compared with new calls to the model functions. These checks establish arithmetic consistency; they cannot establish the accuracy of an assumed equipment cost or future operating condition.

# 5. Study boundary and alternatives

The functional unit is heat rejection associated with 1 MWh of IT energy, including the required make-up water. All alternatives share the same IT service and liquid-cooling arrangement, consistent with the CFA2 awardees' adoption of liquid cooling (EDB & IMDA, 2026). The model includes water production, conveyance and recovery energy, water-system non-energy emission proxies, and the additional electricity and capital associated with the selected heat-rejection option.

{{table_alternatives}}

Table 4. Four configurations serving the same IT load. CoC means cycles of concentration; wet trim means additional water-assisted heat rejection during hot conditions.

![Figure 1. Comparison boundary. Common IT and liquid-cooling infrastructure are excluded. The alternatives differ in water supply, tower operation and heat rejection.](fig_system_boundary.png)

The base case uses NEWater for the residual water demand of A3 and A4. A structural scenario replaces that source with desalination. Common IT electricity, building construction and the common liquid-cooling equipment are excluded. Upstream wastewater collection and secondary treatment are also excluded under an effluent cut-off for NEWater. No reliable inventory was established for the differential cooling equipment's embodied impacts or end of life, so these are omitted rather than assigned a negligible percentage.

Consequently, the emissions results are a simplified screening assessment of the stated components. They are not full-facility carbon footprints, a complete multi-impact LCA, or a claim of ISO conformity. Brine and blowdown volumes are reported as physical proxies; equal volumes do not imply equal ecological effects.

# 6. Cooling-water demand model

Annual IT energy is calculated for each capacity tranche as allocated IT capacity × utilisation × commissioning ramp × 8,760 hours. Annual water demand is IT energy multiplied by WUE. The base utilisation is {{util}}%, and each tranche reaches its assumed operating level over {{ramp_years}} years. The results for 2035 refer to the completed ramp at that utilisation, not to 100% equipment loading.

For wet rejection, the evaporation estimate is 3.6 divided by latent heat, multiplied by heat rejected per unit of IT energy and the evaporative fraction. Blowdown adds the factor CoC/(CoC−1). We scale this curve to the PUB (2025) benchmark of {{wue_base}} m³/MWh. This is calibration to a published fleet benchmark, not independent validation of the new sites. The higher-CoC configuration then applies the recovery fraction to its remaining blowdown.

For A4, the dry loop handles {{liquid_share}}% of the heat. The remainder uses wet rejection. The model applies tower-equivalent water use to the dry-loop share only when ambient temperature exceeds {{trim_threshold}}°C. This occurs in {{trim_percent}}% of the archived hours. The approximation does not model heat-exchanger size, fan curves or humidity-dependent adiabatic effectiveness.

{{table_demand}}

Table 5. Modelled annual make-up water in 2035, million m³. S2 and S3 are hypothetical total-capacity cases. All use the same utilisation and cooling assumptions.

![Figure 2. Annual cooling-water demand through the assumed commissioning ramps. A1 and A2 have the same site demand and differ only in the source supplying it.](fig_demand_fan.png)

The S1 conventional-wet case uses approximately {{national_share}}% of the {{national_water}} million m³ of potable water and NEWater sold nationally in {{national_year}} (Department of Statistics Singapore, 2026). This is a scale comparison, not a statement that all water sales are cooling water. A3 avoids {{a3_water_avoided}} million m³/year in S1 and A4 avoids {{a4_water_avoided}} million m³/year. Capacity changes scale these volumes; they do not demonstrate that the alternatives have the same performance at every site.

# 7. Assessment methods

## 7.1 Simplified life cycle assessment

For each functional unit, production electricity is make-up water multiplied by the water source's specific energy. Conveyance and recovery electricity are added separately. Additional dry-rejection electricity equals the difference in PUE multiplied by 1,000. The desalination energy reference of 3.5 kWh/m³ comes from PUB (2023a); its lower technology target is not treated as an achieved plant value. NEWater energy remains an assumption requiring stronger plant-specific evidence.

Annual calculations use a grid path starting at the rounded 2025 factor of 0.404 kg CO₂/kWh (EMA, 2026, Table 2.3), with an assumed 2035 endpoint. Per-MWh comparison tables use the unweighted 2027–2035 mean, {{base_grid_factor}} kg CO₂/kWh in the base case. Water-system non-energy proxies are then added. The results combine operational CO₂ factors with assumed CO₂-equivalent inventory terms; they do not implement a separate gas-by-gas IPCC characterisation model.

The primary comparison uses the full grid factor. A 50% green-energy commitment is not interpreted as zero emissions for half the supply. The official pathways include low-carbon fuels (METI, 2026), whose lifecycle intensities require separate evidence. Structural scenarios therefore use explicitly stated, non-zero alternative factors for the DC electricity share. Water production remains on grid electricity in those cases.

## 7.2 Life cycle costing

Water-production cost consists of annualised plant capital, non-energy operating cost and electricity. Capital recovery factors use the stated asset life and discount rate. The social perspective uses a resource-price proxy for electricity and excludes water taxes. The operator perspective uses the water bill and the operator electricity-price assumption. All monetary estimates are expressed on a constant-price modelling basis before GST; historical capital and concession figures have not been converted into verified 2026 procurement quotes.

The per-MWh cost table describes mature utilisation. Horizon net present cost is calculated separately. Once a tranche is commissioned, its incremental cooling equipment incurs a fixed annual capital-service charge, including during the load ramp. Only variable costs scale with energy output. Annualising across the equipment's full assumed life allocates a service charge to the study horizon without charging the entire purchase price to nine years of operation. The resulting horizon levelised cost can therefore differ from the mature-utilisation estimate.

No incremental resource cost for discharged blowdown is included in the primary case because a plant-specific value was not established. Separate cases apply S$0.30 and S$1.09/m³. Neither value is presented as a measured treatment cost. The cooling-equipment calculation includes capital and electricity, but omits incremental non-energy maintenance costs because these were not established.

Carbon-price-equivalent and eco-cost additions are reported separately. The carbon scenario uses the announced S$45/t for 2026–2027 and a selected S$65/t midpoint of the published S$50–80 range for 2030 (NCCS, 2026). The eco-cost valuation uses the retained workbook's EUR0.15/kg carbon-dioxide factor, with assumed sensitivity bounds and currency conversion (Sustainability Impact Metrics, 2026). These valuations are not additional tax bills, and electricity prices may already include carbon-tax pass-through. Neither valuation enters primary resource cost or AHP.

## 7.3 Analytic hierarchy process

The hierarchy combines economic, environmental, water-security and implementation criteria. Its two economic leaves use resource cost before carbon valuation and operator cost. The economic criterion therefore does not add an explicit carbon value before emissions are scored separately. Quantitative leaves use distance from the worst result plus a small positive floor. This is a chosen value function, not an elicited preference. Judgment matrices use reciprocal comparisons and require a consistency ratio no greater than 0.10 (Saaty, 1980).

![Figure 3. AHP hierarchy. Quantitative inputs are distinguished from judgments. Main weights describe illustrative perspectives rather than surveyed stakeholder preferences.](fig_ahp_hierarchy.png)

The five main-weight scenarios are supplemented by subcriterion sweeps, alternative scoring floors and perturbed judgments. A reduced-overlap hierarchy removes electricity and discharge-volume proxies, along with qualitative leaves that partly repeat water demand, while preserving cost, emissions, water volume, maturity and policy alignment. This tests whether the ranking depends on counting related concerns more than once. A low consistency ratio describes internal agreement among judgments, not their empirical validity.

## 7.4 Sensitivity and uncertainty

The parameter simulation uses {{n_mc}} draws with seed {{mc_seed}}. It independently samples {{n_mc_inputs}} active uncertain inputs from triangular distributions while using the same draw for all alternatives. Capacity is kept fixed within each named scenario. Both annual-demand and horizon-demand intervals are calculated. They describe the specified assumptions rather than statistical confidence intervals for future Singapore demand.

A separate set of {{n_pref}} preference trials uses seed {{pref_seed}}. Main weights follow Dirichlet(1, 1, 1, 1), uniform over the four-weight simplex. Subcriterion and qualitative pairwise ratios receive lognormal multiplicative perturbations with log standard deviation 0.35; the resulting ratios are clipped to the interval from 1/9 to 9. Matrices above the consistency threshold are redrawn. Scoring floors of 0.01, 0.10 and 0.30 receive equal sampling probability. Each accepted preference set is evaluated with base inputs and with sampled model inputs, for the full and reduced-overlap hierarchies. These are prescribed stress tests, not estimates of stakeholder belief distributions.

# 8. Results

## 8.1 Water use and greenhouse-gas emissions

A3 reduces WUE from {{wue_base}} to {{wue_A3}} m³/MWh through reduced blowdown and recovery. Its modelled emissions fall from {{gwp_A2}} to {{gwp_A3}} kg CO₂e/MWh relative to A2. A4 achieves the lowest site water use, {{wue_A4}} m³/MWh, but its assumed additional {{dry_kwh}} kWh/MWh of electricity raises emissions to {{gwp_A4}} kg CO₂e/MWh. The water-production saving is too small to offset that penalty in the base case.

![Figure 4. Emissions by modelled component. Additional dry-rejection electricity is shown separately from water-production and non-energy contributions.](fig_lca_hotspots.png)

The results do not imply that dry rejection always increases emissions. They identify the performance needed for it to avoid doing so. Against A2, the incremental dry-rejection PUE must be approximately {{ghg_threshold}} or lower for equal modelled emissions at the base grid factor and water assumptions. This threshold is an absolute PUE difference, not a percentage saving in total data-centre energy.

## 8.2 Resource costs and operator costs

The calculated levelised production costs are S${{lcow_desal}}/m³ for desalination and S${{lcow_newater}}/m³ for NEWater. The second Changi NEWater concession was awarded at a first-year price of S$0.276/m³ (PUB, 2014). That historical price provides context, but differences in award year, financing and contractual scope prevent it from validating current marginal costs. A3 costs more than A2 from the resource perspective because annual equipment charges exceed the modelled resource value of its water saving. At the operator's water price, the avoided bill is larger and A3 has a modest base-case saving.

{{table_npc}}

Table 6. S1 discounted cost for 2027–2035, S$ million. Fixed equipment charges start when capacity is commissioned. Common IT and liquid-cooling costs are excluded.

![Figure 5. Efficient alternatives depend on the objectives considered. The cost–emissions comparison differs from the cost–water comparison.](fig_frontier.png)

For A3, the operator breaks even against A2 at a NEWater price of S${{reuse_tariff_threshold}}/m³, holding other inputs fixed. This is below the current assumed price of S${{newater_tariff}}/m³, but it does not guarantee payback at a particular site. Recovery capital, maintenance requirements and achievable water quality still need confirmation.

## 8.3 AHP rankings

{{ahp_interpretation}}

{{table_ahp}}

Table 7. AHP priorities under five illustrative main-weight scenarios. These values combine the numerical model with the stated qualitative judgments.

The maximum consistency ratio among the base judgment matrices is {{max_cr}}. Quantitative score transformations have no elicited pairwise matrix, so no consistency ratio is used to validate them. Matrix entries, local priorities and evidence notes are supplied with the model outputs.

## 8.4 Parameter and preference sensitivity

{{table_uncertainty}}

Table 8. Frequency of first place in the specified AHP simulations. Parameter-only frequencies keep the base judgments fixed. Combined trials vary both inputs and preferences. Percentages are conditional on the stated sampling design.

{{uncertainty_interpretation}}

{{table_parameter_intervals}}

Table 9. Fifth–95th percentile ranges from {{n_mc}} parameter draws. Water demand uses the fixed 200 MW IT scenario; resource cost is per MWh at mature utilisation. These are conditional simulation ranges, not confidence intervals, and comparisons use paired draws rather than overlap between marginal ranges.

![Figure 6. Dry-rejection thresholds as incremental equipment cost changes. The base PUE penalty is compared with the conditions for equal cost or emissions. Negative cost thresholds require an electricity saving rather than a penalty.](fig_cooling_thresholds.png)

The structural cases replace residual NEWater with desalination, change the unmeasured discharge-cost allowance and assign explicit non-zero intensities to low-carbon DC electricity. These cases are kept separate from the Monte Carlo probabilities. The results also report carbon-price-equivalent and eco-cost valuations separately from the primary resource comparison.

# 9. Interpretation and recommendations

For PUB, the model supports distinguishing water saved from money saved. Recovery can reduce the national supply requirement even where it raises the modelled resource cost. A general subsidy claim would require evidence for the value of that reduced demand, including avoided infrastructure or treatment costs. The present calculation does not establish that value. The water-use benchmark can instead be used to screen proposals, followed by checks of site performance and water quality.

For IMDA and EDB, bidders' heat-rejection designs should be assessed alongside their liquid-cooling commitments. Two sites with liquid-cooled IT can have very different water demand depending on whether they reject heat through towers or dry equipment. Reporting annual PUE and WUE together would make this trade-off visible. The model's energy threshold can help specify the performance evidence required; it is not a design standard.

For operators, the base case gives a reason to examine blowdown recovery, but the estimated saving should be tested against quotations, maintenance and measured recovery rates. Dry rejection offers a larger water reduction. Its selection requires either much lower incremental electricity use than the base assumption, a sufficiently high value placed on water savings, or another operational benefit outside this model.

NEWater is the lower-cost and lower-emissions supply option under the modelled treatment assumptions. Desalination retains a diversification role because it does not depend on used-water feedstock. A cost-and-carbon result alone therefore does not establish that desalination is inferior on every sustainability criterion.

# 10. Limitations and further work

Several limitations affect the strength of the conclusions. The wet-rejection benchmark describes an existing fleet and is transferred to new liquid-cooled facilities as a proxy. Neither the dry-rejection energy penalty nor its capital premium is calibrated to a quotation for the CFA2 sites. Directly measured annual performance and engineering load calculations would be needed before selecting equipment.

The boundary omits upstream wastewater treatment, differential cooling-equipment embodied impacts and off-site water consumed in electricity generation. Different water sources also produce discharges with different salinity and chemistry, which a volume proxy cannot capture. These omissions limit the LCA claim to screening the specified components.

The operating-year schedule is assumed. Actual commissioning dates and phased equipment installation would change cumulative demand and discounted cost. The model uses constant real price assumptions and does not forecast contractual electricity tariffs, equipment replacements or future water-price revisions. Historical weather has not been cross-checked against an independent station record or adjusted for future warming. The independent triangular distributions omit potential dependence between hot weather, energy penalties, utilisation and water use.

Finally, the AHP judgments are illustrative. Preference stress tests reveal sensitivity to the imposed distributions, but cannot replace stakeholder elicitation. Further work should prioritise site measurements and equipment quotations, then revisit the model and decision weights. Adding more assessment methods would not resolve these evidence gaps.

# 11. Conclusion

The project estimates cooling-water demand and compares four ways of meeting it within a common liquid-cooling baseline. For 200 MW IT, the base annual demand is {{water_A2}} million m³ with conventional wet rejection, {{water_A3}} million m³ with higher-concentration towers and recovery, and {{water_A4}} million m³ with dry rejection and wet assistance. These estimates retain the assumed utilisation and weather conditions.

The alternatives involve different trade-offs. NEWater with wet rejection has the lowest modelled resource cost. Recovery reduces water demand and emissions, and can save the operator money under the stated tariff and capital assumptions. Dry rejection saves the most site water but requires evidence that its electricity penalty is acceptable. The practical contribution is the set of quantities and thresholds needed to assess those choices, together with a record of where the evidence remains incomplete.

Generative AI assistance: ChatGPT assisted with model development, code checks and drafting and editing this report. Numerical results were produced by the submitted Python calculations. Assumptions, source limitations and the scope of the checks are stated in the report and supporting files.

## Reproducibility

The analysis reads config/assumptions.csv and retained source data, then produces demand, LCA, LCC, AHP and sensitivity outputs. All deliverables read those tables. The report template is paper/report_template.md; src/09_build_paper.py inserts current results. Reproduction commands and the team recording task are in README.md. Source hashes and numerical checks are in outputs/validation/.

# References

{{references}}

# Appendix A. Active model inputs

{{table_active_assumptions}}

Table A1. Active numerical assumptions. Context and calibration-only entries remain in config/assumptions.csv but are excluded from parameter uncertainty unless they affect the reported metric.

# Appendix B. AHP audit trail

{{table_ahp_weights}}

Table B1. Global subcriterion weights in the balanced base case. Alternative scoring and reduced-overlap cases are reported separately.

{{table_ahp_notes}}

Table B2. Basis and limitations of qualitative comparisons. Pairwise entries and consistency ratios are supplied in outputs/tables/ahp_pairwise_matrices.csv and ahp_consistency.csv.

