# SRN Autonomous Sprint Report

**Sprint date:** 2026-08-17  
**Workspace:** `/home/xjy/ARIS`  
**Starting branch/HEAD:** `autonomous-sprint-20260817` / `1d09e89`  
**Published reference verified:** `50306cccbf7e34444a4ac1ca012fa69a61cef4da`  
**Scientific verdict:** `STOP` the tested low-capacity SRN mechanism claim  
**Evidence status:** valid bounded real-ground-truth pilot/diagnostic evidence; no run invalidated

## 1. Starting state

The repository already contained a refined SRN hypothesis, frozen minimal specification,
protocol manifest, baseline registry, experiment plan, restricted-bridge implementation,
tests, and historical synthetic dry runs. The real Ped2/Avenue data, official DINOv2
weights, formal frozen feature caches, real Tier-A results, post-run audit, and paper did
not yet exist.

The active workspace history differs from the public reference. The public repository was
independently cloned to `/tmp` and checked out at the exact published hash; it was not
copied over the local research history.

## 2. Runtime and permission status

- Workspace reads/writes and non-interactive shell execution succeeded.
- Outbound network probes and public research/development downloads succeeded.
- Disk capacity was sufficient before every material download.
- `/home/xjy/ARIS/.git` was readable but mounted read-only. Fetch, commit, and push were
  impossible because `.git/FETCH_HEAD` and object metadata could not be written.
- NVIDIA kernel modules were present, but the runtime exposed no usable device nodes;
  `nvidia-smi`, PyTorch CUDA discovery, and the repository GPU selector all failed.
- No GPU workload was launched on an assumed device. Extraction and experiments ran on CPU.
- No `sudo`, system service, firewall, or machine-global configuration change was made.

## 3. Environment created or reused

The project-recommended `aris-torch` environment supplied PyTorch 2.4.1 and torchvision
0.19.1. A project-local venv at `.envs/srn-autonomous` inherited that base and added pinned
SciPy, OpenCV-headless, Matplotlib, pytest, tqdm, and CairoSVG dependencies. Python is
3.10.20; the PyTorch build targets CUDA 12.1 but CUDA visibility is false.

A project-local TinyTeX installation at `.envs/.TinyTeX` supplies XeLaTeX/TeX Live 2026.
An earlier Conda TeXLive attempt failed because its format builder lacked `mktexlsr.pl`;
that failure remains in `logs/tex_env_install.log`. Exact commands and versions are in
`refine-logs/AUTONOMOUS_ENVIRONMENT.md` and `requirements-srn-autonomous.txt`.

## 4. Data and assets obtained

- UCSD Ped2 official archive: official MD5 matched; archive and extracted split audited.
- CUHK Avenue official video and ground-truth archives: both ZIP integrity checks passed;
  all 21 mask lengths match decoded test-video lengths.
- Official DINOv2 ViT-S/14 checkpoint: strict model load, 384-dimensional class-token
  output, and checkpoint provenance verified.
- DINOv2 source code was pinned to the recorded upstream commit in the provenance log.
- ShanghaiTech was not used. Authoritative access routes were unavailable from this host,
  and an unverified community copy without accountable provenance was rejected.

Full URLs, acquisition dates, checksums, split identities, frame counts, FPS values, and
preprocessing are recorded in `refine-logs/DATA_AND_FEATURE_PROVENANCE.md`.

## 5. Code changes

The sprint repaired the restricted bridge before formal evaluation:

- added dataset identity and feature-cache provenance guards;
- enforced whole-video split and non-test-label assertions;
- made the configured low-rank SRN predictor rank effective;
- replaced the training classifier as a “probe” with an independent held-video
  nearest-centroid identity probe;
