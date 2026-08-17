# SRN Autonomous Adversarial Review

**Status:** complete  
**Evidence policy:** only real, protocol-valid experiment outputs may support a scientific
verdict. Synthetic dry-runs are excluded.

## Initial zero-context concerns

1. Ped2 and Avenue cannot establish the claimed whole-scene ELOS result by themselves;
   dataset identity is not equivalent to a genuine multi-scene holdout.
2. The existing ELOS implementation requires scrutiny: rotating an omitted source scene
   during optimization and logging its distance is not automatically a model-selection
   principle and may not isolate the contribution of ELOS.
3. A trained scene classifier’s own accuracy is not an independent residual scene probe;
   a post-hoc probe with held-out normal videos/scenes is needed.
4. False-alarm events/hour must respect chronological `frame_index` order and explicit gap
   handling inside each video.
5. Real conclusions require verified data provenance, label/frame alignment, shared frozen
   features, at least three complete seeds where feasible, and strict separation of source
   threshold transfer from target-normal calibration.

The final review will test whether raw, scene-mean, background, or generic adversarial
controls explain any apparent SRN gain and will assign `GO`, `REVISE`, `STOP`, or
`INCONCLUSIVE` without favoring SRN.

## Final adversarial review

**Verdict:** `STOP` the current mechanism claim; retain the score-shift observation as a
bounded premise for future calibration work.

1. **Strongest alternative explanation.** The decisive cross-dataset result is numerical
   score-scale shift, not evidence that a learned scene component was isolated. Target
   normal q99 values are 6.50--32.42 times their source-normal counterparts.
2. **Trivial control.** Scene-mean subtraction reduces the independent identity probe from
   1.000 to 0.283, yet its anomaly ranking matches raw prototype. Removing identity alone
   is neither sufficient nor synonymous with useful residualization.
3. **Hidden target information.** None was found in the audited strict track. Target-normal
   calibration is declared separately and uses no target anomalies.
4. **Split scope.** Ped2/Avenue is cross-dataset for raw scorer transfer, but the joint SRN
   matrix trains on both identities. It is not a genuine held-out-scene experiment.
5. **Method evidence.** Full SRN is below raw Gaussian and its matched-head delta is tiny
   and mixed at low FPR. Its residual scene probe remains 1.000.
6. **ELOS novelty.** ELOS remains a source-normal checkpoint-selection principle and is
   not established as an algorithmic contribution.
7. **Stability.** Learned/prototype methods cover three seeds; deterministic Gaussian/kNN
   cover one run. Two dataset identities and broad bootstrap intervals preclude robust
   generalization language.
8. **Reviewer acceptance.** A positive SRN paper would fail. A narrowly framed
   two-dataset falsification/threshold-transfer paper is evidence-grounded if it preserves
   oracle-versus-deployable terminology and the unseen-scene claim ceiling.

The independent post-run experiment auditor returned `WARN` for scope and no invalidated
runs. An attempted external DeepSeek review was cancelled by the connector; the independent
GPT-5.5 audits and internal adversarial review were completed instead.
