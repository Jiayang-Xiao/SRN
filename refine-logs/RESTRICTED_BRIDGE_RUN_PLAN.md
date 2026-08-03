# Restricted Bridge 正式运行计划

**日期：** 2026-08-03
**状态：** `PLAN READY / FORMAL RUN NOT STARTED`
**范围：** Ped2 + Avenue 最小 pilot；ShanghaiTech 仅保留为通过 gate 后的下一阶段。
**非结果声明：** synthetic dry-run 只验证工程链路，所有数值均不得作为科研结果。

## 1. 数据、backbone 与 cache

| 项目 | 冻结值/当前状态 |
|---|---|
| Pilot datasets | UCSD Ped2、CUHK Avenue；本地均缺失 |
| Planned cache | `data/frozen_features/ped2_avenue_frozen.npz`；当前不存在 |
| Frozen backbone | provisional `DINOv2-S/14 frame pooling`，384 维；checkpoint/cache 当前不存在 |
| Backbone policy | 所有方法同一 cache；backbone 完全冻结；禁止 SRN 单独换 backbone |
| ShanghaiTech | 不在首轮实际运行；Ped2/Avenue gate 通过后另行生成/审计 cache |
| Background subtraction | 仅当 cache 合法提供 label-free `background_features` 时启用，否则标记 unavailable |

`.npz` 必须包含 `features[N,D]`、`split[N]`、`scene_id[N]`、`video_id[N]`、`frame_index[N]`、`label[N]`、`fps[N]`；可选 `location_dependent[N]` 与 `background_features[N,D]`。train/source_val/target_calibration 的 `label` 必须全为 0，异常标签只可出现在 test evaluation。

## 2. Split 定义

- `train`：官方 normal-only training videos；按 whole video 分配，不切帧到其他 split。
- `source_val`：从 source normal videos 中预先冻结的 whole-video validation；只用于 source threshold 和 model selection。
- `target_calibration`：可选、预先声明、whole-video target normal subset；只进入独立 calibration table。
- `test`：官方 test videos；labels 仅在最终 evaluation 读取。
- 严禁 frame-level random split、同一视频相邻帧跨 split、test score normalization、target anomaly thresholding。

Ped2/Avenue 的限制：二者不能单独提供可信的 multi-source-scene LOSO。首轮可将官方 dataset identity 作为 source domain 做双域诊断，但不得将其包装成 unseen-scene 结论。ELOS 必要性和 whole-scene generalization 的最终 gate 必须在通过先行 pilot后由 ShanghaiTech official scene mapping 验证。

## 3. 实验矩阵

所有条目共享同一 features、split、seed、训练轮数、normality scorer 配置、阈值协议和评价代码。

| ID | Representation | Scorer / track | 目的 |
|---|---|---|---|
| P01 | raw | kNN | 最小 frozen feature baseline |
| P02 | raw | shrinkage Gaussian/Mahalanobis | density control |
| P03 | raw | prototype memory | shared primary head |
| P04 | source scene mean subtraction | prototype | trivial subtraction falsification |
| P05 | label-free background subtraction | prototype | 仅 cache 可计算时 |
| P06 | adversarial scene-invariant residual | prototype | generic invariance control |
| P07 | full SRN + ELOS | prototype | 主机制 |
| P08 | SRN without ELOS | prototype | ELOS isolation |
| P09 | ELOS without SRN | prototype | protocol-only control |
| P10 | SRN residual-only | prototype | controlled context / over-invariance |
| P11 | raw calibration-only | prototype | representation vs calibration |
| P12 | all applicable methods | source-threshold transfer | strict zero-shot table |
| P13 | all applicable methods | target-normal calibration | separate table, never merged |

Strict zero-shot 的未知 scene mean subtraction 不估计 target mean：seen source scene 使用其 source-normal mean，未知 scene 回退到冻结的 source global mean。若要使用 target-normal mean，只能放入 target-normal calibration track，并明确命名，不能与 P04 混用。

## 4. Seed、预算与资源

