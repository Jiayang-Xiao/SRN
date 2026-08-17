# Track B Calibration Report

**Primary status:** `NO_CALIBRATION_ADVANTAGE`
**Decision time:** 2026-08-17 +0800
**Integrity:** PASS after independent repair verification
**Evidence scope:** exact Ped2→Avenue and Avenue→Ped2 cross-dataset stress protocol;
not multi-source unseen-scene evidence

## Research question and information regimes

Track B tests whether a detector can preserve a usable source-derived operating point when
normal-score scale shifts. B-ZS uses source-normal data only. B-CAL may use cumulative,
predeclared sets of 1, 2, or 4 target-normal training videos and is always labeled
adaptation. Neither branch uses target anomalies or final target test-score statistics for
fitting, selection, normalization, or threshold derivation.

The shared immutable DINOv2 ViT-S/14 parent catalog has SHA-256
`9d048d0fadeb9dd19393e1f04a507d6292c70abcf743e50a7b46093c6807cfd1`.
Whole videos are disjoint. Final labels are official Ped2/Avenue masks and enter only
`evaluate_scores`.

## Implemented methods

- B0: pooled source-validation q99.
- B1: source mean/std affine invariance control.
- B2: source median/MAD affine invariance control.
- B3: median of per-source-video q99 thresholds.
- B4: eight-coordinate PCA context plus ridge conditional location prediction on
  `log1p(raw_score)`, selected with leave-one-whole-source-video-out normal FPR error.
- B-CAL: target-normal q99, mean/std, median/MAD, and fixed empirical-CDF mappings at
  budgets 1, 2, and 4.

Scorers are 5-NN, shrinkage-0.1 Gaussian/Mahalanobis, and 32-prototype distance.
Prototype seeds are 13, 29, and 43; deterministic methods run once. Gates average
stochastic seeds within each direction-by-scorer cell, then weight the six cells equally.

## Validation

- 15 tests pass and all Python files compile.
- Every recomputed raw score array matches its historical NPZ counterpart within
  `rtol=atol=1e-8`.
- Historical AUROC/probe/FPR values recompute within the declared tolerance.
- Final output contains 170 run rows and 17 raw-run aggregates.
- A fresh reviewer independently recomputed all 170 rows and both aggregation tables with
  zero mismatches.
- B-CAL NPZ artifacts retain the exact target-normal calibration scores and video IDs.
- False-alarm events/hour means contiguous false-positive runs divided by total
  represented test-video duration.

## Strict source-only results

Seed-balanced direction-by-scorer summaries:

| Method | Median target-normal FPR | Worst FPR | Median recall | Median AUROC | Median FA / total video hour | Gate |
|---|---:|---:|---:|---:|---:|---|
| B0 pooled q99 | 1.0000 | 1.0000 | 1.0000 | 0.4556 | 321.25 | fail |
| B1 source mean/std | 1.0000 | 1.0000 | 1.0000 | 0.4556 | 321.25 | fail |
| B2 source median/MAD | 1.0000 | 1.0000 | 1.0000 | 0.4556 | 321.25 | fail |
| B3 video-balanced q99 | 1.0000 | 1.0000 | 1.0000 | 0.4556 | 321.25 | fail |
| B4 conditional location | 1.0000 | 1.0000 | 1.0000 | 0.3787 | 321.25 | fail |

B1/B2 are expected to preserve decisions because the same monotone affine map is applied
to source scores, test scores, and threshold. B3 changes the raw threshold but cannot
bridge the dataset-scale gap. B4 selects alpha 0.001 in all ten raw runs, leaves FPR
saturated, and degrades seed-balanced median AUROC from 0.4556 to 0.3787; it is discarded.

**Observation:** all source-only thresholds flag every target-normal frame.
**Interpretation:** none of the tested source-only mappings predicts the target score
scale. Recall 1.0 is meaningless because specificity is zero.
**Implication:** the strict source-only positive claim is rejected.
**Next step:** do not tune this minimal family on the same Ped2/Avenue labels.

**Evidence label:** exact-protocol scientific evidence for two cross-dataset directions.

## Target-normal calibration-budget results

Seed-balanced summaries show the central tradeoff:

| Method | Budget | Median FPR | Worst FPR | Median recall | Median FA / total video hour |
|---|---:|---:|---:|---:|---:|
| target q99 | 1 | 0.01873 | 0.24862 | 0.01845 | 350.43 |
| mean/std | 1 | 0.00230 | 0.03867 | 0.00748 | 14.93 |
| median/MAD | 1 | 0.00000 | 0.02210 | 0.00061 | 0.00 |
| empirical CDF | 1 | 0.01860 | 0.19337 | 0.01845 | 350.43 |
| target q99 | 4 | 0.00092 | 0.00276 | 0.00623 | 5.97 |
| mean/std | 4 | 0.00000 | 0.00276 | 0.00425 | 0.00 |
| median/MAD | 4 | 0.00000 | 0.00000 | 0.00000 | 0.00 |
| empirical CDF | 4 | 0.00000 | 0.00276 | 0.00492 | 0.00 |

All four methods miss the frozen 0.05 median-recall gate at four videos. The apparent FPR
repair is over-conservative: in Ped2→Avenue, most calibrated operating points make almost
no detections. Some Avenue→Ped2 scorer cells retain more recall, but the effect is neither
cross-direction stable nor a passing aggregate result.

