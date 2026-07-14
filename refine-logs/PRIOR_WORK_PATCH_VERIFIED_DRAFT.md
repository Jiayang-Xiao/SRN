# Prior Work Patch Verified Draft 第一轮

**日期：** 2026-07-14  
**基于：** `refine-logs/PRIOR_WORK_PATCH.md`  
**状态：** 候选修订稿；不替换冻结文件。  
**证据来源：** `refine-logs/PRIOR_WORK_EVIDENCE_TABLE.md`

## 1. 已核验 paper 覆盖

| Paper / method | 核验状态 | 支持的作用 | 对 SRN 的影响 | 限制 |
|---|---|---|---|---|
| Rashidi 2026, *Benchmark AUC Is Not Deployable Reliability* | 已核验，P01 | 支持 frozen features + kNN/Mahalanobis cross-dataset collapse；支持 FA/hour 与 source→target matrix 必要性 | SRN 不能 claim cross-dataset audit novelty；必须在同协议下证明 mechanism gain | 不是新 detector；不提供 scene residualization |
| Sun and Gong 2023, HSC | 已核验，P02 | scene-aware VAD from normal videos；foreground/background scene semantics；scene/object contrast | 支持 context retention 风险；HSC 是 scene-aware 近邻 | 不做 explicit residual subtraction；不是 unseen-scene invariance |
| Aich et al. 2023, zxVAD | 已核验，P03 | zero-shot cross-domain VAD without target adaptation；Normalcy Classifier；pseudo-abnormal synthesis | 强 partial overlap；SRN 不得 claim zero-shot cross-domain setting novelty | 使用 pseudo-abnormal synthesis / prediction，不是 SRN residual interface |
| Lu et al. 2020, Few-shot Scene-adaptive AD | 已核验，P04 | unseen scene + few frames + meta-learning；normal-only scene adaptation | ELOS/meta-learning 风险；strict zero-shot 与 target-normal adaptation 必须分开 | 使用 target frames，不是 strict source-only |
| Tang et al. 2025, Action Hints | 已核验，P05 | zero-shot / generalizable skeleton-based VAD；context uniqueness；100+ unseen scenes | 强 partial overlap；SRN 必须区别于 skeleton/language/test-time uniqueness | 使用 skeleton/action typicality；非 SRN frozen feature residual |
| Lyu et al. 2026/2024, Appearance Blur + Motion-guided Memory | 已核验，P06 | cross-dataset zero-shot VAD；motion-guided memory | 对 AMCN 和 SRN normality head 有风险；可作 later baseline family | pseudo-anomaly blur + motion memory；无 scene residualization |
| Huang et al. 2023, MAMC | 已核验，P07 | appearance-motion correspondence、memory-guided suppression | AMCN 风险；对 SRN 是 mechanism-only neighbor | same-dataset AUC；无 scene/domain protocol |
| Huang et al. 2022/2023, AMSRC | 已核验，P08 | appearance-motion semantic consistency | AMCN 风险；不直接覆盖 SRN | 无 explicit scene nuisance |
| Ristea et al. 2024, Self-Distilled MAE | 已核验，P09 | motion-weighted tokens、teacher/student discrepancy、synthetic anomalies | Idea 11 降为 efficiency baseline | 不纯 normal-only；不解决 SRN scene residual |
| Singh et al. 2023, EVAL | 已核验，P10 | object/motion representations + location-dependent scene model | 支持 context/location 不能简单删除 | single-scene model；非 cross-scene residual |
| Cao et al. 2023, NWPU Campus | 已核验，P11 | scene-dependent anomalies、43 scenes、scene-conditioned AE | 支持 controlled context path 与 scene-dependent stratification | Tier B；首轮不下载；不是 scene-invariant |
| Ramachandra and Jones 2020, Street Scene | 已核验，P12 | location anomalies、RBDC/TBDC / event-spatial protocol | 支持 low-FPR/location/evaluation track | 单场景；不覆盖 SRN mechanism |

## 2. 必查 prior work 类别：第一轮状态

