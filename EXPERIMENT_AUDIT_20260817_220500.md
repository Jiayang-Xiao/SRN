# Experiment Audit Report

**Date:** 2026-08-17
**Auditor:** fresh GPT-5.5 xhigh reviewer thread, read-only
**Review type:** Type-A same-family independent review; configured DeepSeek cross-family
call was cancelled by the runtime
**Project:** SRN dual-track calibration sprint

## Overall Verdict: PASS

## Integrity Status: pass

The first audit returned `WARN` for four reporting/provenance issues. Those issues were
repaired without changing methods, labels, or final test access, the artifacts were fully
regenerated, and the same reviewer returned `PASS` on the targeted follow-up.

## Checks

### A. Ground Truth Provenance: PASS

Ped2 and Avenue labels originate from the official masks documented in
`refine-logs/DATA_AND_FEATURE_PROVENANCE.md`. Active configs load immutable NPZ
features, test metrics consume `data.label[test_index]`, and the loader rejects anomaly
labels outside the final test split.

### B. Score Normalization and Hidden Test Fitting: PASS

B-ZS fitting, normalization, and thresholds use source-normal train/validation data only.
B-CAL uses only the cumulative predeclared target-normal calibration videos. Neither
branch uses final target test-score statistics or target anomaly labels for fitting,
selection, mapping, or threshold derivation. Raw/source/test scores and thresholds are
retained in per-method NPZ files.

### C. Result Existence and Numeric Consistency: PASS

The auditor independently recomputed all 170 NPZ-backed result rows with zero mismatches
for thresholds, AUROC, AUPRC, FPR, recall, false-alarm events/hour, macro-video AUROC,
quantiles, and anomaly medians. Aggregate and seed-balanced tables reproduce exactly from
`results_long.csv`. Historical result recomputation also passes.

### D. Dead Code and Retained Outputs: PASS after repair

All calibration functions are called. The runner now retains every computed scalar
diagnostic plus serialized per-scene/per-video outputs in `results_long.csv`.
The generic `grouped_auroc` convenience wrapper is not called, but its underlying
`grouped_auroc_values` implementation is exercised; this has no result impact.

### E. Scope Assessment: PASS

Claims are explicitly limited to two cross-dataset stress directions, three scorer
families, and the declared prototype seeds. The files state that this is neither
multi-source unseen-scene evidence nor a population-level result.

### F. Leakage: PASS

Whole-video isolation and absence of abnormal training/calibration labels are asserted by
the data validator and recorded in provenance. B-ZS never accesses target calibration.
B-CAL is explicitly target-normal adaptation, and test labels enter only final metrics.

### G. Statistical Units and Implementation: PASS after repair

Gate summaries now average stochastic seeds within each direction-by-scorer cell and
weight the six cells equally. False-alarm events/hour is explicitly defined per total
represented test-video hour. B-CAL NPZ artifacts now store the exact target-normal
calibration scores and video IDs.

## Invalidated attempts

Two reporting attempts remain preserved in
`analysis/track_b/invalidated_runs.json`: one NumPy-boolean serialization failure and
one inverted aggregate worst-column calculation. Neither per-run metrics nor the frozen
gate changed. Only the fully regenerated post-review artifacts are accepted.

## Claim impact

- **Supported:** Under this exact Ped2↔Avenue protocol, no tested source-only or
  target-normal calibration method passes the frozen joint FPR/recall advantage gates.
- **Supported:** B-CAL is target-normal adaptation, not zero-shot.
- **Needs qualifier:** false alarms/hour means per total represented video hour.
- **Unsupported:** comprehensive, multi-source unseen-scene, population-level, or general
  no-calibration claims.

## Reviewer limitation

The reviewer was a fresh thread that read primary artifacts directly, but it is from the
same GPT model family as the executor. A configured DeepSeek call was attempted with raw
primary artifacts and cancelled by the runtime. Therefore this report is not represented
as cross-family Type-B acquittal.
