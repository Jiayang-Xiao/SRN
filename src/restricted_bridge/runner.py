"""restricted bridge 实验主运行器。

runner 负责把配置矩阵展开成多随机种子、多方法、多评分器的实验：读取冻结特征、
训练可训练表示、抽取各切分 embedding、拟合无监督异常评分器、根据源域/目标
正常样本校准阈值，并把每次运行的 checkpoint、metrics、CSV 和汇总 JSON 写入
输出目录。
"""

from __future__ import annotations

import csv
import copy
import json
import logging
import random
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn

from .data import FeatureData, load_feature_data, validate_feature_data
from .metrics import evaluate_scores, source_normal_threshold
from .models import (
    AdversarialResidual,
    IdentityRepresentation,
    SRN,
    representation_loss,
)
from .scorers import build_scorer


TRAINABLE_METHODS = {
    "adversarial_residual", "full_srn", "srn_without_elos", "srn_residual_only"
}
ELOS_METHODS = {"full_srn", "elos_without_srn"}


def run_experiment(config: dict[str, Any], output_dir: str | Path | None = None) -> dict:
    """运行完整的 restricted bridge 实验矩阵。

    Args:
        config: 已校验的实验配置字典，通常来自 ``load_config``。函数会读取
            ``data``、``seeds``、``matrix``、``model``、``training``、
            ``scorer``、``evaluation`` 和 ``output`` 等子树。
        output_dir: 可选输出目录。为 ``None`` 时使用 ``config["output"]["dir"]``。

    Returns:
        实验结果 payload。包含运行状态、设备、协议摘要、每个 seed/method 的
        详细结果，以及按方法聚合的指标均值/标准差。

    Side Effects:
        在输出目录写入 ``run.log``、``resolved_config.json``、``results.json``、
        ``results.csv``，并为每个 seed/matrix entry 写入 checkpoint 和
        ``metrics.json``。

    Notes:
        当前实现固定在 CPU 上运行冻结特征矩阵；视觉骨干特征提取由独立的、
        可审计脚本完成。
    """
    run_dir = Path(output_dir or config["output"]["dir"]).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    logger = _configure_logging(run_dir / "run.log")
    _write_json(run_dir / "resolved_config.json", _json_safe_config(config))
    all_runs: list[dict] = []
    protocol_reports: list[dict] = []

    for seed in config["seeds"]:
        _seed_everything(seed)
        data = load_feature_data(config["data"], seed)
        protocol = validate_feature_data(data, config["data"])
        protocol_reports.append({"seed": seed, **protocol})
        for entry in config["matrix"]:
            if seed not in entry.get("seeds", config["seeds"]):
                continue
            logger.info("seed=%s run=%s method=%s scorer=%s", seed, entry["name"], entry["method"], entry["scorer"])
            result = _run_one(config, data, entry, seed, run_dir, logger)
            all_runs.append(result)

    aggregate = _aggregate(all_runs)
    payload = {
        "status": "synthetic_dry_run_only" if config["data"]["type"] == "synthetic" else "pilot",
        "device": "cpu",
        "protocol": protocol_reports,
        "runs": all_runs,
        "aggregate": aggregate,
        "calibration_only_control": _calibration_control(all_runs),
    }
    _write_json(run_dir / "results.json", payload)
    _write_csv(run_dir / "results.csv", all_runs)
    logger.info("completed %d run entries on CPU", len(all_runs))
    return payload


