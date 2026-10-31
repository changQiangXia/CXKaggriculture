# V45 后续候选验证计划（2026-09-17）

## 目标

`submission_competitive_v45.tar.gz` 在线约 2650 且平局很多，最可能的解释是大量对手复制了相同 notebook。下一阶段的目标不是让候选在同一开局族中偶然多赢几局，而是判断候选是否能在保持 V45 核心收益的同时，解除同质化平局，并且不伤害未见过的策略族。

所有结果均解释为“候选相对冻结 V45 的方向”，不能把不同提交日期的绝对 Kaggle 分数当作同一指标。

## 策略谱系和 opening 分层

同一作者、同一 notebook 的包装变体只算一个策略族。初始分层如下：

| 层 | 内容 | 用途 |
|---|---|---|
| L1 | V45/V44 及其已知 clone | 检验是否解除同质化平局、测量 shared-market exploit |
| L2 | V43/Ahmed/Jaxa K0006 | 检验 raw-V43 lineage 兼容性，不能把多个包装算独立样本 |
| L3 | Nathan sales-first/fixed-route | 检验销售节奏和库存账本是否被破坏 |
| L4 | flex、Thomas、Dmitrii 等动态或不同架构 | 主要抗过拟合层 |
| L5 | 候选冻结后才选取的近期公开模型或随机策略 | 时间外 holdout，不能用于调参 |

每场还按 V45 基线中对手的 step-0 动作预先标注 opening：

| Opening | 定义 |
|---|---|
| A | 70 wheat buy / 70 wheat sell 的 shared-market round trip |
| B | 5/10/60 等小 round trip |
| C | sell-first 或没有第二个 wheat buy |
| D | 不含 wheat round trip 或其他订单顺序 |

标注来自父版本的对手动作；不能因候选改变了市场后对手动作变化而重新分类。每个 opening 的样本数、成交价格、实际成交量和后续现金都要单独报告。

同时保存 `baseline_opening`（V45 对局中的对手 step-0 订单）和
`realized_opening`（候选实际对局中的订单）。候选的首单可能改变报价，使对手
进入另一个分支；两者不一致的局标成 opening migration，单独报告迁移率和
迁移局的 Δ，不能事后按候选结果重新归类。

## 实验表

| 阶段 | 对象和规模 | 必存指标 | 通过条件 |
|---|---|---|---|
| 0. runner null | V45 对 V45，4 个未用于调参的 seed，各换两次 seat | 完成步数、reward、action hash、stderr、运行时间 | 结果逐场相同；否则先修 runner/环境，不运行候选 |
| 1. 机制消融 | V45、关闭改动的 V45、最小改动版本；每个主要 opening 至少 6 seed×2 seat | 首次 action 差异、触发次数、订单 index、成交/失败请求、24/72 步现金和库存 | 机制只在预期 opening 触发；无意外订单或 RNG/loader 差异 |
| 2. Pilot | 每个 L1–L4 至少 8 seed×2 seat；L5 不看结果 | paired margin Δ、W/L/T、W+0.5T、tie rate、P10、最差三场、异常率；按 lineage/opening 输出 | 无加载/超时；非目标族平均 Δ ≥ −100；无 Δ<−2000 灾难局；触发率可解释 |
| 3. Confirm | 预注册最多 2 个候选；每族 20 seed×2 seat（资源不足最低 16），加 L5 时间外族；seed 与 Pilot 不重叠 | seed-cluster bootstrap 95% CI、paired permutation/sign test、等权族结果、leave-one-lineage-out、opening 交叉表 | 见下方 Confirm 门槛 |
| 4. 线上校准 | 仅在用户授权后提交；记录提交时间、候选 hash、当时线上分数和可见对手组成 | 本地预测方向与提交后相对变化 | 只校准方向，不倒推绝对分数；相反时检查对手池和 opening 分布 |

## 平局和统计口径

主指标是同一 `(lineage, seed, seat)` 下候选与 V45 的连续 `Δmargin = margin_candidate − margin_V45`。平局不能丢弃，因为同质化正是问题本身。

同时报告：

* `W/L/T`：按最终 reward 或 margin 的正、负、零；
* `score = W + 0.5T`，以及 `conditional win = W/(W+L)`；
* exact-identical action rate、tie rate 的变化；
* 每个 seed 先聚合两个 seat，再对 seed 做 bootstrap（10,000 次）和 paired permutation/sign test；两个 seat 不是两个独立世界；
* 均值、中位数、10% 分位数、最差三场和最大回撤。

候选把平局变成微小胜时，只有 `Δmargin` 和尾部风险也改善才算收益；平局率下降本身不能晋级。

## Confirm 晋级门槛

1. 按主要策略族等权平均 `Δmargin ≥ +150`，seed-cluster bootstrap 95% CI 下界大于 0。
2. 至少 3/4 主要族的族均值不低于 −50；任一族 bootstrap CI 下界不低于 −300。
3. 总体 P10 不低于 −1000，最差单局不低于 −2000。
4. 完成率 100%，无新增加载、stderr、超时或非法动作；胜率相对 V45 下降不超过 5 个百分点，`W+0.5T` 至少提高 3 个百分点或保持不下降。
5. leave-one-lineage-out 后总体方向仍为正；若去掉 L1 后全为负，候选只能标为 clone exploit，不得称为通用升级。
6. 针对 L1 的候选可要求 L1 `Δmargin ≥ +250`，但 L2–L4 平均不得低于 −100 且各族 CI 下界不得低于 −300。

任何候选只靠一个 opening、一个 seed 或少于 5% 的偶发触发获得收益，都视为过拟合。Pilot 通过后才进入 Confirm；Confirm 最多登记两个候选，查看结果后不得再改代码或复用同一 holdout。

## 每场日志最低字段

记录源码/引擎/tar SHA、seed、seat、对手族、opening 标签、720-step 完成状态、每回合 action hash、首次动作差异、订单 index 与请求/成交量、现金/库存/产量、买卖/雇佣/土地/动物/种子/肥料/town 成本、最终 reward/margin、stderr 和 callback 延迟。共享市场改动必须同时记录父版本报价和候选报价，才能区分“实际抬价”与“请求量未成交”。
