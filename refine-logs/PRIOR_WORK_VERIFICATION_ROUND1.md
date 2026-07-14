# Prior Work Verification Round 1

**检索日期：** 2026-07-14  
**项目状态：** `READY WITH RESTRICTIONS / HOLD`；restricted bridge 尚未启动。  
**本轮范围：** 只做文献查新、论文核验、证据整理和文档编写；未下载数据、未训练、未使用 GPU、未调用 `/experiment-bridge`。

## 1. Scope

本轮回答一个窄问题：

> 已有工作是否已经直接提出，或实质等价地提出了 SRN 所描述的机制？

SRN 的当前最小机制链为：

1. 输入 frozen representation `z`；
2. 提取低容量 scene/context token `c`；
3. 从 `c` 估计 scene-predictable component `û`；
4. 构造 residual event feature `r = z - û`；
5. 保留受控 context path `q`，避免完全删除 location/context；
6. 用 `r` 与有限 `q` 做 normality modeling；
7. 用 held-out scene / leave-one-scene-out / episodic protocol 面向 unseen-scene 泛化；
8. 关注 fixed source-threshold transfer、low-FPR、FA/hour、worst-target，而不只 pooled frame AUROC。

## 2. Search Sources

使用的一手来源类型：

- arXiv 原文页 / HTML；
- CVF Open Access；
- 论文 DOI / official paper page（如 arXiv 页面列出的 DOI）；
- 作者代码仓库仅作为辅助确认，未作为机制结论主证据。

未使用作为最终证据的来源：

- 搜索结果摘要；
- Google Scholar / Semantic Scholar 作为唯一证据；
- 博客、知乎、CSDN、二手论文解读；
- LLM 自动生成的引用。

## 3. Search Queries

### Round 1：高精度检索

- `"scene-invariant" "video anomaly detection"`
- `"scene-disentangled" "video anomaly detection"`
- `"domain generalization" "video anomaly detection" "anomaly detection"`
- `"cross-dataset" "video anomaly detection" "normal-only"`
- `"Domain-Invariant Feature Learning" "Video Anomaly Detection"`
- `"Disentangled Representations" "Domain-General" "Video Anomaly Detection"`
- `"SDG-net" "video anomaly detection"`
- `"DIRT" "video anomaly detection"`

### Round 2：方法族扩展

- `"Generalizable" "Video Anomaly Detection" arxiv`
- `"unseen scene" "video anomaly detection"`
- `"cross-scene" "video anomaly detection"`
- `"scene-aware" "video anomaly detection" "CVPR"`
- `"zero-shot" "video anomaly detection" "ShanghaiTech" "NWPU"`
- `"normal-only" "video anomaly detection" "zero-shot"`
- `"source-free" "video anomaly detection" "anomaly"`
- `"target domain" "video anomaly detection" "normal"`
- `"Few-Shot Scene-Adaptive Anomaly Detection"`
- `"Meta-AD" "video anomaly detection"`
- `"Motion-Appearance Co-Memory" "video anomaly detection"`
- `"MocoDAD" "video anomaly detection"`

### Round 3：反向查漏

- `"residual" "scene" "video anomaly detection"`
- `"scene component" "video anomaly detection"`
- `"leave-one-scene-out" "video anomaly detection"`
- `"episodic" "one-class" "anomaly detection" "domain generalization"`
- `"nuisance" "one-class" "domain generalization" "anomaly detection"`
- `"domain-invariant normality" "anomaly detection"`
- `"domain generalization" "industrial anomaly detection"`
- `"cross-domain" "one-class" "anomaly detection"`
- `"false alarms per hour" "video anomaly detection"`
- `"RBDC" "TBDC" "video anomaly detection"`

## 4. Inclusion / Exclusion Criteria

纳入：

- normal-only / one-class / semi-supervised VAD；
- zero-shot / cross-domain / cross-dataset / unseen-scene VAD；
- scene-aware / scene-adaptive / scene-conditioned VAD；
- appearance-motion consistency、motion-guided memory、prototype/memory VAD；
- 非 VAD 但机制上接近 domain generalization、nuisance removal、residualization 的工作。

