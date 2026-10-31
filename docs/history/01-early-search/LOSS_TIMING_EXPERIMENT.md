# 可证伪机制：MILK 首次销售时序

对 37 场 h5sim96 线上 loss replay，比较我方与对手首次 MILK SELL（取实际 replay action，decision t 对应 `steps[t+1]`）：

- 我方首卖晚于对手：26/37
- 我方首卖早于对手：7/37
- 同回合：4/37
- 首卖回合差（我方-对手）均值 +4.08 turns

WOOL 几乎同步（32/37 同回合），STRAWBERRY 也几乎同步（34/37 同回合）。因此 premium 差距最清晰的可见信号是 MILK 首卖时序，而不是产量或 TOMATO。多场 loss 中我方 MILK 首卖约 day13，对手 day12/day13；共享市场价格会因先后顺序变化。

## 最小可证伪实验

从 h5sim96/cap2 复制候选，只改 MILK sale lead：在 288–647 的普通销售块中，当父 action 首次出现 MILK SELL，且预测库存中 MILK > 0、当前 `market.prices[MILK]` 不低于过去 4-turn 中位价时，将该 MILK lot 提前一回合加入 market order；保留原订单数量、purchase barrier 和 max 10 slots，若该回合有 BUY/HIRE 或订单已满则 abstain。禁止改 WOOL/STRAWBERRY/TOMATO、禁止 step 695+ 终端清算。

评估：

1. 冻结 V37 未见 15 seeds × 双席（与 cap2 unseen 相同）；
2. Flex/Thomas/Dmitrii 各 10 seeds × 双席；
3. 固定真实线上 replay 的 opponent action 做反事实，至少 12 场（结果只作机制证据，不等同 rating）；
4. 记录 MILK 首卖差、MILK 收入、总 margin、市场 order 是否重排、720/DONE、stderr。

成功判据：未见 seed 面板胜率不下降（允许最多 1 局回归），12 场真实 replay 反事实中 MILK 收入提高且总 margin 翻转至少 3 场；若收益仅来自固定 opponent 或出现订单槽/融资异常则废弃。

## TOMATO 结论

将 `CROP_MIN_PRICE` 从 70 降至 60 的对照在未见 V37 30 局仍完全相同（30/30，均值 +1873.7），且在真实 replay action 上没有触发差异；该改动应废弃。真实 loss 中只有少数（约 5/37）对手在 day18 投资 TOMATO，且通常需 Pizza/Farmers Market 多店、高价格条件；我方 day‑6 价格低于 70 时不种植是合理的。
