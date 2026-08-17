#!/usr/bin/env python3
"""Generate the joint seen-domain method and mechanism comparison figure."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from paper_plot_style import COLORS, ROOT, save_figure


SOURCE = ROOT / "analysis/main_comparison.csv"
ORDER = [
    "raw_gaussian", "raw_knn", "raw_prototype", "scene_mean_prototype",
    "adversarial_residual", "full_srn", "srn_without_elos", "srn_residual_only",
]
LABELS = ["Raw-G", "Raw-kNN", "Raw-P", "Mean", "Adv.", "SRN", "No-ELOS", "Resid."]


def number(row, key):
    return float(row[key]) if row[key] else np.nan


with SOURCE.open(encoding="utf-8") as handle:
    rows = {
        row["name"]: row for row in csv.DictReader(handle)
        if row["experiment"] == "ped2_avenue_joint_seen_mechanism"
    }
selected = [rows[name] for name in ORDER]
x = np.arange(len(selected))
colors = [COLORS["blue"], COLORS["light_gray"], COLORS["gray"], COLORS["green"],
          COLORS["orange"], COLORS["red"], COLORS["purple"], COLORS["light_gray"]]

fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.7), gridspec_kw={"wspace": 0.28})
auroc = np.asarray([number(row, "strict_micro_auroc_mean") for row in selected])
low = np.asarray([number(row, "strict_micro_auroc_bootstrap_ci_low") for row in selected])
high = np.asarray([number(row, "strict_micro_auroc_bootstrap_ci_high") for row in selected])
for index, (center, lower, upper, color) in enumerate(zip(auroc, low, high, colors)):
    axes[0].errorbar(index, center, yerr=[[center - lower], [upper - center]], fmt="o",
                     color=color, markeredgecolor="black", markeredgewidth=0.4,
                     ecolor=color, elinewidth=1.2, capsize=3, markersize=5)
axes[0].set_ylabel("Frame AUROC")
axes[0].set_ylim(0.50, 0.82)
axes[0].set_xticks(x, LABELS, rotation=32, ha="right")
axes[0].axhline(0.5, color="black", linestyle=":", linewidth=0.7)
axes[0].axhline(auroc[2], color=COLORS["gray"], linestyle="--", linewidth=0.8)
axes[0].text(-0.12, 1.02, "(a)", transform=axes[0].transAxes, fontweight="bold")

width = 0.36
tpr1 = np.asarray([number(row, "strict_tpr_at_1pct_fpr_mean") for row in selected])
tpr01 = np.asarray([number(row, "strict_tpr_at_0_1pct_fpr_mean") for row in selected])
axes[1].bar(x - width / 2, tpr1, width, label="Oracle ROC TPR @ 1% FPR", color=COLORS["blue"])
axes[1].bar(x + width / 2, tpr01, width, label="Oracle ROC TPR @ 0.1% FPR", color=COLORS["orange"], hatch="//")
axes[1].set_ylabel("Oracle true-positive rate")
axes[1].set_ylim(0.0, 0.13)
axes[1].set_xticks(x, LABELS, rotation=32, ha="right")
axes[1].legend(frameon=False, loc="upper right")
axes[1].text(-0.12, 1.02, "(b)", transform=axes[1].transAxes, fontweight="bold")

save_figure(fig, "fig2_method_comparison")
