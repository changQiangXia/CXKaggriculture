# Kaggriculture 研究总文档（2026-09-15 12:56:15 UTC）

## 研究结论

当前最可靠的工作方式是把 log 和公开 agent 当作机制发现材料，把规则和 engine 当作硬约束，把新鲜公开对手、未见 seed、双 seat、状态扰动和长时域 paired panel 当作泛化证据。不能把单个 episode 的动作、某个作者的 tape 或一次线上 rating 变化直接写成策略规则。

## 游戏理解

官方 Kaggle overview 与本地 `kaggriculture/README.md`、`AGENTS.md` 已交叉核对；官方文件 SHA256 与本地一致。比赛是 simulation/file-based 双 agent farming game，30×24=720 turns，目标是季末 bank coins 最大。agent callback 实际为 step 0..718，engine 随后给出 DONE 终局状态。

每 turn 先执行双方 farmer/hand physical actions，再按有序 market order 逐单位处理，然后 town/shop 消耗，再做 day/market refresh 和收入更新。market 每玩家最多 10 个 order，SELL 顺序会影响逐单位价格；premium 商品供给过量可能跌到 $1。shed 非 seed 容量为 100，overflow 丢弃；animal feed、plant water、care bonus、locked tile、shop with replacement、对手私有 shed 不可见等边界都必须进入策略状态契约。

## 泛化方法

log-derived 修改必须经过 discovery、development、confirmation、final holdout 四层切分。固定 replay 只用于单状态反事实；真实 engine 的交互式 paired holdout 才能支持策略泛化。必须做 leave-one-opponent-out、leave-one-time-block-out、state perturbation 以及 24/72/144-step 长时域检查。条件不满足时 candidate action 必须 parent-equivalent；触发时只改变一个可识别变量并记录 activation、rejection、fallback 和最大延迟。

## 当前候选判断

`slot_rank_v1` 已真实触发但终局 paired delta 近零，暂不晋级。`premium_front_run_v1` 和 `terminal_product_slots_v1` 之前 activation 为零，不能由 zero delta 判定机制无效，必须先刷新当前 V42 route/future state 接口。

## 后续模型路线

将创建两个独立本地备选：

1. `guts_`：完全从规则和状态账本出发，不读取公开代码逻辑；强调 physical safety、capacity、market pressure 和 parent fallback。
2. `inspired_`：以 no-R128 V42 为父策略，只吸收优秀公开提交中的可解释机制（例如 bounded one-turn premium timing），不复制 tape；要求当前 route future suffix、pickup reserve、town demand 和 barrier 均满足才触发。

两个模型各执行两轮“编写→审阅→修改”，再做统一 engine smoke 和 paired validation。未通过泛化门槛的分支只保留研究状态，不提交 Kaggle。
