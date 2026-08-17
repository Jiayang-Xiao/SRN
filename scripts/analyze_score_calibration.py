#!/usr/bin/env python3
"""Create balanced Track-B analysis tables and deterministic figures."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "analysis/track_b/results_long.csv"
OUTPUT = ROOT / "analysis/track_b"


def read_rows() -> list[dict[str, str]]:
    with INPUT.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def seed_balanced_cells(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (
            row["method"],
            row["calibration_budget_videos"],
            row["direction"],
            row["scorer"],
        )
        groups[key].append(row)
    output = []
    metrics = (
        "threshold_false_positive_rate",
        "absolute_fpr_error",
        "threshold_recall",
        "false_alarm_events_per_hour",
        "micro_auroc",
        "auprc",
        "tpr_at_1pct_fpr",
        "tpr_at_0_1pct_fpr",
        "q95_transfer_ratio",
        "q99_transfer_ratio",
    )
    for key, selected in sorted(groups.items()):
        method, budget, direction, scorer = key
        record: dict[str, object] = {
            "method": method,
            "calibration_budget_videos": budget,
            "direction": direction,
            "scorer": scorer,
            "seed_count": len(selected),
        }
        for metric in metrics:
            record[metric] = float(np.mean([float(row[metric]) for row in selected]))
        output.append(record)
    return output


def aggregate_cells(cells: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in cells:
        groups[(str(row["method"]), str(row["calibration_budget_videos"]))].append(row)
    output = []
    for (method, budget), selected in sorted(groups.items()):
        record: dict[str, object] = {
            "method": method,
            "calibration_budget_videos": budget,
            "balanced_cell_count": len(selected),
        }
        for metric in (
            "threshold_false_positive_rate",
            "absolute_fpr_error",
            "threshold_recall",
            "false_alarm_events_per_hour",
            "micro_auroc",
            "auprc",
            "q99_transfer_ratio",
        ):
            values = np.asarray([float(row[metric]) for row in selected])
            record[f"{metric}_median"] = float(np.median(values))
            record[f"{metric}_min"] = float(np.min(values))
            record[f"{metric}_max"] = float(np.max(values))
        output.append(record)
    return output


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def make_operating_figure(cells: list[dict[str, object]]) -> None:
    methods = [
        ("B0_pooled_q99", "B0 source-only"),
        ("B3_video_balanced_q99", "B3 video-balanced"),
        ("B4_conditional_location", "B4 conditional"),
        ("CAL_quantile_q99", "CAL q99, 1 video"),
        ("CAL_quantile_q99", "CAL q99, 4 videos"),
        ("CAL_mean_std", "CAL mean/std, 1 video"),
        ("CAL_mean_std", "CAL mean/std, 4 videos"),
    ]
    budgets = ["", "", "", "1", "4", "1", "4"]
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    colors = plt.get_cmap("tab10")
    for index, ((method, label), budget) in enumerate(zip(methods, budgets)):
        selected = [
            row for row in cells
            if row["method"] == method
            and str(row["calibration_budget_videos"]) == budget
        ]
        raw_x = [float(row["threshold_false_positive_rate"]) for row in selected]
        x = [max(value, 1e-5) for value in raw_x]
        y = [float(row["threshold_recall"]) for row in selected]
        ax.scatter(x, y, s=42, alpha=0.72, color=colors(index), label=label)
        ax.scatter(np.median(x), np.median(y), s=110, marker="X", color=colors(index))
    ax.axvline(0.01, color="black", linestyle="--", linewidth=1, label="desired FPR")
    ax.set_xscale("log")
    ax.set_xlim(7e-6, 1.15)
    ax.set_xlabel("Target-normal FPR at frozen threshold (zeros shown at $10^{-5}$)")
    ax.set_ylabel("Anomaly recall at frozen threshold")
    ax.set_title("Operating-point reliability: seed-balanced scorer/direction cells")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7, ncol=2, loc="best")
    fig.tight_layout()
    for suffix in ("png", "pdf"):
        fig.savefig(OUTPUT / f"operating_point_reliability.{suffix}", dpi=220)
    plt.close(fig)


def make_budget_figure(cells: list[dict[str, object]]) -> None:
    methods = {
        "CAL_quantile_q99": "quantile q99",
        "CAL_mean_std": "mean/std",
        "CAL_median_mad": "median/MAD",
        "CAL_empirical_cdf": "empirical CDF",
    }
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8), sharex=True)
    for method, label in methods.items():
        fpr_values, recall_values = [], []
        for budget in (1, 2, 4):
            selected = [
                row for row in cells
                if row["method"] == method
                and str(row["calibration_budget_videos"]) == str(budget)
            ]
            fpr_values.append(np.median([float(row["threshold_false_positive_rate"]) for row in selected]))
            recall_values.append(np.median([float(row["threshold_recall"]) for row in selected]))
        axes[0].plot((1, 2, 4), fpr_values, marker="o", label=label)
        axes[1].plot((1, 2, 4), recall_values, marker="o", label=label)
    axes[0].axhline(0.01, color="black", linestyle="--", linewidth=1)
    axes[0].set_ylabel("Median target-normal FPR")
    axes[1].set_ylabel("Median anomaly recall")
    for ax in axes:
        ax.set_xlabel("Target-normal calibration videos")
        ax.set_xticks((1, 2, 4))
        ax.grid(alpha=0.25)
    axes[0].legend(fontsize=7)
    fig.suptitle("Calibration-budget curve (six seed-balanced scorer/direction cells)")
    fig.tight_layout()
    for suffix in ("png", "pdf"):
        fig.savefig(OUTPUT / f"calibration_budget_curve.{suffix}", dpi=220)
    plt.close(fig)


def main() -> int:
    rows = read_rows()
    cells = seed_balanced_cells(rows)
    aggregate = aggregate_cells(cells)
    write_csv(OUTPUT / "seed_balanced_cells.csv", cells)
    write_csv(OUTPUT / "seed_balanced_summary.csv", aggregate)
    make_operating_figure(cells)
    make_budget_figure(cells)
    payload = {
        "input": str(INPUT.relative_to(ROOT)),
        "input_rows": len(rows),
        "seed_balanced_cells": len(cells),
        "unit": "direction-by-scorer after averaging prototype seeds",
        "confidence_scope": "descriptive only; two target datasets do not support population inference",
        "figure_data": "analysis/track_b/seed_balanced_cells.csv",
    }
    (OUTPUT / "analysis_manifest.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
