#!/usr/bin/env python3
"""Generate LaTeX result tables from the analysis CSV without hard-coded numbers."""

from __future__ import annotations

import csv

from paper_plot_style import FIG_DIR, ROOT


with (ROOT / "analysis/main_comparison.csv").open(encoding="utf-8") as handle:
    records = list(csv.DictReader(handle))

with (ROOT / "analysis/score_distribution_shift.csv").open(encoding="utf-8") as handle:
    shift_records = list(csv.DictReader(handle))


def value(row, key):
    return float(row[key])


joint = {
    row["name"]: row for row in records
    if row["experiment"] == "ped2_avenue_joint_seen_mechanism"
}
order = [
    ("raw_gaussian", "Raw + Gaussian"),
    ("raw_knn", "Raw + kNN"),
    ("raw_prototype", "Raw + prototype"),
    ("scene_mean_prototype", "Scene mean + prototype"),
    ("adversarial_residual", "Adversarial residual"),
    ("full_srn", "Full SRN + ELOS"),
    ("srn_without_elos", "SRN without ELOS"),
    ("srn_residual_only", "SRN residual only"),
]
lines = [
    r"\begin{table*}[t]", r"\centering", r"\caption{Joint two-seen-domain real-GT diagnostic. The protocol is not unseen-scene evaluation.}",
    r"\label{tab:main_results}", r"\small", r"\resizebox{\textwidth}{!}{%", r"\begin{tabular}{lrrrrrr}", r"\toprule",
    r"Method & AUROC $\uparrow$ & AUPRC $\uparrow$ & Oracle TPR@1\% $\uparrow$ & Oracle TPR@0.1\% $\uparrow$ & Source-thr. FPR $\downarrow$ & Scene probe \\",
    r"\midrule",
]
for name, label in order:
    row = joint[name]
    probe = row["scene_probe_mean"]
    lines.append(
        f"{label} & {value(row, 'strict_micro_auroc_mean'):.4f} & "
        f"{value(row, 'strict_auprc_mean'):.4f} & "
        f"{value(row, 'strict_tpr_at_1pct_fpr_mean'):.4f} & "
        f"{value(row, 'strict_tpr_at_0_1pct_fpr_mean'):.4f} & "
        f"{value(row, 'strict_threshold_false_positive_rate_mean'):.4f} & "
        f"{float(probe):.3f} \\\\" if probe else ""
    )
lines.extend([
    r"\bottomrule", r"\end{tabular}}",
    r"\vspace{1mm}\parbox{0.97\textwidth}{\footnotesize Raw Gaussian and kNN are deterministic (one run); stochastic prototype and learned rows use three seeds. Scene probe is held-video nearest-centroid dataset/camera accuracy. A value of 1.0 establishes decodability; below-chance binary accuracy is label-direction sensitive and is not interpreted as invariance. Oracle TPR columns are not deployable thresholds.}",
    r"\end{table*}", ""
])
(FIG_DIR / "TABLE_main_results.tex").write_text("\n".join(lines), encoding="utf-8")

transfer_lines = [
    r"\begin{table}[t]", r"\centering", r"\caption{Cross-dataset threshold transfer. Strict thresholds use source-normal validation only.}",
    r"\label{tab:threshold_transfer}", r"\small", r"\resizebox{\columnwidth}{!}{%", r"\begin{tabular}{llrrrrrr}", r"\toprule",
    r"Direction & Scorer & AUROC & Src. recall & Src. FPR & q99 ratio & Cal. recall & Cal. FPR \\", r"\midrule",
]
for experiment, direction in (("ped2_to_avenue_raw", r"Ped2$\to$Avenue"), ("avenue_to_ped2_raw", r"Avenue$\to$Ped2")):
    exp_rows = {row["name"]: row for row in records if row["experiment"] == experiment}
    for name, scorer in (("raw_gaussian", "Gaussian"), ("raw_knn", "kNN"), ("raw_prototype", "Prototype")):
        row = exp_rows[name]
        ratios = [
            float(item["target_normal_over_source_q99"])
            for item in shift_records
            if item["experiment"] == experiment and item["name"] == name
        ]
        ratio = sum(ratios) / len(ratios)
        transfer_lines.append(
            f"{direction} & {scorer} & {value(row, 'strict_micro_auroc_mean'):.4f} & "
            f"{value(row, 'strict_threshold_recall_mean'):.3f} & "
            f"{value(row, 'strict_threshold_false_positive_rate_mean'):.3f} & "
            f"{ratio:.2f} & "
            f"{value(row, 'calibrated_threshold_recall_mean'):.4f} & "
            f"{value(row, 'calibrated_threshold_fpr_mean'):.4f} \\\\"
        )
transfer_lines.extend([
    r"\bottomrule", r"\end{tabular}}",
    r"\vspace{1mm}\parbox{0.95\columnwidth}{\footnotesize Source thresholds are selected from source-normal validation only. q99 ratio is target-test-normal q99 divided by source-validation-normal q99. Target-calibrated thresholds use separately declared target-normal videos.}",
    r"\end{table}", ""
])
(FIG_DIR / "TABLE_threshold_transfer.tex").write_text("\n".join(transfer_lines), encoding="utf-8")
print("saved result tables")