排除或降权：

- weakly supervised UCF-Crime / XD-Violence 主线，若训练使用异常视频标签；
- 使用 target normal 或 target few-shot data 的方法，不能等价为 strict zero-shot；
- 只做 same-dataset AUC 的方法，不能覆盖 SRN 的 fixed-threshold transfer 目标；
- 未能找到一手来源的 reviewer seed。

## 5. Candidate Literature by Priority Category

### Priority 1：Scene-invariant / scene-disentangled VAD

第一轮没有发现显式满足 `z→c→û→r=z-û→q` 的 scene residual VAD。最接近的是：

- HSC：scene-aware，不是 scene-invariant。它增强 foreground object 和 background scene semantics，并用 scene/object-level contrast 使 latent features 按 semantic class compact/separable。
- NWPU scene-conditioned auto-encoder：面向 scene-dependent anomalies，强调 scene context，而不是删除 scene nuisance。
- EVAL：location-dependent single-scene model，证明 context/location 有价值，但不是 unseen-scene residualization。

结论：这类工作支持 SRN 的“不能完全去场景化”边界，但没有直接覆盖 SRN 的 selective scene residual interface。

### Priority 2：Domain Generalization for Anomaly Detection

高相关工作包括：

- zxVAD：定义 zero-shot cross-domain VAD without target adaptation；用 future-frame prediction、Normalcy Classifier 和 pseudo-abnormal synthesis。
- Action Hints：zero-shot skeleton-based VAD，使用 skeleton 减少 background/appearance domain gap，训练 action typicality，测试时做 context uniqueness。
- Few-shot Scene-adaptive AD：unseen scene + few target frames + meta-learning；不是 strict zero-shot。
- Appearance Blur + Motion-guided Memory：cross-dataset zero-shot VAD，依赖 blur pseudo-anomaly 与 motion memory。

结论：这些工作强烈覆盖 cross-domain / zero-shot problem setting，构成 SRN 的主要 novelty risk；但它们没有显式估计 scene-predictable feature component 并做 residual subtraction，也没有 SRN 的 controlled context path。

### Priority 3：Feature Disentanglement / Nuisance Removal

VAD 内直接的 `scene nuisance prediction → feature subtraction` 未找到。机制邻近包括：

- appearance-motion semantics consistency；
- multi-level memory-augmented appearance-motion correspondence；
- motion-guided memory；
- skeleton-based background/appearance domain removal。

结论：appearance-motion family 对 AMCN 风险更高；对 SRN 是机制邻居而非 direct coverage。下一轮应继续查 domain-invariant / residualization 的非 VAD one-class AD 文献。

### Priority 4：Cross-Dataset / Normal-Only VAD

Rashidi 2026 是 SRN 动机最关键的 problem-setting overlap：frozen feature + kNN/Mahalanobis 在 cross-dataset source→target matrix 中 collapse，且 false alarms/hour 极高。它不是新 detector，但锁定了 SRN 不能把 cross-dataset audit 本身作为贡献。

## 6. Direct-Coverage Analysis

本轮未发现 A 类 direct coverage。

未发现任何论文同时满足以下组合：

- normal-only 或严格近似 normal-only VAD；
- 显式识别 scene/domain nuisance；
- 从低容量 scene/context token 预测 scene-predictable feature component；
- 执行显式 `r = z - û` residual subtraction；
- 保留 controlled context path；
- 使用 unseen-scene / leave-one-scene-out / episodic protocol；
- 以 fixed source-threshold transfer、low-FPR 或 FA/hour 作为关键目标。

最需要警惕的是 zxVAD、Action Hints、Appearance Blur + Motion-guided Memory、Few-shot Scene-adaptive AD。它们覆盖 zero-shot / unseen-domain / scene adaptation 问题，但机制与 SRN 不等价。

## 7. Partial-Overlap Analysis

### zxVAD