False-alarm event rate is not monotone in frame FPR: a small number of isolated false
positives can form more events than a single long saturated false-positive run. For
example, one-video target-q99 calibration has lower median frame FPR than B0 but higher
median events/hour. Both quantities are therefore retained.

**Observation:** limited target-normal data can move numerical FPR close to or below 1%.
**Interpretation:** the tested estimators overshoot into an excessively conservative
threshold because calibration-normal and final-test score distributions still differ.
**Implication:** claim support is partial for FPR repair only; no usable calibration
advantage is demonstrated.
**Next step:** any new method must predeclare a joint FPR/recall criterion and be tested
on genuinely unseen scenes, not tuned on these final labels.

**Evidence label:** exact-protocol target-normal adaptation evidence, never zero-shot.

## Ranking versus operating-point reliability

Raw scorer AUROC is asymmetric: seed-balanced cells range from 0.3567 to 0.6929 with
median 0.4556. Thus this stress test does not even show uniformly useful ranking. The
monotone B-CAL mappings preserve raw ranking (empirical-CDF ties cause only negligible
differences), while B4 changes and worsens it. Ranking quality and deployed-threshold
behavior are reported separately throughout.

## Prior work and novelty

The focused primary-source audit found direct adjacent precedent. WACV 2023 studies
zero-shot cross-domain VAD; NeurIPS 2024 studies multi-domain VAD; anomalous-sound work
explicitly normalizes score distributions for a single cross-domain threshold; and a 2026
speech-deepfake audit explicitly shows that oracle ranking can hide threshold failure.
Conformal and contamination-transfer work additionally demonstrates that many guarantees
or corrections require target covariates or the unlabeled target score mixture.

**Novelty decision:** no broad calibration-method novelty claim is authorized. The
defensible contribution is a narrow, reproducible negative VAD operating-point audit.

## Statistical scope

Prototype seeds are averaged before scorer/direction aggregation. Deterministic methods
are not duplicated. With only two target datasets, the tables are descriptive; frames are
not treated as IID replicates and no population-level confidence interval or unseen-scene
generalization claim is made.

## Invalidated attempts

Two reporting attempts are preserved rather than erased:

1. a complete scoring pass failed when a NumPy boolean was serialized to JSON;
2. a later aggregate file inverted the meaning of the `worst` FPR column.

The final run regenerates every output, passes assertions, and is the only accepted
artifact set. Details are machine-readable in
`analysis/track_b/invalidated_runs.json`.

## Independent review

The initial read-only audit returned `WARN` for seed weighting, unretained diagnostics,
FA/hour definition, and absent calibration samples in B-CAL artifacts. All four were
repaired and the regenerated follow-up verdict is `PASS`. A separate result-to-claim
review judges B-ZS support `no`, B-CAL support `partial` only for FPR repair, and
confirms `NO_CALIBRATION_ADVANTAGE`.

Both completed reviewers are fresh GPT-family threads (Type-A). A configured DeepSeek
cross-family call was attempted with raw primary artifacts but cancelled by the runtime;
no Type-B cross-family acquittal is claimed.

## Supported and unsupported claims

- **Engineering validation:** leakage guards, cache provenance, historical score
  reproduction, calibration artifact retention, and metric recomputation pass.
- **Exact-protocol scientific evidence:** the tested source-only methods do not improve
  transferred thresholds; limited target-normal calibration lowers FPR but fails the
  recall gate.
- **Unseen-scene evidence:** unavailable.
- **Supported:** ranking and operating reliability can differ; B-CAL is adaptation; the
  minimal learned model offers no advantage here.
- **Unsupported:** calibration is generally impossible; target-normal calibration is
  useless in all settings; the result generalizes to arbitrary cameras; the method is
  novel; a positive paper claim.
- **Speculation:** calibration-normal/test-normal drift, not anomaly-scale overlap alone,
  causes the over-conservative budget curve. New data are needed to test this mechanism.

## Paper decision

No separate positive Track B paper is scientifically justified. The existing SRN
falsification paper remains unchanged. The new outputs form a rigorous negative research
report and do not warrant new XeLaTeX claims or tables.

## Reproducibility artifacts

- `TRACK_B_PROTOCOL_FREEZE.md`
- `analysis/track_b/results_long.csv`
- `analysis/track_b/seed_balanced_cells.csv`
- `analysis/track_b/seed_balanced_summary.csv`
- `analysis/track_b/summary.json`
- `analysis/track_b/provenance.json`
- `analysis/track_b/scores/`
- `analysis/track_b/operating_point_reliability.{png,pdf}`
- `analysis/track_b/calibration_budget_curve.{png,pdf}`
- `scripts/run_score_calibration_study.py`
- `scripts/analyze_score_calibration.py`
- `src/restricted_bridge/calibration.py`
- `tests/test_score_calibration.py`

Final accepted hashes:

- `results_long.csv`: `a2a5baa927a4618bbcef54f789bc9768e8d96771745a8f400ce9e5964906a1d1`
- `results_aggregate.csv`: `24fb850ac34f72ae53a8e807dd3cbe7c80e42bc6fac8cea6dd68decfb826f256`
- `summary.json`: `d421eb617b78c0550ce1f525a0b8c54b4676d0f87ae12a91a1d7afc49a63ea01`
- `provenance.json`: `16199f0c163155a47790f28caeda8dc65c8eadcf2a232be728e0322a03a46b2d`
