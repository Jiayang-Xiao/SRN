---
type: paper
node_id: paper:zhou2026_when_eer_hides
title: "When EER Hides Deployment Failure: Auditing Threshold Transfer and Unlabeled Score Calibration for Speech Deepfake Detectors"
authors: ["Jingwen Zhou", "Mingzhe Wang"]
year: 2026
venue: "arXiv"
external_ids:
  arxiv: "2606.21584"
  doi: null
  s2: null
tags: ["threshold-transfer", "calibration", "audit"]
added: 2026-08-17T13:30:57Z
---

# When EER Hides Deployment Failure: Auditing Threshold Transfer and Unlabeled Score Calibration for Speech Deepfake Detectors

## One-line thesis
Oracle ranking metrics can conceal catastrophic transferred-threshold failure, and unlabeled corrections can themselves collapse.

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

> Speech deepfake countermeasures (CMs) are compared almost exclusively by equal error rate (EER), a metric computed at an oracle threshold chosen on the labeled test set. Deployed CMs enjoy no such oracle: a threshold must be fixed in advance and applied to unlabeled target data. We audit this gap with a frozen state-of-the-art SSL-AASIST detector trained on ASVspoof 2019 LA. While its in-domain EER is 0.21%, transferring its LA-calibrated threshold to the In-the-Wild corpus yields a half total error rate (HTER) of 39.5%, with 78.7% of bona fide speech rejected, even though the In-the-Wild EER (11.2%) appears moderate. We then test whether popular unlabeled test-time corrections close this gap, and first prove a simple proposition: any strictly increasing score transform, including z-norm, temperature/shift calibration, and embedding mean alignment under a frozen linear head, cannot change EER. An audit of seven corrections on In-the-Wild and ASVspoof 2021 DF confirms the proposition empirically and exposes two further failure modes: AS-norm with an unlabeled target cohort collapses (EER 11.2% to 60.2%), and pseudo-label calibration that reduces HTER by 38% relative on In-the-Wild degenerates to 50% HTER on DF21, whose spoof prior is 96%. No audited correction reduces EER by more than 1% relative. We recommend reporting HTER at a transferred threshold alongside EER.

