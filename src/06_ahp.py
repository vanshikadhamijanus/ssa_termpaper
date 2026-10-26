"""
Step 6 - AHP (research question Q4). Four-level hierarchy, five weighting
scenarios, rainbow diagrams on the main criteria.

Outputs: ahp_weights.csv, ahp_local_priorities.csv, ahp_scores_by_scenario.csv, ahp_consistency.csv, ahp_judgement_notes.csv
Figures: fig_ahp_hierarchy.png, fig_ahp_scores.png, fig_ahp_rainbow.png
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import load_params, lca, lcc, STRATEGIES, SHORT, COLORS, TAB
import ahp as H
import plotstyle as ps
import matplotlib.pyplot as plt


def main():
    p = load_params()
    L = lca(p); C = lcc(p, L)
    W, CRleaf, q = H.local_priorities(L, C)
    v, CRsub = H.sub_weights()

    # ---- weights table
    rows = []
    for sc in H.WEIGHT_SCENARIOS:
        u, cr = H.main_weights(sc)
        for i, c in enumerate(H.CRITERIA):
            for j, leaf in enumerate(H.SUB[c]):
                rows.append(dict(weight_scenario=sc, criterion=c, main_weight=u[i], cr_main=cr, sub_criterion=leaf,
                                 sub_weight=v[c][j], global_weight=u[i] * v[c][j]))
    pd.DataFrame(rows).to_csv(TAB / "ahp_weights.csv", index=False)

    # ---- local priorities + raw values
    rows = []
    for c in H.CRITERIA:
        for j, leaf in enumerate(H.SUB[c]):
            for k, a in enumerate(STRATEGIES):
                rows.append(dict(criterion=c, sub_criterion=leaf, strategy=a, local_priority=W[c][k, j],
                                 raw_value=q[leaf][k] if leaf in q else np.nan, kind="quantitative" if leaf in q else "pairwise", CR=CRleaf[leaf]))
    pd.DataFrame(rows).to_csv(TAB / "ahp_local_priorities.csv", index=False)

    # ---- consistency table
    cons = [dict(matrix=f"Main criteria ({sc})", CR=H.main_weights(sc)[1]) for sc in H.WEIGHT_SCENARIOS]
    cons += [dict(matrix=f"Sub-criteria under {c}", CR=CRsub[c]) for c in H.CRITERIA]
    cons += [dict(matrix=f"Alternatives wrt {leaf}", CR=cr) for leaf, cr in CRleaf.items() if np.isfinite(cr)]
    cons = pd.DataFrame(cons); cons["ok"] = cons.CR <= 0.1
    cons.to_csv(TAB / "ahp_consistency.csv", index=False)

    # ---- judgement notes
    notes = [dict(matrix=c, note=n) for c, (_, n) in H.SUB_PAIRWISE.items()] + [dict(matrix=l, note=n) for l, (_, n) in H.QUAL_PAIRWISE.items()]
    pd.DataFrame(notes).to_csv(TAB / "ahp_judgement_notes.csv", index=False)

    # Export the comparisons themselves, not only their consistency statistics.
    matrices = [(f"Main {sc}", H.CRITERIA, H.pairwise(upper)) for sc, upper in H.WEIGHT_SCENARIOS.items()]
    matrices += [(f"Sub {c}", H.SUB[c], H.pairwise(spec[0])) for c, spec in H.SUB_PAIRWISE.items()]
    matrices += [(leaf, STRATEGIES, H.pairwise(spec[0])) for leaf, spec in H.QUAL_PAIRWISE.items()]
    pair_rows = []
    for name, labels, matrix in matrices:
        weights, lam, ci, cr = H.AHPmat(matrix)
        for i, row_label in enumerate(labels):
            for j, col_label in enumerate(labels):
                pair_rows.append(dict(matrix=name, row=row_label, column=col_label,
                                      comparison=matrix[i, j], row_priority=weights[i], CR=cr))
    pd.DataFrame(pair_rows).to_csv(TAB / "ahp_pairwise_matrices.csv", index=False)

    # ---- scores by weighting scenario
    rows = []
    for sc in H.WEIGHT_SCENARIOS:
        u, _ = H.main_weights(sc)
        g = H.global_scores(W, v, u)
        rank = (-g).argsort().argsort() + 1
        for k, a in enumerate(STRATEGIES):
            rows.append(dict(weight_scenario=sc, strategy=a, score=g[k], rank=rank[k]))
    S = pd.DataFrame(rows); S.to_csv(TAB / "ahp_scores_by_scenario.csv", index=False)

    # ---- Figure: scores by scenario (grouped bars)
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    scs = list(H.WEIGHT_SCENARIOS); x = np.arange(len(scs)); w = 0.2
    for k, a in enumerate(STRATEGIES):
        vals = [S[(S.weight_scenario == sc) & (S.strategy == a)].score.iloc[0] for sc in scs]
        ax.bar(x + (k - 1.5) * w, vals, w, color=COLORS[a], label=SHORT[a], edgecolor="white")
        for xi, vv in zip(x, vals):
            ax.text(xi + (k - 1.5) * w, vv + 0.005, f"{vv:.2f}", ha="center", fontsize=7)
    ax.set_xticks(x); ax.set_xticklabels([s.replace(" / ", "\n").replace(" (", "\n(") for s in scs], fontsize=8.5)
    ax.set_ylabel("Global priority"); ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.15))
    ax.set_title("AHP priorities under five illustrative weighting scenarios", pad=28)
    ps.save(fig, "fig_ahp_scores")

    # ---- Figure: rainbow diagrams, main criteria (W1)
    u0, _ = H.main_weights("W1 Balanced")
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.3), sharey=True)
    for k, (ax, c) in enumerate(zip(axes, H.CRITERIA)):
        ps_ = np.linspace(0, 1, 21)
        G = np.array([H.global_scores(W, v, H.renorm_wt(pp, k, u0)) for pp in ps_])
        for j, a in enumerate(STRATEGIES):
            ax.plot(ps_, G[:, j], color=COLORS[a], lw=2, label=SHORT[a])
        ax.axvline(u0[k], color="black", ls="--", lw=1)
        ax.set_title(c, fontsize=9.5); ax.set_xlabel(f"weight of {c.split()[0]}"); ax.set_xlim(0, 1); ax.set_ylim(0, 0.7)
    axes[0].set_ylabel("Global priority")
    fig.legend(*axes[0].get_legend_handles_labels(), ncol=4, loc="lower center", bbox_to_anchor=(0.5, -0.12), fontsize=9)
    fig.suptitle("Rainbow diagrams: how the ranking moves as each main-criterion weight changes (others rescaled; dashed = W1 base)", fontsize=10.5, fontweight="bold", y=1.04)
    ps.save(fig, "fig_ahp_rainbow")

    # Deterministic stress cases keep their changed assumption explicit.
    robustness = []
    def record(case, kind, weights, subweights, local=W, value=np.nan):
        scores = H.global_scores(local, subweights, weights)
        ranks = (-scores).argsort().argsort() + 1
        for k, a in enumerate(STRATEGIES):
            robustness.append(dict(case=case, kind=kind, value=value, strategy=a,
                                   score=scores[k], rank=ranks[k]))
    for floor in (.01, .10, .30):
        local, _, _ = H.local_priorities(L, C, floor=floor)
        for name, omitted in H.PROXY_CASES.items():
            record(f"{name}; floor={floor:g}", "proxy and score floor", u0,
                   H.omit_leaves(v, omitted), local, floor)
    for i, c in enumerate(H.CRITERIA):
        for weight in np.linspace(0, 1, 21):
            record(c, "main weight", H.renorm_wt(weight, i, u0), v, value=weight)
        for j, leaf in enumerate(H.SUB[c]):
            for weight in np.linspace(0, 1, 21):
                vv = {key: val.copy() for key, val in v.items()}
                vv[c] = H.renorm_wt(weight, j, v[c])
                record(leaf, "subcriterion weight", u0, vv, value=weight)
    pd.DataFrame(robustness).to_csv(TAB / "ahp_robustness.csv", index=False)

    # ---- Figure: compact hierarchy readable at a 17 cm report width
    from matplotlib.patches import FancyBboxPatch
    fig, ax = plt.subplots(figsize=(6.8, 5.4))
    fig.subplots_adjust(left=.015, right=.985, bottom=.015, top=.985)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    def panel(x, y, width, height, face, edge="#a8b7c1"):
        ax.add_patch(FancyBboxPatch((x, y), width, height,
                     boxstyle="round,pad=0.006", facecolor=face, edgecolor=edge, linewidth=.7))

    panel(.025, .89, .95, .095, "#edf1f4")
    ax.text(.5, .942, "Choose water supply and heat rejection", ha="center", va="center",
            fontsize=10, fontweight="bold")
    ax.text(.5, .909, "New Singapore data centres · 2027–2035", ha="center", va="center", fontsize=9)
    ax.text(.08, .855, "Main criteria", fontsize=9, fontweight="bold")
    ax.text(.385, .855, "Subcriteria · weights within each criterion", fontsize=9, fontweight="bold")
    ax.plot([.04, .04], [.89, .245], color="#8295a1", lw=.9)
    labels = {
        "C1a Societal life-cycle cost": "C1a Resource cost before carbon valuation",
        "C1b Cost to DC operators": "C1b Operator cost",
        "C2a GHG per MWh_IT": "C2a Greenhouse-gas emissions",
        "C2b Electricity use": "C2b Electricity use",
        "C2c Marine discharge (brine, blowdown)": "C2c Discharge volume proxy",
        "C3a Water drawn from national supply": "C3a Water drawn from national supply",
        "C3b Weather resilience": "C3b Weather resilience",
        "C3c Dependence on used-water feedstock": "C3c Used-water feedstock dependence",
        "C4a Technical maturity in the tropics": "C4a Heat-rejection maturity in tropics",
        "C4b Policy alignment & enforceability": "C4b Policy alignment and enforceability",
        "C4c Effect on other water users": "C4c Effect on other water users",
    }
    for i, (criterion, yc) in enumerate(zip(H.CRITERIA, (.765, .595, .425, .255))):
        panel(.08, yc - .069, .255, .138, "#e3edf3")
        panel(.385, yc - .069, .59, .138, "#f8fafb")
        ax.annotate("", xy=(.08, yc), xytext=(.04, yc),
                    arrowprops=dict(arrowstyle="-", color="#8295a1", lw=.9))
        ax.annotate("", xy=(.385, yc), xytext=(.335, yc),
                    arrowprops=dict(arrowstyle="->", color="#8295a1", lw=.9))
        code, name = criterion.split(" ", 1)
        ax.text(.2075, yc + .02, f"{code} {name}", ha="center", va="center", fontsize=9,
                fontweight="bold")
        ax.text(.2075, yc - .024, f"Main weight {u0[i]:.2f}", ha="center", va="center", fontsize=9)
        ys = np.linspace(yc + .04, yc - .04, len(H.SUB[criterion]))
        for j, (leaf, yy) in enumerate(zip(H.SUB[criterion], ys)):
            kind = "Q" if leaf in q else "P"
            ax.text(.399, yy, labels[leaf], ha="left", va="center", fontsize=8.8)
            ax.text(.963, yy, f"{v[criterion][j]:.2f} [{kind}]", ha="right", va="center", fontsize=8.8,
                    color="#475a67" if kind == "Q" else "#8a5b2e")
    ax.text(.5, .155, "Each subcriterion compares the same four alternatives", ha="center", fontsize=9)
    alternatives = ["A1 Wet + desal", "A2 Wet + NEWater", "A3 Tower + reuse", "A4 Dry + trim"]
    for a, label, x in zip(STRATEGIES, alternatives, (.025, .268, .511, .754)):
        panel(x, .08, .222, .048, COLORS[a], COLORS[a])
        ax.text(x + .111, .104, label, ha="center", va="center", fontsize=8.8,
                fontweight="bold", color="white")
    ax.text(.5, .038, "[Q] transformed model output   [P] team judgment", ha="center", fontsize=9)
    ax.text(.5, .009, "Illustrative balanced weights; sensitivity cases change weights and judgments.",
            ha="center", fontsize=8.8, color="#475a67")
    ps.save(fig, "fig_ahp_hierarchy")

    print(S.pivot(index="weight_scenario", columns="strategy", values="score").round(3))
    print(cons.to_string(index=False))


if __name__ == "__main__":
    main()
