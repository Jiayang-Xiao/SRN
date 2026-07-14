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

## Authorized Cross-Model Review

**调用日期：** 2026-07-14  
**Reviewer backend：** `llm-chat MCP` calling DeepSeek API  
**Model：** `deepseek-v4-pro`  
**调用状态：** 成功。由于第一次 reviewer 输出在第 3 节中途截断，随后发出一次 continuation 请求补全第 3-8 节。

### 发送内容范围

本次发送的是脱敏后的 reviewer bundle，包含：

- 研究方向：normal-only VAD on general/public VAD benchmarks；
- SRN 最小机制链：`z -> c -> u_hat -> r = z - u_hat -> q -> normality`；
- ELOS / held-out scene / fixed source-threshold / low-FPR / FA/hour 边界；
- 13 篇第一轮 evidence table 的论文、任务、机制和 overlap 分类摘要；
- 未核验 reviewer/search seeds；
- 第一轮本地 verdict：`NOVELTY PLAUSIBLE`；
- 请求 reviewer 审查 direct coverage、分类是否过度乐观、遗漏方法族、Round 2 查新方向和 go/revise/stop 建议。

### 脱敏说明

发送内容不包含：

- API key、access token、密码、SSH private key、cookie；
- `.env`、用户级环境配置、GitHub/DeepSeek 凭据；
- 数据集原始文件、视频/音频、feature cache、权重、checkpoint；
- venv / Conda 环境内容；
- 与评审无关的服务器地址、用户名或绝对路径；
- `.agents/skills` 或 `.aris` 内部内容。

### Reviewer 原始输出

#### Part 1

```text
## 1. Verdict

**NOVELTY AT RISK**

*Rationale.*  
First-round evidence tables showed **no A-class direct coverage** (i.e. identical “scene-residual + frozen features + episodic leave-one-scene-out with fixed-source threshold” pipeline), but this conclusion is fragile for three reasons.  
- Multiple **unverified search seeds** (DIRT, “Domain-Invariant Feature Learning for VAD”, “Disentangled Representations for Domain-General VAD”, MoCoDAD, etc.) promise explicit *domain/scene-invariant* or *disentangled* representations for video anomaly detection. If any of them performs feature decomposition into scene- and event-related components and then builds a normality model on the residual, the core mechanism of SRN would be **partially pre-empted**.  
- Several **strong partial overlaps** (P02 HSC, P03 zxVAD, P05 Action Hints, P06 Lyu et al.) have already adopted *scene-aware contrast*, *foreground/background separation*, *skeleton-based scene removal*, or *cross-dataset zero-shot training* - the conceptual distance to a residual scene-removal strategy is small, and the combination of these techniques could be interpreted as an obvious next step.  
- The **evaluation protocol** (ELOS, fixed source-threshold, FA/hour, worst-target reliability) is a measurement discipline, not a model contribution. The present report acknowledges this, but the risk remains that the project could inadvertently claim that *novelty lies in the protocol*, which would be incorrect if any prior work already used leave-one-scene-out or reported per-scene FA rates (as done in P01 and probably in other domain-generalization audits).  

Therefore, while the *exact* SRN formulation (frozen representation -> low-capacity scene token -> residual -> controlled context path -> density/kNN) may not yet be verbatim published, **the margin between “plausible” and “collapsed” is thin**. The actual novelty depends on whether the unverified seeds already describe a functionally equivalent method. A “NOVELTY PLAUSIBLE” verdict at this stage would be premature.

---

## 2. Strongest Novelty Threats

1. **Unverified “Domain-Invariant Feature Learning for VAD” (MVA 2023 / CVPRW 2024).**  
   If this work learns a representation that is explicitly invariant to scene/domain via adversarial training or decomposition, then it likely already isolates the “scene-residual” event representation. The remaining step - building a normality model on it - would be a trivial extension.  
   *Requires primary-source verification.*

2. **Action Hints (P05, Tang et al. 2025).**  
   By using *skeleton* as representation, this work implements an extreme form of scene-removal (no background/appearance). Although it is modality-specific, it achieves zero-shot cross-scene generalization on 100+ unseen scenes, directly targeting the same deployment goal as SRN. The novelty of SRN’s “soft” residual over frozen video features may appear incremental if the community already accepts that scene suppression is the key to generalization.

3. **Appearance-motion disentanglement lines (P07, P08, and unverified “Disentangled Representations for Domain-General VAD”).**  
   Several two-stream or memory-augmented methods suppress scene-specific appearance via semantic alignment. If any of them explicitly *subtracts* a scene-predicted component from the feature space, the mechanism becomes a direct antecedent.

4. **Domain-general one-class / out-of-distribution learning with feature decomposition.**  
   Outside the VAD literature (e.g., in medical imaging or industrial inspection), “background-residual” or “context-residual” strategies have been used for one-class anomaly detection. If such a method was already applied to videos, SRN’s claimed contribution could be considered a domain transfer rather than a new model.

---

## 3. Suspected Missing Papers / Methods / Authors / Keywords

*All items below require primary-source verification before they can be treated as established prior art.*

- **Domain-invariant / disentangled VAD:**  
  “Domain-Invariant Feature Learning for Video Anomaly Detection” (MVA 2023 or similar venue)  
  “Disentangled Representations for Domain-General Video Anomaly Detection” (CVPRW 2024, as flagged)  
  “Learning Scene-Invariant Normalcy for Video Anomaly Detection”  
  “Deep Scene Decomposition for Unsupervised Anomaly Detection in Surveillance Videos”

- **Adversarial / transformation-based scene suppression:**  
  DIRT (Domain-Invariant Residual Transformation, if applicable to videos)  
  SDG-Net (if it uses subtractive scene modeling)  
  DeepCrowd / scene-gated normality head (unverified, from reviewer seeds)  
  MocoDAD (MoCo + domain adversarial) - mentioned only indirectly.

- **Meta-learning and episodic protocols for VAD:**  
  Meta-AD (TNNLS 2023, as flagged) - could already employ leave-one-scene-out episodes.  
  “Few-Shot Anomaly Detection via Episodic Training” -
```

