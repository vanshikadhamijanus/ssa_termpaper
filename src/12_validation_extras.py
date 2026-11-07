"""
Step 12 - validation checks added for the final report (November 2026).

Four checks that sit outside the main pipeline but use the same model code:

1. Weather: compare the Open-Meteo gridded record used for the A4 trim share
   with the SingStat monthly station series already held in data/raw.
2. A4 under warmer conditions: rerun the model with the trim threshold lowered
   by the measured bias, which is equivalent to warming every archived hour by
   that amount, and with the register's 27 and 32 degC bounds.
3. AHP scoring rule: rerun the five weighting scenarios with the ratio
   (inverse-proportional) rule for measured criteria instead of the linear
   distance-from-worst rule, and record whether first place changes.
4. Calibration against validation: one table that separates benchmark
   calibration from comparisons with independent references.

Outputs (outputs/tables): validation_weather.csv, validation_a4_weather.csv,
validation_ahp_scoring.csv, validation_summary.csv
Figure (outputs/figures): fig_tornado_cost_top5.png (five largest cost drivers)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import (load_params, load_assumptions, lca, lcc, lcow, wue_by_strategy, mwh_per_mw_year,
                   wue_heat_balance, it_energy, STRATEGIES, SHORT, COLORS, TAB, ROOT)
import ahp as H
import plotstyle as ps
import matplotlib.pyplot as plt

RAW = ROOT / "data" / "raw"
STATION_FILE = RAW / "datagovsg" / "singstat_climate_monthly.csv"
HOURLY_FILE = RAW / "weather" / "openmeteo_jurong_island_hourly_2015_2025.csv"


# ---------------------------------------------------------------- 1. weather
def station_series(name):
    ss = pd.read_csv(STATION_FILE)
    ss["DataSeries"] = ss["DataSeries"].str.strip()
    row = ss[ss["DataSeries"] == name].iloc[0].drop("DataSeries")
    row = pd.to_numeric(row, errors="coerce")
    row.index = pd.to_datetime(row.index, format="%Y%b", errors="coerce")
    row = row[~row.index.isna()]
    row = row[~row.index.duplicated()]
    return row.dropna().sort_index()


def weather_check():
    hourly = pd.read_csv(HOURLY_FILE, parse_dates=["time"]).set_index("time")["temperature_2m"]
    daily = hourly.resample("D").agg(["max", "min"])
    om_mid = ((daily["max"] + daily["min"]) / 2).resample("MS").mean().rename("openmeteo_midrange")
    om_max = daily["max"].resample("MS").mean().rename("openmeteo_daily_max")
    ss_max = station_series("Air Temperature Means Daily Maximum")
    ss_min = station_series("Air Temperature Means Daily Minimum")
    ss_mid = ((ss_max + ss_min) / 2).rename("station_midrange")
    both = pd.concat([om_mid, om_max, ss_mid, ss_max.rename("station_daily_max")], axis=1, sort=True).dropna()
    both = both[(both.index.year >= 2015) & (both.index.year <= 2025)]
    diff = both.openmeteo_midrange - both.station_midrange
    rows = [
        ("months_compared", len(both), "2015-2025 months present in both series"),
        ("bias_midrange_degC", diff.mean(), "Open-Meteo minus station, monthly mean of daily (max+min)/2"),
        ("rmse_midrange_degC", float(np.sqrt((diff ** 2).mean())), "root mean square of the monthly differences"),
        ("max_abs_diff_degC", diff.abs().max(), "largest monthly difference"),
        ("correlation", both.openmeteo_midrange.corr(both.station_midrange), "month-to-month agreement"),
        ("openmeteo_mean_daily_max_degC", both.openmeteo_daily_max.mean(), "mean of daily maxima, Open-Meteo"),
        ("station_mean_daily_max_degC", both.station_daily_max.mean(), "mean of daily maxima, SingStat station"),
        ("station_note", "SingStat monthly climate series (data.gov.sg d_1744ca68dc7ed37221b17c441042405e). Dataset footnote: "
                         "'With effect from January 1984, data are from designated climate station located at Changi, Singapore.'",
         "cross-location comparison (Changi station against a Jurong Island grid cell), not a measured Jurong bias"),
    ]
    table = pd.DataFrame(rows, columns=["metric", "value", "note"])
    table.to_csv(TAB / "validation_weather.csv", index=False)
    return table, float(diff.mean())


# ---------------------------------------------------------------- 2. A4 cases
def a4_weather_cases(p0, bias):
    """Lowering the threshold by b degC equals warming every archived hour by b."""
    base_thr = p0["trim_threshold"]
    e2035 = it_energy(p0, "S1")[2035]
    cases = [("Base (30 degC threshold, record as archived)", base_thr),
             ("Record warmed by 0.5 degC", base_thr - 0.5),
             ("Record warmed by 1.0 degC", base_thr - 1.0),
             (f"Hypothetical warming by the cross-location difference ({abs(bias):.2f} degC)", base_thr - abs(bias)),
             ("Register low bound: 27 degC threshold", 27.0),
             ("Register high bound: 32 degC threshold", 32.0)]
    rows = []
    for name, thr in cases:
        p = {**p0, "trim_threshold": thr}
        wue, share = wue_by_strategy(p)
        L, C = lca(p), lcc(p)
        rows.append(dict(case=name, equivalent_threshold_degC=thr, trim_hour_share=share,
                         a4_wue_m3_per_mwh=wue["A4"],
                         a4_from_wet_remainder=(1 - p["liquid_heat_share"]) * p["wue_base"],
                         a4_from_hot_hour_trim=p["liquid_heat_share"] * share * p["wue_base"],
                         a4_water_saving_vs_A2=1 - wue["A4"] / wue["A2"],
                         a4_water_2035_S1_Mm3=e2035 * wue["A4"] / 1e6,
                         a4_gwp_kg_per_mwh=L.loc["A4", "gwp_total"],
                         a4_resource_cost_sgd_per_mwh=C.loc["A4", "social_cost"]))
    table = pd.DataFrame(rows)
    table.to_csv(TAB / "validation_a4_weather.csv", index=False)
    return table


# ---------------------------------------------------------------- 3. AHP rule
def inverse_proportional(x):
    """Ratio scale for a less-is-better measured criterion: priority ~ 1/x."""
    s = 1.0 / np.asarray(x, dtype=float)
    return s / s.sum()


def ahp_scoring_rule(p0):
    L = lca(p0)
    C = lcc(p0, L)
    q = H.quantitative_values(L, C)
    v, _ = H.sub_weights()
    rules = {"Linear distance from worst, floor 0.10 (report base)": lambda x: H.less_is_better(x, 0.10),
             "Inverse proportional (ratio) scoring": inverse_proportional}
    rows, leaf_rows = [], []
    for rule, scorer in rules.items():
        W = {}
        for cr, leaves in H.SUB.items():
            cols = []
            for leaf in leaves:
                if leaf in q:
                    pri = scorer(q[leaf])
                    cols.append(pri)
                    for a, val in zip(STRATEGIES, pri):
                        leaf_rows.append(dict(rule=rule, leaf=leaf, strategy=a, local_priority=val))
                else:
                    cols.append(H.AHPmat(H.pairwise(H.QUAL_PAIRWISE[leaf][0]))[0])
            W[cr] = np.array(cols).T
        for sc in H.WEIGHT_SCENARIOS:
            u, _ = H.main_weights(sc)
            g = H.global_scores(W, v, u)
            order = [STRATEGIES[i] for i in np.argsort(-g)]
            gap = float(np.sort(g)[-1] - np.sort(g)[-2])
            rows.append(dict(rule=rule, weight_scenario=sc, **{a: g[k] for k, a in enumerate(STRATEGIES)},
                             first=order[0], second=order[1], first_minus_second=gap,
                             tie_within_0_005=gap < 0.005))
    table = pd.DataFrame(rows)
    table.to_csv(TAB / "validation_ahp_scoring.csv", index=False)
    pd.DataFrame(leaf_rows).to_csv(TAB / "validation_ahp_scoring_leaves.csv", index=False)
    return table


# ---------------------------------------------------------------- 3b. cycles vs recovery
def cycles_versus_recovery(p0):
    """How much of A3's saving comes from running at higher cycles alone.

    The comparator keeps the same side-stream treatment capital as A3, because
    the register bundles treatment and recovery in one allowance; only the
    recovered flow and its treatment electricity are removed.
    """
    rows = []
    for name, override in [("A2: ordinary towers, 3 cycles", None),
                           ("Towers at 8 cycles, no recovery (same treatment capex as A3)", {"blowdown_recovery": 0.0}),
                           ("A3: towers at 8 cycles with 70% recovery", {})]:
        p = {**p0, **(override or {})}
        L, C = lca(p), lcc(p)
        a = "A2" if override is None else "A3"
        rows.append(dict(configuration=name, wue_m3_per_mwh=L.loc[a, "wue"], gwp_kg_per_mwh=L.loc[a, "gwp_total"],
                         resource_cost_sgd_per_mwh=C.loc[a, "social_cost"], operator_cost_sgd_per_mwh=C.loc[a, "operator_cost"]))
    table = pd.DataFrame(rows)
    base, mid, full = table.wue_m3_per_mwh
    table["share_of_A3_water_saving"] = [0.0, (base - mid) / (base - full), 1.0]
    table.to_csv(TAB / "validation_cycles_vs_recovery.csv", index=False)
    return table


def maintenance_breakeven(p0):
    """Operating cost per MW-year that would remove A3's operator saving.

    The model omits incremental maintenance, chemicals and membrane
    replacement for the recovery unit. This is a break-even allowance, not an
    estimate of those costs.
    """
    C = lcc(p0)
    advantage = C.loc["A2", "operator_cost"] - C.loc["A3", "operator_cost"]
    mwh = mwh_per_mw_year(p0)
    social_gap = C.loc["A3", "social_cost"] - C.loc["A2", "social_cost"]
    table = pd.DataFrame([
        dict(quantity="A3 operator saving against A2", value=advantage, unit="SGD per MWh IT"),
        dict(quantity="Annual IT energy per MW at base utilisation", value=mwh, unit="MWh per MW-year"),
        dict(quantity="Omitted operating cost that removes the saving", value=advantage * mwh, unit="SGD per MW IT-year"),
        dict(quantity="Same allowance as a share of the assumed recovery capex", value=advantage * mwh / p0["capex_hicoc"], unit="fraction per year"),
        dict(quantity="A3 resource-cost premium against A2 (society already pays more)", value=social_gap, unit="SGD per MWh IT"),
    ])
    table.to_csv(TAB / "validation_maintenance_breakeven.csv", index=False)
    return table


def run_unit_tests():
    """Run the test suite now and record the dated result used in Table S10."""
    import re
    import subprocess
    from datetime import datetime
    proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                          cwd=ROOT, capture_output=True, text=True)
    out = proc.stdout + proc.stderr
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    ran = int(m.group(1)) if (m := re.search(r"Ran (\d+) tests?", out)) else 0
    failed = sum(int(v) for v in re.findall(r"(?:failures|errors)=(\d+)", out))
    summary = dict(run_time=stamp, tests_run=ran, failures=failed, errors=0, ok=proc.returncode == 0 and ran > 0)
    (ROOT / "outputs/validation").mkdir(exist_ok=True)
    (ROOT / "outputs/validation/unit_tests.txt").write_text(f"run_time: {stamp}\n" + out)
    pd.DataFrame([summary]).to_csv(TAB / "validation_unit_tests.csv", index=False)
    return summary


# ---------------------------------------------------------------- 4. summary
def calibration_table(p0, weather_bias, tests):
    import json
    receipt = ROOT / "outputs/validation/checks.json"
    max_diff = "not yet checked"
    if receipt.exists():
        diffs = [c["details"].get("max_absolute_difference") for c in json.loads(receipt.read_text())["checks"]
                 if isinstance(c.get("details"), dict) and "max_absolute_difference" in c["details"]]
        if diffs:
            max_diff = f"{max(diffs):.1e}" if max(diffs) else "0"
    hb3, _ = wue_heat_balance(p0, p0["coc_current"])
    lw_d, lw_n = lcow(p0, "desal")["total"], lcow(p0, "newater")["total"]
    rows = [
        dict(component="Wet-tower water use (A1, A2)", kind="Calibration",
             model_value=f"{hb3:.2f} m3/MWh from the heat balance before scaling",
             reference=f"PUB sector benchmark {p0['wue_base']:.2f} m3/MWh",
             difference=f"{(hb3 / p0['wue_base'] - 1) * 100:+.0f}% before scaling; scaled to the benchmark",
             reading="The benchmark sets the curve, so it cannot also validate it"),
        dict(component="Levelised cost of desalinated water", kind="Independent context",
             model_value=f"S${lw_d:.2f}/m3 bottom-up",
             reference=f"S${p0['ppp_price_desal']:.2f}/m3 Keppel Marina East first-year price",
             difference=f"{(lw_d / p0['ppp_price_desal'] - 1) * 100:+.0f}%",
             reading="Different year, financing and scope; agreement in magnitude only"),
        dict(component="Levelised cost of NEWater", kind="Independent context",
             model_value=f"S${lw_n:.2f}/m3 bottom-up",
             reference=f"S${p0['ppp_price_newater']:.2f}/m3 Changi and Sembcorp first-year prices",
             difference=f"{(lw_n / p0['ppp_price_newater'] - 1) * 100:+.0f}%",
             reading="Model is higher; the gap is reported, not corrected"),
        dict(component="Hourly weather for the A4 trim share", kind="Independent record, different location",
             model_value="Open-Meteo gridded record, Jurong Island",
             reference="SingStat monthly series, Changi climate station",
             difference=f"{weather_bias:+.2f} degC monthly midrange; gridded record is cooler",
             reading="Cross-location discrepancy; used as a hypothetical warming case for A4"),
        dict(component="Grid emission factor", kind="Input, not validated",
             model_value="0.404 kg CO2/kWh in 2025, linear to 0.38 in 2035",
             reference="EMA Singapore Energy Statistics 2026, Table 2.3",
             difference="2025 value used directly; 2035 endpoint is a team assumption",
             reading="No back-test is possible for a future path"),
        dict(component="Arithmetic and AHP mathematics", kind="Internal check",
             model_value=f"Saved tables against fresh model calls; {tests['tests_run']} unit tests run {tests['run_time'][:10]}",
             reference="Independent eigenvector calculation; mass and energy balances",
             difference=f"Maximum absolute difference {max_diff} (saved tables versus fresh calls); " + ("all tests pass" if tests["ok"] else f"{tests['failures'] + tests['errors']} tests fail"),
             reading="Shows consistency, not the truth of any assumption"),
    ]
    table = pd.DataFrame(rows)
    table.to_csv(TAB / "validation_summary.csv", index=False)
    return table


# ---------------------------------------------------------------- figure 10
LABELS = {
    "sec_desal": "Desalination energy", "price_elec_plant": "Plant electricity price",
    "capex_desal": "Desalination capex", "opex_desal_nonenergy": "Desal. O&M", "wue_base": "Baseline WUE",
    "opex_newater_nonenergy": "NEWater O&M", "capex_newater": "NEWater capex", "sec_newater": "NEWater energy",
    "disc_social": "Social discount rate", "capex_hicoc": "Recovery capex", "life_dc_cooling": "Cooling equipment life",
    "util": "Utilisation", "dpue_dry": "Dry-cooling extra PUE", "capex_dry_premium": "Dry-cooling capex premium",
    "sec_distrib": "Conveyance energy", "sec_hicoc": "Recovery treatment energy", "life_plant": "Water-plant life",
    "plant_cf": "Plant capacity factor", "blowdown_recovery": "Blowdown recovery share", "coc_best": "High cycles",
    "coc_current": "Typical cycles", "trim_threshold": "Trim threshold", "liquid_heat_share": "Dry-loop heat share",
    "price_elec": "Operator electricity price", "disc_private": "Operator discount rate",
}


def tornado_top5():
    T = pd.read_csv(TAB / "tornado.csv")
    fig, axes = plt.subplots(2, 2, figsize=(8.2, 5.6))
    for ax, a in zip(axes.ravel(), STRATEGIES):
        d = T[(T.strategy == a) & (T.cost_swing > 1e-9)].nlargest(5, "cost_swing").iloc[::-1]
        base = d.cost_base.iloc[0]
        y = np.arange(len(d))
        ax.barh(y, d.cost_low - base, color="#9ecae1", label="input at low value")
        ax.barh(y, d.cost_high - base, color="#2b5c8a", label="input at high value")
        ax.set_yticks(y)
        ax.set_yticklabels([LABELS.get(k, k) for k in d.param], fontsize=9)
        ax.axvline(0, color="#333", lw=.8)
        ax.set_title(f"{a} {SHORT[a]}  (base S$ {base:.2f})", fontsize=10, color=COLORS[a])
        ax.grid(axis="y", visible=False)
    for ax in axes[1]:
        ax.set_xlabel("change in S$ per MWh IT", fontsize=9)
    fig.legend(*axes[0, 0].get_legend_handles_labels(), ncol=2, loc="lower center", bbox_to_anchor=(.5, -.03), fontsize=9)
    fig.tight_layout(rect=(0, .04, 1, 1))
    ps.save(fig, "fig_tornado_cost_top5")


def main():
    p = load_params()
    weather, bias = weather_check()
    print(weather.to_string(index=False))
    print(a4_weather_cases(p, bias).round(4).to_string(index=False))
    print(ahp_scoring_rule(p).round(3).to_string(index=False))
    print(cycles_versus_recovery(p).round(4).to_string(index=False))
    print(maintenance_breakeven(p).round(4).to_string(index=False))
    tests = run_unit_tests()
    print(tests)
    print(calibration_table(p, bias, tests).to_string(index=False))
    tornado_top5()


if __name__ == "__main__":
    main()
