# Prior Work Verification Cross-Model Review 记录

**日期：** 2026-07-14  
**计划 reviewer：** `llm-chat MCP` calling DeepSeek API / `deepseek-v4-pro`  
**状态：** 未执行成功。

## 1. 计划审查内容

原计划在第一版 evidence bundle 完成后，请 DeepSeek 作为 cross-model reviewer 审查：

- 是否漏掉关键方法族；
- 分类是否过度乐观；
- 是否把任务相似误判为机制覆盖；
- 是否把机制相似误判为 novelty collapse；
- 当前 preliminary verdict 是否证据充分。

## 2. 实际结果

调用 `llm-chat MCP` 时被安全策略拒绝。原因摘要：

- 将未公开 workspace research notes 和综合性结论发送到外部 LLM 服务存在数据外传风险；
- 当前不能通过 workaround、间接执行或其他路径绕过该限制；
- 若要继续外部 cross-model review，需要用户在知情后明确批准。

本文件不包含 API key、环境变量、私密配置或未授权外发内容。

## 3. 对本轮查新的影响

- `refine-logs/PRIOR_WORK_VERIFICATION_ROUND1.md`、`refine-logs/PRIOR_WORK_EVIDENCE_TABLE.md`、`refine-logs/PRIOR_WORK_TODO_RESOLUTION.md`、`refine-logs/SRN_NOVELTY_RISK_REGISTER.md` 和 `refine-logs/PRIOR_WORK_PATCH_VERIFIED_DRAFT.md` 已作为本地第一轮 evidence bundle 生成。
- 本轮 preliminary verdict 仍是本地判断，尚未获得 DeepSeek cross-model reviewer 背书。
- 后续若用户明确批准，可重新发送经过脱敏/压缩的 evidence summary 给 `llm-chat MCP`，并将 reviewer opinion 单独保存到本文件或新文件中。

## 4. 当前建议

在未获得额外批准前，不再尝试外部 reviewer。下一步优先进行本地第二轮查新：

- zxVAD references / cited-by；
- Action Hints references 中的 MoCoDAD、STG-NF、DA-Flow、Ada-VAD；
- non-VAD domain-invariant one-class learning；
- residualization / predictable component removal / nuisance prediction；
- threshold transfer、EVT、conformal anomaly detection 与 FA/hour operating-point 文献。
