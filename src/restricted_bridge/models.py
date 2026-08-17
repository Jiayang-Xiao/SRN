"""restricted bridge 实验中的表示模型与训练损失。

本模块包含三类表示：原样输出冻结特征的 identity 表示、通过梯度反转弱化场景
信息的 adversarial residual，以及显式预测并扣除场景分量的 SRN。所有模型都
返回统一的 ``RepresentationOutput``，便于 runner 在训练和评分阶段复用同一套
接口。
"""

from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn
from torch.nn import functional as F


class _GradientReverse(torch.autograd.Function):
    """梯度反转层的自定义 autograd 实现。

    前向传播时该层等价于恒等映射；反向传播时把传回的梯度乘以
    ``-weight``。它常用于对抗训练：下游分类器尝试预测场景，主干表示则通过
    反向梯度学习“不要保留容易被分类器利用的场景信息”。
    """

    @staticmethod
    def forward(ctx, value: torch.Tensor, weight: float) -> torch.Tensor:
        """执行恒等前向传播并保存反向权重。

        Args:
            ctx: PyTorch autograd 上下文，用于把 ``weight`` 传给 backward。
            value: 输入张量。
            weight: 反向传播时的梯度缩放系数。

        Returns:
            与输入形状和值相同的张量视图。
        """
        ctx.weight = weight
        return value.view_as(value)

    @staticmethod
    def backward(ctx, gradient: torch.Tensor):
        """把输入梯度反号并按权重缩放。

        Args:
            ctx: 保存了 ``weight`` 的 autograd 上下文。
            gradient: 从上游传入的梯度。

        Returns:
            第一个返回值是对 ``value`` 的梯度；第二个返回值对应 ``weight``，
            由于 ``weight`` 是普通浮点超参数，因此不需要梯度。
        """
        return -ctx.weight * gradient, None


@dataclass
class RepresentationOutput:
    """表示模型的统一输出结构。

    Attributes:
        embedding: 送入异常评分器的最终表示。不同方法可能是原始特征、残差
            特征，或残差与场景上下文拼接后的向量。
        residual: 去场景化后的残差表示。诊断指标会用它衡量方差保留情况。
        scene_token: SRN 提取的低维场景 token。非 SRN 方法通常为 ``None``。
        scene_component: SRN 根据场景 token 预测出的场景分量，用于从原特征中
            扣除并计算 scene prediction/capacity 损失。
        scene_logits: 场景分类器输出。对抗残差和 SRN 用它训练去场景化表示。
    """

    embedding: torch.Tensor
    residual: torch.Tensor
    scene_token: torch.Tensor | None = None
    scene_component: torch.Tensor | None = None
    scene_logits: torch.Tensor | None = None


class IdentityRepresentation(nn.Module):
    """不改变输入特征的基线表示模型。"""

    def forward(self, features: torch.Tensor) -> RepresentationOutput:
        """直接把冻结特征作为 embedding 和 residual 返回。

        Args:
            features: 形状为 ``[batch, feature_dim]`` 的冻结特征。

        Returns:
            ``RepresentationOutput``，其中 ``embedding`` 和 ``residual`` 都是
            输入特征本身。
        """
        return RepresentationOutput(features, features)


class AdversarialResidual(nn.Module):
    """使用对抗场景分类器学习残差表示。

    该模型先用一个初始化为单位矩阵的线性层投影特征，再通过梯度反转层连接到
    场景分类器。分类器本身会尝试预测训练场景；投影层收到反向梯度后会减少
    残差中可预测场景的信息。
    """

    def __init__(self, feature_dim: int, num_scenes: int, adversarial_weight: float):
        """初始化对抗残差模型。

        Args:
            feature_dim: 输入冻结特征维度，同时也是残差维度。
            num_scenes: 训练集中源场景数量，决定场景分类器输出维度。
            adversarial_weight: 梯度反转层的缩放权重，越大表示去场景化压力越强。
        """
        super().__init__()
        self.projector = nn.Linear(feature_dim, feature_dim, bias=False)
        nn.init.eye_(self.projector.weight)
        self.scene_classifier = nn.Linear(feature_dim, num_scenes)
        self.adversarial_weight = adversarial_weight

    def forward(self, features: torch.Tensor) -> RepresentationOutput:
        """计算残差 embedding 和场景分类 logits。

        Args:
            features: 形状为 ``[batch, feature_dim]`` 的冻结特征。

        Returns:
            ``RepresentationOutput``。``embedding`` 与 ``residual`` 都是投影后的
            残差；``scene_logits`` 来自经过梯度反转的残差。
        """
        residual = self.projector(features)
        reversed_residual = _GradientReverse.apply(residual, self.adversarial_weight)
        logits = self.scene_classifier(reversed_residual)
        return RepresentationOutput(residual, residual, scene_logits=logits)


