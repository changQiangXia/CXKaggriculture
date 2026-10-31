# 下一阶段研究·第 1 轮：列出假设与冻结基线

本轮完成了候选基线冻结、证据矩阵和修改优先级登记。冻结基线为 no-R128 V42，no-R127 V42 作为第二对照，完整 V42 只作历史参考。源码与 archive 的 SHA256 保存在 `next_research_baseline_manifest_20260915.json`。

## 修改优先级

1. `slot_rank`：day 18–28 仅在已有 SELL 连续块内换序，保持数量、槽位和非 SELL barrier；不合并、不新增订单。
2. `premium_front_run`：day 24–29 依据下一回合 SELL、town demand、pickup reserve 和可见价格做一步有限前移，下一回合偿还。
3. `terminal_frontier`：step 718 完成父动作投影后，在剩余槽位内补可售 MILK/WOOL/EGG 等。

优先级来自两份提交的 loss/tie 日志、两条高分录像以及公开代码和讨论。所有机制都只使用 observation 可见状态，低置信度时精确回退父动作。

## 共享硬约束

- 不改变 opening、route、FEED、CARE、PICKUP、BUY/HIRE 和容量账本；
- day 1 必须保留 FEED；
- 所有局完成 720 steps、输出 DONE、stderr 为空；
- 每个分支只打开一个开关，不能把 A/B/C 叠加后再解释收益；
- 不做全局 SELL merge，不读取对手隐藏库存，不使用未来不可见信息；
- 记录 activation、修改单位数、barrier 拒绝、回退原因、callback 延迟。

详细的修改轮方案见 [PLAN_MODIFY_NOTES.md](PLAN_MODIFY_NOTES.md)。本轮没有修改策略源码，也没有提交 Kaggle。
