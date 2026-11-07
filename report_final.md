%title The Thirsty Cloud
%subtitle Meeting the water needs of Singapore's data-centre growth
%course DSS5202 Sustainable Systems Analysis | Term Paper | Group 29
%authors Aditya Vijindra Pandhari | A0328872R; Apurwa Kumari | A0333260R; Vanshika Dhamija | A0333989H
%date November 2026

%abstract Singapore's new data centres need cooling water. For 200 MW of new IT load over 2027 to 2035 we compare four options on one basis, 1 MWh of IT energy: wet towers fed by desalinated water (A1) or NEWater (A2), high-cycle towers that recover their blowdown (A3), and dry cooling with a small wet share (A4). A demand model feeds a simplified life cycle assessment, a life cycle costing from society's and the operator's viewpoints, and an AHP under five illustrative weightings, followed by sensitivity tests. A2 has the lowest resource cost, S${{cost_A2}} per MWh. A3 cuts water by {{a3_water_saving_r}}% and emissions by {{a3_carbon_saving_r}}% and lowers the operator's bill, at a small extra cost to society. A4 cuts water by {{a4_water_saving_r}}% but its assumed fan electricity makes it the most expensive and most carbon-intensive option; it matches A2 on carbon only if its extra PUE falls below about {{ghg_threshold}}. A3 ranks first in four of five viewpoints under a linear scoring rule and ties with A2 in one under a ratio rule. The A4 result rests on two unmeasured inputs, the extra PUE and the 80/20 heat split. The report states the thresholds that would change each conclusion and the evidence needed to settle them.

# 1. Introduction

Data centres reject their heat to the air, and many do it by evaporating water in cooling towers. In Singapore, where water is imported or made at a high energy cost, that water use is a policy concern. The second Data Centre Call for Application (DC-CFA2) provisionally allocated 200 MW of new IT capacity to four proposals (Economic Development Board & Infocomm Media Development Authority [EDB & IMDA], 2026). The Government has since put the country's planned maximum IT load at 1.6 GW, which includes this allocation (Ministry of Digital Development and Information [MDDI], 2026).

The decision we study is how the extra cooling water should be supplied at system level and how much of it each site should need. It is not a choice between building a desalination plant and installing cooling equipment at one site. We allocate water-supply costs per cubic metre of output, so an option that supplies more water and an option that needs less water can be compared on the same basis.

This report asks one practical question: **how can Singapore meet the cooling-water needs of new data centres at reasonable cost, with low carbon, and without straining the water system?** We compare four options on a common basis of 1 MWh of IT energy, then test how far the answer depends on our assumptions.

The four options are shown in Figure 1. All four share the same liquid-cooled IT equipment. They differ only in the water source and in how heat is rejected.

![Figure 1. The four options. Each row shows the water source, the heat-rejection method and the resulting water use per MWh of IT energy.](fig_report_options.png)

Table 1 explains the terms used in the rest of the report. Table 2 maps the five questions in our proposal to the method that answers each one.

Table 1. Terms used in this report.

| Term | Meaning |
| --- | --- |
| IT energy | Electricity used by the computing equipment itself. Our unit of comparison is 1 MWh of it. |
| WUE | Water-use effectiveness: cubic metres of water used per MWh of IT energy (the same number as litres per kWh). |
| PUE | Power-use effectiveness: total facility energy divided by IT energy. We use the *extra* PUE that dry cooling adds. |
| NEWater | High-grade reclaimed water made from treated used water. |
| Cycles of concentration (CoC) | The ratio of dissolved solids in the circulating tower water to those in the make-up water. A higher number means less water is drained as blowdown. |
| Blowdown | The salty water drained from a cooling tower to keep it clean. |
| Wet trim | Water-assisted cooling used on hot hours by the dry loop in A4. |

Table 2. Research questions from the proposal and the evidence used to answer them.

{{table_questions}}

Five groups have a stake in the answer. PUB manages water supply and demand and sets the efficiency benchmarks. IMDA and EDB set the conditions attached to data-centre growth. Operators pay for equipment, water and electricity and must meet reliability requirements. The Energy Market Authority (EMA) has an interest because water treatment and cooling both draw on the grid. Households and other industries share the same water system. The AHP in Section 7 represents these concerns through five illustrative weightings. It does not measure any organisation's actual preferences.

The report follows the method in Figure 2. Section 2 sets the scope and Section 3 the data. Section 4 estimates demand. Sections 5 and 6 cover carbon and cost. Section 7 ranks the options with the Analytic Hierarchy Process (AHP). Section 8 tests the results. Sections 9 to 11 draw out the findings. Detailed tables, equations and checks are in the supplementary section after the references.

![Figure 2. Method overview. Demand feeds both the carbon and cost assessments. The AHP combines them with other criteria, and the sensitivity tests check the inputs and the weights.](fig_report_method.png)

# 2. Scope and system boundary

**What we compare.** The functional unit is the heat rejection that goes with **1 MWh of IT energy**, including the make-up water it needs. The study period is 2027 to 2035. The base case is the 200 MW allocation (scenario S1). Two larger cases, 500 MW (S2) and 700 MW (S3), are hypothetical growth scenarios, not confirmed allocations.

**What is inside the boundary.** Figure 3 follows the convention of ISO 14040 (International Organization for Standardization [ISO], 2006a). Everything inside the dashed line is counted. Arrows outside the line are flows to and from the environment.

![Figure 3. System boundary for 1 MWh of IT energy. Solid arrows are flows inside the system. Dashed boxes are outside it.](fig_report_boundary.png)

