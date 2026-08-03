# 当前研究状态总览

**日期：** 2026-08-03
**状态类型：** 状态同步与执行边界记录
**当前状态：** `RESTRICTED BRIDGE AUTHORIZED / IN PROGRESS`

## Research direction

面向通用公开视频异常检测数据集的 normal-only VAD，重点关注未见场景、跨场景/跨数据集泛化和低误报工作点。

## Current hypothesis and contribution boundary

SRN 是唯一主机制：在 frozen representation 上学习低容量 scene token `c`，预测 scene-predictable component `u_hat`，构造 `r=P(z-u_hat)`，并通过低容量 `q=a(c)` 保留受控上下文，最终以 `e=concat(r, lambda*q)` 建模 normality。

- ELOS 仅是 whole-scene held-out 训练/验证原则，不是独立贡献。
- source-threshold、low-FPR、FA/hour 是评价纪律，不是方法 novelty。
- AMCN 不进入 restricted bridge 首轮。
- SRN 必须胜过 raw、scene/background subtraction 与 generic adversarial residual 才能保留机制 claim。

## Review status

- Original review：`REVISE / NOT READY`。
- Revision re-review：`READY WITH RESTRICTIONS`。
- Prior-work Round 2：`NOVELTY PLAUSIBLE / READY TO REQUEST RESTRICTED BRIDGE`。
- 2026-08-03 用户已正式授权 restricted bridge 的 audit、代码骨架、CPU dry-run 和 run planning 阶段。

## Completed in current bridge phase

- 完整核对冻结规格及其直接引用的 current documents。
- 完成本地 Tier A 数据、feature、代码、split、环境、磁盘和版本审计：`RESTRICTED_BRIDGE_AUDIT.md`。
- 实现统一 frozen-feature bridge：raw/kNN/Gaussian/prototype、scene/background subtraction、adversarial residual、full SRN、SRN without ELOS、ELOS without SRN、residual-only、calibration 与 threshold tracks。
- 通过 CPU synthetic dry-run：2 seeds × 11 matrix entries；结果可重复，但不属于科研结果。
- 生成 `RESTRICTED_BRIDGE_RUN_PLAN.md` 和 `[local-only]` code review。

## Current assets and blockers

- Ped2、Avenue、ShanghaiTech 本地均未发现；没有可复用 Tier A frozen features。
- 其他项目的工业 normal/abnormal features 不属于 public VAD，禁止复用。
- DINOv2-S/14 checkpoint/cache 尚不存在；数据许可、checksum、真实 split、fps 与 label alignment 未核验。
- Ped2/Avenue 只能先做轻量双数据域 pilot，不能单独关闭 whole-scene/ELOS gate；通过后才可申请 ShanghaiTech gated stage。

## Authorized now

- 继续完善受冻结协议约束的代码、测试和文档。
- 在已有合规 cache 时执行 CPU preflight；当前 cache 不存在，因此正式运行未开始。

## Still controlled / not executed

- 不自动下载 Tier A/Tier B 数据或 backbone weights。
- 不使用 GPU，不做 feature extraction，不启动正式训练/正式 evaluation。
- 不做 end-to-end fine-tuning，不使用异常训练样本，不使用 target anomaly 调阈值。
- 不引入 AMCN，不扩展 Tier B，不进入 ShanghaiTech 实际运行。

正式运行状态为 `PLAN READY / BLOCKED ON AUTHORIZED DATA AND FROZEN FEATURES`。下一步需要用户单独授权合法数据获取和 frozen feature extraction，或提供现有合规 cache。
