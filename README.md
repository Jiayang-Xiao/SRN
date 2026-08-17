# SRN: Scene-Residual Normality

This repository contains the reproducible research state for **normal-only video anomaly
detection under scene and dataset shift**.

## Current Verdict

The tested low-capacity SRN mechanism remains **stopped**. The follow-up dual-track sprint
closed with:

- Track A, genuine unseen-scene SRN/ELOS closure: `EXTERNALLY_BLOCKED` because no
  authoritative multi-scene raw archive passed the acquisition gate.
- Track B, score calibration and threshold transfer: `NO_CALIBRATION_ADVANTAGE`.
- Final dual-track integrity audit: `PASS` after complete regeneration and independent
  recomputation of all 170 result rows.

- Six real-ground-truth experiment batches completed on official UCSD Ped2 and CUHK
  Avenue data with frozen DINOv2 ViT-S/14 features.
- Full SRN reaches 0.6677 joint-seen AUROC, below raw Gaussian at 0.6885 and only 0.0024
  above its matched raw-prototype head.
- The independent residual identity probe remains 1.000, so the tested module does not
  remove dataset/camera identity.
- Every tested strict source-only calibration method retains target-normal FPR 1.0 in the
  Ped2-to-Avenue and Avenue-to-Ped2 stress tests.
- Declared target-normal calibration lowers FPR but misses the frozen recall gate; at a
  four-video budget the best median recall is 0.00624.
- A negative-result paper draft and independent claim/citation audits are included.

## Review Entry Points

1. `DUAL_TRACK_SCIENTIFIC_REVIEW_BUNDLE.txt`: self-contained latest review bundle.
2. `DUAL_TRACK_AUTONOMOUS_SPRINT_REPORT.md`: complete dual-track execution record.
3. `findings.md`: concise scientific findings and constraints.
4. `refine-logs/CURRENT_RESEARCH_STATE.md`: authoritative terminal research state.
5. `EXPERIMENT_AUDIT.md`: final dual-track integrity audit.
6. `analysis/track_b/summary.json`: machine-readable calibration verdict and gates.
7. `paper/main.pdf`: preserved 11-page SRN falsification paper, including appendix.
8. `paper/PAPER_CLAIM_AUDIT.md` and `paper/CITATION_AUDIT.md`: paper assurance records.

## Main Results

| Setting and method | AUROC | AUPRC | Oracle TPR@1% FPR |
|---|---:|---:|---:|
| Ped2 within, raw Gaussian | 0.8982 | 0.9780 | 0.6845 |
| Avenue within, raw prototype | 0.6197 | 0.4235 | 0.1043 |
| Joint seen, raw Gaussian | 0.6885 | 0.5536 | 0.1082 |
| Joint seen, raw prototype | 0.6653 | 0.5001 | 0.0857 |
| Joint seen, full SRN + ELOS | 0.6677 | 0.5014 | 0.0880 |

The joint experiment exposes both Ped2 and Avenue identities during normal training. It is
a two-seen-domain mechanism diagnostic, not an unseen-scene generalization test. The
cross-dataset threshold experiments use raw frozen-feature scorers and must not be cited as
direct SRN transfer evidence.

## Dual-Track Calibration Results

| Protocol and method | Median FPR | Worst FPR | Median recall | Median AUROC |
|---|---:|---:|---:|---:|
| Source-only pooled q99 | 1.0000 | 1.0000 | 1.0000 | 0.4556 |
| Source-only video-balanced q99 | 1.0000 | 1.0000 | 1.0000 | 0.4556 |
| Source-only conditional location | 1.0000 | 1.0000 | 1.0000 | 0.3787 |
| Four-video target q99 | 0.00092 | n/a | 0.00623 | unchanged by monotone mapping |
| Four-video target mean/std | 0.00000 | n/a | 0.00425 | unchanged by affine mapping |
| Four-video target empirical CDF | 0.00000 | n/a | 0.00492 | unchanged by monotone mapping |

Target-normal calibration is adaptation, not zero-shot transfer. Its apparent FPR repair
is operationally unusable here because it largely eliminates anomaly detections. Track A
produced no new unseen-scene numbers and does not reopen the negative SRN verdict.

## Repository Map

- `src/restricted_bridge/`: SRN, baselines, scoring, metrics, and experiment runner.
- `scripts/`: feature extraction, cache construction, execution, and result analysis.
- `configs/`: frozen configurations for the six formal experiment batches.
- `analysis/track_a/`: authoritative multi-scene asset availability audit.
- `analysis/track_b/`: 170-row calibration study, seed-balanced summaries, provenance,
  invalidated-attempt records, and reliability figures.
- `figures/`: generated paper figures, tables, plotting code, and figure specifications.
- `paper/`: LaTeX sources, compiled PDF, and claim/citation audits.
- `refine-logs/`: protocol, provenance, decisions, reviews, and experiment state.
- `research-wiki/`: persistent idea, experiment, and evidence traceability.
- `tests/`: protocol, metric, scorer, model, and CPU end-to-end tests.

## Validation

Install the pinned project additions into a compatible PyTorch environment, then run:

```bash
python -m pip install -r requirements-srn-autonomous.txt
python -m unittest discover -s tests -v
python -m py_compile scripts/*.py src/restricted_bridge/*.py
```

The current suite contains 15 tests and runs on CPU. Dataset archives, DINOv2 weights,
feature caches, raw per-frame score arrays, checkpoints, and experiment run directories are
not published. Their sources, hashes, split identities, and preprocessing contracts are
recorded in `refine-logs/DATA_AND_FEATURE_PROVENANCE.md`.

## Evidence Boundary

This repository supports a bounded SRN mechanism falsification and a negative
cross-dataset operating-point audit. It does not support state-of-the-art claims, general
SRN efficacy, whole-scene ELOS validation, a novel calibration algorithm, or calibration
conclusions beyond Ped2/Avenue. A genuine ELOS test still requires an authoritative
multi-scene dataset with a scene held out from both representation learning and checkpoint
selection.
