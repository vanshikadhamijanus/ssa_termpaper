"""
Core model for 'The Thirsty Cloud' (DSS5202 Group 29).

Everything the analysis scripts (03-07) need is a pure function of one
parameter dictionary `p`, so the same code serves the base case, the tornado
and the Monte Carlo. Units: SGD on a constant-price modelling basis, m3,
MWh of IT energy (MWh_IT). Historical equipment costs are illustrative inputs;
they have not been rebased to verified 2026 procurement prices.

    from model import load_params, demand, lca, lcc
    p = load_params()            # base values from config/assumptions.csv
    D = demand(p)                # annual IT energy and water by scenario x strategy
    L = lca(p)                   # electricity and GWP per MWh_IT by strategy
    C = lcc(p, L)                # cost per MWh_IT, both perspectives, eLCC
"""
from pathlib import Path
from functools import lru_cache

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config"
PROC = ROOT / "data" / "processed"
OUT = ROOT / "outputs"
TAB = OUT / "tables"
FIG = OUT / "figures"

YEARS = list(range(2027, 2036))
STRATEGIES = ["A1", "A2", "A3", "A4"]
STRATEGY_NAME = {
    "A1": "A1 Wet rejection with desalination",
    "A2": "A2 Wet rejection with NEWater",
    "A3": "A3 High-CoC wet rejection with blowdown recovery",
    "A4": "A4 Dry rejection with adiabatic trim",
}
SHORT = {"A1": "Wet + desal", "A2": "Wet + NEWater", "A3": "High-CoC + reuse", "A4": "Dry + trim"}
SCENARIOS = ["S1", "S2", "S3"]
SCENARIO_NAME = {"S1": "S1 DC-CFA2 (200 MW IT)",
                 "S2": "S2 Hypothetical growth (500 MW IT total)",
                 "S3": "S3 Hypothetical growth (700 MW IT total)"}
GRIDS = ["bau", "lowc", "flat"]
GRID_NAME = {"bau": "BAU grid", "lowc": "Low-carbon grid", "flat": "Flat grid (0.40)"}
COLORS = {"A1": "#1f5fa8", "A2": "#2a9d8f", "A3": "#e69f00", "A4": "#c1443c"}

# Only these inputs affect reported model results. The register separately
# retains historical/context and heat-balance calibration inputs.
ACTIVE_UNCERTAIN_PARAMS = (
    "util", "ramp_years", "wue_base", "coc_current", "coc_best",
    "blowdown_recovery", "trim_threshold", "liquid_heat_share", "dpue_dry",
    "sec_desal", "sec_newater", "sec_distrib", "sec_hicoc",
    "ghg_desal_nonenergy", "ghg_newater_nonenergy", "ef_grid_2035_bau",
    "ef_grid_2035_lowc", "capex_desal", "capex_newater",
    "opex_desal_nonenergy", "opex_newater_nonenergy", "price_elec",
    "price_elec_plant", "capex_hicoc", "capex_dry_premium", "life_plant",
    "life_dc_cooling", "disc_social", "disc_private", "carbon_tax_2030",
    "ecocost_gwp", "fx_eur_sgd", "swro_recovery", "newater_recovery", "plant_cf",
)

MODEL_SCOPE = (
    "Screening comparison of water supply and heat-rejection components. "
    "All alternatives share liquid-cooled IT equipment; its common energy and "
    "capital are excluded. A4 includes only the incremental dry-rejection "
    "energy and capital. Primary GHG uses the full grid factor, without assuming "
    "green-energy pathways have zero lifecycle emissions. Plant capital and "
    "on-site equipment assumptions are illustrative where source data are absent."
)


# --------------------------------------------------------------------------
def load_params(case="base"):
    """Return {id: value} for one column of assumptions.csv (low/base/high)."""
    a = pd.read_csv(CFG / "assumptions.csv").set_index("id")
    return a[case].astype(float).to_dict()


def load_assumptions():
    return pd.read_csv(CFG / "assumptions.csv")


def crf(rate_pct, n):
    """Capital recovery factor, rate in percent per year."""
    i = rate_pct / 100.0
    return i * (1 + i) ** n / ((1 + i) ** n - 1) if i > 0 else 1.0 / n


