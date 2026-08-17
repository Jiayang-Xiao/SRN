# SRN Dual-Track Autonomous Sprint Report

**Sprint date:** 2026-08-17 (Asia/Shanghai)
**Track A:** `EXTERNALLY_BLOCKED`
**Track B:** `NO_CALIBRATION_ADVANTAGE`

## 1. Starting state

The sprint began on branch `autonomous-dual-track-20260817` at
`de85cab7f85370563667bc120d571f6bfa47d74b` (“Complete autonomous SRN
falsification sprint”) with a clean worktree. The requested published object
`9a13a4f7b183c452de34c17de54b761f20a5d085` is absent from the local Git object
database, so an object-level diff was impossible; the local divergent history was
preserved. The requested root `README.md` is also absent.

## 2. Environment and runtime

| Item | Value |
|---|---|
| project | `/home/xjy/ARIS` |
| project environment | `.envs/srn-autonomous` |
| Python | 3.10.20 |
| NumPy / SciPy | 2.2.6 / 1.15.3 |
| PyTorch / torchvision | 2.4.1 / 0.19.1 |
| OpenCV / Matplotlib | 4.12.0 / 3.10.5 |
| pytest / PyYAML | 8.4.1 / 6.0.3 |
| GPU | unavailable; `nvidia-smi` fails and PyTorch reports zero CUDA devices |
| storage at bootstrap | about 1.1 TiB free in workspace; 706 GiB free in `/tmp` |
| tests | 15 passed |
| Python compilation | passed |

Project-local `gdown==5.2.0` and `openpyxl==3.1.5` were installed for official
asset/metadata acquisition. No system package or service was modified.

## 3. Acquired data and assets

The official MSAD metadata, train/test lists, ground truth, and 720-video workbook were
downloaded to `data/raw/msad/metadata/`. No raw dataset, large feature cache, or model
weight was added to Git scope.

ShanghaiTech, MSAD raw video, and UBnormal were evaluated as authoritative Track A
candidates. ShanghaiTech official links were inaccessible; MSAD raw video requires a
reviewed request form; the official UBnormal archive returned a quota-exceeded HTML page.
No community copy was substituted.

## 4. Provenance and checksums

Previously recorded hashes were reverified:

- DINOv2 checkpoint:
  `b938bf1bc15cd2ec0feacfe3a1bb553fe8ea9ca46a7e1d8d00217f29aef60cd9`
- Avenue archive:
  `fc9cb8432a11ca79c18aa180c72524011411b69d3b0ff27c8816e41c0de61531`
- Avenue ground truth:
  `60fec1728ec8f73a58aad3aeb5729d70a805a47e0b8eb4bf91ab67ef06386d77`
- UCSD archive:
  `2329af326951f5097fdd114c50e853957d3e569493a49d22fc082a9fd791915b`
- immutable DINOv2 parent catalog:
  `9d048d0fadeb9dd19393e1f04a507d6292c70abcf743e50a7b46093c6807cfd1`
- DINOv2 code commit:
  `7764ea0f912e53c92e82eb78a2a1631e92725fc8`

MSAD per-file hashes and the 2,009-byte UBnormal failure response are recorded in
`analysis/track_a/asset_audit.json`.

## 5. Code changes

Added:

- `src/restricted_bridge/calibration.py`: robust/affine calibration, empirical-CDF
  mapping, video-balanced thresholds, and a source-only PCA-ridge conditional calibrator.
- `scripts/run_score_calibration_study.py`: frozen B-ZS/B-CAL study, historical
  score equality checks, per-method NPZ artifacts, summaries, gates, and provenance.
- `scripts/analyze_score_calibration.py`: seed-balanced tables and deterministic
  PNG/PDF figures.
- `tests/test_score_calibration.py`: affine decision invariance, calibration-only CDF
  mapping, and whole-video conditional cross-fitting tests.

The existing metric documentation was clarified: false-alarm events/hour uses total
represented test-video duration. Independent-review repairs made gate aggregation
seed-balanced and retained all computed grouped diagnostics and B-CAL calibration samples.

## 6. Track A protocol

`TRACK_A_PROTOCOL_FREEZE.md` contains an unactivated protocol shell. Had an
authoritative archive passed the barrier, it would have frozen whole-scene source/held-out
identity, DINOv2 preprocessing, seeds, the full raw/control/SRN/ELOS matrix, independent
scene probing, low-FPR metrics, and a practical simultaneous success gate before final
anomaly labels.

## 7. Track A experiments

No Track A model run was activated. This is a deliberate scientific no-run, not a missing
result:

- no authoritative raw multi-scene asset crossed the activation barrier;
- no scene allocation was selected after labels;
- no DINOv2 multi-scene cache was fabricated;
- no SRN/ELOS checkpoint or baseline matrix was run.

**Evidence label:** engineering validation of external availability only.

## 8. Track A numerical results

There are no new Track A unseen-scene numbers. Historical results were independently
recomputed as background:

| Prior two-seen-domain diagnostic | Recomputed |
|---|---:|
| raw Gaussian AUROC | 0.6884609 |
| raw prototype AUROC | 0.6652737 |
| full SRN AUROC | 0.6677126 |
| SRN − raw prototype | +0.0024389 |
| SRN residual identity probe | 1.0000 |
| source-fixed cross-dataset target-normal FPR | 1.0000 |

**Evidence label:** exact prior protocol, not Track A unseen-scene evidence.

## 9. Track A mechanism diagnostics

No new identity probe or event/motion-retention diagnostic was possible. Event/motion
retention remains unavailable rather than being replaced with an invented proxy.
Historical residual variance remains an engineering diagnostic only.

## 10. Track A verdict

`EXTERNALLY_BLOCKED`

This does not reopen SRN. The earlier Ped2/Avenue study remains negative for its own
scope, but the final genuine held-out-scene closure was not executed.

## 11. Track B prior-work findings

The focused primary-source audit found:

- WACV 2023 zero-shot cross-domain VAD;
- NeurIPS 2024 multi-domain VAD;
- NeurIPS 2023 invariant anomaly detection under shift;
- IEEE TASLP 2026 local-density anomaly-score normalization for a shared cross-domain
  threshold in anomalous sound detection;
- a 2026 speech-deepfake transferred-threshold audit;
- AAAI 2022 target-mixture contamination transfer;
- conformal prediction/anomaly detection with explicit calibration or shift assumptions.

Therefore generic score-scale calibration or the ranking-versus-threshold distinction is
not novel. A VAD-specific operating-point audit is the only defensible narrow positioning.

## 12. Track B protocol

`TRACK_B_PROTOCOL_FREEZE.md` separates:

- B-ZS source-only B0--B4 with no target statistics;
- B-CAL target-normal budgets of 1, 2, and 4 sorted training videos;
- final official test labels used only by metrics;
- 1% desired normal FPR;
- three scorer families and prototype seeds 13/29/43;
- seed-first, direction-by-scorer gate aggregation;
- joint FPR, stability, and recall success gates.

## 13. Track B experiments

Two directions were run on the immutable shared DINOv2 cache:

- Ped2 → Avenue;
- Avenue → Ped2.

Each used kNN, Gaussian/Mahalanobis, and prototype scoring. B-ZS compared pooled q99,
two affine invariance controls, video-balanced q99, and one low-capacity conditional
location model. B-CAL compared quantile, mean/std, median/MAD, and empirical-CDF mappings
at all budgets. The accepted output contains 170 per-run rows.

## 14. Track B numerical results

Source-only seed-balanced summary:

| Method | Median FPR | Worst FPR | Median recall | Median AUROC |
|---|---:|---:|---:|---:|
| B0 pooled q99 | 1.0000 | 1.0000 | 1.0000 | 0.4556 |
| B3 video-balanced q99 | 1.0000 | 1.0000 | 1.0000 | 0.4556 |
| B4 conditional location | 1.0000 | 1.0000 | 1.0000 | 0.3787 |

Four-video target-normal summary:

| Method | Median FPR | Median absolute FPR error | Median recall |
|---|---:|---:|---:|
| target q99 | 0.0009208 | 0.0090792 | 0.0062345 |
| mean/std | 0.0000000 | 0.0100000 | 0.0042476 |
| median/MAD | 0.0000000 | 0.0100000 | 0.0000000 |
| empirical CDF | 0.0000000 | 0.0100000 | 0.0049198 |

## 15. Strict zero-shot findings

All B-ZS variants retain FPR 1.0. The learned B4 model selects alpha 0.001 in every run,
fails to alter the deployed decision failure, and worsens ranking. The source-only
positive claim receives `claim_supported = no` with high confidence within this exact
protocol.

**Evidence label:** exact-protocol scientific evidence; not unseen-scene evidence.

## 16. Target-normal calibration-budget findings

Target-normal data can numerically lower FPR, but the tested mappings become
over-conservative. At four videos every median recall is below 0.00624, far below the
frozen 0.05 gate. The target-normal claim receives `claim_supported = partial` only for
FPR repair, not for a useful operating point. It is adaptation, never zero-shot.

**Evidence label:** exact-protocol target-normal adaptation evidence.

## 17. Low-FPR and false-alarm findings

B0’s seed-balanced median false-alarm rate is 321.25 events per total represented video
hour (range 143.28–499.22 across cells). Four-video target-q99 calibration lowers the
median to 5.97 but also lowers median recall to 0.00623. One-video target-q99 calibration
has median FPR 0.01873 yet 350.43 events/hour, illustrating that fragmented isolated false
positives can increase event rate even when frame FPR falls.

Oracle TPR@1%/0.1% and AUROC are retained separately; no oracle test threshold is used for
deployment claims.

## 18. Invalidated runs

Two attempts are preserved in `analysis/track_b/invalidated_runs.json`:

1. NumPy-boolean JSON serialization failure after scoring;
2. inverted aggregate `worst` FPR column.

