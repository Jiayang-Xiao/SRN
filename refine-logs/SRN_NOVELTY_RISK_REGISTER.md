# SRN Novelty Risk Register 第一轮

**检索日期：** 2026-07-14  
**当前 preliminary verdict：** `NOVELTY PLAUSIBLE`，但存在 strong partial overlap。

| Risk ID | Threatening paper / method | 被覆盖的 SRN component | 风险等级 | 当前证据 | 是否可通过重新定位 contribution 规避 | 需要的实验或进一步查新 | Stop condition |
|---|---|---|---|---|---|---|---|
| R01 | zxVAD: *Cross-Domain Video Anomaly Detection without Target Domain Adaptation* | zero-shot cross-domain VAD；normalcy learning；no target adaptation | 高 | Abstract 明确提出 target-domain no-training VAD、Normalcy Classifier、pseudo-abnormal synthesis | 可以。SRN 必须定位为 scene-predictable residualization + controlled context，而非 zero-shot VAD setting | 追踪 zxVAD references/cited-by；实验中加入 pseudo-anomaly/future-prediction 或引用为 setting prior | 若发现 zxVAD 或后续工作已有 scene component subtraction + context path，SRN novelty at risk。 |
| R02 | Action Hints: skeleton-based generalizable / zero-shot VAD | unseen-scene generalization；context uniqueness；scene-adaptive boundary | 高 | arXiv 明确 no target training samples、100+ unseen scenes、test-time uniqueness analysis | 可以。SRN 是 frozen video representation residualization，不依赖 skeleton-only / language typicality / test-time target boundary | 核验其 references：MoCoDAD、STG-NF、DA-Flow、Ada-VAD | 若其方法或 follow-up 已有 residual scene nuisance suppression，需收缩 SRN。 |
| R03 | HSC: *Hierarchical Semantic Contrast for Scene-aware VAD* | scene/background/object semantic modeling；normal-only VAD | 中高 | Abstract 明确 from normal videos，scene-level/object-level contrast | 可以。HSC 是 scene-aware，SRN 是 selective suppression + retained context；需强调不是 complete invariance | 实验需对比 scene-aware/context path failure；related work 明确 contrast vs residual | 若 HSC 在未见场景或 scene-disentangled variant 中已有同机制，SRN 降级。 |
| R04 | Few-shot Scene-adaptive AD | unseen scene；meta-learning / episodic adaptation | 中高 | ECCV 2020 work uses few target frames from previously unseen scene | 可以。SRN strict zero-shot 不使用 target frames；ELOS 不能作为独立 novelty | 继续查 meta-learning / scene-adaptive VAD | 若 SRN 后续使用 target normal data，必须分到 calibration/adaptation track。 |
| R05 | Appearance Blur + Motion-guided Memory | cross-dataset zero-shot VAD；motion memory | 中高 | Abstract 明确 cross-dataset validation with zero-shot; motion-guided memory | 可以。该方法是 blur/deblur + motion memory，不是 scene residualization | 核验 KBS version and cross-domain protocol；作为 AMCN/SRN baseline risk | 若其 motion memory解释 SRN全部收益，SRN必须收缩到 scene residual diagnostic。 |
| R06 | MAMC / AMSRC appearance-motion correspondence family | AMCN backup；appearance-motion relation | 中 | Abstracts show appearance-motion semantics alignment / consistency | 可规避，对 SRN 风险较低，对 AMCN 风险高 | 若转向 AMCN，必须全量查新 conditional motion / correspondence | 若已有 frozen-feature conditional residual + cross-scene protocol，AMCN discard。 |
| R07 | Rashidi 2026 cross-dataset audit | frozen-feature audit；kNN/Mahalanobis baselines；FA/hour | 中 | cross-dataset AUC collapse and Mahalanobis control already shown | 可规避。SRN 不 claim audit novelty，只 claim mechanism if validated | 复核 code/splits later；本轮不下载数据 | 若 SRN 只重复 audit，无机制增益，不能作为 method contribution。 |
| R08 | NWPU scene-conditioned auto-encoder / scene-dependent anomalies | context-retention necessity；scene-conditioned modeling | 中 | NWPU paper states scene-dependent anomalies and scene-conditioned AE | 可规避。SRN must not remove all scene info; context path central | 后续分层 scene-dependent/generic anomalies；首轮不下载 Tier B | 若 SRN harms scene-dependent anomalies，停止 scale-up。 |
| R09 | EVAL location-dependent scene model | context/location normality | 中 | CVF abstract: location-dependent model of particular scene | 可规避。EVAL is same-scene/location model, not unseen-scene residualization | 后续作为 object/location baseline, not first-round implementation | 若 SRN fails location-dependent context, contribution must shrink. |
| R10 | 未核验 reviewer seed: DIRT/SDG-net/domain-invariant VAD | possible direct scene/domain disentanglement | 未知但需警惕 | 第一轮未找到 primary source | 暂不能规避，只能继续查 | 第二轮从 venue proceedings、references、作者链查 | 若发现真实 direct coverage，verdict 改为 `NOVELTY AT RISK` 或 `COLLAPSED`。 |

## 当前总体风险判断

- Direct coverage：未发现。
- Strong partial overlap：已发现，尤其 zxVAD、Action Hints、HSC、Few-shot Scene-adaptive、Appearance Blur + Motion-guided Memory。
- 最大风险不是“有人做过 cross-domain VAD”，而是下一轮可能发现某个 domain-invariant / residualization 工作已经包含 `scene token → predicted nuisance → residual + retained context`。
- 当前可保留 SRN，但 contribution 必须写成：**面向 frozen-feature normal-only VAD 的 selective scene-predictable residualization，并显式诊断 context retention 与 fixed-threshold transfer**。

## Round 2 Risk Update

**日期：** 2026-07-14

| Risk ID | Updated risk | Round 2 evidence | Action |
|---|---|---|---|
| R01 zxVAD | Medium-high, problem-setting threat | verified cross-domain VAD without target adaptation, but no M4/M5/M6 | cite as setting prior; do not claim cross-domain setting novelty |
| R02 Action Hints | High, deployment-goal / skeleton threat | verified skeleton-based zero-shot/generalizable VAD; no learned scene residualization | cite as skeleton alternative; compare later if feasible |
| R03 HSC | Medium-high, context/scene-aware threat | verified scene-aware contrast; no subtraction | use to motivate controlled context and scene-aware baseline |
| R04 Few-shot Scene-adaptive / MPN | High for ELOS, low for SRN mechanism | verified target-support / meta-learning adaptation; no M3-M6 | ELOS not contribution; strict zero-shot must stay separate |
| R05 Background-Agnostic AED | High baseline threat | verified object-level background-agnostic cross-database VAD | required conceptual baseline / related work; no direct coverage |
| R06 STG-NF / DA-Flow / MoCoDAD | Medium-high skeleton / AMCN threat | verified skeleton normalizing flow and motion-conditioned diffusion | baseline narrative; not SRN direct |
| R07 InCTRL | Medium non-VAD residual threat | verified in-context residual learning on images with normal prompts | do not claim generic residual learning novelty |
| R08 ADShift / invariant AD | Medium non-VAD DG threat | verified distribution-invariant normality; no subtraction | include as non-VAD mechanism neighbor |
| R09 reviewer hallucinated seeds | lowered | many exact titles unresolved or likely hallucinated | do not cite; preserve disposition table |

**Round 2 gate risk：** direct SRN novelty is plausible, but only under narrow contribution language and required baselines.
