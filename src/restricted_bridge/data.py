"""特征数据加载、合成数据生成与协议完整性校验。

restricted bridge 实验只在冻结特征上运行，不在这里读取原始视频或训练视觉
骨干网络。本模块统一把合成数据或 ``.npz`` 特征缓存转换成 ``FeatureData``，
并检查切分、标签、视频边界和场景泛化约束，避免后续评分阶段混入训练泄漏。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


ALLOWED_SPLITS = {"train", "source_val", "target_calibration", "test"}


@dataclass(frozen=True)
class FeatureData:
    """冻结帧级特征及其元数据容器。

    Attributes:
        features: 形状为 ``[N, D]`` 的帧级特征矩阵，``N`` 是样本数，``D`` 是
            特征维度。所有实验方法都从该矩阵派生表示或异常分数。
        split: 每个样本所属的数据切分。允许值为 ``train``、``source_val``、
            ``target_calibration`` 和 ``test``。
        dataset_id: 每个样本所属数据集 ID。它与场景和视频 ID 组合使用，防止
            不同数据集中的同名实体被错误合并。
        scene_id: 每个样本所属场景 ID，用于场景均值基线、ELOS 留一场景验证
            和按场景统计 AUROC。
        video_id: 每个样本所属视频 ID。校验函数会确保同一个视频不会跨切分，
            避免相邻帧泄漏。
        frame_index: 样本在视频内的帧编号。与 ``video_id`` 组成唯一帧身份。
        label: 测试阶段使用的二值异常标签。非测试切分必须全为 0，以保证无
            异常训练/校准协议。
        fps: 每个样本对应视频的帧率，用于把误报事件数换算为每小时误报。
        location_dependent: 异常是否依赖位置的标记。``1`` 表示位置相关异常，
            ``0`` 表示位置无关异常，``-1`` 表示正常样本或未知。
        background_features: 可选的无标签背景特征。``background_mean`` 方法
            需要它来从原始特征中扣除背景项。
    """

    features: np.ndarray
    split: np.ndarray
    dataset_id: np.ndarray
    scene_id: np.ndarray
    video_id: np.ndarray
    frame_index: np.ndarray
    label: np.ndarray
    fps: np.ndarray
    location_dependent: np.ndarray
    background_features: np.ndarray | None = None

    def indices(self, split: str) -> np.ndarray:
        """返回指定切分的样本下标。

        Args:
            split: 要选择的数据切分名称，通常来自 ``ALLOWED_SPLITS``。

        Returns:
            一维整数数组，包含 ``self.split == split`` 的所有位置。返回值可
            直接用于切片 ``FeatureData`` 的各个数组字段。
        """
        return np.flatnonzero(self.split == split)

    @property
    def feature_dim(self) -> int:
        """返回特征矩阵的列数。

        Returns:
            ``features`` 的第二维大小，即每帧冻结特征的维度。
        """
        return int(self.features.shape[1])


def load_feature_data(config: dict, seed: int) -> FeatureData:
    """根据配置加载冻结特征数据。

    Args:
        config: 数据配置子树。``type`` 为 ``synthetic`` 时调用
            ``make_synthetic_features``；``type`` 为 ``npz`` 时从 ``path``
            指定的特征缓存读取数组。
        seed: 合成数据随机种子。对 ``npz`` 缓存无随机影响，但保留统一接口。

    Returns:
        已通过 ``validate_feature_data`` 检查的 ``FeatureData`` 实例。

    Raises:
        FileNotFoundError: 当 ``npz`` 缓存路径不存在或不是普通文件时抛出。
        ValueError: 当缓存缺少必需数组，或数组内容不满足实验协议时抛出。

    Notes:
        ``npz`` 缓存必须包含 ``features``、``split``、``dataset_id``、
        ``scene_id``、``video_id``、``frame_index``、``label`` 和 ``fps``。可选字段
        ``location_dependent`` 和 ``background_features`` 缺失时会分别用
        ``-1`` 标记和 ``None`` 补齐。
    """
    if config["type"] == "synthetic":
        return make_synthetic_features(config, seed)
    path = Path(config["path"]).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"frozen feature cache not found: {path}")
    with np.load(path, allow_pickle=False) as cache:
        required = {
            "features", "split", "dataset_id", "scene_id", "video_id",
            "frame_index", "label", "fps"
        }
        missing = sorted(required.difference(cache.files))
        if missing:
            raise ValueError(f"feature cache is missing arrays: {missing}")
        labels = np.asarray(cache["label"], dtype=np.int64)
        location = (
            np.asarray(cache["location_dependent"], dtype=np.int64)
            if "location_dependent" in cache.files
            else np.full(labels.shape, -1, dtype=np.int64)
        )
        background = (
            np.asarray(cache["background_features"], dtype=np.float32)
            if "background_features" in cache.files
            else None
        )
        data = FeatureData(
            features=np.asarray(cache["features"], dtype=np.float32),
            split=np.asarray(cache["split"]).astype(str),
            dataset_id=np.asarray(cache["dataset_id"]).astype(str),
            scene_id=np.asarray(cache["scene_id"]).astype(str),
            video_id=np.asarray(cache["video_id"]).astype(str),
            frame_index=np.asarray(cache["frame_index"], dtype=np.int64),
            label=labels,
            fps=np.asarray(cache["fps"], dtype=np.float32),
            location_dependent=location,
            background_features=background,
        )
    validate_feature_data(data, config)
    return data


def make_synthetic_features(config: dict, seed: int) -> FeatureData:
    """构造一个用于 dry-run 的合成帧级特征数据集。

    Args:
        config: 数据配置子树。可通过 ``feature_dim``、
            ``synthetic_frames_per_video`` 和 ``synthetic_source_scenes`` 控制
            特征维度、每个视频帧数和源域场景数。
        seed: NumPy 随机数生成器种子，保证 dry-run 数据可复现。

    Returns:
        合成的 ``FeatureData``。其中训练、源验证和目标校准样本都是正常样本，
        测试集中前三个视频带有一段异常片段。

    Notes:
        合成过程把特征拆成“场景背景偏移 + 事件扰动”。异常样本会在前若干维
        注入明显偏移，用于快速检查评分器、阈值和指标管线是否正常工作。
    """
    rng = np.random.default_rng(seed)
    dim = int(config.get("feature_dim", 16))
    frames = int(config.get("synthetic_frames_per_video", 12))
    source_scenes = int(config.get("synthetic_source_scenes", 3))
    scene_offsets = rng.normal(0.0, 2.0, size=(source_scenes + 1, dim))
    rows: list[tuple] = []

    def add_video(split: str, scene: int, video: int, anomalous: bool = False) -> None:
        """向 ``rows`` 追加一个合成视频的所有帧。

        Args:
            split: 视频所属切分。
            scene: 场景编号。源域场景和目标场景共享同一偏移表。
            video: 当前场景内的视频编号，用于构造稳定的 ``video_id``。
            anomalous: 是否在视频中间插入异常片段。
        """
        video_name = f"{split}_s{scene}_v{video}"
        background = np.repeat(scene_offsets[scene][None, :], frames, axis=0)
        background += rng.normal(0.0, 0.04, size=background.shape)
        event = rng.normal(0.0, 0.45, size=(frames, dim))
        labels = np.zeros(frames, dtype=np.int64)
        location = np.full(frames, -1, dtype=np.int64)
        if anomalous:
            start = frames // 3
            stop = min(frames, start + max(2, frames // 4))
            labels[start:stop] = 1
            location[start:stop] = video % 2
            event[start:stop, : max(2, dim // 4)] += 4.0
        features = background + event
        for frame in range(frames):
            rows.append(
                (features[frame], split, "synthetic", f"scene_{scene}", video_name, frame,
                 labels[frame], 25.0, location[frame], background[frame])
            )

    for scene in range(source_scenes):
        for video in range(3):
            add_video("train", scene, video)
        add_video("source_val", scene, 0)
    target_scene = source_scenes
    add_video("target_calibration", target_scene, 0)
    for video in range(4):
        add_video("test", target_scene, video, anomalous=video < 3)

    data = FeatureData(
        features=np.stack([row[0] for row in rows]).astype(np.float32),
        split=np.asarray([row[1] for row in rows]),
        dataset_id=np.asarray([row[2] for row in rows]),
        scene_id=np.asarray([row[3] for row in rows]),
        video_id=np.asarray([row[4] for row in rows]),
        frame_index=np.asarray([row[5] for row in rows], dtype=np.int64),
        label=np.asarray([row[6] for row in rows], dtype=np.int64),
        fps=np.asarray([row[7] for row in rows], dtype=np.float32),
        location_dependent=np.asarray([row[8] for row in rows], dtype=np.int64),
        background_features=np.stack([row[9] for row in rows]).astype(np.float32),
    )
    validate_feature_data(data, config)
    return data


def validate_feature_data(data: FeatureData, config: dict) -> dict[str, object]:
    """校验特征数据是否满足无泄漏实验协议。

    Args:
        data: 待检查的特征数据对象。
        config: 数据配置子树。函数会读取 ``feature_dim`` 和
            ``require_unseen_test_scene`` 等约束。

    Returns:
        一个可写入实验报告的协议摘要，包括样本数、特征维度、训练/测试场景、
        是否满足整视频切分，以及训练集中是否包含异常标签等信息。

    Raises:
        ValueError: 当特征矩阵非二维或含非有限值、元数据长度不一致、切分缺失、
            视频跨切分、帧身份重复、非测试集出现异常标签，或场景泛化约束不
            满足时抛出。

    Notes:
        这里的核心目标是防止评估协议被“无意中变容易”：同一视频不能同时出现在
        训练和测试；异常标签只能出现在最终测试；需要 whole-scene 泛化时训练
        场景和测试场景必须不相交。
    """
    count = data.features.shape[0]
    if data.features.ndim != 2 or not np.isfinite(data.features).all():
        raise ValueError("features must be a finite [N, D] array")
    expected_dim = int(config.get("feature_dim", data.feature_dim))
    if data.feature_dim != expected_dim:
        raise ValueError(
            f"feature dimension mismatch: cache={data.feature_dim}, config={expected_dim}"
        )
    for name in (
        "split", "dataset_id", "scene_id", "video_id", "frame_index", "label", "fps"
    ):
        if len(getattr(data, name)) != count:
            raise ValueError(f"{name} length does not match features")
    unknown = set(np.unique(data.split)).difference(ALLOWED_SPLITS)
    if unknown:
        raise ValueError(f"unknown split labels: {sorted(unknown)}")
    required_splits = {"train", "source_val", "test"}
    if config.get("require_target_calibration", True):
        required_splits.add("target_calibration")
    missing = required_splits.difference(np.unique(data.split))
    if missing:
        raise ValueError(f"required splits are missing: {sorted(missing)}")
    if np.any(~np.isfinite(data.fps)) or np.any(data.fps <= 0):
        raise ValueError("fps must be finite and positive")
    if np.any(data.frame_index < 0):
        raise ValueError("frame_index must be non-negative")
    if np.any(np.char.str_len(data.dataset_id.astype(str)) == 0):
        raise ValueError("dataset_id must be non-empty")

    video_splits: dict[str, set[str]] = {}
    for dataset, video, split in zip(data.dataset_id, data.video_id, data.split):
        key = f"{dataset}/{video}"
        video_splits.setdefault(key, set()).add(str(split))
    leaked_videos = sorted(video for video, splits in video_splits.items() if len(splits) > 1)
    if leaked_videos:
        raise ValueError(f"whole-video split violation: {leaked_videos[:5]}")

    identities = set()
    for dataset, video, frame in zip(data.dataset_id, data.video_id, data.frame_index):
        identity = (str(dataset), str(video), int(frame))
        if identity in identities:
            raise ValueError(f"duplicate frame identity: {identity}")
        identities.add(identity)

    non_test = data.split != "test"
    if np.any(data.label[non_test] != 0):
        raise ValueError("anomaly labels or anomaly samples occur outside final test evaluation")
    if not set(np.unique(data.label[data.split == "test"])).issubset({0, 1}):
        raise ValueError("test labels must be binary")

    for dataset in np.unique(data.dataset_id):
        dataset_mask = data.dataset_id == dataset
        if not np.any(dataset_mask):
            continue
        for video in np.unique(data.video_id[dataset_mask]):
            mask = dataset_mask & (data.video_id == video)
            if len(np.unique(data.scene_id[mask])) != 1:
                raise ValueError(f"video has multiple scene IDs: {dataset}/{video}")
            if not np.allclose(data.fps[mask], data.fps[mask][0], rtol=0.0, atol=1e-6):
                raise ValueError(f"video has inconsistent fps: {dataset}/{video}")

    train_scenes = set(data.scene_id[data.split == "train"])
    min_train_scenes = int(config.get("min_train_scenes", 1))
    if len(train_scenes) < min_train_scenes:
        raise ValueError(
            f"training data has {len(train_scenes)} scenes; configuration requires "
            f"at least {min_train_scenes}"
        )
    test_scenes = set(data.scene_id[data.split == "test"])
    if config.get("require_unseen_test_scene", False) and train_scenes.intersection(test_scenes):
        raise ValueError("whole-scene generalization requires disjoint train and test scenes")
    return {
        "samples": count,
        "feature_dim": data.feature_dim,
        "datasets": sorted(set(data.dataset_id)),
        "train_scenes": sorted(train_scenes),
        "test_scenes": sorted(test_scenes),
        "whole_video_split": True,
        "abnormal_training_labels": False,
        "adjacent_frame_leakage": False,
    }