风险等级：高。  
重叠：zero-shot cross-domain VAD without target adaptation；normalcy feature learning。  
差异：使用 pseudo-abnormal synthesis、future-frame prediction 与 Normalcy Classifier；没有 scene token、scene-predictable component subtraction、controlled context path 或 ELOS。

### Action Hints

风险等级：高。  
重叠：generalizable / zero-shot VAD，100+ unseen scenes；显式利用 context uniqueness。  
差异：skeleton-only；使用 language/LLM typicality 知识和 test-time uniqueness；不属于 frozen video feature residualization，也不是 strict normal-only SRN。

### HSC

风险等级：中高。  
重叠：显式建模 scene/background/object semantics；从 normal videos 学 VAD。  
差异：目标是 scene-aware，而非 scene-invariant；contrastive learning 使 semantic class compact/separable，不做 scene component subtraction。

### Few-shot Scene-adaptive AD

风险等级：中高。  
重叠：unseen scene、normal-only、meta-learning。  
差异：使用 target few frames；不是 strict zero-shot；没有 SRN residual interface。

### Appearance Blur + Motion-guided Memory

风险等级：中高。  
重叠：cross-dataset zero-shot VAD；motion memory；关注 new target domains。  
差异：pseudo-anomaly blur + motion memory；没有 scene residual subtraction 或 context path。

## 8. Important Negative Findings

- 第一轮没有核验到 reviewer seed 中的 `DIRT` / `SDG-net` / “Domain-Invariant Feature Learning for VAD, MVA 2023” / “Disentangled Representations for Domain-General VAD, CVPRW 2024” 为可靠一手来源。
- 未发现 VAD 论文明确提出 `z → c → û → r = z - û → q`。
- 未发现已有 VAD 工作把 scene-aware 与 scene-invariant 的冲突通过“显式 residual subtraction + controlled context retention”组合处理。
- cross-dataset / zero-shot VAD 已经是活跃主题，SRN 不能声称提出这个 problem setting。
- ELOS / leave-one-domain-out 不能作为独立 novelty；只能作为 SRN 的训练/验证原则。

## 9. Remaining Uncertainty

- 非 VAD 领域的一类 anomaly detection / industrial AD / OOD 中可能已有更接近的 domain nuisance residualization。
- zxVAD、Action Hints、Appearance Blur + Motion-guided Memory 的 references / cited-by 需要继续追踪，尤其是 domain-adversarial、skeleton diffusion、motion-conditioned diffusion、domain adaptation VAD。
- reviewer seed 可能存在简称错写或 venue/year 错写，需要用作者链和 references 继续查。
- 本轮未系统核验 IEEE/ACM/Springer paywalled 正式版本，主要使用 open primary sources。

## 10. Preliminary Novelty Verdict

**Verdict：`NOVELTY PLAUSIBLE`**

理由：

- 第一轮未发现直接覆盖 SRN 完整机制链的工作；
- 已发现多篇 strong partial overlap，说明 SRN 的贡献表述必须收缩；
- SRN 可保留为“selective scene-predictable residualization + controlled context retention + fixed-threshold transfer diagnostics”的候选，而不能表述为泛泛 scene-invariant / domain-general VAD；
- 该 verdict 不是最终 novelty 证明，仍需要第二轮 references/cited-by 与非 VAD residualization 查新。

## 11. Recommended Next Verification Round

下一轮优先查：

1. zxVAD 的 related work / cited-by，特别是 cross-domain VAD without adaptation、Ada-VAD、domain-adversarial VAD；
2. Action Hints references 中的 MoCoDAD、STG-NF、DA-Flow、FG-Diff 和 skeleton zero-shot VAD；
3. industrial / image anomaly detection 中的 domain nuisance residualization、value-order decomposition、domain-invariant one-class learning；
4. “residualization / predictable component removal / nuisance prediction” 在 OOD 和 one-class learning 中的先例；
5. threshold transfer、EVT、conformal anomaly detection 与 FA/hour operating point 文献。

## 12. Sources

详细逐篇证据见 `refine-logs/PRIOR_WORK_EVIDENCE_TABLE.md`。
