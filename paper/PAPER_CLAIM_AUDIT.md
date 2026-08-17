# Paper Claim Audit Report

- **Date:** 2026-08-17
- **Auditor:** GPT-5.5 xhigh, fresh zero-context thread
- **Paper:** *A Two-Dataset Falsification Study of Scene Residualization for Normal-Only Video Anomaly Detection*
- **Overall verdict:** `PASS`

## Claims verified

| Audit group | Count | Mismatches |
|---|---:|---:|
| Reported table numeric cells | 111 | 0 |
| Narrative result values | 23 | 0 |
| Protocol/config/split/hash values | 57 | 0 |
| Comparison or scope claim groups | 28 | 0 |

The auditor also opened 61 per-row score artifacts and recomputed 976 core metrics from
`scores.npz`; every recomputed metric matched its corresponding structured result.

## Overall finding

All audited numerical, comparison, configuration, split, hash, threshold, and scope claims
in the frozen paper source match the declared current raw evidence under standard rounding.
No missing evidence or material mismatch remains.

## High-value checks

- All 48 numeric cells in the joint main table match the joint mechanism results.
- All 36 numeric cells in the threshold-transfer table match the analysis outputs; q99
  ratios were also recomputed from per-frame score arrays.
- Every Ped2/Avenue appendix mean and shown standard deviation rounds correctly from the
  within-dataset results.
- The SRN dimensions, loss weights, scorer settings, seeds, epochs, learning rates, and
  source-threshold rule match the frozen configurations and implementation.
- Split sizes, whole-video separation, zero non-test anomaly labels, preprocessing,
  DINOv2 checkpoint/hash prefix, and CPU device records are supported by provenance.
- The text correctly limits SRN/ELOS conclusions to the two-seen-dataset diagnostic and
  makes no genuine unseen-scene generalization claim.

## Non-blocking scope notes

- Literature/context truth is handled by `CITATION_AUDIT`, which passes independently.
- The catalog hash is repeated in every experiment provenance sidecar; the top-level
  catalog sidecar does not redundantly store a field named `catalog_sha256`.
- Cross-dataset configs also contain scene-mean diagnostic rows that the paper does not
  tabulate; these rows likewise collapse to source-threshold target-normal FPR 1.0.

## Traceability

The authoritative ledger, input hashes, and result-file list are in
`PAPER_CLAIM_AUDIT.json`. The fresh reviewer trace is under
`.aris/traces/paper-claim-audit/2026-08-17_run03/`.
