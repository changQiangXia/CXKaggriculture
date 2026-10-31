# Q25 v4 worker-only 局部搜索设计

日期：2026-09-17  
基线：`/root/autodl-tmp/candidate_v45_q25.py`（candidate_v45_q25 / Q25）  
目标：在不改市场订单、不改普通 tape 工人、不改变开局投资的条件下，给已经确认职责的晚期 V219 工人提供一个小范围的路线顺序搜索。

## 1. 先澄清当前模型的工人逻辑

Q25 的主干由 `Chassis` 回放 `_ROUTES` 中的静态 tape，然后依次运行 `hand_align`、`weed_repair`、卖单抑制、预算和仓库保护等层。它不是一个可以随意重算全盘任务的纯贪心 agent。`_v219_worker` 只在满足 `_v219_qualifies`、完成第 18 天番茄投资并确认新增帮工之后接管相应 actor；其他 actor 仍由父 tape 和响应式层处理。

V219 worker 当前每个回合会：

1. 处理肥料返仓或 `PICKUP FERTILIZER`；
2. 扫描自己 `role['targets']` 内的地块；
3. 对能执行的 `WATER`、`FERTILIZE`、`HARVEST`、第 18 天 `PLANT` 等任务，用曼哈顿距离选最近目标；
4. 在剩余时间只够回仓时优先回到四个 shed-access 格；
5. 有货物时回仓 `DROP`/`PLACE`。

`_r53_labor_assignment` 已经在雇佣时对预定义的 target group 做了有限排列，以最小化各组的最大路线成本。v4 不应重新分配角色、改变 spawn、改变雇佣数量或接管主农夫。可搜索的缺口是：一个 actor 在自己的 target group 内每步选择最近目标，可能造成总路线长度变长；成熟、快过期和需要连续操作的地块也没有进入同一个排序目标。

## 2. v4 的最小可行范围

v4 只尝试以下范围：

* 只在 `state['workers']` 中已经确认的 V219 actor 上运行；
* 只处理 `role['kind'] == 'crop'` 或 `role['kind'] == 'fertilizer'`；
* 只从当前 actor 已有的 `role['targets']` 产生候选；
* 只使用当前 observation 中可见的 farm/private/market 数据；
* 只替换**当前 actor 当前一步**，必要时将一小段（最多当日剩余时间）路线放入 actor 的私有计划，下一 callback 重新验证；
* 所有 market 字段完全保留父动作。worker-only 实验不允许同时触发 v3 SELL 搜索；联合版本也必须先单独通过 worker-only 验证；
* 普通 tape actor、`_r53_labor_assignment` 的 spawn/分组、`_v219_request` 的 HIRE/BUY_LAND/BUY_SEED、`_r70` 肥料购买和 `_r128` 服务层保持原行为。

这样搜索的是“已投入且已确认的专属工人如何访问自己的已知地块”，而不是用一条录像替换整局行为。主 farmer 和普通帮工不被重排，可以减少改变随机状态、shed 竞争和父模型时序的风险。

## 3. 状态表示与安全边界

每个玩家、每个 V219 actor 使用如下易失性状态；在 `step == 0` 或 step 倒退时全部清空：

```python
state['worker_plan'][actor] = {
    'day': int,
    'targets': [(x, y), ...],       # 尚未完成的私有顺序
    'cursor': int,
    'expected': {                   # 仅用于下一 callback 的观察核验
        'step': int,
        'pos': [x, y],
        'command': ['EAST' | ..., ...],
        'tile_fingerprint': tuple,
    },
    'abandoned': False,
}
```

计划不能跨日延续。以下任一条件发生时立即删除该 actor 的计划，在当前 step 和后续 step 回退到原 `_v219_worker`：

* observation 的 `step`、player、day 或 actor 数量不连续；
* actor 的实际位置不同于上一计划预期位置；
* 目标 tile 的 fingerprint 改变（被其他 actor 收获、变成 WEED、被 DIG/PLANT、产量或浇水状态变化）；
* private inventory、shed 总量或 seeds 与投影不一致；
* actor 不再存在（雇佣短缺/对局重置）；
* 当前 `configuration` 不是固定的 10x10、24 turns/day、720 steps、shed 100、最多 10 orders；
* 当前 step 距离当天结束不够完成返仓和 DROP；
* 搜索或路线生成异常、耗时超过预算。

fingerprint 只包含规划需要的公开字段，例如 `kind`、`crop`/`animal`、`yield_units`、`watered_today`、`fertilized_until_day`、`fed_today`、`cared_today`、`fertilizer_available`、`planted_day`。不能保存或读取未来 hidden state。

## 4. 候选任务和路线

### 4.1 合法任务

对一个 actor，在当前 observation 的 role target 集合内生成：