def _run_one(
    config: dict,
    data: FeatureData,
    entry: dict,
    seed: int,
    run_dir: Path,
    logger: logging.Logger,
) -> dict:
    """运行单个 seed 与单个矩阵条目的实验。

    Args:
        config: 全局实验配置。
        data: 当前 seed 对应的特征数据。
        entry: 矩阵中的一个方法/评分器配置项，至少包含 ``name``、``method`` 和
            ``scorer``。
        seed: 当前随机种子。
        run_dir: 整个实验的输出根目录。
        logger: 实验日志记录器。

    Returns:
        单次运行结果字典。包含 strict zero-shot 与 target-normal calibration
        两套阈值评估结果、诊断指标、训练损失和 checkpoint 路径。

    Side Effects:
        在 ``run_dir / seed_<seed> / <entry name>`` 下写入 ``checkpoint.pt`` 和
        ``metrics.json``。
    """
    method = entry["method"]
    indices = {split: data.indices(split) for split in ("train", "source_val", "target_calibration", "test")}
    train_scenes = sorted(np.unique(data.scene_id[indices["train"]]))
    scene_to_index = {scene: index for index, scene in enumerate(train_scenes)}
    scene_means = {
        scene: data.features[indices["train"]][data.scene_id[indices["train"]] == scene].mean(axis=0)
        for scene in train_scenes
    }
    global_scene_mean = data.features[indices["train"]].mean(axis=0)

    model = _build_model(method, data.feature_dim, len(train_scenes), config["model"])
    history: list[dict] = []
    selection: dict[str, Any] | None = None
    if method in TRAINABLE_METHODS:
        # 只有显式表示学习方法需要训练；纯基线直接使用固定变换或 identity。
        history, selection = _train_model(
            model, method, data, indices["train"], indices["source_val"],
            scene_to_index, scene_means,
            config["training"], seed, logger
        )

    method_dir = run_dir / f"seed_{seed}" / entry["name"]
    method_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = method_dir / "checkpoint.pt"
    torch.save(
        {
            "method": method,
            "seed": seed,
            "model_state": model.state_dict(),
            "feature_dim": data.feature_dim,
            "scene_to_index": scene_to_index,
            "training_history": history,
            "model_selection": selection,
        },
        checkpoint,
    )

    embeddings = {}
    for split, split_indices in indices.items():
        # 每个切分都先投影到同一个表示空间，再交给无监督评分器。
        embeddings[split] = _represent(
            model, method, data, split_indices, scene_means, global_scene_mean
        )

    elos_without_srn = None
    if method == "elos_without_srn":
        elos_without_srn = _elos_scorer_diagnostic(
            embeddings["train"], data.scene_id[indices["train"]], entry["scorer"],
            config["scorer"], seed
        )
    scorer = build_scorer(entry["scorer"], config["scorer"])
    scorer.fit(embeddings["train"], seed)
    scores = {split: scorer.score(values) for split, values in embeddings.items()}
    source_fpr = float(config["evaluation"]["source_threshold_fpr"])
    # strict zero-shot 阈值只看源域正常验证集；calibrated 阈值允许使用目标正常样本。
    source_threshold = source_normal_threshold(scores["source_val"], source_fpr)
    target_threshold = source_normal_threshold(scores["target_calibration"], source_fpr)
    test_idx = indices["test"]
    test_scene_ids = np.asarray([
        f"{dataset}/{scene}" for dataset, scene in
        zip(data.dataset_id[test_idx], data.scene_id[test_idx])
    ])
    test_video_ids = np.asarray([
        f"{dataset}/{video}" for dataset, video in
        zip(data.dataset_id[test_idx], data.video_id[test_idx])
    ])
    strict = evaluate_scores(
        data.label[test_idx], scores["test"], source_threshold, test_scene_ids,
        test_video_ids, data.frame_index[test_idx], data.fps[test_idx],
        data.location_dependent[test_idx]
    )
    calibrated = evaluate_scores(
        data.label[test_idx], scores["test"], target_threshold, test_scene_ids,
        test_video_ids, data.frame_index[test_idx], data.fps[test_idx],
        data.location_dependent[test_idx]
    )
    residuals = {
        split: _residual_representation(
            model, method, data, split_indices, scene_means, global_scene_mean
        )
        for split, split_indices in indices.items()
    }
    diagnostics = _diagnostics(
        data, indices, embeddings, residuals, scene_to_index
    )
    score_artifact = method_dir / "scores.npz"
    np.savez_compressed(
        score_artifact,
        test_scores=np.asarray(scores["test"], dtype=np.float64),
        source_val_scores=np.asarray(scores["source_val"], dtype=np.float64),
        target_calibration_scores=np.asarray(scores["target_calibration"], dtype=np.float64),
        test_labels=data.label[test_idx],
        dataset_id=data.dataset_id[test_idx],
        scene_id=data.scene_id[test_idx],
        video_id=data.video_id[test_idx],
        frame_index=data.frame_index[test_idx],
        fps=data.fps[test_idx],
    )
    result = {
        "name": entry["name"],
        "method": method,
        "scorer": entry["scorer"],
        "seed": seed,
        "strict_zero_shot": strict,
        "target_normal_calibration": calibrated,
        "source_threshold_transfer": strict,
        "source_threshold": source_threshold,
        "target_calibrated_threshold": target_threshold,
        "train_loss_final": (
            history[selection["selected_epoch"]]["loss"]["total"]
            if history and selection else None
        ),
        "elos_validation_final": (
            selection["selected_score"]
            if selection and method in ELOS_METHODS else elos_without_srn
        ),
        "diagnostics": diagnostics,
        "model_selection": selection,
        "evaluation_type": (
            "simulation_only" if config["data"]["type"] == "synthetic" else "real_gt"
        ),
        "score_artifact": str(score_artifact),
        "checkpoint": str(checkpoint),
    }
    _write_json(method_dir / "metrics.json", result)
    return result


