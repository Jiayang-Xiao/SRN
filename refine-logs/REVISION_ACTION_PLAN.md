# DeepSeek 独立评审后的修订行动计划

**日期：** 2026-07-12  
**外部评审来源：** `refine-logs/INDEPENDENT_REVIEW_RAW.md`  
**评审后端/模型：** 通过 `llm-chat MCP` 调用 DeepSeek API / `deepseek-v4-pro`  
**保留的原始外部结论：** **REVISE / NOT READY**  
**本轮范围：** 仅做研究方案修订规划；未下载数据、未训练、未使用 GPU、未产生新实验结果。

## 问题锚点

- **底层问题：** 在 normal-only VAD 中，模型部署到未见场景或跨数据集时，frozen feature 与 normality score 往往编码 source scene 身份、背景、视角和人群密度，而不是可迁移的事件正常性。
- **必须解决的瓶颈：** 在不使用异常训练样本、不使用目标异常标签、不偷看目标测试分布的前提下，减少 scene-identifying nuisance leakage，同时保留 location-dependent anomaly 所需的上下文信息。
- **非目标：** 不声称完全 scene-invariant；不把评测指标套件包装成主贡献；不把 ELOS 当独立创新；在 Gate 1 未关闭前不进入 `/experiment-bridge`。
- **成功条件：** 形成一个保守、可证伪的 SRN 中心方案：prior work 边界可核验，数学定义冻结，baseline 冻结，strict zero-shot 与 target-normal calibration 协议分离，并有最小 pilot gate。

## 1. Reviewer 批评清单

| ID | Reviewer 原始观点摘要 | 影响 | 严重程度 | 进入 `/experiment-bridge` 前是否必须解决 | 需要修改的设计/文件 |
|---|---|---|---|---|---|
| C01 | 当前没有 pilot 数据，直接投入完整实现预算过早。 | feasibility, claim strength | blocking | 是 | 在 `EXPERIMENT_PLAN.md` 中冻结 pilot-only gate：frozen-feature audit + SRN-vs-adversarial baseline，不做 scale-up。 |
| C02 | SRN 的 subtraction 与 domain-invariant / adversarial disentanglement、通用 nuisance removal 高度相似。 | novelty, prior work | blocking | 是 | 增加 PW02/PW04/PW05 prior-work patch；明确 SRN 相对 mean subtraction、GRL/MMD、conditional factorization 的 novelty delta。 |
| C03 | 尚未证明 residual 比普通 domain-invariant space 更 event-specific。 | claim strength, experiment design | blocking | 是 | 同时要求 scene-ID probe、event/motion retention probe 与 low-FPR transfer metrics；不能只靠 scene-probe 下降宣称成功。 |
| C04 | 移除 scene-predictable component 可能同时移除正常 motion/layout 线索，导致误报增加。 | feasibility | major | 是 | 将 SRN 表述为 selective suppression，而非 full invariance；加入 context-retention guardrail 与 over-removal diagnostics。 |
| C05 | controlled context path 描述含糊，可能重新引入 source-scene leakage。 | feasibility, experiment design | blocking | 是 | 明确 context path 的容量、允许输入、target-time freezing，以及 context on/off/capacity ablation。 |
| C06 | ELOS 本质接近 leave-one-domain-out / meta-learning，不应作为独立贡献。 | novelty | major | 是 | 将 ELOS 合并为 SRN 的训练/模型选择原则，不作为 numbered contribution。 |
| C07 | ELOS episode 构造和防作弊机制未定义。 | feasibility, experiment design | blocking | 是 | 定义 whole-scene holdout episode；禁止用 frame masking 冒充 ELOS；审计低层 scene leakage。 |
| C08 | AMCN 与 conditional future prediction / motion-appearance 方法重叠。 | novelty, prior work | major | 是 | AMCN 仅保留为 backup/auxiliary，等待 PW07；只与 conditional/unconditional prediction baseline 比较。 |
| C09 | Ideas 4-11 造成 contribution sprawl，且多数是成熟模块或评测协议。 | novelty, claim strength | major | 是 | 收敛到一个 dominant mechanism；辅助 idea 按第 3 节降级或放弃。 |
| C10 | stress-test metrics 是基础设施，不是技术主贡献。 | claim strength | major | 是 | stress-test suite 只作为 evaluation contract / appendix，不作为论文主 claim。 |
| C11 | “frozen/lightweight” 与过多 trainable heads 冲突。 | feasibility | major | 是 | 首轮复杂度预算：frozen backbone、一个 scene/residual interface、一个 normality head；AMCN/calibration 走独立 track。 |
| C12 | strict zero-shot 与 target-normal calibration 混在一起。 | experiment design, claim strength | blocking | 是 | 分离协议、调参数据、阈值规则和结果表。 |
| C13 | source-rank calibration 假设 score ordering 能跨域迁移，风险很高。 | feasibility, experiment design | major | 是 | calibration 作为 evaluation/supporting track；比较 raw、z-score、EVT/quantile、source-threshold、target-normal calibration。 |
| C14 | 缺少关键 baseline：GRL/MMD、conditional prediction、ERM/ELOS、simple normalization。 | experiment design | blocking | 是 | 运行前冻结 baseline registry。 |
| C15 | 必须报告 macro、low-FPR、FA/hour，以及标签允许时的 anomaly-type stratification。 | experiment design | major | 是 | 实验前冻结 metric schema 和 stratification rules。 |
| C16 | Reviewer 提到的部分论文名可能只是 search lead，不是已验证 citation。 | prior work | blocking | 是 | reviewer 给出的论文名必须经 primary source 核验后才能进入 bibliography；在 `PRIOR_WORK_PATCH.md` 记录 overlap/action。 |

