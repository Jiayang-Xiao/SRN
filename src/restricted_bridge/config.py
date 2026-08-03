from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


METHODS = {
    "raw",
    "scene_mean",
    "background_mean",
    "adversarial_residual",
    "full_srn",
    "srn_without_elos",
    "elos_without_srn",
    "srn_residual_only",
    "calibration_only",
}
SCORERS = {"knn", "gaussian", "prototype"}


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path).resolve()
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError("configuration root must be a mapping")
    config["_config_path"] = str(config_path)
    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    data = config.get("data", {})
    if data.get("type") not in {"synthetic", "npz"}:
        raise ValueError("data.type must be synthetic or npz")
    if data.get("type") == "npz" and not data.get("path"):
        raise ValueError("data.path is required for an npz feature cache")

    seeds = config.get("seeds")
    if not isinstance(seeds, list) or not seeds or not all(isinstance(x, int) for x in seeds):
        raise ValueError("seeds must be a non-empty list of integers")

    matrix = config.get("matrix")
    if not isinstance(matrix, list) or not matrix:
        raise ValueError("matrix must be a non-empty list")
    names: set[str] = set()
    for entry in matrix:
        if not isinstance(entry, dict):
            raise ValueError("each matrix entry must be a mapping")
        name = entry.get("name")
        if not name or name in names:
            raise ValueError(f"matrix entry names must be unique: {name!r}")
        names.add(name)
        if entry.get("method") not in METHODS:
            raise ValueError(f"unknown method for {name}: {entry.get('method')}")
        if entry.get("scorer") not in SCORERS:
            raise ValueError(f"unknown scorer for {name}: {entry.get('scorer')}")

    model = config.get("model", {})
    feature_dim = int(data.get("feature_dim", model.get("feature_dim", 0)))
    token_dim = int(model.get("scene_token_dim", 0))
    if feature_dim <= 0 or token_dim <= 0 or token_dim >= feature_dim:
        raise ValueError("scene_token_dim must be positive and smaller than feature_dim")
    if int(model.get("scene_predictor_rank", token_dim)) > token_dim:
        raise ValueError("scene_predictor_rank cannot exceed scene_token_dim")
