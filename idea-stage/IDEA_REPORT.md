# Normal-Only 通用视频异常检测 Idea Discovery Report

**Direction**: Normal-Only Video Anomaly Detection on General/Public VAD Benchmarks  
**Date**: 2026-07-06  
**Pipeline**: research-wiki → research-lit → idea generation → novelty screening → local critical review → experiment planning  
**Evidence status**: 纸面验证；按用户约束未运行 pilot、未下载数据

## Executive Summary

方向值得做，但不能把“跨数据集评测”本身当成主要创新。2026-06 的预印本 *Benchmark AUC Is Not Deployable Reliability* 已用四个真实数据集和四类 frozen features 展示 same-dataset AUC 与 cross-dataset AUC 的巨大落差，简单跨域 detector 平均接近随机。因此更可辩护的主线是：**学习能剥离场景外观、保留事件动态的 normality representation，并用严格的跨场景协议证明它确实改善迁移，而非只提升对角线 AUC。**

推荐优先级：

1. **Scene-Residual Normality (SRN)**：显式分离 scene nuisance 与 event residual，最聚焦、最符合问题锚点。
2. **Appearance–Motion Conditional Normality (AMCN)**：学习“外观条件下何种运动正常”的轻量条件模型，作为机制独立的强备选。
3. **Episodic Leave-One-Scene-Out Training (ELOS)**：把未见场景作为训练 episode，方法风险较低，但新颖性风险较高，适合作为训练策略/消融而非独立论文主贡献。

## 1. Research Boundary

### Included

- 训练集仅含 normal videos；测试集含 normal + anomalous events。
- 公开 VAD 数据集，重点是跨摄像机、跨场景、跨数据集泛化。
- 一个模型或统一训练程序，不为每个目标测试数据集使用异常标签调参。
- 冻结视觉/视频 backbone + 小型可训练 normality head 优先。
- 评价关注部署可靠性：跨域退化、低误报工作点、阈值迁移与场景间方差。

### Excluded

- UCF-Crime / XD-Violence 式 weakly supervised abnormal-video training。
- 完全无监督 mixed normal/abnormal training。
- 工业异常、音频、多模态、异常类别命名与通用视频问答。
- 大规模端到端 foundation model 训练。

## 2. Literature Landscape

### 2.1 Method lineage

1. **Reconstruction / prediction era**：autoencoder、future-frame prediction 与 memory/prototype methods 从 normal clips 学习可重构/可预测模式；核心弱点是强场景绑定及异常也可能被重构。
2. **Object-centric / semantics era**：检测对象、动作、姿态与轨迹以削弱背景影响；HSC（CVPR 2023）进一步用 scene/object semantic contrast 建模多样正常模式，但其目标是 scene-aware，而不是对未见场景不变。
3. **Synthetic anomaly era**：PFMF（CVPR 2023）与 synthetic augmentation 用伪异常扩大决策边界；风险是引入异常先验、虚实 gap，并可能偏离严格 normal-only 的干净定义。
4. **Efficient masked modeling era**：Self-Distilled Masked Auto-Encoders（CVPR 2024）用 motion-weighted tokens、自蒸馏和轻量 MAE 获得很高吞吐，但包含 synthetic abnormal augmentation；它是效率基线，而非纯 normal-only 跨场景答案。
5. **Realistic benchmark/evaluation era**：Street Scene 指出 frame/pixel criteria 的定位与误报缺陷并提出 RBDC/TBDC；NWPU Campus 引入 43 场景与 scene-dependent anomalies；最新 cross-dataset audit 显示 frozen features 的同域好成绩几乎不能迁移。

### 2.2 Structural gaps

- **G1 — scene leakage**：高层 frozen features 仍编码视角、背景和密度，normality model 主要学习“来自哪个场景”。
- **G2 — transfer protocol gap**：多数工作仍以每数据集单独训练/测试和 micro-AUC 为主，跨数据集矩阵与统一阈值很少成为主结果。
- **G3 — calibration gap**：即使 ranking 尚可，源域阈值在目标域可能造成不可接受的 false alarms/hour。
- **G4 — context ambiguity**：同一动作在不同位置/场景可正常或异常；完全 scene-invariant 与完全 scene-aware 都可能失败。
- **G5 — compute/reproducibility**：复杂 object pipeline 或大模型微调难以在有限算力下稳定复现。