class SRN(nn.Module):
    """Scene Residual Network 表示模型。

    SRN 先从冻结特征中抽取低维 ``scene_token``，再用它预测可扣除的
    ``scene_component``。扣除场景分量后的 residual 进入异常评分器；可选的
    context path 会把场景 token 映射成上下文向量并拼接回 embedding，用于比较
    “只用残差”和“残差+受限场景上下文”的效果。
    """

    def __init__(
        self,
        feature_dim: int,
        scene_token_dim: int,
        scene_predictor_rank: int,
        context_dim: int,
        num_scenes: int,
        context_lambda: float,
        use_context: bool,
        adversarial_weight: float,
    ):
        """初始化 SRN。

        Args:
            feature_dim: 输入冻结特征维度。
            scene_token_dim: 场景 token 的低维瓶颈大小。
            context_dim: 可选上下文向量维度。
            num_scenes: 训练源场景数量，决定对抗场景分类器输出维度。
            context_lambda: 上下文向量拼接前的缩放系数。
            use_context: 是否把 context path 输出拼接到 residual 上。
            adversarial_weight: 对抗场景分类梯度反转权重。
        """
        super().__init__()
        self.scene_token = nn.Linear(feature_dim, scene_token_dim)
        self.scene_predictor = nn.Sequential(
            nn.Linear(scene_token_dim, scene_predictor_rank, bias=False),
            nn.Linear(scene_predictor_rank, feature_dim, bias=False),
        )
        self.residual_projector = nn.Linear(feature_dim, feature_dim, bias=False)
        nn.init.eye_(self.residual_projector.weight)
        self.context_path = nn.Linear(scene_token_dim, context_dim)
        self.scene_classifier = nn.Linear(feature_dim, num_scenes)
        self.context_lambda = context_lambda
        self.use_context = use_context
        self.adversarial_weight = adversarial_weight

    def forward(self, features: torch.Tensor) -> RepresentationOutput:
        """把冻结特征分解为场景分量、残差分量和最终 embedding。

        Args:
            features: 形状为 ``[batch, feature_dim]`` 的冻结特征。

        Returns:
            ``RepresentationOutput``。当 ``use_context`` 为真时，``embedding``
            是 ``[residual, context_lambda * context]`` 的拼接；否则只包含
            residual。
        """
        token = self.scene_token(features)
        scene_component = self.scene_predictor(token)
        residual = self.residual_projector(features - scene_component)
        scene_logits = self.scene_classifier(
            _GradientReverse.apply(residual, self.adversarial_weight)
        )
        if self.use_context:
            context = self.context_lambda * self.context_path(token)
            embedding = torch.cat((residual, context), dim=1)
        else:
            embedding = residual
        return RepresentationOutput(
            embedding=embedding,
            residual=residual,
            scene_token=token,
            scene_component=scene_component,
            scene_logits=scene_logits,
        )


def representation_loss(
    model: nn.Module,
    output: RepresentationOutput,
    features: torch.Tensor,
    scene_targets: torch.Tensor,
    scene_labels: torch.Tensor,
    weights: dict,
) -> tuple[torch.Tensor, dict[str, float]]:
    """计算表示学习阶段的总损失及各项分量。

    Args:
        model: 当前训练的表示模型。函数会从模型上读取 ``residual_projector`` 或
            ``projector``，用于计算保持接近单位映射的 retention 损失。
        output: 模型前向传播得到的统一输出。
        features: 输入冻结特征批次。
        scene_targets: 每个样本对应的场景均值目标，用于训练 SRN 的场景分量预测。
        scene_labels: 每个样本的源场景类别标签，用于对抗场景分类。
        weights: 损失权重字典。支持 ``normal``、``scene_prediction``、
            ``capacity`` 和 ``retention``，缺省时使用代码中的默认值。

    Returns:
        二元组 ``(total, parts)``。``total`` 是可反向传播的 PyTorch 标量；
        ``parts`` 是已经 detach 并转成 Python float 的日志字典。

    Notes:
        损失由五部分组成：embedding compactness 约束正常样本聚集；
        scene prediction 约束 SRN 预测可扣除的场景分量；scene classification
        通过梯度反转提供去场景化压力；capacity 限制场景分量能量；retention
        防止残差投影层过度偏离单位映射。
    """
    center = output.embedding.mean(dim=0, keepdim=True).detach()
    compactness = (output.embedding - center).square().mean()
    scene_cls = (
        F.cross_entropy(output.scene_logits, scene_labels)
        if output.scene_logits is not None
        else features.new_zeros(())
    )
    scene_prediction = (
        F.mse_loss(output.scene_component, scene_targets)
        if output.scene_component is not None
        else features.new_zeros(())
    )
    capacity = (
        output.scene_component.square().mean()
        if output.scene_component is not None
        else features.new_zeros(())
    )
    projector = getattr(model, "residual_projector", getattr(model, "projector", None))
    identity = torch.eye(features.shape[1], device=features.device)
    retention = (
        F.mse_loss(projector.weight, identity) if projector is not None else features.new_zeros(())
    )
    total = (
        float(weights.get("normal", 1.0)) * compactness
        + float(weights.get("scene_prediction", 1.0)) * scene_prediction
        + scene_cls
        + float(weights.get("capacity", 0.01)) * capacity
        + float(weights.get("retention", 1.0)) * retention
    )
    parts = {
        "total": float(total.detach()),
        "normal": float(compactness.detach()),
        "scene_prediction": float(scene_prediction.detach()),
        "scene_classification": float(scene_cls.detach()),
        "capacity": float(capacity.detach()),
        "retention": float(retention.detach()),
    }
    return total, parts
