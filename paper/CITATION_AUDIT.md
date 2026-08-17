# Citation Audit Report

- **Date:** 2026-08-17
- **Bib file:** `references.bib`
- **Cited entries audited:** 12
- **Verdict:** `PASS`

## Summary

| Verdict | Count |
|---|---:|
| KEEP | 12 |
| FIX | 0 |
| REPLACE | 0 |
| REMOVE | 0 |

Twelve independent fresh reviewers checked one cited entry each using primary or authoritative web sources. All works exist and all final citation contexts are supported. No hallucinated, wrong-context, or unverifiable citation remains.

## Corrections applied during the audit

- Separated the Lu et al. Avenue study citation from exact official-archive counts, which are established by the official project page and local decode audit.
- Changed “sparse reconstruction” to the source's more precise “sparse-combination learning.”
- Rephrased Street Scene as motivation for explicit false-positive burden rather than as the source of the events/hour metric.
- Clarified zxVAD's Normalcy Classifier and relative-normalcy learning.
- Changed “recent audits” to “a recent audit” and identified Rashidi's Mahalanobis experiment as a control.
- Described MDVAD as a formalized leave-one-out multi-source/unseen-target protocol.
- Added verified DOIs and NeurIPS page ranges where authoritative metadata were available.

## All-clean entries

- `li2014anomaly` — TPAMI paper, method context, and Ped2 origin verified.
- `lu2013abnormal` — ICCV paper, method context, and Avenue origin verified.
- `liu2018future` — future-frame prediction context verified.
- `gong2019memorizing` — memory-augmented autoencoder context verified.
- `park2020memory` — memory items and compactness/separateness losses verified.
- `ramachandra2020street` — single-/multi-scene distinction and practical evaluation critique verified.
- `aich2023crossdomain` — target-adaptation-free zxVAD setting verified.
- `ganin2016domain` — gradient-reversal mechanism verified.
- `oquab2024dinov2` — TMLR record and general-purpose frozen-feature context verified.
- `rashidi2026benchmark` — 2026 arXiv audit and stated evaluation components verified.
- `cho2024multidomain` — NeurIPS 2024 MDVAD leave-one-out protocol verified.
- `zhu2024advancing` — NeurIPS 2024 MSAD 14-scenario benchmark verified.

## Metadata notes

CVF Open Access and IEEE/Crossref assign different page ranges to several CVPR/WACV papers. The bibliography consistently retains the defensible CVF pagination while adding verified DOI identifiers. This is a source-pagination discrepancy, not a paper-identity or attribution failure.

The machine-readable ledger and source hashes are in `CITATION_AUDIT.json`; per-entry reviewer traces are under `.aris/traces/citation-audit/2026-08-17_run01/`.
