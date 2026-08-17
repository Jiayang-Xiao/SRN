# 实验追踪器

| ID | Claim / task | 状态 | 前置条件 | 产出 |
|---|---|---|---|---|
| R0 | 独立评审结论与 revision actions | complete | DeepSeek raw review + local traceability | review raw/summary + `REVISION_ACTION_PLAN.md` |
| R1 | prior-work patch 与 Round 2 novelty gate | complete for bridge gate | verified mechanism coverage；remaining optional leads non-blocking | `PRIOR_WORK_VERIFICATION_ROUND2.md` |
| R2 | SRN 数学定义与边界 | freeze complete | low-capacity token/predictor、context guardrail | `SRN_MINIMAL_SPEC.md` |
| R3 | baseline registry | freeze complete | shared backbone/head/budget | `BASELINE_REGISTRY.md` |
| R4 | zero-shot/calibration protocol | freeze complete | data-use、split、threshold rules | `PROTOCOL_MANIFEST.md` |
| RB0 | restricted bridge authorization | complete | user authorization 2026-08-03 | 状态更新为 `AUTHORIZED / IN PROGRESS` |
| RB1 | local asset/environment audit | complete | read-only scan；no download/GPU | `RESTRICTED_BRIDGE_AUDIT.md` |
| RB2 | unified frozen-feature code skeleton | complete | frozen specification and registry | `src/restricted_bridge/` + configs + runner |
| RB3 | CPU synthetic dry-run | complete, non-scientific | 2 seeds × 11 entries | ignored `runs/restricted_bridge_synthetic_dry_run/`; reproducibility true |
| RB4 | local code review and tests | complete | no secondary reviewer available | `EXPERIMENT_CODE_REVIEW.md`; 9 unittest pass |
| RB5 | formal run plan | complete | asset audit + code dry-run | `RESTRICTED_BRIDGE_RUN_PLAN.md` |
| G0 | Tier A data/cache protocol preflight | complete | official Ped2/Avenue/DINOv2 assets, checksums, split/fps/label audits | `DATA_AND_FEATURE_PROVENANCE.md` + five cache sidecars |
| E1 | Ped2/Avenue frozen-feature audit | complete, negative transfer finding | 35,212-frame shared DINOv2 catalog | raw scorers + within/cross-dataset tables |
| E2 | SRN vs mean/adversarial mechanism pilot | complete, mechanism falsified | joint two-seen-domain cache; 3 learned seeds | main/ablation table + independent scene probe |
| E3 | ShanghaiTech whole-scene falsification | externally blocked | official links inaccessible; unverified mirror rejected | no whole-scene ELOS claim |
| E4 | low-FPR/FA-hour claim | complete for bounded pilots | chronological/gap-aware alarm metric; official FPS | source-threshold and calibrated tracks |
| E5 | Tier B scale-up | stopped | E2 STOP verdict; no scientific justification for scale-up | none |

截至 2026-08-17，Ped2/Avenue 官方数据、统一 DINOv2 frozen features、within/cross-dataset
baselines、joint seen-domain SRN/ablation matrix、独立 integrity review、自动结果分析与
negative-result paper draft 均已完成。Synthetic outputs 仍不属于科研证据。ShanghaiTech
官方资源访问失败，因此 genuine whole-scene ELOS 未测试。当前结论为 `STOP` tested SRN
mechanism claim；不继续 Tier B scale-up。
