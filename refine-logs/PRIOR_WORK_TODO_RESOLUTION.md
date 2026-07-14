# PRIOR_WORK_PATCH TODO Resolution 第一轮

**检索日期：** 2026-07-14  
**输入文件：** `refine-logs/PRIOR_WORK_PATCH.md`  
**输出性质：** 第一轮核验记录；不替换冻结文件。

## TODO 清单与核验结果

| ID | 原 TODO | 核验结果 | Supporting papers | Resolved | Confidence | Remaining action |
|---|---|---|---|---|---|---|
| T01 | `DIRT` / `SDG-net` / domain-adversarial video feature decomposition | 精确检索未找到与 VAD + scene/domain residualization 直接对应的一手来源；可能是简称误写或 reviewer hallucination。domain-adversarial baseline 仍应保留为实验 baseline。 | zxVAD；Few-shot Scene-adaptive AD；Action Hints 作为 DG/problem-setting 近邻 | 否 | 中 | 第二轮从 zxVAD / cross-domain VAD references 追踪 domain-adversarial 或 Ada-VAD family。 |
| T02 | “Domain-Invariant Feature Learning for Video Anomaly Detection”, MVA 2023 | 未找到可核验一手来源。不能作为正式 citation。 | 无直接 supporting paper | 否 | 中 | 继续以 `"domain-invariant" "video anomaly detection"`、MVA proceedings、作者链检索。 |
| T03 | “Disentangled Representations for Domain-General Video Anomaly Detection”, CVPRW 2024 | 未找到可核验一手来源。不能作为正式 citation。 | 无直接 supporting paper | 否 | 中 | 下一轮查 CVPRW/VAND workshop proceedings 与 “domain-general VAD disentangled” 变体。 |
| T04 | MAC / Motion-Appearance Co-Memory, AAAI 2023 | 未找到 VAD 论文；检索到 Motion-Appearance Co-Memory Networks 但任务是 video QA，不应作为 VAD prior。appearance-motion VAD family 可由 MAMC/AMSRC/AMM 替代。 | MAMC；AMSRC；Appearance Blur + Motion-guided Memory | 部分 | 中高 | 若后续转向 AMCN，再核验 motion-appearance memory / correspondence 全链。 |
| T05 | “Learning Conditional Motion Priors for VAD”, ICCV 2023 | 未找到可核验一手来源。conditional / motion prior 风险由 skeleton diffusion、appearance-motion consistency、motion-guided memory 支撑，但不是该标题。 | MAMC；AMSRC；Action Hints related work 中的 MoCoDAD | 部分 | 中 | 下一轮核验 MoCoDAD / multimodal motion-conditioned diffusion 原文。 |
| T06 | MocoDAD / motion-appearance disentanglement | 在 Action Hints related work 中确认 MoCoDAD 是 skeleton-based VAD family 的相关方法；本轮未核验 MoCoDAD 原文。 | Action Hints related work | 否 | 中 | 第二轮直接核验 MoCoDAD 原文，判断其 conditional motion prior 是否威胁 AMCN。 |
| T07 | “Few-Shot Scene-Adaptive Anomaly Detection”, ICLR 2022 | 已核验到 Lu et al. *Few-shot Scene-adaptive Anomaly Detection*，ECCV 2020 spotlight / arXiv 2007.07843；venue/year 与 TODO 不一致。它使用 unseen scene + few target frames + meta-learning，覆盖 scene-adaptive setting，但不是 strict zero-shot SRN。 | Lu et al. 2020 | 是 | 高 | 在 related work 中引用为 scene-adaptive / target-normal adaptation 风险；不要把它当 SRN direct coverage。 |
| T08 | Meta-AD, TNNLS 2023 | 未找到与 VAD scene adaptation 直接对应的一手来源。 | 无直接 supporting paper | 否 | 中 | 下一轮用 `"meta anomaly detection" "video anomaly"`、TNNLS、作者链继续查。 |
| T09 | DeepCrowd / scene-gated normality head | 未找到可核验一手来源。crowd / scene gated normality 仍是概念风险，但不能引用。 | HSC、EVAL、NWPU 作为 scene-aware/context family | 否 | 中 | 第二轮查 crowd anomaly detection + scene-conditioned/gated model。 |
| T10 | prototype alignment for unsupervised domain adaptation | VAD-specific prototype alignment direct source 未在本轮核验到；memory/prototype VAD family 已由 kNN/Mahalanobis audit、motion memory、MAMC 支撑。 | Rashidi 2026；MAMC；Appearance Blur + Motion-guided Memory | 部分 | 中 | 若 SRN 使用 prototype transport，再补 domain adaptation / OT prototype alignment 文献。 |

