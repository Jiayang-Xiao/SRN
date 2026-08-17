# SRN Autonomous Sprint Log

**Sprint start:** 2026-08-17T01:30:00+08:00  
**Workspace:** `/home/xjy/ARIS`  
**Branch:** `autonomous-sprint-20260817`  
**Starting HEAD:** `1d09e89fcd48be1b67b3123a75a9b82dd72f9b0c`  
**Published reference:** `50306cccbf7e34444a4ac1ca012fa69a61cef4da`

This file is append-only for the 2026-08-17 unattended sprint. Synthetic dry-run
outputs are engineering evidence only and must never be promoted to scientific results.

## 2026-08-17T01:30:00+08:00 — Mandatory bootstrap

- **State:** Sprint initialized from a clean worktree.
- **Observation:** Shell execution and workspace writes are available without interactive
  approval. HTTPS access to GitHub succeeded. A project/user-space `pip --dry-run`
  resolved `packaging==24.2` from the configured package index.
- **Observation:** `/` has about 706 GB free and `/home` has about 1.1 TB free.
- **Observation:** The default shell Python is 3.14.2 from the unrelated `xjy`
  environment. The project-recommended `/home/xjy/.conda/envs/aris-torch` uses Python
  3.10.20, PyTorch 2.4.1, torchvision 0.19.1, NumPy 2.2.6, and a CUDA 12.1 build.
- **Observation:** `nvidia-smi` fails to communicate with the NVIDIA driver. The kernel
  module is loaded, but the sandbox exposes no `/dev/nvidia*` device nodes; PyTorch reports
  `cuda_available=False` and zero devices.
- **Decision:** Reuse `aris-torch` for initial CPU audit/tests. Do not launch CUDA work
  unless the repository selector succeeds in the same shell as the workload.
- **Reason:** The environment already satisfies the current bridge runtime, while arbitrary
  GPU selection would violate project policy.
- **Commands:** Mandatory bootstrap commands from the sprint prompt; environment/version
  probes; non-destructive network and package-resolution probes.
- **Result:** CPU/offline work can proceed. GPU extraction is currently a host/runtime
  blocker, not an authorization blocker.
- **Next action:** Complete authoritative-state/code audit, run tests, repair protocol and
  implementation defects, then pursue legitimate dataset and backbone acquisition.

## 2026-08-17T01:34:20+08:00 — Historical gate disposition

- **State:** Prior restricted-bridge documents read and preserved.
- **Observation:** Earlier documents prohibited downloads, GPU use, formal experiments, and
  ShanghaiTech progression pending separate human authorization.
- **Decision:** Mark those clauses as historical process controls superseded by the current
  unattended sprint authorization. Retain the frozen mechanism, dataset, leakage, fairness,
  baseline, and evaluation constraints.
- **Reason:** The 2026-08-17 master prompt expressly grants ordinary research execution
  authority but does not relax scientific or runtime safeguards.
- **Result:** Data acquisition and experiment execution may proceed when technically and
  legally possible; the failed GPU selector still blocks CUDA work.
- **Next action:** Audit the full code path and public asset availability.

## 2026-08-17T01:39:00+08:00 — Isolated environment

- **State:** Project-local experiment environment created.
- **Observation:** `aris-torch` contains the required PyTorch base but lacks SciPy,
  OpenCV, Matplotlib, pytest, and tqdm needed for dataset conversion, MATLAB label
  parsing, video decoding, testing, and plotting.
- **Decision:** Create `.envs/srn-autonomous` with `--system-site-packages` and install
  only the missing pinned packages.
- **Reason:** This preserves the recommended base environment while making sprint-specific
  dependencies reproducible and workspace-local.
- **Command/result:** Exact commands and versions are recorded in
  `refine-logs/AUTONOMOUS_ENVIRONMENT.md`; installation completed successfully.
- **Next action:** Verify downloaded archives, implement conversion/extraction, and run the
  expanded integrity tests.

## 2026-08-17T02:03:08+08:00 — Public assets and integrity repairs

- **State:** Ped2, Avenue, official ground truth, and DINOv2 ViT-S/14 assets acquired and
  archive/checkpoint integrity verified; CPU feature extraction in progress.
- **Observation:** Ped2's official MD5 matches. Both Avenue ZIP integrity tests pass and all
  decoded test lengths match official masks. The official DINOv2 checkpoint loads strictly
  through official model code and emits 384-dimensional features.
- **Observation:** An independent pre-run audit found missing dataset identity, ignored
  predictor rank, non-independent scene probing, incomplete threshold-transfer output,
  non-chronological FA/hour logic, and ELOS diagnostics without checkpoint selection.
- **Decision:** Repair each immediately testable defect before real evaluation; preserve the
  old synthetic output as invalid for scientific use.
- **Command/result:** The data contract, scorer chunking, metric logic, low-rank SRN
  predictor, source-normal checkpoint selection, independent probe, score artifacts, and
  aggregation were repaired. The expanded suite passes 11/11 tests.
