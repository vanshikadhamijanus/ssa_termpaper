"""Shared matplotlib style so every figure in the paper and poster matches."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from model import COLORS, SHORT, FIG

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 11, "axes.titlepad": 10, "axes.titleweight": "bold",
    "axes.labelsize": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#e3e3e3", "grid.linewidth": 0.6, "axes.axisbelow": True,
    "legend.frameon": False, "legend.fontsize": 9, "figure.dpi": 150, "savefig.dpi": 220,
    "savefig.bbox": "tight", "savefig.facecolor": "white",
})
GREY = "#6b6b6b"


def save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.png")
    plt.close(fig)
    print(f"  fig  {name}.png")

TICK = {"A1": "A1\nDesal", "A2": "A2\nNEWater", "A3": "A3\nTower + reuse", "A4": "A4\nDry + trim"}
