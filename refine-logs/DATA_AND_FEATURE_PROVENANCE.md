# SRN Data and Frozen-Feature Provenance

**Acquisition date:** 2026-08-17 (Asia/Shanghai)  
**Scope:** Public Tier-A data and the shared DINOv2 ViT-S/14 backbone used by every method.

## UCSD Ped2

- Official project archive: `http://www.svcl.ucsd.edu/projects/anomaly/UCSD_Anomaly_Dataset.tar.gz`
- Local archive: `data/raw/archives/UCSD_Anomaly_Dataset.tar.gz`
- Size: 740,306,953 bytes.
- Official MD5: `5006421b89885f45a6f93b041145f2eb` (verified exact match).
- SHA-256: `2329af326951f5097fdd114c50e853957d3e569493a49d22fc082a9fd791915b`.
- Extracted root: `data/raw/ucsd/UCSD_Anomaly_Dataset.v1p2/UCSDped2`.
- Official split retained: 16 normal training videos and 12 labeled test videos;
  2,550 training frames and 2,010 test frames.
- Ground truth: official per-frame pixel masks. The extractor also cross-checks their
  frame-level reduction against the archive's `UCSDped2.m` interval annotations.
- FPS: 10, from the dataset literature because the official archive contains TIFF frames,
  not video-container metadata.

## CUHK Avenue

- Official dataset page: `https://www.cse.cuhk.edu.hk/leojia/projects/detectabnormal/dataset.html`.
- Official video archive: `https://www.cse.cuhk.edu.hk/~leojia/projects/detectabnormal/Avenue_Dataset.zip`.
- Official ground-truth archive:
  `https://www.cse.cuhk.edu.hk/~leojia/projects/detectabnormal/ground_truth_demo.zip`.
- Local archives: `data/raw/archives/Avenue_Dataset.zip` and
  `data/raw/archives/Avenue_ground_truth_demo.zip`.
- Video archive: 813,227,845 bytes; SHA-256
  `fc9cb8432a11ca79c18aa180c72524011411b69d3b0ff27c8816e41c0de61531`.
- Ground-truth archive: 931,269 bytes; SHA-256
  `60fec1728ec8f73a58aad3aeb5729d70a805a47e0b8eb4bf91ab67ef06386d77`.
- Both ZIP integrity tests passed before extraction.
- Official split retained: 16 training videos and 21 labeled test videos. OpenCV decoded
  15,328 training and 15,324 test frames; every test video count matches its official
  `volLabel` mask length exactly.
- FPS: 25 for every AVI, read from official video-container metadata.
- Limitation: the official page notes a few training outliers. This sprint does not use
  anomaly annotations to remove or select those frames; it retains the official training
  partition and reports this caveat.

## DINOv2 ViT-S/14

- Official checkpoint:
  `https://dl.fbaipublicfiles.com/dinov2/dinov2_vits14/dinov2_vits14_pretrain.pth`.
- Local checkpoint: `data/models/dinov2/dinov2_vits14_pretrain.pth`.
- Size: 88,283,115 bytes.
- SHA-256: `b938bf1bc15cd2ec0feacfe3a1bb553fe8ea9ca46a7e1d8d00217f29aef60cd9`.
- Architecture source: official `facebookresearch/dinov2` repository, local ignored clone
  commit `7764ea0f912e53c92e82eb78a2a1631e92725fc8`.
- Checkpoint loading: strict; all keys matched. Confirmed output dimension: 384.
- Frame transform: RGB; bicubic resize to 256; center crop 224; tensor conversion;
  ImageNet mean `(0.485, 0.456, 0.406)` and standard deviation
  `(0.229, 0.224, 0.225)`, matching the official evaluation transform.
- Sampling: every decoded/archived frame, in original order. Extraction is label-blind;
  official test labels are joined only when writing each completed feature shard.
- Extraction script: `scripts/extract_ped2_avenue_dinov2.py`.
- Cache assembler: `scripts/build_ped2_avenue_experiment_caches.py`.
- Runtime: CPU, batch size 32, 16 PyTorch threads. CUDA was unavailable to this runtime;
  the repository GPU selector failed safely and no arbitrary GPU was selected.

## ShanghaiTech Campus status

- Official page: `https://svip-lab.github.io/dataset/campus_dataset.html`.
- The page documents 13 scenes, 130 abnormal events, and over 270,000 training frames.
- The current Google Drive anchor has an empty URL. The current OneDrive link redirects to
  a route that returns an access failure from this host.
- Official repository history shows that commit `46e7bc178996cac4394f17e6e6aaa8bdec84e9a7`
  replaced the former institutional mirror with those two links. Both former HTTP mirrors
  timed out without returning bytes during bounded probes.
- A community Hugging Face upload exists, but its page has no dataset card, checksum, or
  authoritative provenance. It was not silently substituted for the official asset.
- Current state: external acquisition blocker. Consequently, this sprint cannot provide a
  genuine 13-scene ELOS/whole-scene conclusion from Ped2 and Avenue alone.

## Cache invariants

- The same immutable 384-dimensional feature catalog is used by every baseline and SRN
  variant.
- Whole videos, never frames, are assigned to train, source-normal validation,
  target-normal calibration, and final test partitions.
- Non-test labels are asserted to be zero by both the cache assembler and loader.
- Test anomaly labels do not influence extraction, normalization, model selection,
  hyperparameters, scoring fit, source thresholds, or target-normal thresholds.
- Per-cache JSON sidecars record catalog hashes, split video identities, counts, and claim
  ceilings.