def _build_model(method: str, feature_dim: int, num_scenes: int, config: dict) -> nn.Module:
    """根据方法名称构造表示模型。

    Args:
        method: 实验方法名称，来自配置矩阵。
        feature_dim: 冻结特征维度。
        num_scenes: 训练源场景数量。
        config: 模型配置子树。

    Returns:
        对应方法的 PyTorch 模型。非训练型或纯基线方法返回
        ``IdentityRepresentation``，由 ``_represent`` 在必要时实现额外变换。
    """
    if method == "adversarial_residual":
        return AdversarialResidual(feature_dim, num_scenes, float(config["adversarial_weight"]))
    if method in {"full_srn", "srn_without_elos", "srn_residual_only"}:
        return SRN(
            feature_dim=feature_dim,
            scene_token_dim=int(config["scene_token_dim"]),
            scene_predictor_rank=int(config["scene_predictor_rank"]),
            context_dim=int(config["context_dim"]),
            num_scenes=num_scenes,
            context_lambda=float(config["context_lambda"]),
            use_context=method != "srn_residual_only",
            adversarial_weight=float(config["adversarial_weight"]),
        )
    return IdentityRepresentation()


def _train_model(
    model: nn.Module,
    method: str,
    data: FeatureData,
    train_indices: np.ndarray,
    source_val_indices: np.ndarray,
    scene_to_index: dict[str, int],
    scene_means: dict[str, np.ndarray],
    config: dict,
    seed: int,
    logger: logging.Logger,
) -> tuple[list[dict], dict[str, Any]]:
    """训练一个可学习的表示模型。

    Args:
        model: 待训练的表示模型。
        method: 方法名称。ELOS 方法会启用留一源场景验证。
        data: 特征数据对象。
        train_indices: 训练切分样本下标。
        scene_to_index: 源场景 ID 到分类标签的映射。
        scene_means: 每个源场景的训练特征均值。
        config: 训练配置子树，包含学习率、epoch 数和损失权重。
        seed: 当前随机种子。当前函数内部不直接使用，但保留接口便于记录和扩展。
        logger: 实验日志记录器。

    Returns:
        逐 epoch 训练历史列表。每个元素包含 epoch、可选留出场景、损失分量，以及
        ELOS 方法的留出场景验证分数。
    """
    del seed
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=float(config["learning_rate"]))
    features_all = torch.from_numpy(data.features[train_indices])
    scene_names = data.scene_id[train_indices]
    scene_labels_all = torch.tensor([scene_to_index[x] for x in scene_names], dtype=torch.long)
    targets_all = torch.from_numpy(np.stack([scene_means[x] for x in scene_names]).astype(np.float32))
    scenes = sorted(scene_to_index)
    validation_features = torch.from_numpy(data.features[source_val_indices])
    validation_scene_names = data.scene_id[source_val_indices]
    history = []
    best_state = copy.deepcopy(model.state_dict())
    best_score = float("inf")
    best_epoch = -1
    criterion = (
        "elos_all_source_scenes_source_normal"
        if method in ELOS_METHODS else "source_normal_validation"
    )
    for epoch in range(int(config["epochs"])):
        # ELOS 方法每个 epoch 轮流留出一个源场景，用其检验表示的跨场景稳定性。
        held_out = scenes[epoch % len(scenes)] if method in ELOS_METHODS else None
        support_mask_np = scene_names != held_out if held_out is not None else np.ones(len(scene_names), dtype=bool)
        support_mask = torch.from_numpy(support_mask_np)
        optimizer.zero_grad(set_to_none=True)
        output = model(features_all[support_mask])
        loss, parts = representation_loss(
            model, output, features_all[support_mask], targets_all[support_mask],
            scene_labels_all[support_mask], config["loss_weights"]
        )
        loss.backward()
        optimizer.step()
        record: dict[str, Any] = {"epoch": epoch, "held_out_scene": held_out, "loss": parts}
        if held_out is not None:
            validation_by_scene: dict[str, float] = {}
            with torch.no_grad():
                for candidate in scenes:
                    candidate_support = torch.from_numpy(scene_names != candidate)
                    candidate_val = torch.from_numpy(validation_scene_names == candidate)
                    if not bool(candidate_support.any()) or not bool(candidate_val.any()):
                        continue
                    support_center = model(
                        features_all[candidate_support]
                    ).embedding.mean(dim=0)
                    heldout_embedding = model(validation_features[candidate_val]).embedding
                    validation_by_scene[candidate] = float(
                        (heldout_embedding - support_center).square().mean()
                    )
            record["elos_validation_by_scene"] = validation_by_scene
            record["elos_validation"] = validation_by_scene.get(held_out)
            if validation_by_scene:
                validation_mean = float(np.mean(list(validation_by_scene.values())))
                record["elos_validation_mean"] = validation_mean
                if validation_mean < best_score:
                    best_score = validation_mean
                    best_epoch = epoch
                    best_state = copy.deepcopy(model.state_dict())
        else:
            with torch.no_grad():
                train_center = model(features_all).embedding.mean(dim=0)
                validation_embedding = model(validation_features).embedding
                validation_score = float(
                    (validation_embedding - train_center).square().mean()
                )
            record["source_normal_validation"] = validation_score
            if validation_score < best_score:
                best_score = validation_score
                best_epoch = epoch
                best_state = copy.deepcopy(model.state_dict())
        history.append(record)
    if best_epoch < 0:
        best_epoch = len(history) - 1
        best_score = float(
            history[-1].get("elos_validation")
            or history[-1].get("source_normal_validation")
            or history[-1]["loss"]["total"]
        )
        best_state = copy.deepcopy(model.state_dict())
    model.load_state_dict(best_state)
    history[best_epoch]["selected_checkpoint"] = True
    selection = {
        "criterion": criterion,
        "selected_epoch": best_epoch,
        "selected_score": best_score,
        "uses_anomaly_labels": False,
    }
    logger.info(
        "trained method=%s epochs=%d selected_epoch=%d selection_score=%.6f",
        method, len(history), best_epoch, best_score,
    )
    return history, selection


