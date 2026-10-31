# inspired_premium_v1 Round 2 review

本轮加入 next-turn repayment ledger：前移单位登记为 step+1 debt，下一回合只从同商品父 SELL 中扣回；偿还不足则返回 parent action。仍限制 day24–28、公开 town gate、父 route future SELL、每次最多一单位，不改变 physical route。审阅通过静态条件，但必须经 activation 与跨策略族 holdout；未获测试证据前不可提交。

复审发现 telemetry 若使用静态合并字典会显示旧计数；已改为共享 `_INS2_STATS` 字典并在 smoke 前后核对。该修复属于 Round 2 的审阅修正，不增加策略触发范围。
