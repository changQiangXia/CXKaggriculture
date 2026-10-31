# Kaggriculture 规则研究·第 1 轮：状态、动作和季节结构

本轮逐条核对 `kaggriculture/README.md` 与 `kaggriculture/AGENTS.md`，确认比赛是双玩家、每局 30 天 × 24 turns = 720 turns 的动态 farming 对抗。每 turn 每个 farmer/hand 同时提交一个 physical action，另有有序 market order 列表。

关键状态分层：

- 公开：双方 farm tiles、位置、hands、unlocked quadrants、hires_today；共享 market inventory/prices 与 town.unlocked_shops。
- 私有：自己的 shed、seeds、各单位 inventories；对手 shed/inventories 不可见。
- 合法推理只能使用 observation 当前可见字段，不得读取对手隐藏库存或未来不可见状态。

物理动作会先同时执行，再按顺序处理 market queue，然后 town 消耗，再做 day/market refresh、收入和 farm update。PICKUP/PLACE/DROP 受 shed 中心四格和容量 100 约束；overflow 会丢弃。Seeds 独立于 shed 容量，不能通过 PICKUP 取出。

规则上最容易造成错误的点：locked tile 可通行但普通 tile action no-op；shed action 在四个中心格可执行，即便格子处于 locked quadrant；hands 每天结束消失并掉落库存；animal 必须连续供给 wheat，连续两天未 feed 会逃逸；新种植当天 consecutive_unwatered 已为 1，因此当天不浇水可在夜间直接变 weed。

候选策略的第一原则应是物理动作和库存账本正确，市场优化必须建立在这些约束之上。
