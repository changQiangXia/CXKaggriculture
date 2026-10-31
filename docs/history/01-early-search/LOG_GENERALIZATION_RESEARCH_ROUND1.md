# Log 修改泛化研究·第 1 轮：从单局行为到状态范式

日志只能用于提出机制假设，不能直接成为训练标签。每条 log 先转成 observation-visible feature：day/step、market inventory/prices、town shops、自己的 shed/inventories、公开对手 tiles、父 route suffix、SELL/PICKUP/BUY/HIRE barrier、订单槽和 sale debt。对手隐藏 shed 不纳入特征。

将修改表达为 `状态契约 → 受限动作 → parent fallback`，例如“连续 SELL block 内公开 contested value 差异超过阈值才换序”，而不是“episode X 的 step 648 把 WHEAT 放到第二个”。日志来源分为 discovery（提出规则）、development（选阈值）、holdout（从未参与调参）和 stress（对价格/库存/shop/seat 做扰动）。

每个 log 修改至少做三种验证：

1. replay counterfactual：真实 engine 中只改变一个动作，推进后续 24/72/144 steps；
2. state perturbation：对可见价格、库存、town demand、公开产出和 shed reserve 做小范围扰动，检查是否合理回退；
3. parent equivalence：条件不满足时 candidate action 必须与 parent 完全一致。

泛化的最低证据是跨两个策略族、多个 seed、两个 seat 仍方向一致；单个对手或固定 tape 上的收益只能标为 tape-specific。