**需要明确保留的冲突：**

- **pilot 阶段冲突：** DeepSeek 认为 pilot 应在 `/experiment-bridge` 前完成；本地 workflow 可能把 `/experiment-bridge` 定义为执行 pilot 的入口。本计划不掩盖该冲突。当前执行状态保持 hold，直到 Gate 1 关闭且用户选择 pre-bridge pilot 或 restricted bridge。
- **synthetic toy 冲突：** DeepSeek 提到可做 toy demonstration。本项目可将 toy data 作为代码 sanity check，但不能用它关闭 public normal-only VAD 的科学 gate。
- **calibration 术语冲突：** 原先的 “source-free rank calibration” 改为更明确的两条 track：`source-threshold transfer` 不使用目标统计；`target-normal calibration` 单独声明 target normal budget。

## 2. Prior Work Patch 清单

本节是检索计划，不是 verified bibliography。本轮不下载数据集，也不批量下载论文全文。

| PW | 关键词 | 为什么必须补查 | 影响 idea | 若发现高度重叠工作 | 推荐检索 query | 预期产出文件 |
|---|---|---|---|---|---|---|
| PW01 | one-class / normal-only VAD | 固定任务边界，避免把 weakly supervised VAD 与 normal-only claim 混用。 | 全部 | 若同 setting 已有相同方法，停止 SRN novelty claim。 | `"normal-only" "one-class" "video anomaly detection" public dataset` | `refine-logs/PRIOR_WORK_PATCH.md` |
| PW02 | scene-invariant / scene-disentangled VAD | 直接检验 SRN 是否只是 scene/domain disentanglement 换名。 | SRN, ELOS, mixture | 若已有 subtraction + context retention，SRN 不再作 main method；若只有 global invariance，则收窄 SRN delta。 | `"video anomaly detection" scene invariant disentangled representation` | 同上 |
| PW03 | cross-dataset / cross-scene VAD | 确定已有 transfer protocol 和失败结论。 | SRN, calibration, stress-test | 不把 audit 当贡献，只在已知协议下声称机制提升。 | `"cross-dataset" "video anomaly detection" "normal-only"` | 同上 |
| PW04 | domain generalization for anomaly detection | ELOS、GRL、MMD、leave-one-domain-out training 的最近邻 family。 | SRN, ELOS, prototype transport | 若 ELOS 已覆盖，只保留为 baseline/training detail。 | `"domain generalization" anomaly detection leave-one-domain-out video` | 同上 |
| PW05 | feature disentanglement / nuisance removal | 检查 subtraction、orthogonality、residualization 与 adversarial scene suppression。 | SRN, mixture, transport | 若数学形式相同，转向 reliability finding 或 AMCN。 | `"feature disentanglement" nuisance removal scene identity video anomaly` | 同上 |
| PW06 | calibration / threshold transfer | 检查 EVT、conformal、source-only score normalization、fixed-threshold transfer。 | calibration, temporal, evaluation | 若已成熟，calibration 只作 evaluation track。 | `"anomaly detection" threshold transfer source-only calibration EVT conformal` | 同上 |
| PW07 | conditional motion prediction / appearance-motion consistency | 直接检验 AMCN 重叠。 | AMCN | 若已有 frozen-feature conditional residual，AMCN 变为 baseline 或 discard。 | `"video anomaly detection" conditional motion appearance prediction co-memory` | 同上 |
| PW08 | object-centric / tracklet / graph VAD | 确认 Idea 5 降级，并选择代表 baseline。 | object graph, stress-test | 只保留代表性 object/tracklet 方法作 baseline。 | `"object-centric" tracklet graph "video anomaly detection" EVAL` | 同上 |
| PW09 | memory / prototype VAD | 检查 memory-bank、prototype alignment、domain-aligned prototypes。 | SRN head, transport, retrieval | prototype 默认只作 normality head，除非 residual prototype gap 明确存在。 | `"video anomaly detection" memory prototype domain alignment cross scene` | 同上 |
| PW10 | meta-learning / few-shot scene adaptation VAD | 验证 ELOS 是否已被覆盖，并区分 adaptation 与 zero-shot。 | ELOS, mixture | 任何 target adaptation 结果必须进入 calibration/adaptation track。 | `"meta-learning" "scene adaptive" "video anomaly detection"` | 同上 |
| PW11 | masked distillation / Self-Distilled MAE | 确认 Idea 11 overlap 和 baseline 设定。 | masked distillation | 只作 efficiency baseline；不能因移除 synthetic anomalies 就声称 novelty。 | `"self-distilled masked autoencoder" "video anomaly detection"` | 同上 |
| PW12 | low-FPR / FA/hour VAD evaluation | 建立 operational metric 与 alarm rule 的已有规范。 | calibration, temporal, evaluation | 作为 metric contract，除非出现新科学发现。 | `"video anomaly detection" "false alarms per hour" "low FPR"` | 同上 |

