# Restricted Bridge 本地资产审计

**审计日期：** 2026-08-03
**状态：** `RESTRICTED BRIDGE AUTHORIZED / IN PROGRESS`
**审计边界：** 只读检查；未下载数据，未运行 GPU 查询或 CUDA 程序，未提取 frozen features，未启动正式训练。

## 1. 权威基线

本轮实现以 `SRN_MINIMAL_SPEC.md`、`PROTOCOL_MANIFEST.md`、`BASELINE_REGISTRY.md`、`EXPERIMENT_TRACKER.md` 和 `PRIOR_WORK_VERIFICATION_ROUND2.md` 为最高优先级，并核对了它们直接引用的 current state、prior-work disposition、revision review、experiment plan 与 final proposal。旧文件中下列内容已被冻结决策覆盖，不再作为实现依据：ELOS 独立贡献、直接大规模三数据集矩阵、AMCN 首轮实现、只报告 pooled frame AUC、允许 target statistics 的未分轨 calibration。

## 2. 仓库与版本

| 项目 | 审计结果 |
|---|---|
| 仓库 | `/home/xjy/ARIS` |
| 初始分支 | `master` |
| 初始工作树 | clean：`git status --short --branch` 仅返回 `## master` |
| 初始 HEAD | `5c3e97c Add prior work verification round two` |
| 最近提交 | `5c3e97c`、`770d066`、`0ace486`、`0633fe6`、`60b5ea2` |

## 3. Tier A 数据与 frozen features

| 资产 | 结果 | 判定 |
|---|---|---|
| UCSD Ped2 | 在 `/home/xjy` 六层目录和文件名扫描中未发现 Ped2/UCSD 候选；项目 `data/` 为空 | 不可用；不得自动下载 |
| CUHK Avenue | 未发现 Avenue 候选；项目 `data/` 为空 | 不可用；不得自动下载 |
| ShanghaiTech | 未发现 ShanghaiTech 候选；项目 `data/` 为空 | 不可用；暂不进入首轮运行 |
| Tier A frozen features | 未发现按上述数据集命名或带其 manifest 的 feature cache | 不可用 |

服务器上存在其他项目的 `.npy` features，但不可复用：

- `/home/xjy/Video-Swin-Transformer/features_T8`：约 28 MB，543 个 `abnormal` 与 451 个 `normal` 文件，内容为工业输送设备/轴承视频。
- `/home/xjy/multimodal_anomaly_baseline/data/features`：约 23 MB，工业音视频特征。
- `/home/xjy/multimodal_anomaly_baseline_final/data/features`：约 10 MB，工业音视频特征。

这些缓存不属于 Tier A public VAD，命名和目录还直接编码 normal/abnormal 语义，不能用于本项目的 normal-only 训练或 scientific pilot。

另发现本机缓存 checkpoint `/home/xjy/.cache/torch/hub/checkpoints/swin3d_t-7615ae03.pth`。它不是冻结计划中预选的 DINOv2-S/14 或 VideoMAE cache，不能在未记录协议变更时替换 backbone。

## 4. 现有代码与 split 审计

- 审计前仓库只有 `scripts/select_free_gpu.py`，没有 SRN、adversarial residual、scene/background mean subtraction、normality scorer、dataset loader 或 evaluation 实现。
- 未发现 Tier A 数据或 manifest，因此无法对真实样本验证 whole-scene / whole-video holdout、frame-level random split、相邻帧泄漏或异常标签使用。
- 该不确定性是正式运行阻塞项，不能被 synthetic dry-run 关闭。
- 新代码的数据契约要求 `split`、`scene_id`、`video_id`、`frame_index`、`label`、`fps`，并在加载时拒绝：同一 video 跨 split、重复 frame identity、非 test split 中出现异常样本、ELOS source scene 少于 2、声明 unseen-scene track 时 train/test scene 重叠。

## 5. 环境与资源

| 项目 | 状态 |
|---|---|
| 推荐环境 | `/home/xjy/.conda/envs/aris-torch` 可启动 |
| Python | 3.10.20 |
| PyTorch | 2.4.1，CUDA build 12.1 |
| NumPy / PyYAML | 2.2.6 / 6.0.3 |
| torchvision | 0.19.1 |
| 缺失依赖 | scikit-learn、SciPy、pytest、ffmpeg、OpenCV、timm、transformers |
| 磁盘 | `/home` 所在盘约 1.1 TB 可用，使用率 85%；`/tmp` 约 706 GB 可用 |
| GPU selector | `scripts/select_free_gpu.py` 存在，支持 free-memory/utilization 门控与失败停止 |
| GPU 状态 | 本轮按停止边界未执行 `nvidia-smi` 或 selector，未使用 GPU |

骨架不新增依赖，使用 PyTorch/NumPy/PyYAML 与标准库 `unittest`。正式 feature extraction 仍需确认 backbone checkpoint、视频解码依赖和数据许可；不得在运行时临时联网下载权重。

## 6. 审计结论

**代码桥接可继续，正式实验不可开始。** 当前已具备 CPU synthetic dry-run 条件，但缺少全部 Tier A 数据、合规 frozen feature cache、真实 split manifest、官方 frame labels/fps 元数据和已冻结 backbone checkpoint。Ped2/Avenue 可作为先行 pipeline/pilot；由于其多场景结构不足，不能单独关闭 whole-scene/ELOS claim，ShanghaiTech 仍是后续 gated core。
