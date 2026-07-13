# 既有方法缺陷 → Gap → Idea 追踪

本文件是 canonical graph relations 的人类可读反向/materialized view。`graph/edges.jsonl` 保留 ARIS canonical `idea --addresses_gap--> gap`；下列表格额外展示 gap→idea 的阅读方向，但不发明未支持的 graph edge type。

## Paper / method → gap

| Prior work | 具体缺陷证据 | Gap |
|---|---|---|
| Rashidi 2026 frozen features + kNN/Mahalanobis | same-dataset 对角线结果无法迁移；off-diagonal 接近随机；更换 head 不能修复问题 | G1, G2, G3 |
| HSC | scene/object contrast 能建模已知场景多样性，但可能保留 scene identity，而不是获得 unseen-scene invariance | G1, G4 |
| PFMF | 通过 prompt-guided synthetic anomalies 和 adaptation 处理 scene/anomaly gap，引入 abnormal prior 与 virtual-real dependence | G4, G5 |
| Self-Distilled MAE | 效率高，但 reconstruction 仍与 appearance 耦合，完整 recipe 使用 synthetic abnormal augmentation | G1, G5 |
| EVAL / tracklet-based EVAL | explainable object/track modeling 依赖 detector 质量和 location-dependent scene model | G4, G5 |
| Street Scene protocol | frame/pixel criteria 不能准确反映 localization 或 operational false positives | G2, G3 |
| NWPU Campus | scene-dependent anomalies 说明 context 既必要，也可能导致过拟合 | G4 |

## Gap → ideas（反向视图）

| Gap | Ideas |
|---|---|
| G1 scene leakage | SRN, AMCN, ELOS, conditional mixture, object relation, prototype transport, counterfactual retrieval |
| G2 unrealistic aggregate evaluation | rank calibration, temporal suppression, stress-test suite |
| G3 threshold transfer | rank calibration, temporal suppression, stress-test suite |
| G4 context duality | SRN, AMCN, ELOS, conditional mixture, prototype transport |
| G5 practicality/abnormal-prior dependence | SRN, AMCN, object relation, masked distillation |

## Idea → 必需 ablation → novelty risk

| Idea | 决定性 ablation | novelty risk |
|---|---|---|
| SRN | raw vs mean subtraction vs adversarial projection vs SRN；scene probe；scene-dependent subset | domain factorization 已较成熟；必须证明 VAD-specific context preservation |
| AMCN | appearance-only、motion-only、concat、unconditional predictor、conditional model | conditional/two-stream prediction prior art |
| ELOS | 同架构下比较 random、scene-balanced 与 held-out-scene episodes | 标准 domain generalization；只能 supporting |
| Conditional mixture | global-only、adapter-only、fixed vs learned gate | 常见 MoE/adapter 机制，且有 contribution sprawl 风险 |
| Object relation | absolute vs relative attributes；oracle vs detected tracks | 与 EVAL/tracklet/object-centric 方法直接重叠 |
| Prototype transport | independent、pooled、matched、OT-aligned banks | generic prototype alignment/OT |
| Rank calibration | fixed threshold 下比较 raw/z-score/EVT/quantile/proposed map | 成熟 calibration/conformal family |
| Temporal suppression | no/hand smoothing/hysteresis/learned dynamics；short-event recall | 可能只是 post-processing |
| Counterfactual retrieval | raw vs factorized retrieval，以及 retrieval correctness | 与失败的 nearest-neighbour audit 直接重叠 |
| Stress-test suite | 复现 protocols，并测试 ranking sensitivity/leakage | Rashidi 2026 和 Street Scene 已建立很多核心论点 |
| Masked distillation | full published recipe vs no synthetic vs normal-only distillation | 与 CVPR 2024 Self-Distilled MAE 非常接近 |

完整分析见：`refine-logs/PRIOR_METHOD_DEFECT_TO_IDEA_MATRIX.md`。

## 外部独立评审 gate