* `WATER`：目标是自己的番茄且 tile 尚未浇水；
* `FERTILIZE`：fertilizer worker 或 role 标记需要肥料，且手上有肥料、tile 仍可施肥；
* `HARVEST`：`yield_units > 0` 且已达到 `first_yield_day`；
* `PLANT TOMATO`：只限 day 18 的已有 V219 规则，v4 默认不重新规划种植；
* `RETURN`：携带货物时前往最近 shed-access 格并执行 `DROP`/合适的 `PLACE`；
* `PASS`：没有满足硬约束的任务时保持原行为。

`BUILD_*`、`DIG`、`FEED`、动物安置、购买、雇佣和跨角色偷取同一目标不在候选集中。V219 crop worker 的 `role['targets']` 是静态责任边界，不能为了“距离更近”访问别组地块。

### 4.2 路线长度

棋盘没有移动阻挡，`FARMER_MOVES` 的最短步数就是 Manhattan 距离。为了与现有执行一致，路线方向固定复用 `_v219_walk` 的 x 优先顺序（先 EAST/WEST，再 SOUTH/NORTH）；不要用不同的等长路径，以免改变未来 tile 访问时序。

对任务序列 `p_1, ..., p_k`，估计成本为：

```text
dist(start, p_1)
+ Σ dist(p_i, p_{i+1})
+ 每个任务的操作回合数
+ dist(p_k, nearest_shed_access) + drop_cost
```

操作回合数按实际 action 计数：`WATER/FERTILIZE/HARVEST/PLANT` 各 1，取货/放货按 `_apply_unit_action` 的一次 callback 计。不要把 shed 的四格当作同一个坐标；`_v219_home` 选最近 access tile，并使用固定索引打破平局。

### 4.3 受限组合搜索

每个 actor 的 target 通常不超过 10 个。每 callback 至多取以下候选：

* 原 `_v219_worker` 选择的最近目标（基线，永远保留）；
* 价值/额外步数最高的最多 3 个目标；
* 有硬时间窗的最多 2 个目标（当天最后可收获/必须先浇水的目标）；
* 携带货物时唯一的返仓候选。

对候选 target 做深度 2 或 3 的 beam（beam width 4，最多 12 个路线），不做全局排列。每个节点保存当前位置、已访问 target、预计剩余回合、预计携带货物；若剩余时间不足以返仓，节点丢弃。搜索总预算默认每 actor 每 callback 1.5 ms，单回合所有 actor 合计 6 ms；超时直接返回父动作。

若需要日内计划，可用 Held-Karp 风格的 bitmask 只求当前 target 集合的前 2 个访问点：`N <= 10` 时状态数不超过 `1 + N + 3N^2`。不应把整个 24 回合或全局 720 步复制到 agent 内。

## 5. 评分函数

搜索评分是“可兑现产量减去路线代价”，不是单纯最近距离：

```text
score = Σ product_price(item) * expected_units
      + urgency_bonus
      - move_cost * travel_steps
      - operation_cost * operations
      - deadline_penalty
      - shed_overflow_penalty
      - baseline_deviation_penalty
```

建议初始常数（仅作为可审计的候选，不是线上结论）：

* `move_cost = 1`；
* `operation_cost = 0.2`；
* `urgency_bonus = 0.5 * price * units`，仅在距产量窗口结束不超过 2 天时使用；
* 不能在 day 29 把浇水价值当作未来收益；
* `deadline_penalty = 4 * price * units`，任务预计无法在窗口内完成时直接丢弃，而不是靠巨大负分；
* shed overflow 为硬拒绝，不是普通软惩罚；
* `baseline_deviation_penalty` 取 0.1–1.0 的小值，并且只用于同分时优先父动作。

价格可使用当前 observation 的 `market.prices`，但只把它作为当前排序信号。不得把未来卖单价格、对手私有库存或录像中的动作作为确定值。

## 6. 状态投影和合法性检查

候选动作必须通过与官方引擎一致的逐单位投影：

1. 用 `_r127_fields(obs, action)` 或等价的 `_PLANNER_NS['_apply_unit_action']` 克隆 farm/private；
2. 按 actor 顺序应用移动/操作，处理同一 crop 的 `PLANT` 需求冲突；
3. 检查 actor inventory 增减、shed 容量、tile fingerprint 和角色 target 所有权；
4. 对同一步的其他 actor，候选投影必须至少保持 baseline 的已获得货物和 deposit 前缀；
5. 候选不得减少 baseline 在未来仍需的 shed 商品，不得制造负库存；
6. 不修改 `market`，因此不在 worker-only 层模拟订单或价格；
7. 通过后只返回一个合法 action，hands 数量按真实 `farm['hands']` 对齐。

一个候选被接受的最小证书是：