Both were reporting bugs. The final run was regenerated end to end; no failed evidence was
deleted or silently accepted.

## 19. Independent audit findings

A fresh read-only reviewer found no fake ground truth, normalization fraud, phantom
results, or leakage and independently recomputed all 170 rows with zero mismatches. Its
initial `WARN` identified seed weighting, unretained diagnostics, an ambiguous FA/hour
denominator, and missing calibration samples in artifacts. After repair and full
regeneration, follow-up verdict is `PASS`.

A separate result-to-claim reviewer confirms:

- B-ZS claim: `no`;
- B-CAL claim: `partial` for FPR repair only;
- Track A: `EXTERNALLY_BLOCKED`;
- Track B: `NO_CALIBRATION_ADVANTAGE`.

These are same-family Type-A reviews. A configured DeepSeek cross-family call was
attempted with raw artifacts and cancelled by the runtime; no Type-B acquittal is claimed.

## 20. Supported claims

- **Engineering validation:** tests, compilation, official label/cache provenance,
  historical score reproduction, and result recomputation pass.
- **Exact-protocol scientific evidence:** tested source-only normalization does not repair
  Ped2↔Avenue thresholds.
- **Exact-protocol scientific evidence:** limited target-normal calibration lowers FPR but
  fails the recall gate.
- **Exact-protocol scientific evidence:** ranking quality and operating-point reliability
  are distinct; B4 has no advantage in this stress test.
- **Engineering validation:** Track A authoritative acquisition is externally blocked.

## 21. Unsupported claims

- SRN/ELOS succeeds or fails on a genuinely unseen multi-scene benchmark.
- The Track B result generalizes beyond Ped2/Avenue.
- Target-normal calibration is zero-shot.
- Calibration is impossible in general.
- A novel source-only calibration algorithm has been established.
- Frame samples provide IID population confidence.
- A positive method paper is warranted.

## 22. Paper status

Outcome 3 applies: Track A is blocked and Track B is negative. The existing SRN
falsification XeLaTeX paper and compiled PDF are preserved unchanged. No new numeric paper
table or calibration-method draft was created because the evidence does not justify a
positive story. The rigorous research reports are the terminal writing output.

## 23. External blockers

- ShanghaiTech official Google link is empty; OneDrive returns 403; historical official
  mirrors time out.
- MSAD raw videos require an identity-bearing reviewed request.
- UBnormal official Google Drive archive is quota-blocked.
- CUDA/NVML are unavailable.
- DeepSeek cross-family reviewer call was cancelled.
- `.git` is read-only in this runtime.

## 24. Exact next experiments

1. Obtain one authoritative multi-scene raw archive through its official channel.
2. Verify checksum, license, official split, and scene mapping.
3. Activate the frozen Track A whole-scene protocol before final labels.
4. Extract the immutable DINOv2 ViT-S/14 catalog and run the full baseline/SRN/ELOS matrix.
5. For future calibration, begin from local-density score normalization, freeze a joint
   FPR/recall objective on source-held scenes, and reserve new final scenes.
6. Seek a true cross-family audit after artifacts are frozen.

Do not continue tuning B4 on Ped2/Avenue final labels.

## 25. Git commit and push status

No commit or push was possible because `.git` is readable but not writable. The branch
and HEAD remain unchanged. The starting worktree was clean; all sprint changes remain
visible in the working tree. No published history was rewritten and no raw dataset,
checkpoint, large feature cache, or secret was staged.

## 26. Important artifact paths

- `TRACK_A_PROTOCOL_FREEZE.md`
- `TRACK_B_PROTOCOL_FREEZE.md`
- `refine-logs/DUAL_TRACK_AUTONOMOUS_DECISIONS.md`
- `refine-logs/DUAL_TRACK_AUTONOMOUS_SPRINT_LOG.md`
- `refine-logs/TRACK_A_SRN_FINAL_REPORT.md`
- `refine-logs/TRACK_B_CALIBRATION_REPORT.md`
- `refine-logs/TRACK_B_PRIOR_WORK.md`
- `EXPERIMENT_AUDIT.md` / `EXPERIMENT_AUDIT.json`
- `analysis/track_a/`
- `analysis/track_b/`
- `findings.md`
- `refine-logs/CURRENT_RESEARCH_STATE.md`
- `.aris/traces/experiment-audit/2026-08-17_run02/`
- `.aris/traces/result-to-claim/2026-08-17_run01/`

Accepted Track B output hashes:

- `results_long.csv`:
  `a2a5baa927a4618bbcef54f789bc9768e8d96771745a8f400ce9e5964906a1d1`
- `results_aggregate.csv`:
  `24fb850ac34f72ae53a8e807dd3cbe7c80e42bc6fac8cea6dd68decfb826f256`
- `summary.json`:
  `d421eb617b78c0550ce1f525a0b8c54b4676d0f87ae12a91a1d7afc49a63ea01`
- `provenance.json`:
  `16199f0c163155a47790f28caeda8dc65c8eadcf2a232be728e0322a03a46b2d`

