"""Report fields for the final report: the 25 October fields plus the tables
added in November 2026 (LCA detail, break-evens, structural cases, cost
components, worked example, weather and scoring-rule validation)."""
from pathlib import Path
import numpy as np
import pandas as pd

from report_data import context as base_context, read, fmt, mdtable, IDS
from model import load_params, crf, lca, lcc, tower_flows, wue_heat_balance, mwh_per_mw_year, commissioned_it_mw, YEARS

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / 'outputs/tables'
LABEL = {'A1': 'A1 Wet + desal', 'A2': 'A2 Wet + NEWater', 'A3': 'A3 Towers + reuse', 'A4': 'A4 Dry + wet trim'}
VIEW = {'W1 Balanced': 'W1 Balanced', 'W2 PUB / water security': 'W2 PUB / water security',
        'W3 Operator / economic': 'W3 Operator / economic', 'W4 Climate (EMA, NGOs)': 'W4 Climate (EMA, NGOs)',
        'W5 Growth (IMDA, EDB)': 'W5 Growth (IMDA, EDB)'}


def context():
    q = base_context()
    p = load_params()
    cfg = pd.read_csv(ROOT / 'config/assumptions.csv').set_index('id')
    L, C = read('lca_inventory', 'strategy'), read('lcc_per_mwh', 'strategy')
    M = read('mc_rank_probability', 'strategy')
    B, S = read('breakeven'), read('structural_sensitivity')
    W = read('ahp_weights')
    R = read('ahp_robustness')
    VW = read('validation_weather').set_index('metric')['value']
    VA = read('validation_a4_weather')
    VS = read('validation_ahp_scoring')
    VL = read('validation_ahp_scoring_leaves')
    VT = read('validation_summary')
    VC = read('validation_cycles_vs_recovery')
    VM = read('validation_maintenance_breakeven').set_index('quantity')['value']
    VU = read('validation_unit_tests').iloc[0]
    VY = read('validation_weather_years')
    CT = read('cooling_thresholds')
    N = read('npc_by_scenario')

    # ---- key inputs table with the desalination-energy status made explicit
    keys = [('util', 'Average utilisation, fraction'), ('wue_base', 'Wet-rejection WUE, m³/MWh'),
            ('coc_best', 'High cycles of concentration'), ('blowdown_recovery', 'Blowdown recovery, fraction'),
            ('dpue_dry', 'Additional dry-rejection PUE'), ('liquid_heat_share', 'Share of heat to the dry loop (A4)'),
            ('capex_hicoc', 'Recovery capex, S$/MW IT'), ('capex_dry_premium', 'Dry-rejection premium, S$/MW IT'),
            ('sec_desal', 'Desalination energy, kWh/m³'), ('sec_newater', 'NEWater energy, kWh/m³'),
            ('price_elec_plant', 'Resource electricity proxy, S$/kWh'), ('price_elec', 'Operator electricity, S$/kWh'),
            ('disc_social', 'Social discount rate, %'), ('disc_private', 'Operator discount rate, %')]
    status = {'sec_desal': 'base verified; range assumed'}
    q['table_parameters'] = mdtable(['Parameter', 'Base', 'Low–high', 'Evidence status'],
        [[label, fmt(cfg.loc[k, 'base']), fmt(cfg.loc[k, 'low']) + '–' + fmt(cfg.loc[k, 'high']), status.get(k, cfg.loc[k, 'status'])] for k, label in keys])

    # ---- LCA detail (Table 5)
    rows = []
    for a in IDS:
        r = L.loc[a]
        rows.append([LABEL[a], fmt(r.kwh_production + r.kwh_conveyance + r.kwh_onsite), fmt(r.kwh_dc_delta, 1),
                     fmt(r.gwp_water_energy + r.gwp_dc_delta), fmt(r.gwp_nonenergy), fmt(r.gwp_total)])
    q['table_lca'] = mdtable(['Option', 'Electricity for water, kWh', 'Extra fan electricity, kWh', 'CO₂e from electricity, kg', 'CO₂e non-energy, kg', 'Total CO₂e, kg'], rows)
    q['trim_percent'] = fmt(float(q['trim_percent']), 1)
    q['a4_gwp_multiple'] = fmt(L.loc['A4', 'gwp_total'] / L.loc['A2', 'gwp_total'], 0)
    q['a4_cost_multiple'] = fmt(C.loc['A4', 'social_cost'] / C.loc['A2', 'social_cost'], 0)
    q['desal_energy_multiple'] = fmt(p['sec_desal'] / p['sec_newater'], 0)
    for a in IDS:
        q[f'cost_{a}'] = fmt(C.loc[a, 'social_cost'])
        q[f'opcost_{a}'] = fmt(C.loc[a, 'operator_cost'])
        q[f'elcc_{a}'] = fmt(C.loc[a, 'elcc_social_eco'])
    model_rows = cfg[cfg.role == 'model']
    q['n_model'] = str(len(model_rows))
    q['n_model_verified'] = str(int((model_rows.status == 'verified').sum()))
    q['a3_water_saving_r'] = fmt(float(q['a3_water_saving']), 0)
    q['a4_water_saving_r'] = fmt(float(q['a4_water_saving']), 0)
    q['a3_carbon_saving_r'] = fmt(float(q['a3_carbon_saving']), 0)
    q['p_a3_cheaper_operator'] = fmt(M.loc['A3', 'p_A3_cheaper_than_A2_operator'] * 100, 1)
    q['p_a2_cheaper_operator'] = fmt((1 - M.loc['A3', 'p_A3_cheaper_than_A2_operator']) * 100, 1)

    # ---- Monte Carlo criterion table (Table 10)
    q['table_mc_criteria'] = mdtable(['Question'] + IDS, [
        ['Lowest resource cost'] + [fmt(M.loc[a, 'p_lowest_social_cost'] * 100, 1) + '%' for a in IDS],
        ['Lowest operator cost'] + [fmt(M.loc[a, 'p_lowest_operator_cost'] * 100, 1) + '%' for a in IDS],
        ['Lowest carbon emissions'] + [fmt(M.loc[a, 'p_lowest_gwp'] * 100, 1) + '%' for a in IDS],
        ['First in the AHP (balanced weights)'] + [fmt(M.loc[a, 'p_rank1_ahp_W1'] * 100, 1) + '%' for a in IDS]])

    # ---- break-even table (Table 11)
    def be(pattern):
        return B[B.question.str.contains(pattern, regex=True)].iloc[0]
    be_rows = [('A4 matches A2 on resource cost: extra dry-cooling PUE of', 'A4 versus A2:.*resource cost', 4),
               ('A4 matches A2 on carbon: extra dry-cooling PUE of', 'A4 versus A2:.*GHG', 4),
               ('Desalination matches NEWater on carbon: desalination energy, kWh/m³', 'Desalination specific energy', 2),
               ('Operator is no better off with A3 than A2: NEWater tariff, S$/m³', 'NEWater tariff', 2),
               ('A3 costs society the same as A2: recovery capex, S$/MW IT', 'A3 recovery capex', 0),
               ('A4 matches A2 for the operator: dry-cooling capex, S$/MW IT', 'A4 dry-rejection capex', 0)]
    rows = []
    op_row = CT[(CT.comparison == 'A2') & ((CT.capex_dry_premium - p['capex_dry_premium']).abs() < 1)].iloc[0]
    for label, pattern, nd in be_rows:
        r = be(pattern)
        base = fmt(r.base, nd if nd else 0) if nd != 4 else f'{r.base:.2f}'
        val = 'no value works' if pd.isna(r.breakeven) else (f'{r.breakeven:.4f}' if nd == 4 else fmt(r.breakeven, nd))
        rows.append([label, base, val])
        if pattern == 'A4 versus A2:.*resource cost':
            rows.append(['A4 matches A2 for the operator: extra dry-cooling PUE of', f"{p['dpue_dry']:.2f}", f'{op_row.operator_cost_equal_dpue:.4f}'])
    from scipy.optimize import brentq
    gap = lambda c: lcc({**p, 'cost_discharge_treatment': c}).loc['A3', 'social_cost'] - lcc({**p, 'cost_discharge_treatment': c}).loc['A2', 'social_cost']
    discharge_be = brentq(gap, 0.0, 3.0)
    rows.append(['A3 costs society the same as A2: resource cost of discharged blowdown, S$/m³', fmt(p['cost_discharge_treatment']), fmt(discharge_be)])
    q['discharge_breakeven'] = fmt(discharge_be)
    q['table_breakeven'] = mdtable(['Question', 'Base value', 'Break-even value'], rows)
    q['dpue_operator_breakeven'] = f'{op_row.operator_cost_equal_dpue:.4f}'
    q['a4_cost_zero_pue'] = fmt(lcc({**p, 'dpue_dry': 0.0}).loc['A4', 'social_cost'])
    # joint boundary cases inside the declared ranges (reported, not sampled)
    j1 = lcc({**p, 'capex_hicoc': 30000.0, 'life_dc_cooling': 20.0, 'util': 0.85})
    q['joint1_a3'], q['joint1_a2'] = fmt(j1.loc['A3', 'social_cost'], 3), fmt(j1.loc['A2', 'social_cost'], 3)
    j2 = lca({**p, 'coc_current': 4.0, 'coc_best': 6.0, 'sec_hicoc': 2.0, 'sec_newater': 0.6, 'sec_distrib': 0.2})
    q['joint2_a3'], q['joint2_a2'] = fmt(j2.loc['A3', 'gwp_total'], 3), fmt(j2.loc['A2', 'gwp_total'], 3)
    # horizon operator advantage of A3 and the fixed charge that removes it
    nop = N[(N.perspective == 'operator') & (N.scenario == 'S1')].set_index('strategy')
    adv = nop.loc['A2', 'npc_sgd'] - nop.loc['A3', 'npc_sgd']
    rate = p['disc_private'] / 100
    pv_mw_years = sum(commissioned_it_mw(p, 'S1', y) / (1 + rate) ** (y - 2026) for y in YEARS)
    q['horizon_adv_m'] = fmt(adv / 1e6, 1)
    q['horizon_fixed_charge'] = fmt(adv / pv_mw_years, 0)
    q['horizon_per_mwh'] = fmt(adv / nop.loc['A3', 'pv_mwh'], 2)
    q['a3_withdrawal_saving'] = fmt(L.loc['A2', 'wue'] - L.loc['A3', 'wue'])
    q['cycles_saving'] = fmt(L.loc['A2', 'wue'] - VC.wue_m3_per_mwh[1])
    # per-year weather exposure
    ymin, ymax = VY.loc[VY.share_above_threshold.idxmin()], VY.loc[VY.share_above_threshold.idxmax()]
    q['trim_year_min'], q['trim_year_min_share'] = str(int(ymin.year)), fmt(ymin.share_above_threshold * 100, 1)
    q['trim_year_max'], q['trim_year_max_share'] = str(int(ymax.year)), fmt(ymax.share_above_threshold * 100, 1)
    q['a4_wue_yearmax'] = fmt(ymax.a4_wue_m3_per_mwh)
    q['a4_saving_yearmax'] = fmt(ymax.a4_water_saving_vs_A2 * 100, 0)
    q['mean_temp_range'] = fmt(VY.mean_temperature_degC.max() - VY.mean_temperature_degC.min(), 1)
    q['table_weather_years'] = mdtable(['Year', 'Hours above threshold', 'Annual mean, °C', 'A4 WUE at that share, m³/MWh', 'Saving vs A2'],
        [[str(int(r.year)), fmt(r.share_above_threshold * 100, 1) + '%', fmt(r.mean_temperature_degC, 1), fmt(r.a4_wue_m3_per_mwh), fmt(r.a4_water_saving_vs_A2 * 100, 0) + '%'] for r in VY.itertuples()])
    q['dpue_cost_breakeven'] = f"{be('A4 versus A2:.*resource cost').breakeven:.4f}"
    q['capex_hicoc_breakeven'] = fmt(be('A3 recovery capex').breakeven, 0)
    q['sec_desal_breakeven'] = fmt(be('Desalination specific energy').breakeven)

    # ---- structural cases (Table 12)
    def case(name, a, col):
        return S[(S.case.str.startswith(name)) & (S.strategy == a)][col].iloc[0]
    low = S[S.case.str.startswith('DC low-carbon') & (S.strategy == 'A4')].gwp
    q['table_structural'] = mdtable(['Case', 'What changes', 'Result'], [
        ['Base case', 'None', f"A2 is cheapest for society (S${fmt(case('Base', 'A2', 'social_cost'))}); A3 has the lowest carbon ({fmt(case('Base', 'A3', 'gwp'))} kg)"],
        ['Towers at 8 cycles without recovery', 'A3 keeps its treatment capex but recovers no blowdown',
         f"Water {fmt(VC.wue_m3_per_mwh[1])} m³ (A3 {fmt(VC.wue_m3_per_mwh[2])}); carbon {fmt(VC.gwp_kg_per_mwh[1])} kg; resource cost S${fmt(VC.resource_cost_sgd_per_mwh[1])}; operator cost S${fmt(VC.operator_cost_sgd_per_mwh[1])}"],
        ['Towers at 8 cycles without recovery, cheaper treatment', 'Treatment capex S$40,000 or S$20,000 per MW instead of S$60,000',
         f"Resource cost S${fmt(VC.resource_cost_sgd_per_mwh[3])} or S${fmt(VC.resource_cost_sgd_per_mwh[4])}; operator cost S${fmt(VC.operator_cost_sgd_per_mwh[3])} or S${fmt(VC.operator_cost_sgd_per_mwh[4])} (A3: S${fmt(VC.resource_cost_sgd_per_mwh[2])} and S${fmt(VC.operator_cost_sgd_per_mwh[2])})"],
        ['Residual desalination', 'A3 and A4 use desalinated water instead of NEWater',
         f"A3 carbon rises from {fmt(case('Base', 'A3', 'gwp'))} to {fmt(case('Residual', 'A3', 'gwp'))} kg; resource cost from S${fmt(case('Base', 'A3', 'social_cost'))} to S${fmt(case('Residual', 'A3', 'social_cost'))}"],
        ['Priced discharge', f"S${fmt(p['fee_waterborne'])} per m³ of blowdown discharged",
         f"A3 (S${fmt(case('Discharge resource cost 1.09', 'A3', 'social_cost'))}) becomes cheaper than A2 (S${fmt(case('Discharge resource cost 1.09', 'A2', 'social_cost'))}) for society"],
        ['Low-carbon electricity for the data centre', '50% or 80% of fan electricity at 0.05–0.30 kg CO₂e/kWh',
         f"A4 carbon falls from {fmt(case('Base', 'A4', 'gwp'))} to {fmt(low.min(), 1)}–{fmt(low.max(), 1)} kg, still above every other option"]])
    q['coc8_wue'] = fmt(VC.wue_m3_per_mwh[1])
    q['coc8_gwp'] = fmt(VC.gwp_kg_per_mwh[1])
    q['coc8_opcost'] = fmt(VC.operator_cost_sgd_per_mwh[1])
    q['coc8_cost'] = fmt(VC.resource_cost_sgd_per_mwh[1])
    q['share_before_recovery'] = fmt(VC.share_of_A3_water_saving[1] * 100, 0)
    q['coc8_opcost_40k'] = fmt(VC.operator_cost_sgd_per_mwh[3])
    q['coc8_opcost_20k'] = fmt(VC.operator_cost_sgd_per_mwh[4])
    q['coc8_cost_20k'] = fmt(VC.resource_cost_sgd_per_mwh[4])
    q['maint_breakeven'] = fmt(VM['Omitted operating cost that removes the saving'], 0)
    q['maint_pct_capex'] = fmt(VM['Same allowance as a share of the assumed recovery capex'] * 100, 1)
    q['tests_run'] = str(int(VU.tests_run))
    q['tests_date'] = str(VU.run_time)[:10]
    q['tests_ok'] = 'pass' if bool(VU.ok) else 'FAIL'
    q['a4_lowc_min'] = fmt(low.min(), 1)
    q['a4_lowc_max'] = fmt(low.max(), 1)

    # ---- viewpoint weights (Table 8)
    rows = []
    for sc, g in W.groupby('weight_scenario', sort=False):
        mw = g.drop_duplicates('criterion').set_index('criterion').main_weight
        rows.append([VIEW[sc]] + [fmt(mw[c]) for c in ['C1 Economic', 'C2 Environmental', 'C3 Water security', 'C4 Implementation']])
    q['table_weights'] = mdtable(['Viewpoint', 'C1 Economic', 'C2 Environmental', 'C3 Water security', 'C4 Implementation'], rows)

    # ---- rainbow crossing for C3 (water security)
    c3 = R[(R.case == 'C3 Water security') & (R.kind == 'main weight')]
    piv = c3.pivot(index='value', columns='strategy', values='score').sort_index()
    gap = piv['A4'] - piv['A3']
    cross = None
    for (w0, g0), (w1, g1) in zip(gap.items(), list(gap.items())[1:]):
        if g0 < 0 <= g1:
            cross = w0 + (w1 - w0) * (-g0) / (g1 - g0)
            break
    q['c3_crossing'] = fmt(cross, 2) if cross is not None else 'n/a'

    # ---- scoring-rule test (Table 14)
    rules = list(dict.fromkeys(VS.rule))
    rows = []
    for sc in VIEW:
        row = [VIEW[sc]]
        for rule in rules:
            r = VS[(VS.rule == rule) & (VS.weight_scenario == sc)].iloc[0]
            lead = f"{r['first']} ({fmt(r[r['first']], 3)})"
            if r.tie_within_0_005:
                lead = f"near tie: {r['first']} first ({r[r['first']]:.4f} vs {r[r['second']]:.4f} for {r['second']})"
            row.append(lead)
        rows.append(row)
    q['table_scoring'] = mdtable(['Viewpoint', 'Linear rule (report base): first', 'Ratio rule: first'], rows)
    lin = VL[(VL.rule == rules[0]) & (VL.leaf == 'C2a GHG per MWh_IT')].set_index('strategy').local_priority
    rat = VL[(VL.rule == rules[1]) & (VL.leaf == 'C2a GHG per MWh_IT')].set_index('strategy').local_priority
    q['ghg_leaf_linear'] = ', '.join(f'{a} {fmt(lin[a], 3)}' for a in IDS)
    q['ghg_leaf_ratio'] = ', '.join(f'{a} {fmt(rat[a], 3)}' for a in IDS)
    ratio_first = VS[VS.rule == rules[1]].set_index('weight_scenario')
    q['ratio_w3_a2'] = fmt(ratio_first.loc['W3 Operator / economic', 'A2'], 3)
    q['ratio_w3_a3'] = fmt(ratio_first.loc['W3 Operator / economic', 'A3'], 3)
    q['ratio_w1_a1'] = fmt(ratio_first.loc['W1 Balanced', 'A1'], 3)
    r3 = ratio_first.loc['W3 Operator / economic']
    q['ratio_w3_lead'] = 'A2' if r3['A2'] >= r3['A3'] else 'A3'
    q['ratio_w3_gap'] = f"{abs(r3['A2'] - r3['A3']):.4f}"

    # ---- weather comparison (Table S5) and A4 cases (Table S6)
    q['weather_months'] = fmt(VW['months_compared'], 0)
    q['weather_bias'] = fmt(abs(float(VW['bias_midrange_degC'])), 2)
    q['weather_rmse'] = fmt(VW['rmse_midrange_degC'], 2)
    q['weather_maxdiff'] = fmt(VW['max_abs_diff_degC'], 2)
    q['weather_corr'] = fmt(VW['correlation'], 2)
    q['om_tmax'] = fmt(VW['openmeteo_mean_daily_max_degC'], 1)
    q['ss_tmax'] = fmt(VW['station_mean_daily_max_degC'], 1)
    q['table_weather'] = mdtable(['Check (2015–2025)', 'Value'], [
        ['Months compared', q['weather_months']],
        ['Open-Meteo minus station, monthly midrange temperature', f"−{q['weather_bias']} °C (gridded record cooler)"],
        ['Root-mean-square monthly difference', f"{q['weather_rmse']} °C"],
        ['Largest monthly difference', f"{q['weather_maxdiff']} °C"],
        ['Month-to-month correlation', q['weather_corr']],
        ['Mean daily maximum, Open-Meteo vs station', f"{q['om_tmax']} vs {q['ss_tmax']} °C"]])
    rows = []
    for r in VA.itertuples():
        rows.append([r.case.replace('degC', '°C'), fmt(r.trim_hour_share * 100, 1) + '%', fmt(r.a4_wue_m3_per_mwh),
                     fmt(r.a4_water_saving_vs_A2 * 100, 0) + '%', fmt(r.a4_water_2035_S1_Mm3), fmt(r.a4_gwp_kg_per_mwh)])
    q['table_a4_weather'] = mdtable(['Case', 'Hours needing trim', 'A4 WUE, m³/MWh', 'Saving vs A2', '2035 water, S1, million m³', 'A4 CO₂e, kg/MWh'], rows)
    biasrow = VA[VA.case.str.contains('Hypothetical warming')].iloc[0]
    q['a4_wue_bias'] = fmt(biasrow.a4_wue_m3_per_mwh)
    q['a4_saving_bias'] = fmt(biasrow.a4_water_saving_vs_A2 * 100, 0)
    q['trim_share_bias'] = fmt(biasrow.trim_hour_share * 100, 1)
    q['a4_water_bias'] = fmt(biasrow.a4_water_2035_S1_Mm3)
    q['a4_saving_min'] = fmt(VA.a4_water_saving_vs_A2.min() * 100, 0)
    q['a4_saving_max'] = fmt(VA.a4_water_saving_vs_A2.max() * 100, 0)
    base = VA.iloc[0]
    q['a4_wet_remainder'] = fmt(base.a4_from_wet_remainder)
    q['a4_trim_part'] = fmt(base.a4_from_hot_hour_trim)
    q['a4_wet_share_pct'] = fmt(base.a4_from_wet_remainder / base.a4_wue_m3_per_mwh * 100, 0)

    # ---- validation summary (Table S10)
    q['table_validation'] = mdtable(['Component', 'Kind', 'Model value vs reference', 'Result'],
        [[r.component, r.kind, f'{r.model_value}; {r.reference}', f'{r.difference}. {r.reading}'] for r in VT.itertuples()])
    hb3, _ = wue_heat_balance(p, p['coc_current'])
    q['hb3_uncalibrated'] = fmt(hb3)
    q['hb3_pct'] = fmt((hb3 / p['wue_base'] - 1) * 100, 0)

    # ---- cost components (Tables S3, S4) and worked example (Table S2)
    q['table_cost_social'] = mdtable(['Option', 'Water', 'Equipment', 'Extra electricity', 'Total'],
        [[LABEL[a], fmt(C.loc[a, 'water_cost_social']), fmt(C.loc[a, 'onsite_capex']), fmt(C.loc[a, 'onsite_energy'] + C.loc[a, 'dc_energy_delta']), fmt(C.loc[a, 'social_cost'])] for a in IDS])
    q['table_cost_operator'] = mdtable(['Option', 'Water bill', 'Equipment', 'Extra electricity', 'Total'],
        [[LABEL[a], fmt(C.loc[a, 'operator_water']), fmt(C.loc[a, 'operator_capex']), fmt(C.loc[a, 'operator_onsite_energy'] + C.loc[a, 'operator_dc_energy_delta']), fmt(C.loc[a, 'operator_cost'])] for a in IDS])
    flows = tower_flows(p)
    wue3 = L.loc['A3', 'wue']; ef = L.loc['A3', 'ef_grid']
    e_prod, e_conv, e_rec = wue3 * p['sec_newater'], wue3 * p['sec_distrib'], flows['recovered'] * p['sec_hicoc']
    e_tot = e_prod + e_conv + e_rec
    crf_s, crf_o = crf(p['disc_social'], p['life_dc_cooling']), crf(p['disc_private'], p['life_dc_cooling'])
    mwh = mwh_per_mw_year(p)
    q['crf_social'] = f'{crf_s:.5f}'
    q['crf_operator'] = f'{crf_o:.5f}'
    q['mwh_per_mw'] = fmt(mwh, 0)
    q['table_worked'] = mdtable(['Step', 'Calculation', 'Result'], [
        ['Make-up water', 'WUE for A3', f'{fmt(wue3)} m³'],
        ['Production electricity', f"{fmt(wue3)} m³ × {p['sec_newater']:g} kWh/m³", f'{fmt(e_prod)} kWh'],
        ['Conveyance electricity', f"{fmt(wue3)} m³ × {p['sec_distrib']:g} kWh/m³", f'{fmt(e_conv)} kWh'],
        ['Recovery electricity', f"{fmt(flows['recovered'])} m³ recovered × {p['sec_hicoc']:g} kWh/m³", f'{fmt(e_rec)} kWh'],
        ['Electricity, total', 'sum', f'{fmt(e_tot, 1)} kWh'],
        ['CO₂e from electricity', f'{fmt(e_tot, 1)} kWh × {ef:.4f}', f'{fmt(e_tot * ef)} kg'],
        ['CO₂e non-energy', f"{fmt(wue3)} m³ × {p['ghg_newater_nonenergy']:g} kg/m³", f"{fmt(wue3 * p['ghg_newater_nonenergy'])} kg"],
        ['**Total CO₂e**', 'sum', f"**{fmt(L.loc['A3', 'gwp_total'])} kg**"],
        ['Equipment charge, society', f"S${fmt(p['capex_hicoc'], 0)} × {crf_s:.5f} ÷ {fmt(mwh, 0)} MWh", f"S${fmt(C.loc['A3', 'onsite_capex'])}"],
        ['Equipment charge, operator', f"S${fmt(p['capex_hicoc'], 0)} × {crf_o:.5f} ÷ {fmt(mwh, 0)} MWh", f"S${fmt(C.loc['A3', 'operator_capex'])}"]])
    q['references'] = (ROOT / 'references.md').read_text()
    return {k: str(v) for k, v in q.items()}


if __name__ == '__main__':
    for k, v in context().items():
        if not k.startswith('table_') and k != 'references':
            print(k, '=', v)