```text
candidate_overflow == 0
每个 baseline 已完成的 deposit/acquire 前缀都仍然完成
角色以外的 actor 动作未改变
当天返仓可达，且携货 actor 在结束前有 DROP/PLACE
候选的 projected value > baseline projected value + margin
```

没有正的物理收益时必须返回父动作。即便候选预计多收获，也要在下一 callback 对位置、tile、inventory 做核验；核验失败后永久放弃该日计划，不能继续执行陈旧路线。

## 7. 推荐的代码接入点

不要改动原始 `candidate_v45_q25.py`。在构建脚本中复制 Q25 文件并在 `_V219_PARENT` 之后插入薄包装：

```python
_V4_WORKER_PARENT = agent
_V4_WORKER_STATE = {}

def _v4_worker_action(observation, action):
    # 仅 standard config、已确认 V219 worker、非 day18 planting。
    # 先核验上一步 expected；失败则清空 actor plan 并调用原 _v219_worker。
    # 搜索只决定当前 actor 命令，market 原样保留。
    return action

def agent(observation, configuration=None):
    action = _V4_WORKER_PARENT(observation, configuration)
    if standard_configuration(configuration):
        action = _v4_worker_action(observation, action)
    return action
```

实际包装应放在现有 V219 `agent` 的最终定义之后、任何新的 market-only 层之前，并更新最终 `agent.telemetry`。如果与 v3 SELL 层联合，先把 worker-only 层放在 market 层之前，且在任何异常时把完整父 action 返回；不可只回退 farmer 而丢弃父 market。

## 8. 验证顺序（先 worker-only）

### A. 单元与差分

* 对 1000 个随机合法 late-game observation，候选 action 用官方 `_apply_unit_action` 和投影器比较：位置、tile、inventory、shed 必须一致；
* 专门覆盖四个 shed-access 格、locked tile、肥料、成熟/未成熟番茄、同一商品双 actor `PLANT` 和 shed capacity 99/100；
* 检查 `_v219_worker` 的 day 29 返仓边界和 day 18 种植路径完全回退；
* 测量最坏单 callback 时间，含 loader，不得接近官方 1 秒限制；建议 p99 < 10 ms。

### B. 机制消融

固定 Q25 和同一 tape，只比较：

1. Q25 parent；
2. worker-only v4；
3. market-only v3（已有候选）；
4. joint v4（只有在 2、3 各自通过后）。

任何实验都使用真实双方交互的 720 step game，不能用固定 replay action 证明强度。每个 seed 两个 seat，胜负按同 seed 配对，按 opponent family 聚合；相同 Beyond/V46/Pipe8 农业骨干只能算一个相关 family，另留 V37/Thomas/Dmitri/Reactive 作为机制 holdout。

### C. 预注册晋级门槛

在看结果前冻结：

* 开发集至少 4 个 seed、每家族两个 seat；
* 未见确认集至少 8 个 seed，包含至少 3 个相关之外的 opponent family；
* 候选不得出现确认集 `W -> L` 的集中回归；
* 任一家族点数差不得低于预设容忍值（建议不低于 -0.05）；
* overall clustered bootstrap 的点数差必须为非负，且不能只靠单个 seed 或单个 family；
* 若 outcome 不变而仅现金 margin 增加，标记为“安全但未证明更强”，不提交；
* 任何不健康对局、超时、异常或 safety_failure 都使该 panel 不具晋级资格。

## 9. 已知风险与明确禁止项

* `v1` 搜索时曾有错误的市场锁步模拟；worker v4 不得复用未差分验证的简化未来模拟器。
* worker 路线会改变 tile 被访问和清空的时间，可能影响日末 `_spawn_weeds` 的空地集合；因此所有跨日承诺都禁止，计划每天清空。
* 同一 crop 的产量与卖价有市场库存反馈；worker-only 只优化“实际多拿到的货”，不把预期现金提升当成线上强度证据。
* 不能从某个失败 replay 直接复制一串动作；对手响应和随机状态会随动作改变。replay 只能用于发现待验证的机制。
* 不能借助未来 observation、对手私有字段、隐藏 shop draw 或 tape 中未发生的动作。
* 不得为了让候选看起来有提升而扩大 beam、放宽 overflow 或降低回退门槛。搜索越大，越需要独立 holdout。

## 10. 当前建议

第一版 v4 应只实现“同一 V219 actor 的 target 顺序 beam，逐步执行并核验”，把评分和候选数量写成常量并记录 telemetry：`search_calls`、`search_accepts`、`search_abandons`、`fallbacks`、`max_ms`、`extra_harvest_units`、`overflow_rejects`。若 worker-only 在确认集没有 W/T/L 改善，保留为安全实验分支，不要再将 market 重排和 worker 路线同时调参。只有当 worker-only 通过独立确认，才构建 joint v4，并继续使用 Q25 原动作作为每一步的可逆 fallback。
