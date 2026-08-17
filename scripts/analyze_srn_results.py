#!/usr/bin/env python3
"""Aggregate real SRN sprint outputs into traceable tables and bootstrap intervals."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import rankdata


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


EXPERIMENTS = (
    "ped2_within_raw",
    "avenue_within_raw",
    "ped2_to_avenue_raw",
    "avenue_to_ped2_raw",
    "ped2_avenue_joint_seen_mechanism",
    "ped2_avenue_joint_lr_diagnostic",
)
METRICS = (
    "micro_auroc", "macro_scene_auroc", "macro_video_auroc", "worst_scene_auroc",
    "auprc", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr",
    "threshold_recall", "threshold_false_positive_rate", "false_alarm_events_per_hour",
)


def main() -> int:
    output = ROOT / "analysis"
    output.mkdir(parents=True, exist_ok=True)
    payloads = {
        name: json.loads((ROOT / "runs" / name / "results.json").read_text())
        for name in EXPERIMENTS
    }
    raw_rows = flatten(payloads)
    write_csv(output / "results_long.csv", raw_rows)
    main_rows = comparison_rows(payloads)
    write_csv(output / "main_comparison.csv", main_rows)
    shifts = score_shift_rows(payloads)
    write_csv(output / "score_distribution_shift.csv", shifts)
    paired = paired_deltas(payloads["ped2_avenue_joint_seen_mechanism"])
    summary = build_summary(main_rows, paired, shifts)
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (ROOT / "refine-logs" / "RESULTS_ANALYSIS.md").write_text(
        render_markdown(main_rows, paired, summary), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def flatten(payloads):
    rows = []
    for experiment, payload in payloads.items():
        for run in payload["runs"]:
            row = {
                "experiment": experiment,
                "name": run["name"],
                "method": run["method"],
                "scorer": run["scorer"],
                "seed": run["seed"],
                "selected_epoch": (
                    run["model_selection"]["selected_epoch"]
                    if run["model_selection"] else None
                ),
                "scene_probe": run["diagnostics"][
                    "independent_residual_scene_probe_accuracy"
                ],
                "residual_variance_ratio": run["diagnostics"]["residual_variance_ratio"],
                "source_threshold": run["source_threshold"],
                "target_calibrated_threshold": run["target_calibrated_threshold"],
                "score_artifact": run["score_artifact"],
            }
            for track in ("strict_zero_shot", "target_normal_calibration"):
                for metric in METRICS:
                    row[f"{track}_{metric}"] = run[track].get(metric)
            rows.append(row)
    return rows


def comparison_rows(payloads):
    rows = []
    for experiment, payload in payloads.items():
        for aggregate in payload["aggregate"]:
            strict = aggregate["tracks"]["strict_zero_shot"]
            calibrated = aggregate["tracks"]["target_normal_calibration"]
            row = {
                "experiment": experiment,
                "name": aggregate["name"],
                "seed_count": len(aggregate["seeds"]),
            }
            for metric in METRICS:
                row[f"strict_{metric}_mean"] = strict[metric]["mean"]
                row[f"strict_{metric}_std"] = strict[metric]["std"]
            row["calibrated_threshold_recall_mean"] = calibrated["threshold_recall"]["mean"]
            row["calibrated_threshold_fpr_mean"] = calibrated[
                "threshold_false_positive_rate"
            ]["mean"]
            row["scene_probe_mean"] = aggregate["diagnostics"][
                "independent_residual_scene_probe_accuracy"
            ]["mean"]
            row["residual_variance_ratio_mean"] = aggregate["diagnostics"][
                "residual_variance_ratio"
            ]["mean"]
            runs = [run for run in payload["runs"] if run["name"] == aggregate["name"]]
            if experiment == "ped2_avenue_joint_seen_mechanism":
                low, high = hierarchical_video_bootstrap_auroc(runs, seed=170817)
            else:
                low, high = None, None
            row["strict_micro_auroc_bootstrap_ci_low"] = low
            row["strict_micro_auroc_bootstrap_ci_high"] = high
            rows.append(row)
    return rows


def hierarchical_video_bootstrap_auroc(runs, seed: int, replicates: int = 500):
    rng = np.random.default_rng(seed)
    loaded = []
    for run in runs:
        with np.load(run["score_artifact"], allow_pickle=False) as data:
            item = {key: np.asarray(data[key]) for key in data.files}
        item["_video_groups"] = []
        for dataset in np.unique(item["dataset_id"]):
            mask = item["dataset_id"] == dataset
            item["_video_groups"].append([
                np.flatnonzero(mask & (item["video_id"] == video))
                for video in np.unique(item["video_id"][mask])
            ])
        loaded.append(item)
    values = []
    for _ in range(replicates):
        seed_samples = rng.choice(len(loaded), size=len(loaded), replace=True)
        seed_aurocs = []
        for sample_index in seed_samples:
            data = loaded[int(sample_index)]
            selected = []
            for groups in data["_video_groups"]:
                sampled = rng.choice(len(groups), size=len(groups), replace=True)
                selected.extend(groups[int(index)] for index in sampled)
            indices = np.concatenate(selected)
            value = fast_binary_auroc(
                data["test_labels"][indices], data["test_scores"][indices]
            )
            if value is not None:
                seed_aurocs.append(value)
        if seed_aurocs:
            values.append(float(np.mean(seed_aurocs)))
    if not values:
        return None, None
    return float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))


def fast_binary_auroc(labels, scores):
    positives = labels == 1
    pos_count = int(np.sum(positives))
    neg_count = int(len(labels) - pos_count)
    if not pos_count or not neg_count:
        return None
    ranks = rankdata(scores, method="average")
    return float(
        (np.sum(ranks[positives]) - pos_count * (pos_count + 1) / 2)
        / (pos_count * neg_count)
    )


def paired_deltas(payload):
    baseline = {
        run["seed"]: run for run in payload["runs"] if run["name"] == "raw_prototype"
    }
    rows = []
    for name in (
        "scene_mean_prototype", "adversarial_residual", "full_srn",
        "srn_without_elos", "elos_without_srn", "srn_residual_only",
    ):
        selected = [run for run in payload["runs"] if run["name"] == name]
        for metric in ("micro_auroc", "auprc", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr"):
            deltas = [
                run["strict_zero_shot"][metric]
                - baseline[run["seed"]]["strict_zero_shot"][metric]
                for run in selected
            ]
            rows.append({
                "name": name,
                "metric": metric,
                "mean_delta_vs_raw_prototype": float(np.mean(deltas)),
                "std_delta": float(np.std(deltas)),
                "seed_count": len(deltas),
            })
    return rows


def score_shift_rows(payloads):
    rows = []
    for experiment, payload in payloads.items():
        for run in payload["runs"]:
            with np.load(run["score_artifact"], allow_pickle=False) as data:
                test_normal = data["test_scores"][data["test_labels"] == 0]
                test_anomaly = data["test_scores"][data["test_labels"] == 1]
                row = {
                    "experiment": experiment, "name": run["name"], "seed": run["seed"],
                    "source_val_median": float(np.median(data["source_val_scores"])),
                    "source_val_q99": float(np.quantile(data["source_val_scores"], 0.99)),
                    "target_calibration_median": float(np.median(data["target_calibration_scores"])),
                    "target_calibration_q99": float(np.quantile(data["target_calibration_scores"], 0.99)),
                    "test_normal_median": float(np.median(test_normal)),
                    "test_normal_q99": float(np.quantile(test_normal, 0.99)),
                    "test_anomaly_median": float(np.median(test_anomaly)),
                }
                row["target_normal_over_source_q99"] = (
                    row["test_normal_q99"] / max(row["source_val_q99"], 1e-12)
                )
                rows.append(row)
    return rows


def build_summary(rows, paired, shifts):
    joint = {
        row["name"]: row for row in rows
        if row["experiment"] == "ped2_avenue_joint_seen_mechanism"
    }
    full_delta = next(
        row for row in paired if row["name"] == "full_srn" and row["metric"] == "micro_auroc"
    )
    transfer = [
        row for row in rows
        if row["experiment"] in {"ped2_to_avenue_raw", "avenue_to_ped2_raw"}
    ]
    return {
        "verdict_signal": "STOP_CURRENT_MECHANISM_CLAIM",
        "joint_raw_gaussian_auroc": joint["raw_gaussian"]["strict_micro_auroc_mean"],
        "joint_raw_prototype_auroc": joint["raw_prototype"]["strict_micro_auroc_mean"],
        "joint_full_srn_auroc": joint["full_srn"]["strict_micro_auroc_mean"],
        "joint_full_srn_delta_vs_raw_prototype": full_delta["mean_delta_vs_raw_prototype"],
        "joint_full_srn_scene_probe": joint["full_srn"]["scene_probe_mean"],
        "joint_scene_mean_scene_probe": joint["scene_mean_prototype"]["scene_probe_mean"],
        "all_cross_dataset_source_threshold_test_fpr": sorted({
            row["strict_threshold_false_positive_rate_mean"] for row in transfer
        }),
        "results_rows": len(rows),
        "score_shift_rows": len(shifts),
        "scientific_ceiling": (
            "Real-GT within/cross-dataset reliability evidence and seen-domain mechanism "
            "diagnostic; no genuine whole-scene ELOS evidence without ShanghaiTech."
        ),
    }


def render_markdown(rows, paired, summary):
    joint = [
        row for row in rows
        if row["experiment"] == "ped2_avenue_joint_seen_mechanism"
    ]
    lines = [
        "# SRN Autonomous Results Analysis", "",
        "All values below are generated from saved `results.json` and per-run `scores.npz` ",
        "artifacts. The confidence interval is a 500-replicate hierarchical bootstrap over ",
        "test videos and, where applicable, seeds. It is descriptive because there are only ",
        "two seen domains.", "", "## Raw main comparison", "",
        "| Method | Seeds | AUROC | 95% video-bootstrap CI | AUPRC | TPR@1% | TPR@0.1% | Source-threshold recall | Test FPR | Scene probe |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(joint, key=lambda item: item["strict_micro_auroc_mean"], reverse=True):
        lines.append(
            f"| {row['name']} | {row['seed_count']} | {row['strict_micro_auroc_mean']:.4f} "
            f"| [{row['strict_micro_auroc_bootstrap_ci_low']:.4f}, {row['strict_micro_auroc_bootstrap_ci_high']:.4f}] "
            f"| {row['strict_auprc_mean']:.4f} | {row['strict_tpr_at_1pct_fpr_mean']:.4f} "
            f"| {row['strict_tpr_at_0_1pct_fpr_mean']:.4f} | {row['strict_threshold_recall_mean']:.4f} "
            f"| {row['strict_threshold_false_positive_rate_mean']:.4f} "
            f"| {format_optional(row['scene_probe_mean'])} |"
        )
    full_deltas = [row for row in paired if row["name"] == "full_srn"]
    lines.extend([
        "", "## Key findings", "",
        f"1. **Observation:** raw Gaussian is the strongest joint seen-domain method "
        f"(AUROC {summary['joint_raw_gaussian_auroc']:.4f}); full SRN reaches "
        f"{summary['joint_full_srn_auroc']:.4f}.",
        "   **Interpretation:** the learned residual is not competitive with a strong raw-feature scorer.",
        "   **Implication:** there is no current evidence for an SRN method advantage.",
        "   **Next step:** do not expand architecture search; require genuine multi-scene data before reconsideration.",
        "",
        f"2. **Observation:** full SRN improves over the matched raw prototype by only "
        f"{summary['joint_full_srn_delta_vs_raw_prototype']:+.4f} AUROC, while its held-video "
        f"scene probe remains {summary['joint_full_srn_scene_probe']:.3f}; scene mean lowers "
        f"the same probe to {summary['joint_scene_mean_scene_probe']:.3f}.",
        "   **Interpretation:** the intended scene-information removal mechanism did not occur.",
        "   **Implication:** the small matched-head delta cannot support the central causal claim.",
        "   **Next step:** treat the current SRN mechanism as falsified, not under-tuned.",
        "",
        "3. **Observation:** every strict cross-dataset source threshold labels every target "
        "normal frame anomalous (test FPR 1.0), while target-normal calibration often becomes overly conservative.",
        "   **Interpretation:** the score distributions undergo a severe domain shift that rank metrics hide.",
        "   **Implication:** fixed-threshold transfer is unsupported for all tested representations.",
        "   **Next step:** if authoritative ShanghaiTech becomes available, evaluate a separately declared "
        "normal-only calibration/reliability hypothesis rather than relabeling it as SRN success.",
        "", "## Paired full-SRN deltas versus raw prototype", "",
        "| Metric | Mean delta | Std across 3 seeds |", "|---|---:|---:|",
    ])
    for row in full_deltas:
        lines.append(
            f"| {row['metric']} | {row['mean_delta_vs_raw_prototype']:+.6f} | {row['std_delta']:.6f} |"
        )
    lines.extend([
        "", "## Suggested next experiments", "",
        "1. Acquire an authoritative, checksum-verifiable ShanghaiTech archive and run true scene-held-out ELOS.",
        "2. If that remains blocked, stop SRN mechanism development in this sprint; the bounded LR diagnostic already failed to restore scene suppression.",
        "3. A future, separately preregistered study may investigate score calibration under domain shift using normal target clips, with no zero-shot claim.",
        "", "Complete raw rows: `analysis/results_long.csv`. Score-shift diagnostics: "
        "`analysis/score_distribution_shift.csv`.", "",
    ])
    return "\n".join(lines)


def format_optional(value):
    return "—" if value is None else f"{value:.3f}"


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
