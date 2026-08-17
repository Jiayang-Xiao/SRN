# SRN: Scene-Residual Normality

This repository contains the reproducible research state for **normal-only video anomaly
detection under scene and dataset shift**.

## Current Verdict

The tested low-capacity SRN mechanism is **stopped**. The bounded Ped2/Avenue evidence is
valid, but it does not support SRN superiority or whole-scene ELOS generalization.

- Six real-ground-truth experiment batches completed on official UCSD Ped2 and CUHK
  Avenue data with frozen DINOv2 ViT-S/14 features.
- The post-run integrity audit found no invalidated run and issued `WARN` only for scope.
- Full SRN reaches 0.6677 joint-seen AUROC, below raw Gaussian at 0.6885 and only 0.0024
  above its matched raw-prototype head.
- The independent residual identity probe remains 1.000, so the tested module does not
  remove dataset/camera identity.
- Every strict Ped2-to-Avenue and Avenue-to-Ped2 source threshold produces target-normal
  FPR 1.0 for all three tested raw scorers.
- A negative-result paper draft and independent claim/citation audits are included.

## Review Entry Points

1. `paper/main.pdf`: 11-page negative-result paper, including appendix.
2. `AUTONOMOUS_SPRINT_REPORT.md`: full execution record, findings, limitations, and next
   experiments.
3. `CLAIMS_FROM_RESULTS.md`: supported and unsupported claims.
4. `EXPERIMENT_AUDIT.md`: post-run integrity audit and evidence classification.
5. `paper/PAPER_CLAIM_AUDIT.md`: numerical and scope-claim reconciliation.
6. `paper/CITATION_AUDIT.md`: independent verification of all bibliography entries.
7. `analysis/summary.json`: machine-readable aggregate results.

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

## Repository Map

- `src/restricted_bridge/`: SRN, baselines, scoring, metrics, and experiment runner.
- `scripts/`: feature extraction, cache construction, execution, and result analysis.
- `configs/`: frozen configurations for the six formal experiment batches.
- `analysis/`: aggregate tables, score-shift diagnostics, and machine-readable summaries.
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

The current suite contains 12 tests and runs on CPU. Dataset archives, DINOv2 weights,
feature caches, raw per-frame score arrays, checkpoints, and experiment run directories are
not published. Their sources, hashes, split identities, and preprocessing contracts are
recorded in `refine-logs/DATA_AND_FEATURE_PROVENANCE.md`.

## Evidence Boundary

This repository supports a bounded mechanism falsification and deployment-reliability
warning. It does not support state-of-the-art claims, general SRN efficacy, whole-scene
ELOS validation, or conclusions about other backbones, temporal models, or object-centric
methods. A genuine ELOS test still requires an authoritative multi-scene dataset with a
scene held out from both representation learning and checkpoint selection.
