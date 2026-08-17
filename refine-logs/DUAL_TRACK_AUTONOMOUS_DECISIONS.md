# Dual-Track Autonomous Decision Ledger

## 2026-08-17 21:13 +0800 — CONTINUE bootstrap

- Evidence: clean branch `autonomous-dual-track-20260817` at
  `de85cab7f85370563667bc120d571f6bfa47d74b`; no pre-existing worktree changes.
- Published object `9a13a4f7b183c452de34c17de54b761f20a5d085` is absent from this local object database,
  so an object-level diff is impossible. Divergent local history is preserved.
- Twelve tests and Python compilation pass. Official Ped2/Avenue/DINOv2 hashes match.
- Decision: baseline is technically valid; independently recompute key metrics before
  reusing them scientifically.

## 2026-08-17 21:13 +0800 — EXTERNALLY_BLOCKED Track A acquisition

- ShanghaiTech official Google anchor is empty, OneDrive returns 403, and historical
  institutional mirrors time out.
- MSAD is authoritative and multi-scenario, but raw videos require a reviewed form; its
  public features do not expose a complete readily enumerable normal-only catalog for
  the requested DINOv2-controlled experiment.
- UBnormal is authoritative, 29-scene, and public, but the official 16,037,804,331-byte
  archive returned a quota-exceeded HTML response. No official mirror was found.
- Decision: do not use community copies; preserve exact blockers and stop Track A model
  execution unless official access changes.

## 2026-08-17 21:13 +0800 — CONTINUE Track B with frozen stress tests

- Ped2↔Avenue cannot establish multi-source unseen-scene calibration, but it can support
  exact-protocol cross-dataset stress evidence using immutable shared features.
- Prior work already covers invariant anomaly detection, conformal FPR control, and
  source-only score normalization in anomalous sound detection. Generic novelty is not
  assumed.
- Decision: freeze simple controls, one low-capacity conditional model, and limited
  target-normal budget curves; discard the learned model if simple controls win.

## 2026-08-17 21:25 +0800 — CONTINUE after preregistered variance clarification

- The already-verified B0 result is target-normal FPR 1.0 in every transfer/scorer run,
  making its variance exactly zero despite universal operating-point failure.
- Before executing any new calibration method, the stability gate is operationalized as
  FPR variance no greater than 0.0025 together with worst FPR no greater than 0.25.
- Decision: retain all other frozen gates unchanged; this clarification cannot rescue a
  method with high FPR or negligible anomaly recall.

## 2026-08-17 21:55 +0800 — STOP_TRACK Track B method branch

- Final regenerated artifact set contains 170 per-run rows and 17 aggregates; all raw
  historical score equality checks and historical metric recomputations pass.
- B-ZS B0--B4 all retain target-normal FPR 1.0. The learned B4 model is not retained and
  lowers median AUROC relative to raw scoring.
- B-CAL methods reduce FPR with predeclared target-normal videos, but the four-video
  median anomaly recall is below 0.01 for every method, far below the frozen 0.05 gate.
- A fresh result-to-claim reviewer judges source-only support `no`, target-normal support
  `partial` only for FPR repair, and selects `NO_CALIBRATION_ADVANTAGE`.
- Decision: stop this exact calibration branch; do not tune it on Ped2/Avenue final labels.
  Preserve target-normal FPR repair as a negative tradeoff finding, not a positive method.

## 2026-08-17 22:15 +0800 — FINAL dual-track decision

- Track A primary status: `EXTERNALLY_BLOCKED`.
- Track B primary status: `NO_CALIBRATION_ADVANTAGE`.
- Independent integrity follow-up: `PASS`; result-to-claim judgments remain source-only
  `no` and target-normal `partial` for FPR repair only.
- Decision: maintain the existing SRN falsification paper, write a rigorous negative
  dual-track report, and do not activate a new positive XeLaTeX paper branch.