Inside the boundary are water production, conveyance to Jurong Island, heat rejection, blowdown recovery (A3 only), the extra fan electricity for dry cooling (A4 only), and the electricity needed for all of these. Outside are the IT equipment, the building and the liquid-cooling loop, because all four options share them. We also leave out wastewater collection and the embodied emissions of the cooling equipment, because we could not find reliable data for the differences between options. Upstream wastewater collection and secondary treatment are excluded under an effluent cut-off for NEWater. The differential embodied emissions of the cooling equipment are omitted, and their effect on the ranking is not quantified.

Our carbon figures are therefore a screening estimate of the components listed, not a full carbon footprint of a data centre. Brine and blowdown are reported as volumes. A litre of brine from desalination and a litre of tower blowdown do not have the same ecological effect, and the AHP treats the volume only as a proxy.

# 3. Data and assumptions

Our main sources are the Public Utilities Board (PUB) for water benchmarks, tariffs and energy figures (PUB, 2023a, 2023b, 2025); the Energy Market Authority for the grid emission factor (EMA, 2026); IMDA and EDB for the policy context (EDB & IMDA, 2026; IMDA, 2024); and hourly Open-Meteo weather data for Jurong Island, 2015 to 2025 (Open-Meteo, n.d.). Mytton (2021) and Shehabi et al. (2024) give background on cooling and water accounting. None of these gives measured performance for the new Singapore sites. The 200 MW allocation is treated as IT capacity, not facility power, because MDDI (2026) counts it within the 1.6 GW IT-load figure.

Table 3 lists the inputs that matter most. Each input has a base value, a range used in the sensitivity tests, and an evidence status. **Verified** means we found a published source for the base value. **Team judgement** means it is our own assumption. For desalination energy the base value is published but the range is ours.

Table 3. Key inputs. Ranges are test ranges unless the evidence column says otherwise. The full register is in Table S1.

{{table_parameters}}

Of the {{n_parameters}} entries in our register, {{n_verified}} are verified, {{n_unverified}} still need checking and {{n_judgment}} are team judgements. Of the {{n_model}} inputs that enter the model, {{n_model_verified}} are verified. We say this early because it shapes how the results should be read. The cost and electricity penalty of dry cooling, the share of heat that dry cooling can take, the cost of recovery equipment and the non-energy emission factors are all our assumptions.

Two price points matter later. PUB's NEWater price is S${{newater_tariff}}/m³ before GST, and the non-domestic potable price is S${{potable_tariff}}/m³ (PUB, 2023b, Annexes A and B). The operator pays these. There is no separate tariff for desalinated water, so A1 uses the potable price as a proxy for the operator's bill. The resource-cost calculation does not use tariffs at all, because they include taxes and transfers.

# 4. Water demand

**How demand is calculated.** For each block of capacity, annual IT energy is the capacity multiplied by utilisation, the commissioning ramp and 8,760 hours. Water demand is that energy multiplied by WUE. We assume {{util}}% utilisation and a {{ramp_years}}-year ramp for each block. The 2035 figures therefore describe a completed ramp, not equipment running flat out.

**How WUE is set for each option.**

- **A1 and A2:** a standard evaporative tower at {{coc_current}} cycles of concentration. We scale a heat-balance curve to the PUB (2025) benchmark of {{wue_base}} m³/MWh.

- **A3:** the same tower run at {{coc_best}} cycles, which cuts the blowdown, with {{recovery}}% of the remaining blowdown recovered and reused. WUE falls to {{wue_A3}} m³/MWh. Running at 8 cycles alone gives {{coc8_wue}} m³/MWh, so about {{share_before_recovery}}% of A3's saving comes from the higher cycles and the rest from recovery (Table 12).

- **A4:** a dry loop takes {{liquid_share}}% of the heat. The other 20% goes through wet towers all year. The dry loop also needs wet trim when the air is hotter than {{trim_threshold}}°C, which is {{trim_percent}}% of hours in our weather record. WUE falls to {{wue_A4}} m³/MWh, of which {{a4_wet_remainder}} comes from the year-round wet share and {{a4_trim_part}} from the hot-hour trim. The A4 water figure therefore depends mainly on the assumed 80/20 split, which is a team judgement, and less on the weather. Section 8 shows what a warmer record does to it.

Figure 4 shows where each option sits. The curve shows how fast the tower's water use falls as cycles of concentration rise, and it flattens after about 8 cycles. That is why A3 also needs recovery, and why A4 needs a different approach altogether. The Green Data Centre Roadmap target of 2.0 m³/MWh (IMDA, 2024) is marked for comparison.

![Figure 4. Water use against cycles of concentration, with the four options marked. The curve is calibrated to the PUB benchmark of 2.1 m³/MWh.](fig_wue_ladder.png)

Table 4 gives the resulting annual demand in 2035. For the 200 MW case, ordinary towers use {{water_A2}} million m³ a year. A3 uses {{water_A3}} million m³ and A4 uses {{water_A4}} million m³. The base case is about {{national_share}}% of the {{national_water}} million m³ of potable water and NEWater sold in Singapore in {{national_year}} (Department of Statistics Singapore, 2026b). That share is small. It is a scale comparison only; most of that national volume is not cooling water.

Table 4. Annual make-up water in 2035, million m³. S2 and S3 are hypothetical total-capacity cases with the same utilisation and cooling assumptions.

{{table_demand}}

The larger scenarios only scale the totals. They do not change which option uses less water per MWh. The ranking of the options is the same in S1, S2 and S3, so we use S1 for most of the analysis.

# 5. Life cycle assessment: carbon

We follow the four phases of ISO 14040 (ISO, 2006a): goal and scope (Sections 2 and 3), inventory, impact assessment and interpretation.