DeepSeek API (`deepseek-v4-pro`, 2026-07-06) 给出 **REVISE / NOT READY**：SRN 只有在最小 pilot 胜过同 backbone 的 adversarial disentanglement baseline 后才可保留为 main contribution；ELOS 降为 supporting training principle；AMCN 仅为 conditional auxiliary。评审要求补查 domain-adversarial/MMD disentanglement、conditional motion–appearance、VAD meta-learning、prototype alignment 与 Self-Distilled MAE 系列，并增加 subtraction、ELOS-vs-ERM、random scene token、context path freezing 和 zero-shot/calibration track separation 等验证。

外部原始输出：`refine-logs/INDEPENDENT_REVIEW_RAW.md`。摘要：`refine-logs/INDEPENDENT_REVIEW_SUMMARY.md`。Reviewer 提到的具体论文名需另行核验，不能由本 traceability 条目视为已确认事实。

## Revision re-review gate

2026-07-12，通过 `llm-chat MCP` 调用 DeepSeek API（`deepseek-v4-pro`）对修订行动计划进行了 re-review，返回 **READY WITH RESTRICTIONS**。restricted bridge 仅限 frozen-feature audit + minimal SRN-vs-adversarial pilot，不做大规模训练，不做 backbone fine-tuning。启动前剩余阻塞项包括：冻结 SRN mathematical spec、完成 verified prior-work patch、冻结 baseline registry、冻结 strict zero-shot 与 target-normal calibration 的 data/protocol split，并由用户单独授权数据下载/GPU 使用。

Re-review 原始返回：`refine-logs/REVISION_REVIEW_RAW.md`。摘要：`refine-logs/REVISION_REVIEW_SUMMARY.md`。

## Pre-bridge freeze pass

2026-07-13 已生成四个 restricted bridge 前的冻结文件：

- `refine-logs/PRIOR_WORK_PATCH.md`：冻结 prior work 类别、当前已有覆盖、`TODO: verify` 项和高重叠时的降级策略。
- `refine-logs/SRN_MINIMAL_SPEC.md`：冻结 minimal SRN pilot 的数学定义、训练/测试信息许可、ELOS episode 和不实现范围。
- `refine-logs/BASELINE_REGISTRY.md`：冻结 required baselines、optional/later baselines、first-round inclusion 和 stop rules。
- `refine-logs/PROTOCOL_MANIFEST.md`：冻结 dataset tiers、首轮数据计划、splits/tracks、metrics 和阈值协议。

这些文件只关闭文档 gate，不授权数据下载、GPU 使用、训练或 `/experiment-bridge` 启动。

## 修订决策追踪

| Reviewer issue | 影响的 ideas | 修订决策 | 关闭证据 |
|---|---|---|---|
| SRN 接近 generic domain invariance/disentanglement | SRN, ELOS | SRN 保留为 conditional main candidate；ELOS 合并为 training principle | verified prior-work patch + equation-level novelty delta |
| selective suppression 可能删除有用 context | SRN, conditional mixture | 不再主张 full invariance；加入 context-retention guardrail；mixture 仅在失败诊断后启用 | scene probe + event retention + location-dependent subset |
| AMCN 与 conditional prediction 重叠 | AMCN | 仅作 backup/auxiliary，先查新 | 与 conditional/unconditional motion baselines 对比 |
| calibration 假设与 track leakage | rank calibration, temporal suppression | calibration 降为独立 evaluation/supporting track；temporal method 降为 baseline | strict-zero-shot 和 target-normal tables + fixed source threshold |
| contribution sprawl | ideas 4–11 | 4/6 conditional；5/8/10/11 baseline/protocol；9 discard | contribution statement 限制为一个 dominant mechanism |
| 无 pilot 且缺少非平凡 controls | SRN, ELOS, AMCN | 冻结 minimal SRN-vs-GRL pilot 与 stop rules；re-review 同意 restricted first round | `REVISION_ACTION_PLAN.md` Gate 1 + `REVISION_REVIEW_SUMMARY.md` |

Canonical action plan：`refine-logs/REVISION_ACTION_PLAN.md`。当前规划状态：**READY WITH RESTRICTIONS**。四个 freeze artifacts 已生成；执行仍保持 hold，直到用户单独授权任何数据下载、GPU 使用或 `/experiment-bridge` 启动。
