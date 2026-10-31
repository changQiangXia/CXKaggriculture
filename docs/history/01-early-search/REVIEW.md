# inspired_premium_v1 Round 1 review

审阅结论：保留 parent fallback；只在 day24–28、非四回合边界、premium 商品、父 route 下一步已有 SELL 且公开 town demand 不冲突时追加 1 单；不读取对手隐藏状态。风险：当前 route 可能与实际 chassis 状态不同，且追加后尚未实现 repayment debt，因此本版本只能作为研究草案，不能晋级。
