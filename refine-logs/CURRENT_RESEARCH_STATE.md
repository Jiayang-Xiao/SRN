# 当前研究状态总览

**日期：** 2026-07-13  
**状态类型：** 状态同步与执行边界记录  
**注意：** 本文件不授权数据下载、GPU feature extraction、训练或 `/experiment-bridge` 启动。

## Research direction

面向通用公开视频异常检测数据集的 **normal-only 视频异常检测**，重点关注未见场景、跨场景、跨数据集泛化，以及低误报部署工作点。

## Current main hypothesis

在 normal-only VAD 中，跨场景失败的一部分来自 frozen representation 中可识别 source scene、但与短时事件动态弱相关的 nuisance leakage。若只抑制这些 scene-identifying components，并通过 context-retention diagnostics 与 leave-one-scene validation 限制过度去场景化，则可能改善 fixed source-threshold 下的 unseen-scene low-FPR performance。

## Current primary path

**SRN + ELOS**

- SRN 是主要机制：selective scene-residual normality。
- ELOS 是训练/验证原则：held-out scene episode，不作为独立贡献。
- 首轮 restricted bridge 若获授权，只能验证 minimal SRN 是否优于 raw、mean/background subtraction 和 adversarial residual baselines。

## Backup path

**AMCN**

AMCN 保留为 backup path。它不进入首轮 restricted bridge；只有 SRN novelty 或 motion-dominant failures 暴露后，并且 conditional motion prediction prior work 留出明确空缺时，才考虑启动。

## Review status

- Original review verdict：**REVISE / NOT READY**
- Original review files：`refine-logs/INDEPENDENT_REVIEW_RAW.md`、`refine-logs/INDEPENDENT_REVIEW_SUMMARY.md`
- Revision re-review verdict：**READY WITH RESTRICTIONS**
- Revision re-review files：`refine-logs/REVISION_REVIEW_RAW.md`、`refine-logs/REVISION_REVIEW_SUMMARY.md`

## Current execution status

**HOLD**

restricted bridge status：**not started**

当前状态是 **READY WITH RESTRICTIONS / HOLD**。这表示文档和计划已经允许后续申请 restricted bridge，但不表示已经可以直接运行实验。

## Freeze artifacts

2026-07-13 已生成：

- `refine-logs/PRIOR_WORK_PATCH.md`
- `refine-logs/SRN_MINIMAL_SPEC.md`
- `refine-logs/BASELINE_REGISTRY.md`
- `refine-logs/PROTOCOL_MANIFEST.md`

## Allowed next actions

- prior work verification；
- local Tier A dataset availability check；
- restricted bridge planning；
- code skeleton / dry-run only if separately authorized。

## Forbidden actions

- no data download without user authorization；
- no GPU feature extraction without user authorization；
- no training without user authorization；
- no Tier B dataset download；
- no end-to-end backbone fine-tuning；
- no abnormal training labels。

## Unresolved blockers

- `PRIOR_WORK_PATCH.md` 中仍有 `TODO: verify` prior work，需要后续核验。
- Tier A 数据本地可用性和许可状态尚未确认。
- 数据下载尚未授权。
- GPU feature extraction 尚未授权。
- 训练尚未授权。
- restricted bridge 尚未启动。

## Next user decision options

1. 仅继续 prior work verification，不触碰数据和 GPU。
2. 只检查本地是否已有 Tier A 数据副本，不下载新数据。
3. 授权 restricted bridge planning 的代码骨架和 dry-run，但不下载数据、不训练。
4. 单独授权 Tier A 数据下载。
5. 单独授权 GPU feature extraction / minimal pilot；若授权，仍必须限制在 frozen-feature audit + minimal SRN-vs-adversarial pilot。
