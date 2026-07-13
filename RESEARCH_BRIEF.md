# Research Brief: General Normal-Only Video Anomaly Detection

## Problem Statement

在公开/通用视频异常检测（VAD）基准上，仅使用 normal training videos 学习正常性，并重点研究模型在未见场景、未见摄像机和跨数据集条件下的泛化，而不是继续只优化单数据集 frame-level AUC。

## Frozen Scope

- **包含**：normal-only training、public/general VAD benchmarks、cross-scene / cross-dataset generalization、scene-agnostic normality modeling、realistic evaluation、有限算力实现。
- **不包含**：工业专用数据、音视频多模态、weakly supervised abnormal-video training、fully unsupervised mixed training、通用视频理解、异常类别识别。
- 异常样本只可用于测试与最终评估；不得用于模型训练、超参数选择或目标域阈值调优。

## Resources and Constraints

- 环境：`aris-torch`，双 RTX 3090，但每次任务必须动态选卡。
- 当前阶段：只做文献、idea、查新和实验规划；不下载数据，不运行训练或 pilot。
- 目标：先建立可复现、低算力的 frozen-feature baseline，再验证一个聚焦的跨场景机制。

## Success Condition

一个值得进入实现阶段的方案应同时满足：

1. 在 within-dataset 基准不明显退化；
2. 在 leave-one-scene-out 与 cross-dataset 矩阵上稳定优于简单 frozen-feature kNN / Mahalanobis；
3. 在 macro-AUROC、AUPRC、低 FPR recall、false alarms/hour 中至少多数指标改善；
4. 不依赖目标测试集异常、目标域标签或每数据集单独阈值调优；
5. 单个核心实验可在一张 24GB RTX 3090 上完成。
