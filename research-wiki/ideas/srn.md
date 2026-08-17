---
type: idea
node_id: idea:srn
title: "Scene-Residual Normality"
stage: piloted
outcome: negative
added: 2026-08-16T18:50:25Z
based_on: ["paper:rashidi2026_benchmark_auc_not", "paper:sun2023_hierarchical_semantic_contrast"]
target_gaps: ["gap:G1", "gap:G4", "gap:G5"]
tags: ["normal-only", "cross-scene", "scene-factorization", "negative-result"]
---

# Scene-Residual Normality

**stage:** `piloted`  ·  **outcome:** `negative`

Low-capacity subtraction of scene-predictable frozen-feature components before normality scoring.

## Thesis
Factor frozen clip features into scene-predictable and event-residual components, then model normality in residual space.

## Key risks
Ped2/Avenue pilot leaves dataset identity fully decodable and does not beat raw Gaussian; genuine multi-scene ELOS remains untested.

## Connections
_Edges are recorded in `graph/edges.jsonl`; summarize here for human readers._

