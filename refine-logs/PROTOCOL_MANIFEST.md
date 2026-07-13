# Protocol Manifest 冻结文件

**日期：** 2026-07-13  
**状态：** pre-bridge freeze pass  
**目标：** 冻结 restricted bridge 前的数据、split、指标和阈值协议。  
**硬约束：** 本文件不下载数据；不训练；不使用 GPU；不授权 `/experiment-bridge` 自动启动。

## 1. Dataset tiers

| Tier | Dataset | 角色 | 首轮状态 | 备注 |
|---|---|---|---|---|
| Tier A | UCSD Ped2 | smoke test；历史可比性 | 可作为最小 smoke test 候选，但需用户授权下载/确认本地存在 | 小、饱和，不能作主结论 |
| Tier A | CUHK Avenue | 单场景 source/target sanity 与 cross-dataset transfer | 首轮候选，需用户授权下载/确认本地存在 | 异常类型少，适合快速检查 |
| Tier A | ShanghaiTech | multi-scene core；LOSO 核心数据集 | 首轮核心候选，需用户授权下载/确认本地存在 | 13 scenes；需要 split/scene id 审计 |
| Tier B | Street Scene | realistic false alarms 与 RBDC/TBDC | 不进入首轮 | 评测实现更重 |
| Tier B | NWPU Campus | 43 scenes；scene-dependent anomalies | 不进入首轮 | 体量约 76.6GB，暂不下载 |
| Tier B | IITB Corridor | 长视频真实走廊异常 | 不进入首轮 | 需确认许可、标签、official split |
| Diagnostic | UBnormal normal/test only if needed | open-set / synthetic diagnostic | 不进入首轮 | synthetic domain；不得使用异常训练集 |

## 2. First restricted bridge dataset plan

首轮最小数据计划只定义范围，不下载数据。

| 用途 | 数据集 | 目的 | 下载/访问要求 |
|---|---|---|---|
| smoke test | UCSD Ped2 或 CUHK Avenue | 验证 pipeline、feature shape、score 计算和 metric 代码 | 需要用户单独授权下载，或确认本地已有合法副本 |
| multi-scene core | ShanghaiTech | SRN/ELOS 的 scene holdout 与 scene leakage 核心检查 | 需要用户单独授权下载，或确认本地已有合法副本 |
| cross-dataset transfer | Avenue ↔ ShanghaiTech，必要时加 Ped2 | source→target off-diagonal sanity | 需要用户单独授权下载，或确认本地已有合法副本 |
| 暂不进入首轮 | Street Scene | 后续 false alarm / RBDC/TBDC scale-up | 首轮不下载 |
| 暂不进入首轮 | NWPU Campus | 大规模 scene-dependent anomaly 验证 | 过大，首轮不下载 |
| 暂不进入首轮 | IITB Corridor | 真实长视频扩展 | 首轮不下载 |

## 3. Splits and tracks

### within-dataset sanity

- 使用官方 normal-only train split。
- test split 只在 evaluation 阶段使用 anomaly labels。
- 只用于 sanity，不作为主 claim。

### within-dataset leave-one-scene-out

- 仅对有 scene id 或可稳定映射 scene 的数据集使用。
- 每次 held-out scene 不参与训练、阈值选择或 normalization。
- ShanghaiTech 是首轮 multi-scene core 候选。

### source→target cross-dataset matrix

- 在 source normal training split 上训练/拟合 normality model。
- 直接在 target test split 上评价。
- 不允许使用 target anomaly labels 调阈值。
- 不允许使用 target test score distribution 做 normalization。

### strict zero-shot

- 允许：source normal train、source normal validation、source scene id。
- 禁止：target normal statistics、target anomaly labels、target score distribution、target-specific threshold、target adaptation。
- 结果单独报告。

### target-normal calibration

- 允许：预先声明的 target normal calibration clips。
- 禁止：target anomalies。
- 不得与 strict zero-shot 混表。
- 所有 target-normal budget 必须报告。

### no abnormal training labels

- 所有训练、model selection、threshold selection、normalization 都不得使用异常标签。
- 异常标签仅用于最终 evaluation。

## 4. Metrics

首轮必须报告或预留：

- micro AUROC；
- macro AUROC；
- AUPRC；
- TPR@1% FPR；
- TPR@0.1% FPR；
- false alarms/hour；
- threshold transfer performance；
- per-scene variance；
- worst-target performance；
- bootstrap confidence intervals if feasible。

## 5. 指标解释规则

- pooled frame AUC 只能作为 sanity check。
- 主结果必须关注 off-diagonal、cross-scene、low-FPR 和 FA/hour。
- source threshold 必须只由 source normal validation 决定。
- 不允许用 target anomaly labels 调阈值。
- target-normal calibration 必须和 strict zero-shot 分开报告。
- 若数据无法支持 FA/hour，需要说明原因并报告替代 low-FPR 指标。
- 若无法做 bootstrap confidence intervals，需要记录原因，不得用单次结果过度 claim。

## 6. 阈值协议

strict zero-shot：

1. 在 source normal validation 上确定 threshold 或 score map。
2. 冻结 threshold。
3. 直接应用到 target test。
4. 报告 target normal false alarms 与 target anomaly recall。

target-normal calibration：

1. 预先声明 target normal calibration set。
2. 只用 target normal clips 调整 threshold / score map。
3. 不使用 target anomaly。
4. 与 strict zero-shot 分表报告。

## 7. 数据与资源授权

- 任何数据下载都需要用户单独授权。
- 任何 GPU feature extraction、training、evaluation 都需要用户单独授权。
- 若自动 GPU 选择失败，后续执行必须停止；不得任意指定 GPU。
- 本 manifest 不授权任何数据下载、训练或 GPU 使用。

## 8. 首轮 restricted bridge 边界

若后续获得用户授权，首轮 `/experiment-bridge` 只能包含：

- Tier A 数据的合法获取/确认；
- frozen-feature audit；
- raw/Mahalanobis/prototype baselines；
- scene/background mean subtraction controls；
- adversarial residual baseline；
- minimal SRN pilot；
- SRN without ELOS / ELOS without SRN；
- strict zero-shot 与 target-normal calibration 分表；
- low-FPR / FA/hour / macro 指标。

明确不包含：

- Street Scene / NWPU / IITB scale-up；
- large VLM / MLLM；
- object detector/tracker pipeline；
- masked distillation training；
- end-to-end backbone fine-tuning；
- 异常训练标签。

## 9. 冻结结论

本 manifest 关闭 data/protocol split gate。当前状态仍为 **READY WITH RESTRICTIONS**，restricted bridge 尚未启动；数据下载、GPU 使用和训练仍需用户单独授权。
