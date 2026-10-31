# Static final review: `guts_` and `inspired_premium_v1`

审阅对象：

* `research_20260915_125615UTC/guts/main.py`（当前 round-2 文件）
* `incubated_candidates/v42_ablations/inspired_premium_v1/main.py`（文件末尾定义的最终 `agent` wrapper）

本轮只做静态审阅，没有改动模型逻辑，也没有调用 Kaggle submit。

## `guts_`

### 已确认的安全点

* `agent` 只从当前 `obs` 读取自己的 `farms[p]`、`private`、`day/hour`；没有访问另一个 seat 的 `private`，也没有读取 replay、线上 log 或对手隐藏 shed/inventory（`main.py:19-27`）。
* 每个 actor 只生成一个 farmer/hands 命令，并通过 `used` 避免两个 actor 同时领取同一块 tile（`main.py:41-47`）。
* 市场列表最终使用 `orders[:10]`，在固定比赛配置 `maxMarketOrdersPerTurn=10` 下不会超过订单槽位（`main.py:47`）。
* watering 的任务优先级为 0，harvest 为 1，plant 为 2；因此同一回合会先保护未浇水作物（`main.py:33-40`）。

### 风险和边界

1. **没有显式 terminal guard（中风险）**。`agent` 没有 `step>=718` 或 episodeSteps 检查；在正常 Kaggriculture callback（0..718）下 step 718 仍可能返回 WATER/HARVEST/PASS，若 runner 额外调用 step 719，则也会继续构造动作（`main.py:19-47`）。虽然 `day < 27` 已阻止晚期 PLANT，仍应在最终候选测试中记录 718 的实际执行和 719 是否被调用。
2. **固定订单上限而不看 configuration（低风险，固定赛制下可接受）**。代码永远按 10 截断；如果测试使用较小 `maxMarketOrdersPerTurn`，动作可能被 engine 截断或拒绝。当前官方配置固定为 10，因此不是本赛制 blocker。
3. **经济/容量保护很薄（中风险）**。`main.py:26-32` 把 shed 中所有已知物品按库存量加入 SELL，再把 seed/HIRE/BUY_LAND 订单混入并截断。没有按价格、预算、夜间 shed 容量或订单优先级重新分配；`orders[:10]` 可能静默丢掉后面的 seed/hire/land 订单。这个问题不构成越权，但可能使最终 money 低于强 parent。
4. **`_MEM` 不是完整 episode 状态（低风险）**。它只写入 `day` 且从未参与决策（`main.py:3,23`），不会泄漏未来信息，但多 episode 重用模块时也没有显式清空；可视为无效状态，应在 telemetry/test 中确认不会影响结果。
5. **作物计数是当前 tile 数，不是累计产量（中风险）**。收获后 `nmelon`/`nwheat` 下降，策略可能重新购买并种植同类作物；这是策略选择而非状态泄漏，但会造成重复种植和资源预算压力（`main.py:24-30`）。

## `inspired_premium_v1`

最终启用链为 `_INS2_PARENT -> INS round-1 wrapper -> R128 parent`，最终 `agent` 在 `main.py:3247-3284`。

### 已确认的安全点

* front-run 只在 day 24..28、非 `step%4==0`、且 `step<718` 时考虑；`route` 长度为 719，step 718 因 `step+1>=len(route)` 退出（`main.py:3210-3214`）。
* 新增订单数量固定为 1，且先检查 `len(market)>=10`，因此添加后最多 10 个订单（`main.py:3215-3216,3228-3231`）。
* 新订单数量受当前 `private.shed[item]` 限制，价格从当前 observation 的 `market.prices` 读取；town gate 只使用公开 `unlocked_shops`（`main.py:3217-3227`）。没有读取对手 private state。
* repayment 失败会返回 `parent` 原动作；异常也回退 parent（`main.py:3265-3268,3281-3282`）。

### 必须在测试报告中标出的风险