## 3. Recommended Datasets and Protocol

### Dataset tiers

| Tier | Dataset | Role | Caveat |
|---|---|---|---|
| A | UCSD Ped2 | 快速 smoke test 与历史可比性 | 小、已饱和，不能作为主结论 |
| A | CUHK Avenue | 单场景时空异常基线 | 异常类型少、场景固定 |
| A | ShanghaiTech | 13 场景，核心 multi-scene 训练/LOSO | 标注与场景差异需审计 |
| B | Street Scene | 真实误报与 RBDC/TBDC | 单场景但复杂、评测实现更重 |
| B | NWPU Campus | 43 场景、scene-dependent anomalies | 约 76.6 GB；当前阶段不下载 |
| B | IITB Corridor | 较长真实走廊视频、复杂异常 | 需确认许可、标签和官方 split |
| Diagnostic | UBnormal normal split/test | open-set 与定位诊断 | synthetic domain；不能使用其训练异常 |

UCF-Crime、XD-Violence 不进入主实验，因为其常用设置含异常训练视频，与冻结边界不一致。

### Four-layer evaluation

1. **Within-dataset sanity**：官方 normal-only split，报告 micro/macro AUROC 与 AUPRC。
2. **Within-dataset cross-scene**：ShanghaiTech/NWPU leave-one-scene-out；目标场景异常和标签均不可见。
3. **Cross-dataset transfer matrix**：在一个源数据集的 normal training split 建模，直接测试其他数据集；同时做 multi-source normal training → leave-one-dataset-out。
4. **Deployment-style operating points**：源域 normal validation 固定阈值，目标域不重调；报告 TPR@1%FPR、TPR@0.1%FPR、false alarms/hour、每视频 macro-AUC、bootstrap 95% CI。空间输出方法额外报告 RBDC/TBDC。

必须同时报告：对角线/非对角线平均、worst-target、scene variance、跨域降幅，以及推理 FPS/显存。不得只报告 pooled frame-level AUC。

## 4. Candidate Ideas (paper validation only)

| # | Idea | Innovation | Feasibility | Compute | Main risk |
|---|---|---|---|---|---|
| 1 | Scene-Residual Normality (SRN) | 在 frozen video features 中显式估计 scene prototype，并只对去场景 residual 建 normality density；用 LOSO regularization 防止 residual 预测 scene ID | 高：backbone 冻结，仅小投影头 + prototype bank | 低–中，约 20–60 GPUh 全套 | residual 可能同时移除 location-dependent anomaly signal |
| 2 | Appearance–Motion Conditional Normality (AMCN) | 不直接检测外观或运动异常，而建模 normal-only 条件关系 `p(motion \| appearance/context)`，减少背景 domain shift | 高：双 frozen encoder + 小 conditional head | 中，约 30–80 GPUh | optical flow/track noise；类似跨模态一致性方法可能构成先例 |
| 3 | Episodic Leave-One-Scene-Out (ELOS) | 训练时反复把一个正常场景当“未知域”，优化对未见 scene 的 normal ranking/compactness | 很高，可包裹 Idea 1/2 | 低增量成本 | domain generalization/meta-learning 思路成熟，单独新颖性不足 |
| 4 | Scene-Conditional, Scene-Agnostic Mixture | 全局 normal prototypes + 极小 scene adapter；用门控决定何时保留位置语义、何时依赖通用动态 | 中 | 中 | 容易变成模块堆叠，且“scene-agnostic”叙事变模糊 |
| 5 | Object-Relation Normality Graph | 去除绝对坐标，以对象类别、相对轨迹与交互图学习 normality | 中：依赖 detector/tracker | 中–高 | 检测错误主导；EVAL/ComplexVAD 等 prior art 接近 |
| 6 | Cross-Scene Prototype Transport | 将各 scene normal prototypes 对齐到共享原型，用 optimal transport 约束同类运动而保留 scene-specific residual | 中 | 中 | prototype matching 不稳定；OT 在 DG 中常见，创新需靠 VAD-specific formulation |
| 7 | Source-Free Rank Calibration | 仅从多源 normal score distributions 学统一分位数/尾部映射，迁移阈值而不看目标标签 | 高 | 极低 | 若允许目标 normal clips 会变成 adaptation；必须严格区分 zero-shot 与 calibration track |
| 8 | Temporal False-Alarm Suppression as Normality Evidence | normal-only 学习异常分数的持续性/变化率先验，优化低 FPR recall 而非 AUC | 高 | 低 | 可能被审稿人视为后处理；需证明跨域且不牺牲短异常 |
| 9 | Counterfactual Normal Retrieval | 从跨场景 normal bank 检索语义相似片段，比较测试片段与“正常反事实”的 motion residual | 中 | 中（检索存储较大） | nearest-neighbour audit 已显示直接检索迁移失败；必须证明 factorized retrieval 是关键差异 |
| 10 | Generalization Stress-Test Suite | 统一 cross-dataset matrix、低 FPR、FA/hour、置信区间和阈值迁移，复现实用性结论 | 很高 | 低 | 2026 cross-dataset audit 已高度重叠；仅适合作为评测贡献/基础设施 |
| 11 | Lightweight Normal-Only Masked Distillation | 只在 normal clips 上让学生重建 teacher 的 motion-sensitive tokens，并以 teacher-student residual 评分 | 高 | 中 | CVPR 2024 self-distilled MAE 很接近；须移除 synthetic anomalies 并证明跨场景机制的新意 |

