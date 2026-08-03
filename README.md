# SRN: Scene-Residual Normality

This repository publishes the current reproducible research state for:

**Normal-Only Video Anomaly Detection on General/Public VAD Benchmarks**

## Current Status

- Original independent review: `REVISE / NOT READY`
- Revision re-review: `READY WITH RESTRICTIONS`
- Prior-work novelty gate: `NOVELTY PLAUSIBLE`
- Restricted bridge: `AUTHORIZED / IN PROGRESS`
- Formal Tier A experiment run: `NOT STARTED`

The restricted bridge currently includes a unified frozen-feature implementation,
protocol and leakage guards, a CPU-only synthetic dry-run, and a gated Ped2/Avenue
pilot plan. The synthetic run completed 2 seeds x 11 matrix entries and 9 unit tests;
its metrics are engineering checks only and are not scientific results.

## Method Boundary

The primary mechanism is SRN:

```text
z -> c -> u_hat -> r = P(z - u_hat)
q = a(c)
e = concat(r, lambda * q)
```

- The backbone remains frozen.
- The scene token and scene-predictor are low-capacity.
- ELOS is a whole-scene training/validation principle, not a standalone contribution.
- No anomaly samples or labels are allowed in training, threshold selection,
  normalization, or model selection.
- AMCN, Tier B datasets, and end-to-end backbone fine-tuning are out of scope for
  the current bridge.

## Current Blockers

UCSD Ped2, CUHK Avenue, ShanghaiTech, and compliant frozen feature caches were not
found on the server. No dataset, backbone weight, or feature cache was downloaded.
No GPU feature extraction or formal training has started. Ped2/Avenue can provide a
low-cost pilot, but ShanghaiTech remains necessary for the gated whole-scene/ELOS
falsification stage.

## Key Files

- `refine-logs/CURRENT_RESEARCH_STATE.md`: authoritative current status
- `refine-logs/RESTRICTED_BRIDGE_AUDIT.md`: local asset and environment audit
- `refine-logs/RESTRICTED_BRIDGE_RUN_PLAN.md`: experiment matrix, metrics, gates,
  and leakage checklist
- `refine-logs/SRN_MINIMAL_SPEC.md`: frozen SRN mechanism boundary
- `refine-logs/BASELINE_REGISTRY.md`: required baselines and stop rules
- `refine-logs/PROTOCOL_MANIFEST.md`: data, split, threshold, and metric protocol
- `src/restricted_bridge/`: unified bridge implementation
- `configs/restricted_bridge_dry_run.yaml`: synthetic CPU validation
- `configs/restricted_bridge_pilot.yaml`: fail-closed Ped2/Avenue pilot config

## CPU Validation

```bash
/home/xjy/.conda/envs/aris-torch/bin/python scripts/run_restricted_bridge.py \
  --config configs/restricted_bridge_dry_run.yaml --device cpu

/home/xjy/.conda/envs/aris-torch/bin/python -m unittest discover -s tests -v
```

No datasets, feature caches, model weights, experiment outputs, API keys, or private
ARIS/Codex skill files are included in this repository.
