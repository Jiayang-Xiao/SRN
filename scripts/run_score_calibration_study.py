#!/usr/bin/env python3
"""Run the frozen Track-B source-only and target-normal calibration study."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from restricted_bridge.calibration import (  # noqa: E402
    empirical_quantile_map,
    fit_conditional_location_calibrator,
    map_location_scale,
    mean_location_scale,
    robust_location_scale,
    standardize,
    video_balanced_threshold,
)
from restricted_bridge.config import load_config  # noqa: E402
from restricted_bridge.data import load_feature_data, validate_feature_data  # noqa: E402
from restricted_bridge.metrics import (  # noqa: E402
    binary_auroc,
    evaluate_scores,
    source_normal_threshold,
)
from restricted_bridge.scorers import build_scorer  # noqa: E402


TARGET_FPR = 0.01
DIRECTIONS = {
    "ped2_to_avenue": ROOT / "configs/ped2_to_avenue_raw.yaml",
    "avenue_to_ped2": ROOT / "configs/avenue_to_ped2_raw.yaml",
}
SCORER_SEEDS = {
    "knn": (13,),
    "gaussian": (13,),
    "prototype": (13, 29, 43),
}
METRIC_FIELDS = (
    "micro_auroc",
    "auprc",
    "tpr_at_1pct_fpr",
    "tpr_at_0_1pct_fpr",
    "threshold_recall",
    "threshold_false_positive_rate",
    "false_alarm_events_per_hour",
    "macro_scene_auroc",
    "macro_video_auroc",
    "scene_auroc_std",
    "worst_scene_auroc",
    "location_dependent_recall",
    "location_independent_recall",
)


def main() -> int:
    output = ROOT / "analysis/track_b"
    score_root = output / "scores"
    score_root.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    run_provenance = []

    for direction, config_path in DIRECTIONS.items():
        config = load_config(config_path)
        data = load_feature_data(config["data"], seed=13)
        integrity = validate_feature_data(data, config["data"])
        indices = {name: data.indices(name) for name in ("train", "source_val", "target_calibration", "test")}
        calibration_videos = sorted(np.unique(data.video_id[indices["target_calibration"]]).tolist())
        budgets = sorted({1, 2, 4, len(calibration_videos)})
        budgets = [budget for budget in budgets if budget <= len(calibration_videos)]

        for scorer_name, seeds in SCORER_SEEDS.items():
            for seed in seeds:
                scorer = build_scorer(scorer_name, config["scorer"])
                scorer.fit(data.features[indices["train"]], seed=seed)
                split_scores = {
                    split: scorer.score(data.features[index])
                    for split, index in indices.items()
                }
                _verify_against_historical(direction, scorer_name, seed, split_scores)

                source_scores = split_scores["source_val"]
                target_scores = split_scores["target_calibration"]
                test_scores = split_scores["test"]
                source_videos = data.video_id[indices["source_val"]]
                source_threshold = source_normal_threshold(source_scores, TARGET_FPR)

                raw_context = {
                    "source_scores": source_scores,
                    "test_scores": test_scores,
                    "threshold": source_threshold,
                }
                rows.append(_record(
                    output, score_root, direction, scorer_name, seed,
                    "B-ZS", "B0_pooled_q99", None, False,
                    raw_context, data, indices,
                ))

                source_mean, source_std = mean_location_scale(source_scores)
                mean_source = standardize(source_scores, source_mean, source_std)
                mean_test = standardize(test_scores, source_mean, source_std)
                rows.append(_record(
                    output, score_root, direction, scorer_name, seed,
                    "B-ZS", "B1_source_mean_std", None, False,
                    {
                        "source_scores": mean_source,
                        "test_scores": mean_test,
                        "threshold": source_normal_threshold(mean_source, TARGET_FPR),
                    }, data, indices,
                ))

                source_median, source_mad = robust_location_scale(source_scores)
                robust_source = standardize(source_scores, source_median, source_mad)
                robust_test = standardize(test_scores, source_median, source_mad)
                rows.append(_record(
                    output, score_root, direction, scorer_name, seed,
                    "B-ZS", "B2_source_median_mad", None, False,
                    {
                        "source_scores": robust_source,
                        "test_scores": robust_test,
                        "threshold": source_normal_threshold(robust_source, TARGET_FPR),
                    }, data, indices,
                ))

                balanced_threshold, per_video_thresholds = video_balanced_threshold(
                    source_scores, source_videos, TARGET_FPR
                )
                rows.append(_record(
                    output, score_root, direction, scorer_name, seed,
                    "B-ZS", "B3_video_balanced_q99", None, False,
                    {
                        **raw_context,
                        "threshold": balanced_threshold,
                        "extra": {"per_source_video_thresholds": per_video_thresholds},
                    }, data, indices,
                ))

                conditional = fit_conditional_location_calibrator(
                    data.features[indices["source_val"]],
                    source_scores,
                    source_videos,
                    target_fpr=TARGET_FPR,
                    rank=8,
                )
                conditional_test = conditional.transform(
                    test_scores, data.features[indices["test"]]
                )
                rows.append(_record(
                    output, score_root, direction, scorer_name, seed,
                    "B-ZS", "B4_conditional_location", None, False,
                    {
                        "source_scores": conditional.cross_fitted_scores,
                        "test_scores": conditional_test,
                        "threshold": conditional.threshold,
                        "extra": {
                            "selected_alpha": conditional.selected_alpha,
                            "cv_mean_absolute_fpr_error": conditional.cv_mean_absolute_fpr_error,
                            "cv_fpr_by_video": conditional.cv_fpr_by_video,
                            "context_rank": 8,
                        },
                    }, data, indices,
                ))

                for budget in budgets:
                    selected_videos = calibration_videos[:budget]
                    selected = np.isin(
                        data.video_id[indices["target_calibration"]], selected_videos
                    )
                    calibration_scores = target_scores[selected]
                    calibration_metadata = {
                        "calibration_videos": selected_videos,
                        "calibration_frames": int(np.sum(selected)),
                    }

                    rows.append(_record(
                        output, score_root, direction, scorer_name, seed,
                        "B-CAL", "CAL_quantile_q99", budget, True,
                        {
                            "source_scores": source_scores,
                            "test_scores": test_scores,
                            "threshold": source_normal_threshold(calibration_scores, TARGET_FPR),
                            "calibration_scores": calibration_scores,
                            "calibration_video_ids": selected_videos,
                            "extra": calibration_metadata,
                        }, data, indices,
                    ))

                    target_mean, target_std = mean_location_scale(calibration_scores)
                    mapped_mean_test = map_location_scale(
                        test_scores, target_mean, target_std, source_mean, source_std
                    )
                    rows.append(_record(
                        output, score_root, direction, scorer_name, seed,
                        "B-CAL", "CAL_mean_std", budget, True,
                        {
                            "source_scores": source_scores,
                            "test_scores": mapped_mean_test,
                            "threshold": source_threshold,
                            "calibration_scores": calibration_scores,
                            "calibration_video_ids": selected_videos,
                            "extra": calibration_metadata,
                        }, data, indices,
                    ))

                    target_median, target_mad = robust_location_scale(calibration_scores)
                    mapped_robust_test = map_location_scale(
                        test_scores, target_median, target_mad, source_median, source_mad
                    )
                    rows.append(_record(
                        output, score_root, direction, scorer_name, seed,
                        "B-CAL", "CAL_median_mad", budget, True,
                        {
                            "source_scores": source_scores,
                            "test_scores": mapped_robust_test,
                            "threshold": source_threshold,
                            "calibration_scores": calibration_scores,
                            "calibration_video_ids": selected_videos,
                            "extra": calibration_metadata,
                        }, data, indices,
                    ))

                    mapped_ecdf_test = empirical_quantile_map(
                        test_scores, calibration_scores, source_scores
                    )
                    rows.append(_record(
                        output, score_root, direction, scorer_name, seed,
                        "B-CAL", "CAL_empirical_cdf", budget, True,
                        {
                            "source_scores": source_scores,
                            "test_scores": mapped_ecdf_test,
                            "threshold": source_threshold,
                            "calibration_scores": calibration_scores,
                            "calibration_video_ids": selected_videos,
                            "extra": calibration_metadata,
                        }, data, indices,
                    ))

                run_provenance.append({
                    "direction": direction,
                    "scorer": scorer_name,
                    "seed": seed,
                    "config": str(config_path.relative_to(ROOT)),
                    "cache": config["data"]["path"],
                    "cache_sha256": sha256(ROOT / config["data"]["path"]),
                    "integrity": integrity,
                    "source_validation_videos": sorted(np.unique(source_videos).tolist()),
                    "target_calibration_videos": calibration_videos,
                    "test_videos": sorted(np.unique(data.video_id[indices["test"]]).tolist()),
                })

    write_csv(output / "results_long.csv", rows)
    aggregates = aggregate_rows(rows)
    write_csv(output / "results_aggregate.csv", aggregates)
    historical = verify_historical_results()
    summary = build_summary(rows, aggregates, historical)
    write_json(output / "summary.json", summary)
    write_json(output / "provenance.json", {
        "protocol": "TRACK_B_PROTOCOL_FREEZE.md",
        "target_fpr": TARGET_FPR,
        "target_test_statistics_used_for_fit": False,
        "target_anomaly_labels_used_for_fit_or_selection": False,
        "runs": run_provenance,
        "historical_verification": historical,
    })
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _record(
    output: Path,
    score_root: Path,
    direction: str,
    scorer: str,
    seed: int,
    track: str,
    method: str,
    budget: int | None,
    uses_target_normal: bool,
    score_context: dict,
    data,
    indices: dict[str, np.ndarray],
) -> dict:
    source_scores = np.asarray(score_context["source_scores"], dtype=np.float64)
    test_scores = np.asarray(score_context["test_scores"], dtype=np.float64)
    threshold = float(score_context["threshold"])
    test_index = indices["test"]
    labels = data.label[test_index]
    metrics = evaluate_scores(
        labels,
        test_scores,
        threshold,
        data.scene_id[test_index],
        data.video_id[test_index],
        data.frame_index[test_index],
        data.fps[test_index],
        data.location_dependent[test_index],
    )
    normal = test_scores[labels == 0]
    anomaly = test_scores[labels == 1]
    safe_method = method.lower()
    suffix = f"_budget{budget}" if budget is not None else ""
    artifact = score_root / direction / f"{scorer}_seed{seed}_{safe_method}{suffix}.npz"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact_payload = {
        "source_normal_scores": source_scores,
        "test_scores": test_scores,
        "test_labels": labels,
        "scene_id": data.scene_id[test_index],
        "video_id": data.video_id[test_index],
        "frame_index": data.frame_index[test_index],
        "fps": data.fps[test_index],
        "threshold": np.asarray(threshold),
    }
    if "calibration_scores" in score_context:
        artifact_payload["target_normal_calibration_scores"] = np.asarray(
            score_context["calibration_scores"], dtype=np.float64
        )
        artifact_payload["target_normal_calibration_video_ids"] = np.asarray(
            score_context["calibration_video_ids"]
        ).astype(str)
    np.savez_compressed(
        artifact,
        **artifact_payload,
    )
    source_q95 = float(np.quantile(source_scores, 0.95))
    source_q99 = float(np.quantile(source_scores, 0.99))
    normal_q95 = float(np.quantile(normal, 0.95))
    normal_q99 = float(np.quantile(normal, 0.99))
    row = {
        "direction": direction,
        "scorer": scorer,
        "seed": seed,
        "track": track,
        "method": method,
        "calibration_budget_videos": budget,
        "uses_target_normal": uses_target_normal,
        "uses_target_anomalies": False,
        "fa_hour_denominator": "total represented test-video duration",
        "threshold": threshold,
        "desired_fpr": TARGET_FPR,
        "absolute_fpr_error": abs(metrics["threshold_false_positive_rate"] - TARGET_FPR),
        "source_normal_q95": source_q95,
        "source_normal_q99": source_q99,
        "target_test_normal_q95": normal_q95,
        "target_test_normal_q99": normal_q99,
        "q95_transfer_ratio": _safe_ratio(normal_q95, source_q95),
        "q99_transfer_ratio": _safe_ratio(normal_q99, source_q99),
        "target_test_anomaly_median": float(np.median(anomaly)),
        "score_artifact": str(artifact.relative_to(ROOT)),
    }
    for field in METRIC_FIELDS:
        row[field] = metrics.get(field)
    row["per_scene_auroc"] = json.dumps(metrics["per_scene_auroc"], sort_keys=True)
    row["per_video_auroc"] = json.dumps(metrics["per_video_auroc"], sort_keys=True)
    row["per_scene_threshold_recall"] = json.dumps(
        metrics["per_scene_threshold_recall"], sort_keys=True
    )
    for key, value in score_context.get("extra", {}).items():
        row[key] = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else value
    return row


def _verify_against_historical(direction, scorer, seed, split_scores) -> None:
    name = f"raw_{scorer}"
    artifact = ROOT / "runs" / f"{direction}_raw" / f"seed_{seed}" / name / "scores.npz"
    if not artifact.is_file():
        raise FileNotFoundError(f"historical score artifact is missing: {artifact}")
    with np.load(artifact, allow_pickle=False) as old:
        comparisons = {
            "source_val_scores": split_scores["source_val"],
            "target_calibration_scores": split_scores["target_calibration"],
            "test_scores": split_scores["test"],
        }
        for key, recomputed in comparisons.items():
            if not np.allclose(old[key], recomputed, rtol=1e-8, atol=1e-8):
                difference = float(np.max(np.abs(old[key] - recomputed)))
                raise AssertionError(f"historical score mismatch {direction}/{name}/{seed}/{key}: {difference}")


def verify_historical_results() -> dict:
    expected = {
        "joint_raw_gaussian_auroc": 0.6885,
        "joint_raw_prototype_auroc": 0.6653,
        "joint_full_srn_auroc": 0.6677,
        "joint_full_srn_delta_vs_raw_prototype": 0.0024,
        "joint_full_srn_scene_probe": 1.0,
    }
    run_root = ROOT / "runs/ped2_avenue_joint_seen_mechanism"

    def method_aurocs(name: str, seeds: tuple[int, ...]) -> list[float]:
        values = []
        for seed in seeds:
            with np.load(run_root / f"seed_{seed}/{name}/scores.npz", allow_pickle=False) as saved:
                values.append(float(binary_auroc(saved["test_labels"], saved["test_scores"])))
        return values

    gaussian = method_aurocs("raw_gaussian", (13,))
    prototype = method_aurocs("raw_prototype", (13, 29, 43))
    full = method_aurocs("full_srn", (13, 29, 43))
    payload = json.loads((run_root / "results.json").read_text(encoding="utf-8"))
    full_runs = [run for run in payload["runs"] if run["name"] == "full_srn"]
    probe = float(np.mean([
        run["diagnostics"]["independent_residual_scene_probe_accuracy"] for run in full_runs
    ]))
    cross_fprs = []
    for direction in DIRECTIONS:
        for scorer, seeds in SCORER_SEEDS.items():
            for seed in seeds:
                artifact = ROOT / "runs" / f"{direction}_raw" / f"seed_{seed}" / f"raw_{scorer}/scores.npz"
                with np.load(artifact, allow_pickle=False) as saved:
                    threshold = source_normal_threshold(saved["source_val_scores"], TARGET_FPR)
                    normal = saved["test_scores"][saved["test_labels"] == 0]
                    cross_fprs.append(float(np.mean(normal > threshold)))
    recomputed = {
        "joint_raw_gaussian_auroc": float(np.mean(gaussian)),
        "joint_raw_prototype_auroc": float(np.mean(prototype)),
        "joint_full_srn_auroc": float(np.mean(full)),
        "joint_full_srn_delta_vs_raw_prototype": float(np.mean(np.asarray(full) - np.asarray(prototype))),
        "joint_full_srn_scene_probe": probe,
        "cross_dataset_source_threshold_target_normal_fprs": sorted(set(cross_fprs)),
    }
    checks = {
        key: {
            "expected_approx": value,
            "recomputed": recomputed[key],
            "absolute_difference": abs(recomputed[key] - value),
            "pass": abs(recomputed[key] - value) <= 5e-4,
        }
        for key, value in expected.items()
    }
    checks["cross_dataset_source_threshold_target_normal_fpr"] = {
        "expected_approx": 1.0,
        "recomputed_unique": recomputed["cross_dataset_source_threshold_target_normal_fprs"],
        "pass": recomputed["cross_dataset_source_threshold_target_normal_fprs"] == [1.0],
    }
    return {"checks": checks, "all_pass": all(item["pass"] for item in checks.values())}


def aggregate_rows(rows: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = {}
    for row in rows:
        key = (row["track"], row["method"], row["calibration_budget_videos"])
        groups.setdefault(key, []).append(row)
    output = []
    for (track, method, budget), selected in sorted(groups.items(), key=lambda item: str(item[0])):
        aggregate = {
            "track": track,
            "method": method,
            "calibration_budget_videos": budget,
            "run_count": len(selected),
            "direction_count": len({row["direction"] for row in selected}),
        }
        for field in (
            "threshold_false_positive_rate",
            "absolute_fpr_error",
            "threshold_recall",
            "false_alarm_events_per_hour",
            "q95_transfer_ratio",
            "q99_transfer_ratio",
            "micro_auroc",
            "auprc",
        ):
            values = np.asarray([float(row[field]) for row in selected], dtype=np.float64)
            aggregate[f"{field}_mean"] = float(np.mean(values))
            aggregate[f"{field}_median"] = float(np.median(values))
            aggregate[f"{field}_std"] = float(np.std(values))
            higher_is_worse = field in {
                "threshold_false_positive_rate",
                "absolute_fpr_error",
                "false_alarm_events_per_hour",
            }
            aggregate[f"{field}_worst"] = float(
                np.max(values) if higher_is_worse else np.min(values)
            )
        output.append(aggregate)
    return output


def build_summary(rows: list[dict], aggregates: list[dict], historical: dict) -> dict:
    baseline_rows = _seed_balanced_rows(rows, "B0_pooled_q99", None)
    baseline = {
        (row["direction"], row["scorer"]): row for row in baseline_rows
    }
    # B0 is already known to saturate at FPR=1 in every stress-test run and
    # therefore has zero variance for the wrong reason. The frozen protocol uses
    # this small absolute cap instead of requiring a reduction below zero.
    source_fpr_variance_cap = 0.0025
    source_candidates = []
    for method in ("B1_source_mean_std", "B2_source_median_mad", "B3_video_balanced_q99", "B4_conditional_location"):
        selected = _seed_balanced_rows(rows, method, None)
        improvements = [
            baseline[(row["direction"], row["scorer"])]["absolute_fpr_error"]
            - row["absolute_fpr_error"] for row in selected
        ]
        fprs = [row["threshold_false_positive_rate"] for row in selected]
        recalls = [row["threshold_recall"] for row in selected]
        candidate = {
            "method": method,
            "median_absolute_fpr_error_improvement": float(np.median(improvements)),
            "worst_fpr": float(np.max(fprs)),
            "median_recall": float(np.median(recalls)),
            "fpr_variance": float(np.var(fprs)),
            "passes_gate": bool(
                np.median(improvements) >= 0.50
                and np.max(fprs) <= 0.25
                and np.median(recalls) >= 0.05
                and np.var(fprs) <= source_fpr_variance_cap
            ),
        }
        source_candidates.append(candidate)

    b3 = next(item for item in source_candidates if item["method"] == "B3_video_balanced_q99")
    b4 = next(item for item in source_candidates if item["method"] == "B4_conditional_location")
    learned_beats_simple = bool(
        b4["median_absolute_fpr_error_improvement"] > b3["median_absolute_fpr_error_improvement"]
        and b4["median_recall"] >= b3["median_recall"]
    )
    b4["beats_video_balanced_control"] = learned_beats_simple
    b4["retained"] = bool(b4["passes_gate"] and learned_beats_simple)

    calibration_candidates = []
    for method in ("CAL_quantile_q99", "CAL_mean_std", "CAL_median_mad", "CAL_empirical_cdf"):
        by_budget = {}
        for budget in (1, 2, 4):
            selected = _seed_balanced_rows(rows, method, budget)
            if not selected:
                continue
            by_budget[str(budget)] = {
                "median_fpr": float(np.median([row["threshold_false_positive_rate"] for row in selected])),
                "median_absolute_fpr_error": float(np.median([row["absolute_fpr_error"] for row in selected])),
                "median_recall": float(np.median([row["threshold_recall"] for row in selected])),
            }
        baseline_error = float(np.median([
            row["absolute_fpr_error"] for row in baseline.values()
        ]))
        errors = [by_budget[str(b)]["median_absolute_fpr_error"] for b in (1, 2, 4) if str(b) in by_budget]
        monotone = all(right <= left + 1e-12 for left, right in zip(errors, errors[1:]))
        passes = (
            set(by_budget) == {"1", "2", "4"}
            and monotone
            and by_budget["1"]["median_fpr"] <= 0.10
            and by_budget["4"]["median_fpr"] <= 0.05
            and baseline_error - by_budget["4"]["median_absolute_fpr_error"] >= 0.50
            and by_budget["4"]["median_recall"] >= 0.05
        )
        calibration_candidates.append({
            "method": method,
            "by_budget": by_budget,
            "monotone_aggregate_error": bool(monotone),
            "passes_gate": bool(passes),
        })

    source_pass = any(item["passes_gate"] for item in source_candidates if item["method"] != "B4_conditional_location") or b4["retained"]
    calibration_pass = any(item["passes_gate"] for item in calibration_candidates)
    if source_pass:
        status = "PROMISING_SOURCE_ONLY_CALIBRATION"
    elif calibration_pass:
        status = "PROMISING_TARGET_NORMAL_CALIBRATION_ONLY"
    else:
        status = "NO_CALIBRATION_ADVANTAGE"
    return {
        "primary_status": status,
        "evidence_scope": "exact Ped2-to-Avenue and Avenue-to-Ped2 cross-dataset stress protocol; not multi-source unseen-scene evidence",
        "historical_results_recomputed": historical["all_pass"],
        "source_only_candidates": source_candidates,
        "target_normal_candidates": calibration_candidates,
        "learned_method_retained": bool(b4["retained"]),
        "source_fpr_variance_cap": source_fpr_variance_cap,
        "gate_aggregation_unit": "direction-by-scorer after averaging stochastic seeds",
        "result_rows": len(rows),
        "aggregate_rows": len(aggregates),
    }


def _seed_balanced_rows(
    rows: list[dict], method: str, budget: int | None
) -> list[dict]:
    """Average stochastic seeds before treating scorer/direction cells equally."""
    selected = [
        row for row in rows
        if row["method"] == method
        and row["calibration_budget_videos"] == budget
    ]
    groups: dict[tuple[str, str], list[dict]] = {}
    for row in selected:
        groups.setdefault((row["direction"], row["scorer"]), []).append(row)
    output = []
    numeric = (
        "absolute_fpr_error",
        "threshold_false_positive_rate",
        "threshold_recall",
    )
    for (direction, scorer), group in sorted(groups.items()):
        record = {"direction": direction, "scorer": scorer}
        for field in numeric:
            record[field] = float(np.mean([float(row[field]) for row in group]))
        output.append(record)
    return output


def _safe_ratio(numerator: float, denominator: float) -> float:
    if abs(denominator) <= 1e-12:
        return math.inf if numerator > 0 else 1.0
    return float(numerator / denominator)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
