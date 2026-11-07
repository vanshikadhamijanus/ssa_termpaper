"""Draw Figure 1 of the report: the four options, their water source, their
heat rejection and the resulting water use. Values come from the model so the
picture cannot drift from the tables.

    python src/16_draw_options_figure.py  ->  outputs/figures/fig_report_options.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import load_params, wue_by_strategy, COLORS
import plotstyle as ps
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


def box(ax, x, y, w, h, text, fc, fs=10.5, bold=False, color="#222"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
                                fc=fc, ec="#333", lw=1.1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else None, color=color, linespacing=1.35)


def arrow(ax, x1, x2, y):
    ax.add_patch(FancyArrowPatch((x1, y), (x2, y), arrowstyle="-|>", mutation_scale=12, color="#333", lw=1.2))


def main():
    p = load_params()
    wue, share = wue_by_strategy(p)
    dry = p["liquid_heat_share"]
    rows = [
        ("A1", "Desalinated seawater\n(seawater RO)", f"Wet cooling towers\n{p['coc_current']:.0f} cycles of concentration"),
        ("A2", "NEWater\n(reclaimed used water)", f"Wet cooling towers\n{p['coc_current']:.0f} cycles of concentration"),
        ("A3", "NEWater", f"Towers at {p['coc_best']:.0f} cycles +\n{p['blowdown_recovery']:.0%} of blowdown recovered"),
        ("A4", "NEWater\n(for the wet share and trim)",
         f"Dry loop takes {dry:.0%} of the heat, with wet trim\non hours above {p['trim_threshold']:.0f}°C ({share:.1%} of hours);\nwet towers take the other {1 - dry:.0%} all year"),
    ]
    fig, ax = plt.subplots(figsize=(9.2, 6.2))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.09)
    ax.grid(False)
    heads = [(0.245, "Make-up water source"), (0.60, "Heat rejection at the data centre"), (0.9025, "Water used,\nm³/MWh IT")]
    for x, t in heads:
        ax.text(x, 1.03, t, ha="center", va="center", fontsize=11, fontweight="bold", color="#1D2D50", linespacing=1.2)
    ys = [0.80, 0.585, 0.37, 0.14]
    h = 0.16
    for (code, source, reject), y in zip(rows, ys):
        hh = h + 0.03 if code == "A4" else h
        yy = y - (0.015 if code == "A4" else 0)
        ax.add_patch(FancyBboxPatch((0.02, yy), 0.065, hh, boxstyle="round,pad=0.012,rounding_size=0.02", fc=COLORS[code], ec=COLORS[code]))
        ax.text(0.0525, yy + hh / 2, code, ha="center", va="center", fontsize=13, fontweight="bold", color="white")
        arrow(ax, 0.09, 0.125, yy + hh / 2)
        box(ax, 0.125, yy, 0.24, hh, source, "#dbe9f6")
        arrow(ax, 0.37, 0.43, yy + hh / 2)
        box(ax, 0.43, yy, 0.34, hh, reject, "#fbe9c9", fs=10.5 if code != "A4" else 9.8)
        arrow(ax, 0.775, 0.825, yy + hh / 2)
        box(ax, 0.825, yy, 0.155, hh, f"{wue[code]:.2f}", "#f1f1f1", fs=15, bold=True)
    ps.save(fig, "fig_report_options")


if __name__ == "__main__":
    main()
