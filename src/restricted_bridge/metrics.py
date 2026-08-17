"""异常检测指标计算工具。

本模块实现 restricted bridge 实验报告中需要的帧级、场景级和视频级指标。
实现只依赖 NumPy，便于在 CPU dry-run 和小规模 pilot 中稳定复现，不额外引入
sklearn 版本差异。
"""

from __future__ import annotations

from typing import Any

import numpy as np


def evaluate_scores(
    labels: np.ndarray,
    scores: np.ndarray,
    threshold: float,
    scene_ids: np.ndarray,
    video_ids: np.ndarray,
    frame_indices: np.ndarray,
    fps: np.ndarray,
    location_dependent: np.ndarray,
) -> dict[str, Any]:
    """汇总一组测试分数在固定阈值下的检测指标。

    Args:
        labels: 二值标签数组，``1`` 表示异常帧，``0`` 表示正常帧。
        scores: 异常分数数组，分数越高表示越异常。
        threshold: 固定决策阈值。通常来自源域验证正常样本或目标校准正常样本的
            指定 FPR 分位数。
        scene_ids: 每帧所属场景 ID，用于计算 macro scene AUROC 和分场景召回。
        video_ids: 每帧所属视频 ID，用于计算 macro video AUROC 和误报事件数。
        frame_indices: 视频内原始帧编号，用于时间排序并在缺帧处切断误报事件。
        fps: 每帧对应视频的帧率，用于把连续误报片段标准化为每小时事件数。
        location_dependent: 异常位置依赖标记，用于分别统计位置相关/无关异常召回。

    Returns:
        指标字典。包含整体 AUROC、AUPRC、TPR@FPR、阈值召回、阈值误报率、
        false alarm events per hour、按场景/视频 AUROC，以及位置相关分组召回。
        当某项指标缺少正样本或负样本而不可定义时，对应值为 ``None``。
    """
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
            labels, predictions, video_ids, frame_indices, fps
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
    """计算二分类 AUROC。

    Args:
        labels: 二值标签数组，``1`` 为正类，``0`` 为负类。
        scores: 正类分数数组，分数越高越偏向正类。

    Returns:
        AUROC 浮点数；如果正类或负类缺失，则返回 ``None``。

    Notes:
        实现采用 Mann-Whitney U 统计量形式，并对相同分数使用平均秩处理。
        ``mergesort`` 保证排序稳定，便于复现实验结果。
    """
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
    """计算 Average Precision，也就是 PR 曲线下的阶梯式面积。

    Args:
        labels: 二值标签数组，``1`` 为异常/正样本。
        scores: 异常分数数组，越大越优先被检出。

    Returns:
        AP 分数；若没有正样本则返回 ``None``。

    Notes:
        函数按分数降序扫描，每遇到一个正样本就累加当前位置 precision，最后
        除以正样本总数。这与信息检索中常用的 AP 定义一致。
    """
    positives = int(np.sum(labels == 1))
    if positives == 0:
        return None
    order = np.argsort(-scores, kind="mergesort")
    sorted_scores = scores[order]
    sorted_positive = labels[order] == 1
    true_positives = np.cumsum(sorted_positive)
    false_positives = np.cumsum(~sorted_positive)
    threshold_ends = np.flatnonzero(
        np.r_[sorted_scores[1:] != sorted_scores[:-1], True]
    )
    precision = true_positives[threshold_ends] / (
        true_positives[threshold_ends] + false_positives[threshold_ends]
    )
    recall = true_positives[threshold_ends] / positives
    recall_increments = np.diff(np.r_[0.0, recall])
    return float(np.sum(recall_increments * precision))


def tpr_at_fpr(labels: np.ndarray, scores: np.ndarray, target_fpr: float) -> float | None:
    """在指定负样本 FPR 阈值下计算正样本 TPR。

    Args:
        labels: 二值标签数组。
        scores: 异常分数数组，分数越高表示越异常。
        target_fpr: 目标假阳性率，例如 ``0.01`` 表示 1% FPR。

    Returns:
        正样本分数高于负样本分位阈值的比例；当正样本或负样本缺失时返回
        ``None``。
    """
    negative_scores = scores[labels == 0]
    positive_scores = scores[labels == 1]
    if not len(negative_scores) or not len(positive_scores):
        return None
    threshold = source_normal_threshold(negative_scores, target_fpr)
    return float(np.mean(positive_scores > threshold))


