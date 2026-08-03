from __future__ import annotations

from typing import Any

import numpy as np


def evaluate_scores(
    labels: np.ndarray,
    scores: np.ndarray,
    threshold: float,
    scene_ids: np.ndarray,
    video_ids: np.ndarray,
    fps: np.ndarray,
    location_dependent: np.ndarray,
) -> dict[str, Any]:
    labels = np.asarray(labels, dtype=np.int64)
    scores = np.asarray(scores, dtype=np.float64)
    predictions = scores > threshold
    per_scene = grouped_auroc_values(labels, scores, scene_ids)
    per_video = grouped_auroc_values(labels, scores, video_ids)
    result: dict[str, Any] = {
        "micro_auroc": binary_auroc(labels, scores),
        "auprc": average_precision(labels, scores),
        "tpr_at_1pct_fpr": tpr_at_fpr(labels, scores, 0.01),
        "tpr_at_0_1pct_fpr": tpr_at_fpr(labels, scores, 0.001),
        "false_alarm_events_per_hour": false_alarm_events_per_hour(
            labels, predictions, video_ids, fps
        ),
        "threshold_recall": _safe_ratio(np.sum(predictions & (labels == 1)), np.sum(labels == 1)),
        "threshold_false_positive_rate": _safe_ratio(
            np.sum(predictions & (labels == 0)), np.sum(labels == 0)
        ),
        "macro_scene_auroc": _mean_or_none(per_scene.values()),
        "macro_video_auroc": _mean_or_none(per_video.values()),
        "scene_auroc_std": _std_or_none(per_scene.values()),
        "worst_scene_auroc": min(per_scene.values()) if per_scene else None,
        "per_scene_auroc": per_scene,
        "per_video_auroc": per_video,
        "per_scene_threshold_recall": grouped_recall_values(
            labels, predictions, scene_ids
        ),
        "location_dependent_recall": subset_recall(
            labels, predictions, location_dependent == 1
        ),
        "location_independent_recall": subset_recall(
            labels, predictions, location_dependent == 0
        ),
    }
    return result


def binary_auroc(labels: np.ndarray, scores: np.ndarray) -> float | None:
    positives = labels == 1
    negatives = labels == 0
    if not positives.any() or not negatives.any():
        return None
    order = np.argsort(scores, kind="mergesort")
    sorted_scores = scores[order]
    ranks = np.empty(len(scores), dtype=np.float64)
    start = 0
    while start < len(scores):
        stop = start + 1
        while stop < len(scores) and sorted_scores[stop] == sorted_scores[start]:
            stop += 1
        ranks[order[start:stop]] = 0.5 * (start + stop - 1) + 1.0
        start = stop
    pos_count = int(positives.sum())
    neg_count = int(negatives.sum())
    return float((ranks[positives].sum() - pos_count * (pos_count + 1) / 2) / (pos_count * neg_count))


def average_precision(labels: np.ndarray, scores: np.ndarray) -> float | None:
    positives = int(np.sum(labels == 1))
    if positives == 0:
        return None
    order = np.argsort(-scores, kind="mergesort")
    sorted_labels = labels[order] == 1
    precision = np.cumsum(sorted_labels) / np.arange(1, len(labels) + 1)
    return float(np.sum(precision * sorted_labels) / positives)


def tpr_at_fpr(labels: np.ndarray, scores: np.ndarray, target_fpr: float) -> float | None:
    negative_scores = scores[labels == 0]
    positive_scores = scores[labels == 1]
    if not len(negative_scores) or not len(positive_scores):
        return None
    threshold = source_normal_threshold(negative_scores, target_fpr)
    return float(np.mean(positive_scores > threshold))


def source_normal_threshold(normal_scores: np.ndarray, target_fpr: float) -> float:
    if not 0.0 < target_fpr < 1.0:
        raise ValueError("target_fpr must be between zero and one")
    return float(np.quantile(np.asarray(normal_scores), 1.0 - target_fpr, method="higher"))


def grouped_auroc(labels: np.ndarray, scores: np.ndarray, groups: np.ndarray) -> float | None:
    return _mean_or_none(grouped_auroc_values(labels, scores, groups).values())


def grouped_auroc_values(
    labels: np.ndarray, scores: np.ndarray, groups: np.ndarray
) -> dict[str, float]:
    values = {}
    for group in np.unique(groups):
        mask = groups == group
        value = binary_auroc(labels[mask], scores[mask])
        if value is not None:
            values[str(group)] = value
    return values


def grouped_recall_values(
    labels: np.ndarray, predictions: np.ndarray, groups: np.ndarray
) -> dict[str, float]:
    values = {}
    for group in np.unique(groups):
        mask = (groups == group) & (labels == 1)
        if mask.any():
            values[str(group)] = float(np.mean(predictions[mask]))
    return values


def false_alarm_events_per_hour(
    labels: np.ndarray, predictions: np.ndarray, video_ids: np.ndarray, fps: np.ndarray
) -> float:
    events = 0
    total_hours = 0.0
    for video in np.unique(video_ids):
        mask = video_ids == video
        false_positive = predictions[mask] & (labels[mask] == 0)
        events += int(false_positive[0]) if len(false_positive) else 0
        events += int(np.sum(false_positive[1:] & ~false_positive[:-1]))
        total_hours += float(np.sum(mask) / np.mean(fps[mask]) / 3600.0)
    return float(events / total_hours) if total_hours > 0 else 0.0


def subset_recall(labels: np.ndarray, predictions: np.ndarray, subset: np.ndarray) -> float | None:
    positives = subset & (labels == 1)
    return float(np.mean(predictions[positives])) if positives.any() else None


def _safe_ratio(numerator: int, denominator: int) -> float | None:
    return float(numerator / denominator) if denominator else None


def _mean_or_none(values) -> float | None:
    values = list(values)
    return float(np.mean(values)) if values else None


def _std_or_none(values) -> float | None:
    values = list(values)
    return float(np.std(values)) if values else None
