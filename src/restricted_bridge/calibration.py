"""Normal-only anomaly-score calibration utilities.

The functions in this module deliberately keep target information out of strict
source-only fitting.  Target arrays are accepted only by transformation methods whose
names explicitly indicate target-normal calibration.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .metrics import source_normal_threshold


EPSILON = 1e-12


def robust_location_scale(values: np.ndarray) -> tuple[float, float]:
    """Return median and Gaussian-consistent MAD with a finite positive floor."""
    array = np.asarray(values, dtype=np.float64)
    location = float(np.median(array))
    scale = float(1.4826 * np.median(np.abs(array - location)))
    return location, max(scale, EPSILON)


def mean_location_scale(values: np.ndarray) -> tuple[float, float]:
    """Return mean and population standard deviation with a positive floor."""
    array = np.asarray(values, dtype=np.float64)
    return float(np.mean(array)), max(float(np.std(array)), EPSILON)


def standardize(
    values: np.ndarray, location: float, scale: float
) -> np.ndarray:
    """Apply a frozen affine standardization."""
    return (np.asarray(values, dtype=np.float64) - location) / max(scale, EPSILON)


def map_location_scale(
    values: np.ndarray,
    target_location: float,
    target_scale: float,
    source_location: float,
    source_scale: float,
) -> np.ndarray:
    """Map scores from a declared target-normal affine scale to the source scale."""
    normalized = standardize(values, target_location, target_scale)
    return normalized * max(source_scale, EPSILON) + source_location


def video_balanced_threshold(
    scores: np.ndarray,
    video_ids: np.ndarray,
    target_fpr: float,
) -> tuple[float, dict[str, float]]:
    """Use the median of whole-video normal quantile thresholds."""
    scores = np.asarray(scores, dtype=np.float64)
    video_ids = np.asarray(video_ids).astype(str)
    thresholds = {
        str(video): source_normal_threshold(scores[video_ids == video], target_fpr)
        for video in np.unique(video_ids)
    }
    return float(np.median(list(thresholds.values()))), thresholds


def empirical_quantile_map(
    values: np.ndarray,
    target_normal_scores: np.ndarray,
    source_normal_scores: np.ndarray,
) -> np.ndarray:
    """Map through a target-normal empirical CDF into source-normal quantiles.

    The target CDF is frozen from the declared calibration split.  No statistics of
    ``values`` are used, so passing final test scores does not create transductive
    normalization.
    """
    target = np.sort(np.asarray(target_normal_scores, dtype=np.float64))
    source = np.asarray(source_normal_scores, dtype=np.float64)
    if not len(target) or not len(source):
        raise ValueError("empirical quantile mapping requires non-empty normal scores")
    probabilities = np.searchsorted(target, values, side="right") / (len(target) + 1.0)
    probabilities = np.clip(probabilities, 1.0 / (len(target) + 1.0), len(target) / (len(target) + 1.0))
    return np.quantile(source, probabilities, method="linear")


@dataclass(frozen=True)
class PcaRidgeModel:
    """Low-capacity PCA-context ridge model for conditional score location."""

    feature_mean: np.ndarray
    components: np.ndarray
    component_scale: np.ndarray
    target_mean: float
    coefficients: np.ndarray
    alpha: float

    def predict(self, features: np.ndarray) -> np.ndarray:
        values = np.asarray(features, dtype=np.float64)
        context = (values - self.feature_mean) @ self.components.T
        context = context / self.component_scale
        return self.target_mean + context @ self.coefficients


@dataclass(frozen=True)
class ConditionalCalibration:
    """Fitted source-only conditional calibrator and its cross-fitted threshold."""

    model: PcaRidgeModel
    threshold: float
    residual_scale: float
    selected_alpha: float
    cv_mean_absolute_fpr_error: float
    cv_fpr_by_video: dict[str, float]
    cross_fitted_scores: np.ndarray

    def transform(self, raw_scores: np.ndarray, features: np.ndarray) -> np.ndarray:
        target = np.log1p(np.maximum(np.asarray(raw_scores, dtype=np.float64), 0.0))
        return (target - self.model.predict(features)) / self.residual_scale


def fit_conditional_location_calibrator(
    features: np.ndarray,
    raw_scores: np.ndarray,
    video_ids: np.ndarray,
    target_fpr: float = 0.01,
    rank: int = 8,
    alphas: tuple[float, ...] = (0.001, 0.01, 0.1, 1.0, 10.0),
) -> ConditionalCalibration:
    """Fit and select the frozen Track-B conditional source-only calibrator.

    Selection is leave-one-whole-video-out and uses only normal source-validation
    examples.  The final threshold is derived from cross-fitted residuals.
    """
    features = np.asarray(features, dtype=np.float64)
    raw_scores = np.asarray(raw_scores, dtype=np.float64)
    video_ids = np.asarray(video_ids).astype(str)
    if features.ndim != 2 or len(features) != len(raw_scores):
        raise ValueError("features and raw_scores must align")
    videos = np.unique(video_ids)
    if len(videos) < 2:
        raise ValueError("conditional calibration requires at least two source videos")
    transformed_target = np.log1p(np.maximum(raw_scores, 0.0))

    candidates = []
    for alpha in alphas:
        cross_fitted = _cross_fitted_predictions(
            features, transformed_target, video_ids, rank, float(alpha)
        )
        residual = transformed_target - cross_fitted
        threshold = source_normal_threshold(residual, target_fpr)
        per_video = {
            str(video): float(np.mean(residual[video_ids == video] > threshold))
            for video in videos
        }
        error = float(np.mean([abs(value - target_fpr) for value in per_video.values()]))
        candidates.append((error, float(alpha), residual, per_video))

    error, alpha, residual, per_video = min(candidates, key=lambda item: (item[0], item[1]))
    residual_location, residual_scale = robust_location_scale(residual)
    normalized = (residual - residual_location) / residual_scale
    threshold = source_normal_threshold(normalized, target_fpr)
    model = _fit_pca_ridge(features, transformed_target, rank, alpha)
    # Fold residual location is absorbed into the deployable intercept so that the
    # transformed test score uses the exact cross-fitted reference location.
    adjusted_model = PcaRidgeModel(
        feature_mean=model.feature_mean,
        components=model.components,
        component_scale=model.component_scale,
        target_mean=model.target_mean + residual_location,
        coefficients=model.coefficients,
        alpha=model.alpha,
    )
    return ConditionalCalibration(
        model=adjusted_model,
        threshold=threshold,
        residual_scale=residual_scale,
        selected_alpha=alpha,
        cv_mean_absolute_fpr_error=error,
        cv_fpr_by_video=per_video,
        cross_fitted_scores=normalized,
    )


def _cross_fitted_predictions(
    features: np.ndarray,
    targets: np.ndarray,
    video_ids: np.ndarray,
    rank: int,
    alpha: float,
) -> np.ndarray:
    predictions = np.empty(len(targets), dtype=np.float64)
    for video in np.unique(video_ids):
        held = video_ids == video
        model = _fit_pca_ridge(features[~held], targets[~held], rank, alpha)
        predictions[held] = model.predict(features[held])
    return predictions


def _fit_pca_ridge(
    features: np.ndarray,
    targets: np.ndarray,
    rank: int,
    alpha: float,
) -> PcaRidgeModel:
    features = np.asarray(features, dtype=np.float64)
    targets = np.asarray(targets, dtype=np.float64)
    feature_mean = features.mean(axis=0)
    centered = features - feature_mean
    _, _, right = np.linalg.svd(centered, full_matrices=False)
    effective_rank = max(1, min(int(rank), right.shape[0]))
    components = right[:effective_rank]
    context = centered @ components.T
    component_scale = np.maximum(np.std(context, axis=0), EPSILON)
    context = context / component_scale
    target_mean = float(np.mean(targets))
    centered_target = targets - target_mean
    system = context.T @ context + float(alpha) * np.eye(effective_rank)
    coefficients = np.linalg.solve(system, context.T @ centered_target)
    return PcaRidgeModel(
        feature_mean=feature_mean,
        components=components,
        component_scale=component_scale,
        target_mean=target_mean,
        coefficients=coefficients,
        alpha=float(alpha),
    )