def grid_ef(p, grid="bau"):
    """Grid emission factor by year, kgCO2/kWh. Linear from the 2025 EMA value."""
    ef0, y0 = 0.404, 2025  # EMA SES 2026 T2.3 (2025)
    target = {"bau": p["ef_grid_2035_bau"], "lowc": p["ef_grid_2035_lowc"], "flat": 0.40}[grid]
    if grid == "flat":
        return {y: 0.40 for y in YEARS}
    return {y: ef0 + (target - ef0) * (y - y0) / (2035 - y0) for y in YEARS}


def carbon_price(p, y):
    """Singapore carbon tax path, SGD/tCO2e (NCCS)."""
    if y <= 2027:
        return p["carbon_tax_2026"]
    if y >= 2030:
        return p["carbon_tax_2030"]
    return p["carbon_tax_2026"] + (p["carbon_tax_2030"] - p["carbon_tax_2026"]) * (y - 2027) / 3


# --------------------------------------------------------------------------
# Demand model (answers Q1, Q2)
# --------------------------------------------------------------------------
def wue_heat_balance(p, coc):
    """Evaporative-tower WUE from a heat balance, m3/MWh_IT."""
    evap = 3.6 / p["latent_heat"] * p["heat_reject_factor"] * p["evap_fraction"]
    return evap * coc / (coc - 1), evap


@lru_cache(maxsize=1)
def _hourly_dry_bulb():
    """Sorted observed archive temperatures; cache avoids repeated CSV reads."""
    path = ROOT / "data/raw/weather/openmeteo_jurong_island_hourly_2015_2025.csv"
    t = pd.read_csv(path, usecols=["temperature_2m"])["temperature_2m"]
    if t.empty or t.isna().any():
        raise ValueError("Hourly weather must contain non-missing temperatures")
    return np.sort(t.to_numpy(dtype=float))


def trim_hour_share(p):
    """Exact fraction of archived hours above the assumed dry-cooler threshold.

    This is an empirical weather exposure proxy, not an equipment performance
    model. The denominator includes actual leap-year hours in the archive.
    """
    t = _hourly_dry_bulb()
    return float((len(t) - np.searchsorted(t, p["trim_threshold"], side="right")) / len(t))


def tower_flows(p):
    """Calibrated A3 water balance, m3/MWh_IT, neglecting drift.

    CoC controls gross tower blowdown before its recovery unit. Recovered
    permeate returns to the tower; residual concentrate leaves the site.
    Treatment energy is specified per m3 recovered, not per m3 avoided.
    """
    if p["coc_current"] <= 1 or p["coc_best"] <= 1:
        raise ValueError("Cycles of concentration must exceed one")
    if not 0 <= p["blowdown_recovery"] <= 1:
        raise ValueError("Blowdown recovery must be between zero and one")
    evaporation = p["wue_base"] * (p["coc_current"] - 1) / p["coc_current"]
    gross_blowdown = evaporation / (p["coc_best"] - 1)
    recovered = gross_blowdown * p["blowdown_recovery"]
    discharge = gross_blowdown - recovered
    return dict(evaporation=evaporation, gross_blowdown=gross_blowdown,
                recovered=recovered, discharge=discharge,
                makeup=evaporation + discharge)


def wue_by_strategy(p):
    """WUE (m3 of make-up water per MWh_IT) for the four strategies.
    A1/A2 use the PUB benchmark (the heat balance at CoC~3 reproduces it).
    A3 is derived from the heat balance at high CoC with blowdown recovery.
    A4 is derived from weather trim hours plus the air-cooled remainder."""
    wue_evap = p["wue_base"]
    wue_a3 = tower_flows(p)["makeup"]
    f_trim = trim_hour_share(p)
    wue_a4 = (p["liquid_heat_share"] * f_trim * wue_evap
              + (1 - p["liquid_heat_share"]) * wue_evap)
    return {"A1": wue_evap, "A2": wue_evap, "A3": wue_a3, "A4": wue_a4}, f_trim


def dpue(p):
    """Heat-rejection PUE increment relative to common liquid-cooled IT + wet rejection."""
    return {"A1": 0.0, "A2": 0.0, "A3": 0.0, "A4": p["dpue_dry"]}


def tranches(p):
    """Capacity tranches (MW allocated, first year of operation) per scenario."""
    t = {"S1": [(p["cap_cfa2"], 2027)],
         "S2": [(p["cap_cfa2"], 2027), (p["cap_roadmap"], 2028)],
         "S3": [(p["cap_cfa2"], 2027), (p["cap_roadmap"], 2028), (p["cap_future_cfa"], 2029)]}
    return t


