from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import torch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from restricted_bridge.config import load_config  # noqa: E402
from restricted_bridge.data import make_synthetic_features, validate_feature_data  # noqa: E402
from restricted_bridge.metrics import (  # noqa: E402
    binary_auroc,
    evaluate_scores,
    source_normal_threshold,
)
from restricted_bridge.models import SRN  # noqa: E402
from restricted_bridge.runner import run_experiment  # noqa: E402
from restricted_bridge.scorers import GaussianScorer, KNNScorer, PrototypeScorer  # noqa: E402


class DataProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = {
            "type": "synthetic",
            "feature_dim": 16,
            "synthetic_source_scenes": 3,
            "synthetic_frames_per_video": 8,
            "require_unseen_test_scene": True,
        }

    def test_synthetic_data_is_reproducible_and_protocol_clean(self) -> None:
        first = make_synthetic_features(self.config, 7)
        second = make_synthetic_features(self.config, 7)
        np.testing.assert_array_equal(first.features, second.features)
        report = validate_feature_data(first, self.config)
        self.assertTrue(report["whole_video_split"])
        self.assertFalse(report["abnormal_training_labels"])
        self.assertFalse(report["adjacent_frame_leakage"])

    def test_whole_video_leakage_is_rejected(self) -> None:
        data = make_synthetic_features(self.config, 7)
        leaked_split = data.split.copy()
        leaked_split[np.flatnonzero(data.video_id == data.video_id[0])[0]] = "source_val"
        leaked = data.__class__(**{**data.__dict__, "split": leaked_split})
        with self.assertRaisesRegex(ValueError, "whole-video split violation"):
            validate_feature_data(leaked, self.config)

    def test_abnormal_training_sample_is_rejected(self) -> None:
        data = make_synthetic_features(self.config, 7)
        labels = data.label.copy()
        labels[data.indices("train")[0]] = 1
        leaked = data.__class__(**{**data.__dict__, "label": labels})
        with self.assertRaisesRegex(ValueError, "outside final test"):
            validate_feature_data(leaked, self.config)


class ModelAndScorerTests(unittest.TestCase):
    def test_srn_context_ablation_changes_only_output_interface(self) -> None:
        features = torch.randn(5, 16)
        full = SRN(16, 4, 2, 3, 0.25, True, 0.1)
        residual_only = SRN(16, 4, 2, 3, 0.25, False, 0.1)
        self.assertEqual(full(features).embedding.shape, (5, 18))
        self.assertEqual(residual_only(features).embedding.shape, (5, 16))
        self.assertEqual(full(features).scene_component.shape, (5, 16))

    def test_all_scorers_rank_far_points_higher(self) -> None:
        train = np.asarray([[0.0, 0.0], [0.1, -0.1], [-0.1, 0.1]])
        query = np.asarray([[0.0, 0.0], [4.0, 4.0]])
        for scorer in (KNNScorer(2), GaussianScorer(0.2), PrototypeScorer(2)):
            scorer.fit(train, seed=3)
            scores = scorer.score(query)
            self.assertGreater(scores[1], scores[0])

    def test_gaussian_uses_full_covariance(self) -> None:
        train = np.asarray([[0.0, 0.0], [1.0, 1.0], [-1.0, -1.0], [0.2, 0.1]])
        scorer = GaussianScorer(0.05)
        scorer.fit(train)
        centered = np.asarray([[1.0, -1.0]]) - scorer.mean
        expected = np.einsum("ni,ij,nj->n", centered, scorer.precision, centered)
        np.testing.assert_allclose(scorer.score(np.asarray([[1.0, -1.0]])), expected)

    def test_metrics_and_source_threshold(self) -> None:
        labels = np.asarray([0, 0, 1, 1])
        scores = np.asarray([0.1, 0.2, 0.8, 0.9])
        self.assertEqual(binary_auroc(labels, scores), 1.0)
        self.assertGreaterEqual(source_normal_threshold(scores[:2], 0.01), 0.2)

    def test_evaluation_reports_per_scene_and_worst_scene(self) -> None:
        labels = np.asarray([0, 1, 0, 1])
        scores = np.asarray([0.1, 0.9, 0.4, 0.6])
        groups = np.asarray(["a", "a", "b", "b"])
        result = evaluate_scores(
            labels, scores, 0.5, groups, groups,
            np.full(4, 25.0), np.asarray([-1, 0, -1, 1]),
        )
        self.assertEqual(result["per_scene_auroc"], {"a": 1.0, "b": 1.0})
        self.assertEqual(result["worst_scene_auroc"], 1.0)
        self.assertEqual(result["scene_auroc_std"], 0.0)


class EndToEndDryRunTests(unittest.TestCase):
    def test_minimal_matrix_writes_checkpoint_metrics_and_logs(self) -> None:
        config = load_config(PROJECT_ROOT / "configs" / "restricted_bridge_dry_run.yaml")
        config = copy.deepcopy(config)
        config["seeds"] = [5]
        config["training"]["epochs"] = 2
        config["matrix"] = [
            {"name": "raw_knn", "method": "raw", "scorer": "knn"},
            {"name": "full_srn", "method": "full_srn", "scorer": "prototype"},
            {"name": "srn_residual_only", "method": "srn_residual_only", "scorer": "prototype"},
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_experiment(config, temp_dir)
            self.assertEqual(len(result["runs"]), 3)
            self.assertTrue((Path(temp_dir) / "results.json").is_file())
            self.assertTrue((Path(temp_dir) / "results.csv").is_file())
            self.assertTrue((Path(temp_dir) / "run.log").is_file())
            self.assertTrue((Path(temp_dir) / "seed_5" / "full_srn" / "checkpoint.pt").is_file())
            with (Path(temp_dir) / "results.json").open(encoding="utf-8") as handle:
                self.assertEqual(json.load(handle)["device"], "cpu")


if __name__ == "__main__":
    unittest.main()
