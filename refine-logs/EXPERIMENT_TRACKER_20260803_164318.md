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
| G0 | Tier A data/cache protocol preflight | blocked: assets absent | legal data copies、checksums、official split、fps、labels、backbone cache | future immutable cache manifest |
| E1 | Ped2/Avenue frozen-feature audit | not started | G0 + separate data/feature authorization | raw/scorer/threshold tables |
| E2 | SRN vs mean/adversarial mechanism pilot | not started | E1 confirms meaningful collapse and source-domain labels | minimal mechanism table |
| E3 | ShanghaiTech whole-scene falsification | gated, not authorized | positive/inconclusive-safe E2 + separate authorization | LOSO whole-scene table |
| E4 | low-FPR/FA-hour claim | not started | trustworthy fps/alarm definition + E2 | reliability table |
| E5 | Tier B scale-up | out of scope | positive E2/E3 + separate authorization | none |

截至 2026-08-03，restricted bridge 的 audit、代码骨架、CPU synthetic dry-run 和正式运行计划已完成。未下载数据，未使用 GPU，未提取 Tier A features，未启动正式训练或正式 evaluation。Synthetic outputs 不是科研证据。当前正式运行阻塞于 Ped2/Avenue 合法数据与统一 frozen feature cache；ShanghaiTech 和 Tier B 均未获本轮实际运行授权。
