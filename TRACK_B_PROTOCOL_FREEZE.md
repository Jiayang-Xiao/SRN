# Track B Protocol Freeze

**Frozen:** 2026-08-17 21:13 +0800, before executing any new calibration method
**Scientific track:** score-level operating-point transfer under normal-only shift

**Post-run audit clarification (2026-08-17 22:03 +0800):** the original freeze declared
seeds, directions, and scorer families but did not state whether three prototype seeds
should receive three times the weight of deterministic scorers. A fresh reviewer flagged
that ambiguity. Final gates therefore average stochastic seeds first and weight each
direction-by-scorer cell equally. Both the original row-weighted and corrected
seed-balanced calculations give `NO_CALIBRATION_ADVANTAGE`; no method, label access, or
numeric gate was changed. The FA/hour denominator was also documented explicitly after
review; its computation did not change.

## Data and claim scope

The immutable DINOv2 ViT-S/14 caches are:

- Ped2 to Avenue: `data/frozen_features/dinov2_vits14/experiments/ped2_to_avenue.npz`
- Avenue to Ped2: `data/frozen_features/dinov2_vits14/experiments/avenue_to_ped2.npz`
- parent catalog SHA-256: `9d048d0fadeb9dd19393e1f04a507d6292c70abcf743e50a7b46093c6807cfd1`

These are two cross-dataset stress tests, not multi-source unseen-scene evidence. The
source train and source validation partitions contain official training videos only.
Target calibration contains the first four sorted official normal training videos.
Final test contains the complete official labeled test partition. Whole videos are
disjoint. Test labels are supplied only to the final metric function.

Primary scorers share the same raw cache: 5-NN mean squared distance, shrinkage-0.1
Gaussian/Mahalanobis distance, and 32-prototype distance. Prototype seeds are 13, 29,
and 43; deterministic methods run once.

## B-ZS: strict source-only methods

No target features, score statistics, calibration videos, test-score distribution, or
target labels may enter fitting, selection, normalization, or threshold derivation.
Desired normal FPR is 0.01.

- **B0 pooled quantile:** pooled source-validation q99 threshold.
- **B1 mean/std:** source-validation affine standardization with the correspondingly
  transformed source q99 threshold. This is retained as an explicit invariance control.
- **B2 median/MAD:** source-validation robust affine standardization (MAD scaled by
  1.4826, epsilon floor) with the correspondingly transformed q99 threshold.
- **B3 video-balanced threshold:** median of the per-source-validation-video q99 raw
  thresholds. It is the only simple source-only control expected to differ from B0.
- **B4 conditional-location residual:** a deliberately low-capacity source-only model.
  It predicts `log1p(raw_score)` from an intercept plus eight PCA context coordinates of
  the frozen feature. PCA and ridge regression are fit only on source-normal validation
  videos. Ridge alpha is selected from `[0.001, 0.01, 0.1, 1, 10]` by leave-one-video-out
  mean absolute q99-FPR error on the held source video. The deployable model is refit on
  all source-validation videos. Its source threshold is the q99 of cross-fitted residuals;
  no target statistic is used. The global source residual MAD is an affine numerical
  scale only and cannot be target-fitted.

B4 is discarded if it does not beat the best simple source-only control on the frozen
operating-point metrics. No extra architecture or hyperparameter search is allowed.

## B-CAL: declared target-normal calibration

This track is adaptation, never zero-shot. Sorted target-normal calibration videos define
budgets of 1, 2, and 4 videos; `all` is identical to 4 in these caches. No final test
score contributes to a mapping. For each budget/scorer compare:

- target-normal q99 threshold (quantile recalibration);
- target mean/std mapped to source mean/std, with the frozen source threshold;
- target median/MAD mapped to source median/MAD, with the frozen source threshold;
- fixed empirical target-CDF to source-quantile mapping, estimated only from calibration
  scores, with the frozen source threshold.

Ties and extrapolation behavior are deterministic. Calibration videos are cumulative in
sorted video-ID order. Hyperparameters are not changed after final labels are read.

## Metrics and gates

Primary metrics are target-normal FPR, absolute error from 0.01 FPR, anomaly recall at
the frozen threshold, false-alarm events/hour, normal q95/q99 transfer ratios, worst
direction FPR, and cross-direction FPR variance. Secondary metrics are AUROC, AUPRC, and
oracle TPR@1%/0.1% FPR. Ranking and operating reliability are reported separately.
False-alarm events/hour uses the total represented test-video duration as denominator;
events themselves are contiguous false-positive runs on normal frames. Stochastic seeds
are averaged first, then direction-by-scorer cells are weighted equally for gates.

`PROMISING_SOURCE_ONLY_CALIBRATION` requires, across both directions: median absolute FPR
error at least 0.50 lower than B0, worst-direction FPR no greater than 0.25, median anomaly
recall at least 0.05, controlled FPR variance, and no target information. The already-known
B0 stress-test result is FPR 1.0 in every run, so its cross-run variance is exactly zero:
a literal variance reduction is mathematically impossible despite total operating-point
failure. Before running any new method, the variance gate is therefore fixed as variance
no greater than 0.0025 together with the worst-FPR gate; this prevents saturation from
being rewarded while preserving a tight stability requirement. B4 must additionally
beat B3 or it is discarded.

`PROMISING_TARGET_NORMAL_CALIBRATION_ONLY` requires a monotone budget curve in aggregate,
median FPR no greater than 0.10 with one normal video and no greater than 0.05 with four,
at least 0.50 median absolute-error reduction from B0, and median anomaly recall at least
0.05 at a qualifying budget. If FPR is repaired only by eliminating essentially all
recall, the gate fails.

Confidence statements use videos, directions, and stochastic seeds as units; frames are
not treated as IID replicates. With only two target datasets, intervals are descriptive
and no population-level unseen-scene claim is permitted.
