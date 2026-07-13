# Independent Review Bundle: Normal-Only General VAD

## Reviewer independence requirement

请由**未参与本项目生成过程的另一模型或独立会话**完成评审。Reviewer 不应阅读执行者的隐藏推理；只依据本 bundle 和其中列出的文件。请原样保存 reviewer 输出，不要由项目主执行者润色后冒充原始评审。

## Research boundary

- normal-only training；测试才可含异常。
- public/general VAD benchmarks；cross-scene 与 cross-dataset generalization 是主问题。
- frozen/lightweight backbone + small normality head，有限算力。
- 不包含工业数据、音视频多模态、weakly supervised abnormal training、fully-unsupervised mixed training、异常类别识别或大模型端到端训练。
- 主要评价不得只用单数据集 pooled frame AUROC；还需 macro-AUROC、AUPRC、低 FPR recall、false alarms/hour、固定源域阈值和跨域矩阵。

## Evidence status

- 当前只有文献与纸面方案；无 pilot、无训练结果。
- 2026 cross-dataset audit 已显示 frozen CLIP/DINOv2/ResNet/EfficientNet + kNN/Mahalanobis 在跨数据集条件下接近随机，因此“只做 audit”不是新贡献。
- 完整材料：
  - `idea-stage/IDEA_REPORT.md`
  - `refine-logs/FINAL_PROPOSAL.md`
  - `refine-logs/EXPERIMENT_PLAN.md`
  - `refine-logs/PRIOR_METHOD_DEFECT_TO_IDEA_MATRIX.md`

## Candidate ideas with prior-work notes

1. **SRN** — responds to frozen-feature scene leakage/cross-dataset collapse, HSC's known-scene awareness, and the context duality exposed by NWPU/EVAL. Design: subtract scene-predictable component and model residual normality, with a controlled context path.
2. **AMCN** — responds to absolute appearance novelty, perspective-dependent motion novelty and confounded reconstruction/prediction error. Design: model `p(motion | appearance/context)` on normal clips.
3. **ELOS** — responds to objectives that never simulate unseen cameras. Design: episodically hold out a normal scene; intended as SRN training principle, not standalone contribution.
4. **Scene-conditional/agnostic mixture** — responds to the conflict between HSC-like scene awareness and overly invariant representations. Design: gate shared prototypes and a tiny context adapter.
5. **Object-relation graph** — responds to appearance/background leakage but overlaps EVAL/tracklet methods. Design: relative interaction graph without absolute coordinates.
6. **Prototype transport** — responds to scene-bound MemAE/MNAD/HSC prototype identities. Design: align scene-specific normal prototypes into shared event prototypes.
7. **Source-free rank calibration** — responds to threshold/score-scale transfer failure in cross-dataset audits. Design: source-only tail/rank map, frozen for target.
8. **Temporal false-alarm suppression** — responds to framewise score spikes ignored by AUROC. Design: learn normal score persistence and report event/FA-hour metrics.
9. **Counterfactual retrieval** — responds to failed raw nearest-neighbour transfer. Design: retrieve in factorized event/motion space; currently archived due direct overlap/risk.
10. **Stress-test suite** — responds to frame-AUC and same-dataset protocol defects identified by Street Scene, EVAL, NWPU and Rashidi 2026. Protocol contribution only.
11. **Normal-only masked distillation** — responds to synthetic-anomaly dependence in Self-Distilled MAE. Strong overlap; likely only an efficiency baseline.

## Matrix summary

- Main contribution candidates: **SRN**, possibly **AMCN**.
- Supporting training principle: **ELOS**.
- Conditional auxiliary modules: gated context mixture, prototype transport, rank calibration, temporal reliability model.
- Baseline/protocol only: object graph, retrieval, stress-test suite, masked distillation.
- Highest novelty threats: generic domain-adversarial factorization, conditional prediction prior art, domain-generalization episodes, CVPR 2024 self-distilled MAE, and Rashidi 2026 cross-dataset audit.

## Proposed mainline

**SRN + ELOS**: freeze a video backbone; estimate a low-dimensional scene token; predict and subtract the scene component; learn normal prototypes/density on the event residual; train with held-out-scene episodes; retain a constrained context path for location-dependent anomalies.

## Required reviewer task

Act as a strict NeurIPS/ICML/CVPR reviewer. Do not reward module count, fashionable terminology or unverified novelty. For **each of the 11 ideas**, return:

1. strongest objection;
2. likely failure mode;
3. novelty risk and closest known family/paper;
4. missing baselines;
5. decisive ablations;
6. role recommendation: main contribution / auxiliary / baseline-protocol / abandon;
7. whether it is ready to proceed to `/experiment-bridge`.

Then provide:

- ranked top 2–3 ideas;
- an explicit verdict on **SRN + ELOS**: `PROCEED`, `REVISE`, or `ABANDON`;
- the minimum changes required before experiment implementation;
- any scope leakage or hidden supervision;
- whether the strict-zero-shot and target-normal-calibration tracks are cleanly separated;
- a final recommendation on entering `/experiment-bridge` now.

## Required output header

```text
Reviewer backend/provider:
Reviewer model:
Review date:
Independent from generating session: yes/no/uncertain
Files/bundle reviewed:
```

The output must be saved verbatim to `refine-logs/INDEPENDENT_REVIEW_RAW.md` before the main project report is updated.