- implemented ELOS checkpoint selection over all source-held normal identities;
- corrected false-alarm event counting to sort frames and split index gaps;
- fixed average-precision behavior under tied scores;
- removed duplicate calibration behavior and separated strict/oracle/calibrated tracks;
- added chunked kNN scoring for bounded memory;
- persisted per-frame scores and complete structured result artifacts;
- added threshold-transfer and score-distribution diagnostics;
- expanded the integrity suite to 12 tests.

Key code paths are under `src/restricted_bridge/`, `scripts/`, `configs/`, and `tests/`.

## 6. Experiments executed

Six real-ground-truth experiment batches completed with finite outputs:

1. Ped2 within-dataset raw-feature sanity checks.
2. Avenue within-dataset raw-feature sanity checks.
3. Ped2 source to Avenue target raw-feature threshold transfer.
4. Avenue source to Ped2 target raw-feature threshold transfer.
5. Joint Ped2/Avenue two-seen-domain mechanism matrix.
6. Bounded learning-rate diagnostic at `1e-4`.

The joint matrix includes raw Gaussian, raw kNN, raw prototype, scene-mean subtraction,
adversarial residualization, full SRN+ELOS, SRN without ELOS, ELOS without SRN, SRN
residual-only, and the separate calibration track. Gaussian/kNN are deterministic;
prototype and learned variants use seeds 13, 29, and 43.

Commands are frozen in the six YAML files under `configs/`; results and per-frame score
arrays are under the corresponding `runs/` directories.

## 7. Main numerical results

### Within-dataset engineering checks

| Dataset/method | AUROC | AUPRC | Oracle TPR@1% FPR | Source-threshold FPR |
|---|---:|---:|---:|---:|
| Ped2 raw Gaussian | 0.8982 | 0.9780 | 0.6845 | 0.0028 |
| Avenue raw prototype | 0.6197 ± 0.0008 | 0.4235 | 0.1043 | 0.0208 ± 0.0014 |

### Joint two-seen-domain diagnostic

| Method | AUROC | AUPRC | Oracle TPR@1% FPR | Oracle TPR@0.1% FPR |
|---|---:|---:|---:|---:|
| Raw Gaussian | 0.6885 | 0.5536 | 0.1082 | 0.0524 |
| Raw prototype | 0.6653 | 0.5001 | 0.0857 | 0.0361 |
| Full SRN + ELOS | 0.6677 | 0.5014 | 0.0880 | 0.0358 |

Full SRN versus its matched raw-prototype head changes AUROC by
`+0.002439 ± 0.002456`, AUPRC by `+0.001272 ± 0.002627`, and oracle
TPR@0.1% FPR by `-0.000311 ± 0.001892`. Its independent residual identity-probe accuracy
is 1.000.

## 8. Baseline comparison

Raw Gaussian is the strongest joint-seen scorer by both AUROC and AUPRC. Scene-mean
subtraction, generic adversarial residualization, and all learned SRN ablations cluster near
the matched raw-prototype baseline. ELOS without a learned representation is numerically
identical to raw prototype. The mechanism has no consistent strong-baseline or low-FPR
advantage.

## 9. Ablation results

- Full SRN: AUROC 0.6677.
- SRN without ELOS: 0.6657.
- SRN residual-only: 0.6665.
- Adversarial residual: 0.6657.
- Scene mean + prototype: 0.6658.
- ELOS without SRN: exactly raw prototype at 0.6653.
- Lower-learning-rate diagnostic: SRN AUROC remains near 0.668 and scene probe remains 1.000.

No tested component earns its complexity through a stable low-FPR or ranking gain.

## 10. Low-FPR and threshold-transfer findings

Every raw scorer in both cross-dataset directions has source-threshold target-normal FPR
`1.0` and source-threshold recall `1.0`; the latter is an all-frames-flagged failure.
Ped2-to-Avenue AUROC is 0.3567--0.3759. Avenue-to-Ped2 Gaussian reaches AUROC 0.6929,
showing that useful ranking can coexist with a completely unusable carried threshold.

