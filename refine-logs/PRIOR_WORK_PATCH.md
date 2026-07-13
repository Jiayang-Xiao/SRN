# Prior Work Patch 冻结文件

**日期：** 2026-07-13  
**状态：** pre-bridge freeze pass  
**适用范围：** restricted `/experiment-bridge` 前的 prior work 边界冻结；本文件不声称完成新联网查新，不下载论文全文，不下载数据集。  
**核心原则：** 已在本仓库材料中出现且有来源的论文可作为“当前已有覆盖”；DeepSeek reviewer 提到但尚未核验的论文名、年份和 venue 一律标为 `TODO: verify`。

## 1. 当前已有 paper 覆盖

| Paper / method | 当前覆盖来源 | 已支持的作用 | 限制 |
|---|---|---|---|
| Rashidi 2026, *Benchmark AUC Is Not Deployable Reliability* | `idea-stage/IDEA_REPORT.md` sources；`PRIOR_METHOD_DEFECT_TO_IDEA_MATRIX.md` | 支持 frozen features + kNN/Mahalanobis 在 cross-dataset 下存在 collapse；约束本项目不能把 cross-dataset audit 本身当主贡献 | 仍需在 `PRIOR_WORK_PATCH.md` 后续版本中核验 threshold-transfer 细节和代码/split |
| Ristea et al., CVPR 2024, *Self-Distilled Masked Auto-Encoders are Efficient Video Anomaly Detectors* | `idea-stage/IDEA_REPORT.md` sources | 说明 masked distillation / MAE 与 Idea 11 高度接近；Idea 11 降为 efficiency baseline | 仍需核验 normal-only 与 synthetic anomaly 设置细节 |
| Sun and Gong, CVPR 2023, HSC | `idea-stage/IDEA_REPORT.md` sources；traceability | 支持 scene-aware contrast 可处理 known-scene 多样性，但不等于 unseen-scene invariance | 仍需核验 HSC 的 scene/object module 与 SRN controlled context path 的精确差异 |
| Liu et al., CVPR 2023, PFMF | `idea-stage/IDEA_REPORT.md` sources | 说明 prompt-guided synthetic anomalies / adaptation 与 strict normal-only 边界冲突 | 不作为首轮 baseline |
| Singh et al., CVPR 2023, EVAL | `idea-stage/IDEA_REPORT.md` sources；traceability | 支持 object-centric / tracklet family 已有强 prior；Idea 5 降为 baseline/diagnostic | 仍需核验是否适合作为 later baseline |
| Ramachandra and Jones, WACV 2020, Street Scene | `idea-stage/IDEA_REPORT.md` sources | 支持 low false alarm、event/spatial localization protocol 的重要性 | Street Scene 不进入首轮 restricted bridge |
| Cao et al., CVPR 2023, NWPU Campus benchmark | `idea-stage/IDEA_REPORT.md` sources | 支持 multi-scene 和 scene-dependent anomalies 的必要性 | NWPU 体量大，首轮不下载、不进入 restricted bridge |
| Acsintoae et al., CVPR 2022, UBnormal | `idea-stage/IDEA_REPORT.md` sources | 可作为 diagnostic/open-set 参考 | synthetic domain；不能使用其异常训练集作为 normal-only 主证据 |

## 2. 必查 prior work 类别与冻结动作