def commissioned_it_mw(p, scenario, year):
    """Installed IT capacity from each commissioning date, independent of load ramp."""
    return sum(mw * p["mw_basis_it_share"] for mw, start in tranches(p)[scenario] if year >= start)


def ramp(y, start, n):
    """Load factor of a tranche in year y (linear ramp over n years)."""
    k = y - start + 1
    if k <= 0:
        return 0.0
    return min(1.0, k / n)


def it_energy(p, scenario):
    """Annual IT energy (MWh_IT) by year for a scenario."""
    out = {}
    for y in YEARS:
        e = 0.0
        for mw, start in tranches(p)[scenario]:
            e += mw * p["mw_basis_it_share"] * p["util"] * ramp(y, start, p["ramp_years"]) * 8760
        out[y] = e
    return out


def demand(p):
    """Long table: scenario, strategy, year, mwh_it, wue, water_m3."""
    wue, f_trim = wue_by_strategy(p)
    rows = []
    for s in SCENARIOS:
        e = it_energy(p, s)
        for a in STRATEGIES:
            for y in YEARS:
                rows.append(dict(scenario=s, strategy=a, year=y, mwh_it=e[y],
                                 wue=wue[a], water_m3=e[y] * wue[a]))
    df = pd.DataFrame(rows)
    df.attrs["wue"] = wue
    df.attrs["trim_share"] = f_trim
    return df


# --------------------------------------------------------------------------
# Simplified LCA (answers Q3 carbon)
# --------------------------------------------------------------------------
def lca(p, grid="bau", year=None, residual_source=None):
    """Water-system GHG plus incremental heat-rejection GHG per MWh_IT.

    Common IT and liquid-cooling equipment are outside this partial boundary.
    These are not full-facility carbon footprints. If year is None an unweighted
    horizon-average grid EF is used; npc() accumulates year-specific results.
    """
    residual_source = residual_source or p.get("residual_source", "newater")
    if residual_source not in ("desal", "newater"):
        raise ValueError("residual_source must be desal or newater")
    wue, _ = wue_by_strategy(p)
    dp = dpue(p)
    ef_series = grid_ef(p, grid)
    ef = ef_series[year] if year else float(np.mean(list(ef_series.values())))
    # Optional explicit scenario. A policy share alone never creates a
    # zero-emissions credit; both a share and a nonnegative factor are required.
    green_share = p.get("dc_green_share_scenario", 0.0)
    green_ef = p.get("dc_green_ef_scenario", ef)
    if not 0 <= green_share <= 1 or green_ef < 0:
        raise ValueError("Explicit green pathway share/factor outside physical bounds")
    if green_share and "dc_green_ef_scenario" not in p:
        raise ValueError("A green pathway scenario requires an explicit emission factor")
    dc_ef = (1 - green_share) * ef + green_share * green_ef
    rows = []
    for a in STRATEGIES:
        source = "desal" if a == "A1" else ("newater" if a == "A2" else residual_source)
        sec = p["sec_desal"] if source == "desal" else p["sec_newater"]
        ghg_ne = p["ghg_desal_nonenergy"] if source == "desal" else p["ghg_newater_nonenergy"]
        kwh_prod = wue[a] * sec
        kwh_conv = wue[a] * p["sec_distrib"]
        recovered = tower_flows(p)["recovered"] if a == "A3" else 0.0
        kwh_onsite = recovered * p["sec_hicoc"]
        kwh_dc = dp[a] * 1000.0            # change in DC cooling electricity
        kwh_grid = kwh_prod + kwh_conv + kwh_onsite
        gwp_water = kwh_grid * ef
        gwp_dc_full = kwh_dc * ef
        gwp_dc_scenario = kwh_dc * dc_ef
        gwp_ne = wue[a] * ghg_ne
        rec = 1 / p["swro_recovery"] if source == "desal" else 1 / p["newater_recovery"]
        brine = wue[a] * (rec - 1)
        coc = p["coc_best"] if a == "A3" else p["coc_current"]
        # For A4 this assumes trim water follows the same tower mass balance;
        # a direct adiabatic pad would require a separate consumption model.
        discharge = tower_flows(p)["discharge"] if a == "A3" else wue[a] / coc
        rows.append(dict(
            strategy=a, source=source, wue=wue[a], ef_grid=ef, ef_dc=dc_ef,
            kwh_production=kwh_prod, kwh_conveyance=kwh_conv, kwh_onsite=kwh_onsite,
            kwh_dc_delta=kwh_dc, kwh_total=kwh_grid + kwh_dc,
            gwp_water_energy=gwp_water, gwp_nonenergy=gwp_ne,
            gwp_dc_delta=gwp_dc_scenario, gwp_dc_delta_nogreen=gwp_dc_full,
            gwp_total=gwp_water + gwp_ne + gwp_dc_scenario,
            gwp_total_nogreen=gwp_water + gwp_ne + gwp_dc_full,
            gwp_water_only=gwp_water + gwp_ne,
            brine_m3=brine, blowdown_discharge_m3=discharge,
            water_from_national_supply_m3=wue[a], recovered_blowdown_m3=recovered))
    return pd.DataFrame(rows).set_index("strategy")


