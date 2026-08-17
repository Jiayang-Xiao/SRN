# Score Calibration and Threshold Transfer Under Domain Shift

**Updated:** 2026-08-17
**Sources:** official CVF/NeurIPS/AAAI/PMLR/MERL pages, arXiv, local repository
(no matching local PDFs)

## Field map

| Theme | Canonical pages | Current implication |
|---|---|---|
| zero-shot cross-domain VAD | `paper:aich2023_crossdomain_video_anomaly` | VAD generalization exists, but source-fixed FPR is not the central evaluation |
| multi-domain VAD | `paper:cho2024_towards_multidomain_learning` | suitable future infrastructure, though its task includes abnormal training data |
| representation invariance | `paper:carvalho2023_invariant_anomaly_detection` | closest to feature-level SRN, not score-level calibration |
| source-only score normalization | `paper:wilkinghoff2025_local_densitybased_anomaly` | generic method novelty is unavailable; direct cross-modal competitor |
| threshold-transfer audit | `paper:zhou2026_when_eer_hides` | directly supports separating ranking from deployed-threshold reliability |
| target-mixture adaptation | `paper:perini2022_transferring_contamination_factor` | must not be called strict zero-shot |
| conformal shift/FPR control | `paper:tibshirani2019_conformal_prediction_under`, `paper:zhang2025_conformal_anomaly_detection` | guarantees require explicit exchangeability/shift assumptions or target information |

## Open gaps

- Authoritative normal-only multi-scene VAD evaluation with a final unseen scene.
- Reporting source-fixed target-normal FPR, anomaly recall, and false alarms/hour beside
  ranking metrics.
- A source-only normalizer that beats simple controls without discarding anomaly recall.
- Calibration-budget curves that use only predeclared target-normal videos and never the
  final target test distribution.

## Sprint outcome

The frozen Ped2↔Avenue stress test rejected the minimal source-only conditional normalizer:
all source-only variants retained target-normal FPR 1.0. Target-normal affine/quantile
controls reduced FPR but generally collapsed recall. This is negative exact-protocol
evidence, not unseen-scene evidence, and it does not establish a new algorithm.

## Follow-up reading

- Read the full local-density normalization paper before designing any new score-level
  method; its official implementation is especially relevant.
- Search later VAD work for deployed operating-point metrics rather than AUC-only tables.
- Revisit conformal approaches only when the target-information and shift assumptions can
  be stated and tested precisely.