`PRIOR_WORK_PATCH.md` 必须输出：`claim -> verified paper -> mechanism/setting -> overlap level -> action`。DeepSeek 提到的 DIRT、SDG-net、MAC、MocoDAD、Meta-AD、DeepCrowd 等，在核验前只能作为 search seed。

## 3. Idea 修订决策

| # | Idea | 决策 | 理由 |
|---|---|---|---|
| 1 | SRN | **保留为 main candidate；需要继续 prior search** | 仍最贴合 problem anchor，但只能作为 selective、capacity-constrained residualization，并必须带 context-retention diagnostics。只有 prior work 未直接覆盖且 pilot 胜过 GRL/MMD/mean-subtraction controls，才可作 main contribution。 |
| 2 | AMCN | **保留为 auxiliary/backup；需要继续 prior search** | 不默认升主线。只有 PW07 显示空缺，且 SRN 无法处理 motion-dominant failures 时，才作为 backup mainline。 |
| 3 | ELOS | **合并进 SRN** | 仅作为 training/model-selection principle；通过 ELOS-vs-ERM ablation 检验，不单独 claim novelty。 |
| 4 | Scene-conditional/agnostic mixture | **条件性 auxiliary** | 仅当 SRN 损害 location-dependent anomalies 时再启用；否则属于 contribution sprawl。 |
| 5 | Object-relation graph | **baseline；不作贡献** | object/tracklet prior art 风险高，且 detector/tracker confound 大。 |
| 6 | Prototype transport | **继续查新；大概率合并或放弃** | 只有 residual prototypes 仍明显 scene-bound 且 PW09 留出真实 gap 时才考虑。 |
| 7 | Calibration / threshold transfer | **evaluation track；可能作为 supporting contribution** | 部署重要但 family 成熟。strict source-threshold transfer 与 target-normal calibration 必须分表。 |
| 8 | Temporal false-alarm suppression | **baseline/protocol only** | 比较简单 smoothing/hysteresis；除非简单方法无法解释关键失败，否则不研发 learned module。 |
| 9 | Counterfactual retrieval | **discard** | 与 kNN/memory/retrieval family 太接近，且不独立于 SRN。 |
| 10 | Generalization stress-test suite | **必要 evaluation infrastructure** | 不作主贡献；用于约束 claim，防止 pooled-AUC 过度乐观。 |
| 11 | Normal-only masked distillation | **efficiency baseline** | 与 Self-Distilled MAE overlap 高；移除 synthetic anomalies 不足以构成贡献。 |