## 5. Top Ideas and Novelty Assessment

### Top 1 — Scene-Residual Normality (SRN)

- **Method**：冻结一个轻量视频 backbone；从每段视频估计低维 scene token；从 clip feature 中减去可预测的 scene component；仅在 residual 上建立 prototypes/density，并用 scene-adversarial 或 leave-one-scene-out consistency 抑制 residual 的 scene 可识别性。
- **Hypothesis**：跨数据集崩溃主要来自 normality bank 编码场景身份；去除场景可预测成分能提升 off-diagonal AUC 和低 FPR recall，同时保留运动/交互异常。
- **Novelty**：7/10，`PROCEED WITH CAUTION`。HSC 是 scene-aware contrast；zxVAD/PFMF 处理 scene/domain gap；2026 audit 诊断跨域崩溃。精确 delta 必须是“normal-only feature factorization + unseen-scene protocol”，而非泛泛 domain invariance。
- **Strongest objection**：位置本身定义异常，移除 scene 会破坏必要语义。
- **Decisive ablation**：raw feature vs remove background mean vs adversarial residual vs full factorization；并按 location-dependent/non-location-dependent anomalies 分层。

### Top 2 — Appearance–Motion Conditional Normality (AMCN)

- **Method**：冻结 appearance encoder 和 motion encoder；用正常视频训练小型 conditional predictor，使当前外观/对象上下文预测允许的 motion embedding；以条件残差与 temporal inconsistency 作为异常分数。
- **Hypothesis**：绝对 appearance 或 motion 都强域相关，但二者的正常条件关系更可迁移。
- **Novelty**：6.5/10，`PROCEED WITH CAUTION`。motion-conditioned prediction 很成熟，但“frozen semantic appearance → normal motion distribution”的跨数据集 normal-only 论证可能形成新贡献。
- **Strongest objection**：只是换 feature 的 prediction baseline。
- **Decisive ablation**：appearance-only、motion-only、拼接 one-class、unconditional motion prediction、conditional model。

### Top 3 — ELOS as a training principle

- **Method**：在多场景 normal data 中进行 episodic training，每个 episode 留出一个 scene，只允许共享 normality module 在 held-out normal clips 上保持低分，同时阻止 scene classifier 从 residual 识别场景。
- **Hypothesis**：训练目标若不模拟场景迁移，跨场景能力不会自然出现。
- **Novelty**：5/10，单独作为论文偏低；建议并入 SRN 作为关键训练机制。
- **Strongest objection**：标准 domain generalization 套用。

## 6. Eliminated / Deprioritized Directions