#### Part 2

```text
（续上文）  
“Few-Shot Anomaly Detection via Episodic Training” (likely ICCV 2021, primary-source verification required) - explicitly builds few-shot tasks from normal-only videos; this is a direct precursor to any few-shot VAD claim. If SRN positions itself as a few-shot VAD method, this work must be discussed and ideally compared.  
**Episodic training for anomaly detection in images** is also represented by “Few-Shot Anomaly Detection via Hierarchical Feature Matching” (AAAI 2022, primary-source verification), which, although targeting industrial images, demonstrates the meta-learning episode paradigm that can be transferred to videos. A missing citation chain exists to “Meta-Learning for Semi-Supervised Few-Shot Video Anomaly Detection” (arXiv 2023, primary-source verification) that explicitly merges meta-learning and VAD.  
Beyond episodic training, **graph-based scene-relation modeling** is another absent thread: “ST-GCN for Video Anomaly Detection with Spatial-Temporal Relation Reasoning” (T-CSVT 2022, primary-source verification) and “HRN: Hierarchical Relation Network for Video Anomaly Detection” (MM 2022, primary-source verification) both exploit object-level or region-level relations, similar to SRN’s relation network. If SRN claims novelty in scene-relation, these must be contrasted.  
**Generative few-shot VAD** also lacks coverage; “Learning Memory-Guided Normality for Anomaly Detection” (CVPR 2020) uses memory but not episodes; however, “Memory-Augmented Meta-Learning for Anomaly Detection in Videos” (WACV 2023, primary-source verification) combines both.  
Overall keyword clusters repeatedly omitted: *few-shot video anomaly detection*, *episodic training anomaly*, *meta-learning VAD*, *scene graph anomaly*, and *leave-one-scene-out generalization*. The related work section’s coverage remains incomplete.  

**4. Evidence table 中 overlap classification 的误判风险**  
The authors provide an overlap classification that in my assessment is **overly optimistic** in several entries:  
- **Meta-AD** is classified as “partial overlap” (different meta-learning backbone); however, both SRN and Meta-AD address **few-shot VAD with leave-one-scene-out evaluation**, making the problem setting essentially identical. The difference reduces to a relation network vs. a generic meta-learner, which is a **method-level variation**, not a problem-setting gap. The overlap should be reclassified as **substantial**.  
- **Episodic training methods** (e.g., the ICCV 2021 work above) are omitted from the table entirely; if included, they would fall into **very high overlap** because they already use episodic sampling for VAD.  
- The authors label some **graph-based anomaly detection** works as “orthogonal/no overlap”, claiming SRN’s relation is learned from dynamic interactions rather than static graphs. This is **overly pessimistic** for the prior art: many graph-based methods (e.g., ST-GCN-based) also learn dynamic relation weights, making the distinction fuzzy. The “no overlap” classification risks downplaying genuine baselines.  

**5. Problem-setting novelty vs method novelty 混淆**  
SRN claims to introduce a **new problem setting** - “scene-aware few-shot anomaly detection” - but the contribution is largely method-level. The setting of **few-shot VAD where support and query come from different scenes** is a straightforward instantiation of leave-one-scene-out cross-validation, already used in Meta-AD and several domain-generalization-inspired VAD papers. Framing this as a novel problem setting overstates the contribution; the truly new element is the specific relation network architecture. The paper should reframe its novelty as a **method for an existing few-shot VAD setting**, not as a new task definition.  

**6. Unsupported claims**  
Several statements lack sufficient support:  
- “We are the first to address few-shot anomaly detection in videos using only normal videos during meta-training.” This ignores the ICCV 2021 episodic training work and the 2023 arXiv meta-learning paper mentioned above, both of which operate in the same normal-only few-shot regime. The claim needs to be removed or carefully qualified after checking priority.  
- “Our scene-relation network is the first to capture dynamic object interactions for anomaly detection.” Similar dynamic relation modeling appears in HRN and ST-GCN-based methods; the claim must be softened unless the authors can demonstrate a clear architectural distinction that is not present in prior work.  
- The paper asserts “state-of-the-art results on all benchmarks” without comparing to Meta-AD or episodic baselines on the same leave-one-scene-out protocol. The current comparison tables only include classical fully-supervised or unsupervised methods, which is insufficient to support SOTA for few-shot VAD.

**7. Required Round 2 searches**  
The authors must conduct systematic database searches (Google Scholar, DBLP, Scopus) with the following queries and report findings:  
- `“few-shot video anomaly detection” AND (“episodic” OR “meta-learning”)`  
- `“leave-one-scene-out” AND “anomaly detection”`  
- `“scene graph” AND “video anomaly”`  
- `“relation network” AND “anomaly detection” AND “video”`  
- `“episodic training” AND “anomaly”`  
All newly identified papers must be discussed and, if feasible, included in the evidence table and experimental comparisons.  

**8. Recommended decision and mandatory SRN contribution narrowing**  
**Decision: Revise (major).** The paper addresses a relevant topic, but the current manuscript’s novelty is significantly obscured by missing related work and overclaims. I cannot recommend acceptance without a thorough revision that:  
1. Explicitly acknowledges and compares the few-shot episodic VAD paradigm (Meta-AD, episodic training approaches) and reclassifies overlap correctly.  
2. Removes claims of a new problem setting; reposition the novelty strictly as a **method contribution within the established few-shot VAD setting**.  
3. Adds mandatory baselines in the experimental section (or provides a compelling reason if code/data are unavailable).  
4. Conducts the Round 2 searches and updates the related work section accordingly.  
If the authors cannot demonstrate a clear, verifiable advantage over existing episodic VAD methods after these additions, the paper’s incremental merit would be insufficient for acceptance, and the manuscript would then lean toward **stop**. The SRN contribution must be **shrunk** to: *a relation-network-based few-shot VAD method that, compared to prior meta-learning VAD, shows improvements on certain scene-shifts.* No new setting, no first-of-its-kind claims.
```

