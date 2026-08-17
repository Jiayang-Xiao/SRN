#!/usr/bin/env python3
"""Generate strict source-threshold versus target-normal calibration reliability bars."""

from __future__ import annotations

import csv

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from paper_plot_style import COLORS, ROOT, save_figure


EXPERIMENTS = ["ped2_to_avenue_raw", "avenue_to_ped2_raw"]
PANEL_LABELS = ["Ped2 $\\rightarrow$ Avenue", "Avenue $\\rightarrow$ Ped2"]
METHODS = ["raw_gaussian", "raw_knn", "raw_prototype"]
METHOD_LABELS = ["Gaussian", "kNN", "Prototype"]

with (ROOT / "analysis/main_comparison.csv").open(encoding="utf-8") as handle:
    records = list(csv.DictReader(handle))

fig, axes = plt.subplots(1, 2, figsize=(7.6, 2.55), sharey=True, gridspec_kw={"wspace": 0.12})
x = np.arange(len(METHODS))
for panel, (experiment, label) in enumerate(zip(EXPERIMENTS, PANEL_LABELS)):
    rows = {
        row["name"]: row for row in records if row["experiment"] == experiment
    }
    strict_fpr = [float(rows[name]["strict_threshold_false_positive_rate_mean"]) for name in METHODS]
    calibrated_fpr = [float(rows[name]["calibrated_threshold_fpr_mean"]) for name in METHODS]
    calibrated_recall = [float(rows[name]["calibrated_threshold_recall_mean"]) for name in METHODS]
    ax = axes[panel]
    ax.bar(x, strict_fpr, 0.55, color=COLORS["red"])
    ax.axhline(0.01, color="black", linestyle=":", linewidth=0.8)
    ax.set_xticks(x, METHOD_LABELS, rotation=20, ha="right")
    ax.set_xlabel(label)
    ax.set_ylim(0, 1.08)
    ax.text(-0.1, 1.02, f"({chr(ord('a') + panel)})", transform=ax.transAxes, fontweight="bold")
    inset = ax.inset_axes([0.19, 0.43, 0.68, 0.38])
    inset.bar(x - 0.18, calibrated_fpr, 0.36, color=COLORS["blue"])
    inset.bar(x + 0.18, calibrated_recall, 0.36, color=COLORS["green"], hatch="//")
    inset.set_ylim(0, 0.18)
    inset.set_xticks(x, ["G", "kNN", "P"], fontsize=6)
    inset.tick_params(axis="y", labelsize=6)
    inset.set_ylabel("Target-cal. rate", fontsize=6)
    inset.spines["top"].set_visible(True)
    inset.spines["right"].set_visible(True)
axes[0].set_ylabel("Rate")
handles = [
    Line2D([0], [0], color="black", linestyle=":", label="Nominal 1% FPR"),
    Patch(facecolor=COLORS["red"], label="Source-threshold test FPR"),
    Patch(facecolor=COLORS["blue"], label="Target-calibrated test FPR"),
    Patch(facecolor=COLORS["green"], hatch="//", label="Target-calibrated recall"),
]
fig.legend(handles=handles, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.06),
           ncol=4, fontsize=7)
save_figure(fig, "fig3_threshold_transfer")
