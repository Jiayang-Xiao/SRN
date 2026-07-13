# 实验追踪器

| ID | Claim | 状态 | 前置条件 | 产出 |
|---|---|---|---|---|
| R0 | 独立评审结论已纳入计划 | complete | DeepSeek API raw review | `INDEPENDENT_REVIEW_RAW.md` + summary |
| R0.5 | reviewer criticism 已转为 revision actions | complete | raw + summary + local traceability | `REVISION_ACTION_PLAN.md` |
| R0.7 | revised plan 已完成 `llm-chat` re-review | complete | `llm-chat MCP` + DeepSeek `deepseek-v4-pro` | `REVISION_REVIEW_RAW.md` + summary；verdict READY WITH RESTRICTIONS |
| R0.8 | `IDEA_REPORT.md` 已同步最新状态 | complete | original review + revision re-review + freeze pass | `IDEA_REPORT.md` 第 7/8 节 + `CURRENT_RESEARCH_STATE.md` |
| R1 | prior-work patch 结构已冻结 | freeze file complete；文献仍有 TODO verify | PW01–PW12 类别与已有覆盖梳理 | `PRIOR_WORK_PATCH.md` |
| R2 | SRN novelty 与机制定义可审计 | freeze file complete | equations、loss、context guardrail、complexity budget | `SRN_MINIMAL_SPEC.md` |
| R3 | baseline registry 冻结 | complete | shared backbone/head/budget rules | `BASELINE_REGISTRY.md` |
| R4 | zero-shot/calibration tracks 分离 | complete | data-use and threshold rules | `PROTOCOL_MANIFEST.md` |
| R5 | minimal pilot specification 冻结 | complete at document level | success/falsification/stop thresholds | `SRN_MINIMAL_SPEC.md` + `BASELINE_REGISTRY.md` + `PROTOCOL_MANIFEST.md` |
| R6 | bridge interpretation 已决定 | Gate 1 后仅允许 restricted bridge | DeepSeek re-review | 首轮限制为 frozen-feature audit + minimal SRN-vs-adversarial pilot |
| G0 | 协议与数据可复现 | document manifest frozen；数据未下载 | 数据许可、split、预处理冻结 | `PROTOCOL_MANIFEST.md`；后续仍需用户授权 |
| E1 | frozen-feature 跨域崩溃可复现 | blocked by R1–R6/G0 | 三数据集可用 | cross matrix |
| E2 | SRN 改善跨场景迁移 | blocked by E1 | adversarial baseline 可信 | minimal pilot metrics |
| E3 | SRN 机制必要 | blocked by E2 | 正向信号 | ablations |
| E4 | 改善部署指标 | blocked by E2 | 阈值协议 | low-FPR/FA-hour |
| E5 | 扩展到复杂数据集 | blocked by E2 | 资源与许可 | scale-up |

本 tracker 仅为计划；截至 2026-07-13 未运行任何实验。原 DeepSeek independent review verdict 为 **REVISE / NOT READY**；2026-07-12 `llm-chat MCP` re-review 将修订后计划升级为 **READY WITH RESTRICTIONS**。2026-07-13 已生成四个 pre-bridge freeze 文件：`PRIOR_WORK_PATCH.md`、`SRN_MINIMAL_SPEC.md`、`BASELINE_REGISTRY.md`、`PROTOCOL_MANIFEST.md`，并已同步 `idea-stage/IDEA_REPORT.md` 与 `CURRENT_RESEARCH_STATE.md`。restricted bridge 尚未启动；当前不下载数据、不训练、不使用 GPU。