**Inventory.** For each option we count the electricity used to produce water, move it to the island, treat recovered blowdown and run any extra dry-cooling fans. Production energy is the make-up water multiplied by the energy needed per cubic metre: 3.5 kWh for desalination (PUB, 2023a) and 0.7 kWh for NEWater, the midpoint of the 0.6 to 0.8 kWh/m³ range our register records for the Changi NEWater plant study. Conveyance adds 0.3 kWh/m³ and recovery treatment 1.0 kWh per m³ recovered; both are team-selected values with test ranges, not measured figures. Table S1 gives the source and status of every input. Dry cooling adds 0.05 to the PUE, which is {{dry_kwh}} kWh per MWh of IT energy. We also add a small non-energy emission term for plant construction and chemicals.

**Impact assessment.** We convert electricity to carbon using the grid emission factor. It starts at 0.404 kg CO₂/kWh in 2025 (EMA, 2026, Table 2.3) and falls to an assumed 0.38 in 2035; the 2027 to 2035 average of {{base_grid_factor}} kg CO₂/kWh is used for the per-MWh comparison. We do not treat the 50% green-energy commitment attached to DC-CFA2 as zero emissions for half the supply, because the official pathways include biomethane, ammonia and hydrogen (Ministry of Energy, Trade and Industry [METI], 2026), and we do not treat their lifecycle emissions as zero. The factors are operational CO₂ combined with assumed CO₂-equivalent inventory terms, not a gas-by-gas characterisation.

**Why climate change and water use only.** ISO 14044 asks that the impact categories fit the goal of the study (ISO, 2006b). Our question is about water supply for data-centre cooling, so we quantify the two categories that separate the options: climate change (kg CO₂e per MWh) and make-up water demand (WUE, a withdrawal measure, not consumptive use). We also report electricity use and brine or blowdown volume. We looked at other midpoint categories, such as acidification, particulate matter, eutrophication and ecotoxicity, and did not model them separately. We had no Singapore-specific data to characterise them and we do not claim a ranking for them. We do not report endpoint damage to health or ecosystems, because that needs value-laden factors built for other regions. The AHP keeps carbon, water, electricity and discharge as separate criteria, so none of them is hidden in a single score.

**Results.** Table 5 and Figure 5 show the results per MWh of IT energy.

Table 5. Electricity and carbon per MWh of IT energy. Carbon uses the average grid factor of {{base_grid_factor}} kg CO₂/kWh.

{{table_lca}}

