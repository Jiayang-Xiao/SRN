#!/usr/bin/env python3
"""Build leakage-safe experiment caches from the immutable Ped2/Avenue catalog."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--catalog", type=Path,
        default=root / "data/frozen_features/dinov2_vits14/ped2_avenue_catalog.npz",
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=root / "data/frozen_features/dinov2_vits14/experiments",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.catalog.is_file():
        raise FileNotFoundError(args.catalog)
    with np.load(args.catalog, allow_pickle=False) as source:
        catalog = {key: np.asarray(source[key]) for key in source.files}
    required = {"features", "dataset_id", "scene_id", "official_split", "video_id",
                "frame_index", "label", "fps"}
    missing = required.difference(catalog)
    if missing:
        raise ValueError(f"catalog missing fields: {sorted(missing)}")

    designs = [
        within_design(catalog, "ped2", train_count=10, val_count=3),
        within_design(catalog, "avenue", train_count=10, val_count=3),
        transfer_design(catalog, "ped2", "avenue", source_train_count=12,
                        target_calibration_count=4),
        transfer_design(catalog, "avenue", "ped2", source_train_count=12,
                        target_calibration_count=4),
        joint_seen_design(catalog),
    ]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    catalog_hash = sha256(args.catalog)
    assembler_hash = sha256(Path(__file__).resolve())
    for design in designs:
        path = args.output_dir / f"{design['name']}.npz"
        payload = materialize(catalog, design)
        write_npz_atomic(path, **payload)
        sidecar = {
            "name": design["name"],
            "track": design["track"],
            "claim_ceiling": design["claim_ceiling"],
            "catalog": str(args.catalog.resolve()),
            "catalog_sha256": catalog_hash,
            "assembler_sha256": assembler_hash,
            "source_normal_only": True,
            "anomaly_labels_used_for_split": False,
            "whole_video_split": True,
            "split_videos": design["split_videos"],
            "unused_normal_videos": design["unused_normal_videos"],
            "counts": {
                split: int(np.sum(payload["split"] == split))
                for split in np.unique(payload["split"])
            },
            "target_calibration_frames": int(np.sum(payload["split"] == "target_calibration")),
            "target_calibration_videos": len(design["split_videos"]["target_calibration"]),
        }
        write_json_atomic(path.with_suffix(".provenance.json"), sidecar)
        print(f"wrote {path}: {len(payload['features'])} frames")
    return 0


def normal_videos(catalog, dataset: str) -> list[str]:
    mask = (catalog["dataset_id"] == dataset) & (catalog["official_split"] == "train")
    if np.any(catalog["label"][mask] != 0):
        raise ValueError(f"official normal training partition contains nonzero labels: {dataset}")
    return sorted(np.unique(catalog["video_id"][mask]))


def test_videos(catalog, dataset: str) -> list[str]:
    mask = (catalog["dataset_id"] == dataset) & (catalog["official_split"] == "test")
    return sorted(np.unique(catalog["video_id"][mask]))


def within_design(catalog, dataset: str, train_count: int, val_count: int):
    videos = normal_videos(catalog, dataset)
    train = videos[:train_count]
    source_val = videos[train_count:train_count + val_count]
    calibration = videos[train_count + val_count:]
    return design(
        f"{dataset}_within",
        "within_dataset_sanity",
        "Within-dataset real-GT sanity only; no cross-scene or cross-domain claim.",
        {"train": [(dataset, item) for item in train],
         "source_val": [(dataset, item) for item in source_val],
         "target_calibration": [(dataset, item) for item in calibration],
         "test": [(dataset, item) for item in test_videos(catalog, dataset)]},
        [],
    )


def transfer_design(catalog, source: str, target: str, source_train_count: int,
                    target_calibration_count: int):
    source_videos = normal_videos(catalog, source)
    target_videos = normal_videos(catalog, target)
    train = source_videos[:source_train_count]
    source_val = source_videos[source_train_count:]
    calibration = target_videos[:target_calibration_count]
    unused = [(target, item) for item in target_videos[target_calibration_count:]]
    return design(
        f"{source}_to_{target}",
        "cross_dataset_transfer",
        "Real-GT single-source cross-dataset baseline; SRN/ELOS mechanism is inapplicable "
        "because the source has one scene.",
        {"train": [(source, item) for item in train],
         "source_val": [(source, item) for item in source_val],
         "target_calibration": [(target, item) for item in calibration],
         "test": [(target, item) for item in test_videos(catalog, target)]},
        unused,
    )


def joint_seen_design(catalog):
    splits = {name: [] for name in ("train", "source_val", "target_calibration", "test")}
    for dataset in ("ped2", "avenue"):
        videos = normal_videos(catalog, dataset)
        splits["train"].extend((dataset, item) for item in videos[:-4])
        splits["source_val"].extend((dataset, item) for item in videos[-4:-2])
        splits["target_calibration"].extend((dataset, item) for item in videos[-2:])
        splits["test"].extend((dataset, item) for item in test_videos(catalog, dataset))
    return design(
        "ped2_avenue_joint_seen",
        "two_source_seen_domain_mechanism_diagnostic",
        "Real-GT mechanism diagnostic on two seen source domains; not unseen-scene or "
        "cross-dataset evidence.",
        splits,
        [],
    )


def design(name, track, claim_ceiling, split_videos, unused):
    encoded = {
        split: [f"{dataset}/{video}" for dataset, video in pairs]
        for split, pairs in split_videos.items()
    }
    all_used = [item for values in encoded.values() for item in values]
    if len(all_used) != len(set(all_used)):
        raise ValueError(f"video leakage in design: {name}")
    return {
        "name": name,
        "track": track,
        "claim_ceiling": claim_ceiling,
        "split_pairs": split_videos,
        "split_videos": encoded,
        "unused_normal_videos": [f"{dataset}/{video}" for dataset, video in unused],
    }


def materialize(catalog, design_spec):
    masks = []
    split_values = []
    for split in ("train", "source_val", "target_calibration", "test"):
        split_mask = np.zeros(len(catalog["features"]), dtype=bool)
        for dataset, video in design_spec["split_pairs"][split]:
            split_mask |= (catalog["dataset_id"] == dataset) & (catalog["video_id"] == video)
        masks.append(split_mask)
        split_values.append(np.repeat(split, int(split_mask.sum())))
    selected = np.concatenate([np.flatnonzero(mask) for mask in masks])
    output = {
        key: catalog[key][selected]
        for key in ("features", "dataset_id", "scene_id", "video_id", "frame_index", "label", "fps")
    }
    output["split"] = np.concatenate(split_values)
    output["location_dependent"] = np.full(len(selected), -1, dtype=np.int64)
    if np.any(output["label"][output["split"] != "test"] != 0):
        raise ValueError(f"non-test anomaly label in {design_spec['name']}")
    return output


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_npz_atomic(path: Path, **arrays) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        np.savez_compressed(handle, **arrays)
    os.replace(temporary, path)


def write_json_atomic(path: Path, payload: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)


if __name__ == "__main__":
    raise SystemExit(main())
