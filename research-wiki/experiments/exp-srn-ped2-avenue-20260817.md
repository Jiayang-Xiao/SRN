---
type: experiment
node_id: exp:exp-srn-ped2-avenue-20260817
title: "SRN Ped2/Avenue real-GT falsification pilot"
idea_id: "idea:srn"
verdict: no
confidence: high
date: "2026-08-17"
hardware: "CPU; CUDA unavailable"
duration: "single unattended sprint"
provenance: "runs/ped2_avenue_joint_seen_mechanism; runs/ped2_to_avenue_raw; runs/avenue_to_ped2_raw; EXPERIMENT_AUDIT.md; analysis/summary.json"
added: 2026-08-16T18:50:25Z
tags: ["real-gt", "ped2", "avenue", "falsification", "normal-only"]
---

# SRN Ped2/Avenue real-GT falsification pilot

**verdict:** `no`  ·  **confidence:** `high`  ·  tests `idea:srn`

## Metrics
Joint seen-domain AUROC: raw Gaussian 0.6885, full SRN 0.6677; SRN residual scene probe 1.000; cross-dataset source-threshold target-normal FPR 1.000 in both directions.

## Reasoning
The tested SRN does not improve the strongest raw scorer or remove dataset/camera identity. Cross-dataset score shift supports the nuisance premise, but not this residualization remedy. Whole-scene ELOS is outside the evidence because authoritative multi-scene data were unavailable.

## Connections
_Edges are recorded in `graph/edges.jsonl`; summarize here for human readers._

