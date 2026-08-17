# Dual-Track Autonomous Sprint Log

## 2026-08-17 21:13 +0800 — Bootstrap audit

- Recorded branch/HEAD/status before writes: `autonomous-dual-track-20260817`,
  `de85cab7f85370563667bc120d571f6bfa47d74b`, clean.
- `.git` is readable but not writable; commit/fetch/push are unavailable in this runtime.
- Root `README.md` requested by the sprint prompt is absent.
- Read the required state, protocol, baseline, result, audit, provenance, source, script,
  config, test, analysis, and paper trees.
- `.envs/srn-autonomous/bin/python -m pytest -q`: 12 passed.
- Python compile-all: passed.
- Runtime: Python 3.10.20, NumPy 2.2.6, SciPy 1.15.3, PyTorch 2.4.1,
  torchvision 0.19.1, OpenCV 4.12.0, Matplotlib 3.10.5, pytest 8.4.1.
- CUDA/NVML unavailable; `nvidia-smi` fails and PyTorch reports zero devices. CPU only.
- Storage: approximately 1.1 TiB free in workspace; `/tmp` approximately 706 GiB free.
- Network/proxy and public GitHub/Google Drive metadata access work.
- Reverified model/archive/catalog hashes against provenance. DINOv2 code commit is
  `7764ea0f912e53c92e82eb78a2a1631e92725fc8`.
- Historical incomplete run `runs/restricted_bridge_ped2_avenue_pilot/` and synthetic
  dry runs remain explicitly excluded.

## 2026-08-17 21:13 +0800 — Acquisition attempts

- Rechecked the live ShanghaiTech page and its official Git history.
- Downloaded official MSAD metadata/ground truth/list files and recorded SHA-256 values;
  raw videos remain form-gated.
- Cloned official UBnormal repository to `/tmp` at
  `8c77642bb72615988ace0451b94ec42f8953a525`; verified 29 scene IDs and official split
  lists. The official archive HEAD advertises 16,037,804,331 bytes.
- Actual UBnormal GET returned a 2,009-byte quota-exceeded page. Preserved at
  `logs/UBnormal_quota_exceeded_20260817.html` with log evidence.

## 2026-08-17 21:13 +0800 — Protocol state

- Track A no-run protocol shell recorded; status `EXTERNALLY_BLOCKED`.
- Track B strict source-only and target-normal protocols frozen before new-method runs.
- Focused literature review in progress; no novelty claim authorized yet.

## 2026-08-17 21:25 +0800 — Track B implementation

- Added leakage-separated score-calibration utilities and the frozen study runner.
- Added an explicit variance-gate clarification before any new-method execution because
  the saturated B0 reference has zero variance for the wrong reason.
- Validation and historical-score invariance checks are in progress.

## 2026-08-17 21:31 +0800 — Invalidated serialization attempt

- The first frozen study execution completed scoring and wrote intermediate CSV/NPZ
  artifacts, then failed while serializing a NumPy boolean in `summary.json`.
- Classification: reporting implementation bug, not model/metric failure. Raw-score
  equality checks had passed. The run is retained as invalidated and will be fully
  regenerated after converting gate flags to built-in booleans.

## 2026-08-17 21:34 +0800 — Reporting repair before interpretation

- The regenerated study passed and produced 170 rows with primary status
  `NO_CALIBRATION_ADVANTAGE`.
- Pre-report inspection found the aggregate `worst` column used substring matching and
  inverted the worst-case direction for `threshold_false_positive_rate`. Per-run metrics
  and all frozen gates were unaffected. The aggregate file will be regenerated with an
  explicit higher-is-worse field set; this attempt is retained as invalidated for
  reporting purposes.

## 2026-08-17 21:47 +0800 — Independent review routing

- Launched two fresh zero-context GPT-5.5 xhigh reviewer threads: experiment integrity
  and result-to-claim. They received primary file paths only.
- A configured cross-family DeepSeek reviewer was detected and invoked with unaltered
  primary-artifact contents, but the MCP call was cancelled by the runtime before a
  response. It is recorded as unavailable, not silently replaced with a cross-family
  acquittal. The completed Codex reviews are Type-A same-family reviews only.

## 2026-08-17 21:55 +0800 — Final Track B run and analysis

- Final runner exit status 0; post-run assertions and 15 tests passed.
- Result hashes: `results_long.csv` `9b9fa091...60d5`, corrected
  `results_aggregate.csv` `24fb850a...256`, `summary.json` `fc4b9a5c...c53`, and
  `provenance.json` `16199f0c...b2d`.
- Generated seed-balanced cell/summary tables and PNG/PDF operating-point and budget
  figures. Statistical unit is direction-by-scorer after prototype-seed averaging;
  intervals remain descriptive because only two target datasets are present.
- Frozen status: `NO_CALIBRATION_ADVANTAGE`. No positive paper branch is activated.

## 2026-08-17 22:03 +0800 — Integrity-review repairs

- Independent read-only audit verdict `WARN`: ground-truth provenance, score handling,
  result existence/recomputation, scope language, and leakage all pass.
- Reporting warnings: row-level gates overweighted prototype seeds; several computed
  grouped diagnostics were not persisted; FA/hour denominator needed clarification; and
  B-CAL score artifacts should carry their calibration samples.
- Repaired all four without changing methods or inspecting new labels: gates now average
  seeds before equal direction-by-scorer weighting, every computed diagnostic is retained,
  FA/hour is explicitly per total represented test-video hour, and B-CAL NPZ files include
  calibration scores/video IDs. Full regeneration is required before final reporting.

## 2026-08-17 22:15 +0800 — Terminal verification and handoff

- Post-review regeneration exit 0; 15 tests and compilation pass; independent follow-up
  verdict `PASS`; statuses unchanged.
- Final hashes supersede the earlier pre-audit log entry: `results_long.csv`
  `a2a5baa9...a1d1`, `results_aggregate.csv` `24fb850a...256`, `summary.json`
  `d421eb61...ea01`, `provenance.json` `16199f0c...b2d`.
- Updated current research state, research wiki, experiment audit, Track A/Track B
  reports, figures, invalidated-run ledger, and terminal sprint report.
- Existing SRN XeLaTeX paper remains unchanged because neither track supplies a justified
  positive paper claim.
- Git branch/HEAD are unchanged; `.git` is not writable, so commit and push are blocked.
