# SRN Results Summary

**Updated:** 2026-08-17  
**Current verdict:** `STOP` the tested low-capacity SRN mechanism claim.  
**Audit status:** valid bounded real-GT pilot/diagnostic evidence; no run invalidated.

## Evidence classes

- **Engineering validation:** 12 passing tests, official-asset/cache gates, within-dataset
  Ped2/Avenue checks, reproducible XeLaTeX build, and complete score artifacts.
- **Pilot evidence:** single-source Ped2↔Avenue cross-dataset threshold transfer and the
  joint two-seen-domain mechanism matrix.
- **Formal evidence for exact stored protocol:** the numerical outputs are valid for the
  declared splits, scorers, and metrics. They are not population-level or unseen-scene
  evidence.
- **Speculation:** whether another residual mechanism or genuine multi-scene ELOS can work.

## Main findings

1. Cross-dataset source-normal thresholds fail completely: target-normal FPR is 1.0 for
   Gaussian, kNN, and prototype scoring in both directions.
2. Full SRN reaches joint-seen AUROC 0.6677, below raw Gaussian at 0.6885 and only
   +0.0024 above matched raw prototype.
3. The independent held-video dataset/camera probe remains 1.000 on the SRN residual;
   scene-mean subtraction lowers it to 0.283 without improving detection.
4. Target-normal calibration restores low FPR but yields weak recall (0--0.0038 for
   Ped2→Avenue; 0.0087--0.1620 for Avenue→Ped2).
5. ELOS whole-scene generalization is untested because authoritative ShanghaiTech data
   could not be obtained and the joint cache contains only two seen domains.

## Supported claim

Frozen DINOv2 features and their normality-score scales are strongly dataset/camera
dependent on Ped2 and Avenue. The tested SRN implementation neither removes that identity
nor improves over strong raw-feature scoring. This is a mechanism falsification and
threshold-transfer warning, not a positive method result.

Machine-readable rows are in `analysis/results_long.csv` and
`analysis/main_comparison.csv`; per-frame evidence remains under `runs/*/scores/`.
