"""冻结表示上的无监督异常评分器。

评分器都遵循同一接口：先在训练 embedding 上 ``fit``，再对任意切分的 embedding
调用 ``score`` 得到一维异常分数。分数越高表示样本越偏离训练正常分布。
"""

from __future__ import annotations

import numpy as np


class KNNScorer:
    """基于 k 近邻平均距离的异常评分器。

    训练阶段只保存正常训练 embedding；评分阶段计算样本到训练 bank 的平方距离，
    并取最近 ``k`` 个距离的平均值作为异常分数。
    """

    def __init__(self, k: int = 5, batch_size: int = 2048):
        """初始化 kNN 评分器。

        Args:
            k: 评分时参与平均的最近邻数量。实际使用时会被截断到训练样本数。
        """
        self.k = k
        self.batch_size = batch_size
        self.bank: np.ndarray | None = None

    def fit(self, features: np.ndarray, seed: int = 0) -> None:
        """保存训练特征库。

        Args:
            features: 形状为 ``[N, D]`` 的训练 embedding。
            seed: 保持评分器统一接口的随机种子参数。kNN 不需要随机性，因此会被
                显式丢弃。
        """
        del seed
        self.bank = np.asarray(features, dtype=np.float64)

    def score(self, features: np.ndarray) -> np.ndarray:
        """计算样本到训练特征库的 kNN 平均平方距离。

        Args:
            features: 待评分 embedding，形状为 ``[M, D]``。

        Returns:
            长度为 ``M`` 的异常分数数组。

        Raises:
            RuntimeError: 当评分器尚未调用 ``fit`` 时抛出。
        """
        if self.bank is None:
            raise RuntimeError("scorer is not fitted")
        values = np.asarray(features, dtype=np.float64)
        k = min(self.k, self.bank.shape[0])
        chunks = []
        for start in range(0, len(values), self.batch_size):
            distances = _squared_distances(
                values[start:start + self.batch_size], self.bank
            )
            chunks.append(
                np.partition(distances, k - 1, axis=1)[:, :k].mean(axis=1)
            )
        return np.concatenate(chunks) if chunks else np.empty(0, dtype=np.float64)


class GaussianScorer:
    """基于收缩协方差高斯模型的马氏距离评分器。"""

    def __init__(self, shrinkage: float = 0.1):
        """初始化高斯评分器。

        Args:
            shrinkage: 协方差向各向同性对角矩阵收缩的比例。该值越大，协方差
                越接近 ``scale * I``，在样本数较少或维度较高时更稳定。
        """
        self.shrinkage = shrinkage
        self.mean: np.ndarray | None = None
        self.precision: np.ndarray | None = None

    def fit(self, features: np.ndarray, seed: int = 0) -> None:
        """估计训练 embedding 的均值和精度矩阵。

        Args:
            features: 形状为 ``[N, D]`` 的训练 embedding。
            seed: 保持接口一致的随机种子参数。高斯估计是确定性的，因此会被丢弃。

        Notes:
            函数先计算经验协方差，再按 ``shrinkage`` 注入对角正则，最后使用
            Moore-Penrose 伪逆得到精度矩阵。伪逆让退化协方差也能被处理。
        """
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
        """计算每个样本到训练高斯分布的马氏距离。

        Args:
            features: 待评分 embedding，形状为 ``[M, D]``。

        Returns:
            长度为 ``M`` 的非负异常分数数组。

        Raises:
            RuntimeError: 当均值或精度矩阵尚未通过 ``fit`` 得到时抛出。
        """
        if self.mean is None or self.precision is None:
            raise RuntimeError("scorer is not fitted")
        centered = np.asarray(features, dtype=np.float64) - self.mean
        return np.einsum("ni,ij,nj->n", centered, self.precision, centered)


class PrototypeScorer:
    """基于原型中心最近距离的异常评分器。

    训练阶段用简化 k-means 在正常 embedding 中学习若干原型；评分阶段返回样本
    到最近原型中心的平方距离。
    """

    def __init__(self, prototypes: int = 8, iterations: int = 20):
        """初始化原型评分器。

        Args:
            prototypes: 期望学习的原型中心数量。实际数量不会超过训练样本数。
            iterations: k-means 更新的最大迭代次数。
        """
        self.prototypes = prototypes
        self.iterations = iterations
        self.centers: np.ndarray | None = None

    def fit(self, features: np.ndarray, seed: int = 0) -> None:
        """用训练 embedding 学习原型中心。

        Args:
            features: 形状为 ``[N, D]`` 的训练 embedding。
            seed: 初始化原型中心时使用的随机种子。

        Notes:
            初始中心从训练样本中无放回抽样。每轮先分配最近中心，再用簇均值更新；
            如果某个簇为空，则保留该中心，避免产生 NaN。
        """
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
        """计算到最近原型中心的平方距离。

        Args:
            features: 待评分 embedding，形状为 ``[M, D]``。

        Returns:
            长度为 ``M`` 的异常分数数组。

        Raises:
            RuntimeError: 当评分器尚未调用 ``fit`` 时抛出。
        """
        if self.centers is None:
            raise RuntimeError("scorer is not fitted")
        return _squared_distances(np.asarray(features, dtype=np.float64), self.centers).min(axis=1)


def build_scorer(name: str, config: dict):
    """根据配置名称构造评分器实例。

    Args:
        name: 评分器名称，支持 ``knn``、``gaussian`` 和 ``prototype``。
        config: 评分器配置子树。不同评分器会读取各自需要的超参数。

    Returns:
        已初始化但尚未 ``fit`` 的评分器对象。

    Raises:
        ValueError: 当 ``name`` 不是已知评分器名称时抛出。
    """
    if name == "knn":
        return KNNScorer(
            int(config.get("knn_k", 5)),
            int(config.get("distance_batch_size", 2048)),
        )
    if name == "gaussian":
        return GaussianScorer(float(config.get("gaussian_shrinkage", 0.1)))
    if name == "prototype":
        return PrototypeScorer(int(config.get("prototype_count", 8)))
    raise ValueError(f"unknown scorer: {name}")


def _squared_distances(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """批量计算两个矩阵之间的平方欧氏距离。

    Args:
        left: 左侧样本矩阵，形状为 ``[N, D]``。
        right: 右侧样本矩阵，形状为 ``[M, D]``。

    Returns:
        形状为 ``[N, M]`` 的距离矩阵，其中第 ``i, j`` 项是
        ``left[i]`` 与 ``right[j]`` 的平方欧氏距离。

    Notes:
        公式 ``||x||^2 + ||y||^2 - 2 x@y`` 可能因浮点舍入产生极小负数，因此
        返回前会用 ``np.maximum`` 截断到非负。
    """
    distances = (
        np.sum(left * left, axis=1, keepdims=True)
        + np.sum(right * right, axis=1)[None, :]
        - 2.0 * left @ right.T
    )
    return np.maximum(distances, 0.0)
