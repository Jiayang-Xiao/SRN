# SRN 最小规格冻结文件

**日期：** 2026-07-13  
**状态：** pre-bridge freeze pass  
**目标：** 冻结 restricted bridge 首轮 minimal SRN pilot 的数学定义与实现边界。  
**硬约束：** 不做 end-to-end backbone fine-tuning；不使用异常训练标签；不下载数据；不训练；不使用 GPU；后续任何执行都需用户单独授权。

## 1. 符号与 frozen feature 表示

- normal 训练 clip：\(x_i \in \mathcal{D}^{src}_{normal}\)。
- 若数据集提供或可从官方 split 稳定得到 scene/domain id，则记为 \(s_i\)；不得人工使用异常标签构造 \(s_i\)。
- frozen feature extractor：\(z_i=f_\theta(x_i)\in\mathbb{R}^d\)，其中 \(\theta\) 在首轮 pilot 中完全冻结。
- 首轮允许的 feature 来源：预先冻结的视觉/视频 backbone feature cache。若需要提取 feature，必须另行获得数据下载/GPU 授权。
- 异常标签只允许在 test-time evaluation 中使用，不能用于训练、阈值选择、normalization 或模型选择。

## 2. scene token / scene prototype

- scene token estimator：\(c_i=g_\phi(z_i)\in\mathbb{R}^k\)，其中 \(k \ll d\)。
- \(g_\phi\) 必须是低容量模块，例如线性层、小 MLP 或低秩 projection；首轮不得使用大型 transformer adapter。
- source-scene prototype 可定义为：

\[
p_s=\frac{1}{|\mathcal{D}^{src}_{normal,s}|}\sum_{i:s_i=s}c_i
\]

- 若 scene id 不可靠或 unavailable，则 scene prototype 只能用 source normal clustering 作为 diagnostic，不可作为主 claim。
- strict zero-shot 下不得估计 target-scene prototype。

## 3. scene-predictable component

- scene-predictable component：

\[
\hat{u}_i=h_\psi(c_i)\in\mathbb{R}^d
\]

- \(h_\psi\) 是受容量约束的 predictor，用于从 scene token 预测 frozen feature 中可由 scene identity 解释的成分。
- 容量约束包括至少一种：
  - \(k\) 小；
  - low-rank projection；
  - \(\|\hat{u}_i\|_2^2\) penalty；
  - orthogonality / decorrelation penalty；
  - scene component variance budget。

## 4. residual event feature

- residual event feature：

\[
r_i=P(z_i-\hat{u}_i)
\]

- \(P\) 可以是 identity、线性 projection 或低容量 MLP。
- controlled context path：

\[
q_i=a_\omega(c_i)
\]

其中 \(a_\omega\) 低容量、target-time frozen，只用于保留 location/context-dependent anomaly 所需的有限上下文。

- normality head 的输入：

\[
e_i=[r_i;\lambda q_i]
\]

\(\lambda\) 必须固定，或只在 source normal validation 上选择。

## 5. normality score

首轮最小 pilot 允许两类 score：

1. kNN / prototype score：

\[
A(x_i)=\min_{m\in \mathcal{M}_{normal}}\|e_i-m\|_2^2
\]

2. Gaussian / Mahalanobis score：

\[
A(x_i)=(e_i-\mu)^\top\Sigma^{-1}(e_i-\mu)
\]

所有主要 baseline 应尽量共享相同 score head，以避免 head capacity 混淆。

## 6. scene-information suppression 最小实现

首轮必须包含 adversarial residual 或等价 scene-information suppression baseline：

- scene classifier：\(d_\eta(r_i)\rightarrow s_i\)。
- GRL objective：训练 \(r_i\) 使 normality loss 降低，同时使 \(d_\eta\) 难以预测 source scene。
- 可选替代：MMD/HSIC scene dependence penalty，但若采用 MMD/HSIC，仍需与 GRL 或明确 adversarial baseline 对照。

最小 adversarial 项：

\[
\mathcal{L}_{adv}=-\mathcal{L}_{scene-cls}(d_\eta(r_i),s_i)
\]

不得只报告 scene classifier accuracy 下降；必须同时报告 event/motion retention 和 low-FPR 指标。

## 7. ELOS episode 定义

ELOS 是训练原则，不是独立机制。

每个 episode \(t\)：

1. 将 source scenes 分成 support scenes \(\mathcal{S}_{sup}^{(t)}\) 和 held-out scene \(\mathcal{S}_{ho}^{(t)}\)。
2. 只用 \(\mathcal{S}_{sup}^{(t)}\) 的 normal clips 更新 SRN 和 normality state。
3. 在 \(\mathcal{S}_{ho}^{(t)}\) 的 normal clips 上检查 anomaly score 是否保持低值。
4. 不允许对 held-out scene 做 target adaptation。
5. 必须 whole-scene holdout；frame masking 不能替代 ELOS。