额外判断：

- **SRN 是否仍适合作为主线：** 是，但只是有条件的主线。
- **ELOS 是否只能作为 SRN 训练原则：** 是，不作独立贡献。
- **AMCN 是否应提升为主线备选：** 是，作为 backup，而非与 SRN 并列打包。
- **calibration / threshold transfer 是否是贡献：** 默认是 evaluation track；只有出现稳定且不依赖 target statistics 的 FA/hour 改善时，才可能是 supporting contribution。
- **stress-test suite 是否是主贡献：** 否，只是评测基础设施。

## 4. 修订后的主假设

**中文版本：**  
在 normal-only VAD 中，跨场景失败的一部分来自 frozen representation 中强烈标识 source scene、但与短时事件动态弱相关的 nuisance leakage。若只抑制与场景身份高度相关且受容量约束的成分，同时通过 leave-one-scene validation、context-retention diagnostics 和低误报指标限制过度去场景化，则 SRN 可能比 raw feature、简单均值/背景减法和标准 adversarial invariance 更好地改善未见场景下的固定 source-threshold 工作点。

**英文版本（用于论文表述）：**  
In normal-only video anomaly detection, part of the cross-scene failure may come from nuisance leakage in frozen representations: components that strongly identify the source scene but are weakly related to short-term event dynamics. If a capacity-constrained mechanism suppresses only those scene-identifying components, while leave-one-scene validation, context-retention diagnostics, and low-false-alarm metrics prevent over-invariance, SRN may improve fixed-source-threshold operation on unseen scenes over raw features, trivial mean/background subtraction, and standard adversarial invariance.

**可证伪条件：**

- residual 上的 linear scene-ID probe 没有下降。
- event/motion retention 或 location-dependent anomaly recall 明显下降。
- 固定 source threshold 下的 low-FPR recall 或 FA/hour 没有改善。
- 在相同 frozen feature 与 normality head 下，GRL/MMD 或简单 mean/background subtraction 与 SRN 持平。
- prior-work patch 找到同样 selective residual interface + normal-only VAD protocol 的已有方法。

**若实验失败，说明：** scene leakage 可能不是当前 feature 下的主瓶颈；residual mechanism 可能删除了有用 event/context 信息；fixed-threshold 失败可能主要是 calibration 问题；或 SRN 与已有 domain generalization / disentanglement 方法没有实质差异。

## 5. 修订后的贡献表述

### 保守叙事

- **Claim：** SRN 是用于测量 scene leakage reduction 与 context retention 权衡的 controlled probe。
- **主贡献：** 一个可证伪协议和最小 residual mechanism，用于检验 selective scene suppression 是否改善 low-FPR transfer。
- **辅助角色：** ELOS 是 validation/training contract；calibration 是独立 evaluation track。
- **适用条件：** novelty delta 有限，但 reliability finding 清晰、稳定、可复现。

