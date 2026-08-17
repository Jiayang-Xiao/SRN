---
type: paper
node_id: paper:wilkinghoff2025_local_densitybased_anomaly
title: "Local Density-Based Anomaly Score Normalization for Domain Generalization"
authors: ["Kevin Wilkinghoff", "Haici Yang", "Janek Ebbers", "François G. Germain", "Gordon Wichern", "Jonathan Le Roux"]
year: 2025
venue: "arXiv"
external_ids:
  arxiv: "2509.10951"
  doi: null
  s2: null
tags: ["score-calibration", "domain-generalization", "anomaly-detection"]
added: 2026-08-17T13:30:56Z
---

# Local Density-Based Anomaly Score Normalization for Domain Generalization

## One-line thesis
Local-density source-only normalization reduces cross-domain anomaly-score mismatch for a shared threshold in anomalous sound detection.

## Problem / Gap
_TODO._

## Method
_TODO._

## Key Results
_TODO._

## Assumptions
_TODO._

## Limitations / Failure Modes
_TODO._

## Reusable Ingredients
_TODO._

## Open Questions
_TODO._

## Claims
_TODO._

## Connections
_Edges are recorded in `graph/edges.jsonl`; summarize here for human readers._

## Relevance to This Project
_TODO._

## Abstract (original)

> State-of-the-art anomalous sound detection (ASD) systems in domain-shifted conditions rely on projecting audio signals into an embedding space and using distance-based outlier detection to compute anomaly scores. One of the major difficulties to overcome is the so-called domain mismatch between the anomaly score distributions of a source domain and a target domain that differ acoustically and in terms of the amount of training data provided. A decision threshold that is optimal for one domain may be highly sub-optimal for the other domain and vice versa. This significantly degrades the performance when only using a single decision threshold, as is required when generalizing to multiple data domains that are possibly unseen during training while still using the same trained ASD system as in the source domain. To reduce this mismatch between the domains, we propose a simple local-density-based anomaly score normalization scheme. In experiments conducted on several ASD datasets, we show that the proposed normalization scheme consistently improves performance for various types of embedding-based ASD systems and yields better results than existing anomaly score normalization approaches.