![Figure 5. Modelled carbon emissions by component. A4's extra fan electricity dominates.](fig_lca_hotspots.png)

**Interpretation.** A3 has the lowest emissions, {{gwp_A3}} kg CO₂e/MWh, about {{a3_carbon_saving_r}}% below A2. It uses less water to treat and move, and recovery energy is small. A1 emits {{gwp_A1}} kg because desalination needs five times the energy of NEWater. A4 emits {{gwp_A4}} kg, about {{a4_gwp_multiple}} times A2, because its {{dry_kwh}} kWh of extra fan electricity far outweighs the water-production energy it saves. This does not mean dry cooling always emits more. Against A2, the extra dry-cooling PUE would have to be about {{ghg_threshold}} or lower for the two to emit the same amount at the base grid factor. That is a very small penalty, and measurements would be needed to know whether a real system can reach it.

# 6. Life cycle costing

We cost each option from two points of view, because the answer differs. Figure 6 shows how the costs are built up.

![Figure 6. Cost flow. The same physical quantities are priced twice: once as a resource cost to society and once as the bill the operator pays.](fig_report_costflow.png)

**Resource cost (society's perspective).** This counts what it costs to provide the water and run the equipment, using a 3% social discount rate, an electricity price of S$0.20/kWh, and no water taxes. We call it the resource cost throughout. The cost of water comes from a levelised cost of water (LCOW): the annualised plant capital, plus non-energy running costs, plus electricity, all divided by the water produced. We get S${{lcow_desal}}/m³ for desalination and S${{lcow_newater}}/m³ for NEWater. For context, the second Changi NEWater plant was awarded at S$0.276/m³ in its first year (PUB, 2014). Differences in year, financing and contract scope mean this does not validate our figure.

**Operator cost.** This counts what the data-centre owner pays: the PUB water tariff, equipment capital at an 8% discount rate, and electricity at S$0.25/kWh. Water taxes are part of the operator's bill, but they are a transfer, not a resource cost to society.

**Equipment costs.** Extra equipment is turned into an annual charge using the capital recovery factor over a 15-year life. For A3 the recovery equipment is assumed to cost S$60,000 per MW of IT load. For A4 the dry-cooling premium is S$100,000 per MW. These are our assumptions, not quotations. Once a block is commissioned, its equipment incurs this fixed annual charge during the load ramp as well; only variable costs scale with output (Section S6). A worked example is in Section S2.

**Carbon valuation.** We also priced the emissions in two separate ways: a carbon-price equivalent using the announced S$45/t for 2026 to 2027 and S$65/t, the midpoint of the published S$50 to 80 range for 2030 (National Climate Change Secretariat [NCCS], 2026), and an eco-cost of €0.15/kg CO₂e (Sustainability Impact Metrics, 2026). With the eco-cost added, the resource costs become S${{elcc_A1}}, {{elcc_A2}}, {{elcc_A3}} and {{elcc_A4}}/MWh for A1 to A4, and the order does not change. Neither valuation enters the main cost figures or the AHP, because electricity prices may already carry the carbon tax. The eco-cost factor is read from the emissions sheet of the published workbook, which is labelled 2025.

**Results.** Table 6 gives the cost per MWh at mature utilisation. Table 7 gives the net present cost over 2027 to 2035 for the 200 MW case.

Table 6. Base-case results per MWh of IT energy. Costs are before GST. Emissions cover the modelled water and heat-rejection components only.

{{table_summary}}

Table 7. Discounted cost over 2027 to 2035 for the 200 MW case, S$ million. Equipment charges start when each block is commissioned.

{{table_npc}}

![Figure 7. Cost per MWh by component, for society (left) and for the operator (right). A4's cost is almost all extra fan electricity.](fig_lcc_stack.png)

**Interpretation.**

- **A2 is the cheapest for society,** at S${{cost_A2}}/MWh. Switching from desalinated water (A1, S${{cost_A1}}) to NEWater cuts the resource cost by more than half.

- **A3 costs society S${{a3_social_premium}} more than A2.** The recovery equipment costs more each year than the value of the water it saves. For the operator it is the reverse: the avoided water bill is bigger, so A3 saves S${{a3_operator_saving}}/MWh. That saving excludes maintenance, chemicals and membrane replacement for the recovery unit, which we could not cost. An extra operating cost of about S${{maint_breakeven}} per MW of IT per year, {{maint_pct_capex}}% of the assumed equipment capital, would remove it at mature utilisation. Over the 2027 to 2035 horizon, with the commissioning ramp, the discounted operator advantage is S${{horizon_adv_m}} million; a fixed charge of about S${{horizon_fixed_charge}} per commissioned MW-year, or S${{horizon_per_mwh}}/MWh if proportional to throughput, removes it.

- **The break-even is a tariff of S${{reuse_tariff_threshold}}/m³.** If NEWater cost the operator less than that, A3 would not pay off. The current price is S${{newater_tariff}}/m³.

- **A4 is far more expensive,** at S${{cost_A4}}/MWh for society and S${{opcost_A4}} for the operator, about {{a4_cost_multiple}} times A2 for society. Fan electricity is almost the whole cost. Even with no electricity penalty at all, A4 would cost society S${{a4_cost_zero_pue}}/MWh because of its capital premium, so resource-cost parity with A2 needs a lower premium or a net electricity advantage. Operator-cost parity needs an extra PUE below {{dpue_operator_breakeven}} and carbon parity below {{ghg_threshold}} (Table 11).

# 7. Multi-criteria ranking with AHP

Cost, carbon and water use pull in different directions, and some things, such as technical maturity, are not on a numerical scale. We use the Analytic Hierarchy Process (Saaty, 1980) to bring them together.

**The hierarchy.** Figure 8 shows the structure: four main criteria (economic, environmental, water security and implementation) and 11 sub-criteria. Six sub-criteria are calculated from the model (marked Q). Five are pairwise judgements by the team (marked P). Tables S7 and S8 explain each one.

![Figure 8. The AHP hierarchy with balanced weights. Q marks scores taken from the model. P marks team judgements.](fig_ahp_hierarchy.png)

**How scores work.** For a Q criterion we use a linear rule: the best option gets the highest score and the worst the lowest, with a small floor so that no option scores zero. This rule is a choice, and Section 8 tests the alternative ratio rule. For a P criterion, we compare the options two at a time on Saaty's 1-to-9 scale and check the consistency ratio, which must stay at or below 0.10. Ours is at most {{max_cr}}. A low ratio shows internal agreement among the judgements, not their empirical validity. An option's final score is the sum of its criterion scores multiplied by the weights. The scoring rule and a worked sum are in Section S7.

**Five viewpoints.** We do not know whose preferences will decide, so we test five sets of main-criterion weights (Table 8). These are illustrations of what different groups might care about, not surveys of those groups. The operator viewpoint raises the weight on the economic criterion; the two cost sub-criteria stay equal, so it is an economic-emphasis case rather than a pure operator objective. The weather-resilience sub-criterion scores all four options equally, because every option must meet the same reliability requirement; it tempers the water-security criterion rather than separating the options, and the reduced-overlap case in Section 8 drops it.

Table 8. Main-criterion weights in each viewpoint.

{{table_weights}}

Table 9. AHP scores under the five viewpoints with the linear scoring rule. Each row adds to about 1. The highest score in each row is the first-ranked option.

{{table_ahp}}

![Figure 9. AHP scores under the five viewpoints.](fig_ahp_scores.png)

**What the ranking says.**

- **Under balanced weights the order is A3, A2, A1, A4.** A3 scores 0.299.

- **A3 is first in four of the five viewpoints under the linear rule.** It is a good all-rounder: lowest carbon, a reasonable cost and a real water saving. Under the ratio rule the operator viewpoint becomes a near tie, with A2 numerically first (Table 14).

- **A4 is first only under the PUB water-security viewpoint,** where water security carries about 54% of the weight. In the weight sweep of Figure S2, A4 overtakes A3 once that weight passes about {{c3_crossing}}.

- **A2 never ranks first under the linear rule.** It wins on resource cost, but a ranking that also values water and implementation prefers A3.

The AHP gives a ranking under stated judgements and a stated scoring rule. It should be read together with the separate cost, carbon and water results.

# 8. Sensitivity and uncertainty

We use a one-way (tornado) analysis, Monte Carlo simulation and rainbow plots for the AHP weights, and add break-even checks, structural cases, a scoring-rule test and a weather check to find where the conclusions can flip. Design details are in Section S9.

**One input at a time (tornado).** Figure 10 shows which inputs move the cost most. For A1 it is desalination energy and the plant electricity price. For A2 it is NEWater operating and capital cost. For A3 it is the recovery equipment cost. For A4 it is the extra dry-cooling PUE, which on its own moves cost from about S$6 lower to S$10 higher per MWh.

![Figure 10. Five largest cost drivers for each option, changing one input at a time from its low to its high value.](fig_tornado_cost_top5.png)

**All inputs together (Monte Carlo).** We drew {{n_mc}} sets of the {{n_mc_inputs}} uncertain inputs from triangular distributions (seed {{mc_seed}}) and re-ran the model each time. Table 10 shows how often each option comes out best.

Table 10. Share of the {{n_mc}} draws in which each option is best on the criterion. The first three rows use the model inputs only. The fourth also uses the base AHP judgements.

{{table_mc_criteria}}

Two rankings did not change in any of the {{n_mc}} sampled combinations: A2 has the lowest resource cost and A3 the lowest carbon. Joint boundary cases inside the declared ranges can still reverse them. With recovery capital at S$30,000/MW, a 20-year equipment life and 85% utilisation, A3's resource cost (S${{joint1_a3}}) falls just below A2's (S${{joint1_a2}}); with 4 and 6 cycles, 2 kWh/m³ recovery energy and NEWater and conveyance energy at their low bounds, A3's emissions ({{joint2_a3}} kg) rise just above A2's ({{joint2_a2}} kg). These are boundary stress cases, not likely outcomes. The operator result is less clear: A3 has the lower operator cost in {{p_a3_cheaper_operator}}% of the sampled parameter combinations and A2 in {{p_a2_cheaper_operator}}%. These shares describe the ranges we sampled, not an estimated probability of success.

**Break-even checks.** Table 11 asks how wrong an input would need to be to change a conclusion.

Table 11. Break-even values. A negative break-even PUE means that, at the assumed capital premium, resource-cost parity would require an electricity advantage over wet cooling, which lies outside the positive-penalty range used in the main analysis; at zero penalty A4 still costs S${{a4_cost_zero_pue}}/MWh against A2's S${{cost_A2}}.

{{table_breakeven}}

**Changing the model itself (structural cases).** Table 12 tests changes that are not just input ranges.

Table 12. Structural cases. Full results are in Section S9.

{{table_structural}}

Towers at 8 cycles without recovery give most of A3's water saving; with cheaper treatment equipment they beat A3 on both cost measures, so recovery itself needs its own justification (operator cost S${{coc8_opcost_40k}} or S${{coc8_opcost_20k}}/MWh against S${{opcost_A3}} for A3). The residual-desalination case shows A3's carbon advantage depends on NEWater. The discharge case shows a modest price on discharge flips the cost comparison between A2 and A3. The low-carbon case shows that even with clean electricity for the fans, A4 stays well above the other options.

**Changing the AHP weights and judgements.** We varied the weights and the pairwise judgements together in {{n_pref}} trials (seed {{pref_seed}}). Table 13 shows how often each option ranks first.

Table 13. Share of simulations in which each option is first. These are stress tests under the stated sampling design, not estimates of anyone's real preferences.

{{table_uncertainty}}

A3 stays first in about three-quarters of trials, and A4 takes most of the rest. When we also remove sub-criteria that overlap, A3 is first in about two-thirds. So the ranking is fairly stable, but it depends on how much weight water security gets.

**Changing the scoring rule.** Our linear rule compresses differences when one option is an extreme outlier. On the carbon criterion the local priorities are {{ghg_leaf_linear}}, so A1, with three and a half times the emissions of A2, scores almost the same as A2. The ratio rule that Saaty (1980) uses for measured quantities, where priority is proportional to 1/x, gives {{ghg_leaf_ratio}}. Table 14 compares the first-ranked option under both rules. The balanced, climate and growth viewpoints still put A3 first and the PUB viewpoint still puts A4 first. The operator viewpoint becomes a near tie, with {{ratio_w3_lead}} numerically first by {{ratio_w3_gap}} (A2 {{ratio_w3_a2}}, A3 {{ratio_w3_a3}}). The headline "first in four of five" therefore holds for the linear rule and becomes "first in three and a near tie in a fourth" for the ratio rule.

Table 14. First-ranked option under each viewpoint for the two scoring rules. Scores in brackets; full scores are in outputs/tables/validation_ahp_scoring.csv.

{{table_scoring}}

**Warmer weather than the record.** The hourly record is gridded, not measured on site. We compared it with the SingStat monthly series from the Changi climate station for the same years (Department of Statistics Singapore, 2026a; Section S5). The gridded record runs {{weather_bias}}°C cooler on the monthly midrange temperature, and its mean daily maximum is {{om_tmax}}°C against {{ss_tmax}}°C at Changi. This is a cross-location discrepancy between the east coast and a Jurong Island grid cell, not a measured bias at the site. We use it as a hypothetical warming case. Warming every hour by {{weather_bias}}°C raises the hours needing trim from {{trim_percent}}% to {{trim_share_bias}}% and A4's WUE from {{wue_A4}} to {{a4_wue_bias}} m³/MWh, so the saving against A2 falls from {{a4_water_saving_r}}% to {{a4_saving_bias}}% (Table S6). That is one selected case; the register's 27°C to 32°C threshold range is a separate sensitivity in which the saving runs from {{a4_saving_min}}% to {{a4_saving_max}}%. A4 stays the lowest water user in every case. Its cost and carbon change little because the extra PUE is held fixed in these runs, and that is what sets them.

**What holds and what does not.**

Table 15. Summary of the sensitivity results.

| Conclusion | Under the tested ranges and cases | Why |
| --- | --- | --- |
| A4 has the highest cost and carbon | Held in every test within the 0.02 to 0.10 extra-PUE range | True in every draw, structural case and weather case; below an extra PUE of {{ghg_threshold}} the carbon ranking would reverse |
| A4 uses the least water | Held in every test; size uncertain | True in every weather case; the saving against A2 ranges from {{a4_saving_min}}% to {{a4_saving_max}}% |
| A2 is cheapest for society | Held in all {{n_mc}} sampled combinations | Reversed if discharge is priced at the waterborne fee, or in the joint boundary case above |
| A3 has the lowest carbon | Held in all {{n_mc}} sampled combinations | Reversed if A3 must use desalinated water, or in the joint boundary case above |
| A3 saves the operator money | Held in {{p_a3_cheaper_operator}}% of sampled combinations, before omitted operating costs | About S${{maint_breakeven}} per MW IT-year at mature utilisation, or S${{horizon_fixed_charge}} per commissioned MW-year over the ramped horizon, removes the saving |
| A3 ranks first in the AHP | Depends on weights and scoring rule | First in four of five viewpoints under the linear rule; a near tie with A2 in the operator viewpoint under the ratio rule; second in the weight sweep once water security weighs more than about {{c3_crossing}} |

# 9. Discussion and recommendations

**Before any ranking applies.** Each option must first pass a feasibility check that this model does not perform: the local water quality must allow the assumed cycles of concentration, the dry cooler must meet the design heat load in the warmest hours, a NEWater connection must be available at the site, and the supply must meet the operator's reliability requirement. The results below assume all four are met.

**For PUB.** The model separates water saved from money saved. Recovery can reduce the supply that the national system has to provide, even though it raises the resource cost. It reduces withdrawal by {{a3_withdrawal_saving}} m³/MWh, but the evaporation term stays at {{evap}} m³/MWh, so consumptive use barely changes; the saving is in blowdown, not in water lost to the air. A claim for support would need evidence of what that saved supply is worth, such as avoided infrastructure, which we have not estimated. The model gives a performance level to test against: towers at 8 cycles reach {{coc8_wue}} m³/MWh and {{wue_A3}} with recovery under our assumptions, against the Roadmap target of 2.0 and the sector median of {{wue_base}}. Before any figure near 1.5 m³/MWh is used as a condition, PUB would need site evidence that those cycles and recovery rates can be held with the local water quality.

**For IMDA and EDB.** Two liquid-cooled sites can have very different water demand depending on whether they use towers or dry cooling. We recommend that bidders report annual PUE and WUE together, so the trade-off is visible. The break-even PUE of {{ghg_threshold}} in Table 11 shows how small the extra energy of a dry system must be before it beats NEWater-fed towers on carbon. It can help set what performance evidence to ask for; it is not a design standard.

**For data-centre operators.** The base case supports looking first at higher cycles of concentration, which give most of the water saving, and then at recovery. The modelled operator saving is small, about S${{a3_operator_saving}}/MWh, and disappears if the recovery unit's maintenance, chemicals and membranes cost more than about S${{maint_breakeven}} per MW-year, or S${{horizon_fixed_charge}} per commissioned MW-year over the ramped horizon. Towers at 8 cycles with cheaper treatment equipment can beat A3 on the operator's bill (Table 12), so recovery should be checked against supplier quotes and measured recovery rates before any investment. Dry cooling saves the most water. It reaches operator-cost parity with A2 only below an extra PUE of about {{dpue_operator_breakeven}} and carbon parity below {{ghg_threshold}}, and resource-cost parity also needs a lower capital premium; it makes sense only with measured performance near those levels, if water savings are valued much more highly, or if the site has another reason to avoid wet cooling.

**NEWater against desalination.** NEWater is cheaper and lower in carbon under our assumptions. Desalination still gives a supply that does not depend on used-water feedstock. A result on cost and carbon alone does not make it the worse choice on every sustainability criterion.

# 10. Limitations

- **Benchmarks are borrowed.** The wet-cooling benchmark comes from an existing fleet and is applied to new liquid-cooled sites. The heat balance alone gives {{hb3_uncalibrated}} m³/MWh at 3 cycles, {{hb3_pct}}% above the benchmark, and we scaled it down to match; the benchmark cannot then also validate the curve. Neither the dry-cooling electricity penalty, its capital cost nor the 80/20 heat split is based on a quotation or a measurement for the CFA2 sites.

- **The boundary leaves things out.** Wastewater treatment upstream, the embodied impact of the cooling equipment and the water used to generate electricity are not counted. Brine and blowdown are volumes, and we assess only climate change and water use, with no other midpoint or endpoint results.

- **The timeline is assumed.** Commissioning dates and phasing are modelling choices. Prices are held constant in real terms, with no forecast of tariffs, equipment replacement or future water-price changes.

- **Weather is gridded data.** It runs about {{weather_bias}}°C cooler than the Changi station series, the station record used in this study, which is in the east of the island. We report the effect on A4 as a hypothetical warming case rather than correcting the record, and we have not adjusted for future warming. The archive request did not pin a weather model, and the share of hours above {{trim_threshold}}°C rises from {{trim_year_min_share}}% in {{trim_year_min}} to {{trim_year_max_share}}% in {{trim_year_max}} while the annual mean moves by less than {{mean_temp_range}}°C, which points to a change in the underlying data product as much as in the weather (Section S3).

- **Inputs are treated as independent.** In reality, hot weather, energy penalties, utilisation and water use move together. A correlated draw could change the uncertainty ranges in either direction; we have not implemented one.

- **Operating costs are incomplete.** The recovery unit's maintenance, chemicals and membrane replacement are not costed. Section 6 gives the allowance that would remove A3's operator saving.

- **The AHP judgements and scoring rule are ours.** They illustrate how stakeholders might weigh things. They do not replace asking the stakeholders, and Table 14 shows that the rule used to score measured criteria can move one viewpoint.

- **Simulation shares are conditional.** The percentages in Tables 10, 13 and S9 describe the ranges we chose. They are not probabilities that a technology will perform best at a real site.

# 11. Conclusion

For 200 MW of new IT load, ordinary wet cooling needs about {{water_A2}} million m³ of water a year. High-concentration towers with recovery cut that to {{water_A3}} million m³, and dry cooling with a small wet share to {{water_A4}} million m³, or about {{a4_water_bias}} million m³ in the hypothetical case where every hour is {{weather_bias}}°C warmer than the gridded record.

The options trade off against each other. NEWater with ordinary towers (A2) is the cheapest for society. Recovery (A3) saves water and carbon and can save the operator money, at a small extra cost to society. Dry cooling (A4) saves the most water, but it reaches operator-cost parity with A2 only below an extra PUE of about {{dpue_operator_breakeven}} and carbon parity below {{ghg_threshold}}, and even with no penalty its capital premium keeps its resource cost above A2's. A3 is the most balanced option: it ranks first in four of five viewpoints under our linear scoring rule, is in a near tie with A2 in the operator viewpoint under a ratio rule, and in the weight sweep falls to second once water security is weighted above about {{c3_crossing}}.

The main contribution is the set of thresholds that show what evidence is needed: how low the dry-cooling energy penalty must be, what NEWater price makes recovery worthwhile, what discharge cost would change the answer, and how much the A4 water figure depends on the share of heat that still needs wet cooling. Site measurements and equipment quotations would settle these; more modelling would not.

# References

{{references}}

# Supplementary material

The sections below hold the detail behind the main report. They are meant for readers who want to check the numbers.

## S1. Full register of model inputs

Table S1. All active numerical assumptions. Context and calibration-only entries stay in config/assumptions.csv but are not varied in the uncertainty tests unless they affect a reported result.

{{table_active_assumptions}}

## S2. Equations and a worked example

**Water demand.** Annual IT energy = capacity × utilisation × ramp × 8,760 h. Make-up water = IT energy × WUE.

**Carbon per MWh of IT energy.** CO₂e = (electricity for water + electricity for dry fans) × grid factor + water × non-energy factor.

**Cost per MWh of IT energy.** Cost = water × (LCOW + conveyance cost) + equipment charge + extra electricity × price.

**Levelised cost of water.** LCOW = (capital recovery factor × capital cost) ÷ (365 × capacity factor) + non-energy running cost + specific energy × electricity price. This is the standard levelised-cost form with constant annual costs and zero salvage value.

Table S2. Worked calculation for A3 per MWh of IT energy. The capital recovery factors use a 15-year life at 3% (society) and 8% (operator). {{mwh_per_mw}} MWh is the yearly IT energy of 1 MW at {{util}}% utilisation.

{{table_worked}}

Table S3. Resource cost per MWh of IT energy by component, S$.

{{table_cost_social}}

Table S4. Operator cost per MWh of IT energy by component, S$.

{{table_cost_operator}}

## S3. Weather data and water balance

The weather file has {{weather_rows}} hourly records for 2015 to 2025. We check timestamps, missing values, duplicates and coverage. For the dry-cooling threshold we count the archived hours above it, instead of interpolating. The share of hours above {{trim_threshold}}°C is {{trim_percent}}%. The Open-Meteo request did not pin a weather model, so the record is not described as ERA5-only (Open-Meteo, n.d.), and it represents conditions near the site rather than an on-site sensor. By year, the share above {{trim_threshold}}°C runs from {{trim_year_min_share}}% in {{trim_year_min}} to {{trim_year_max_share}}% in {{trim_year_max}} while the annual mean temperature changes by less than {{mean_temp_range}}°C (Table S6b in Section S5). At the {{trim_year_max}} share alone, A4's WUE would be {{a4_wue_yearmax}} m³/MWh and its saving against A2 {{a4_saving_yearmax}}%. The pooled share is used in the base case; a re-fetch with a single pinned model is the next check.

The water balance is checked separately from the cost model. At the base settings the evaporation term is {{evap}} m³/MWh. Raising cycles of concentration from {{coc_current}} to {{coc_best}} reduces blowdown before recovery to {{blowdown_before}} m³/MWh. Recovering {{recovery}}% returns {{recovered}} m³/MWh and leaves {{discharge}} m³/MWh to discharge. Treatment electricity is charged only to the recovered water.

## S4. Levelised cost of water

The calculated LCOW is S${{lcow_desal}}/m³ for desalination and S${{lcow_newater}}/m³ for NEWater. Figure S1 compares these with historical concession prices, which are shown for context only.

![Figure S1. Modelled water cost and historical concession prices.](fig_lcow_check.png)

## S5. Weather record against a station series

The SingStat monthly climate series on data.gov.sg (Department of Statistics Singapore, 2026a) gives mean daily maximum and minimum temperatures by month. Its footnote states that from January 1984 the data come from the designated climate station at Changi. We averaged the Open-Meteo hourly record to the same monthly midrange, (maximum + minimum) ÷ 2, and compared the two for 2015 to 2025 (Table S5). The gridded record is cooler throughout. Because the station is on the east coast and the data-centre sites are in the west, this is a cross-location comparison, and we do not correct the record; we show the effect of a warmer record on A4 in Table S6. Warming every hour by b degrees is equivalent to lowering the trim threshold by b, which is how the cases were run.

Table S5. Open-Meteo gridded record for Jurong Island against the SingStat series from the Changi climate station.

{{table_weather}}

Table S6. A4 under warmer conditions and at the register's threshold bounds. Cost and carbon change little because fan electricity dominates them.

{{table_a4_weather}}

Table S6b. Share of archived hours above {{trim_threshold}}°C in each year, the annual mean temperature, and the A4 WUE that each year's share would imply on its own.

{{table_weather_years}}

## S6. Levelised cost and discount rates

The social perspective uses 3% and the operator perspective uses the 8% weighted average cost of capital in Table 3. Both are team judgements with ranges of 2 to 5% and 6 to 10%. The capital recovery factors used in Table S2 are {{crf_social}} and {{crf_operator}}.

## S7. AHP detail

**Scoring rule for model criteria.** For a criterion where less is better, an option scores (worst value − its value) + 0.10 × (range between worst and best), and the scores are then normalised to sum to 1. The 0.10 floor stops the worst option from scoring zero. We also tested floors of 0.01 and 0.30, and the ratio rule in Table 14.

**Worked sum for A3 under balanced weights.** A3's score is the sum over the 11 sub-criteria of the global weight × A3's local priority. The global weight is the main-criterion weight × the sub-criterion's share inside it. For example, the weight of greenhouse-gas emissions is 0.25 × 0.54 = 0.135.

Table S7. Global sub-criterion weights in the balanced case.

{{table_ahp_weights}}

## S8. Basis of the pairwise judgements

Table S8. Basis and limits of each comparison. The pairwise matrices and consistency ratios are in outputs/tables/ahp_pairwise_matrices.csv and ahp_consistency.csv.

{{table_ahp_notes}}

![Figure S2. Rainbow diagrams. Each panel changes one main-criterion weight from 0 to 1 and rescales the others. The dashed line marks the balanced weight.](fig_ahp_rainbow.png)

**Reading Figure S2.** In the C3 (water security) panel, A4 overtakes A3 at a weight of about {{c3_crossing}}. A2 comes first only if the economic weight is close to 1.

## S9. Sensitivity detail

**Design.** The Monte Carlo draws each uncertain input independently from a triangular distribution and uses the same draw for all four options, so comparisons are paired. Capacity is fixed within a scenario. The preference trials draw main weights uniformly from the weight simplex (Dirichlet 1,1,1,1), perturb the pairwise ratios with log-normal noise (log standard deviation 0.35, clipped to 1/9 to 9), redraw any matrix with a consistency ratio above 0.10, and sample the scoring floor from 0.01, 0.10 and 0.30. Each accepted set is evaluated with base inputs and with sampled inputs, for the full hierarchy and for a reduced-overlap hierarchy that drops electricity use, discharge volume and the qualitative leaves that partly repeat water demand.

Table S9. Fifth to 95th percentile ranges from the Monte Carlo draws. These are conditional simulation ranges, not confidence intervals.

{{table_parameter_intervals}}

![Figure S3. Distribution of the Monte Carlo results.](fig_mc_distributions.png)

![Figure S4. How often each option is best on each criterion, with fixed base preferences.](fig_mc_rank.png)

![Figure S5. Carbon tornado: the inputs that move emissions most.](fig_tornado_gwp.png)

## S10. Calibration, validation and checks

This is a deterministic scenario model; no statistical model is fitted, so there is no prediction error to report. We evaluate it in three ways: calibration against a benchmark, comparison with independent references, and internal consistency checks. Table S10 separates the three. The tower curve is calibrated to one benchmark, which cannot also serve as its validation, and the weather comparison in Table S5 is a descriptive cross-location check, not a validation of the site record.

Table S10. What was calibrated, what was compared with an independent reference, and what was only checked for consistency.

{{table_validation}}

**Checks carried out.** Demand scaling, unit consistency, the timing of equipment charges and the separation of resource costs from tariffs are tested. The AHP priority vectors are compared with an independent eigenvector calculation, normalisation is verified, and the consistency criterion is enforced for every judgement matrix. Saved base tables are compared with fresh calls to the model functions. These checks show the arithmetic is consistent. They cannot show that an assumed equipment cost or a future operating condition is right.

## S11. Reproducibility and AI use

The analysis reads config/assumptions.csv and the retained source data, and writes demand, LCA, LCC, AHP and sensitivity tables to outputs/tables (src/run_all.py, stages 02 to 08). src/12_validation_extras.py adds the weather comparisons, the A4 weather cases, the scoring-rule test, the calibration table and Figure 10. The report text is report_final.md in the project root; src/report_data_final.py reads the result tables and src/13_build_paper_final.py inserts the current numbers and builds the Word file. Figure 1 is drawn by src/16_draw_options_figure.py. Figures 2, 3 and 6 are diagrams supplied as image files in outputs/figures (fig_report_*.png); the script that drew them was not kept. The video deck (20 slides, deliverables/DSS5202_Group29_Video_Slides.pptx) was prepared in PowerPoint from the report figures and tables; src/17_edit_video_deck.py records the later text edits. The earlier generated deck from src/15_build_video_slides.py is kept in .build. The poster was generated on 25 October 2026 outside the Python environment; src/14_edit_presentations.py re-applies the later edits and redraws its AHP figure. The PDF was exported from the Word file with Microsoft Word (see README.md). The unit tests were last run on {{tests_date}} ({{tests_run}} tests, {{tests_ok}}). Source hashes and numerical checks are in outputs/validation/.

**Generative AI use.** Generative AI tools (ChatGPT and Claude) assisted with model development, code checks, and drafting and editing this report. The numerical results come from the submitted Python calculations. Assumptions, source limits and the scope of the checks are stated in the report and its supporting files.
