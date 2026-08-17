from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from restricted_bridge.calibration import (  # noqa: E402
    empirical_quantile_map,
    fit_conditional_location_calibrator,
    mean_location_scale,
    robust_location_scale,
    standardize,
)
from restricted_bridge.metrics import source_normal_threshold  # noqa: E402


class ScoreCalibrationTests(unittest.TestCase):
    def test_source_affine_controls_preserve_threshold_decisions(self) -> None:
        source = np.asarray([0.1, 0.2, 0.4, 0.8, 1.6])
        test = np.asarray([0.15, 0.5, 2.0])
        raw_threshold = source_normal_threshold(source, 0.2)
        raw_decisions = test > raw_threshold
        for location, scale in (
            mean_location_scale(source),
            robust_location_scale(source),
        ):
            calibrated_source = standardize(source, location, scale)
            calibrated_test = standardize(test, location, scale)
            threshold = source_normal_threshold(calibrated_source, 0.2)
            np.testing.assert_array_equal(calibrated_test > threshold, raw_decisions)

    def test_empirical_mapping_is_monotone_and_calibration_only(self) -> None:
        calibration = np.asarray([10.0, 20.0, 30.0, 40.0])
        source = np.asarray([1.0, 2.0, 3.0, 4.0, 5.0])
        first = empirical_quantile_map(
            np.asarray([15.0, 25.0, 35.0]), calibration, source
        )
        second = empirical_quantile_map(
            np.asarray([15.0, 25.0, 35.0, 1000.0]), calibration, source
        )
        np.testing.assert_allclose(first, second[:3])
        self.assertTrue(np.all(np.diff(first) >= 0.0))

    def test_conditional_calibrator_cross_fits_whole_videos(self) -> None:
        rng = np.random.default_rng(4)
        video_ids = np.repeat(np.asarray(["v1", "v2", "v3"]), 20)
        features = rng.normal(size=(60, 6))
        raw_scores = np.exp(0.5 * features[:, 0] + 0.1 * rng.normal(size=60))
        result = fit_conditional_location_calibrator(
            features,
            raw_scores,
            video_ids,
            target_fpr=0.1,
            rank=3,
            alphas=(0.01, 0.1),
        )
        transformed = result.transform(raw_scores, features)
        self.assertEqual(transformed.shape, raw_scores.shape)
        self.assertTrue(np.all(np.isfinite(transformed)))
        self.assertIn(result.selected_alpha, (0.01, 0.1))
        self.assertEqual(set(result.cv_fpr_by_video), {"v1", "v2", "v3"})
        self.assertTrue(np.all(np.isfinite(result.cross_fitted_scores)))


if __name__ == "__main__":
    unittest.main()