Target-test-normal/source-validation-normal q99 ratios range from 6.50 to 32.42.
Target-normal calibration restores test-normal FPR to 0--0.0028 but leaves anomaly recall
at 0--0.0038 for Ped2-to-Avenue and 0.0087--0.1620 for Avenue-to-Ped2. This is a distinct
adaptation track, not zero-shot repair.

## 11. Bugs and problems discovered

- Predictor rank was configured but ignored.
- The original “scene probe” was not independent of training.
- ELOS diagnostics did not perform the required all-source-held checkpoint selection.
- False-alarm/hour logic could merge shuffled or discontinuous frame intervals.
- Dataset/cache identity and provenance checks were incomplete.
- Cross-domain threshold and score-shift artifacts were incomplete.
- A source-normal calibration path was duplicated.
- The initial local Conda TeX environment was incomplete.
- CUDA device visibility and `.git` writes are blocked by the runtime.

All immediately repairable engineering defects were fixed and tested.

## 12. Invalidated experiments

Historical synthetic dry-run numbers remain preserved but are explicitly excluded from
scientific evidence. No real Ped2/Avenue run was invalidated. The post-run integrity audit
found no anomaly-label leakage, test-score normalization, failed-seed selection, missing
score artifact, or frame-order error in the reported real runs.

The incomplete historical directory `runs/restricted_bridge_ped2_avenue_pilot/` and stale
`configs/restricted_bridge_pilot.yaml` are excluded from the final evidence set; they were
not deleted.

## 13. Independent review findings

- Experiment integrity audit: `WARN` for scope, with no invalidated run.
- Result-to-claim review: broad nuisance/score-shift premise partially supported; SRN
  efficacy unsupported; whole-scene ELOS untested.
- Draft review: required the closest frozen-feature audit, MDVAD/MSAD context, explicit
  separation of raw cross-dataset tests from the joint SRN diagnostic, a compactness
  definition, q99/source-recall table columns, and conservative probe interpretation.
- Citation audit: `PASS`; 12/12 cited entries independently verified for existence,
  metadata, and context after precision fixes.
- Paper claim audit: every reported numerical cell and comparison reconciled to raw output;
  its final machine-readable verdict is stored under `paper/`.

External DeepSeek review was attempted through the configured connector but canceled by
the external service; no credential wait or fabricated external review was introduced.

## 14. Current verdict: STOP

`STOP` applies to the current low-capacity SRN mechanism claim, not to the broader study of
calibration under scene/domain shift. The conditions for `GO` are not met:

- SRN does not consistently improve over raw features;
- it trails the strongest raw scorer;
- its matched-head gain is negligible and inconsistent with low-FPR improvement;
- dataset/camera identity remains perfectly decodable from the residual;
- ELOS has not been tested on a genuinely unseen scene.

Broad tuning on the same two datasets would add test-specific degrees of freedom without
answering the missing multi-scene question.

## 15. Scientific claims currently supported

1. Under the exact stored Ped2/Avenue protocol, frozen DINOv2 normality-score scales shift
   enough that 99th-percentile source-normal thresholds flag every target normal frame for
   all three tested scorers.
2. Within the joint two-seen-domain diagnostic, the implemented SRN residual does not
   suppress independently probed dataset/camera identity.
3. Full SRN does not outperform raw Gaussian and provides only a negligible matched-head
   change over raw prototype.
4. Oracle low-FPR ranking statistics, fixed source thresholds, and target-normal
   calibration answer materially different questions and must be reported separately.

## 16. Scientific claims not supported

- General SRN superiority for normal-only VAD.
- Whole-scene or population-level cross-scene generalization.
- ELOS as an independently validated algorithmic contribution.
- A claim that scene-mean subtraction or adversarial invariance solves the transfer problem.
- State-of-the-art performance on Ped2, Avenue, or ShanghaiTech.
- A causal claim that all cross-dataset failure arises from removable scene components.
- A claim about temporal, object-centric, end-to-end, or other backbones.

## 17. Paper status

