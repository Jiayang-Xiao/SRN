from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


ALLOWED_SPLITS = {"train", "source_val", "target_calibration", "test"}


@dataclass(frozen=True)
class FeatureData:
    features: np.ndarray
    split: np.ndarray
    scene_id: np.ndarray
    video_id: np.ndarray
    frame_index: np.ndarray
    label: np.ndarray
    fps: np.ndarray
    location_dependent: np.ndarray
    background_features: np.ndarray | None = None

    def indices(self, split: str) -> np.ndarray:
        return np.flatnonzero(self.split == split)

    @property
    def feature_dim(self) -> int:
        return int(self.features.shape[1])


def load_feature_data(config: dict, seed: int) -> FeatureData:
    if config["type"] == "synthetic":
        return make_synthetic_features(config, seed)
    path = Path(config["path"]).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"frozen feature cache not found: {path}")
    with np.load(path, allow_pickle=False) as cache:
        required = {
            "features", "split", "scene_id", "video_id", "frame_index", "label", "fps"
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
    rng = np.random.default_rng(seed)
    dim = int(config.get("feature_dim", 16))
    frames = int(config.get("synthetic_frames_per_video", 12))
    source_scenes = int(config.get("synthetic_source_scenes", 3))
    scene_offsets = rng.normal(0.0, 2.0, size=(source_scenes + 1, dim))
    rows: list[tuple] = []

    def add_video(split: str, scene: int, video: int, anomalous: bool = False) -> None:
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
                (features[frame], split, f"scene_{scene}", video_name, frame,
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
        scene_id=np.asarray([row[2] for row in rows]),
        video_id=np.asarray([row[3] for row in rows]),
        frame_index=np.asarray([row[4] for row in rows], dtype=np.int64),
        label=np.asarray([row[5] for row in rows], dtype=np.int64),
        fps=np.asarray([row[6] for row in rows], dtype=np.float32),
        location_dependent=np.asarray([row[7] for row in rows], dtype=np.int64),
        background_features=np.stack([row[8] for row in rows]).astype(np.float32),
    )
    validate_feature_data(data, config)
    return data


def validate_feature_data(data: FeatureData, config: dict) -> dict[str, object]:
    count = data.features.shape[0]
    if data.features.ndim != 2 or not np.isfinite(data.features).all():
        raise ValueError("features must be a finite [N, D] array")
    expected_dim = int(config.get("feature_dim", data.feature_dim))
    if data.feature_dim != expected_dim:
        raise ValueError(
            f"feature dimension mismatch: cache={data.feature_dim}, config={expected_dim}"
        )
    for name in ("split", "scene_id", "video_id", "frame_index", "label", "fps"):
        if len(getattr(data, name)) != count:
            raise ValueError(f"{name} length does not match features")
    unknown = set(np.unique(data.split)).difference(ALLOWED_SPLITS)
    if unknown:
        raise ValueError(f"unknown split labels: {sorted(unknown)}")
    missing = ALLOWED_SPLITS.difference(np.unique(data.split))
    if missing:
        raise ValueError(f"required splits are missing: {sorted(missing)}")
    if np.any(data.fps <= 0):
        raise ValueError("fps must be positive")

    video_splits: dict[str, set[str]] = {}
    for video, split in zip(data.video_id, data.split):
        video_splits.setdefault(str(video), set()).add(str(split))
    leaked_videos = sorted(video for video, splits in video_splits.items() if len(splits) > 1)
    if leaked_videos:
        raise ValueError(f"whole-video split violation: {leaked_videos[:5]}")

    identities = set()
    for video, frame in zip(data.video_id, data.frame_index):
        identity = (str(video), int(frame))
        if identity in identities:
            raise ValueError(f"duplicate frame identity: {identity}")
        identities.add(identity)

    non_test = data.split != "test"
    if np.any(data.label[non_test] != 0):
        raise ValueError("anomaly labels or anomaly samples occur outside final test evaluation")
    if not set(np.unique(data.label[data.split == "test"])).issubset({0, 1}):
        raise ValueError("test labels must be binary")

    train_scenes = set(data.scene_id[data.split == "train"])
    if len(train_scenes) < 2:
        raise ValueError("ELOS requires at least two source training scenes")
    test_scenes = set(data.scene_id[data.split == "test"])
    if config.get("require_unseen_test_scene", False) and train_scenes.intersection(test_scenes):
        raise ValueError("whole-scene generalization requires disjoint train and test scenes")
    return {
        "samples": count,
        "feature_dim": data.feature_dim,
        "train_scenes": sorted(train_scenes),
        "test_scenes": sorted(test_scenes),
        "whole_video_split": True,
        "abnormal_training_labels": False,
        "adjacent_frame_leakage": False,
    }
