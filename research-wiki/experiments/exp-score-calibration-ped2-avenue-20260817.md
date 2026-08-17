---
type: experiment
node_id: exp:exp-score-calibration-ped2-avenue-20260817
title: "Ped2/Avenue score-calibration stress test"
idea_id: "idea:rank-calibration"
verdict: no
confidence: high
date: "2026-08-17"
hardware: "CPU; CUDA unavailable"
duration: "single unattended dual-track sprint"
provenance: "analysis/track_b; refine-logs/TRACK_B_CALIBRATION_REPORT.md; EXPERIMENT_AUDIT.md"
added: 2026-08-17T13:42:58Z
tags: ["calibration", "threshold-transfer", "ped2", "avenue", "negative"]
---

# Ped2/Avenue score-calibration stress test

**verdict:** `no`  ·  **confidence:** `high`  ·  tests `idea:rank-calibration`

## Metrics
B-ZS B0-B4 target-normal FPR=1.0; B-CAL budget-4 median FPR <=0.000921 but median recall <=0.006235; learned B4 discarded

## Reasoning
No tested method satisfies the frozen joint FPR-and-recall gate; target-normal controls repair FPR by becoming over-conservative.

## Connections
_Edges are recorded in `graph/edges.jsonl`; summarize here for human readers._