def _represent(
    model: nn.Module,
    method: str,
    data: FeatureData,
    indices: np.ndarray,
    scene_means: dict[str, np.ndarray],
    global_scene_mean: np.ndarray,
) -> np.ndarray:
    """把指定样本切分转换为异常评分器使用的 embedding。

    Args:
        model: 表示模型。对纯均值扣除基线，该参数只用于保持统一接口。
        method: 方法名称，决定是使用模型前向传播还是手工基线变换。
        data: 特征数据对象。
        indices: 要表示的样本下标。
        scene_means: 源训练场景均值字典。
        global_scene_mean: 源训练集全局均值，用于未知场景的 fallback。

    Returns:
        形状为 ``[len(indices), embedding_dim]`` 的 NumPy embedding 矩阵。

    Raises:
        ValueError: 当 ``background_mean`` 方法需要背景特征但数据中不存在
            ``background_features`` 时抛出。
    """
    features = data.features[indices]
    if method == "scene_mean":
        # 测试场景可能是未见场景；没有对应源场景均值时退回源域全局均值。
        means = np.stack([scene_means.get(scene, global_scene_mean) for scene in data.scene_id[indices]])
        return features - means
    if method == "background_mean":
        if data.background_features is None:
            raise ValueError("background_mean requires label-free background_features in the cache")
        return features - data.background_features[indices]
    model.eval()
    with torch.no_grad():
        return model(torch.from_numpy(features)).embedding.cpu().numpy()


def _residual_representation(
    model: nn.Module,
    method: str,
    data: FeatureData,
    indices: np.ndarray,
    scene_means: dict[str, np.ndarray],
    global_scene_mean: np.ndarray,
) -> np.ndarray:
    """Return the residual view used for independent scene-leakage diagnostics."""
    if method in {"scene_mean", "background_mean"}:
        return _represent(model, method, data, indices, scene_means, global_scene_mean)
    model.eval()
    with torch.no_grad():
        return model(torch.from_numpy(data.features[indices])).residual.cpu().numpy()


