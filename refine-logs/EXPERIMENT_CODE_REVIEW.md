# Restricted Bridge Experiment Code Review

**日期：** 2026-08-03
**审查方式：** `[local-only]`；当前会话无可用 secondary Codex reviewer delegation。
**结论：** CPU dry-run 可接受；正式数据运行仍受 data/cache preflight 阻塞。

## Blocking issues found and fixed

1. Gaussian scorer 初版二次型只会使用 precision diagonal；已改为完整 `x^T precision x`，并添加非对角协方差测试。
2. `ELOS without SRN` 初版与 raw representation 等价且没有 episodic 输出；已增加 whole-scene support/held-out scorer stability diagnostic。

## Checklist

- SRN forward 保持 `z -> c -> u_hat -> r=P(z-u_hat)`；context 为 `q=a(c)`，输出 `concat(r, lambda*q)`。
- `g/h/P/a` 均为 linear low-capacity modules；scene token 维度由 config 限制为小于 feature dimension。
- 所有方法使用同一 cache、split、seed、scorer registry、threshold/evaluation path。
- labels 只在 test metrics 使用；非 test 异常样本由 loader 直接拒绝。
- ELOS held-out scene 不参与该 episode 的 gradient update，只计算 no-grad validation diagnostic。
- source threshold 只由 source normal validation scores 确定；target-normal calibration 使用独立 split 和独立结果字段。
- checkpoint、JSON、CSV 和 log 均已在 end-to-end test 与 full dry-run 验证。
- evaluation 输出 per-scene/per-video AUROC、scene variance、worst scene 与 per-scene threshold recall，避免 pooled AUC 掩盖失败。
- synthetic metrics 明确标记 `synthetic_dry_run_only`，不能进入科研结果。

## Non-blocking limitations before formal run

- 当前没有 Tier A cache conversion/extraction script；因数据和 feature extraction 均未授权，未虚构数据适配器。
- Ped2/Avenue 不足以单独验证 whole-scene/ELOS claim；需要 gated ShanghaiTech stage。
- strict unseen scene mean subtraction 使用 source global fallback；target mean 只能属于 calibration track。
- background subtraction、location-dependent recall、FA/hour 均依赖真实 cache 的可审计元数据，缺失时必须报告 unavailable。
- 当前 `residual_variance_ratio` 只是工程 smoke proxy，不是 event/motion retention 科学证据；正式 cache 若无 motion/event metadata，相关 probe 必须标记 unavailable。
