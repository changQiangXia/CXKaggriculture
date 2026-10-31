# V37 hybrid 优化方案（本地实验稿）

更新时间：2026-09-12 UTC

这份方案以 `public_v37_candidate.tar.gz` 为唯一行为基线。目标是找到在固定本地引擎中对 V37 零负差的候选，再考虑线上替换；没有达到门槛的实验只保留在本地，不上传。

## 从新日志得到的约束

监控报告目前包含 163 个 bot-side tie/loss 记录。V37（submission `56178383`）的 20 个 loss 平均差约 `-1793`、最差 `-6106`，另有 8 个 tie。所有记录都是 720 步 `DONE`，stderr 为零，最大 callback 约 `0.59s`，因此性能和异常恢复不是主要瓶颈。

V37 的 tie（包括 episode `108071579`、`108082646`、`108084841`、`108094789`、`108096777`、`108104921`、`108108869`、`108113943`）是逐步镜像或同一公开路线，动作序列和终局销售都一致。重排同一回合的 SELL 顺序不能改变共享市场的经济结果；固定 seat 偏置的实验曾在反向 seat 产生约 `-1581`，不能作为默认策略。

loss 主要分成三类：

1. **标准动物路线的共享市场错位**：COW/SHEEP/GOOSE 数量与对手不同，day 6–9 的 WHEAT 往返、动物购买和 day 27–29 的 MILK/WOOL/CARROT 清仓累积成几百到几千差距（例如 `108078615`、`108083700`、`108105829`）。
2. **TOMATO 路线竞争**：对手投入 10 个 TOMATO seed 时，V37 有时没有对应产量；V37 自身 TOMATO 资格路线也可能在终局差距中落后（`108084677`、`108097868`、`108112913`）。不能简单永久打开或永久关闭 TOMATO。
3. **高 SELL 流量/额外 HARVEST 路线**：对手比 V37 多一次 HARVEST 或有 450+ SELL，导致市场 inventory 在终局前不同步（`108085679`、`108088314`、`108112913`）。

这些现象支持“路线级条件选择 + 物理库存约束”的 hybrid，不支持从零 PPO/DQN 或对单局 ad hoc 打补丁。

### 追加的 step 648 库存审计

对最新 V37 loss/tie replay 在 step 648 提取了双方公开 tile 的 standing yield 和 tile 类型。镜像 tie 的各商品库存/standing yield 完全一致；loss 中更常见的是我方 WHEAT shed 较高但终局仍落后，例如 `108097868` 我方/对手 WHEAT standing 为 `37/45`，`108102850` 为 `50/44`，`108106854` 为 `50/36`，而 `108105829` 双方 standing 相同仍有 `-3368`。这表明“对手 standing yield 更高”不是充分信号，单独按该方向提前销售没有触发，不能直接放宽为反向全量销售。

因此 late-sale 层必须把 **自己的 projected shed、未来 route SELL suffix、未来 BUY/PICKUP 义务和公开对手差异** 一起作为状态输入，先在 shadow simulator 中评估，不允许仅凭 standing yield 改动作。

## 候选结构

### 1. V37 启发式底座

保留 V37 的 opening tape、day 6 shop-aware route、四回合 reservation、smarter-labor、weed repair、V219/V231/V233/V51 物理确认和终局 planner。所有新增层都包在底座外，异常时返回底座动作。

### 2. shadow contextual bandit（第一阶段只观察）

在 step 12、144、216 和 648 记录低维 context，并让一个离散 bandit 给出“本应选择的 profile”，但暂时不改动作。context 只能来自当前及过去 observation：

- step/day/hour、自己的 money、shed room、seed/库存和 weed 数量；
- 自己已解锁的 quadrant/shop、农田中各 crop/animal/weed 数量和成熟度；
- 对手公开 farm 的 tile kind/animal/crop、公开 money、hands 数量、已解锁 quadrant/shop；
- 当前公开 market price/inventory 和本回合已申报的订单。

禁止读取对手 private inventory、未来 SELL、未来随机数或 replay 中之后的状态。每个 context 保存 profile、终局结果、是否发生 recovery 和动作延迟，使用按 seed 留出的验证块拟合，避免按 episode 泄漏。