### 方法中心叙事

- **Claim：** capacity-constrained SRN 选择性抑制 scene-identifying nuisance，同时保留 anomaly semantics 所需上下文。
- **主贡献：** SRN residual/context interface、normal-only objective 与 target-time freeze rules。
- **辅助角色：** ELOS 用 held-out scenes 验证 residual；calibration 仍为 post-hoc track。
- **适用条件：** prior work 未直接覆盖 SRN interface，且 pilot 胜过 GRL/MMD/mean-subtraction controls。

### 评测与可靠性叙事

- **Claim：** normal-only VAD 的部署可靠性需要区分 representation transfer 与 threshold/calibration transfer。
- **主贡献：** 围绕 fixed source threshold、low-FPR recall 和 FA/hour 的可靠性分析，SRN 只是其中一个 controlled method。
- **辅助角色：** source-threshold transfer 与 target-normal calibration 明确分表；stress-test suite 是 infrastructure。
- **适用条件：** SRN novelty 较弱，但 calibration/metric findings 强，并且超出现有 audit。

**AMCN/SRN 关系：** SRN 仍是 primary，除非 PW02/PW05 或 pilot 结果使其失效。AMCN 是处理 motion-conditioned failures 的机制性 backup，不应与 SRN 堆叠成双主线。

## 6. 必需 Baseline 与 Ablation 清单

| Baseline / ablation | 验证的 claim | 对应 reviewer 批评 | 结果不好时如何解释 | 是否属于首轮最小实验 |
|---|---|---|---|---|
| raw frozen feature + kNN | 证明 cross-domain collapse 存在，naive nearest normal 不够。 | C01, C15 | 若很强，SRN 可能不必要；需检查 protocol leakage。 | 是 |
| raw frozen feature + Mahalanobis/Gaussian density | 证明单换 normality head 不足以解决 transfer。 | C14 | 若与 SRN 持平，贡献转向 simple density baseline。 | 是 |
| scene mean subtraction | 简单 scene centering baseline。 | C02, C14 | 若与 SRN 持平，SRN novelty collapse。 | 有 scene ID 时是 |
| background mean subtraction | 检查 nuisance removal 是否只是 background centering。 | C02, C04 | 若与 SRN 持平，采用更简单方法或改作 reliability finding。 | 若 background estimate 不用标签则是 |
| adversarial residual / GRL scene classifier | 主要 domain-invariant baseline。 | C02, C03, C14 | 若 GRL 胜出或持平，SRN 不能作方法贡献。 | 是 |
| MMD-style invariance | 非 adversarial alignment baseline。 | C02, C14 | 若 MMD 持平，SRN 必须重构或放弃。 | 首轮可选，论文 claim 前必须有 |
| full SRN | 检验 selective scene residual mechanism。 | 全部 SRN 批评 | 若 low-FPR/FA-hour 无改善，停止 SRN scale-up。 | 是 |
| SRN without ELOS | 检查 episodes 是否超过 ERM。 | C06, C07 | 若与 full SRN 相同，ELOS 只作 model selection 或删除。 | 是 |
| ELOS without SRN | 检查训练协议是否单独解释增益。 | C06, C14 | 若与 SRN 持平，贡献不是 residual mechanism。 | 是 |
| learned scene token vs random/constant token | 检查 scene token 是否真正承载 scene component。 | C03, C07 | 若无退化，scene branch 只是装饰。 | 是 |
| context path on/off/capacity | 检查 context 是否被保留且不泄漏。 | C04, C05 | 若 context path 有害或泄漏，则删除或限容。 | 是 |
| AMCN baseline | 检查 motion-conditioned backup。 | C08 | 若 conditional baselines 持平，AMCN 变 baseline/discard。 | 否，除非 SRN 失败 |
| calibration-only baseline | 区分 representation 与 threshold transfer。 | C12, C13 | 若 calibration 解释全部增益，SRN claim 变弱。 | 是，作为 evaluation track |
| source-threshold transfer | 检验部署固定阈值。 | C12, C13, C15 | 若所有方法都失败，论文可能转向 calibration/reliability。 | 是 |
| target-normal calibration track | 量化允许 target normal data 的收益。 | C12, C13 | 若 target-normal 明显占优，strict zero-shot claim 必须收窄。 | 不属于 strict 首轮 |
| per-scene macro vs micro metrics | 防止 pooled-AUC 掩盖场景失败。 | C15 | 若 macro 变差，SRN 不具备部署可靠性。 | 是 |
| low-FPR metrics | 检验真实工作点。 | C15 | 若 AUROC 提升但 low-FPR 失败，claim 很弱。 | 是 |
| FA/hour | 检验 operational false alarms。 | C15 | 若 FA/hour 变差，不得声称 deployability。 | 是 |
| location-dependent vs non-location-dependent stratification | 检查过度去场景化风险。 | C04, C15 | 若 location-dependent recall 下降，限制 context path 或停止 SRN。 | 仅在标签/映射允许时 |

