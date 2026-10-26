"""
Step 3 - demand model (research questions Q1 and Q2).

How much extra cooling water does new DC capacity need, 2027-2035, and how
much of it can be avoided by demand-side measures?

Outputs (outputs/tables): demand_annual.csv, demand_summary.csv, wue_derivation.csv
Figures (outputs/figures): fig_demand_fan.png, fig_wue_ladder.png, fig_weather_trim.png
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import (load_params, demand, wue_heat_balance, trim_hour_share, SCENARIOS, STRATEGIES,
                   SCENARIO_NAME, SHORT, COLORS, YEARS, TAB, PROC)
import plotstyle as ps
import matplotlib.pyplot as plt


def main():
    TAB.mkdir(parents=True, exist_ok=True)
    p = load_params()
    D = demand(p)
    D.to_csv(TAB / "demand_annual.csv", index=False)

    # ---- summary per scenario x strategy: 2035 demand and 2027-35 cumulative
    summ = (D.groupby(["scenario", "strategy"])
              .agg(water_2035_m3=("water_m3", lambda s: s.iloc[-1]),
                   water_cum_m3=("water_m3", "sum"),
                   mwh_it_2035=("mwh_it", lambda s: s.iloc[-1]),
                   wue=("wue", "first")).reset_index())
    base = summ[summ.strategy == "A1"].set_index("scenario")["water_2035_m3"]
    summ["avoided_vs_A1_2035_m3"] = summ.apply(lambda r: base[r.scenario] - r.water_2035_m3, axis=1)
    summ["avoided_share"] = summ["avoided_vs_A1_2035_m3"] / summ.scenario.map(base)
    nat = pd.read_csv(PROC / "water_sales.csv")
    nat_total = nat[(nat.year == nat.year.max()) & nat.series.isin(["Sales Of Potable Water", "Sales Of Newater"])]["million_m3"].sum() * 1e6
    summ["share_of_national_sales_2025"] = summ["water_2035_m3"] / nat_total
    summ["m3_per_day_2035"] = summ["water_2035_m3"] / 365
    summ.to_csv(TAB / "demand_summary.csv", index=False)

    # ---- WUE derivation table (how each strategy's WUE was obtained)
    wue = D.attrs["wue"]
    f_trim = D.attrs["trim_share"]
    hb3, evap = wue_heat_balance(p, p["coc_current"])
    hb8, _ = wue_heat_balance(p, p["coc_best"])
    der = pd.DataFrame([
        dict(item="Heat-balance evaporation only", value=round(evap, 3), basis="3.6/L x heat-reject factor x evaporative fraction"),
        dict(item=f"Heat-balance WUE at CoC {p['coc_current']:.0f}", value=round(hb3, 3), basis="evaporation x CoC/(CoC-1)"),
        dict(item="PUB benchmark median (used for A1, A2)", value=wue["A1"], basis="PUB Sectoral Water Efficiency Benchmark, Dec 2025"),
        dict(item=f"Calibrated WUE at CoC {p['coc_best']:.0f} (before recovery)", value=round(hb8 * wue['A1'] / hb3, 3), basis="heat-balance curve scaled to benchmark; not independent validation"),
        dict(item="A3 WUE: high CoC + blowdown recovery", value=round(wue["A3"], 3), basis=f"{p['blowdown_recovery']:.0%} of remaining blowdown recovered; scaled to PUB median"),
        dict(item="Share of hours needing adiabatic trim (A4)", value=round(f_trim, 4), basis=f"Open-Meteo hourly data, Jurong Island 2015-2025, dry-bulb > {p['trim_threshold']:.0f} C"),
        dict(item="A4 WUE: dry rejection with wet assistance", value=round(wue["A4"], 3), basis=f"{p['liquid_heat_share']:.0%} of heat uses dry loop with trim; remainder uses towers; all strategies share liquid-cooled IT"),
        dict(item="LBNL (2024), other cooling configurations", value="0.1-0.3", basis="p.47: airside economizer/adiabatic systems with air-cooled chillers; not validation of tropical A4"),
        dict(item="IMDA (2021) median / Roadmap target", value="2.2 / 2.0", basis="Green DC Roadmap 2024"),
    ])
    der.to_csv(TAB / "wue_derivation.csv", index=False)

    # ---- Figure: demand fan (S1-S3) for A1 vs A3 vs A4
    fig, axes = plt.subplots(1, 3, figsize=(6.8, 3.2), sharey=True)
    fig.subplots_adjust(left=0.105, right=0.985, bottom=0.27, top=0.80, wspace=0.19)
    panel_titles = {"S1": "S1  200 MW IT", "S2": "S2  500 MW IT", "S3": "S3  700 MW IT"}
    legend_labels = {"A1": f"A1/A2 Wet ({wue['A1']:.2f})", "A3": f"A3 Reuse ({wue['A3']:.2f})",
                     "A4": f"A4 Dry + trim ({wue['A4']:.2f})"}
    for ax, s in zip(axes, SCENARIOS):
        for a in STRATEGIES:
            d = D[(D.scenario == s) & (D.strategy == a)]
            if a == "A2":
                continue  # same water as A1
            ax.plot(d.year, d.water_m3 / 1e6, color=COLORS[a], lw=2, label=legend_labels[a])
            ax.annotate(f"{d.water_m3.iloc[-1]/1e6:.2f}", (2035, d.water_m3.iloc[-1] / 1e6), xytext=(4, 0), textcoords="offset points", fontsize=8.5, color=COLORS[a], va="center")
        ax.set_title(panel_titles[s], fontsize=9.5, pad=9)
        ax.set_xticks([2027, 2031, 2035]); ax.set_xlim(2027, 2037.2)
        ax.tick_params(labelsize=8.5)
    axes[0].set_ylabel("Water supplied\nmillion m³/year", fontsize=9)
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", bbox_to_anchor=(0.53, 0.07),
               fontsize=8.5, ncol=3, handlelength=1.8, columnspacing=1.2)
    fig.text(0.53, 0.035, "Legend values are WUE in m³/MWh IT. S2 and S3 are hypothetical growth cases.",
             ha="center", fontsize=8.5, color="#555")
    fig.suptitle("Cooling-water demand from 2027 to 2035", fontsize=11, fontweight="bold", y=0.98)
    ps.save(fig, "fig_demand_fan")

    # ---- Figure: WUE ladder (CoC curve + strategies)
    cocs = np.linspace(2, 12, 50)
    curve = [wue_heat_balance(p, c)[0] * wue["A1"] / hb3 for c in cocs]
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.plot(cocs, curve, color="#444", lw=2, label="Heat-balance WUE, evaporative towers (calibrated)")
    ax.hlines(wue['A1'], 2, 12, color=COLORS["A1"], ls="--", lw=1.2); ax.text(12.2, wue['A1'], f"Benchmark {wue['A1']:.1f} (A1, A2)", va="center", fontsize=8, color=COLORS["A1"])
    ax.hlines(2.0, 2, 12, color="#999", ls=":", lw=1); ax.text(12.2, 1.9, "Roadmap target 2.0", va="center", fontsize=8, color="#666")
    ax.hlines(wue["A3"], 2, 12, color=COLORS["A3"], ls="--", lw=1.2); ax.text(12.2, wue["A3"], f"A3 with reuse {wue['A3']:.2f}", va="center", fontsize=8, color=COLORS["A3"])
    ax.hlines(wue["A4"], 2, 12, color=COLORS["A4"], ls="--", lw=1.2); ax.text(12.2, wue["A4"], f"A4 dry + trim {wue['A4']:.2f}", va="center", fontsize=8, color=COLORS["A4"])
    ax.scatter([p["coc_current"], p["coc_best"]], [wue["A1"], hb8 * wue["A1"] / hb3], color="#444", zorder=5, s=25)
    ax.annotate(f"CoC {p['coc_best']:.0f} alone: {hb8*wue['A1']/hb3:.2f}", (p["coc_best"], hb8 * wue["A1"] / hb3), xytext=(0, 10), textcoords="offset points", fontsize=8, ha="center")
    ax.set_xlabel("Cycles of concentration (CoC)"); ax.set_ylabel("WUE, m³ per MWh of IT energy")
    ax.set_xlim(2, 16.5); ax.set_ylim(0, 3.5); ax.set_xticks(range(2, 13, 2)); ax.legend(loc="upper right", fontsize=8)
    ax.set_title("Where each strategy sits on the water-efficiency ladder")
    ps.save(fig, "fig_wue_ladder")

    # ---- Figure: weather, hours above thresholds by month
    clim = pd.read_csv(PROC / "weather_climatology.csv")
    fig, ax = plt.subplots(figsize=(6.2, 3.2))
    for thr, c in zip([27, 30, 32], ["#9ecae1", "#4292c6", "#08519c"]):
        ax.bar(clim.month, clim[f"hrs_tdb_gt_{thr}"], color=c, width=0.8, label=f"hours with dry-bulb > {thr} °C", alpha=0.95 if thr > 27 else 0.8)
    ax.set_xticks(range(1, 13)); ax.set_xticklabels("JFMAMJJASOND")
    ax.set_ylabel("Hours per month (2015-2025 mean)"); ax.legend(fontsize=8)
    ax.set_title(f"Weather-based trim proxy: >{p['trim_threshold']:.0f} °C for {f_trim:.1%} of recorded hours")
    ps.save(fig, "fig_weather_trim")

    print(summ.round(3).to_string(index=False))
    print(der.to_string(index=False))


if __name__ == "__main__":
    main()
