# Current SRN Research State

**Date:** 2026-08-17
**Current state:** `AUTONOMOUS SPRINT COMPLETE / SRN MECHANISM STOP`
**Evidence status:** valid bounded Ped2/Avenue real-GT pilots; no genuine unseen-scene ELOS result.

## Direction and contribution boundary

The project studies normal-only video anomaly detection under cross-camera/domain shift and
low false-positive operation. The tested SRN mechanism predicts a low-rank scene component
from frozen features, subtracts it, and optionally restores a constrained context vector.
ELOS remains a source-normal training/model-selection principle, not a standalone method.

Historical requirements for separate human approval of ordinary downloads, environment
setup, feature extraction, experiments, plotting, and drafting were superseded by the
2026-08-17 unattended sprint authorization. Scientific freezes were not superseded:
normal-only training, whole-video separation, shared frozen features, target-information
prohibitions, fair budgets, and stop logic remain binding.

## Completed

- Acquired and checksum-verified official UCSD Ped2 and CUHK Avenue assets plus the official
  DINOv2 ViT-S/14 checkpoint.
- Extracted one immutable label-blind catalog: 35,212 frames, 384 dimensions, 65 videos.
- Built and audited five whole-video caches for within-dataset, cross-dataset, and joint
  two-seen-domain evaluation.
- Repaired dataset-identity guards, chronological/gap-aware FA/hour, chunked kNN, actual
  predictor-rank use, source-normal ELOS checkpoint selection, independent held-video
  scene probes, threshold-track naming, score artifacts, and aggregation.
- Passed 12 tests and an independent post-run integrity audit; no real run was invalidated.
- Ran six real configurations covering raw Gaussian/kNN/prototype, scene mean,
  adversarial residual, full SRN, no-ELOS, ELOS-without-SRN, residual-only, and a bounded
  learning-rate diagnostic.
- Generated machine-readable analysis, figures/tables, a research-wiki verdict node, and a
  compiled eleven-page XeLaTeX paper including appendix (main body through Conclusion on
  page 8), plus independent `PASS` claim and citation audits.

## Scientific result

- Raw Gaussian joint-seen AUROC: 0.6885; full SRN: 0.6677.
- Matched full-SRN minus raw-prototype AUROC: +0.0024 with mixed low-FPR deltas.
- Full-SRN residual dataset/camera probe: 1.000; scene-mean control: 0.283.
- Every source-normal cross-dataset threshold yields target-normal FPR 1.000 for all three
  raw scorers in both directions.
- Target-normal calibration reduces FPR but yields weak anomaly recall.

**Verdict:** `STOP` the tested low-capacity SRN mechanism claim and Tier-B scale-up. The
narrow nuisance/score-shift premise is supported; the SRN remedy is not.

## External/runtime blockers

- ShanghaiTech's authoritative current links were inaccessible and historical official
  mirrors returned no bytes. An unverified community upload was rejected. Whole-scene
  ELOS remains untested.
- CUDA device nodes were not exposed; all extraction and experiments ran on CPU.
- `.git` is read-only in this runtime. Working-tree changes are complete and inspectable,
  but local commits/fetches/pushes cannot be created here.

## Highest-value future work

Do not resume SRN tuning on the same two datasets. Reopen the mechanism only after securing
an authoritative multi-scene dataset and preregistering an unseen-scene protocol that
requires both independent identity-probe reduction and non-degraded source-fixed low-FPR
detection. A separate study may test normal-only score calibration under domain shift, but
must not relabel target-normal adaptation as zero-shot SRN success.