- **纯 cross-dataset audit**：与 2026-06 Rashidi 预印本直接重叠，降级为 baseline/protocol。
- **纯 frozen DINOv2/CLIP + kNN/Mahalanobis**：已被最新 audit 系统测试，不能作为方法贡献。
- **大 VLM/MLLM zero-shot anomaly reasoning**：偏离 normal-only 学习边界且算力/复现风险更高。
- **仅 synthetic anomaly generation**：可能利用异常先验，且 PFMF/self-distilled MAE prior art 强。
- **纯 object graph**：EVAL、ComplexVAD 等已覆盖较多，工程成本也更高。

## 7. Local Critical Review

本轮未获得独立次级代理评审（当前执行约束不允许委派），因此以下仅是本地 reviewer-style 评估，不能冒充 cross-model verdict：

- 最大叙事风险是把 scene invariance 说得过满；场景既是 nuisance，也是异常定义的一部分。
- 最有价值的论文问题不是“能否完全去场景”，而是“应移除多少场景身份，同时保留 context-dependent normality”。
- 需要先建立最新 audit 的强复现 baseline；否则任何 off-diagonal 改善都可能来自预处理差异。
- 主结果必须以 leave-one-dataset-out / leave-one-scene-out 为锚，within-dataset AUC 只能作为 sanity check。
- 论文级 novelty 仍需对 2025-2026 并行工作做持续查新。

### Original Independent Review Summary

2026-07-06 通过 **DeepSeek API**、模型 **`deepseek-v4-pro`** 获得第一次真实外部独立评审。Raw response 原样保存在 `refine-logs/INDEPENDENT_REVIEW_RAW.md`；摘要文件为 `refine-logs/INDEPENDENT_REVIEW_SUMMARY.md`。本节仅摘要，不替代原文。

- Reviewer backend：DeepSeek API。
- Model：`deepseek-v4-pro`。
- Original verdict：**REVISE / NOT READY**。
- Raw file：`refine-logs/INDEPENDENT_REVIEW_RAW.md`。
- Summary file：`refine-logs/INDEPENDENT_REVIEW_SUMMARY.md`。
- Overall verdict：**REVISE / NOT READY**；当前是零实验、pre-pilot 状态，SRN 与既有 domain-invariant/disentanglement 方法的差异尚未充分成立。
- **SRN + ELOS：REVISE**。SRN 仅在最小 pilot 显著优于 adversarial disentanglement baseline 后才可作为主贡献；ELOS 应降为 supporting training principle。
- Reviewer 未认为 AMCN 更适合作为主线；AMCN 至多是有条件的 auxiliary，需证明对 SRN 的互补性并胜过 conditional prediction baselines。
- Ideas 5/9 建议放弃为贡献，10/11 降为 protocol/baseline；rank calibration 与 temporal false-alarm suppression 可保留为辅助或评估项。
- 必须补齐相关 prior work、严格分开 strict-zero-shot 与 target-normal-calibration，并完成 subtraction、ELOS-vs-ERM、scene token、context path 和 adversarial baseline 等消融。
- External reviewer 对进入 `/experiment-bridge` 的结论为 **NOT READY**。

### Revision Re-review Summary

2026-07-12，在完成 revision planning 后，通过 **`llm-chat MCP` 调用 DeepSeek API**、模型 **`deepseek-v4-pro`** 进行了简短 re-review。

- Date：2026-07-12。
- Reviewer backend：`llm-chat MCP` calling DeepSeek API。
- Model：`deepseek-v4-pro`。
- Raw file：`refine-logs/REVISION_REVIEW_RAW.md`。
- Summary file：`refine-logs/REVISION_REVIEW_SUMMARY.md`。
- Revised verdict：**READY WITH RESTRICTIONS**。
- 含义：允许进入 restricted bridge planning / minimal pilot preparation，但不等于 full experiment-bridge ready。

Restricted boundary：

- only frozen-feature audit + minimal SRN-vs-adversarial pilot；
- no large-scale training；
- no end-to-end backbone fine-tuning；
- no abnormal training labels；
- no Tier B dataset download；
- data download、GPU feature extraction 和 training 仍需用户单独授权。

