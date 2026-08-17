# Claims from SRN Results

**Date:** 2026-08-17  
**Independent result-to-claim verdict:** `partial` for the broad premise; `no` for the
central SRN+ELOS efficacy claim. Confidence: high.

## Supported

1. Frozen DINOv2 features on Ped2 and Avenue retain strong dataset/camera identity. The
   independent held-video nearest-centroid probe is 1.0 for raw features.
2. Normal anomaly-score distributions shift severely across Ped2 and Avenue. Every tested
   strict source-normal threshold yields target-test normal FPR 1.0 in both directions.
3. Within-dataset detection is materially easier on Ped2 than Avenue for these frame-level
   features and scorers.

## Not supported

1. Full SRN does not beat the strongest raw-feature baseline: joint seen-domain AUROC is
   0.6677 for SRN versus 0.6885 for raw Gaussian.
2. The intended mechanism does not suppress source-scene identity: the SRN residual probe
   remains 1.0, whereas scene-mean subtraction reduces the probe to 0.283.
3. The matched prototype-head gain is tiny and mixed: +0.00244 AUROC, +0.00230 TPR@1%
   FPR, and -0.00031 TPR@0.1% FPR.
4. ELOS is not established because Ped2 and Avenue each provide only one scene and the
   joint mechanism diagnostic uses two seen domains.
5. Fixed source-threshold transfer is not supported for any tested representation.

## Safe paper claim

Frozen DINOv2 features on Ped2 and Avenue encode strong dataset/camera identity and undergo
severe normal-score shift across datasets. The tested minimal SRN/ELOS implementation does
not reliably remove this identity and does not improve over strong raw-feature scorers. The
result is a mechanism falsification and deployment-reliability warning, not an SRN success.

## Missing decisive evidence

- authoritative multi-scene data for whole-scene-held-out ELOS;
- direct SRN cross-domain testing with at least two source scenes;
- event/motion retention labels and location-dependent annotations;
- independently verified multi-scene residual probes and low-FPR event metrics.
