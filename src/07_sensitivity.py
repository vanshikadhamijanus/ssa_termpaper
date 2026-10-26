"""Conditional sensitivity analysis for the common-liquid-cooling comparison.

Parameter uncertainty, preference uncertainty and structural scenarios are
reported separately. Random draws describe the declared test distributions;
they are not probabilities estimated from stakeholder or operating records.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import brentq

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import (load_params, load_assumptions, demand, lca, lcc, npc, it_energy,
                   STRATEGIES, SHORT, COLORS, SCENARIOS, GRIDS, GRID_NAME, TAB)
import model as M
import ahp as H
import plotstyle as ps
import matplotlib.pyplot as plt

N_MC = 10000
N_PREFERENCE = 2000
PARAMETER_SEED = 29
PREFERENCE_SEED = 2901
PREFERENCE_SIGMA = .35
SCORE_FLOORS = (.01, .10, .30)


def evaluate(p):
    L = lca(p)
    return L, lcc(p, L)


def active_uncertain_inputs():
    """Triangular inputs active in these base-grid cost/GHG/AHP/demand outputs.

    Low-carbon-grid and eco-cost factors belong to explicit scenario analyses;
    drawing them here would add inputs that do not affect these outputs.
    """
    A = load_assumptions()
    active = set(M.ACTIVE_UNCERTAIN_PARAMS)
    active -= {"ef_grid_2035_lowc", "ecocost_gwp", "fx_eur_sgd"}
    return A[A.id.isin(active) & (A.dist == "tri") & (A.low < A.high)].copy()


def tornado(p0, a):
    L0, C0 = evaluate(p0)
    rows = []
    for _, r in active_uncertain_inputs().iterrows():
        out = {}
        for case in ("low", "high"):
            L, C = evaluate({**p0, r.id: float(r[case])})
            out[case] = C.loc[a, "social_cost"], L.loc[a, "gwp_total"]
        rows.append(dict(strategy=a, param=r.id, parameter=r.parameter,
                         low=r.low, base=r.base, high=r.high,
                         cost_low=out["low"][0], cost_high=out["high"][0],
                         cost_base=C0.loc[a, "social_cost"],
                         gwp_low=out["low"][1], gwp_high=out["high"][1],
                         gwp_base=L0.loc[a, "gwp_total"]))
    df = pd.DataFrame(rows)
    df["cost_swing"] = (df.cost_high - df.cost_low).abs()
    df["gwp_swing"] = (df.gwp_high - df.gwp_low).abs()
    return df


def plot_tornado(T, metric, fname, unit):
    fig, axes = plt.subplots(1, 4, figsize=(13, 4.2))
    for ax, a in zip(axes, STRATEGIES):
        d = T[(T.strategy == a) & (T[f"{metric}_swing"] > 1e-9)].nlargest(8, f"{metric}_swing").iloc[::-1]
        base = d[f"{metric}_base"].iloc[0] if len(d) else 0
        y = np.arange(len(d))
        ax.barh(y, d[f"{metric}_low"] - base, color="#9ecae1", label="low input")
        ax.barh(y, d[f"{metric}_high"] - base, color="#2b5c8a", label="high input")
        ax.set_yticks(y)
        ax.set_yticklabels(d.param, fontsize=7.5)
        ax.axvline(0, color="#333", lw=.8)
        ax.set_title(f"{SHORT[a]} (base {base:.2f})", fontsize=9.5, color=COLORS[a])
        ax.set_xlabel(f"change in {unit}", fontsize=8)
    fig.legend(*axes[0].get_legend_handles_labels(), ncol=2, loc="lower center", bbox_to_anchor=(.5, -.06), fontsize=8.5)
    title = "Resource cost" if metric == "cost" else "Screening GHG"
    fig.suptitle(f"{title} per MWh IT: one input at a time", fontsize=11, fontweight="bold", y=1.02)
    fig.tight_layout()
    ps.save(fig, fname)


def scenario_matrix(p):
    D = demand(p)
    rows = []
    for grid in GRIDS:
        for perspective in ("social", "operator"):
            N = npc(p, D, grid, perspective)
            N["grid_name"] = GRID_NAME[grid]
            rows.append(N)
    table = pd.concat(rows, ignore_index=True)
    table.to_csv(TAB / "scenario_matrix.csv", index=False)
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6), sharey=True)
    for ax, column, title, scale in zip(
            axes, ("npc_sgd", "total_gwp_t"),
            ("Resource NPC 2027–35 (S$ million)", "Screening GHG 2027–35 (kt CO₂e)"), (1e6, 1e3)):
        piv = table[table.perspective == "social"].pivot(index=["scenario", "grid"], columns="strategy", values=column) / scale
        ax.imshow(piv.values, cmap="YlGnBu", aspect="auto")
        ax.set_xticks(range(4))
        ax.set_xticklabels([SHORT[a] for a in STRATEGIES], fontsize=8)
        ax.set_yticks(range(len(piv)))
        ax.set_yticklabels([f"{s} · {GRID_NAME[g]}" for s, g in piv.index], fontsize=7.5)
        for i in range(len(piv)):
            for j in range(4):
                ax.text(j, i, f"{piv.values[i, j]:,.1f}", ha="center", va="center", fontsize=7.5,
                        color="white" if piv.values[i, j] > np.nanmax(piv.values) * .65 else "#222")
        ax.set_title(title, fontsize=9.5)
        ax.grid(False)
    fig.tight_layout()
    ps.save(fig, "fig_scenario_matrix")
    return table


def breakevens(p0):
    rows = []
    def solve(param, function, lo, hi, label):
        flo, fhi = function({**p0, param: lo}), function({**p0, param: hi})
        if flo * fhi <= 0:
            value = brentq(lambda x: function({**p0, param: x}), lo, hi)
            status = "crossing in tested interval"
        else:
            value, status = np.nan, "no crossing in tested interval"
        rows.append(dict(question=label, parameter=param, base=p0[param], breakeven=value,
                         search_low=lo, search_high=hi, difference_at_low=flo,
                         difference_at_high=fhi, status=status))
    for comparison in ("A2", "A3"):
        solve("dpue_dry", lambda p, b=comparison: lcc(p).loc["A4", "social_cost"] - lcc(p).loc[b, "social_cost"],
              -.03, .15, f"A4 versus {comparison}: dry-rejection delta PUE at equal resource cost")
        solve("dpue_dry", lambda p, b=comparison: lca(p).loc["A4", "gwp_total"] - lca(p).loc[b, "gwp_total"],
              -.03, .15, f"A4 versus {comparison}: dry-rejection delta PUE at equal screening GHG")
    solve("sec_desal", lambda p: lca(p).loc["A1", "gwp_total"] - lca(p).loc["A2", "gwp_total"],
          .1, 5., "Desalination specific energy at equal GHG with NEWater")
    solve("tariff_newater", lambda p: lcc(p).loc["A3", "operator_cost"] - lcc(p).loc["A2", "operator_cost"],
          .2, 6., "NEWater tariff at A3 operator break-even against A2")
    solve("capex_hicoc", lambda p: lcc(p).loc["A3", "social_cost"] - lcc(p).loc["A2", "social_cost"],
          0., 5e5, "A3 recovery capex at resource-cost break-even against A2")
    solve("capex_dry_premium", lambda p: lcc(p).loc["A4", "operator_cost"] - lcc(p).loc["A2", "operator_cost"],
          0., 1e6, "A4 dry-rejection capex at operator break-even against A2")
    table = pd.DataFrame(rows)
    table.to_csv(TAB / "breakeven.csv", index=False)
    return table


def structural_cases(p0):
    """Scenarios remain separate from probability calculations."""
    cases = [("Base: grid electricity, no discharge resource cost", {})]
    cases += [("Residual desalination for A3/A4", {"residual_source": "desal"})]
    cases += [(f"Discharge resource cost {cost:.2f} SGD/m3", {"cost_discharge_treatment": cost})
              for cost in (0., .30, 1.09)]
    rows = []
    for name, override in cases:
        p = {**p0, **override}
        L, C = evaluate(p)
        for a in STRATEGIES:
            rows.append(dict(case=name, strategy=a, source=L.loc[a, "source"],
                             water_m3_per_mwh=L.loc[a, "wue"],
                             social_cost=C.loc[a, "social_cost"], operator_cost=C.loc[a, "operator_cost"],
                             gwp=L.loc[a, "gwp_total"], accounting="full grid"))
    # Explicit non-zero low-carbon intensities. Water production stays on grid.
    for share in (.5, .8):
        for lowcarbon_ef in (.05, .15, .30):
            L, C = evaluate({**p0, "dc_green_share_scenario": share,
                             "dc_green_ef_scenario": lowcarbon_ef})
            for a in STRATEGIES:
                rows.append(dict(case=f"DC low-carbon share {share:g}; intensity {lowcarbon_ef:.2f} kgCO2e/kWh",
                                 strategy=a, source=L.loc[a, "source"], water_m3_per_mwh=L.loc[a, "wue"],
                                 social_cost=C.loc[a, "social_cost"], operator_cost=C.loc[a, "operator_cost"],
                                 gwp=L.loc[a, "gwp_total"], accounting="illustrative blended intensity"))
    table = pd.DataFrame(rows)
    table.to_csv(TAB / "structural_sensitivity.csv", index=False)
    return table


def cooling_thresholds(p0):
    """A4–A2/A3 trade-off as dry energy and incremental equipment cost vary."""
    rows, thresholds = [], []
    capex_values = np.linspace(0, 300000, 31)
    energy_values = np.linspace(-.02, .10, 61)
    for capex in capex_values:
        for delta in energy_values:
            p = {**p0, "capex_dry_premium": capex, "dpue_dry": delta}
            L, C = evaluate(p)
            for b in ("A2", "A3"):
                rows.append(dict(dpue_dry=delta, capex_dry_premium=capex, comparison=b,
                                 cost_difference=C.loc["A4", "social_cost"] - C.loc[b, "social_cost"],
                                 operator_cost_difference=C.loc["A4", "operator_cost"] - C.loc[b, "operator_cost"],
                                 gwp_difference=L.loc["A4", "gwp_total"] - L.loc[b, "gwp_total"]))
        # Cost and GHG are affine in delta PUE in this screening model.
        L0, C0 = evaluate({**p0, "capex_dry_premium": capex, "dpue_dry": 0.})
        L1, C1 = evaluate({**p0, "capex_dry_premium": capex, "dpue_dry": .01})
        for b in ("A2", "A3"):
            def crossing(zero, one):
                return -zero / ((one - zero) / .01) if one != zero else np.nan
            thresholds.append(dict(capex_dry_premium=capex, comparison=b,
                resource_cost_equal_dpue=crossing(C0.loc["A4", "social_cost"] - C0.loc[b, "social_cost"], C1.loc["A4", "social_cost"] - C1.loc[b, "social_cost"]),
                operator_cost_equal_dpue=crossing(C0.loc["A4", "operator_cost"] - C0.loc[b, "operator_cost"], C1.loc["A4", "operator_cost"] - C1.loc[b, "operator_cost"]),
                ghg_equal_dpue=crossing(L0.loc["A4", "gwp_total"] - L0.loc[b, "gwp_total"], L1.loc["A4", "gwp_total"] - L1.loc[b, "gwp_total"])))
    grid = pd.DataFrame(rows)
    lines = pd.DataFrame(thresholds)
    grid.to_csv(TAB / "cooling_threshold_grid.csv", index=False)
    lines.to_csv(TAB / "cooling_thresholds.csv", index=False)
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.7), sharey=True)
    for ax, b in zip(axes, ("A2", "A3")):
        sub = lines[lines.comparison == b]
        ax.plot(sub.capex_dry_premium / 1000, sub.resource_cost_equal_dpue, label="Equal resource cost", color="#245a78")
        ax.plot(sub.capex_dry_premium / 1000, sub.operator_cost_equal_dpue, label="Equal operator cost", color="#b36524")
        ax.plot(sub.capex_dry_premium / 1000, sub.ghg_equal_dpue, label="Equal GHG", color="#55905c", ls="--")
        ax.scatter([p0["capex_dry_premium"] / 1000], [p0["dpue_dry"]], color="#c1443c", marker="x", s=60, label="Base assumption", zorder=3)
        ax.axhline(0, color="#888", lw=.7)
        comparison_label = "wet + NEWater" if b == "A2" else "tower + recovery"
        ax.set_title(f"A4 versus {b}\n{comparison_label}", fontsize=9)
        ax.set_xlabel("Extra capital\n(S$ thousand / MW IT)", fontsize=9)
        ax.tick_params(labelsize=9)
        ax.grid(alpha=.2)
    axes[0].set_ylabel("Dry-rejection change in PUE", fontsize=9)
    axes[0].legend(fontsize=8.2, loc="upper right")
    fig.suptitle("A4 breaks even along each line", fontsize=10)
    fig.tight_layout()
    ps.save(fig, "fig_cooling_thresholds")
    return grid, lines


def monte_carlo(p0, n=N_MC, n_preference=N_PREFERENCE):
    if n_preference > n:
        raise ValueError("Combined preference draws must not exceed parameter draws")
    rng = np.random.default_rng(PARAMETER_SEED)
    pref_rng = np.random.default_rng(PREFERENCE_SEED)
    tri = active_uncertain_inputs()
    draws = {r.id: rng.triangular(r.low, r.base, r.high, n) for _, r in tri.iterrows()}
    cost, elcc, opc, gwp, water, score = [np.zeros((n, 4)) for _ in range(6)]
    # Capacity quantities are fixed scenarios; utilisation, ramp and WUE vary.
    demand_2035 = {s: np.zeros((n, 4)) for s in SCENARIOS}
    demand_horizon = {s: np.zeros((n, 4)) for s in SCENARIOS}
    v, _ = H.sub_weights()
    u, _ = H.main_weights("W1 Balanced")
    base_L, base_C = evaluate(p0)
    preference_scores = {(mode, hierarchy): np.zeros((n_preference, 4))
                         for mode in ("preferences_only", "parameters_and_preferences")
                         for hierarchy in ("Full hierarchy", "Reduced overlap")}
    matrix_attempts = matrix_rejections = 0
    max_cr = 0.
    floor_counts = {floor: 0 for floor in SCORE_FLOORS}
    for i in range(n):
        p = {**p0, **{key: float(values[i]) for key, values in draws.items()}}
        L, C = evaluate(p)
        cost[i] = C.social_cost.values
        elcc[i] = C.elcc_social_tax.values
        opc[i] = C.operator_cost.values
        gwp[i] = L.gwp_total.values
        water[i] = L.wue.values
        W, _, _ = H.local_priorities(L, C)
        score[i] = H.global_scores(W, v, u)
        for scenario in SCENARIOS:
            energy = it_energy(p, scenario)
            demand_2035[scenario][i] = energy[2035] * water[i]
            demand_horizon[scenario][i] = sum(energy.values()) * water[i]
        if i < n_preference:
            pu, pv, qualitative, diagnostics = H.sample_preferences(pref_rng, PREFERENCE_SIGMA)
            floor = float(pref_rng.choice(SCORE_FLOORS))
            floor_counts[floor] += 1
            matrix_attempts += diagnostics["matrix_attempts"]
            matrix_rejections += diagnostics["matrices_rejected"]
            max_cr = max(max_cr, diagnostics["maximum_accepted_cr"])
            for mode, LL, CC in (("preferences_only", base_L, base_C),
                                ("parameters_and_preferences", L, C)):
                local, _, _ = H.local_priorities(LL, CC, floor=floor, qualitative=qualitative)
                for hierarchy in ("Full hierarchy", "Reduced overlap"):
                    vv = H.omit_leaves(pv, H.PROXY_CASES[hierarchy])
                    preference_scores[(mode, hierarchy)][i] = H.global_scores(local, vv, pu)

    def summary(arr, metric):
        quantile = np.percentile(arr, [5, 25, 50, 75, 95], axis=0)
        return pd.DataFrame(dict(metric=metric, strategy=STRATEGIES, mean=arr.mean(0),
                                p5=quantile[0], p25=quantile[1], p50=quantile[2],
                                p75=quantile[3], p95=quantile[4], n_draws=n, seed=PARAMETER_SEED))
    table = pd.concat([summary(cost, "social_cost_per_mwh"), summary(elcc, "social_elcc_per_mwh"),
                       summary(opc, "operator_cost_per_mwh"), summary(gwp, "gwp_per_mwh"),
                       summary(water, "wue"), summary(score, "ahp_score_W1")], ignore_index=True)
    table.to_csv(TAB / "mc_summary.csv", index=False)
    rank = pd.DataFrame(dict(strategy=STRATEGIES,
        p_rank1_ahp_W1=[(score.argmax(1) == k).mean() for k in range(4)],
        p_lowest_social_cost=[(cost.argmin(1) == k).mean() for k in range(4)],
        p_lowest_operator_cost=[(opc.argmin(1) == k).mean() for k in range(4)],
        p_lowest_gwp=[(gwp.argmin(1) == k).mean() for k in range(4)], n_draws=n, seed=PARAMETER_SEED))
    rank["p_A3_cheaper_than_A2_operator"] = (opc[:, 2] < opc[:, 1]).mean()
    rank["p_A3_cheaper_than_A2_social"] = (cost[:, 2] < cost[:, 1]).mean()
    rank["p_A4_cheaper_than_A2_social"] = (cost[:, 3] < cost[:, 1]).mean()
    rank["p_A3_lower_gwp_than_A2"] = (gwp[:, 2] < gwp[:, 1]).mean()
    rank.to_csv(TAB / "mc_rank_probability.csv", index=False)
    demand_rows = []
    for scenario in SCENARIOS:
        for metric, arr in (("water_2035_m3", demand_2035[scenario]), ("water_2027_2035_m3", demand_horizon[scenario])):
            out = summary(arr, metric)
            out["scenario"] = scenario
            demand_rows.append(out)
    pd.concat(demand_rows, ignore_index=True).to_csv(TAB / "mc_demand_summary.csv", index=False)
    preference_rows = []
    for (mode, hierarchy), scores in preference_scores.items():
        for k, a in enumerate(STRATEGIES):
            preference_rows.append(dict(mode=mode, hierarchy=hierarchy, strategy=a,
                                        p_rank1=(scores.argmax(1) == k).mean(), mean_score=scores[:, k].mean(),
                                        n_draws=n_preference, seed=PREFERENCE_SEED))
    pd.DataFrame(preference_rows).to_csv(TAB / "mc_preference_rank_probability.csv", index=False)
    metadata = [
        ("parameter_seed", PARAMETER_SEED), ("parameter_draws", n),
        ("active_triangular_inputs", len(tri)), ("input_ids", ";".join(tri.id)),
        ("input_dependence", "Independent triangular inputs; shared inputs use the same draw across strategies"),
        ("capacity_policy", "Fixed IT capacity in each explicit scenario; no stochastic capacity weights"),
        ("parameter_AHP", "W1 and base subweights/judgments fixed; score floor 0.1"),
        ("preference_seed", PREFERENCE_SEED), ("preference_draws_per_case", n_preference),
        ("main_weight_distribution", "Dirichlet(1,1,1,1); broad simplex stress test, not elicited preferences"),
        ("sub_and_qualitative_distribution", f"Upper ratios times exp(N(0,{PREFERENCE_SIGMA}^2)); clipped to [1/9,9]; reciprocal lower triangle"),
        ("matrix_acceptance_rule", "CR <= 0.10; redraw the rejected matrix"),
        ("matrix_attempts", matrix_attempts), ("matrices_accepted", matrix_attempts - matrix_rejections),
        ("matrices_rejected", matrix_rejections), ("maximum_accepted_CR", max_cr),
        ("score_floor_distribution", "Equal probability over 0.01, 0.10, 0.30"),
        ("score_floor_draw_counts", str(floor_counts)),
        ("interpretation", "Conditional frequencies under declared assumptions, not validated real-world probabilities"),
    ]
    pd.DataFrame(metadata, columns=["setting", "value"]).to_csv(TAB / "uncertainty_metadata.csv", index=False)
    plot_mc(cost, gwp, score, rank, n)
    return table, rank


def plot_mc(cost, gwp, score, rank, n):
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    for ax, arr, title in zip(axes, (cost, gwp, score),
                              ("Resource cost (S$/MWh IT)", "Screening GHG (kg CO₂e/MWh IT)", "AHP score with fixed W1 preferences")):
        parts = ax.violinplot([arr[:, k] for k in range(4)], showmedians=True, widths=.8)
        for k, body in enumerate(parts["bodies"]):
            body.set_facecolor(COLORS[STRATEGIES[k]])
            body.set_alpha(.75)
        for key in ("cmedians", "cbars", "cmins", "cmaxes"):
            parts[key].set_color("#333")
        ax.set_xticks(range(1, 5))
        ax.set_xticklabels([SHORT[a] for a in STRATEGIES], fontsize=8)
        ax.set_title(title, fontsize=9)
    fig.suptitle(f"{n:,} parameter draws; frequencies depend on the specified input distributions", fontsize=10)
    fig.tight_layout()
    ps.save(fig, "fig_mc_distributions")
    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    columns = ["p_rank1_ahp_W1", "p_lowest_social_cost", "p_lowest_gwp", "p_lowest_operator_cost"]
    labels = ["AHP rank 1\nfixed preferences", "Lowest\nresource cost", "Lowest\nGHG", "Lowest\noperator cost"]
    x, width = np.arange(4), .2
    for k, a in enumerate(STRATEGIES):
        ax.bar(x + (k - 1.5) * width, rank.loc[k, columns].values.astype(float), width,
               color=COLORS[a], label=SHORT[a])
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Conditional frequency")
    ax.set_ylim(0, 1.15)
    ax.legend(ncol=4, fontsize=8, loc="upper center")
    ax.set_title("Ranking under parameter uncertainty only")
    fig.tight_layout()
    ps.save(fig, "fig_mc_rank")


def main():
    p = load_params()
    T = pd.concat([tornado(p, a) for a in STRATEGIES], ignore_index=True)
    T.to_csv(TAB / "tornado.csv", index=False)
    plot_tornado(T, "cost", "fig_tornado_cost", "S$/MWh IT")
    plot_tornado(T, "gwp", "fig_tornado_gwp", "kg CO₂e/MWh IT")
    scenario_matrix(p)
    B = breakevens(p)
    structural_cases(p)
    cooling_thresholds(p)
    S, R = monte_carlo(p)
    print(B.round(4).to_string(index=False))
    print(R.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
