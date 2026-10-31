# Kaggriculture 规则研究·第 3 轮：边界、验证和策略含义

本轮把规则映射到候选验证边界。

1. **时间边界**：agent 在 step 0–718 提交动作；engine 在 720-step season 后给出 DONE。step 718 是最后一个可执行策略节点，不能把 step 719 当成普通 turn，也不能把 terminal 逻辑提前到更早步骤而破坏生产/库存。
2. **动作边界**：每单位每 turn 一个 action；market 每玩家最多 10 orders，超出的静默丢弃。动作无效通常是 silent no-op，因此“运行完成”不等于动作生效，必须记录有效 action/库存变化。
3. **资源边界**：shed 容量 100（不含 seeds）；end-of-day drop 仍受容量限制。animal max_held 是 tile 上未收获产品上限，不是 lifetime 上限；care bonus 只在 fed 且下一次 scheduled production 时兑现，production day unfed 会清空 bonus。
4. **随机边界**：weed spawn、shop unlock 和 shop draws 使用 engine RNG；shop 是 with replacement。固定录像不能覆盖随机市场/需求分布。
5. **可见性边界**：对手 farm 可见、对手 shed/inventory 不可见；任何“对手未来 SELL”只能来自自家已知 route 或公开当前动作，不能假设隐藏 tape。
6. **验证边界**：必须在真实 engine 跑 common seeds、双 seat、多策略族对手；需要检查 DONE/720、stderr、timeout、负局、5% 分位、min margin、seat variance、future debt 和 physical inventory，而不仅看终局平均 reward。

对当前研究的直接结论：高分/线上 log 只能用来提取范式（状态条件→受限动作），不能复制固定 step/tape；所有市场调整都要保留 parent fallback，先确认动作在当前 route 上真实触发，再做跨 seed/opponent holdout。任何只在单一录像上产生的收益都不能作为线上提升证据。