1. **高风险：错误识别 parent 原有 SELL 为“本 wrapper 追加的订单”**。Round-2 的 debt 检测遍历 `out = _INS2_PARENT(...)` 的全部 SELL；只要商品属于 `_INS_ITEMS`、数量 `<=1`，且静态 route 下一回合也有该商品 SELL，就登记 debt（`main.py:3270-3279`）。它没有保存 `_ins_action` 添加前后的 market 差异。因此 parent 自己原本的一单位 SELL 也会被误标，下一回合 repayment 会扣减 parent 的 SELL。
2. **高风险：repayment 可能留下数量为 0 的 SELL order**。扣债逻辑直接执行 `o[2]-=take`，没有删除变成 0 的 order（`main.py:3258-3264`）。若 engine 要求正整数数量，该动作可能被判无效；即便 0 被接受，也会改变 parent 原有订单形状。该风险与上面的误标 debt 叠加。
3. **中高风险：future route 不是当前 parent 的真实下一回合动作**。`_ins_route_for` 读取 `_IMPL.chassis.routes[route]` 的静态 tape（`main.py:3200-3208`），而 `_INS2_PARENT` 之后还会运行 R124/R127/R128 wrappers，这些 wrappers 会按当前 observation 改写动作。`next_orders = route[step+1]['market']`（`3223`）以及 debt 的 `own_next`（`3274`）可能与 parent 下一回合实际 market 不一致；这解释了已观测到的 trigger=0，也使触发条件和 repayment 证明失去稳健性。它不是读取环境隐藏未来，但属于对自有静态计划的未来耦合，必须做 fresh-route/activation profile。
4. **中风险：telemetry 跨 episode 未完整重置**。step 0 只重置 `_INS_STATS` 的 `triggered/units/repaid/rejects/errors`（`3235-3237`）；`_INS2_STATS['repay_attempts'/'repay_complete'/'repay_fail']` 没有同步清零。重复运行多个 episode 时这些计数会累加，不能直接按单局解释。
5. **低风险：telemetry 字段语义不完整**。`_INS_STATS['repaid']` 与 `rejects` 从未递增；最终字典主要应使用 `repay_attempts/repay_complete/repay_fail` 和 `triggered/units`，否则报告中的“repaid=0”容易误读（`main.py:3198,3236,3257-3267`）。
6. **低风险：repayment 成功判定只检查可匹配数量，不检查最终订单预算/形状**。正常 parent 应已有合法订单且数量上限不变，但在 parent 订单异常或动态 wrapper 改写时，应对返回 action 再做 schema、正数量、<=10 检查。

### 本轮结论

* `guts_` 没有发现对手私有状态或外部未来信息泄漏；它的主要问题是策略简单、容量/预算/terminal 保护弱，适合作为独立 baseline。
* `inspired_premium_v1` 的订单上限和异常 fallback 基本存在，但 debt 识别与静态 route 耦合是实质性研究风险；在修复或至少通过专门的“parent 一单位 SELL + route 下一回合 SELL”合成测试前，不应把任何正收益或 repayment telemetry 解释为可靠证据。
* 两个模型都应继续做固定 engine 的 718/719 边界 smoke、schema validator，以及多 episode telemetry reset 检查；当前不提交。

## 修复记录（本轮）

经复核，`inspired_premium_v1/main.py` 末尾 wrapper 已落实三项修复，并已重新打包：

* `_INS_LAST_TRIGGER`（`main.py:3200,3232,3256,3280`）记录 `_ins_action` 本次实际追加的 `(item, qty)`，Round-2 只从该 marker 建 debt，不再扫描 parent 的全部 SELL；
* repayment 扣减后过滤 `SELL` 数量 `<=0` 的订单（`main.py:3274`）；
* `step==0` 时清零 `_INS2_STATS` 的 `repay_attempts/complete/fail`，并清理 seat 的旧 trigger（`main.py:3253-3257`）。

验证：工作文件与 archive 内 `main.py` SHA256 均为 `263c93cb45c6b96067d79f38fda4dd47b18174b6300c6f47c5b5addaf684a0f9`；`python -m py_compile` 通过；`smoke_inspired.py` 在 seed 9001 vs pass 完成 `DONE`, 720 steps，`errors=0`，`repay_attempts=0`, `triggered=0`。未提交 Kaggle。

补充定向单元检查：构造一笔 `MILK` debt=1、parent 返回 `SELL MILK 1` 时，返回 action 已删除该零数量订单并保留其他订单；预置 `_INS2_STATS` 后调用 step 0，三个 repayment 计数均正确归零。

追加 seat-1 smoke：seed 9002、`pass` 对 `inspired_premium_v1`，完成 `DONE/720`，两方 status 均 `DONE`，`errors=0`。
