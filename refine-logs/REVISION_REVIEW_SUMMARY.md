# 修订方案 Re-review 摘要

- **Reviewer backend：** 通过 `llm-chat MCP` 调用 DeepSeek API
- **模型：** `deepseek-v4-pro`
- **日期：** 2026-07-12
- **来源：** `refine-logs/REVISION_REVIEW_RAW.md`
- **状态：** 对修订后行动计划的外部 re-review；未运行任何实验

## 结论

DeepSeek 将修订后的规划状态升级为 **READY WITH RESTRICTIONS**。

这不等于可以启动广泛实验。Reviewer 明确限制首轮工作只能包括：

- frozen-feature audit；
- minimal SRN pilot；
- 与 adversarial baselines 的直接比较；
- 不做大规模训练；
- 不做 end-to-end backbone fine-tuning。

## restricted bridge 启动前仍需关闭的阻塞项

1. 冻结 SRN mathematical specification，包括 capacity constraint、context-retention diagnostics，并明确区别于 GRL/MMD nuisance removal。
2. 完成 prior-work verification，覆盖 normal-only VAD、scene-invariant/disentangled VAD、cross-dataset VAD、domain generalization、conditional motion prediction、object-centric/memory/prototype VAD、meta-learning、masked distillation、calibration 和 low-FPR/FA-hour evaluation。
3. 冻结 baseline registry：raw kNN/Mahalanobis、mean/background subtraction、adversarial GRL/MMD、ERM/ELOS、conditional prediction、calibration controls、low-FPR/FA-hour metrics。
4. 冻结 data protocol：strict zero-shot 与 target-normal calibration 分离；保证不使用异常训练标签；数据下载和 GPU 使用需要用户单独授权。

## 解释

本次 re-review 将之前的 reviewer/workflow 冲突解释为：**只有在文档 gate 冻结之后，才允许 restricted bridge**。它同意首个实验步骤在获得授权后只能是 frozen-feature audit + minimal SRN-vs-adversarial pilot。