# --------------------------------------------------------------------------
# LCC and environmental LCC (answers Q3 cost)
# --------------------------------------------------------------------------
def lcow(p, source, rate_pct=None):
    """Levelised cost of marginal water, SGD/m3, bottom-up (lecture eq. 6 form)."""
    r = p["disc_social"] if rate_pct is None else rate_pct
    capex = p["capex_desal"] if source == "desal" else p["capex_newater"]
    opex = p["opex_desal_nonenergy"] if source == "desal" else p["opex_newater_nonenergy"]
    sec = p["sec_desal"] if source == "desal" else p["sec_newater"]
    annual_m3_per_m3d = 365 * p["plant_cf"]
    cap_part = crf(r, p["life_plant"]) * capex / annual_m3_per_m3d
    energy_part = sec * p["price_elec_plant"]
    return dict(capital=cap_part, om=opex, energy=energy_part, total=cap_part + opex + energy_part)


def mwh_per_mw_year(p):
    return p["util"] * 8760


def lcc(p, L=None, grid="bau", residual_source=None):
    """Cost per MWh_IT for each strategy under the social and operator views,
    plus optional carbon-price-equivalent and eco-cost sensitivities.

    social_cost is the primary screening resource-cost result. The legacy
    elcc_*_tax columns are carbon-price equivalents, not additional tax cash
    flows: electricity prices can already contain carbon-tax pass-through.
    """
    if L is None:
        L = lca(p, grid, residual_source=residual_source)
    wue, _ = wue_by_strategy(p)
    dp = dpue(p)
    mwh_mw = mwh_per_mw_year(p)
    ct_avg = float(np.mean([carbon_price(p, y) for y in YEARS]))  # SGD/t
    eco = p["ecocost_gwp"] * p["fx_eur_sgd"]                        # SGD/kg
    rows = []
    for a in STRATEGIES:
        source = L.loc[a, "source"]
        lw = lcow(p, source)
        conv = p["sec_distrib"] * p["price_elec_plant"]
        # ---- social: resource costs
        water_cost = wue[a] * (lw["total"] + conv)
        onsite_cap = onsite_om = op_onsite_om = 0.0
        if a == "A3":
            onsite_cap = crf(p["disc_social"], p["life_dc_cooling"]) * p["capex_hicoc"] / mwh_mw
            onsite_om = L.loc[a, "kwh_onsite"] * p["price_elec_plant"]
            op_onsite_om = L.loc[a, "kwh_onsite"] * p["price_elec"]
        if a == "A4":
            onsite_cap = crf(p["disc_social"], p["life_dc_cooling"]) * p["capex_dry_premium"] / mwh_mw
        dc_energy = dp[a] * 1000 * p["price_elec_plant"]
        op_dc_energy = dp[a] * 1000 * p["price_elec"]
        discharge = L.loc[a, "blowdown_discharge_m3"] * p["cost_discharge_treatment"]
        social = water_cost + onsite_cap + onsite_om + dc_energy + discharge
        # ---- operator: tariffs and own capex at WACC
        tariff = p["tariff_potable_nd"] if source == "desal" else p["tariff_newater"]
        op_water = wue[a] * tariff
        op_cap = 0.0
        if a == "A3":
            op_cap = crf(p["disc_private"], p["life_dc_cooling"]) * p["capex_hicoc"] / mwh_mw
        if a == "A4":
            op_cap = crf(p["disc_private"], p["life_dc_cooling"]) * p["capex_dry_premium"] / mwh_mw
        operator = op_water + op_cap + op_onsite_om + op_dc_energy
        # ---- environmental LCC
        gwp = L.loc[a, "gwp_total"]
        rows.append(dict(
            strategy=a, lcow_source=lw["total"], water_cost_social=water_cost,
            onsite_capex=onsite_cap, onsite_energy=onsite_om, dc_energy_delta=dc_energy,
            discharge_cost=discharge, social_cost=social,
            operator_water=op_water, operator_capex=op_cap, operator_cost=operator,
            onsite_energy_operator=op_onsite_om, dc_energy_delta_operator=op_dc_energy,
            operator_onsite_energy=op_onsite_om, operator_dc_energy_delta=op_dc_energy,
            gwp_kg=gwp, carbon_tax_cost=gwp / 1000 * ct_avg,
            carbon_price_equivalent=gwp / 1000 * ct_avg, ecocost=gwp * eco,
            elcc_social_tax=social + gwp / 1000 * ct_avg,
            elcc_social_eco=social + gwp * eco,
            elcc_operator_tax=operator + gwp / 1000 * ct_avg))
    return pd.DataFrame(rows).set_index("strategy")


