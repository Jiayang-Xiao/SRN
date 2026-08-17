# SRN Autonomous Results Analysis

All values below are generated from saved `results.json` and per-run `scores.npz` 
artifacts. The confidence interval is a 500-replicate hierarchical bootstrap over 
test videos and, where applicable, seeds. It is descriptive because there are only 
two seen domains.

## Raw main comparison

| Method | Seeds | AUROC | 95% video-bootstrap CI | AUPRC | TPR@1% | TPR@0.1% | Source-threshold recall | Test FPR | Scene probe |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| raw_gaussian | 1 | 0.6885 | [0.5927, 0.7994] | 0.5536 | 0.1082 | 0.0524 | 0.4282 | 0.1686 | 1.000 |
| raw_knn | 1 | 0.6723 | [0.5697, 0.7813] | 0.5025 | 0.0877 | 0.0321 | 0.4955 | 0.2224 | 1.000 |
| full_srn | 3 | 0.6677 | [0.6066, 0.7246] | 0.5014 | 0.0880 | 0.0358 | 0.4590 | 0.2054 | 1.000 |
| srn_residual_only | 3 | 0.6665 | [0.6037, 0.7253] | 0.5020 | 0.0838 | 0.0348 | 0.4620 | 0.2050 | 1.000 |
| scene_mean_prototype | 3 | 0.6658 | [0.6028, 0.7240] | 0.4985 | 0.0832 | 0.0360 | 0.4886 | 0.2201 | 0.283 |
| adversarial_residual | 3 | 0.6657 | [0.6033, 0.7247] | 0.5001 | 0.0854 | 0.0356 | 0.4616 | 0.2056 | 1.000 |
| srn_without_elos | 3 | 0.6657 | [0.6034, 0.7243] | 0.4992 | 0.0864 | 0.0369 | 0.4591 | 0.2045 | 1.000 |
| elos_without_srn | 3 | 0.6653 | [0.6030, 0.7242] | 0.5001 | 0.0857 | 0.0361 | 0.4611 | 0.2058 | 1.000 |
| raw_prototype | 3 | 0.6653 | [0.6030, 0.7242] | 0.5001 | 0.0857 | 0.0361 | 0.4611 | 0.2058 | 1.000 |

## Key findings

1. **Observation:** raw Gaussian is the strongest joint seen-domain method (AUROC 0.6885); full SRN reaches 0.6677.
   **Interpretation:** the learned residual is not competitive with a strong raw-feature scorer.
   **Implication:** there is no current evidence for an SRN method advantage.
   **Next step:** do not expand architecture search; require genuine multi-scene data before reconsideration.

2. **Observation:** full SRN improves over the matched raw prototype by only +0.0024 AUROC, while its held-video scene probe remains 1.000; scene mean lowers the same probe to 0.283.
   **Interpretation:** the intended scene-information removal mechanism did not occur.
   **Implication:** the small matched-head delta cannot support the central causal claim.
   **Next step:** treat the current SRN mechanism as falsified, not under-tuned.

3. **Observation:** every strict cross-dataset source threshold labels every target normal frame anomalous (test FPR 1.0), while target-normal calibration often becomes overly conservative.
   **Interpretation:** the score distributions undergo a severe domain shift that rank metrics hide.
   **Implication:** fixed-threshold transfer is unsupported for all tested representations.
   **Next step:** if authoritative ShanghaiTech becomes available, evaluate a separately declared normal-only calibration/reliability hypothesis rather than relabeling it as SRN success.

## Paired full-SRN deltas versus raw prototype

| Metric | Mean delta | Std across 3 seeds |
|---|---:|---:|
| micro_auroc | +0.002439 | 0.002456 |
| auprc | +0.001272 | 0.002627 |
| tpr_at_1pct_fpr | +0.002301 | 0.002743 |
| tpr_at_0_1pct_fpr | -0.000311 | 0.001892 |

## Suggested next experiments

1. Acquire an authoritative, checksum-verifiable ShanghaiTech archive and run true scene-held-out ELOS.
2. If that remains blocked, stop SRN mechanism development in this sprint; the bounded LR diagnostic already failed to restore scene suppression.
3. A future, separately preregistered study may investigate score calibration under domain shift using normal target clips, with no zero-shot claim.

Complete raw rows: `analysis/results_long.csv`. Score-shift diagnostics: `analysis/score_distribution_shift.csv`.