- Seeds：`13, 29, 43`。
- Small-head budget：每个 trainable representation 最多 30 epochs；统一 Adam、学习率 `1e-3`；相同 early-stop 规则。不得为 SRN 增加轮数。
- Scene token：16 维；linear `g`；linear low-rank `h`；context 8 维；`lambda=0.25`，仅 source normal validation 可改。
- CPU：scorer、metrics、cache audit、small-head fallback 可运行。
- GPU：只在另行授权后的 feature extraction 或必要 small-head acceleration 使用。必须同一 shell 执行 selector 与 workload。
- 当前 GPUh：0；本轮不估计正式 extraction GPUh，直到数据帧数和 backbone pipeline 审计完成。

## 5. 输出

计划输出目录：`runs/restricted_bridge_ped2_avenue_pilot/`。

- `resolved_config.json`
- `run.log`
- `results.json`
- `results.csv`
- `seed_<seed>/<method>/checkpoint.pt`
- `seed_<seed>/<method>/metrics.json`
- cache provenance sidecar（正式 cache 建立时必须新增）：dataset path/checksum、extractor checkpoint checksum、git commit、clip sampling、feature dimension、command。

## 6. 指标

- micro AUROC（仅 sanity）与 macro scene/video AUROC；
- AUPRC；
- TPR@1% FPR、TPR@0.1% FPR；
- false alarm events/hour，依赖可信 fps；若 fps 不可核验则标记 unavailable，并报告 low-FPR 替代指标；
- source-threshold recall/FPR 与 target-normal calibration robustness；
- per-scene/domain variance、worst target；
- location-dependent / scene-dependent recall 仅在官方标签或预冻结可审计映射存在时报告，否则 unavailable；
- 3 seeds 均值与标准差；bootstrap CI 在样本量和 video grouping 可行时添加。

## 7. Go / Revise / Stop

- **GO to ShanghaiTech gated audit：** full SRN 相对 raw、scene mean subtraction 和 adversarial residual 在主要 seed 上方向一致；low-FPR/固定阈值至少不恶化；controlled context 移除后出现可解释的 location/context retention 退化或稳定性下降。
- **REVISE：** adversarial residual 稳定优于 SRN；SRN 只提高 AUROC、不改善 low-FPR/FA-hour；SRN without ELOS 与 full SRN 持平；Ped2/Avenue 因单场景结构只能给出 inconclusive。
- **STOP mechanism claim：** scene/background mean subtraction 与 full SRN 持平；raw baseline 无 cross-domain collapse；controlled context 造成不可接受的 source-scene leakage；发现异常训练标签或 split leakage。
- 不允许选择性删除失败 seed、改变 scorer/head、为 SRN 单独调 backbone/epochs/后处理。

## 8. 正式运行前 checklist

- [ ] 数据许可和本地路径已确认；无自动下载。
- [ ] 数据集 checksum、官方 split 和 frame label 对齐已记录。
- [ ] cache feature dimension/backbone/checkpoint checksum 与 config 一致。
- [ ] train/source_val/calibration/test 按 whole video 隔离。
- [ ] ELOS episode 按 whole scene/domain；不使用 frame masking。
- [ ] 无相邻帧跨 split；无重复 `(video_id, frame_index)`。
- [ ] train/source_val/calibration 无异常样本；test labels 不参与训练、阈值、normalization 或 model selection。
- [ ] strict zero-shot 与 target-normal calibration 输出分表。
- [ ] fps 和 alarm event definition 已核验。
- [ ] `git status`、commit、config、seed 和输出目录已记录。
- [ ] 若调用 CUDA，先在同一 shell执行 selector；自动选择失败即停止。

## 9. 命令

当前可安全复现的 CPU dry-run：

```bash
/home/xjy/.conda/envs/aris-torch/bin/python scripts/run_restricted_bridge.py \
  --config configs/restricted_bridge_dry_run.yaml --device cpu
```

正式 Ped2/Avenue cache 就绪且 preflight 全部通过后：

```bash
/home/xjy/.conda/envs/aris-torch/bin/python scripts/run_restricted_bridge.py \
  --config configs/restricted_bridge_pilot.yaml --device cpu
```

当前 runner 有意只接受 `--device cpu`，因此本轮没有有效的 GPU 正式运行命令。若后续另行授权 GPU feature extraction 或 small-head run，必须先实现并复审对应 CUDA entrypoint，再以 `eval "$(python scripts/select_free_gpu.py --emit-shell)" && python <task>.py` 的同一 shell 形式启动；不能通过环境变量暗中使当前 runner 运行 CUDA。