## 7. 最小数学定义草案

本节是 specification draft，不是实现。

### 数据与 frozen features

- normal 训练 clip：\(x_i \in \mathcal{D}^{src}_{normal}\)，若可用则有 source scene/domain id \(s_i\)。
- frozen feature extractor：\(z_i = f_\theta(x_i) \in \mathbb{R}^d\)，其中 \(\theta\) 对所有 track 冻结。
- strict zero-shot target clips：\(x_j^{tgt}\) 仅在测试时使用；不能用于训练、模型选择、阈值、normalization 或统计估计。
- target-normal calibration track：声明的 \(\mathcal{D}^{tgt}_{normal-cal}\) 只能用于 calibration 模块/表格，不能混入 strict zero-shot 结果。

### Scene token 与 prototype

- scene token estimator：\(c_i = g_\phi(z_i) \in \mathbb{R}^k\)，其中 \(k\) 很小，并受容量约束。
- 可选 source-scene prototype：\(p_s = \frac{1}{|\mathcal{D}_s|}\sum_{i:s_i=s} c_i\)，用于 source-scene diagnostics 和 episode 构造。
- strict zero-shot 下不估计 target-scene prototype。

### Scene-predictable component

- scene component predictor：\(\hat{u}_i = h_\psi(c_i) \in \mathbb{R}^d\)。
- 容量约束：\(k \ll d\)、低秩/瓶颈 \(h_\psi\)，以及可选 norm penalty \(\|\hat{u}_i\|_2^2\)，避免该分支吸收全部 event 信息。

### Residual event feature

- residual：\(r_i = P(z_i - \hat{u}_i)\)，其中 \(P\) 是小 projection 或 identity。
- controlled context：\(q_i = a_\omega(c_i)\)，可选、低容量、target-time frozen。
- score input：\(e_i = [r_i; \lambda q_i]\)，\(\lambda\) 固定或只在 source validation 上选择。

### Normality score

首轮 pilot 允许：

- kNN/prototype score：\(A(x_i)=\min_{m \in \mathcal{M}_{normal}}\|e_i-m\|_2^2\)。
- Gaussian/Mahalanobis score：\(A(x_i)=(e_i-\mu)^\top \Sigma^{-1}(e_i-\mu)\)。

raw-feature、adversarial、ELOS-only 与 SRN variants 应尽量使用同一个 normality head。

### Scene-information suppression

- scene adversary：\(d_\eta(r_i)\) 预测 \(s_i\)。SRN 最小化 normality/source losses，同时通过 GRL 或等价 adversarial objective 最大化 scene confusion。
- 可选非 adversarial penalty：\(r_i\) 与 source scene id 之间的 MMD 或 HSIC。它们默认是 baseline/control，不自动算作 SRN 组件。

### ELOS episode