2026-07-13 已完成 pre-bridge freeze pass，并生成四个冻结文件：`refine-logs/PRIOR_WORK_PATCH.md`、`refine-logs/SRN_MINIMAL_SPEC.md`、`refine-logs/BASELINE_REGISTRY.md`、`refine-logs/PROTOCOL_MANIFEST.md`。当前 execution status 仍为 **HOLD**；restricted bridge 尚未启动。

## 8. Recommendation

当前主线仍是 **SRN mechanism + ELOS training principle**。SRN 是待验证机制；ELOS 仅作为训练/验证原则，不作为独立贡献。AMCN 仍是 backup path，不进入首轮 restricted bridge。calibration / threshold transfer 是 evaluation/supporting track，必须与 strict zero-shot 分表。

**Original independent review verdict: REVISE / NOT READY.** After revision planning, DeepSeek re-review upgraded the planning status to **READY WITH RESTRICTIONS**. Current execution status remains **HOLD**: restricted bridge has not started, and data download/GPU/training require separate user authorization.

四个 freeze 文件已经生成：

- `refine-logs/PRIOR_WORK_PATCH.md`
- `refine-logs/SRN_MINIMAL_SPEC.md`
- `refine-logs/BASELINE_REGISTRY.md`
- `refine-logs/PROTOCOL_MANIFEST.md`

当前仍有未关闭事项：

- `PRIOR_WORK_PATCH.md` 中仍有 `TODO: verify` 的 prior work；
- Tier A 数据本地可用性与许可仍需确认；
- 数据下载、GPU feature extraction、训练尚未授权。

下一步不应直接进入 full `/experiment-bridge`。若用户后续授权 restricted bridge，首轮只能执行 frozen-feature audit + minimal SRN-vs-adversarial pilot，且必须遵守 no Tier B dataset download、no large-scale training、no end-to-end backbone fine-tuning、no abnormal training labels 的边界。

## Sources

- Rashidi, 2026, *Benchmark AUC Is Not Deployable Reliability* (arXiv:2606.29506): https://arxiv.org/abs/2606.29506
- Ristea et al., CVPR 2024, *Self-Distilled Masked Auto-Encoders are Efficient Video Anomaly Detectors*: https://openaccess.thecvf.com/content/CVPR2024/html/Ristea_Self-Distilled_Masked_Auto-Encoders_are_Efficient_Video_Anomaly_Detectors_CVPR_2024_paper.html
- Cao et al., CVPR 2023, *A New Comprehensive Benchmark for Semi-Supervised Video Anomaly Detection and Anticipation*: https://openaccess.thecvf.com/content/CVPR2023/html/Cao_A_New_Comprehensive_Benchmark_for_Semi-Supervised_Video_Anomaly_Detection_and_CVPR_2023_paper.html
- Sun and Gong, CVPR 2023, *Hierarchical Semantic Contrast for Scene-Aware Video Anomaly Detection*: https://openaccess.thecvf.com/content/CVPR2023/html/Sun_Hierarchical_Semantic_Contrast_for_Scene-Aware_Video_Anomaly_Detection_CVPR_2023_paper.html
- Liu et al., CVPR 2023, *Generating Anomalies for Video Anomaly Detection With Prompt-Based Feature Mapping*: https://openaccess.thecvf.com/content/CVPR2023/html/Liu_Generating_Anomalies_for_Video_Anomaly_Detection_With_Prompt-Based_Feature_Mapping_CVPR_2023_paper.html
- Singh et al., CVPR 2023, *EVAL: Explainable Video Anomaly Localization*: https://openaccess.thecvf.com/content/CVPR2023/html/Singh_EVAL_Explainable_Video_Anomaly_Localization_CVPR_2023_paper.html
- Ramachandra and Jones, WACV 2020, *Street Scene*: https://openaccess.thecvf.com/content_WACV_2020/html/Ramachandra_Street_Scene_A_New_Dataset_and_Evaluation_Protocol_for_Video_Anomaly_WACV_2020_paper.html
- Acsintoae et al., CVPR 2022, *UBnormal*: https://openaccess.thecvf.com/content/CVPR2022/html/Acsintoae_UBnormal_New_Benchmark_for_Supervised_Open-Set_Video_Anomaly_Detection_CVPR_2022_paper.html