profile 只取四个离散值：

- `base`：完整 V37；
- `late_sale`：只允许 step 648–695 的 stock-bounded 下一回合销售提前；
- `tomato_guard`：保留 TOMATO 分支，但提高资金、价格、shed room 和可完成 harvest 的联合门槛；
- `animal_guard`：禁用未确认的 COW/SHEEP substitution，只执行已经确认的购买/放置。

bandit 的输出必须有置信度；置信度不足、字段缺失、配置不是 10x10/24/720/100 时回退 `base`。第一阶段记录选择结果，不改变线上行为，先检查选择与终局收益是否有稳定相关性。

### 3. 可解释硬门控

只有同时满足以下条件才允许 profile 改变行为：

- 当前 action 的所有 BUY/HIRE/PICKUP/PLACE 资源在真实 observation 中可满足；
- shed 使用量加 carried cargo 不超过 100，且下一次回 shed 的步数小于剩余步数；
- weed 位于即将执行的 PLANT/BUILD 路径时，优先 DIG；存在未确认 pending 时禁止新增投资；
- 新增 SELL 数量不超过当前真实 shed stock，并且单物品每个 day 最多提前一个回合、最多 8–24 单位；
- 任何物理状态与预测状态不一致时，立即放弃 overlay，恢复 V37 原路线。

这组门控直接针对日志中 day 27–29 的错位，避免把未来产量当作已经存在的库存。

## 第二阶段实验顺序

每个实验从独立 V37 副本开始，只改一个变量。官方本地引擎使用 seeds `9001–9020`、`1495252849`，三类社区对手（Flex、Thomas、Dmitrii）都跑双 seat。每局必须 720 步 `DONE`，并记录平均差、最差差、胜/负/平、seat 差异、异常数和最大 callback。

1. **shadow 统计**：确认 step 12/144 的公开特征是否能稳定区分 TOMATO、标准动物和高 SELL 对手；不改变动作。
2. **晚期真实库存销售提前**：从 step 648 开始，仅对当前 shed 已有且 route 下一步计划出售的 MILK/CARROT/STRAWBERRY/WOOL 做一回合提前，建立 debt 并在原回合扣除。先限制为每个 step 一个物品、最多 8 单位。
3. **TOMATO 联合门控**：只改变资格阈值（资金、价格、空间、可完成收获量），不增加 seed 数，不改变 worker tape。重点检查 `108084677` 类对手和所有 9001–9020 seed。
4. **动物确认门控**：禁用 speculative COW/SHEEP 替换，只有下一回合 observation 确认 BUY/PLACE 后才改变 worker；这项实验专门验证 `108078615`/`108083700` 类差异。
5. **profile 组合**：仅把前面单变量中通过门槛的 profile 组合成状态级 selector，不逐 action 拼接 Thomas/Dmitrii/V37。组合后重新跑完整 panel。

追加实验：在 V233 资格判断中加入“对手公开 SHEEP/WEED 更多则不投资”的门控，在 9001–9005 双 seat 上与 V37 完全同轨（1 胜/1 负/8 平、平均差 0，最差 -1581），说明该信号在当前块不可达，已停止继续堆叠同类门控。

已新增 `build_v37_context_dataset.py` 与 `shadow_profile_selector.py`。前者从 tie/loss replay 生成公开状态快照，后者按 `(step, TOMATO, WEED, animal divergence)` 分组并计算均值及 95% lower confidence bound。当前 10 个分组没有任何一个满足最小样本数和正 lower bound，因此 selector 对所有 context 保持 `base`，不会把噪声误转成动作改动。

## 接受/淘汰标准

相对原 V37，候选须在 `9001–9020 + 1495252849` 双 seat 的 42 场中零负差；平均差必须为正，且不能靠单一 seat。tie seed 至少出现一次可重复的正差，或在不改变镜像经济结果的情况下保持零差并改善其他对手。任一运行时异常、负 margin、配置回退失效或最大 callback 接近 1 秒，立即淘汰。

只有通过上述 panel、再通过单文件解压隔离运行和 latency 检查的候选，才进入待提交列表。任何上传仍需用户明确点名授权；当前不提交。