### Codex 对 reviewer 建议的一手来源核验状态

| Reviewer item | 当前核验状态 | Codex 初步处理 |
|---|---|---|
| Verdict `NOVELTY AT RISK` | 作为 reviewer opinion 已记录；不是一手证据 | 接受其风险分级作为保守外部意见。第一轮本地 `NOVELTY PLAUSIBLE` 应下调为“有条件 / contested”，待 Round 2 后再定。 |
| Domain-invariant / disentangled VAD seeds | 第一轮未找到可靠一手来源；reviewer 仍认为是最高风险 | 保留为 Round 2 最高优先级；不得写入正式 evidence table，直到核验原文。 |
| Action Hints 作为强威胁 | 已有一手来源；但其 skeleton / language typicality / test-time uniqueness 与 SRN 机制不同 | 上调为 strong novelty threat；下一轮核验其 references 和是否有 scene residualization follow-up。 |
| Appearance-motion / memory family | 已有部分一手来源，但主要威胁 AMCN，不直接覆盖 SRN | 保留为 AMCN 风险和 SRN baseline/head 风险；继续核验是否存在 explicit subtraction。 |
| Few-shot / episodic / Meta-AD claims | reviewer 输出明显将 SRN 误读为 few-shot / relation-network method；当前 SRN 不是 few-shot support-query method，也不是 relation-network paper | 作为“可能遗漏 episodic normality learning / meta-learning VAD”处理，但 reviewer 关于 SRN claims 的具体批评不直接适用。需要 Round 2 核验 Meta-AD / episodic VAD 原文。 |
| Graph / ST-GCN / HRN / relation network | reviewer 误读 SRN 为 relation network；当前 SRN 最小规格没有 object graph / relation network | 不作为 SRN direct threat；可作为 object-centric / relation baseline 的 later check。 |
| Unsupported claims: first few-shot VAD / SOTA / relation network first | 当前项目文档没有这些 claim | 记录为“避免未来误写”的负面约束；不需要修改现有第一轮 evidence table。 |
| Required Round 2 searches | 多数合理，但需扩展回 SRN 真正主线 | Round 2 应同时覆盖：domain-invariant/disentangled VAD、scene residualization、nuisance prediction/subtraction、one-class DG、episodic normality learning、Meta-AD/few-shot VAD、MoCoDAD/Ada-VAD、threshold transfer。 |

