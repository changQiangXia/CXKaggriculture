# v37 后续研究准则（2026-09-14）

当前没有发现已经证明稳定强于 v37 的候选。h5sim95/96 的配对审计在 Flex seed 9004 出现尾部退化，cap2 虽然在固定本地面板表现稳健，但线上历史结果较差；这些版本不再作为新父策略。

最新 56185929/56190357 的败局日志把问题收窄到两个相互耦合的机制：

1. 高价值商品（尤其 WOOL、STRAWBERRY、MILK）数量与对手接近，但成交批次和共享市场顺序不同，导致数百至数千金币差异。对三场已核验 replay，不能用一个全局的“提前卖”或“延后卖”规则解释：WOOL 常常需要提前，部分 STRAWBERRY 等待需求恢复反而更好。
2. step 623/695 的 end-of-day 入库把 carried inventory、当轮产出和 shed 合并计算，曾实际丢失 EGG/FERTILIZER。单独压制 harvest 会产生机会成本，必须在完整阶段账本中验证。

因此下一候选只允许采用阶段级、可回退的 H-DSS 结构：在 72-step 边界依据当前公开状态选择 profile，阶段内保持一致；联合评估库存、worker 回仓、SELL slot、购买/拾取 barrier 和 sale debt。profile 只在真实引擎反演确认 `overflow=0`、父级 deposit 前缀不减少、barrier 不变且保守收益至少高出 50 金币时生效。否则逐回合返回 v37 原动作。

已建立的最小实现位于 [`incubated_candidates/v37_hdss`](incubated_candidates/v37_hdss)。当前实现故意保持 native profile，只提供可审计账本和 certificate gate。对线上 replay 108205627 的 719 个决策状态，candidate 与 v37 动作 719/719 完全一致；这证明打包和回退安全，不代表性能提升。

在此基础上新增的 `v37_premium_gate` 是第一个可证伪的策略变体：只有公开 premium 价格处于高位时才启用五回合预留。它在 5 场同 seed/同 seat 的 V37 配对筛选中均为正（平均 +1447.6、最小 +151），并在 seed 9004 对 Flex、Thomas、Dmitrii 各一场均获胜；这些结果仍只是 screening，尚未达到跨对手双席 confirmation 门槛。

后续实验顺序：

- 先把真实 engine 的 block replay 接入 `simulate_dss_block`，覆盖生产、自动入库、市场 lockstep 和 debt；禁止用名义价格替代成交价格。
- 先做 15 个未见 seed、Flex/Thomas/Dmitrii 双 seat screening，再做至少 12 个真实 loss tape 的固定对手机制核验；两类证据分开报告。
- 若任一 profile 出现负 paired margin、premium 产量下降、barrier 改变、runtime/stderr 异常或 fixed-tape 收益无法在交互式对手复现，立即归档，不继续叠加门控。
- 在候选通过 confirmation 与 holdout 前，不生成提交包，也不调用 Kaggle submit。

监控脚本已恢复为单实例、600 秒轮询，覆盖 active 队列中的两个提交；其职责仅为收集 tie/loss replay 和 logs，不改变任何候选代码。
