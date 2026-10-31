# V45 同质化后的候选路线与验证方案

## 现状判断

线上约 2650 且平局增多，暂时只能提出“V45 与若干对手可能共享同一 opening/route”这一假设。先按线上 replay 的 720-step action hash 核实 exact mirror、不同动作但同 reward、以及近零 margin 三类平局。只在 exact mirror 且 step 0 的 wheat opening 为 `BUY 70 / SELL 70` 的比例足够高时，才把 anti-clone opening 作为主要方向。

已有本地 `open_ablation` 显示 opening 是高方差机制：相对关闭 opening 的同世界 paired 变化在 V43 seed 9001 为 `+1355`，seed 9004 seat 0 为 `-739`、seat 1 为 `-5880`。因此不能把公开 notebook 的固定镜像战绩直接外推。

## 候选优先级

1. `V45` 原包作为冻结控制，任何候选都必须与它 common-world paired。
2. `V45_Q5`：只把 `_OPEN_UNITS` 从 70 改为 5。它是针对 Q70 克隆的 exploit 候选，不自动视为通用模型。
3. `V45_Q50`：只改为 50，作为平台内较保守的中间强度候选。Q5 与 Q50 共同进入最终确认时，最多登记这两个。
4. `V45_post0_gate`：step 0 保持父动作；用 step 0 后公开 market inventory/price 的变化识别对手 opening，只有高置信度时才改变后续销售 reservation。默认和未识别分支必须逐动作等价 V45。
5. 分别关闭 `front_run`、`sell_lead`、`race escalation` 做消融，定位 V45 跨族退化来源；不把多个消融叠加为提交候选。

暂缓 Q24、Q40、Q60、Q65 等更多变体的 Confirm；它们可在开发 grid 中扫描，但看过开发结果后只登记两个最终候选。暂缓 horizon 24、frontload、sale advance 的组合，因为这些变化同时改变订单时序和 RNG，难以归因。

## 开发与确认矩阵

开发阶段对 Q=`0,5,10,20,30,40,50,60,65,70,75,80` 做 5 个策略族、每族 8 seed、双 seat 的 paired panel。策略族为：V45/Q70 clone、V43/V37 同 lineage、Nathan sales-first、flex/Thomas/Dmitrii 动态族、冻结后时间外公开模型。保存每局 margin、胜负平、step 0 实际成交量/价格、step 1 是否出现第二 wheat BUY、后续产量/库存/现金、首次动作差异、异常和耗时。

Q 类必须按 opponent opening 分层：第二槽 BUY wheat、先 SELL 再 BUY、无 wheat round trip。总平均不能掩盖某一层的灾难。

确认阶段在源码、引擎和 seeds 冻结后只登记 `Q5`、`Q50` 或其中两个最稳候选，每族 16–24 seed、双 seat，并使用 seed 聚类 bootstrap。沿用既定晋级门槛：等权族均值 `>+150` 且 bootstrap CI 下界 `>0`；至少 3/4 主要族均值 `>-50`；10% 分位不低于 `-1000`；最差局不低于 `-2000`；胜率下降不超过 5 个百分点；完成率 100%。若候选只在 Q70 层有收益，则标记为 anti-clone exploit，只有线上 exact-mirror 比例足够高且非 Q70 层无实质退化才考虑提交。

## 线上决策

以线上对手层的估计比例计算期望方向：`E[delta] = f_Q70 * delta_Q70 + (1-f_Q70) * delta_other`，并使用各层置信区间的保守下界。若 exact mirror 比例不高，继续使用 V45；若高且 Q5/Q50 的确认结果跨世界稳定，再由用户选择是否授权提交。研究阶段不上传任何候选。