### Codex 综合判断

Reviewer 成功指出第一轮 `NOVELTY PLAUSIBLE` 可能偏乐观，尤其是未核验的 domain-invariant / disentangled VAD seeds 和 non-VAD residualization family。其 `NOVELTY AT RISK` verdict 应被视为保守外部风险意见。

但 reviewer 的第二段存在明显任务漂移：它把 SRN 误读为 few-shot / relation-network / scene-relation paper，并提出了若干与当前 SRN 最小规格不直接对应的批评。这些内容不能直接改变 SRN 机制判定，但应触发 Round 2 对 meta-learning / episodic VAD 的补查，防止 ELOS 被已有 episodic normality learning 覆盖。

当前建议：

- 将第一轮状态从单纯 `NOVELTY PLAUSIBLE` 调整为：**`NOVELTY PLAUSIBLE but externally contested; treat as NOVELTY AT RISK until Round 2 closes domain-invariant/disentangled and episodic VAD leads`**。
- 不把 reviewer 新论文名写入正式 evidence table；全部先进入 Round 2 TODO。
- SRN contribution 继续收缩为：**frozen-feature normal-only VAD 中的 selective scene-predictable residualization + controlled context retention + fixed-threshold reliability diagnostics**。
- ELOS 继续仅作为 training/validation principle，不作为贡献。
- 立即进行 Round 2 primary-source verification，而不是进入实验。
