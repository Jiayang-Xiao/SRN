# Prior Work Verification Round 2

**日期：** 2026-07-14  
**任务类型：** 高风险线索关闭与 SRN Novelty Gate  
**执行边界：** 未下载数据、未使用 GPU、未训练、未提取 feature、未进入 `/experiment-bridge`。

## SRN Ground-Truth Definition

SRN 不是 few-shot support-query VAD、relation network、scene graph、object interaction network、新 few-shot setting、target-scene adaptation、complete scene removal、单纯 domain adversarial training 或单纯 ELOS protocol。当前 SRN 是：在 frozen video representation `z=f(x)` 上提取低容量 scene token `c=g(z)`，预测 scene-predictable component `u_hat=h(c)`，显式构造 residual event feature `r=P(z-u_hat)`，同时保留低容量受控上下文 `q=a(c)`，用 `e=[r;lambda q]` 在 source normal data 上建模 normality；held-out whole source scene 只用于泛化检查，不做 target adaptation。fixed source-threshold、low-FPR 和 FA/hour 是可靠性评估要求，不是独立方法贡献。

## 1. Scope

Round 2 只回答三个 gate 问题：

1. 是否已有 VAD 或高度相近 one-class AD 提出 `predict nuisance -> explicit residualization -> retained context -> normality modeling`？
2. 是否已有 episodic / leave-one-scene-out / meta-learning VAD 使 ELOS 只能作为常规训练/验证手段？
3. SRN 是 ready to request restricted bridge、revise before bridge、stop，还是 continue verification？

## 2. Sources and Search Process

使用 primary / traceable sources：

- arXiv 原文页 / ar5iv HTML；
- CVF / official paper pages where available；
- DBLP-oriented title/acronym search；
- precise title search；
- acronym search；
- query variants for VAD, one-class AD, OOD, industrial AD。

未使用作为证据：

- reviewer-generated titles without primary source；
- 搜索结果摘要作为唯一机制证据；
- 博客、二手综述、LLM-generated citation。

## 3. Search Queries

### Lane A: reviewer seed resolution

- `"Domain-Invariant Feature Learning for Video Anomaly Detection"`
- `"Disentangled Representations for Domain-General Video Anomaly Detection"`
- `"Learning Scene-Invariant Normalcy" "Video Anomaly Detection"`
- `"Deep Scene Decomposition" "Unsupervised Anomaly Detection"`
- `DIRT "video anomaly detection"`
- `"SDG-Net" "video anomaly detection"`
- `"Meta-AD" "video anomaly detection"`
- `"DeepCrowd" "video anomaly detection"`
- `"Few-Shot Anomaly Detection via Episodic Training"`
- `"Memory-Augmented Meta-Learning" "Video Anomaly Detection"`

### Lane B/C: domain invariance and residualization

- `"domain invariant" "video anomaly detection"`
- `"domain generalization" "video anomaly detection"`
- `"disentangled" "video anomaly detection"`
- `"background-agnostic" "video anomaly detection"`
- `"scene residual" anomaly detection`
- `"nuisance component" residual anomaly`
- `"predictable component" anomaly detection`
- `"feature residualization" one-class`
- `"context residual" anomaly detection`
- `"background residual" anomaly detection`
- `"Anomaly Detection under Distribution Shift"`
- `"Toward Generalist Anomaly Detection via In-context Residual Learning"`

### Lane D/E/F: episodic / skeleton / threshold

- `"few-shot video anomaly detection" episodic meta-learning`
- `"Learning Normal Dynamics in Videos with Meta Prototype Network"`
- `"MoCoDAD"`
- `"STG-NF" "video anomaly detection"`
- `"DA-Flow" "video anomaly detection"`
- `"false alarms per hour" "video anomaly detection"`
- `"threshold transfer" "video anomaly detection"`

## 4. Lane A Findings: Reviewer Seed Resolution

Full disposition is in `refine-logs/REVIEWER_LEAD_DISPOSITION.md`.

Key outcomes:

- `DIRT`, `SDG-Net`, exact “Domain-Invariant Feature Learning for VAD”, “Disentangled Representations for Domain-General VAD”, “Learning Scene-Invariant Normalcy”, “Deep Scene Decomposition”, and “Memory-Augmented Meta-Learning for VAD” were not resolved as reliable primary-source VAD papers.
- `Meta-AD` was not verified under the reviewer’s title/year; the real relevant family is Few-shot Scene-adaptive AD and Meta Prototype Network.
- `Learning Conditional Motion Priors for VAD` appears to be an identity mismatch; the verified relevant work is MoCoDAD.
- `MoCoDAD`, `STG-NF`, `DA-Flow`, and Meta Prototype Network are real and relevant, but do not cover M3-M6.

## 5. Lane B Findings: Scene / Domain Invariance in VAD

Verified strong VAD neighbors:

- Background-Agnostic AED uses object detections and adversarial pseudo-abnormal training to become background-agnostic across databases.
- STG-NF / DA-Flow / Action Hints use skeleton representations to sidestep appearance/background nuisance.
- HSC uses foreground/background semantics and scene/object contrast to become scene-aware.
- zxVAD addresses cross-domain VAD without target adaptation, but via prediction, normalcy classifier and pseudo-abnormal synthesis.

