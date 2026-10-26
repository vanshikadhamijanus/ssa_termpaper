"""
Step 5 - life cycle costing and environmental LCC (research question Q3, cost).

Follows the LCC lecture: levelised cost (eq. 6 form), NPC / EUAC with the
capital recovery factor, two perspectives (social 3 %, operator WACC 8 %),
monetised GHG using the carbon tax path and eco-costs (both discounted), and
the cost-vs-carbon efficient frontier with dominance analysis.

Outputs: lcc_per_mwh.csv, lcow.csv, npc_by_scenario.csv, frontier.csv
Figures: fig_lcc_stack.png, fig_frontier.png, fig_lcow_check.png
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import (load_params, demand, lca, lcc, lcow, npc, pareto_efficient, STRATEGIES, SHORT, COLORS,
                   SCENARIOS, SCENARIO_NAME, TAB)
import plotstyle as ps
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def main():
    p = load_params()
    L = lca(p)
    C = lcc(p, L)
    C.to_csv(TAB / "lcc_per_mwh.csv")

    # LCOW: bottom-up vs top-down check
    rows = []
    for src, ppp, lab in [("desal", p["ppp_price_desal"], "Keppel Marina East PPP first-year price (2020)"),
                          ("newater", p["ppp_price_newater"], "Changi/Sembcorp NEWater PPP first-year price")]:
        lw = lcow(p, src)
        rows.append(dict(source=src, capital=lw["capital"], om=lw["om"], energy=lw["energy"], bottom_up_total=lw["total"],
                         top_down_ppp=ppp, top_down_note=lab,
                         user_price=p["tariff_potable_nd"] if src == "desal" else p["tariff_newater"]))
    W = pd.DataFrame(rows); W.to_csv(TAB / "lcow.csv", index=False)

    # NPC over the horizon, both perspectives, BAU grid
    D = demand(p)
    N = pd.concat([npc(p, D, "bau", "social"), npc(p, D, "bau", "operator")], ignore_index=True)
    N.to_csv(TAB / "npc_by_scenario.csv", index=False)

    # Frontier (social EUAC vs GWP per MWh_IT), S1
    F = pd.DataFrame({"strategy": STRATEGIES,
                      "social_cost_per_mwh": [C.loc[a, "social_cost"] for a in STRATEGIES],
                      "operator_cost_per_mwh": [C.loc[a, "operator_cost"] for a in STRATEGIES],
                      "gwp_per_mwh": [L.loc[a, "gwp_total"] for a in STRATEGIES],
                      "gwp_water_only": [L.loc[a, "gwp_water_only"] for a in STRATEGIES],
                      "water_per_mwh": [L.loc[a, "wue"] for a in STRATEGIES]})
    F["efficient_social"] = pareto_efficient(F.social_cost_per_mwh, F.gwp_per_mwh)
    F["efficient_cost_water"] = pareto_efficient(F.social_cost_per_mwh, F.water_per_mwh)
    F.to_csv(TAB / "frontier.csv", index=False)

    # ---- Figure: cost stack per MWh_IT, both perspectives
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.9), sharey=False)
    soc = [("water_cost_social", "Marginal water (LCOW + conveyance)", "#4a90c4"), ("onsite_capex", "On-site capex (annualised)", "#e69f00"),
           ("onsite_energy", "On-site treatment energy", "#f4c87a"), ("discharge_cost", "Blowdown discharge", "#8c8c8c"),
           ("dc_energy_delta", "Additional dry-rejection electricity", "#c1443c")]
    opr = [("operator_water", "Water bill (PUB tariff incl. fees)", "#4a90c4"), ("operator_capex", "Own capex at 8 % WACC", "#e69f00"),
           ("operator_onsite_energy", "On-site treatment energy", "#f4c87a"), ("operator_dc_energy_delta", "Additional dry-rejection electricity", "#c1443c")]
    x = np.arange(4)
    for ax, parts, title, tot in zip(axes, [soc, opr], ["Resource-cost proxy (social, 3%)", "Operator cost (8%, water taxes included)"], ["social_cost", "operator_cost"]):
        pos = np.zeros(4); neg = np.zeros(4)
        for col, lab, c in parts:
            v = C[col].values
            ax.bar(x, v, bottom=np.where(v >= 0, pos, neg), color=c, width=0.6, label=lab, edgecolor="white", linewidth=1)
            pos += np.where(v >= 0, v, 0); neg += np.where(v < 0, v, 0)
        for i, a in enumerate(STRATEGIES):
            ax.text(i, pos[i] + 0.3, f"net {C.loc[a, tot]:+.1f}", ha="center", fontsize=8.5, fontweight="bold")
        ax.axhline(0, color="#333", lw=0.8); ax.set_xticks(x); ax.set_xticklabels([ps.TICK[a] for a in STRATEGIES]); ax.margins(y=0.15)
        ax.set_title(title, fontsize=10); ax.legend(fontsize=7, loc="upper left")
    axes[0].set_ylabel("SGD per MWh of IT energy")
    ps.save(fig, "fig_lcc_stack")

    # ---- Figure: frontier
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.8))
    fig.subplots_adjust(left=0.10, right=0.98, top=0.84, bottom=0.30, wspace=0.35)
    for ax, xc, yc, effc, title in [(axes[0], "social_cost_per_mwh", "gwp_per_mwh", "efficient_social", "Cost and emissions"),
                                    (axes[1], "social_cost_per_mwh", "water_per_mwh", "efficient_cost_water", "Cost and national water demand")]:
        xs = F[xc]
        for i, a in enumerate(STRATEGIES):
            ax.scatter(xs[i], F[yc][i], s=40 if F[effc][i] else 35, color=COLORS[a], edgecolor="black" if F[effc][i] else "white", linewidth=1.1, zorder=5)
            off = ({"A1": (5, 5), "A2": (-8, -12), "A3": (8, -11), "A4": (6, 5)}
                   if yc == "gwp_per_mwh" else
                   {"A1": (6, 5), "A2": (-8, 5), "A3": (7, 5), "A4": (6, 5)})[a]
            ax.annotate(a, (xs[i], F[yc][i]), xytext=off, textcoords="offset points", fontsize=9,
                        ha="right" if a == "A2" else "left", fontweight="bold",
                        arrowprops=dict(arrowstyle="-", color="#999", lw=0.6) if a in ("A2", "A3") else None)
        eff = F[F[effc]].copy(); eff["x"] = xs[F[effc]]; eff = eff.sort_values("x")
        ax.plot(eff.x, eff[yc], color="#555", lw=1, ls="--", zorder=1)
        ax.set_xlabel("Social cost, S$/MWh IT", fontsize=9); ax.set_title(title, fontsize=9.5); ax.margins(x=0.23, y=0.22)
        ax.tick_params(labelsize=8.5)
        ax.axhline(0, color="#aaa", lw=0.6); ax.axvline(0, color="#aaa", lw=0.6)
    axes[0].set_ylabel("Modelled kg CO₂e/MWh IT", fontsize=9)
    axes[1].set_ylabel("Water supplied, m³/MWh IT", fontsize=9)
    handles = [Line2D([0], [0], marker="o", ls="", color=COLORS[a], label=f"{a} {SHORT[a]}", markersize=6)
               for a in STRATEGIES]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.53, 0.07), fontsize=8.5,
               ncol=2, columnspacing=2, handletextpad=0.5)
    fig.text(0.53, 0.02, "Black outlines and dashed lines mark the efficient set in each panel.",
             ha="center", fontsize=8.5, color="#555")
    fig.suptitle("Cost trade-offs with emissions and water demand", fontsize=11, fontweight="bold", y=0.99)
    ps.save(fig, "fig_frontier")

    # ---- Figure: LCOW check
    fig, ax = plt.subplots(figsize=(6, 3.2))
    for i, r in W.iterrows():
        ax.bar(i - 0.2, r.capital, 0.38, color="#9ecae1", label="Capital (CRF 3 %, 25 y)" if i == 0 else None)
        ax.bar(i - 0.2, r.om, 0.38, bottom=r.capital, color="#8c8c8c", label="O&M excl. energy" if i == 0 else None)
        ax.bar(i - 0.2, r.energy, 0.38, bottom=r.capital + r.om, color="#4a90c4", label="Electricity" if i == 0 else None)
        ax.bar(i + 0.2, r.top_down_ppp, 0.38, color="#e69f00", label="Historical PPP price (context only)" if i == 0 else None)
        ax.text(i - 0.2, r.bottom_up_total + 0.03, f"{r.bottom_up_total:.2f}", ha="center", fontsize=8.5)
        ax.text(i + 0.2, r.top_down_ppp + 0.03, f"{r.top_down_ppp:.2f}", ha="center", fontsize=8.5)
        ax.text(i, -0.22, f"user price {r.user_price:.2f}", ha="center", fontsize=8, color="#555")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Desalination (SWRO)", "NEWater (reclamation)"]); ax.set_ylabel("SGD per m³"); ax.set_ylim(-0.3, 1.5)
    ax.legend(fontsize=7.5); ax.set_title("Modelled water cost and historical concession prices")
    ps.save(fig, "fig_lcow_check")

    print(C[["lcow_source", "social_cost", "operator_cost", "elcc_social_tax", "elcc_social_eco"]].round(2))
    print(N.pivot_table(index=["perspective", "scenario"], columns="strategy", values="npc_sgd").round(-3))
    print(F.round(2))


if __name__ == "__main__":
    main()
