# Task 1 日志研究·第 2 轮（2026-09-15）

本轮针对两份提交的可下载 loss/tie replay 与 agent callback log 做动作级汇总。输入由 `TASK1_ROUND2_20260915.json` 生成；仅分析已有缓存，不触发线上请求或提交。

## 覆盖范围与完整性

| 提交 | loss/tie 行（state） | 有 replay 的行 | 720-step 完整 | stderr |
|---:|---:|---:|---:|---:|
| 56238321 no-R128 | 56 | 56 | 全部 | 0 |
| 56234455 v42_pkg | 11 | 11 | 全部 | 0 |

每行 callback 记录为 719 条（末状态对应 replay 的第 720 步）。日志解析未发现 stderr；缓存行的最大 callback 时长约 0.58 s（no-R128）和 0.52 s（v42_pkg），均未出现超时级别异常。

## 负局/平局行为

两份提交的 loss/tie 中，动作计数排序一致：`WATER`、移动（`NORTH/WEST/EAST/SOUTH`）、`PASS`、`HARVEST`、`SELL`、`CARE`、`COLLECT_FERTILIZER`、`FEED` 是主要操作。按单局计，no-R128 loss 的 SELL 事件均值约 456，v42_pkg 约 432；这是 replay 展开后逐 actor/step 的事件数，不能直接解释为订单槽数量。销售主要集中在 day 22–29，day 29 最密集，产品总量排序稳定为 WHEAT、CARROT、FERTILIZER、MILK/EGG，其后是 STRAWBERRY、WOOL、MELON、TOMATO。

最大的已缓存负 margin：

- v42_pkg episode 109173463：−6,887；
- no-R128 episode 109048973：−6,463；
- v42_pkg episode 109191019：−4,864；
- no-R128 episode 109049475：−4,396。

这些极端局的总销售构成几乎相同（例如 WHEAT 约 17.4k、CARROT 17.0k、FERTILIZER 10.3k、MELON 6.1k），差异更像市场随机流、对手订单顺序或少量路线时序，而非某个商品完全缺失。平局行的动作与销售构成也与负局相近，未显示独立的“平局模式”。

## 首次分歧与终局检查

对三条代表性 replay（no-R128 109202620/109202449；v42_pkg 109202960）逐步比对后，首次可见分歧在 step 1，来自对手 opening order 不同；自身 opening 与 terminal liquidation 基本一致。后续差距在共享市场 SELL 的数量/顺序和路线时序逐渐形成，未观察到 R128/no-R128 或 step-718 终局包装器导致的确定性断点。该结果与第 1 轮的 aggregate 统计一致：不能把少数线上负局归因于 R128 删除或终局逻辑。

## 对候选研究的约束

1. 保留已验证 opening、FEED/CARE/PICKUP 与路线骨架；不要依据三条 replay 改 opening。
2. 若研究销售调整，只允许在父动作已有 SELL 槽位内做可回退、受 pickup reserve/BUY/HIRE barrier 约束的微调；全局合并同品订单没有日志或高分录像支持。
3. 将线上 loss 的 margin、对手身份和市场序列作为分层变量；当前缓存没有足够胜局 replay，不能估计无偏胜率。
4. 后续本地 paired panel 必须报告 min margin、5% 分位、负局数、seat 差异和最大 callback 时长，避免用线上单局分差做因果判断。

机器明细见 [TASK1_ROUND2_20260915.json](TASK1_ROUND2_20260915.json)，第 1 轮聚合见 [TASK1_ROUND1_20260915.md](TASK1_ROUND1_20260915.md)。