None of these explicitly predicts a scene/domain component and subtracts it from frozen video features. They support required baselines and contribution narrowing, but not direct SRN coverage.

## 6. Lane C Findings: Residualization / Nuisance Subtraction

The highest non-VAD mechanism threat is InCTRL. It learns residuals between query images and few-shot normal prompts using frozen CLIP features, but it is image/generalist AD, uses target normal prompts at inference, and the residual is query-vs-normal-prompt discrepancy, not scene/domain-predictable component subtraction.

ADShift / GNL and invariant AD under distribution shifts are strong non-VAD domain-shift priors. They learn distribution-invariant normality or causal invariance, but do not perform `c=g(z), u_hat=h(c), r=z-u_hat`.

No verified non-VAD paper in this pass fully covers M3-M6 in the SRN sense. However, these papers make it unsafe to claim generic residual learning or generic domain-invariant AD novelty.

## 7. Lane D Findings: Episodic / Meta-learning / Leave-one-scene-out

ELOS has clear prior as a general idea:

- Few-shot Scene-adaptive AD uses meta-learning to detect anomalies in unseen scenes with a few target frames.
- Meta Prototype Network introduces a few-shot normalcy learner for fast adaptation to new scenes.
- ADShift’s related work identifies MPN and Few-shot Scene-adaptive AD as cross-domain AD methods requiring few target samples or labels.

Therefore ELOS must remain a training/validation principle only. This does not collapse SRN because the verified episodic/few-shot methods use target support/adaptation and do not implement M3-M6.

## 8. Lane E Findings: Action Hints Citation Chain

Resolved items:

- STG-NF: skeleton normalizing flow, normal-only option, removes nuisance by pose input.
- MoCoDAD: skeleton diffusion conditioned on past motion, OCC trained on normalcy.
- DA-Flow: dual-attention normalizing flow on skeleton sequences.

Unresolved:

- FG-Diff exact VAD identity not resolved.
- Ada-VAD exact identity not resolved.

These are important skeleton / motion-conditioned baselines and AMCN threats, but not SRN direct coverage.

## 9. Lane F Findings: Threshold and Low-FPR Reliability

Rashidi 2026 remains the key source for cross-dataset audit and FA/hour reliability. Street Scene / RBDC / TBDC remain evaluation-protocol prior. Exact “threshold transfer VAD” papers were not resolved as direct SRN threats in this pass.

Conclusion: fixed threshold and low-FPR are protocol discipline, not method novelty.

## 10. Mechanism Coverage Summary

Across verified papers, no VAD paper satisfies all of:

- M2 normal-only；
- M3 explicit scene/domain/context representation；
- M4 predictor of scene/domain/nuisance component；
- M5 explicit subtraction / residualization `z-u_hat`；
- M6 controlled context-retention path。

Closest verified coverage:

- Background-Agnostic AED: M2/M3-ish/M7-ish, no M4/M5/M6.
- STG-NF / DA-Flow / Action Hints: scene removal by skeleton input, no learned residualization.
- MPN / Few-shot Scene-adaptive: ELOS/meta prior, but target adaptation and no residual interface.
- InCTRL: non-VAD residual learning, but query-vs-normal prompts, not scene-predictable subtraction.
- ADShift/GNL: non-VAD distribution-invariant normality, no subtraction.

## 11. Negative Findings

- No verified direct VAD coverage of `c -> u_hat -> z-u_hat -> q`.
- No verified VAD work retaining a controlled scene/context path after explicit scene-predictable component subtraction.
- No verified exact primary source for several reviewer-generated titles.
- No verified source-threshold transfer method that changes SRN mechanism verdict.

## 12. Unresolved Uncertainty

- `FG-Diff` and `Ada-VAD` remain unresolved acronym leads.
- Paywalled IEEE/ACM/Springer variants may contain details not visible through open abstracts.
- Non-VAD residualization is broad; this pass found InCTRL and GNL but did not exhaust all industrial/medical residual decomposition work.

## 13. Round 2 Verdict

**Novelty verdict：`NOVELTY PLAUSIBLE`**

Reason: Round 2 closed the highest reviewer-generated direct-coverage seeds as hallucinated, identity mismatch, or relevant-but-not-direct. Verified VAD works cover scene removal, background-agnostic object modeling, skeleton input, cross-domain setting, target-scene adaptation, and meta-learning, but not M3-M6.

## 14. Operational Decision

**Operational decision：`READY TO REQUEST RESTRICTED BRIDGE`**

This only means the novelty gate is sufficiently closed to ask the user whether to enter a restricted bridge later. Execution remains `HOLD`; no data, GPU, feature extraction, training, or `/experiment-bridge` is authorized.

Required contribution narrowing:

- SRN is not a new cross-domain VAD setting.
- ELOS is not a contribution.
- Low-FPR / FA/hour is evaluation discipline, not method novelty.
- SRN’s minimal contribution is: **selective scene-predictable residualization with controlled context retention for frozen-feature normal-only VAD, evaluated under source-only threshold transfer and low-FPR reliability diagnostics.**
