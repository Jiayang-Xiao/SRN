# 实验计划：Scene-Residual Normality

> 修订依据：`refine-logs/REVISION_ACTION_PLAN.md`。DeepSeek 原始结论为 **REVISE / NOT READY**；2026-07-12 re-review 将修订后计划升级为 **READY WITH RESTRICTIONS**。本文件只规定未来证据，不报告已完成实验。

## Gate 1 — 实现前修订闭环

- Re-review 解释：只有下列文档 gate 冻结后，才允许 restricted bridge；本轮不启动 `/experiment-bridge`。
- reviewer-driven prior-work patch 已冻结为 `refine-logs/PRIOR_WORK_PATCH.md`；其中未核验论文继续标注 `TODO: verify`，query seed 不等于 verified citation。
- SRN 最小数学定义已冻结为 `refine-logs/SRN_MINIMAL_SPEC.md`：scene token、capacity-constrained suppression、residual/context score、loss、inference path 与 target-time freezing。
- baseline registry 与共享预算已冻结为 `refine-logs/BASELINE_REGISTRY.md`；核心对照包含 raw kNN/Mahalanobis、prototype/memory bank、scene/background mean subtraction、GRL/MMD-style invariance、ERM/ELOS、calibration controls。
- strict-zero-shot 与 target-normal calibration 协议已冻结为 `refine-logs/PROTOCOL_MANIFEST.md`，使用独立许可、调参流程与结果表。
- 冻结 minimal pilot 的成功、否证和 stop criteria；首轮范围只允许 frozen-feature audit + SRN-vs-adversarial pilot。
- 关闭 bridge 流程冲突：决定 pilot 是 pre-bridge 执行，还是作为 restricted bridge 的唯一首轮任务。

## Gate 0 — 无训练预检查

- 确认 Avenue、ShanghaiTech、Ped2 的官方下载/许可与 checksum；暂不下载 NWPU。
- 固化统一帧率、resize、clip length、stride、标签对齐和 score smoothing。
- 复核 arXiv:2606.29506 的代码与 split，建立不可变 same/cross matrix manifest。
- 明确两个 protocol：`strict-zero-shot`（无目标 normal data）与 `normal-calibration`（只允许目标 normal calibration），主论文以前者为主。
- 核验 DeepSeek external review 列出的 domain-adversarial/MMD disentanglement、conditional motion–appearance、meta-learning、prototype alignment 与 Self-Distilled MAE 相关工作；未经核验的 reviewer 论文名不直接写入 bibliography。
- 写清 SRN scene token、subtraction、normality head、context path、全部 loss 和 target-time freezing 规则。
- 将所有 idea 明确归入 `strict-zero-shot` 或 `normal-calibration`，结果表完全分开。

## Claims 与实验

### E1 — Frozen-feature audit baseline

- Backbones：DINOv2-S/14 frame pooling、轻量 VideoMAE/VideoMAE-v2（视可用 checkpoint）。
- Heads：kNN、shrinkage Mahalanobis / Gaussian density。
- 数据：Ped2、Avenue、ShanghaiTech；形成完整 source→target matrix。
- 指标：micro/macro AUROC、AUPRC、TPR@1%FPR、FA/hour。
- Gate：若无法复现“显著 cross-domain collapse”，暂停方法实验并审计预处理。

### E2 — SRN 主对照

- Baselines：raw feature、per-scene mean subtraction、background mean subtraction、PCA nuisance removal、frozen DINOv2 + gradient reversal scene classifier + prototype head、可行时的 MMD control、SRN。
- 主实验：ShanghaiTech LOSO；Ped2/Avenue/ShanghaiTech leave-one-dataset-out。
- Claim success：off-diagonal macro-AUROC 平均提升至少 3 points，且 worst-target 不下降；同域平均下降不超过 2 points。

### E3 — 机制隔离

- 删除 scene projector。
- 删除 residual scene-confusion。
- 删除 ELOS episodes。
- scene token：background mean vs temporal pooled token。
- learned scene token vs random/constant token；scene-token dimension 与 residual bottleneck sweep。
- context path on/off；严格冻结 vs 任何 target-normal adaptation（后者只能进入 calibration track）。
- normality head：prototype vs Mahalanobis。
- ELOS vs scene-balanced ERM / leave-one-out ERM，保持架构、数据和预算完全一致。
- ELOS without SRN（raw feature + identical normality head），检验 episodic protocol 是否独立产生增益。
- scene-ID probe 与 event/motion retention probe 联合报告；只降低 scene-ID accuracy 不足以支持 claim。

### E4 — 真实可靠性指标

- 阈值只在 source normal validation 上确定。
- 报告 TPR@0.1%/1% FPR、FA/hour、每视频 macro metrics、95% bootstrap CI。
- 按 scene-dependent/location-dependent 与 generic motion anomalies 分层。
- 分层仅在官方标签或预先冻结的可审计映射允许时执行；否则报告 unavailable。
- calibration controls：raw score、source z-score、EVT/quantile/rank map；target-normal calibration 单独 track。

### E5 — 仅在正信号后 scale-up

- 加入 Street Scene、IITB Corridor；最后再评估 NWPU Campus。
- 若输出空间定位，加入 RBDC/TBDC；否则不虚报 localization 能力。

## 运行顺序与预算

| 顺序 | 模块 | 预计 GPU 成本 | 决策 |
|---|---|---:|---|
| 0 | 数据/协议/代码 preflight | 0 GPUh | 未通过则不进入 bridge |
| 1 | 单 backbone + 3 datasets audit | 5–15 GPUh（主要是 feature extraction） | 不复现 collapse 则停 |
| 2 | ShanghaiTech LOSO SRN pilot | 5–12 GPUh | <1 point 改善则重新设计 |
| 3 | 三数据集 cross matrix | 10–25 GPUh | 达到主 gate 再做消融 |
| 4 | 完整消融 + seeds | 20–50 GPUh | 决定论文 claim |
| 5 | Street/NWPU scale-up | 额外 30–80 GPUh | 仅正信号后执行 |

所有 GPU 命令必须使用：

```bash
eval "$(python scripts/select_free_gpu.py --emit-shell)" && python <task>.py
```

## Experiment-Bridge 准备状态

当前规划 verdict 为 **READY WITH RESTRICTIONS**，四个 pre-bridge freeze 文件已生成，但执行状态仍为 **HOLD**：restricted bridge 尚未启动，数据下载、GPU 使用和训练仍需用户单独授权。若后续进入 restricted bridge，首轮只能包含 frozen-feature audit 与 minimal SRN-vs-adversarial pilot；在正信号出现前禁止完整矩阵、扩展数据集、规模化训练和 backbone 微调。当前不启动任何实验。