SRN 是机制；ELOS 是训练/验证原则。论文和实验中不得把 ELOS 作为 standalone contribution。

## 8. overall objective

最小目标：

\[
\mathcal{L}=
\mathcal{L}_{normal}(e_i)
+\alpha\mathcal{L}_{scene-pred}(z_i,c_i)
-\beta\mathcal{L}_{scene-cls}(d_\eta(r_i),s_i)
+\gamma\mathcal{L}_{capacity}(\hat{u}_i,c_i)
+\delta\mathcal{L}_{ELOS}
\]

含义：

- \(\mathcal{L}_{normal}\)：source normal clips 上的 compactness / density objective。
- \(\mathcal{L}_{scene-pred}\)：约束 \(c_i\) 捕获可预测的 scene component。
- \(-\mathcal{L}_{scene-cls}\)：抑制 residual 中的 scene identity。
- \(\mathcal{L}_{capacity}\)：限制 scene branch 过度吸收 event information。
- \(\mathcal{L}_{ELOS}\)：held-out normal scene 上的 score consistency / model selection。

## 9. training-time allowed information

允许：

- source normal clips；
- source scene/domain id（若官方 split 或稳定 metadata 提供）；
- source normal validation；
- source normal score distribution；
- source-only threshold selection；
- source-only scene probe / diagnostic labels。

禁止：

- abnormal training labels；
- target anomaly labels；
- target test score distribution；
- target-specific threshold；
- target-scene adaptation；
- end-to-end backbone fine-tuning；
- 任何需要下载数据或使用 GPU 的操作，除非用户另行授权。

## 10. test-time allowed information

strict zero-shot：

- 只允许输入 target test clips 并输出 scores。
- 不允许用 target normal statistics、target anomaly labels、target score distribution 或 target threshold。

target-normal calibration：

- 允许使用预先声明的 target normal calibration clips。
- 不允许使用 target anomalies。
- 结果必须与 strict zero-shot 分表报告。

## 11. 必须实现项

restricted bridge 首轮若获授权，必须包含：

- raw frozen feature + kNN；
- raw frozen feature + Mahalanobis / Gaussian density；
- raw frozen feature + prototype / memory bank；
- scene mean subtraction（若 scene id 可用）；
- background mean subtraction（若可 label-free 计算）；
- adversarial residual only；
- full minimal SRN；
- SRN without ELOS；
- ELOS without SRN（若数据 scene 数量足够）；
- source-threshold transfer；
- strict zero-shot 与 target-normal calibration 分表。

## 12. 可选正则项

仅在首轮信号需要时加入：

- MMD / HSIC scene dependence penalty；
- orthogonality penalty；
- prototype transport；
- temporal smoothing baseline；
- AMCN branch。

这些项不得成为首轮方法复杂度的默认组成。

## 13. 本轮明确不实现项

- end-to-end backbone fine-tuning；
- 大规模多数据集训练；
- Street Scene / NWPU / IITB Corridor scale-up；
- object-centric detector/tracker pipeline；
- retrieval system；
- masked distillation training；
- large VLM / MLLM baseline；
- 使用异常训练标签；
- 使用目标异常标签调阈值；
- 未授权的数据下载、GPU feature extraction 或训练。

## 14. 避免过度去场景化

SRN 不能以“删除所有 scene 信息”为目标。必须采用：

- 低容量 scene token；
- context path target-time frozen；
- scene-ID probe + event/motion retention probe 联合判据；
- location-dependent anomaly stratification（仅在标签/映射允许时）；
- context path on/off/capacity sweep。

若 residual scene probe 下降但 location-dependent recall 或 FA/hour 变差，则判定为 over-invariance failure。

## 15. 关键 ablation

- **检查 SRN 是否只是 scene mean subtraction：** 比较 raw、scene mean subtraction、background mean subtraction、PCA nuisance removal、full SRN。
- **检查 adversarial residual 是否必要：** 比较 full SRN、SRN without adversarial suppression、adversarial residual only、GRL/MMD baseline。
- **检查 ELOS 是否必要：** 比较 SRN with ELOS、SRN without ELOS、ELOS without SRN、scene-balanced ERM。
- **检查 scene token 是否有效：** learned scene token vs random/constant token；若可合法使用 scene labels，则 scene-label token 只作 upper-bound diagnostic。

## 16. 冻结结论

本文件冻结的是 minimal SRN pilot 的数学和实现边界。它允许后续在用户授权后进入 restricted bridge，但仅限 frozen-feature audit + minimal SRN-vs-adversarial pilot；任何扩大范围都必须另行申请。