def npc(p, D=None, grid="bau", perspective="social", residual_source=None):
    """Net present cost (SGD) and discounted MWh_IT over 2027-2035 for every
    scenario x strategy, with year-specific grid EF and carbon price.

    On-site capital uses a fixed commissioned-capacity annuity from the first
    operating year, including low-load ramp years. This is equivalent to paying
    capital at commissioning and crediting the discounted remaining service
    annuities at the horizon: a service-value residual assumption, not a forecast
    resale price. Water infrastructure remains a purchased levelised service.
    """
    if D is None:
        D = demand(p)
    rate = p["disc_social"] if perspective == "social" else p["disc_private"]
    base_year = 2026
    rows = []
    for s in SCENARIOS:
        for a in STRATEGIES:
            pv_cost = pv_elcc = pv_mwh = tot_gwp = tot_water = 0.0
            for y in YEARS:
                L = lca(p, grid, year=y, residual_source=residual_source)
                C = lcc(p, L, grid)
                col = "social_cost" if perspective == "social" else "operator_cost"
                e = D[(D.scenario == s) & (D.strategy == a) & (D.year == y)]["mwh_it"].iloc[0]
                df = 1 / (1 + rate / 100) ** (y - base_year)
                cap_col = "onsite_capex" if perspective == "social" else "operator_capex"
                premium = p["capex_hicoc"] if a == "A3" else (p["capex_dry_premium"] if a == "A4" else 0.0)
                annual_cap = (commissioned_it_mw(p, s, y) * premium
                              * crf(rate, p["life_dc_cooling"]))
                cost = (C.loc[a, col] - C.loc[a, cap_col]) * e + annual_cap
                gwp = L.loc[a, "gwp_total"] * e           # kg
                tax = gwp / 1000 * carbon_price(p, y)
                pv_cost += cost * df
                pv_elcc += (cost + tax) * df
                pv_mwh += e * df
                tot_gwp += gwp
                tot_water += L.loc[a, "water_from_national_supply_m3"] * e
            rows.append(dict(scenario=s, strategy=a, perspective=perspective, grid=grid,
                             npc_sgd=pv_cost, npc_elcc_sgd=pv_elcc, pv_mwh=pv_mwh,
                             euac_per_mwh=pv_cost / pv_mwh, elcc_per_mwh=pv_elcc / pv_mwh,
                             total_gwp_t=tot_gwp / 1000, total_water_m3=tot_water,
                             capital_basis="commissioned_capacity_annuity_with_service_value_residual"))
    return pd.DataFrame(rows)


def pareto_efficient(costs, gwps):
    """Return boolean mask of non-dominated points (both less-is-better)."""
    costs, gwps = np.asarray(costs), np.asarray(gwps)
    eff = np.ones(len(costs), dtype=bool)
    for i in range(len(costs)):
        for j in range(len(costs)):
            if i != j and costs[j] <= costs[i] and gwps[j] <= gwps[i] and (costs[j] < costs[i] or gwps[j] < gwps[i]):
                eff[i] = False
    return eff
