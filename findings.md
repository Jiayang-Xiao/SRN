# Research Findings

## 2026-08-17 — Dual-track SRN/calibration sprint

### Track A: final SRN/ELOS closure

- Verdict: `EXTERNALLY_BLOCKED`.
- Authoritative ShanghaiTech access failed, MSAD raw video is request-gated, and the
  official UBnormal archive returned a quota-exceeded HTML page.
- No unseen-scene SRN/ELOS experiment was run. The earlier Ped2/Avenue two-seen-domain
  falsification remains valid but cannot answer the held-out-scene question.
- Future constraint: do not substitute a community archive or relabel Ped2/Avenue as
  unseen-scene evidence.

### Track B: strict source-only calibration

- Result-to-claim verdict: `no` (high confidence within the exact stress protocol).
- B0--B4 all yield target-normal FPR 1.0 in both Ped2↔Avenue directions/scorers. Source
  mean/std and median/MAD are affine invariance controls; video-balanced q99 and the
  learned conditional-location residual also fail.
- The learned B4 method reduces the seed-balanced median AUROC from 0.4556 to 0.3787 and
  is discarded.
- Future constraint: do not tune this minimal model further on the same final labels.

### Track B: declared target-normal calibration

- Result-to-claim verdict: `partial` only for numerical FPR repair, not for a usable
  operating point.
- At four target-normal videos, seed-balanced median FPR is 0.00092 for target q99 and
  zero for the affine/ECDF controls, but median recall is only 0.00623, 0.00425, 0, and
  0.00492 respectively—every method misses the frozen 0.05 recall gate.
- The scientifically relevant tradeoff is over-conservatism: FPR improves chiefly by
  eliminating detections. This is adaptation, never zero-shot.

### Overall Track B route

- Primary status: `NO_CALIBRATION_ADVANTAGE`.
- Broad calibration-method novelty is unavailable; close score-normalization and
  threshold-transfer work already exists in anomalous sound and speech deepfake
  detection.
- No new positive paper is activated. The defensible output is a narrow negative
  cross-dataset operating-point audit with explicit scope limits.
