---
type: idea
node_id: idea:rank-calibration
title: "Source-Free Rank Calibration"
stage: piloted
outcome: negative
added: 2026-07-06T09:50:05Z
based_on: []
target_gaps: ["gap:G2", "gap:G3"]
tags: ["normal-only", "calibration", "evaluation"]
---

# Source-Free Rank Calibration

**stage:** `piloted`  ·  **outcome:** `negative`

## Thesis
Learn a transferable tail/rank mapping from source normal score distributions without target labels.

## Key risks
Must distinguish strict zero-shot from target-normal calibration.

## Failure / Risk Notes

The 2026-08-17 Ped2↔Avenue stress test rejected the tested source-only family: pooled
q99, source affine controls, video-balanced q99, and a low-capacity conditional-location
normalizer all retained target-normal FPR 1.0. The learned normalizer also degraded
ranking. This does not rule out all source-only calibration, but it closes this minimal
formulation on these repeatedly inspected datasets.

## Lessons Learned

Target-normal calibration can reduce FPR with one to four declared normal videos, but
the tested methods mostly do so by suppressing detections; at four videos, seed-balanced
median recall remains at or below 0.00624. Future work needs multi-scene evidence and a
joint FPR/recall objective frozen before final labels. Adaptation must never be relabeled
as zero-shot.

## Connections
_Edges are recorded in `graph/edges.jsonl`; summarize here for human readers._
