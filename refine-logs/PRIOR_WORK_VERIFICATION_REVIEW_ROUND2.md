# Prior Work Verification Review Round 2

**日期：** 2026-07-14  
**Reviewer backend：** `llm-chat MCP` calling DeepSeek API  
**Model：** `deepseek-v4-pro`  
**状态：** 成功完成。  
**注意：** Reviewer 输出是 opinion，不是一手证据；其未新增论文。

## 1. 脱敏 Bundle

发送内容包括：

- SRN Ground-Truth Definition；
- M1-M10 机制代码；
- Round 2 verified evidence summary；
- reviewer seed disposition；
- local conclusion：No verified VAD prior satisfies M2+M3+M4+M5+M6；
- local verdict：`NOVELTY PLAUSIBLE`；
- operational decision：`READY TO REQUEST RESTRICTED BRIDGE`。

发送内容不包括：

- API key、token、密码、SSH key、cookie；
- `.env` 或用户级环境配置；
- GitHub / DeepSeek 凭据；
- 数据集、视频、feature cache、权重、checkpoint；
- venv / Conda 环境；
- `.agents/skills`、`.aris` 内部内容；
- 与评审无关的服务器绝对路径或个人隐私信息。

## 2. Reviewer 原始输出

```text
作为严格的科研查新 reviewer，基于提供的脱敏 evidence bundle，我对 SRN Prior Work Verification Round 2 novelty gate 作出以下审查回答：

1. **Round 2 是否真正关闭了 domain-invariant/disentangled leads？**  
   在本次 evidence bundle 范围内，domain-invariant/disentangled 相关的种子论文（如 DIRT、SDG-Net、Domain-Invariant Feature Learning for VAD 等）均未解析为可验证的 primary-source VAD 文献，被分类为 likely hallucinated 或 identity mismatch。截至目前，并无任何经过主源验证的这类工作被证实存在且覆盖 M3–M6。因此，基于现有证据，这些 leads 实质上已被关闭，但需注意“likely hallucinated”并非绝对证伪，若未来出现可验证的主源仍可能重新打开。

2. **是否发现 M3-M6 direct coverage？**  
   否。审查明确结论：**No verified VAD prior satisfies M2+M3+M4+M5+M6**。所有被查验的 VAD 方法（包括 background-agnostic AED、STG-NF、MoCoDAD、DA-Flow、Meta Prototype Network、Few-shot scene-adaptive AD、zxVAD、HSC、Action Hints 等）均缺少 M4（预测场景/域成分的显式模块）、M5（显式减法/残差化 z−u_hat）和/或 M6（受控上下文保留）中的关键组合，未形成对 SRN 核心机制链的直接覆盖。

3. **哪些 seed disposition 可能仍过度乐观？**  
   以下种子 disposition 存在过度乐观风险：  
   - **DIRT、SDG-Net、Domain-Invariant Feature Learning for VAD** 等被标记为 likely hallucinated/nonexistent，但缺乏穷尽性排除证据；若它们真实存在并恰好满足 M3–M6，将直接构成威胁。  
   - **Meta-AD** 被解析为 identity mismatch 到真实 MPN/few-shot 家族，但若原意指代另一独立工作，则该 disposition 可能误判。  
   - **Learning Conditional Motion Priors** 被等同为 MoCoDAD，亦可能遗漏独立发表物。  
   这些 disposition 应视为暂时性，需保留“unverified lead”标记直至绝对确认。

4. **evidence classification 是否仍过度乐观？**  
   整体分类严谨。所列各项均基于具体缺失模块（M4/M5/M6）被归为威胁有限的 C/E 类或 D 机制邻居，未见有明显误判。但需警惕：skeleton-based 方法（如 MoCoDAD、DA-Flow）虽因领域归约而不显式拥有 scene token，但其内部可能隐式实现某种“姿态减背景”的残差，若被重新解读为等效操作，则可能动播分类。当前分类在显式证据层面无过度乐观。

5. **non-VAD residualization 是否足以把 SRN 降为应用创新？**  
   不足以。现有非 VAD 残差工作（如 InCTRL）的残差定义为 query–normal prompt 差异，并非从 learnable scene token 预测场景可预测成分再作减法；亦缺乏 M6 受控上下文保留。ADShift/GNL、Invariant AD 等方法强调不变性但无显式减法模块。因此，这些非 VAD 工作未实现 M3+M4+M5+M6 组合，尚不能将 SRN 降为单纯的领域迁移（应用创新），SRN 在 VAD 内的方法组装仍具新颖性。

6. **ELOS 是否已有明确 prior？**  
   是。ELOS 设定（held-out whole source scene 仅用于泛化检验，不做 target adaptation）已在几项工作中明确出现，例如 **Meta Prototype Network**（arXiv:2104.06689）和 **Few-shot Scene-adaptive AD**（arXiv:2007.07843），虽然它们属于 few-shot 而非 zero-shot，但协议层面已使用 unseen source scenes 评估泛化。因此 ELOS 作为协议本身非新颖，SRN 的协议创新不被认定为方法 novelty。

7. **当前 novelty verdict：**  
   **NOVELTY PLAUSIBLE**。在已核实的 VAD 前案中，没有方案同时实现 frozen feature、normal-only、显式 scene token、scene-predictable 成分预测、残差减法与受控上下文保留的组合。ELOS prior 不改变方法层 novelty 判断。

8. **operational decision：**  
   **go**（推进至 restricted bridge 请求）。当前证据足以支撑 novelty plausible，但仍需保留若干 unverified leads 的监控，并在 restricted bridge 阶段要求作者显式讨论这些 leads 并给出差异化分析。

9. **未提出新论文**，无新增 unverified lead。

综上，Round 2 审查维持 SRN 方法核心的新颖性初步成立，建议在受控条件下继续推进。
```

## 3. Codex 对 Reviewer 输出的校验

| Reviewer point | 校验状态 | Codex handling |
|---|---|---|
| Round 2 closes domain-invariant/disentangled leads | 接受，但不是绝对证伪 | 在 `REVIEWER_LEAD_DISPOSITION.md` 保留 unresolved / likely hallucinated 状态；后续论文写作前可 supplemental search |
| No M3-M6 direct coverage | 与 Round 2 evidence table 一致 | 支持 `NOVELTY PLAUSIBLE` |
| Seed disposition may be over-optimistic | 合理 | 不删除 unverified labels；FG-Diff/Ada-VAD 保持 unresolved |
| Skeleton methods could be interpreted as implicit scene removal | 合理但不等于 SRN | 保持 skeleton as strong baseline / competing family, not direct coverage |
| Non-VAD residualization insufficient to downgrade SRN to application-only | 与 evidence table 一致 | SRN may claim VAD-specific mechanism, not generic residual novelty |
| ELOS has prior | 与 evidence table 一致 | ELOS remains training/validation principle only |
| Operational go | Translate to project vocabulary: `READY TO REQUEST RESTRICTED BRIDGE` | Execution remains `HOLD`; no automatic bridge |

## 4. Final Integrated Verdict

**Novelty verdict：** `NOVELTY PLAUSIBLE`  
**Operational decision：** `READY TO REQUEST RESTRICTED BRIDGE`

This does not authorize data download, GPU use, feature extraction, training, or `/experiment-bridge`. It only closes the prior-work novelty gate enough to ask the user for a restricted bridge decision.
