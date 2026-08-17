#!/usr/bin/env python3
"""Extract one shared DINOv2 ViT-S/14 catalog for UCSD Ped2 and Avenue.

The extractor is deliberately label-blind during model inference. Official frame labels
are joined only when each per-video feature shard is serialized. Shards make the process
resumable and are merged into one immutable catalog after every expected video succeeds.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import cv2
import numpy as np
import torch
from PIL import Image
from scipy.io import loadmat
from torch import nn
from torchvision import transforms


IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
EXPECTED_DIM = 384


@dataclass(frozen=True)
class VideoSpec:
    dataset_id: str
    scene_id: str
    official_split: str
    video_id: str
    source: Path
    labels: np.ndarray
    fps: float
    kind: str


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ped2-root",
        type=Path,
        default=root / "data/raw/ucsd/UCSD_Anomaly_Dataset.v1p2/UCSDped2",
    )
    parser.add_argument(
        "--avenue-root", type=Path, default=root / "data/raw/avenue/Avenue Dataset"
    )
    parser.add_argument(
        "--avenue-label-root",
        type=Path,
        default=root / "data/raw/avenue/ground_truth_demo/testing_label_mask",
    )
    parser.add_argument(
        "--model-repo", type=Path, default=root / ".cache/dinov2-repo"
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=root / "data/models/dinov2/dinov2_vits14_pretrain.pth",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=root / "data/frozen_features/dinov2_vits14"
    )
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--threads", type=int, default=16)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument(
        "--limit-videos", type=int, help="engineering benchmark only; does not merge a catalog"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for path in (args.ped2_root, args.avenue_root, args.avenue_label_root,
                 args.model_repo, args.checkpoint):
        if not path.exists():
            raise FileNotFoundError(path)
    if args.batch_size <= 0 or args.threads <= 0:
        raise ValueError("batch size and thread count must be positive")
    if args.device == "cuda":
        if "CUDA_VISIBLE_DEVICES" not in os.environ:
            raise RuntimeError("CUDA extraction requires the repository GPU selector in the same shell")
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA requested but PyTorch cannot access a CUDA device")

    torch.set_num_threads(args.threads)
    device = torch.device(args.device)
    output_dir = args.output_dir.resolve()
    shard_dir = output_dir / "shards"
    shard_dir.mkdir(parents=True, exist_ok=True)
    videos = ped2_specs(args.ped2_root.resolve()) + avenue_specs(
        args.avenue_root.resolve(), args.avenue_label_root.resolve()
    )
    expected_video_count = len(videos)
    if args.limit_videos is not None:
        videos = videos[:args.limit_videos]

    model, transform = load_model(args.model_repo.resolve(), args.checkpoint.resolve(), device)
    started = time.time()
    for position, spec in enumerate(videos, start=1):
        shard = shard_dir / f"{spec.dataset_id}_{spec.official_split}_{spec.video_id}.npz"
        if shard.is_file() and validate_shard(shard, spec):
            print(f"[{position}/{len(videos)}] reuse {shard.name}", flush=True)
            continue
        video_started = time.time()
        features = extract_video(model, transform, spec, args.batch_size, device)
        if features.shape != (len(spec.labels), EXPECTED_DIM):
            raise RuntimeError(
                f"feature shape mismatch for {spec.dataset_id}/{spec.video_id}: {features.shape}"
            )
        write_npz_atomic(
            shard,
            features=features,
            dataset_id=np.repeat(spec.dataset_id, len(features)),
            scene_id=np.repeat(spec.scene_id, len(features)),
            official_split=np.repeat(spec.official_split, len(features)),
            video_id=np.repeat(spec.video_id, len(features)),
            frame_index=np.arange(len(features), dtype=np.int64),
            label=spec.labels.astype(np.int64),
            fps=np.full(len(features), spec.fps, dtype=np.float32),
        )
        print(
            f"[{position}/{len(videos)}] wrote {shard.name}: {len(features)} frames "
            f"in {time.time() - video_started:.1f}s",
            flush=True,
        )

    if args.limit_videos is not None:
        print("limit-videos set: benchmark shards written; formal catalog not merged", flush=True)
        return 0

    catalog = output_dir / "ped2_avenue_catalog.npz"
    arrays = merge_shards(shard_dir, videos)
    write_npz_atomic(catalog, **arrays)
    provenance = build_provenance(args, videos, arrays, started, expected_video_count)
    write_json_atomic(output_dir / "ped2_avenue_catalog.provenance.json", provenance)
    print(f"catalog={catalog} samples={len(arrays['features'])}", flush=True)
    return 0


def load_model(repo: Path, checkpoint: Path, device: torch.device):
    model: nn.Module = torch.hub.load(
        str(repo), "dinov2_vits14", source="local", pretrained=False
    )
    state = torch.load(checkpoint, map_location="cpu", weights_only=True)
    model.load_state_dict(state, strict=True)
    model.eval().to(device)
    transform = transforms.Compose(
        [
            transforms.Resize(256, interpolation=transforms.InterpolationMode.BICUBIC),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]
    )
    with torch.inference_mode():
        probe = model(torch.zeros(1, 3, 224, 224, device=device))
    if tuple(probe.shape) != (1, EXPECTED_DIM):
        raise RuntimeError(f"unexpected DINOv2 output shape: {tuple(probe.shape)}")
    return model, transform


def ped2_specs(root: Path) -> list[VideoSpec]:
    specs: list[VideoSpec] = []
    for directory in sorted((root / "Train").glob("Train[0-9][0-9][0-9]")):
        frames = sorted_numeric(directory.glob("*.tif"))
        specs.append(VideoSpec("ped2", "ped2_camera_01", "train", directory.name.lower(),
                               directory, np.zeros(len(frames), dtype=np.int64), 10.0, "tiff"))

    intervals_path = root / "Test" / "UCSDped2.m"
    interval_pairs = [tuple(map(int, pair)) for pair in re.findall(
        r"gt_frame\s*=\s*\[(\d+):(\d+)\]", intervals_path.read_text(encoding="utf-8")
    )]
    test_dirs = sorted((root / "Test").glob("Test[0-9][0-9][0-9]"))
    if len(interval_pairs) != len(test_dirs):
        raise ValueError("UCSDped2.m interval count does not match test video count")
    for directory, (start, stop) in zip(test_dirs, interval_pairs):
        frames = sorted_numeric(directory.glob("*.tif"))
        masks = sorted_numeric((directory.parent / f"{directory.name}_gt").glob("*.bmp"))
        if len(frames) != len(masks):
            raise ValueError(f"Ped2 frame/mask mismatch: {directory}")
        labels = np.asarray([bool(np.asarray(Image.open(mask)).any()) for mask in masks], dtype=np.int64)
        expected = np.zeros(len(frames), dtype=np.int64)
        expected[start - 1:stop] = 1
        if not np.array_equal(labels, expected):
            raise ValueError(f"Ped2 mask labels disagree with UCSDped2.m: {directory.name}")
        specs.append(VideoSpec("ped2", "ped2_camera_01", "test", directory.name.lower(),
                               directory, labels, 10.0, "tiff"))
    return specs


def avenue_specs(root: Path, label_root: Path) -> list[VideoSpec]:
    specs: list[VideoSpec] = []
    for official_split, directory_name in (("train", "training_videos"), ("test", "testing_videos")):
        for video in sorted_numeric((root / directory_name).glob("*.avi")):
            capture = cv2.VideoCapture(str(video))
            frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = float(capture.get(cv2.CAP_PROP_FPS))
            capture.release()
            if fps <= 0 or frame_count <= 0:
                raise ValueError(f"could not read Avenue metadata: {video}")
            if official_split == "train":
                labels = np.zeros(frame_count, dtype=np.int64)
            else:
                label_file = label_root / f"{int(video.stem)}_label.mat"
                volume = np.ravel(loadmat(label_file, squeeze_me=True, struct_as_record=False)["volLabel"])
                labels = np.asarray([bool(np.asarray(mask).any()) for mask in volume], dtype=np.int64)
                if len(labels) != frame_count:
                    raise ValueError(f"Avenue video/label mismatch: {video}")
            specs.append(VideoSpec("avenue", "avenue_camera_01", official_split,
                                   f"{official_split}_{video.stem}", video, labels, fps, "video"))
    return specs


def sorted_numeric(paths) -> list[Path]:
    def key(path: Path):
        match = re.search(r"(\d+)", path.stem)
        return int(match.group(1)) if match else path.name
    return sorted(paths, key=key)


def iter_images(spec: VideoSpec) -> Iterator[Image.Image]:
    if spec.kind == "tiff":
        for path in sorted_numeric(spec.source.glob("*.tif")):
            with Image.open(path) as image:
                yield image.convert("RGB").copy()
        return
    capture = cv2.VideoCapture(str(spec.source))
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            yield Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    finally:
        capture.release()


def extract_video(model, transform, spec: VideoSpec, batch_size: int, device: torch.device):
    outputs: list[np.ndarray] = []
    batch: list[torch.Tensor] = []
    for image in iter_images(spec):
        batch.append(transform(image))
        if len(batch) == batch_size:
            outputs.append(run_batch(model, batch, device))
            batch.clear()
    if batch:
        outputs.append(run_batch(model, batch, device))
    features = np.concatenate(outputs, axis=0) if outputs else np.empty((0, EXPECTED_DIM), np.float32)
    if len(features) != len(spec.labels):
        raise ValueError(
            f"decoded frame count mismatch for {spec.dataset_id}/{spec.video_id}: "
            f"decoded={len(features)} labels={len(spec.labels)}"
        )
    return features


def run_batch(model, batch: list[torch.Tensor], device: torch.device) -> np.ndarray:
    values = torch.stack(batch).to(device)
    with torch.inference_mode():
        features = model(values)
    if not torch.isfinite(features).all():
        raise FloatingPointError("DINOv2 produced non-finite features")
    return features.float().cpu().numpy()


def validate_shard(path: Path, spec: VideoSpec) -> bool:
    try:
        with np.load(path, allow_pickle=False) as shard:
            return (
                shard["features"].shape == (len(spec.labels), EXPECTED_DIM)
                and np.array_equal(shard["label"], spec.labels)
                and np.isfinite(shard["features"]).all()
            )
    except (OSError, KeyError, ValueError):
        return False


def merge_shards(shard_dir: Path, videos: list[VideoSpec]) -> dict[str, np.ndarray]:
    keys = ("features", "dataset_id", "scene_id", "official_split", "video_id",
            "frame_index", "label", "fps")
    merged: dict[str, list[np.ndarray]] = {key: [] for key in keys}
    for spec in videos:
        path = shard_dir / f"{spec.dataset_id}_{spec.official_split}_{spec.video_id}.npz"
        if not path.is_file() or not validate_shard(path, spec):
            raise RuntimeError(f"missing or invalid feature shard: {path}")
        with np.load(path, allow_pickle=False) as shard:
            for key in keys:
                merged[key].append(np.asarray(shard[key]))
    return {key: np.concatenate(values, axis=0) for key, values in merged.items()}


def build_provenance(args, videos, arrays, started, expected_video_count):
    root = Path(__file__).resolve().parents[1]
    archive_paths = {
        "ucsd": root / "data/raw/archives/UCSD_Anomaly_Dataset.tar.gz",
        "avenue": root / "data/raw/archives/Avenue_Dataset.zip",
        "avenue_ground_truth": root / "data/raw/archives/Avenue_ground_truth_demo.zip",
    }
    counts = {}
    for dataset in np.unique(arrays["dataset_id"]):
        for split in np.unique(arrays["official_split"]):
            mask = (arrays["dataset_id"] == dataset) & (arrays["official_split"] == split)
            if mask.any():
                counts[f"{dataset}_{split}_frames"] = int(mask.sum())
    return {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "duration_seconds": time.time() - started,
        "command": " ".join(sys.argv),
        "evaluation_type": "real_gt_catalog",
        "feature_extraction_uses_labels": False,
        "label_join_stage": "after all model inference for a video, at shard serialization",
        "extractor_sha256": sha256(root / "scripts/extract_ped2_avenue_dinov2.py"),
        "feature_dim": EXPECTED_DIM,
        "samples": int(len(arrays["features"])),
        "videos": expected_video_count,
        "counts": counts,
        "datasets": {
            "ped2": {
                "source": "http://www.svcl.ucsd.edu/projects/anomaly/UCSD_Anomaly_Dataset.tar.gz",
                "official_md5": "5006421b89885f45a6f93b041145f2eb",
                "fps": 10.0,
                "fps_provenance": "UCSD dataset literature; archive contains still frames",
                "labels": "official TestNNN_gt masks cross-checked against UCSDped2.m",
            },
            "avenue": {
                "source": "https://www.cse.cuhk.edu.hk/~leojia/projects/detectabnormal/Avenue_Dataset.zip",
                "ground_truth_source": "https://www.cse.cuhk.edu.hk/~leojia/projects/detectabnormal/ground_truth_demo.zip",
                "fps": 25.0,
                "fps_provenance": "decoded official AVI metadata",
                "labels": "official volLabel masks; length checked against every AVI",
            },
        },
        "archive_sha256": {
            name: sha256(path) if path.is_file() else None for name, path in archive_paths.items()
        },
        "backbone": {
            "name": "dinov2_vits14",
            "checkpoint": str(args.checkpoint.resolve()),
            "checkpoint_sha256": sha256(args.checkpoint.resolve()),
            "official_url": "https://dl.fbaipublicfiles.com/dinov2/dinov2_vits14/dinov2_vits14_pretrain.pth",
            "code_repo": "https://github.com/facebookresearch/dinov2",
            "code_commit": git_rev(args.model_repo.resolve()),
            "output": "model forward CLS feature after final normalization",
        },
        "preprocessing": {
            "color": "RGB (grayscale Ped2 replicated by PIL RGB conversion)",
            "resize_short_side": 256,
            "center_crop": 224,
            "interpolation": "bicubic",
            "mean": IMAGENET_MEAN,
            "std": IMAGENET_STD,
            "frame_sampling": "every official frame, zero-based cache frame_index",
        },
        "runtime": {
            "python": sys.version,
            "torch": torch.__version__,
            "torchvision": __import__("torchvision").__version__,
            "numpy": np.__version__,
            "device": args.device,
            "threads": args.threads,
            "batch_size": args.batch_size,
            "project_git_head": git_rev(root),
        },
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_rev(path: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"], text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def write_npz_atomic(path: Path, **arrays) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        np.savez_compressed(handle, **arrays)
    os.replace(temporary, path)


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)


if __name__ == "__main__":
    raise SystemExit(main())
