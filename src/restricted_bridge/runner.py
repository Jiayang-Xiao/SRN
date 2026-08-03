from __future__ import annotations

import csv
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
    if method in TRAINABLE_METHODS:
        history = _train_model(
            model, method, data, indices["train"], scene_to_index, scene_means,
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
        },
        checkpoint,
    )

    embeddings = {}
    for split, split_indices in indices.items():
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
    source_threshold = source_normal_threshold(scores["source_val"], source_fpr)
    target_threshold = source_normal_threshold(scores["target_calibration"], source_fpr)
    test_idx = indices["test"]
    strict = evaluate_scores(
        data.label[test_idx], scores["test"], source_threshold, data.scene_id[test_idx],
        data.video_id[test_idx], data.fps[test_idx], data.location_dependent[test_idx]
    )
    calibrated = evaluate_scores(
        data.label[test_idx], scores["test"], target_threshold, data.scene_id[test_idx],
        data.video_id[test_idx], data.fps[test_idx], data.location_dependent[test_idx]
    )
    diagnostics = _diagnostics(model, data, indices, scene_to_index)
    result = {
        "name": entry["name"],
        "method": method,
        "scorer": entry["scorer"],
        "seed": seed,
        "strict_zero_shot": strict,
        "target_normal_calibration": calibrated,
        "source_threshold": source_threshold,
        "target_calibrated_threshold": target_threshold,
        "train_loss_final": history[-1]["loss"]["total"] if history else None,
        "elos_validation_final": (
            history[-1].get("elos_validation") if history else elos_without_srn
        ),
        "diagnostics": diagnostics,
        "checkpoint": str(checkpoint),
    }
    _write_json(method_dir / "metrics.json", result)
    return result


def _build_model(method: str, feature_dim: int, num_scenes: int, config: dict) -> nn.Module:
    if method == "adversarial_residual":
        return AdversarialResidual(feature_dim, num_scenes, float(config["adversarial_weight"]))
    if method in {"full_srn", "srn_without_elos", "srn_residual_only"}:
        return SRN(
            feature_dim=feature_dim,
            scene_token_dim=int(config["scene_token_dim"]),
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
    scene_to_index: dict[str, int],
    scene_means: dict[str, np.ndarray],
    config: dict,
    seed: int,
    logger: logging.Logger,
) -> list[dict]:
    del seed
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=float(config["learning_rate"]))
    features_all = torch.from_numpy(data.features[train_indices])
    scene_names = data.scene_id[train_indices]
    scene_labels_all = torch.tensor([scene_to_index[x] for x in scene_names], dtype=torch.long)
    targets_all = torch.from_numpy(np.stack([scene_means[x] for x in scene_names]).astype(np.float32))
    scenes = sorted(scene_to_index)
    history = []
    for epoch in range(int(config["epochs"])):
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
            heldout_mask = torch.from_numpy(scene_names == held_out)
            with torch.no_grad():
                support_center = model(features_all[support_mask]).embedding.mean(dim=0)
                heldout_embedding = model(features_all[heldout_mask]).embedding
                record["elos_validation"] = float(
                    (heldout_embedding - support_center).square().mean()
                )
        history.append(record)
    logger.info("trained method=%s epochs=%d final_loss=%.6f", method, len(history), history[-1]["loss"]["total"])
    return history


def _represent(
    model: nn.Module,
    method: str,
    data: FeatureData,
    indices: np.ndarray,
    scene_means: dict[str, np.ndarray],
    global_scene_mean: np.ndarray,
) -> np.ndarray:
    features = data.features[indices]
    if method == "scene_mean":
        means = np.stack([scene_means.get(scene, global_scene_mean) for scene in data.scene_id[indices]])
        return features - means
    if method == "background_mean":
        if data.background_features is None:
            raise ValueError("background_mean requires label-free background_features in the cache")
        return features - data.background_features[indices]
    model.eval()
    with torch.no_grad():
        return model(torch.from_numpy(features)).embedding.cpu().numpy()


def _diagnostics(model: nn.Module, data: FeatureData, indices: dict, scene_to_index: dict) -> dict:
    if not isinstance(model, (SRN, AdversarialResidual)):
        return {"scene_probe_accuracy": None, "residual_variance_ratio": None}
    train_idx = indices["train"]
    with torch.no_grad():
        output = model(torch.from_numpy(data.features[train_idx]))
        predictions = output.scene_logits.argmax(dim=1).numpy()
    labels = np.asarray([scene_to_index[x] for x in data.scene_id[train_idx]])
    ratio = float(np.var(output.residual.numpy()) / max(np.var(data.features[train_idx]), 1e-12))
    return {
        "scene_probe_accuracy": float(np.mean(predictions == labels)),
        "residual_variance_ratio": ratio,
    }


def _elos_scorer_diagnostic(
    embeddings: np.ndarray,
    scene_ids: np.ndarray,
    scorer_name: str,
    scorer_config: dict,
    seed: int,
) -> float:
    heldout_scores = []
    for scene in np.unique(scene_ids):
        support = scene_ids != scene
        heldout = ~support
        scorer = build_scorer(scorer_name, scorer_config)
        scorer.fit(embeddings[support], seed)
        heldout_scores.append(float(np.mean(scorer.score(embeddings[heldout]))))
    return float(np.mean(heldout_scores))


def _aggregate(runs: list[dict]) -> list[dict]:
    aggregates = []
    for name in sorted({run["name"] for run in runs}):
        selected = [run for run in runs if run["name"] == name]
        metrics = {}
        for metric in (
            "micro_auroc", "auprc", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr",
            "false_alarm_events_per_hour", "threshold_recall", "threshold_false_positive_rate",
        ):
            values = [run["strict_zero_shot"][metric] for run in selected]
            values = [value for value in values if value is not None]
            metrics[metric] = {
                "mean": float(np.mean(values)) if values else None,
                "std": float(np.std(values)) if values else None,
            }
        aggregates.append({"name": name, "seeds": [run["seed"] for run in selected], "metrics": metrics})
    return aggregates


def _seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)


def _configure_logging(path: Path) -> logging.Logger:
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
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=True, indent=2, sort_keys=True)
        handle.write("\n")


def _write_csv(path: Path, runs: list[dict]) -> None:
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
    return {key: value for key, value in config.items() if not key.startswith("_")}
