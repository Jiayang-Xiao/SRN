# Track A Asset-Acquisition Audit

**Primary status:** `EXTERNALLY_BLOCKED`

No SRN/ELOS model run was activated. The required authoritative multi-scene raw video
asset could not be acquired in this runtime, and community mirrors were deliberately not
substituted. This directory contains the blocker evidence rather than fabricated results.

## Authoritative candidates

- **ShanghaiTech Campus:** the [official dataset page](https://svip-lab.github.io/dataset/campus_dataset.html)
  documents 13 scenes, but its Google Drive anchor is empty, the current OneDrive share
  returns HTTP 403, and two links recovered from the official page history timed out.
- **MSAD:** the [official project](https://msad-dataset.github.io/) documents 14 scenarios
  and an official normal-training split. Metadata was acquired and checksummed, but raw
  video access requires a reviewed request form, so the requested DINOv2 cache could not
  be built unattended. Public pretrained features were not silently substituted.
- **UBnormal:** the [official repository](https://github.com/lilygeorgescu/UBnormal)
  documents 29 virtual scenes and the required normal/abnormal lists. The official
  16,037,804,331-byte archive endpoint returned a 2,009-byte quota-exceeded HTML page.

## Preserved evidence

- `analysis/track_a/asset_audit.json`
- `data/raw/msad/metadata/`
- `logs/UBnormal_quota_exceeded_20260817.html`
- `logs/download_ubnormal.log`
- `TRACK_A_PROTOCOL_FREEZE.md`

**Evidence label:** engineering validation of external availability only. It is not
unseen-scene scientific evidence and does not change the earlier SRN scientific verdict.
