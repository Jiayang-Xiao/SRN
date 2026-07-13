---
reviewer_backend: DeepSeek API via llm-chat MCP
model: deepseek-v4-pro
date: 2026-07-12
input: 原始 REVISE / NOT READY 评审与修订行动计划的压缩摘要
note: 外部 re-review 返回内容的中文转写；未保存 API key 或私密环境变量内容
---

## 1. Verdict

**READY WITH RESTRICTIONS**

## 2. restricted bridge 前仍需完成的阻塞项

- 必须冻结 SRN mathematical specification，包括精确的 capacity-constraint mechanism 和 context-retention diagnostics，并清楚区分其与标准 domain-adversarial（GRL/MMD）nuisance removal 的差异。
- 必须完整执行 prior-work verification patch，并映射到所有必需 baseline 类别：one-class normal-only VAD、scene-invariant/disentangled VAD、cross-dataset VAD、domain generalization、adversarial/MMD methods、conditional motion prediction、object-centric/memory/prototype VAD、meta-learning、masked distillation、low-FPR/FA-hour evaluation。
- 必须冻结 baseline registry，显式包含 raw kNN/Mahalanobis、mean/background subtraction、adversarial GRL/MMD、ERM/ELOS、conditional prediction、calibration controls、low-FPR 与 FA/hour metrics。
- 必须冻结 data protocol，严格分离 strict zero-shot 和 target-normal calibration 两条 track，保证不使用异常训练标签，并要求数据下载和 GPU 使用都获得用户单独授权。

## 3. 是否同意首轮只做 frozen-feature audit + minimal SRN pilot

同意。

## 4. 一句话理由

修订方案正确推迟了大规模训练，分离了此前混在一起的 claim，要求所有关键 baseline，并把第一步实验限制为低资源 pilot，用来直接检验受约束的 SRN 假设是否优于 adversarial baselines，因此可作为审慎的 evidence gate。
