# Baseline Registry 冻结文件

**日期：** 2026-07-13  
**状态：** pre-bridge freeze pass  
**目标：** 冻结 restricted bridge 首轮 baseline / ablation 列表。  
**统一约束：** 所有首轮方法共享 frozen features、clip sampling、normal-only training split、normality head 容量、阈值协议和评测指标。不得使用异常训练标签；不得用目标异常标签调参。

## 1. Required baselines

| Baseline | purpose | claim tested | required inputs | 使用 target normal data | 使用 anomaly labels | expected compute | first-round inclusion | failure interpretation |
|---|---|---|---|---|---|---|---|---|
| raw frozen feature + kNN | 建立最小 frozen-feature audit baseline | 检查 nearest normal distance 是否跨域崩溃 | source normal features；target test features | 否 | 仅 evaluation | 低；主要为 feature cache + kNN | yes | 若很强，SRN 可能不必要；需检查 split 或 normalization leakage |
| raw frozen feature + Mahalanobis / Gaussian density | 检查简单 density head 是否足够 | head replacement 是否能解决 transfer | source normal features；shrinkage covariance | 否 | 仅 evaluation | 低 | yes | 若与 SRN 持平，SRN 贡献弱化为复杂 baseline |
| raw frozen feature + prototype / memory bank | 对齐 memory/prototype VAD family | prototype normality 是否已足够 | source normal features；prototype bank | 否 | 仅 evaluation | 低-中 | yes | 若胜过 SRN，SRN residual 不必要 |
| scene mean subtraction | 检查 SRN 是否只是 scene centering | scene-level mean 是否解释全部收益 | source normal features；source scene id | 否 | 仅 evaluation | 低 | yes, if scene id available | 若持平，SRN novelty collapse |
| background mean subtraction if computable | 检查 scene nuisance 是否可由背景均值解释 | background/appearance centering 是否足够 | 可 label-free 估计的 background/clip mean | 否 | 仅 evaluation | 低 | yes, if computable | 若持平，采用更简单方法或改作 reliability finding |
| adversarial residual only | 非平凡 domain-invariant baseline | GRL/MMD 是否已能去 scene leakage | source normal features；source scene id | 否 | 仅 evaluation | 中；小 head 训练 | yes | 若胜过/持平 SRN，SRN 不是有效主机制 |
| full minimal SRN | 检验 selective residual mechanism | SRN 是否改善 off-diagonal / low-FPR / FA-hour | source normal features；scene token；normality head | 否 | 仅 evaluation | 中；小投影头训练 | yes | 若无改善，停止 SRN scale-up |
| SRN without ELOS | 隔离 ELOS 贡献 | episodes 是否必要 | 同 full SRN，但普通 ERM/scene-balanced training | 否 | 仅 evaluation | 中 | yes | 若与 full SRN 持平，ELOS 仅作 model selection 或删除 |
| ELOS without SRN if meaningful | 检查训练原则是否单独解释收益 | ELOS 是否只是 protocol gain | raw features；episodic held-out scenes；相同 head | 否 | 仅 evaluation | 低-中 | yes, if enough scenes | 若与 SRN 持平，贡献不在 residual mechanism |
| calibration-only baseline | 区分 representation 与 threshold transfer | calibration 是否解释主要收益 | source score distribution；source validation | 否（strict track）/ 是（calibration track） | 仅 evaluation | 很低 | yes | 若 calibration-only 解释收益，SRN claim 收窄 |
| source-threshold transfer | 部署式固定阈值 | source threshold 能否迁移 | source normal validation；target test scores | 否 | 仅 evaluation | 很低 | yes | 若所有方法失败，论文转向 calibration/reliability |
| target-normal calibration track | 量化允许 target normal clips 的收益 | target normal data 是否显著改善 threshold | 预声明 target normal calibration clips | 是 | 否 | 很低 | yes, separate table | 若显著优于 strict zero-shot，必须收窄 zero-shot claim |

## 2. Optional / later baselines

| Baseline | purpose | claim tested | required inputs | 使用 target normal data | 使用 anomaly labels | expected compute | first-round inclusion | failure interpretation |
|---|---|---|---|---|---|---|---|---|
| AMCN | motion-conditioned backup | 条件 motion compatibility 是否补足 SRN | appearance/motion frozen features；normal clips | 否 | 仅 evaluation | 中 | no | 若 later 也无优势，AMCN discard |
| object-centric baseline | 对照 object/tracklet family | object relation 是否提供更强 context | detector/tracker outputs；normal clips | 否 | 仅 evaluation | 中-高 | no | 若强，SRN 需解释 object/context gap；若弱，不影响首轮 |
| retrieval baseline | 检查 factorized retrieval 是否必要 | kNN/retrieval family 是否足够 | normal bank；retrieval index | 否 | 仅 evaluation | 中 | no | 若 retrieval 强，SRN score 需重新解释 |
| masked distillation baseline | 对照 Self-Distilled MAE family | normal-only distillation 是否已足够 | MAE/student-teacher setup | 否 | 仅 evaluation | 中-高 | no | 若强，SRN 可能只作轻量替代 |
| large VLM / MLLM baseline | later diagnostic | zero-shot semantic reasoning 是否改变问题 | 大模型 API 或本地模型 | 可能 | 不应用训练异常 | 高且边界复杂 | no | 若强，也不改变 normal-only 学习主线，除非另开方向 |

## 3. 共享实验规则

- 所有首轮 baseline 必须使用同一 feature cache。
- 所有需要训练的小 head 必须共享参数量/训练轮数/early stopping 预算。
- strict zero-shot 下禁止 target normal statistics。
- target-normal calibration 必须单独成表。
- anomaly labels 只用于最终 evaluation，不用于训练、阈值、normalization 或模型选择。
- pooled frame AUC 只能作为 sanity check；主指标是 macro、off-diagonal、low-FPR、FA/hour、worst-target。

## 4. 首轮 inclusion 冻结

**首轮 yes：**

- raw frozen feature + kNN
- raw frozen feature + Mahalanobis / Gaussian density
- raw frozen feature + prototype / memory bank
- scene mean subtraction（若 scene id 可用）
- background mean subtraction（若可 label-free 计算）
- adversarial residual only
- full minimal SRN
- SRN without ELOS
- ELOS without SRN（若 scene 数量足够）
- calibration-only baseline
- source-threshold transfer
- target-normal calibration track（独立表）

**首轮 no：**

- AMCN
- object-centric baseline
- retrieval baseline
- masked distillation baseline
- large VLM / MLLM baseline

## 5. stop rules

- 若 raw/Mahalanobis/prototype 已无明显 cross-domain collapse，暂停 SRN，审计 protocol。
- 若 scene/background mean subtraction 持平 SRN，SRN 不作方法贡献。
- 若 adversarial residual 持平或胜过 SRN，SRN 降级或重构。
- 若 full SRN 改善 AUROC 但 low-FPR/FA-hour 失败，不能 claim deployability。
- 若 location-dependent recall 下降，SRN 判为过度去场景化。

## 6. 冻结结论

本 registry 关闭首轮 baseline list gate。后续 restricted bridge 若获授权，只能执行本文件中 first-round inclusion 为 yes 的项目；任何 optional baseline 都需要单独授权。
