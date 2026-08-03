from __future__ import annotations

import numpy as np


class KNNScorer:
    def __init__(self, k: int = 5):
        self.k = k
        self.bank: np.ndarray | None = None

    def fit(self, features: np.ndarray, seed: int = 0) -> None:
        del seed
        self.bank = np.asarray(features, dtype=np.float64)

    def score(self, features: np.ndarray) -> np.ndarray:
        if self.bank is None:
            raise RuntimeError("scorer is not fitted")
        distances = _squared_distances(np.asarray(features, dtype=np.float64), self.bank)
        k = min(self.k, self.bank.shape[0])
        return np.partition(distances, k - 1, axis=1)[:, :k].mean(axis=1)


class GaussianScorer:
    def __init__(self, shrinkage: float = 0.1):
        self.shrinkage = shrinkage
        self.mean: np.ndarray | None = None
        self.precision: np.ndarray | None = None

    def fit(self, features: np.ndarray, seed: int = 0) -> None:
        del seed
        values = np.asarray(features, dtype=np.float64)
        self.mean = values.mean(axis=0)
        centered = values - self.mean
        covariance = centered.T @ centered / max(1, len(values) - 1)
        scale = max(float(np.trace(covariance) / covariance.shape[0]), 1e-6)
        covariance = (1.0 - self.shrinkage) * covariance
        covariance += self.shrinkage * scale * np.eye(covariance.shape[0])
        self.precision = np.linalg.pinv(covariance, hermitian=True)

    def score(self, features: np.ndarray) -> np.ndarray:
        if self.mean is None or self.precision is None:
            raise RuntimeError("scorer is not fitted")
        centered = np.asarray(features, dtype=np.float64) - self.mean
        return np.einsum("ni,ij,nj->n", centered, self.precision, centered)


class PrototypeScorer:
    def __init__(self, prototypes: int = 8, iterations: int = 20):
        self.prototypes = prototypes
        self.iterations = iterations
        self.centers: np.ndarray | None = None

    def fit(self, features: np.ndarray, seed: int = 0) -> None:
        values = np.asarray(features, dtype=np.float64)
        count = min(self.prototypes, len(values))
        rng = np.random.default_rng(seed)
        centers = values[rng.choice(len(values), size=count, replace=False)].copy()
        for _ in range(self.iterations):
            assignments = _squared_distances(values, centers).argmin(axis=1)
            updated = np.stack(
                [values[assignments == index].mean(axis=0) if np.any(assignments == index)
                 else centers[index] for index in range(count)]
            )
            if np.allclose(updated, centers):
                break
            centers = updated
        self.centers = centers

    def score(self, features: np.ndarray) -> np.ndarray:
        if self.centers is None:
            raise RuntimeError("scorer is not fitted")
        return _squared_distances(np.asarray(features, dtype=np.float64), self.centers).min(axis=1)


def build_scorer(name: str, config: dict):
    if name == "knn":
        return KNNScorer(int(config.get("knn_k", 5)))
    if name == "gaussian":
        return GaussianScorer(float(config.get("gaussian_shrinkage", 0.1)))
    if name == "prototype":
        return PrototypeScorer(int(config.get("prototype_count", 8)))
    raise ValueError(f"unknown scorer: {name}")


def _squared_distances(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    distances = (
        np.sum(left * left, axis=1, keepdims=True)
        + np.sum(right * right, axis=1)[None, :]
        - 2.0 * left @ right.T
    )
    return np.maximum(distances, 0.0)
