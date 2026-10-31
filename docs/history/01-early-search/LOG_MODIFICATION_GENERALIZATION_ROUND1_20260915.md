# 基于线上 log 的修改：泛化性研究第 1 轮（设计）

本轮回答的问题是：从 loss/tie log 得到一个局部修改后，怎样证明它学到的是跨状态的机制，而不是对某一场 replay 的补丁。

## 先区分三种证据

1. **描述性证据**：某商品、某 SELL 顺序或某 day 在 loss 中出现。它只能产生假设，不能直接产生规则。
2. **固定 replay 反事实**：把 parent 的单个动作替换后，让真实 engine 继续推进。这能证明该状态下的方向，但仍受固定 tape 约束。
3. **交互式泛化证据**：候选和 parent 在同 seed、同 seat、同 opponent 的真实 engine 中独立运行，并在未参与开发的对手/seed/opening 上重复改善。只有这一层能支持候选晋级。

## log 到规则的转换

每条 log 先转换为可观测状态特征，而不是复制 action：

- `day/step` 与回合边界；
- market inventory、公开 price 及价格变化方向；
- town/shop 当前是否消耗该商品；
- 自己的 shed、carried、pickup reserve 和未来 SELL；
- market 剩余槽位、BUY/HIRE/PICKUP barrier 和 sale debt；
- 生产成熟度、现金、容量、动物/工人和公开对手产出。

候选规则必须写成 `状态契约 -> 有限动作 -> 预期下一状态 -> 回退`。例如，一步 premium 前移只有在下一回合有同商品 SELL、扣除 reserve 后有库存、没有 town demand、槽位足够且下一回合可偿还时才触发。固定商品、固定 step、固定数量或固定 opponent ID 都不是可接受的泛化规则。

## 数据隔离

每个 log-derived hypothesis 预先固定四层数据：

| 层 | 用途 | 规则 |
|---|---|---|
| discovery | 发现重复状态模式 | 可看完整 replay，但不能作为最终指标 |
| development | 调整状态阈值 | 只用未进入 discovery 的 seed/opening/opponent 家族 |
| confirmation | 冻结规则后确认 | 不再改变阈值；双 seat、多个 seed |
| final holdout | 最终审查 | 按时间、对手族、opening、seed 隔离，并设置线上反馈 embargo |

同一 episode 不能同时出现在发现和 holdout。参与阈值选择的 seed、opening 或 replay 永久排除。线上新 log 到来时先进入 embargo，不能立即用于修改正在评估的规则。

## 必须做的反事实

- `parent` 与 `candidate` 成对运行，common random numbers、相同 opponent/seed/seat；
- 固定 replay 中只改变一个 SELL block 或一个 gate，比较 24/72/144 步后的现金、库存、capacity、pickup、debt 和终局 margin；
- 对价格、market inventory、town demand、shed 余量、未来 SELL 做小扰动，检查规则是否平滑回退；
- leave-one-opponent-out：去掉产生假设的某个对手，规则仍需在其他策略族有效；
- leave-one-time-block-out：不能只在当前线上窗口有效；
- parent-equivalence：触发条件不满足时 action 必须逐项等于 parent。

## 泛化判据

一个 log-derived 修改只有同时满足以下条件，才进入第 2 轮：

- 固定 replay 方向与交互式对局方向一致；
- 至少两个不同策略族、两个 seat、多个 seed 上重复；
- 未见对手和未见 opening 上没有系统性退化；
- 平均 paired delta、5% 分位、最小 margin、CVaR、负局数和 seat 差异都通过门槛；
- activation 具有可解释的覆盖率，未触发局保持 parent-equivalence；
- 不能依赖未来 action、对手 private state、episode ID 或 seat 硬编码。

本轮的核心结论是：单场 loss 只能回答“哪里值得提出机制假设”；泛化性必须由状态契约、留出切分、交互式 paired panel 和长时域反事实共同证明。
