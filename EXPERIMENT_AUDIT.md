# Experiment Audit Report

**Date:** 2026-08-17  
**Auditor:** GPT-5.5 xhigh, independent post-run reviewer  
**Overall verdict:** `WARN`  
**Integrity disposition:** no run invalidated; claims limited to real-GT Ped2/Avenue pilots and two-seen-domain diagnostics.

## Summary

The official Ped2/Avenue ground truth, label-blind frozen-feature extraction, whole-video
splits, score artifacts, source-normal thresholds, target-normal calibration track, and
result row counts all passed audit. No anomaly-label leakage, test-score normalization,
failed-seed selection, missing artifact, duplicate frame identity, or frame-order FA/hour
defect remains in the formal runs.

The warning concerns scope rather than run validity. Ped2 and Avenue provide two
dataset/camera identities and the joint cache exposes both during normal training. The
results cannot support a general SRN/ELOS whole-scene claim. Avenue's official training
partition also contains project-documented outliers that were retained without label-based
filtering; it must be described as the official training split, not guaranteed anomaly-free.

## Check results

| Check | Status | Finding |
|---|---|---|
| Official GT and cache provenance | PASS | Official assets, archive hashes, split identities, catalog hash, and label/frame alignment are recorded. |
| Label use and leakage | PASS | Non-test labels are asserted zero; labels are joined after feature inference and used only for final held-out evaluation. |
| Dataset/split identity | PASS | Dataset ID is required, whole-video keys include dataset/video, and cross-split videos are disjoint. |
| Raw score integrity | PASS | kNN, Gaussian, and prototype distances use train embeddings only; no test-set rescaling was found. |
| Strict/calibrated thresholds | PASS with terminology warning | Source thresholds use source-normal validation; calibrated thresholds use declared target-normal videos. Oracle TPR@FPR uses final test negatives and is not deployable. |
| FA/hour | PASS | Frame indices are sorted and alarm runs split at gaps; regression coverage exists. |
| Independent scene probe | PASS implementation; FAIL mechanism signal | Held-video nearest-centroid probing is independent, but full SRN retains probe accuracy 1.000. |
| Predictor rank | PASS | The configured rank-8 factorization is wired into SRN and unit-tested. |
| ELOS selection | PASS implementation; WARN scope | Checkpoint selection uses source-normal episodic validation, but only two seen domains are available. |
| Seed coverage | WARN | Prototype/learned rows use three seeds; deterministic Gaussian/kNN use one run. |
| Result completeness | PASS | Expected row counts and saved per-frame score artifacts match all six formal configurations. |

## Evaluation classification

- `runs/ped2_within_raw`: real-GT within-dataset engineering sanity check.
- `runs/avenue_within_raw`: real-GT within-dataset engineering sanity check, with official-training outlier caveat.
- `runs/ped2_to_avenue_raw` and `runs/avenue_to_ped2_raw`: real-GT single-source cross-dataset baseline pilots; not SRN/ELOS evidence.
- `runs/ped2_avenue_joint_seen_mechanism`: real-GT two-seen-domain mechanism diagnostic; not unseen-scene evidence.
- `runs/ped2_avenue_joint_lr_diagnostic`: bounded optimization diagnostic on the same joint-seen cache.
- Historical synthetic dry-run: simulation-only and excluded from scientific claims.

## Claim disposition

- SRN improves anomaly detection: **unsupported**; AUROC 0.6677 versus raw Gaussian 0.6885 and only +0.0024 versus matched raw prototype.
- SRN removes dataset/camera identity: **contradicted for the tested module**; residual probe remains 1.000.
- Fixed source-threshold transfer works: **contradicted**; cross-dataset target-normal FPR is 1.0 in both directions for all raw scorers.
- Whole-scene ELOS generalization: **not tested**; authoritative multi-scene data remain unavailable.

The formal evidence is valid for this bounded negative-result paper. It is not valid for a
positive SRN method claim, a robust best-baseline claim over deterministic one-run scorers,
or an unseen-scene ELOS claim.
