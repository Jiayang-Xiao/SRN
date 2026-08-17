# Research Wiki Query Pack

_Auto-generated. Do not edit._

## Project Direction
**Problem**

在公开/通用视频异常检测（VAD）基准上，仅使用 normal training videos 学习正常性，并重点研究模型在未见场景、未见摄像机和跨数据集条件下的泛化，而不是继续只优化单数据集 frame-level AUC。
## Open Gaps
# Gap Map

_Field gaps with stable IDs._

## G1 — Scene identity leakage

Normality representations encode camera background, viewpoint, and density, causing cross-domain collapse.

## G2 — Unrealistic aggregate evaluation

Same-dataset pooled frame AUROC obscures per-scene variance, spatial correctness, and operational false positives.

## G3 — Threshold transfer failure

Source-domain score thresholds do not transfer reliably to unseen scenes at low false-positive operating points.

## G4 — Context duality

Scene context is both a nuisance variable and part of the anomaly definition; blindly removing it can erase real anomalies.

## G5 — Practicality gap

Many cross-scene approaches depend on complex object pipelines, synthetic anomalies, or expensive adaptation.

## Failed Ideas (avoid repeating)
- **Source-Free Rank Calibration**: ## Lessons Learned

Target-normal calibration can reduce FPR with one to four declared normal videos, but
- **Scene-Residual Normality**:
## Key Papers (15 total)
- [paper:aich2023_crossdomain_video_anomaly] Cross-Domain Video Anomaly Detection Without Target Domain Adaptation
- [paper:cao2023_new_comprehensive_benchmark] A New Comprehensive Benchmark for Semi-Supervised Video Anomaly Detection and Anticipation
- [paper:carvalho2023_invariant_anomaly_detection] Invariant Anomaly Detection under Distribution Shifts: A Causal Perspective
- [paper:cho2024_towards_multidomain_learning] Towards Multi-Domain Learning for Generalizable Video Anomaly Detection
- [paper:liu2023_generating_anomalies_video] Generating Anomalies for Video Anomaly Detection With Prompt-Based Feature Mapping
- [paper:perini2022_transferring_contamination_factor] Transferring the Contamination Factor between Anomaly Detection Domains by Shape Similarity
- [paper:ramachandra2020_street_scene_new] Street Scene: A New Dataset and Evaluation Protocol for Video Anomaly Detection
- [paper:rashidi2026_benchmark_auc_not] Benchmark AUC Is Not Deployable Reliability: A Cross-Dataset Audit of Off-the-Shelf Features for Surveillance Video Anomaly Detection
- [paper:ristea2024_selfdistilled_masked_autoencoders] Self-Distilled Masked Auto-Encoders are Efficient Video Anomaly Detectors
- [paper:singh2023_eval_explainable_video] EVAL: Explainable Video Anomaly Localization
- [paper:sun2023_hierarchical_semantic_contrast] Hierarchical Semantic Contrast for Scene-Aware Video Anomaly Detection
- [paper:tibshirani2019_conformal_prediction_under] Conformal Prediction Under Covariate Shift
## Recent Relationships (42 total)
  idea:srn --inspired_by--> paper:rashidi2026_benchmark_auc_not
  idea:srn --inspired_by--> paper:sun2023_hierarchical_semantic_contrast
  idea:amcn --inspired_by--> paper:rashidi2026_benchmark_auc_not
  idea:amcn --inspired_by--> paper:ristea2024_selfdistilled_masked_autoencoders
  idea:elos --inspired_by--> paper:cao2023_new_comprehensive_benchmark
  idea:elos --inspired_by--> paper:sun2023_hierarchical_semantic_contrast
  paper:rashidi2026_benchmark_auc_not --addresses_gap--> gap:G1
  paper:rashidi2026_benchmark_auc_not --addresses_gap--> gap:G2
  paper:rashidi2026_benchmark_auc_not --addresses_gap--> gap:G3
  paper:sun2023_hierarchical_semantic_contrast --addresses_gap--> gap:G1
  paper:sun2023_hierarchical_semantic_contrast --addresses_gap--> gap:G4
  paper:liu2023_generating_anomalies_video --addresses_gap--> gap:G5
  paper:ristea2024_selfdistilled_masked_autoencoders --addresses_g
