# Prior Work Patch Verified Draft V2

**日期：** 2026-07-14  
**来源：** Round 1 + Round 2 prior work verification  
**状态：** 候选修订稿；不替换 `PRIOR_WORK_PATCH.md`。

## 1. Round 2 后已核验覆盖

| Paper / method | 核验状态 | 支持的作用 | 对 SRN 的影响 | 限制 |
|---|---|---|---|---|
| Rashidi 2026, cross-dataset audit | 已核验 | frozen features + kNN/Mahalanobis cross-dataset collapse；FA/hour reliability | SRN 不能 claim audit/protocol novelty | 不提出 residual method |
| Background-Agnostic AED | 已核验 | object-level background-agnostic normal-only VAD；cross-database evaluation；adversarial pseudo-abnormal training | 强 baseline / problem-setting threat | 无 `scene token -> predicted component -> subtraction`；context mostly removed |
| HSC CVPR 2023 | 已核验 | scene-aware foreground/background semantics and contrast | 支持 context-retention risk | scene-aware, not residualization |
| zxVAD | 已核验 | cross-domain VAD without target adaptation | SRN 不得 claim cross-domain setting novelty | pseudo-abnormal synthesis; no M4/M5 |
| Few-shot Scene-adaptive AD | 已核验 | unseen-scene target support; meta-learning | ELOS prior / adaptation boundary | uses target frames; not strict zero-shot |
| Meta Prototype Network | 已核验 | few-shot normalcy learner; fast adaptation to new scenes | ELOS/meta-learning prior | target adaptation; no SRN residual |
| STG-NF / DA-Flow | 已核验 | skeleton-based VAD removes background/appearance nuisance | skeleton scene-removal baseline | skeleton input is not learned residualization |
| MoCoDAD | 已核验 | motion-conditioned diffusion in skeleton VAD | AMCN/skeleton threat | no scene residualization |
| Action Hints | 已核验 | generalizable skeleton VAD; context uniqueness | strong deployment-goal neighbor | not normal-only SRN; no M4/M5 |
| InCTRL | 已核验 non-VAD | in-context residual learning on frozen CLIP | generic residual AD threat | image AD; target normal prompts; not scene-predictable subtraction |
| ADShift / GNL | 已核验 non-VAD | distribution-invariant normality under shifts | domain-invariance prior | no explicit subtraction |

## 2. Reviewer Seed Cleanup

The following should not be used as paper names unless a primary source is later found:

- `DIRT` for VAD；
- `SDG-Net` for VAD；
- “Domain-Invariant Feature Learning for Video Anomaly Detection”；
- “Disentangled Representations for Domain-General Video Anomaly Detection”；
- “Learning Scene-Invariant Normalcy for Video Anomaly Detection”；
- “Deep Scene Decomposition for Unsupervised Anomaly Detection”；
- “Memory-Augmented Meta-Learning for Video Anomaly Detection”。

Use verified replacements:

- Few-shot Scene-adaptive AD；
- Learning Normal Dynamics in Videos with Meta Prototype Network；
- STG-NF；
- MoCoDAD；
- DA-Flow；
- Background-Agnostic AED；
- InCTRL；
- ADShift/GNL。

## 3. Mechanism-Gate Outcome

No verified VAD prior currently covers M3-M6:

- M3 explicit scene/domain/context representation；
- M4 predictor of scene/domain/nuisance component；
- M5 explicit subtraction / residualization；
- M6 controlled context-retention path。

The strongest VAD priors remove or avoid scene/background by using objects or skeletons, or learn scene-aware semantics, or adapt to target scenes. These are important controls but not direct SRN coverage.

## 4. Updated Role Decisions

- **SRN：** remains conditional main candidate; novelty plausible after Round 2, but contribution must be narrow.
- **ELOS：** not novel; only source held-out scene validation / training principle.
- **AMCN：** still backup; MoCoDAD/MAMC/AMSRC make this path risky.
- **calibration / reliability：** evaluation track only.
- **object/skeleton abstraction：** baseline / competing family, not SRN mechanism.

## 5. V2 Candidate Verdict

**Novelty verdict：`NOVELTY PLAUSIBLE`**  
**Operational decision：`READY TO REQUEST RESTRICTED BRIDGE`**

This is not authorization to run experiments. It only means prior-work gate is sufficiently closed to ask the user whether to authorize a restricted bridge.

## 6. Required Claim Language

Acceptable:

- “SRN tests whether selective scene-predictable residualization improves source-only threshold transfer over raw, mean/background subtraction and adversarial invariance baselines.”
- “ELOS is used as a training/validation principle.”
- “Skeleton/object methods are strong alternative ways to avoid background leakage.”

Not acceptable:

- “SRN introduces cross-domain VAD.”
- “ELOS is a novel contribution.”
- “SRN is the first scene-invariant VAD.”
- “Residual learning is new.”
- “Protocol metrics are a method contribution.”