| 类别 | 第一轮状态 | 对 SRN 的当前动作 |
|---|---|---|
| one-class / normal-only VAD | 已有 HSC、Few-shot Scene-adaptive、Rashidi、Ristea、NWPU 等支撑边界 | 保持 normal-only claim，但区分 pseudo-anomaly / weakly supervised / target adaptation |
| cross-dataset VAD | Rashidi、zxVAD、Appearance Blur + Motion-guided Memory 已核验 | 不 claim setting novelty；必须用 source→target matrix 和 fixed threshold |
| scene-invariant / scene-disentangled VAD | 未发现 direct residualization；HSC/NWPU/EVAL 多为 scene-aware/context family | SRN 表述为 selective suppression，而非 full invariance |
| domain generalization for anomaly detection | zxVAD、Action Hints、Few-shot Scene-adaptive 构成问题设定近邻 | ELOS 仅为 training/validation principle |
| feature disentanglement / nuisance removal | VAD 内未发现 `scene token→û→r` direct source；appearance-motion family 为机制邻居 | 第二轮继续查非 VAD residualization / domain nuisance |
| object-centric VAD | EVAL 已核验 | object/location 只作 baseline/diagnostic，不进首轮 restricted bridge |
| memory / prototype VAD | Rashidi kNN/Mahalanobis、MAMC、motion-guided memory 已覆盖 | prototype/memory 是 baseline/head，不是贡献 |
| conditional motion prediction | MAMC/AMSRC/Action Hints references 已显示 AMCN 风险 | AMCN 保留 backup；不得进入首轮 |
| threshold transfer / calibration | Rashidi 支持 FA/hour 与 cross-dataset threshold failure；EVT/conformal 尚未细查 | calibration 仍是 evaluation/supporting track |
| low-FPR / false-alarm VAD evaluation | Rashidi + Street Scene 支持 | 主指标保留 low-FPR、FA/hour、macro/worst-target |

## 3. reviewer seed 修订

以下条目不应直接进入 bibliography，除非后续核验：

- `DIRT` / `SDG-net` / domain-adversarial video feature decomposition：仍为 `TODO: verify`。
- “Domain-Invariant Feature Learning for Video Anomaly Detection”, MVA 2023：仍为 `TODO: verify`。
- “Disentangled Representations for Domain-General Video Anomaly Detection”, CVPRW 2024：仍为 `TODO: verify`。
- “Learning Conditional Motion Priors for VAD”, ICCV 2023：仍为 `TODO: verify`。
- Meta-AD, TNNLS 2023：仍为 `TODO: verify`。
- DeepCrowd / scene-gated normality head：仍为 `TODO: verify`。

以下条目建议替换或澄清：

- “Few-Shot Scene-Adaptive Anomaly Detection, ICLR 2022” 应改为 Lu et al., ECCV 2020 spotlight / arXiv 2007.07843。
- “MAC / Motion-Appearance Co-Memory, AAAI 2023” 未核验为 VAD；建议改为 MAMC / AMSRC / Appearance Blur + Motion-guided Memory family。
- “MocoDAD” 第一轮只通过 Action Hints related work 间接确认，应继续核验原文。

## 4. 候选修订后的冻结影响

- **SRN：** 第一轮未发现 direct coverage，可继续作为 conditional main candidate；但 contribution 必须收缩为 `selective scene-predictable residualization + controlled context retention + fixed-threshold transfer diagnostics`。
- **ELOS：** 不能作为 standalone novelty；只能是 held-out scene training / validation principle。
- **AMCN：** appearance-motion / motion memory family 已经很拥挤，继续作为 backup，不进入首轮 restricted bridge。
- **calibration：** Rashidi 已覆盖 cross-dataset audit 与 FA/hour 动机；calibration 只能作为 evaluation/supporting track。

## 5. 第一轮候选结论

第一轮查新没有发现 A 类 direct coverage，因此当前 preliminary verdict 为：

**`NOVELTY PLAUSIBLE`**

但该结论带有以下限制：

- 不能声称 SRN 首次提出 cross-domain / zero-shot VAD；
- 不能声称 ELOS 是新颖主贡献；
- 不能声称 simple scene/domain invariance 足够；
- 必须继续核验非 VAD residualization、domain-invariant one-class learning、MoCoDAD / skeleton diffusion、Ada-VAD / cross-domain VAD references。