对于 episode \(t\)：

- 将 source scenes 分为 support scenes \(\mathcal{S}_{sup}^{(t)}\) 和 held-out normal scene \(\mathcal{S}_{ho}^{(t)}\)。
- 只在 support normal clips 上拟合/更新 SRN 和 normality state。
- 验证 held-out normal clips 在不适配 held-out scene 的情况下仍得到低 anomaly score。
- 必须 whole-scene holdout；frame masking 不能替代 ELOS。

### 总体目标

最小训练目标：

\[
\mathcal{L} =
\mathcal{L}_{normal}(e_i)
+ \alpha \mathcal{L}_{scene-pred}(z_i, c_i)
- \beta \mathcal{L}_{scene-cls}(d_\eta(r_i), s_i)
+ \gamma \mathcal{L}_{capacity}(\hat{u}_i, c_i)
+ \delta \mathcal{L}_{ELOS}
\]

其中：

- \(\mathcal{L}_{normal}\)：source normal clips 上的 compactness/density objective。
- \(\mathcal{L}_{scene-pred}\)：允许 \(c_i\) 捕获受限的 scene-predictable component。
- \(-\mathcal{L}_{scene-cls}\)：抑制 residual \(r_i\) 中的 scene identity。
- \(\mathcal{L}_{capacity}\)：瓶颈、norm 或 orthogonality constraints。
- \(\mathcal{L}_{ELOS}\)：held-out scene normal score consistency 与 model-selection criterion。

### 必须组件与可选组件

- **首轮 pilot 必须有：** frozen features、scene token、residual feature、raw/kNN 或 Mahalanobis normality head、adversarial 或显式 scene-leakage suppression baseline、ELOS-vs-ERM comparison、fixed source threshold。
- **可选 regularizers：** MMD/HSIC、orthogonality penalty、prototype transport、learned temporal smoothing、AMCN branch。
- **首轮 pilot 禁止：** end-to-end backbone tuning、target-test normalization、target anomaly labels、大规模 multi-dataset training。

### 避免删除 location-dependent anomaly signal

- 保留低容量且 target-time frozen 的 scene/context path，而不是删除全部 context。
- 同时测量 scene-ID leakage 和 event/motion retention；不能只接受 scene-probe reduction。
- 只有在公开标签或预审计映射存在时，才做 location-dependent anomaly stratification。
- 加入 context on/off 与 capacity sweep；若 context removal 改善 scene probe 但损害 location-dependent recall，说明 SRN 过度 invariant。

### 检查过度去场景化

- 比较 raw、mean subtraction、GRL、SRN without context、SRN with controlled context。
- 报告 source normal compactness、target low-FPR recall、FA/hour 和 location-dependent recall。
- 失败模式：residual 看似 scene-invariant，但 normal motion/layout modeling collapse；这会否证主假设。

### 协议信息许可

- **Strict zero-shot：** 仅 source normal clips 可用于训练、验证和阈值；不使用 target normal statistics、target score distribution、target threshold 或 target adaptation。
- **Target-normal calibration：** 声明的 target normal clips 可用于 calibrate thresholds 或 score maps；不能使用 target anomalies；结果必须单独成表，不能与 strict zero-shot 混合。

## 8. 进入 Experiment-Bridge 前的 Gate 条件

正常 `/experiment-bridge` 前必须关闭全部 Gate 1。通过 Gate 1 不等于授权下载数据、使用 GPU 或训练。

