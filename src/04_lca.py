"""
Step 4 - simplified LCA (research question Q3, carbon).

Functional unit: heat rejection for 1 MWh of IT energy in a new Singapore DC,
including the supply of all make-up water. Impact category: climate change
(GWP100). Electricity use is reported explicitly as in the lecture case studies.

Outputs: lca_inventory.csv, lca_by_grid.csv, lca_totals.csv
Figures: fig_lca_hotspots.png, fig_lca_grid_cases.png, fig_system_boundary.png
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import (load_params, demand, lca, grid_ef, GRIDS, GRID_NAME, STRATEGIES, SHORT, COLORS,
                   SCENARIOS, SCENARIO_NAME, YEARS, TAB)
import plotstyle as ps
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


def main():
    p = load_params()
    L = lca(p)
    L.to_csv(TAB / "lca_inventory.csv")

    rows = []
    for g in GRIDS:
        Lg = lca(p, g)
        for a in STRATEGIES:
            rows.append(dict(grid=g, strategy=a, ef_grid_avg=Lg.loc[a, "ef_grid"], gwp_total=Lg.loc[a, "gwp_total"],
                             gwp_water_only=Lg.loc[a, "gwp_water_only"], gwp_total_nogreen=Lg.loc[a, "gwp_total_nogreen"]))
    G = pd.DataFrame(rows); G.to_csv(TAB / "lca_by_grid.csv", index=False)

    # horizon totals (t CO2e) with year-specific EF, by scenario
    D = demand(p)
    tot = []
    for g in GRIDS:
        for s in SCENARIOS:
            for a in STRATEGIES:
                t = tw = 0.0
                for y in YEARS:
                    Ly = lca(p, g, year=y)
                    e = D[(D.scenario == s) & (D.strategy == a) & (D.year == y)].mwh_it.iloc[0]
                    t += Ly.loc[a, "gwp_total"] * e / 1000
                    tw += Ly.loc[a, "gwp_water_only"] * e / 1000
                tot.append(dict(grid=g, scenario=s, strategy=a, gwp_2027_35_t=t, gwp_water_only_t=tw))
    T = pd.DataFrame(tot); T.to_csv(TAB / "lca_totals.csv", index=False)

    # ---- Figure: hotspot (contribution) chart per MWh_IT
    parts = [("gwp_water_energy", "Electricity: water production, conveyance and on-site recovery", "#4a90c4"),
             ("gwp_nonenergy", "Water-system embodied emissions and chemicals", "#8c8c8c"),
             ("gwp_dc_delta", "Additional dry-rejection electricity (full grid factor)", "#c1443c")]
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    fig.subplots_adjust(left=0.11, right=0.98, top=0.87, bottom=0.35)
    x = np.arange(len(STRATEGIES))
    pos = np.zeros(4); neg = np.zeros(4)
    for col, lab, c in parts:
        v = L[col].values
        bottom = np.where(v >= 0, pos, neg)
        ax.bar(x, v, bottom=bottom, color=c, width=0.6, label=lab, edgecolor="white", linewidth=1)
        pos += np.where(v >= 0, v, 0); neg += np.where(v < 0, v, 0)
    for i, a in enumerate(STRATEGIES):
        ax.text(i, pos[i] + 0.45, f"{L.loc[a,'gwp_total']:.2f}", ha="center", fontsize=9, fontweight="bold")
    ax.axhline(0, color="#333", lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels([ps.TICK[a] for a in STRATEGIES]); ax.margins(y=0.18)
    ax.tick_params(labelsize=9)
    ax.set_ylabel("Modelled kg CO₂e/MWh IT", fontsize=9)
    fig.legend(*ax.get_legend_handles_labels(), fontsize=8.5, loc="lower center", bbox_to_anchor=(0.52, 0.015))
    ax.set_title(f"Modelled emissions by component (grid EF {L.ef_grid.iloc[0]:.3f} kg/kWh)", fontsize=10)
    ps.save(fig, "fig_lca_hotspots")

    # ---- Figure: water-only GWP under the three grid cases + the energy effect
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    w = 0.25
    for k, g in enumerate(GRIDS):
        d = G[G.grid == g].set_index("strategy")
        axes[0].bar(x + (k - 1) * w, d.gwp_water_only, width=w, color=["#9ecae1", "#4292c6", "#08306b"][k], label=GRID_NAME[g])
        axes[1].bar(x + (k - 1) * w, d.gwp_total, width=w, color=["#9ecae1", "#4292c6", "#08306b"][k], label=GRID_NAME[g])
    for ax, t in zip(axes, ["Water-related components", "Including additional dry-rejection electricity"]):
        ax.set_xticks(x); ax.set_xticklabels([ps.TICK[a] for a in STRATEGIES]); ax.set_title(t, fontsize=9.5); ax.axhline(0, color="#333", lw=0.8)
    axes[0].set_ylabel("kg CO₂e per MWh_IT"); axes[0].legend(fontsize=8)
    ps.save(fig, "fig_lca_grid_cases")

    # ---- Figure: system boundary diagram
    fig, ax = plt.subplots(figsize=(6.8, 4.9))
    fig.subplots_adjust(left=0.015, right=0.985, bottom=0.05, top=0.98)
    ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1.02)
    def box(x, y, w, h, text, fc, ec="#333", fs=8.5, bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012", fc=fc, ec=ec, lw=1))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
                fontweight="bold" if bold else None)
    def arrow(x1, y1, x2, y2, color="#333"):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                    mutation_scale=11, color=color, lw=1.1))
    for x, w, fc, ec in [(0.02, 0.44, "#f3f7fb", "#4a90c4"),
                         (0.50, 0.48, "#fdf6ee", "#e69f00")]:
        ax.add_patch(FancyBboxPatch((x, 0.14), w, 0.64, boxstyle="round,pad=0.01",
                                   fc=fc, ec=ec, lw=1.4, ls="--"))
    ax.text(0.24, 0.825, "National water supply", ha="center", fontsize=9.5,
            color="#2b5c8a", fontweight="bold")
    ax.text(0.74, 0.825, "Data-centre heat rejection", ha="center", fontsize=9.5,
            color="#9a6400", fontweight="bold")
    box(0.08, 0.91, 0.84, 0.075, "Grid electricity\nProduction, conveyance, recovery and dry rejection", "#e8e8e8", bold=True)
    box(0.04, 0.57, 0.21, 0.16, "A1 Desalination\nSeawater RO", "#dbe9f6")
    box(0.04, 0.32, 0.21, 0.18, "A2–A4 NEWater\nSecondary effluent\nMF / RO / UV", "#dbe9f6")
    box(0.30, 0.43, 0.13, 0.16, "Conveyance\nto island", "#eef3f8")
    box(0.54, 0.52, 0.22, 0.21, "Heat rejection\nA1/A2  CoC 3\nA3  CoC 8\nA4  Dry + trim", "#fbe9c9")
    box(0.81, 0.54, 0.14, 0.15, "1 MWh IT\nCommon\nliquid loop", "#eee")
    box(0.54, 0.22, 0.22, 0.13, "A3 treatment\nand recovery", "#fbe9c9")
    box(0.81, 0.22, 0.14, 0.13, "Residual\nblowdown", "#f2f2f2")
    arrow(0.25, 0.64, 0.30, 0.55)
    arrow(0.25, 0.42, 0.30, 0.47)
    arrow(0.43, 0.52, 0.54, 0.59)
    ax.text(0.475, 0.625, "Make-up\nwater", ha="center", fontsize=8.5,
            bbox=dict(fc="white", ec="none", pad=1))
    arrow(0.81, 0.61, 0.76, 0.61)
    ax.text(0.795, 0.49, "Heat", ha="center", fontsize=8.5)
    arrow(0.60, 0.52, 0.60, 0.35)
    ax.text(0.555, 0.42, "Gross\nblowdown", ha="center", fontsize=8.5)
    arrow(0.71, 0.35, 0.71, 0.52, "#2a9d8f")
    ax.text(0.765, 0.42, "Recovered\nwater", ha="center", fontsize=8.5, color="#247a70")
    arrow(0.76, 0.285, 0.81, 0.285)
    arrow(0.08, 0.91, 0.04, 0.79, "#777")
    arrow(0.92, 0.91, 0.96, 0.79, "#777")
    ax.text(0.50, 0.065, "Excluded: common IT, building and liquid-cooling components; upstream wastewater\ntreatment, differential cooling-equipment embodied emissions and end of life.",
            ha="center", va="center", fontsize=8.5, color="#555")
    ps.save(fig, "fig_system_boundary")

    print(L[["wue", "kwh_total", "gwp_water_only", "gwp_dc_delta", "gwp_total", "brine_m3"]].round(3))
    print(T[T.grid == "bau"].pivot(index="scenario", columns="strategy", values="gwp_2027_35_t").round(0))


if __name__ == "__main__":
    main()
