"""配置加载与实验矩阵校验工具。

本模块只负责把 YAML 配置读成普通 Python 字典，并在真正启动实验前检查
数据来源、随机种子、方法矩阵和模型维度是否满足 restricted bridge 实验协议。
这里的校验尽量提前失败，避免训练或评估运行一半后才暴露配置错误。
"""

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
}
SCORERS = {"knn", "gaussian", "prototype"}


def load_config(path: str | Path) -> dict[str, Any]:
    """读取并校验实验配置文件。

    Args:
        path: YAML 配置文件路径。可以传入字符串或 ``Path`` 对象；函数会将其
            解析为绝对路径，并写入返回字典的 ``_config_path`` 字段，方便后续
            记录 resolved config 或排查实验来源。

    Returns:
        通过基础结构校验的配置字典。返回值保持 YAML 中的层级结构不变，仅额外
        添加 ``_config_path``。

    Raises:
        ValueError: 当 YAML 根节点不是映射，或配置字段不满足
            ``validate_config`` 的协议约束时抛出。
        OSError: 当配置文件无法打开或读取时由底层文件系统调用抛出。
        yaml.YAMLError: 当 YAML 语法非法时由 PyYAML 抛出。
    """
    config_path = Path(path).resolve()
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError("configuration root must be a mapping")
    config["_config_path"] = str(config_path)
    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    """检查配置是否能驱动一次完整的 restricted bridge 实验。

    Args:
        config: 已经从 YAML 反序列化得到的配置字典。函数期望至少包含
            ``data``、``seeds``、``matrix`` 和 ``model`` 等实验关键字段。

    Raises:
        ValueError: 当数据类型、数据路径、随机种子、方法矩阵、评分器或模型
            维度不合法时抛出。错误消息会尽量指出具体字段，便于直接修改配置。

    Notes:
        该函数不返回值；它的作用是作为启动实验前的“协议门禁”。只要函数正常
        返回，就说明配置在结构层面可执行，但不代表数据文件内容一定有效，数据
        级别检查由 ``validate_feature_data`` 完成。
    """
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
        entry_seeds = entry.get("seeds")
        if entry_seeds is not None:
            if (
                not isinstance(entry_seeds, list)
                or not entry_seeds
                or not all(isinstance(seed, int) for seed in entry_seeds)
                or not set(entry_seeds).issubset(seeds)
            ):
                raise ValueError(
                    f"matrix seeds for {name} must be a non-empty subset of top-level seeds"
                )

    model = config.get("model", {})
    feature_dim = int(data.get("feature_dim", model.get("feature_dim", 0)))
    token_dim = int(model.get("scene_token_dim", 0))
    if feature_dim <= 0 or token_dim <= 0 or token_dim >= feature_dim:
        raise ValueError("scene_token_dim must be positive and smaller than feature_dim")
    predictor_rank = int(model.get("scene_predictor_rank", token_dim))
    if predictor_rank <= 0 or predictor_rank > token_dim:
        raise ValueError("scene_predictor_rank must be positive and cannot exceed scene_token_dim")
    context_dim = int(model.get("context_dim", 0))
    if context_dim <= 0:
        raise ValueError("context_dim must be positive")

    training = config.get("training", {})
    if int(training.get("epochs", 0)) <= 0:
        raise ValueError("training.epochs must be positive")
    if float(training.get("learning_rate", 0.0)) <= 0.0:
        raise ValueError("training.learning_rate must be positive")

    scorer = config.get("scorer", {})
    for key in ("knn_k", "prototype_count", "distance_batch_size"):
        if key in scorer and int(scorer[key]) <= 0:
            raise ValueError(f"scorer.{key} must be positive")
    shrinkage = float(scorer.get("gaussian_shrinkage", 0.1))
    if not 0.0 < shrinkage <= 1.0:
        raise ValueError("scorer.gaussian_shrinkage must be in (0, 1]")

    source_fpr = float(config.get("evaluation", {}).get("source_threshold_fpr", 0.0))
    if not 0.0 < source_fpr < 1.0:
        raise ValueError("evaluation.source_threshold_fpr must be in (0, 1)")
