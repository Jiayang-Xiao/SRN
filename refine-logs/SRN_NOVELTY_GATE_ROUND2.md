# SRN Novelty Gate Round 2

**日期：** 2026-07-14  
**状态：** Round 2 高风险线索关闭记录；不授权实验。

## 1. Direct Coverage

**结论：未发现 direct coverage。**

Round 2 没有核验到任何 VAD 论文同时覆盖 normal-only VAD、explicit scene/domain/context representation、predictor of scene/domain/nuisance component、explicit subtraction / residualization `z - u_hat`、controlled context-retention path、normality modeling 和 unseen-scene/source-only generalization。

因此未触发 `NOVELTY COLLAPSED`。

## 2. Strongest Verified Threats

| Rank | Threat | Why dangerous | Why not direct coverage |
|---|---|---|---|
| 1 | Background-Agnostic AED | normal-only, object-level, background-agnostic, cross-database VAD | object/foreground abstraction + pseudo-abnormal adversarial training；no predicted nuisance subtraction；context mostly removed rather than controlled retained |
| 2 | STG-NF / DA-Flow / Action Hints skeleton VAD | strong scene/background removal by skeleton modality; zero-shot/generalizable evidence | skeleton input is not learned scene residualization; no `c -> u_hat -> z-u_hat` |
| 3 | Few-shot Scene-adaptive AD / Meta Prototype Network | ELOS/meta-learning prior; unseen-scene adaptation | uses target support/adaptation; no M3-M6 |
| 4 | InCTRL | non-VAD residual learning with frozen CLIP and normal prompts | image/generalist AD; target normal prompts; residual is query-normal prompt discrepancy, not scene component subtraction |
| 5 | ADShift / invariant AD | non-VAD distribution-invariant normality under shifts | invariance/regularization, no explicit predicted subtraction or controlled context |

## 3. Strongest Non-VAD Mechanism Threat

**InCTRL** is the strongest non-VAD residual threat. It demonstrates that residual learning over frozen CLIP features and normal prompts is a real AD idea. SRN therefore cannot claim generic residual-learning novelty.

However, InCTRL does not estimate a scene/domain component from a low-capacity context token and subtract it from a video representation. It also uses few-shot target normal prompts at inference. Its threat level is `D. Mechanism-only neighbor`, not direct coverage.

## 4. ELOS Prior Status

**ELOS has prior and is not novel as a contribution.**

Verified prior:

- Few-shot Scene-adaptive AD；
- Learning Normal Dynamics in Videos with Meta Prototype Network；
- general meta-learning / few-shot adaptation framing.

ELOS must remain a training/validation principle. It may be useful for SRN model selection and held-out source-scene diagnostics, but it cannot be claimed as a standalone contribution.

## 5. Protocol Novelty Status

Fixed source-threshold transfer, low-FPR, FA/hour, macro/worst-target and RBDC/TBDC are evaluation requirements or protocol discipline. They are important for reliability, but cannot be framed as method novelty.

## 6. SRN Minimal Contribution That Remains

SRN may still be defensible only as:

> A selective scene-predictable residualization interface for frozen-feature normal-only VAD, which explicitly predicts and subtracts a scene/domain-predictable component while retaining a controlled low-capacity context path, then evaluates whether this improves source-only threshold transfer and low-FPR reliability over raw, mean/background subtraction, adversarial invariance and skeleton/object abstraction baselines.

## 7. Claims That Must Be Deleted or Avoided

- “first cross-domain / zero-shot VAD setting”；
- “ELOS is a novel method contribution”；
- “scene invariance alone solves generalization”；
- “skeleton/background removal is equivalent to SRN”；
- “low-FPR / FA/hour metric is a method contribution”；
- “generic residual learning is new”；
- “SRN is ready for full experiment-bridge”。

## 8. Required Baselines Before Any Claim

If later restricted bridge is authorized, SRN must be compared against raw frozen feature + kNN / Mahalanobis, prototype / memory bank, scene mean subtraction, background / object-level abstraction where computable, adversarial residual / GRL, MMD/HSIC or equivalent invariance penalty if feasible, SRN without context, SRN without ELOS, ELOS without SRN, source-threshold transfer and target-normal calibration split, and low-FPR / FA-hour / macro / worst-target metrics.

## 9. Novelty Verdict

**`NOVELTY PLAUSIBLE`**

This is not “safe novelty”. It means Round 2 did not find M3-M6 direct coverage, and the remaining threats are partial, protocol, or non-VAD mechanism neighbors.

## 10. Operational Recommendation

**`READY TO REQUEST RESTRICTED BRIDGE`**

This does not start any experiment. Current execution remains:

- execution：`HOLD`
- restricted bridge：`not started`
- data download：not authorized
- GPU / feature extraction / training：not authorized

The recommended next user decision is whether to authorize a restricted bridge limited to frozen-feature audit + minimal SRN-vs-adversarial pilot.