def source_normal_threshold(normal_scores: np.ndarray, target_fpr: float) -> float:
    """从正常样本分数中取出满足目标 FPR 的阈值。

    Args:
        normal_scores: 只包含正常样本的异常分数。
        target_fpr: 目标假阳性率，必须在 ``(0, 1)`` 内。

    Returns:
        ``normal_scores`` 的 ``1 - target_fpr`` 分位数。使用 ``higher`` 方法
        保守地选择现有样本分数作为阈值。

    Raises:
        ValueError: 当 ``target_fpr`` 不在开区间 ``(0, 1)`` 内时抛出。
    """
    if not 0.0 < target_fpr < 1.0:
        raise ValueError("target_fpr must be between zero and one")
    return float(np.quantile(np.asarray(normal_scores), 1.0 - target_fpr, method="higher"))


def grouped_auroc(labels: np.ndarray, scores: np.ndarray, groups: np.ndarray) -> float | None:
    """计算按组 AUROC 的宏平均。

    Args:
        labels: 二值标签数组。
        scores: 异常分数数组。
        groups: 与样本一一对应的组 ID，例如场景 ID 或视频 ID。

    Returns:
        各有效组 AUROC 的平均值；如果没有任何组同时包含正负样本，则返回
        ``None``。
    """
    return _mean_or_none(grouped_auroc_values(labels, scores, groups).values())


def grouped_auroc_values(
    labels: np.ndarray, scores: np.ndarray, groups: np.ndarray
) -> dict[str, float]:
    """计算每个组内的 AUROC。

    Args:
        labels: 二值标签数组。
        scores: 异常分数数组。
        groups: 组 ID 数组。

    Returns:
        从组名字符串到 AUROC 的字典。只返回正负样本都存在的组，因为只有这类
        组的 AUROC 有定义。
    """
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
    """计算每个组内异常样本的阈值召回率。

    Args:
        labels: 二值标签数组。
        predictions: 阈值化后的布尔预测数组。
        groups: 组 ID 数组。

    Returns:
        从组名字符串到召回率的字典。没有异常样本的组会被跳过。
    """
    values = {}
    for group in np.unique(groups):
        mask = (groups == group) & (labels == 1)
        if mask.any():
            values[str(group)] = float(np.mean(predictions[mask]))
    return values


def false_alarm_events_per_hour(
    labels: np.ndarray,
    predictions: np.ndarray,
    video_ids: np.ndarray,
    frame_indices: np.ndarray,
    fps: np.ndarray,
) -> float:
    """计算每小时误报事件数。

    Args:
        labels: 二值标签数组。
        predictions: 阈值化后的布尔预测数组。
        video_ids: 视频 ID 数组。事件边界只在同一视频内部计算，不跨视频连接。
        frame_indices: 视频内原始帧编号。函数会据此排序；编号不连续时开始新事件。
        fps: 每帧帧率数组，用于估算每个视频片段的时长。

    Returns:
        每小时误报事件数。一个误报事件定义为正常帧上的连续正预测片段；片段的
        第一帧或从负预测跳到正预测的位置计为一个事件。
    """
    events = 0
    total_hours = 0.0
    for video in np.unique(video_ids):
        mask = video_ids == video
        order = np.argsort(frame_indices[mask], kind="mergesort")
        ordered_frames = frame_indices[mask][order]
        ordered_labels = labels[mask][order]
        ordered_predictions = predictions[mask][order]
        ordered_fps = fps[mask][order]
        false_positive = ordered_predictions & (ordered_labels == 0)
        events += int(false_positive[0]) if len(false_positive) else 0
        gaps = np.diff(ordered_frames) != 1
        events += int(np.sum(false_positive[1:] & (~false_positive[:-1] | gaps)))
        if len(ordered_frames):
            represented_frames = int(ordered_frames[-1] - ordered_frames[0] + 1)
            total_hours += float(represented_frames / np.mean(ordered_fps) / 3600.0)
    return float(events / total_hours) if total_hours > 0 else 0.0


def subset_recall(labels: np.ndarray, predictions: np.ndarray, subset: np.ndarray) -> float | None:
    """计算某个子集内异常样本的召回率。

    Args:
        labels: 二值标签数组。
        predictions: 阈值化后的布尔预测数组。
        subset: 布尔掩码，指定要统计的样本子集。

    Returns:
        子集中正样本被检出的比例；如果子集中没有正样本则返回 ``None``。
    """
    positives = subset & (labels == 1)
    return float(np.mean(predictions[positives])) if positives.any() else None


def _safe_ratio(numerator: int, denominator: int) -> float | None:
    """安全地计算比值，避免零分母异常。"""
    return float(numerator / denominator) if denominator else None


def _mean_or_none(values) -> float | None:
    """返回值序列均值；空序列返回 ``None``。"""
    values = list(values)
    return float(np.mean(values)) if values else None


def _std_or_none(values) -> float | None:
    """返回值序列标准差；空序列返回 ``None``。"""
    values = list(values)
    return float(np.std(values)) if values else None
