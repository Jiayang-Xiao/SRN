# Track A SRN Final Report

**Primary status:** `EXTERNALLY_BLOCKED`
**Decision time:** 2026-08-17 +0800
**Evidence ceiling:** engineering validation of availability/provenance; no new
unseen-scene evidence

## Research question

Track A was intended to decide whether low-capacity SRN trained and selected with ELOS on
multiple source-normal scenes improves anomaly detection on a genuinely held-out scene
while reducing independent scene-identity decodability. The Ped2/Avenue diagnostic is
explicitly excluded from this question.

## Bootstrap and prior-result verification

The existing test suite passed, Python sources compiled, the DINOv2 checkpoint/cache
checksums matched provenance, and the preserved raw-score artifacts were regenerated
exactly by the Track B runner. Direct recomputation from the historical score files
confirmed the prior numbers:

| Historical diagnostic | Recomputed |
|---|---:|
| joint raw Gaussian AUROC | 0.6885 |
| joint raw prototype AUROC, 3-seed mean | 0.6653 |
| joint full SRN AUROC, 3-seed mean | 0.6677 |
| full SRN − raw prototype AUROC | +0.0024 |
| full SRN residual scene-probe accuracy | 1.0000 |
| source-fixed target-normal FPR, both cross-dataset directions/scorers | 1.0000 |

**Label:** exact-protocol scientific evidence for the previous two-seen-domain
falsification study only. It is not an unseen-scene result and cannot activate or satisfy
the Track A decision gate.

## Authoritative asset audit

| Candidate | Scientific suitability | Authoritative access outcome | Decision |
|---|---|---|---|
| ShanghaiTech Campus | 13 real scenes; preferred benchmark | official Google anchor empty; current OneDrive 403; two official-history mirrors timed out | blocked |
| MSAD | 14 scenarios; official normal-only protocol | metadata/features public, but raw videos require reviewed request; no unattended DINOv2 extraction | blocked for the controlled backbone |
| UBnormal | 29 virtual scenes; official split lists permit normal-only restriction | official 16,037,804,331-byte archive returned a 2,009-byte quota-exceeded HTML page | blocked |

No anonymous or community re-upload was used. Official MSAD metadata checksums and the
preserved UBnormal response are recorded in
`analysis/track_a/asset_audit.json`. The official UBnormal repository was inspected at
commit `8c77642bb72615988ace0451b94ec42f8953a525`.

## Protocol state

`TRACK_A_PROTOCOL_FREEZE.md` records a no-run protocol shell and the prospective
success gate. It was deliberately not activated because no authoritative raw asset passed
the acquisition barrier. Consequently:

- no Track A feature cache was created;
- no source/held-out scene allocation was chosen after labels;
- no SRN/ELOS checkpoint was trained or selected;
- no Track A comparison matrix, identity probe, retention diagnostic, or held-out anomaly
  metric was run;
- no failed download was reclassified as data.

## Track A verdict

`EXTERNALLY_BLOCKED`

This status is about the missing authoritative input, not a scientific rescue of SRN.
The current SRN formulation remains falsified in the earlier two-seen-domain protocol, but
this sprint did not perform the stronger final unseen-scene closure requested here.

## Supported and unsupported statements

- **Engineering validation:** the current Ped2/Avenue implementation, official labels,
  cache provenance, stored raw scores, and historical metrics are reproducible.
- **Exact-protocol scientific evidence:** the previous two-seen-domain study does not show
  useful SRN gain and does not suppress dataset identity.
- **Unseen-scene evidence:** unavailable in this sprint.
- **Supported:** authoritative ShanghaiTech/MSAD/UBnormal acquisition was attempted and
  blocked for distinct documented reasons.
- **Unsupported:** SRN succeeds or fails on a final held-out multi-scene benchmark; ELOS
  adds value; SRN preserves event/motion evidence on an unseen scene.
- **Speculation:** an official multi-scene run would likely stop the current formulation;
  the prior negative result is not logically sufficient to claim that outcome.

## Exact next experiment

When one authoritative raw archive becomes available, verify its checksum/license and
official scene map, instantiate the predeclared whole-scene protocol before final labels,
extract the immutable DINOv2 ViT-S/14 catalog, and run the frozen baseline/SRN/ELOS matrix.
Do not tune on the same held-out scenes and do not replace the backbone to rescue SRN.

## Important artifacts

- `TRACK_A_PROTOCOL_FREEZE.md`
- `analysis/track_a/README.md`
- `analysis/track_a/asset_audit.json`
- `data/raw/msad/metadata/`
- `logs/UBnormal_quota_exceeded_20260817.html`
- `logs/download_ubnormal.log`
