# Current Research State

**Updated:** 2026-08-17 +0800
**Branch:** `autonomous-dual-track-20260817`
**Starting HEAD:** `de85cab7f85370563667bc120d571f6bfa47d74b`

## Terminal dual-track state

- Track A: `EXTERNALLY_BLOCKED`
- Track B: `NO_CALIBRATION_ADVANTAGE`
- Integrity audit: `PASS` after reporting/provenance repairs
- Paper route: maintain the existing SRN falsification paper; no new positive calibration
  paper or XeLaTeX claims are justified

## What is now established

1. The earlier Ped2/Avenue results are reproducible from raw score artifacts: raw
   Gaussian 0.68846 AUROC, raw prototype 0.66527, full SRN 0.66771, delta +0.002439,
   residual identity probe 1.0, and all source-fixed cross-dataset FPR values 1.0.
2. No authoritative multi-scene raw asset could be acquired unattended. ShanghaiTech
   links fail, MSAD raw video is request-gated, and UBnormal is quota-blocked.
3. In the exact Ped2↔Avenue Track B stress protocol, every strict source-only method B0--B4
   retains target-normal FPR 1.0.
4. Declared target-normal calibration lowers FPR, but seed-balanced four-video median
   recall is at most 0.00624, so no method passes the 0.05 recall gate.
5. The learned conditional-location calibrator is discarded because it neither repairs
   FPR nor preserves ranking.
6. Generic score-calibration novelty is unavailable from the focused prior-work audit.

## Evidence boundaries

- **Engineering validation:** code/tests/provenance/historical recomputation pass.
- **Exact-protocol scientific evidence:** two cross-dataset directions only.
- **Unseen-scene evidence:** unavailable.
- **Population-level claim:** unsupported.
- **Speculation:** a new method on a genuinely multi-scene benchmark might improve the
  tradeoff; existing data do not support that conclusion.

## Do not repeat

- Do not tune B4 or its alpha/rank on Ped2/Avenue final anomaly labels.
- Do not call target-normal calibration zero-shot.
- Do not use a community ShanghaiTech/UBnormal copy without authoritative provenance.
- Do not convert the two-seen-domain SRN diagnostic into an unseen-scene claim.
- Do not report FPR repair without the associated anomaly recall and FA/hour.

## Exact next work

1. Acquire one authoritative multi-scene raw archive through its official channel.
2. Instantiate the frozen Track A whole-scene protocol before inspecting final labels.
3. Reuse the frozen DINOv2 backbone and run the complete raw/control/SRN/ELOS matrix.
4. If revisiting calibration, start from the local-density normalization literature and
   preregister a joint FPR/recall objective on source-held scenes before final evaluation.
5. Seek a true cross-family Type-B audit; the configured DeepSeek call was cancelled.

## Primary artifacts

- `DUAL_TRACK_AUTONOMOUS_SPRINT_REPORT.md`
- `TRACK_A_PROTOCOL_FREEZE.md`
- `TRACK_B_PROTOCOL_FREEZE.md`
- `refine-logs/TRACK_A_SRN_FINAL_REPORT.md`
- `refine-logs/TRACK_B_CALIBRATION_REPORT.md`
- `refine-logs/TRACK_B_PRIOR_WORK.md`
- `EXPERIMENT_AUDIT.md`
- `analysis/track_a/`
- `analysis/track_b/`