## 对冻结文件的建议更新方向

本轮不直接修改 `PRIOR_WORK_PATCH.md`。后续若用户授权合并，可考虑：

- 把 T07 正式改为 Lu et al. ECCV 2020，而不是 ICLR 2022；
- 删除或降权未能核验的具体标题，改写为 search seed；
- 将 zxVAD、Action Hints、Appearance Blur + Motion-guided Memory 加入 strong partial overlap；
- 将 HSC/EVAL/NWPU 用于说明 context retention 的必要性，而不是 direct novelty threat；
- 明确 SRN 不能 claim zero-shot/cross-domain VAD setting novelty。

## Cross-Model Reviewer 后新增 Round 2 TODO

**来源：** 2026-07-14 授权 `llm-chat MCP` / DeepSeek reviewer。  
**注意：** 以下条目均为 reviewer opinion 或 search lead，尚未核验一手来源；不得直接进入正式 evidence table、bibliography 或冻结文件。

| ID | 新增 TODO | reviewer concern | 当前处理 | Priority |
|---|---|---|---|---|
| R2-T01 | 继续核验 domain-invariant / disentangled VAD 是否存在 direct source | reviewer 认为这可能直接威胁 `scene token -> residual` 机制 | 用 primary source 搜索，不引用未核验标题 | 最高 |
| R2-T02 | 搜索 scene residualization / scene component subtraction / predictable component removal | reviewer 认为只要已有 `scene-predictable component -> residual normality`，SRN novelty 会显著受损 | 扩展到 VAD、one-class AD、OOD、industrial AD | 最高 |
| R2-T03 | 核验 Meta-AD / episodic VAD / few-shot VAD | reviewer 将 ELOS 风险上调；但其部分表述误读 SRN 为 few-shot/relation-network method | 只核验其是否覆盖 ELOS / held-out scene normality learning，不把 SRN改写成 few-shot task | 高 |
| R2-T04 | 核验 MoCoDAD、STG-NF、DA-Flow、FG-Diff、Ada-VAD | reviewer 和 Action Hints related work 均指向 skeleton / diffusion / domain-adaptive VAD family | 从 Action Hints、zxVAD references/cited-by 追踪 | 高 |
| R2-T05 | 核验 graph / ST-GCN / HRN / relation-network VAD | reviewer 误读 SRN 为 relation network，但 object/relation family 仍可能影响 baseline narrative | 作为 object-centric / relation baseline 查新，不作为 SRN direct threat unless mechanism overlaps | 中 |
| R2-T06 | 核验 threshold transfer / EVT / conformal / FA/hour operating point | reviewer 认为 protocol novelty 不能作为主贡献 | 继续保持 calibration/evaluation track，不作主方法 claim | 中 |

## Reviewer 后的临时状态调整

第一轮本地 verdict 仍记录为 `NOVELTY PLAUSIBLE`，但经 DeepSeek reviewer 审查后，应在内部决策中临时降为：

**`NOVELTY PLAUSIBLE but externally contested; treat as NOVELTY AT RISK until Round 2 closes domain-invariant/disentangled and episodic VAD leads`.**

该状态不是最终 novelty collapse，也不是正式改写冻结文件；它只是 Round 2 查新优先级和 stop/go gate 的保守输入。
