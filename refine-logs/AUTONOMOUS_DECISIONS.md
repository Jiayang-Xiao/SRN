# SRN Autonomous Decisions

## D001 — Continue from the refined SRN state

- **Timestamp:** 2026-08-17T01:31:00+08:00
- **State:** The repository already contains idea discovery, novelty review, a frozen SRN
  specification, protocol manifest, baseline registry, and a restricted bridge skeleton.
- **Decision:** Treat idea discovery as complete and start the autonomous pipeline at
  implementation/audit rather than regenerate unrelated ideas.
- **Reason:** This maximizes scientific information gained per unit time and preserves the
  project’s authoritative contribution boundary.

## D002 — Preserve scientific freezes; supersede only human gates

- **Timestamp:** 2026-08-17T01:34:20+08:00
- **Decision:** The current sprint supersedes historical clauses requiring separate human
  approval for public downloads, user-space installs, GPU use, experiments, plotting,
  paper drafting, and local commits. It does not supersede normal-only training, split
  integrity, target-information prohibitions, shared-backbone fairness, or stop rules.
- **Reason:** This is the narrow interpretation consistent with both the master prompt and
  the frozen research protocol.

## D003 — Do not bypass failed GPU selection

- **Timestamp:** 2026-08-17T01:34:20+08:00
- **Decision:** Continue CPU, data, code, analysis, and documentation branches, but do not
  run any CUDA workload while `nvidia-smi` and `scripts/select_free_gpu.py` fail.
- **Reason:** GPU device nodes are unavailable despite loaded NVIDIA kernel modules; choosing
  a device by assumption would be unsafe and violate `AGENTS.md`.

## D004 — Use CPU extraction rather than change the backbone

- **Timestamp:** 2026-08-17T01:51:00+08:00
- **Decision:** Extract the official DINOv2 ViT-S/14 features on CPU with resumable
  per-video shards.
- **Reason:** A benchmark showed usable throughput, the checkpoint and official model code
  are available, and changing the backbone solely because CUDA is hidden would invalidate
  the frozen comparison.

## D005 — Do not treat an unverified ShanghaiTech mirror as authoritative

- **Timestamp:** 2026-08-17T02:03:08+08:00
- **Decision:** Record ShanghaiTech as externally blocked after exhausting current and
  historical official routes; continue Ped2/Avenue work without claiming genuine ELOS.
- **Reason:** The available community upload lacks a dataset card, checksum, and accountable
  provenance. Its use would create an avoidable data-integrity uncertainty in a formal run.

## D006 — Preserve the divergent local research history

- **Timestamp:** 2026-08-17T02:06:00+08:00
- **Decision:** Use the active `autonomous-sprint-20260817` branch as the research workspace
  after separately verifying the published reference in `/tmp`; do not replace local files
  with the public tree.
- **Reason:** The active tree was clean at sprint start but intentionally contains research
  history not present at published commit `50306cc`. In addition, `.git` is read-only, so
  commits/fetches cannot be recorded in this runtime.

## D007 — Stop the tested SRN mechanism claim

- **Timestamp:** 2026-08-17T02:25:00+08:00
- **Decision:** Do not run broad architecture or hyperparameter searches and do not advance
  to Tier B scale-up.
- **Reason:** Full SRN underperforms raw Gaussian, barely changes the matched prototype
  head, leaves dataset/camera probe accuracy at 1.000, and does not improve strict
  cross-dataset thresholds. A bounded lower-learning-rate diagnostic does not alter this.

## D008 — Draft an honest negative-result paper

- **Timestamp:** 2026-08-17T02:46:00+08:00
- **Decision:** Frame the artifact as a two-dataset falsification and threshold-transfer
  study; call TPR@FPR an oracle test-curve statistic and state that ELOS is untested.
- **Reason:** This is the strongest claim set supported by the independent integrity,
  result-to-claim, figure, outline, and paper reviews.

## D009 — Install a project-local XeLaTeX toolchain

- **Timestamp:** 2026-08-17T02:45:00+08:00
- **Decision:** Use project-local TinyTeX after the current Conda TeXLive package proved
  incomplete; install only required packages and compile without system changes.
- **Reason:** The user requested a compiled XeLaTeX draft, network/storage were adequate,
  and system TeX was absent. The resulting PDF is reproducible from workspace-local tools.

## D010 — Freeze the current SRN formulation after assurance review

- **Timestamp:** 2026-08-17T03:25:00+08:00
- **Decision:** Apply only evidence-precision and presentation corrections requested by the
  independent paper/citation audits; do not add experiments or mechanism tuning after the
  `STOP` criterion was met.
- **Reason:** The audits found no material numerical mismatch. The remaining scientific
  limitation is absent genuine unseen-scene data, which text polishing or two-dataset
  hyperparameter search cannot resolve.