def _diagnostics(
    data: FeatureData,
    indices: dict,
    embeddings: dict[str, np.ndarray],
    residuals: dict[str, np.ndarray],
    scene_to_index: dict,
) -> dict:
    """用独立最近质心 probe 计算源正常验证诊断指标。

    Args:
        data: 特征数据对象。
        indices: 各切分样本下标字典。
        embeddings: 各切分的最终表示。
        residuals: 各切分的残差表示。
        scene_to_index: 源场景 ID 到分类标签的映射。

    Returns:
        诊断字典。probe 只在训练正常视频上拟合并在不重叠的源正常验证视频上
        评估；单源场景时准确率不可定义，返回 ``None``。
    """
    train_idx = indices["train"]
    val_idx = indices["source_val"]
    train_labels = np.asarray([scene_to_index[x] for x in data.scene_id[train_idx]])
    known_val = np.asarray([x in scene_to_index for x in data.scene_id[val_idx]])
    val_labels = np.asarray(
        [scene_to_index.get(x, -1) for x in data.scene_id[val_idx]], dtype=np.int64
    )
    residual_probe = _nearest_centroid_probe_accuracy(
        residuals["train"], train_labels,
        residuals["source_val"][known_val], val_labels[known_val],
    )
    embedding_probe = _nearest_centroid_probe_accuracy(
        embeddings["train"], train_labels,
        embeddings["source_val"][known_val], val_labels[known_val],
    )
    ratio = float(
        np.var(residuals["train"]) / max(np.var(data.features[train_idx]), 1e-12)
    )
    return {
        "scene_probe_accuracy": residual_probe,
        "scene_probe_protocol": "independent_nearest_centroid_train_to_source_val",
        "independent_residual_scene_probe_accuracy": residual_probe,
        "independent_embedding_scene_probe_accuracy": embedding_probe,
        "scene_probe_chance": 1.0 / len(scene_to_index),
        "scene_probe_validation_samples": int(np.sum(known_val)),
        "residual_variance_ratio": ratio,
    }


def _nearest_centroid_probe_accuracy(
    train_features: np.ndarray,
    train_labels: np.ndarray,
    validation_features: np.ndarray,
    validation_labels: np.ndarray,
) -> float | None:
    """Fit a fresh source-normal scene probe and evaluate only held-out videos."""
    if not len(validation_features) or len(np.unique(train_labels)) < 2:
        return None
    classes = np.unique(train_labels)
    centers = np.stack([train_features[train_labels == label].mean(axis=0) for label in classes])
    distances = (
        np.sum(validation_features * validation_features, axis=1, keepdims=True)
        + np.sum(centers * centers, axis=1)[None, :]
        - 2.0 * validation_features @ centers.T
    )
    predictions = classes[np.argmin(distances, axis=1)]
    return float(np.mean(predictions == validation_labels))


def _elos_scorer_diagnostic(
    embeddings: np.ndarray,
    scene_ids: np.ndarray,
    scorer_name: str,
    scorer_config: dict,
    seed: int,
) -> float:
    """用留一场景方式诊断评分器的跨源场景偏移。

    Args:
        embeddings: 训练 embedding 矩阵。
        scene_ids: 与训练 embedding 对应的源场景 ID。
        scorer_name: 评分器名称。
        scorer_config: 评分器配置子树。
        seed: 拟合评分器时使用的随机种子。

    Returns:
        每个被留出源场景的平均异常分数，再对场景取均值。数值越大通常表示训练
        源场景之间分布差异越明显。
    """
    heldout_scores = []
    for scene in np.unique(scene_ids):
        support = scene_ids != scene
        heldout = ~support
        scorer = build_scorer(scorer_name, scorer_config)
        scorer.fit(embeddings[support], seed)
        heldout_scores.append(float(np.mean(scorer.score(embeddings[heldout]))))
    return float(np.mean(heldout_scores))


