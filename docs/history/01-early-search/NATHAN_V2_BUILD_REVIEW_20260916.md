# Nathan v2 构建、两轮审查与提交决策（2026-09-16）

用户授权了本轮构建、本地验证和一次提交；提交门槛是候选必须先通过配对验证。本轮未提交负收益候选。

## 基线

基线为 `nathan_3rounds_20260916/corrected/main.py`，即已上传的 loader/market-list 修复版父策略。它保留真实加载入口，但上游 `_v224_sales_first` 仍会在最终 `_NC2` wrapper 之前删除零量订单并移动 SELL，因此最终 wrapper 不能恢复原始槽位。

## 第一轮：槽位保留但继续重排

`round1/main.py` 保留所有非空槽位，并要求 SELL 数量不超过当前观察到的库存；仍允许 SELL 跨越 HIRE/LAND 等订单。16 场配对：v37 8 场平均 **−429.9**，flex 8 场平均 **−188.1**；16 场全部低于基线。

结论：仅修复零量订单删除不够，跨槽位移动仍会改变对手的同 index 交易和后续市场状态。

## 第二轮：小批量、价格和 town 保护

`round2/main.py` 进一步限制：SELL 数量最多 8、当前库存必须覆盖、价格不低于商品基准 90%、town 当前消费需求预留库存，并禁止跨 BUY_PRODUCT/BUY_ANIMAL/BUY_SEED；仍允许跨 HIRE/LAND。16 场配对：v37 平均 **−1117.8**，flex 平均 **−315.1**；16 场全部低于基线。

结论：即使“真实库存 + 价格 + town 安全”成立，移动 SELL 仍会影响随机数、订单配对和之后的路线；条件本身不足以证明收益。

## 第二轮复审：关闭重排与只禁用终局重排

作为审查对照，额外测试了：

- 完全禁用 `_v224_sales_first`，保留 R36 显式销售预留：v37 平均 **−1118.3**，flex 平均 **−315.6**。
- 只在 callback 648 以后禁用重排：v37 平均 **−298.9**，flex 平均 **−59.9**。

因此“完全关闭”或“只修终局”都不能作为 v2。简单关闭 sales-first 在某些路线明显损失收益，说明它有策略作用；但它也会改变对手相同 market index 的行为，不能只从 Nathan 自己的成交账本判断。

一个直接证据是 v37 seed 9001 seat 0：callback 144，基线把 `[HIRE×7, SELL FERTILIZER 2]` 重排为 `[SELL FERTILIZER 2, HIRE×7]`。基线自己的最终 margin 比 no-reorder 高 537，但 own reward 只高 290、对手 reward 也高 247。这是双方槽位耦合效果，不是单纯的 Nathan 自身销售收益。

## 决策

本轮没有任何策略候选通过“跨对手不劣”的本地门槛，因此不提交 round1、round2、late-guard 或 no-reorder 包。已授权提交不等于应上传未通过验证的候选；提交一个已知平均负收益的包会污染线上两个 agent 的比较。

当前可保留的只有已提交的 corrected loader 修复版 `56270791`，它的作用是让 wrapper 导出路径正确，不能称为策略提升。

## 后续可行方向

下一版不要再做“把 SELL 移到更前面”的自家局部规则。应当把 market index 看成双方共享的耦合决策，并记录原始/最终 index、双方实际成交和现金变化。若要继续研究，只测试不改变已占用 index 的机制，例如：

1. 只在原始列表已有空位且不会压缩列表时追加可兑现小批量 SELL；
2. 只在同一商品的连续 SELL block 内排序，不跨 HIRE、LAND、BUY_PRODUCT、BUY_ANIMAL、BUY_SEED；
3. 先用 shadow telemetry 统计这种机会在不同策略族中的频率，再决定是否实施。

相关源码和配对结果：

- `nathan_v2_20260916/round1/main.py`
- `nathan_v2_20260916/round2/main.py`
- `nathan_v2_20260916/late_guard.py`
- `nathan_v2_20260916/round1_panel.json`
- `nathan_v2_20260916/NATHAN_V2_BUILD_REVIEW_20260916.md`