| 类别 | reviewer 为什么要求补查 | 当前已有覆盖 | 对 SRN / AMCN / ELOS / calibration 的影响 | 高度重叠时的降级/调整 | restricted bridge 前是否必须确认 | 可在实验过程中继续补 | 检索关键词 |
|---|---|---|---|---|---|---|---|
| one-class / normal-only VAD | 固定任务边界，避免与 weakly supervised 或 mixed anomaly setting 混淆 | 当前已有 normal-only 边界描述；Self-Distilled MAE、Rashidi audit 部分覆盖 | 影响全部 claim；决定哪些 baseline 合法 | 若已有同 setting + 同机制，SRN 降为 probe 或放弃 | 是，至少确认任务边界与首轮 baseline 合法性 | 是，补完整 related work | `"normal-only" "one-class" "video anomaly detection"` |
| cross-dataset VAD | SRN 的核心动机来自跨数据集崩溃 | Rashidi 2026 已覆盖；Street Scene/NWPU 提供评测背景 | 支持 strict source→target matrix、worst-target、off-diagonal 指标 | 若已有同协议同改进，不能 claim protocol novelty | 是，确认 Rashidi 2026 与本 protocol 不冲突 | 是，补更多 cross-dataset papers | `"cross-dataset" "video anomaly detection" "normal-only"` |
| scene-invariant / scene-disentangled VAD | SRN 最大 novelty risk 是换名的 scene/domain disentanglement | HSC 覆盖 scene-aware 反方向；DeepSeek 提到 DIRT/SDG-net 等需核验 | 直接决定 SRN 是否能作 main candidate | 若已有 selective suppression + context retention，SRN 降级为 reliability probe 或停止 | 是，至少核验最接近的 scene/domain disentanglement papers | 是，但不能拖到论文 claim 后 | `"video anomaly detection" scene invariant disentangled representation` |
| domain generalization for anomaly detection | ELOS、GRL、MMD 与 leave-one-domain-out 属于 DG family | 当前仅有 reviewer 和矩阵中的 family-level 论述 | ELOS 只能作 training principle；GRL/MMD 是必需 baseline | 若 ELOS 已覆盖，不再强调 ELOS；SRN 必须靠机制差异 | 是，确认 GRL/MMD baseline 必需性 | 是 | `"domain generalization" anomaly detection leave-one-domain-out video` |
| feature disentanglement / nuisance removal | SRN subtraction 与 generic factorization 可能同构 | 当前已有 robust PCA/background subtraction/domain invariance 风险描述 | 决定 scene-predictable component 的 novelty delta | 若数学相同，SRN 改为 controlled audit 或 AMCN backup | 是，至少核验 subtraction/residualization 近邻 | 是 | `"feature disentanglement" nuisance removal scene identity video anomaly` |
| object-centric VAD | reviewer 要求将 object graph 降级为 baseline | EVAL 已覆盖；HSC 也涉及 object/scene semantics | Idea 5 不作贡献；仅 later baseline | 若首轮需要 object baseline，会扩大工程范围，因此不进首轮 | 否，首轮不实现 | 是 | `"object-centric" tracklet graph "video anomaly detection"` |
| memory / prototype VAD | SRN normality head 可能只是 memory/prototype variant | Rashidi kNN、prototype/memory family、Self-Distilled MAE 部分覆盖 | prototype/memory bank 是 baseline/head，不是贡献 | 若 prototype alignment 已覆盖 transport，Idea 6 discard | 是，确认首轮 prototype/memory baseline 定义即可 | 是 | `"video anomaly detection" memory prototype domain alignment` |
| conditional motion prediction | AMCN 直接 overlap 风险 | 当前只有 reviewer family-level 判断 | AMCN 保留为 backup/later baseline，不进首轮 | 若已有 frozen-feature conditional residual，AMCN discard | 否，除非 SRN pilot 失败后转向 AMCN | 是 | `"video anomaly detection" conditional motion appearance prediction"` |
| threshold transfer / calibration | strict zero-shot 与 target-normal calibration 必须分离 | Rashidi 2026 audit 与 rank calibration idea 已覆盖动机 | calibration 是 evaluation/supporting track，不并入 SRN 主机制 | 若 source-only calibration 已成熟，只作 baseline/protocol | 是，确认首轮阈值规则 | 是 | `"anomaly detection" threshold transfer source-only calibration EVT conformal` |
| low-FPR / false-alarm-oriented VAD evaluation | reviewer 要求低误报工作点和 FA/hour | Street Scene、Rashidi audit、当前 plan 已覆盖 | 决定主指标；pooled AUC 只能 sanity check | 若指标已有规范，沿用规范，不 claim evaluation novelty | 是，冻结指标 | 是 | `"video anomaly detection" "false alarms per hour" "low FPR"` |

## 3. reviewer 提到但必须核验的 search leads

以下条目不得直接写入 bibliography，除非后续通过 primary source 核验：

- `DIRT` / `SDG-net` / domain-adversarial video feature decomposition：`TODO: verify`
- “Domain-Invariant Feature Learning for Video Anomaly Detection”, MVA 2023：`TODO: verify`
- “Disentangled Representations for Domain-General Video Anomaly Detection”, CVPRW 2024：`TODO: verify`
- MAC / Motion-Appearance Co-Memory, AAAI 2023：`TODO: verify`
- “Learning Conditional Motion Priors for VAD”, ICCV 2023：`TODO: verify`
- MocoDAD / motion-appearance disentanglement：`TODO: verify`
- “Few-Shot Scene-Adaptive Anomaly Detection”, ICLR 2022：`TODO: verify`
- Meta-AD, TNNLS 2023：`TODO: verify`
- DeepCrowd / scene-gated normality head：`TODO: verify`
- prototype alignment for unsupervised domain adaptation：`TODO: verify`

## 4. 对主线的冻结影响

- **SRN：** 仍是 conditional main candidate。restricted bridge 可以只验证最小 SRN 是否胜过 raw、mean/background subtraction 和 adversarial residual；但论文 novelty claim 必须等待 scene/disentanglement/DG prior work 核验。
- **AMCN：** 不进入首轮 restricted bridge。只有 SRN novelty 或 motion-dominant subset 失败后，且 conditional motion prediction prior work 留出空缺，才进入 backup route。
- **ELOS：** 冻结为 SRN 的 training principle / validation principle。不能作为独立贡献。
- **calibration：** 冻结为 evaluation/supporting track。strict zero-shot 与 target-normal calibration 必须分开表。

## 5. restricted bridge 前必须确认 vs 可后补

**restricted bridge 前必须确认：**

1. 首轮 baseline 不违反 normal-only 边界。
2. GRL/MMD 或等价 adversarial residual 是必要 non-trivial baseline。
3. strict zero-shot 与 target-normal calibration 的数据许可边界。
4. low-FPR、FA/hour、macro AUROC、worst-target 是主指标。
5. reviewer 提到的具体论文名仍未核验，不得作为已证实事实写入论文。

**可在实验过程中继续补：**

1. AMCN 相关 conditional prediction 全量查新。
2. object-centric / retrieval / masked distillation later baselines 的代表方法筛选。
3. prototype transport / prototype alignment 更细粒度比较。
4. Street Scene、NWPU、IITB Corridor 的扩展协议文献。

## 6. 当前冻结结论

本文件关闭的是 **prior-work patch 结构与风险应对策略**，不是完整 bibliography。当前状态允许进入“文档已冻结、但执行需授权”的 restricted bridge 准备状态；若后续发现 SRN 被直接覆盖，应立即降级为 reliability probe、转向 AMCN backup，或返回 idea discovery。