def _aggregate(runs: list[dict]) -> list[dict]:
    """按矩阵条目聚合多 seed 的 strict zero-shot 指标。

    Args:
        runs: ``_run_one`` 返回的所有单次运行结果。

    Returns:
        聚合结果列表。每个元素对应一个矩阵条目，包含参与聚合的 seed，以及核心
        指标的均值和标准差。不可定义的 ``None`` 指标会被过滤。
    """
    aggregates = []
    for name in sorted({run["name"] for run in runs}):
        selected = [run for run in runs if run["name"] == name]
        tracks = {}
        for track in ("strict_zero_shot", "target_normal_calibration"):
            metrics = {}
            for metric in (
                "micro_auroc", "macro_scene_auroc", "macro_video_auroc",
                "worst_scene_auroc", "scene_auroc_std", "auprc",
                "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr",
                "false_alarm_events_per_hour", "threshold_recall",
                "threshold_false_positive_rate", "location_dependent_recall",
                "location_independent_recall",
            ):
                values = [run[track].get(metric) for run in selected]
                values = [value for value in values if value is not None]
                metrics[metric] = {
                    "mean": float(np.mean(values)) if values else None,
                    "std": float(np.std(values)) if values else None,
                    "count": len(values),
                }
            tracks[track] = metrics
        diagnostic_metrics = {}
        for metric in (
            "independent_residual_scene_probe_accuracy",
            "independent_embedding_scene_probe_accuracy",
            "residual_variance_ratio",
        ):
            values = [run["diagnostics"].get(metric) for run in selected]
            values = [value for value in values if value is not None]
            diagnostic_metrics[metric] = {
                "mean": float(np.mean(values)) if values else None,
                "std": float(np.std(values)) if values else None,
                "count": len(values),
            }
        aggregates.append({
            "name": name,
            "seeds": [run["seed"] for run in selected],
            "tracks": tracks,
            "diagnostics": diagnostic_metrics,
        })
    return aggregates


def _calibration_control(runs: list[dict]) -> list[dict]:
    """Expose calibration-only effects without duplicating a representation row."""
    controls = []
    for run in runs:
        if run["name"] != "raw_prototype":
            continue
        controls.append({
            "seed": run["seed"],
            "representation": "raw",
            "scorer": "prototype",
            "strict_threshold_recall": run["strict_zero_shot"]["threshold_recall"],
            "strict_threshold_fpr": run["strict_zero_shot"]["threshold_false_positive_rate"],
            "target_normal_calibrated_recall": run["target_normal_calibration"]["threshold_recall"],
            "target_normal_calibrated_fpr": run["target_normal_calibration"]["threshold_false_positive_rate"],
            "uses_target_anomalies": False,
        })
    return controls


def _seed_everything(seed: int) -> None:
    """设置 Python、NumPy 和 PyTorch 的随机种子。

    Args:
        seed: 实验随机种子。

    Notes:
        ``torch.use_deterministic_algorithms(True)`` 会要求 PyTorch 使用确定性算子。
        这有助于复现 CPU pilot，但如果未来迁移到 GPU/复杂算子，可能需要处理
        不支持确定性的算子报错。
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)


def _configure_logging(path: Path) -> logging.Logger:
    """创建同时写文件和标准错误流的日志记录器。

    Args:
        path: 日志文件路径。

    Returns:
        已配置好的 ``logging.Logger``。logger 名称包含日志路径，避免不同输出
        目录之间 handler 混用。
    """
    logger = logging.getLogger(f"restricted_bridge:{path}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler = logging.FileHandler(path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


def _write_json(path: Path, payload: object) -> None:
    """把对象以稳定格式写入 JSON 文件。

    Args:
        path: 输出 JSON 路径。
        payload: 可被 ``json.dump`` 序列化的对象。

    Side Effects:
        自动创建父目录，并以排序键、两空格缩进和末尾换行写入文件。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=True, indent=2, sort_keys=True)
        handle.write("\n")


def _write_csv(path: Path, runs: list[dict]) -> None:
    """把每次运行的核心 strict zero-shot 指标写成 CSV。

    Args:
        path: 输出 CSV 路径。
        runs: ``_run_one`` 返回的运行结果列表。

    Notes:
        CSV 只保留最常用于快速比较的标量指标；完整分场景/分视频指标仍在
        ``results.json`` 和各自的 ``metrics.json`` 中。
    """
    fields = [
        "name", "method", "scorer", "seed", "micro_auroc", "auprc",
        "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr", "false_alarm_events_per_hour",
        "threshold_recall", "threshold_false_positive_rate", "source_threshold",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for run in runs:
            strict = run["strict_zero_shot"]
            writer.writerow({
                "name": run["name"], "method": run["method"], "scorer": run["scorer"],
                "seed": run["seed"], "source_threshold": run["source_threshold"],
                **{field: strict.get(field) for field in fields if field in strict},
            })


def _json_safe_config(config: dict) -> dict:
    """移除内部字段，得到适合落盘的配置副本。

    Args:
        config: 原始配置字典。

    Returns:
        不包含以下划线开头键的浅拷贝。当前主要用于去掉 ``_config_path`` 等内部
        运行时字段。
    """
    return {key: value for key, value in config.items() if not key.startswith("_")}
