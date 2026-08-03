from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn
from torch.nn import functional as F


class _GradientReverse(torch.autograd.Function):
    @staticmethod
    def forward(ctx, value: torch.Tensor, weight: float) -> torch.Tensor:
        ctx.weight = weight
        return value.view_as(value)

    @staticmethod
    def backward(ctx, gradient: torch.Tensor):
        return -ctx.weight * gradient, None


@dataclass
class RepresentationOutput:
    embedding: torch.Tensor
    residual: torch.Tensor
    scene_token: torch.Tensor | None = None
    scene_component: torch.Tensor | None = None
    scene_logits: torch.Tensor | None = None


class IdentityRepresentation(nn.Module):
    def forward(self, features: torch.Tensor) -> RepresentationOutput:
        return RepresentationOutput(features, features)


class AdversarialResidual(nn.Module):
    def __init__(self, feature_dim: int, num_scenes: int, adversarial_weight: float):
        super().__init__()
        self.projector = nn.Linear(feature_dim, feature_dim, bias=False)
        nn.init.eye_(self.projector.weight)
        self.scene_classifier = nn.Linear(feature_dim, num_scenes)
        self.adversarial_weight = adversarial_weight

    def forward(self, features: torch.Tensor) -> RepresentationOutput:
        residual = self.projector(features)
        reversed_residual = _GradientReverse.apply(residual, self.adversarial_weight)
        logits = self.scene_classifier(reversed_residual)
        return RepresentationOutput(residual, residual, scene_logits=logits)


class SRN(nn.Module):
    def __init__(
        self,
        feature_dim: int,
        scene_token_dim: int,
        context_dim: int,
        num_scenes: int,
        context_lambda: float,
        use_context: bool,
        adversarial_weight: float,
    ):
        super().__init__()
        self.scene_token = nn.Linear(feature_dim, scene_token_dim)
        self.scene_predictor = nn.Linear(scene_token_dim, feature_dim, bias=False)
        self.residual_projector = nn.Linear(feature_dim, feature_dim, bias=False)
        nn.init.eye_(self.residual_projector.weight)
        self.context_path = nn.Linear(scene_token_dim, context_dim)
        self.scene_classifier = nn.Linear(feature_dim, num_scenes)
        self.context_lambda = context_lambda
        self.use_context = use_context
        self.adversarial_weight = adversarial_weight

    def forward(self, features: torch.Tensor) -> RepresentationOutput:
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