| Gate | 通过条件 | 证据产物 | 状态 |
|---|---|---|---|
| G1.1 Prior-work verification | PW01-PW12 经 primary sources 核验；完成 overlap/action table。 | `refine-logs/PRIOR_WORK_PATCH.md` | OPEN |
| G1.2 SRN coverage decision | SRN 未被直接覆盖，或已正式 reframed/pivoted。 | novelty delta table | OPEN |
| G1.3 Minimal math frozen | 将第 7 节转为稳定 spec，包含 losses、inference、target-time freeze。 | `refine-logs/SRN_MINIMAL_SPEC.md` 或 plan appendix | PARTIAL |
| G1.4 Baseline list frozen | 第 6 节 baselines、共享预算和 stop rules 固定。 | `refine-logs/BASELINE_REGISTRY.md` 或更新后的 plan | PARTIAL |
| G1.5 Data protocol frozen | 数据许可、split、预处理、source-target directions、metrics、threshold、smoothing rules 固定。 | protocol manifest | OPEN |
| G1.6 Track separation frozen | strict zero-shot 与 target-normal calibration 有独立允许输入和结果表。 | protocol manifest | PARTIAL |
| G1.7 First-round scope frozen | 只允许 frozen-feature audit + minimal SRN-vs-GRL pilot；不做 full matrix，不 scale-up。 | 更新后的 experiment plan | PARTIAL |
| G1.8 Normal-only guarantee | 不使用异常训练标签、target anomaly data 或隐藏 target-test statistics。 | protocol manifest | OPEN |
| G1.9 Resource authorization | 数据下载和 GPU 使用需要用户单独授权。 | 后续用户批准 | OPEN |

## 9. Cross-Model Re-review 结果

由于 `llm-chat MCP` 已配置，且本计划改变了 bridge gate，2026-07-12 已进行一次短 DeepSeek re-review，并保存为：

- 原始返回：`refine-logs/REVISION_REVIEW_RAW.md`
- 摘要：`refine-logs/REVISION_REVIEW_SUMMARY.md`

**Re-review verdict：** **READY WITH RESTRICTIONS**。

Reviewer 同意首轮只能是 frozen-feature audit + minimal SRN pilot。它仍要求在 restricted bridge 启动前冻结 SRN mathematical spec、prior-work patch、baseline registry 和 data/protocol separation。

## 10. 需要同步的追踪文件

本行动计划需要同步：

- `refine-logs/EXPERIMENT_PLAN.md`：Gate 1、首轮范围和 restricted bridge 边界。
- `refine-logs/EXPERIMENT_TRACKER.md`：R1-R8 修订 gate 和 re-review 状态。
- `research-wiki/traceability.md`：reviewer criticism 到 revision decision 的追踪。
- `MANIFEST.md`：登记本修订计划和 re-review 产物。

## 11. 最终结论

**当前规划结论：READY WITH RESTRICTIONS。**

**当前执行状态：** 本轮不启动 `/experiment-bridge`。restricted bridge 的边界已经定义，但文档 gate 仍需冻结，数据下载/GPU 使用仍需用户单独授权。

restricted first-round `/experiment-bridge` 边界：

- 不做大规模训练；
- 不做 end-to-end backbone fine-tuning；
- 只做 frozen-feature audit + minimal SRN-vs-adversarial pilot；
- 不使用异常训练标签；
- 未经用户单独授权，不下载数据、不运行 GPU 命令。

启动 restricted bridge 前最多五个必做下一步：

1. 完成 `PRIOR_WORK_PATCH.md`，对 PW01-PW12 做 primary-source verification。
2. 将 SRN mathematical spec 和 complexity budget 冻结为 `SRN_MINIMAL_SPEC.md`。
3. 冻结 `BASELINE_REGISTRY.md`，包含 GRL/MMD、mean/background subtraction、ELOS/ERM、AMCN 和 calibration controls。
4. 冻结 strict zero-shot vs target-normal calibration protocol manifest，包含 fixed source threshold、macro/low-FPR/FA-hour metrics，以及不得使用 hidden target statistics。
5. Gate 1 关闭后，请用户选择 reviewer 要求的 pilot 是作为 pre-bridge task 执行，还是作为 restricted `/experiment-bridge` 的唯一首轮范围。

这个 **READY WITH RESTRICTIONS** verdict 将首轮 `/experiment-bridge` 边界固定为：不做大规模训练，不做 end-to-end backbone fine-tuning，只做 frozen-feature audit + minimal SRN-vs-adversarial pilot。