- **Observation:** ShanghaiTech's current official Google URL is empty, its OneDrive path is
  inaccessible here, and both historical institutional mirrors time out. An unverified
  community upload was not substituted.
- **Next action:** Finish immutable cache extraction, assemble whole-video experiment
  caches, execute real-GT baselines and the two-source mechanism diagnostic, then re-audit.

## 2026-08-17T02:06:00+08:00 — Published-reference and Git audit

- **State:** Published reference independently cloned read-only to `/tmp` and checked out at
  exact commit `50306cccbf7e34444a4ac1ca012fa69a61cef4da`.
- **Observation:** The active workspace starts from a distinct local history at `1d09e89`;
  its restricted-bridge implementation differs from the public commit and includes local
  research artifacts. No public files were copied over the active workspace.
- **Observation:** The runtime permits reading but not writing `/home/xjy/ARIS/.git`;
  `git fetch` fails at `.git/FETCH_HEAD` with `Read-only file system`.
- **Decision:** Preserve the active branch and evidence files. Produce a complete working
  tree but do not claim local commits or pushes unless `.git` becomes writable.
- **Result:** Repository edits remain inspectable with `git diff`/`git status`; Git commit
  production is a runtime permission blocker, not deferred human approval.

## 2026-08-17T02:18:00+08:00 — Real feature caches and experiments

- **State:** Label-blind CPU extraction completed for all 65 videos and 35,212 frames;
  catalog SHA-256 `9d048d0fadeb9d...`.
- **Observation:** Five cache variants pass dimensionality, whole-video separation,
  dataset-identity, non-test-label, and target-calibration gates.
- **Commands:** Six recorded YAML configurations under `configs/`; complete logs and
  machine-readable artifacts under `runs/`.
- **Result:** Within-domain, two cross-dataset, joint mechanism, and bounded LR diagnostic
  matrices completed with finite scores and expected seed/row counts.
- **Next action:** Aggregate results, perform independent post-run audit, and apply stop logic.

## 2026-08-17T02:25:00+08:00 — Result analysis and verdict

- **Observation:** Cross-dataset source-threshold target-normal FPR is 1.0 for every raw
  scorer in both directions. Full SRN AUROC 0.6677 is below raw Gaussian 0.6885 and its
  residual scene probe remains 1.000.
- **Decision:** Assign `STOP` to the current mechanism; do not broaden tuning or Tier-B
  experiments. Retain the score-shift premise as a bounded finding.
- **Result:** Analysis CSV/JSON, hierarchical video/seed bootstrap intervals, claim matrix,
  and research-wiki negative verdict generated.
- **Review:** Independent experiment audit returned `WARN` for scope with no invalidated
  runs. Independent result-to-claim review rated the broad premise partial and central
  SRN/ELOS efficacy unsupported.
- **Next action:** Create traceable figures and an honest negative-result draft.

## 2026-08-17T02:47:00+08:00 — Figures and paper

- **State:** Three publication figures, two generated main tables, and one appendix table
  produced exclusively from machine-readable outputs.
- **Decision:** Use the narrowed title “A Two-Dataset Falsification Study of Scene
  Residualization for Normal-Only Video Anomaly Detection.”
- **Result:** Complete modular ICLR-style source compiled with project-local XeLaTeX.
  The final `paper/main.pdf` has eleven total pages including appendix. Fonts are embedded,
  references/citations resolve, and the build has no overfull box or undefined-reference
  warning.
- **Toolchain repair:** A broken Conda TeXLive build was preserved in logs; project-local
  TinyTeX provided a non-root resolution.
- **Next action:** Complete zero-context paper claim audit, final tests, and sprint report.

## 2026-08-17T03:25:00+08:00 — Assurance and terminal report

- **State:** Paper text frozen after independent draft review and assurance fixes.
- **Observation:** Twelve fresh per-entry citation reviewers verified every cited work and
  context. Precision fixes were applied for Avenue provenance, Street Scene operating-point
  attribution, zxVAD/MDVAD wording, and the closest frozen-feature audit.
- **Result:** `paper/CITATION_AUDIT.json` is `PASS`; the HTML reading view passed an
  independent render-fidelity review after one cosmetic metadata-layout repair.
- **Observation:** Fresh paper claim review reconciled all substantive paper numbers to
  raw results. The only initial paper warning concerned an appendix uncertainty caption;
  the caption was corrected and a final zero-context pass was launched on the frozen text.
- **Verification:** 12/12 tests pass; XeLaTeX produces an 11-page PDF with embedded fonts,
  resolved citations/references, and no overfull box warning.
- **Decision/result:** Retain the scientific `STOP` verdict for the current SRN mechanism,
  publish the bounded score-shift finding, and complete `AUTONOMOUS_SPRINT_REPORT.md`.
