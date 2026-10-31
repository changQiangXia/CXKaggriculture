# V37 surplus timing shadow experiment

候选包：[candidate_v37_surplus.tar.gz](/root/autodl-tmp/candidate_v37_surplus.tar.gz)

这是第二个 shadow 候选：保留 V37 全部逻辑，仅在 step 648–695 检查某商品的真实 projected shed 是否超过未来 4 回合 route SELL 义务加 4 单位缓冲；满足时提前最多 8 单位，并在原回合抑制 debt。默认关闭，只有 `V37_HYBRID_ENABLE=1` 时生效。

验证：seeds 9001–9005、双 seat 共 10 局，对 V37 自战得到 `7 胜 / 3 负 / 0 平`，平均差 `-43.2`，最差 `-1905`。所有对局 720 步 `DONE`，但 seed 9001 双 seat 为 `-28`，seed 9004 seat 1 为 `-1905`。

结论：即使加入真实库存和未来销售义务限制，简单的 surplus timing 仍然有明显 seat-dependent 风险，立即淘汰，不进入待提交队列。它证明后续 shadow RL 必须联合模拟市场价格/库存与对手路线，不能用单一库存阈值直接改 SELL 时序。

