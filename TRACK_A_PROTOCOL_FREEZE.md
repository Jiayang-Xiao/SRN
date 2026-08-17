# Track A Protocol Freeze

**Created:** 2026-08-17 21:13 +0800
**State:** `NOT_ACTIVATED_EXTERNAL_ASSET_BLOCKER`
**Scientific track:** feature-level scene residualization on genuinely unseen scenes

## Activation barrier

No Track A model run is permitted until an authoritative multi-scene video-anomaly
asset is locally acquired, checksum-recorded, and shown to contain normal source videos,
normal held-out-scene calibration videos, and labeled final held-out-scene videos.

The authoritative ShanghaiTech page currently has an empty Google Drive anchor; its
OneDrive share returns HTTP 403; both historical institutional mirrors time out. MSAD
raw videos require a reviewed identity-bearing request form. The official UBnormal
archive is public and protocol-compatible, but its only official download returned a
Google Drive quota-exceeded page on 2026-08-17. Community re-uploads are excluded.

Because no valid asset crossed this barrier, scene IDs, source scenes, and final held-out
scenes cannot be honestly frozen. This document freezes the no-run decision rather than
inventing a dataset-specific protocol.

## Protocol shell if the barrier is later crossed

- Whole scene IDs, never adjacent frames, define source and final holdout units.
- Held-out scenes are chosen from documented scene/video availability before anomaly
  scores or labels are inspected; no best-scene selection is allowed.
- Source-normal videos are partitioned by whole video into representation/scorer train
  and source-normal model-selection validation.
- Any target-normal calibration videos are declared separately and are unavailable to
  the strict source-only track.
- The primary backbone is the existing strict-loaded DINOv2 ViT-S/14 checkpoint and its
  fixed RGB 256-resize/224-center-crop preprocessing. A different official frozen
  representation is allowed only when raw videos are authoritatively unavailable, and
  that run must be labeled a backbone-substitution study.
- Feature shards are per-video, deterministic, resumable, SHA-256 cataloged, and joined
  to labels only after inference.
- Seeds for stochastic methods: 13, 29, 43. Deterministic scorers are run once.
- SRN dimensions: scene token 16, predictor rank 8, context 8, identity-initialized
  residual projection, capacity penalty, GRL scene suppression, source-normal
  compactness. Epoch and learning-rate budgets remain those of the current minimal
  formulation unless a correctness defect is established before evaluation.
- Matrix: raw kNN, raw Gaussian/Mahalanobis, raw prototype, scene mean, legitimate
  label-free background subtraction if available, adversarial residual, full SRN+ELOS,
  SRN without ELOS, ELOS without SRN, SRN residual-only, and a separately labeled
  target-normal calibration control.
- Metrics: micro AUROC, macro scene/video AUROC, AUPRC, TPR@1% and 0.1% oracle FPR,
  source-fixed target-normal FPR and anomaly recall, FA events/hour when FPS is known,
  worst scene, scene variance, and a train-to-disjoint-normal independent identity probe.
- Event/motion retention is reported only when defensible annotations exist.
- Practical gate fixed before results: SRN must improve both raw Gaussian and matched raw
  prototype by at least 0.01 absolute macro-scene AUROC on average, have a positive
  paired delta in every declared seed/holdout, reduce source-fixed target-normal FPR by
  at least 0.10 absolute without materially lowering oracle TPR@1% FPR (no more than
  0.01 absolute), reduce independent scene-probe balanced accuracy by at least 0.15,
  beat scene-mean/adversarial controls, and show a nonzero ELOS contribution. Failure of
  any simultaneous gate yields `STOP_CURRENT_SRN_FORMULATION`.

## Frozen current disposition

Track A performs no scientific model run in this sprint unless an authoritative asset
becomes available. Current primary status is therefore `EXTERNALLY_BLOCKED`.