An honest negative-result/falsification draft is complete at `paper/main.pdf`. It has 11
pages in ICLR-style review format, including appendix; fonts are embedded, citations and
cross-references resolve, and the build log contains no overfull box or undefined-reference
warning. Source is modular under `paper/sections/`; figures and tables are generated from
machine-readable outputs only.

The paper's evidence ceiling is explicit: SRN is evaluated only in the joint two-seen-domain
diagnostic, while the cross-dataset threshold experiment uses raw frozen-feature scorers.

## 18. Remaining external blockers

- No authenticated, verifiable ShanghaiTech asset was obtainable from the routes available
  to this host; genuine ELOS remains untested.
- CUDA device nodes are not exposed; GPU work cannot be safely scheduled.
- `.git` is read-only; no local commit, fetch, or push can be produced in this runtime.
- The configured external reviewer service canceled its request.

## 19. Exact next recommended experiments

Only resume the SRN mechanism if an authoritative multi-scene dataset is secured.

1. Freeze a ShanghaiTech or equivalent whole-scene split before running any model.
2. Train/select only on source-normal scenes and keep a final camera identity unseen from
   both representation updates and ELOS selection.
3. Run raw Gaussian/kNN/prototype, scene-mean, adversarial residual, full SRN, no-ELOS,
   residual-only, and calibration controls on the identical frozen cache.
4. Require three or more seeds for stochastic methods and preserve every failed seed.
5. Gate continuation on simultaneous evidence: residual identity probe materially reduced,
   source-fixed target-normal FPR improved, oracle low-FPR TPR not degraded, and SRN exceeds
   both raw Gaussian and its matched prototype by a practically meaningful margin.
6. If those gates fail, retain `STOP`; investigate score calibration directly rather than
   increasing residual-network capacity.

## 20. Git commits produced

None. The runtime mounted `.git` read-only, so creating the requested local commits was
technically impossible. The working tree preserves all changes and `git status`/`git diff`
remain available. No push was attempted after the permission failure.

## 21. Important artifact paths

- Final report: `AUTONOMOUS_SPRINT_REPORT.md`
- Environment/provenance: `refine-logs/AUTONOMOUS_ENVIRONMENT.md`,
  `refine-logs/DATA_AND_FEATURE_PROVENANCE.md`
- Decisions/log: `refine-logs/AUTONOMOUS_DECISIONS.md`,
  `refine-logs/AUTONOMOUS_SPRINT_LOG.md`
- Results: `refine-logs/RESULTS_SUMMARY.md`, `analysis/`, `runs/`
- Integrity audit: `EXPERIMENT_AUDIT.md`, `EXPERIMENT_AUDIT.json`
- Claim mapping: `CLAIMS_FROM_RESULTS.md`
- Frozen feature catalog: `data/frozen_features/dinov2_vits14/ped2_avenue_catalog.npz`
- Catalog provenance: `data/frozen_features/dinov2_vits14/ped2_avenue_catalog.provenance.json`
- Figures/tables: `figures/`
- Paper source/PDF: `paper/main.tex`, `paper/main.pdf`
- Paper claim audit: `paper/PAPER_CLAIM_AUDIT.md`, `paper/PAPER_CLAIM_AUDIT.json`
- Citation audit: `paper/CITATION_AUDIT.md`, `paper/CITATION_AUDIT.json`,
  `paper/CITATION_AUDIT.html`
- Research-wiki experiment: `research-wiki/experiments/exp-srn-ped2-avenue-20260817.md`

## Evidence-class summary

- **Engineering validation:** complete for the repaired CPU pipeline and exact frozen
  Ped2/Avenue caches.
- **Pilot evidence:** real, audited Ped2/Avenue within/cross/joint results.
- **Formal scientific evidence:** valid only for the exact stored splits, scorers, metrics,
  and two seen dataset identities.
- **Speculation:** whether a revised mechanism or genuine multi-scene ELOS would succeed.
