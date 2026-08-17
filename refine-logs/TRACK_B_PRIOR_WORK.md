# Track B Prior Work

**Search completed:** 2026-08-17 +0800
**Evidence class:** engineering literature audit; not a systematic-review claim
**Search channels:** official proceedings, publisher/project pages, arXiv metadata/API,
and the local paper library (no local PDFs matched).

## Scope and search terms

The audit targeted video anomaly detection (VAD) calibration, anomaly-score normalization
under domain shift, source-only threshold transfer, normal-only calibration, conformal
anomaly detection, domain-generalized scoring, multi-source calibration, and
false-positive-controlled detection. Primary papers were preferred; later works were
included through the sprint date. The central distinction is whether a method may use
source normal data only, unlabeled target mixtures, declared target-normal data, or target
anomaly labels.

## Closest work matrix

| Work | Exact task | Target information | Anomaly labels | Frozen-threshold transfer evaluated? | Closest overlap / boundary |
|---|---|---|---|---|---|
| Aich, Peng, Roy-Chowdhury, “Cross-Domain Video Anomaly Detection Without Target Domain Adaptation,” WACV 2023 ([official](https://openaccess.thecvf.com/content/WACV2023/html/Aich_Cross-Domain_Video_Anomaly_Detection_Without_Target_Domain_Adaptation_WACV_2023_paper.html)) | zero-shot cross-domain VAD | none at training/adaptation | no real source anomalies; generated pseudo-abnormal frames | evaluation emphasizes frame AUC, not source-fixed target-normal FPR | closest VAD zero-shot setting, but feature/prediction generalization rather than explicit score-scale calibration |
| Cho et al., “Towards Multi-Domain Learning for Generalizable Video Anomaly Detection,” NeurIPS 2024 ([official](https://proceedings.neurips.cc/paper_files/paper/2024/hash/59eb2d8ce0e4830f80780f7f78c67dec-Abstract-Conference.html)) | multi-domain VAD with abnormal conflicts | multiple training domains | weakly supervised abnormal data are part of the benchmark/task | not the paper’s primary question | establishes multi-domain VAD infrastructure, but differs from normal-only calibration |
| Carvalho et al., “Invariant Anomaly Detection under Distribution Shifts: A Causal Perspective,” NeurIPS 2023 ([official](https://proceedings.neurips.cc/paper_files/paper/2023/hash/b010241b9f1cdfc7d4c392db899cef86-Abstract-Conference.html)) | general anomaly detection under domain/covariate shift | multiple training environments | method is framed around normal-training anomaly detection; evaluation uses labeled anomalies | primarily OOD ranking/performance, not the deployed source threshold | representation-level invariance is close to Track A, not Track B’s score-level boundary |
| Wilkinghoff et al., “Local Density-Based Anomaly Score Normalization for Domain Generalization,” IEEE TASLP 2026 / arXiv 2025 ([publisher](https://www.merl.com/publications/TR2026-010), [arXiv](https://arxiv.org/abs/2509.10951)) | anomalous sound detection across domains | source-side density/context; unseen domains at inference | normal-only system fitting; anomalies for evaluation | yes: the motivation explicitly identifies one-domain thresholds becoming suboptimal and the need for a single threshold | extremely close generic hypothesis and source-only normalization mechanism, but in sound rather than video |
| Zhou and Wang, “When EER Hides Deployment Failure,” arXiv 2026 ([primary manuscript](https://arxiv.org/abs/2606.21584)) | threshold transfer for speech deepfake detectors | evaluates unlabeled target-time corrections | labeled target data for audit metrics, not method fitting | yes, directly audits transferred thresholds versus oracle EER | extremely close operational thesis; shows that ranking/oracle metrics can hide threshold failure and that corrections may collapse |
| Perini, Vercruyssen, Davis, “Transferring the Contamination Factor … by Shape Similarity,” AAAI 2022 ([official](https://ojs.aaai.org/index.php/AAAI/article/view/20331)) | threshold/contamination transfer across related anomaly domains | unlabeled target score distribution | no labeled target data required | yes, but threshold depends on the target mixture score distribution | not strict zero-shot and not target-normal calibration; it is transductive target-mixture adaptation |
| Tibshirani et al., “Conformal Prediction Under Covariate Shift,” NeurIPS 2019 ([official](https://proceedings.neurips.cc/paper_files/paper/2019/hash/8fb21ee7a2207526da55a679f0332de2-Abstract.html)) | conformal prediction with covariate shift | known likelihood ratio or unlabeled target covariates | supervised regression responses in its core setting | coverage transfer, not VAD threshold transfer | provides formal shift-aware calibration, but requires target covariates/ratio and assumptions absent from strict B-ZS |
| Zhang et al., “Conformal Anomaly Detection in Event Sequences,” ICML 2025 ([official](https://proceedings.mlr.press/v267/zhang25dn.html)) | continuous-time event-sequence anomaly tests | calibration data under its conformal setting | anomaly labels are not used for fitting the detector | finite-sample FPR control is central | directly relevant to FPR reliability but neither VAD nor cross-domain source-only transfer |

## Findings

1. **Generic novelty is unavailable.** The score-scale/threshold-transfer problem is
   explicit in anomalous sound detection and, by 2026, in speech deepfake auditing.
   Track B must not claim to originate the ranking-versus-decision-boundary distinction.
2. **The VAD-specific empirical audit remains a defensible narrow contribution.** The
   close zero-shot VAD paper evaluates cross-domain detection, while the reviewed VAD
   literature does not make source-fixed target-normal FPR and false alarms/hour its
   central comparison.
3. **Target-information regimes are often blurred in adjacent work.** Contamination
   transfer and covariate-shift conformal methods may use unlabeled target mixtures or
   target covariates. They are not evidence for strict source-only calibration.
4. **A learned conditional normalizer needs a high bar.** Local-density source-only score
   normalization is already established in another modality. A VAD version is interesting
   only if it beats simple controls on multiple genuinely unseen scenes and preserves
   anomaly recall.
5. **Conformal guarantees do not automatically survive arbitrary scene shift.** Exchangeability
   or correctly modeled covariate shift is a substantive assumption; applying an ordinary
   source quantile to a shifted target is not conformal FPR control.

## Novelty decision

**No broad method novelty claim is authorized.** The present Ped2↔Avenue experiment is an
exact-protocol VAD stress audit and a negative test of minimal controls. A future paper
would require authoritative multi-scene VAD evidence, explicit operating-point metrics,
and a result not already explained by local-density normalization or target-distribution
adaptation. Until then, the strongest supportable positioning is a reproducibility-oriented
negative finding, not a new calibration algorithm.

## Search limitations

This was a focused current audit, not an exhaustive systematic review. Search-engine and
arXiv retrieval can miss terminology variants. Citation contexts were checked against
official abstracts/pages and, where needed, paper text, but no claim of exhaustive coverage
or priority is made.
