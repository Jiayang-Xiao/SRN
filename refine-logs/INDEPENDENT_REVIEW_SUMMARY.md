# DeepSeek Independent Review Summary

- **Reviewer backend:** DeepSeek API
- **Model:** `deepseek-v4-pro`
- **Date:** 2026-07-06
- **Source:** `refine-logs/INDEPENDENT_REVIEW_RAW.md`
- **Status:** faithful local summary of the external raw review; not a second review

## Overall verdict

Reviewer 认为研究假设有一定价值，但当前仍是零实验、pre-pilot 状态，SRN 的场景分量减法与既有 domain-invariant/disentanglement 方法区分不足，SRN 与 ELOS 的交互机制也未充分定义。总体结论是 **REVISE**，且明确建议当前不要进入 `/experiment-bridge`。

## Mainline judgments

- **SRN + ELOS:** 不同意按当前形式直接推进。明确 verdict 为 **REVISE**；需先定义 SRN 架构、损失、episode sampling 与防止 scene leakage 的约束，并用 pilot 证明 ELOS 相对 ERM 有增益。
- **AMCN:** Reviewer 未认为 AMCN 更适合作为主线。它最多是有条件的 auxiliary，只有在能补足 SRN 对快速运动异常的不足且胜过 conditional prediction baselines 时保留。
- **Reviewer top ranking:** SRN 第一；source-only rank calibration 第二；temporal false-alarm suppression 第三。后两者被视为实用辅助/评估项，而非高新颖度主贡献。

## Roles for all 11 ideas

| # | Idea | Reviewer role judgment |
|---|---|---|
| 1 | SRN | 仅在 pilot 显著优于 adversarial disentanglement baseline 时作为 main contribution；否则降为 auxiliary 或重构 |
| 2 | AMCN | 条件性 auxiliary；若不能证明与 SRN 互补则放弃 |
| 3 | ELOS | supporting training principle，不作为独立贡献 |
| 4 | Scene-conditional/agnostic mixture | low-priority auxiliary |
| 5 | Object-relation graph | abandon as contribution；仅作 baseline |
| 6 | Prototype transport | auxiliary at best；若无法与 SRN residual vocabulary 结合则放弃 |
| 7 | Source-free rank calibration | auxiliary calibration module；待 SRN score 可用后测试 |
| 8 | Temporal false-alarm suppression | baseline/protocol only |
| 9 | Counterfactual retrieval | abandon |
| 10 | Stress-test suite | evaluation protocol only，放 appendix |
| 11 | Normal-only masked distillation | baseline only |

## Prior work that must be checked

- VAD 中的 domain-adversarial、MMD-based disentanglement；
- conditional motion–appearance prediction / co-occurrence；
- Self-Distilled MAE (CVPR 2024) 及后续；
- scene/domain-shift VAD 的 meta-learning、few-shot scene adaptation；
- Rashidi 2026 cross-dataset audit 的 threshold-transfer 结论；
- prototype alignment in unsupervised domain adaptation。

Reviewer 要求至少补查并明确区分 5–7 项直接相关工作。原始评审中的部分论文名和年份仍需单独核验，不能直接当作已验证 bibliography。

## Required baselines

1. Frozen DINOv2 + gradient reversal scene classifier + prototype normality head 的 adversarial domain-invariant baseline；
2. AMCN 对应的 conditional ConvLSTM/future-prediction baseline；
3. 相同 SRN 架构的 leave-one-out ERM（无 ELOS）；
4. subtraction-free SRN；
5. random scene-token control；
6. frozen-feature kNN/Mahalanobis 与既有 cross-dataset audit 基线。

## Required ablations

- scene subtraction on/off；
- ELOS vs ERM，固定架构和数据；
- learned vs random/constant scene token；
- context path on/off 与其 target-time freezing；
- scene-token dimension / residual bottleneck；
- SRN vs adversarial disentanglement under identical backbone and head；
- strict-zero-shot 与 target-normal-calibration 完全分表；
- macro-AUROC、per-dataset AUPRC、low-FPR recall、false alarms/hour 与 cross-dataset matrix 分解报告。

## Experiment-bridge decision

**NOT READY.** Reviewer 明确要求先完成无大规模训练的架构/损失定义、prior-work 核验、evaluation-track 分离，以及一个最小 pilot 与非平凡 adversarial baseline 对比。只有 pilot 对 cross-dataset macro-AUROC 和 false alarms/hour 给出正信号后，才建议申请进入 `/experiment-bridge`。
