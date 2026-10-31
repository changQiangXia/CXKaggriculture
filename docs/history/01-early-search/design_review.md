# V37 后续候选设计审查：阶段级「现金–货运联动」策略

更新时间：2026-09-14 UTC。本文是设计审查，不是可提交实现；没有修改 `public_v37_pkg/main.py`，也没有读取对手私有状态。

## 选择的、尚未证伪的假设

**H-DSS（day-block delivery scheduler）**：V37 的生产闭环和资产路线已经在公开面板中很强，败局主要集中在同量商品的成交时点、共享市场的批次竞争，以及 day 26/29 附近 `shed + carried + 当轮产出` 的耦合。当前 V37 的 `R36` 预留和 `R37` contiguous SELL 排序分别处理未来 SELL 数量和订单顺序，但没有在一个阶段内同时决定“哪名工人何时回仓、哪一批已确认货物何时出售、哪些低价值产出可以等待”。

因此，候选不改变开局、动物数量或 crop yield，而是在公开阶段边界（`step ∈ {288, 360, 432, 504, 576, 648}`）选择一个**完整的 72-step 货运/销售 profile**。profile 一旦选定，直到下一个边界保持不变；它联合生成工人回仓、`HARVEST`/`COLLECT_FERTILIZER` 的安排和已有 SELL slot 的数量/顺序，并维护与 R36 相同的 sale debt。它不是每回合的价格阈值，也不是全局抑制 harvest：只有在 profile 的模拟账本显示能消除 overflow 且不会减少后续高价值产出时才改变动作。

这个假设尚未被现有实验直接证伪。已有 overflow623/695 是单点 gate，MILKLEAD 是单商品提前一回合，quote-floor/threshold scan 是固定阈值，route 1/2 是整条不兼容 tape；它们都没有执行上述“阶段内工人路径 + 库存 + market slot + debt”的联合选择。

## 状态契约和可见输入

每个 seat 维护独立状态 `DSSState`：

```text
profile              # native | premium_convoy | staple_buffer | endday_runner
block_start, block_end
debt[due_step][item] # 提前成交后在原 due_step 扣除的数量
reserved_pickups     # (step, actor, item, qty)
market_slots_used    # 当前 action 的 SELL/BUY/HIRE 槽位账本
last_action_digest   # 检测父动作或 observation 漂移
abandoned, reason    # 任何不一致立即回退 V37
```

选择器只读取：

- 我方 `farms[player]`、`private.shed`、各 worker inventory/position、money、tiles、unlocked quadrants；
- 当前 `market.inventory/prices/params` 和公开对手 tiles 的 crop/animal、yield_units；
- V37 route 的未来 SELL suffix、`PICKUP`/`BUY_PRODUCT`/`BUY_ANIMAL`/`HIRE` barrier，以及当前 R36 debt；
- 固定的 engine 规则和 72-step block 边界。

禁止读取对手 `private`、未来 observation、未来 action tape 的对手版本、随机数或终局结果。缺字段、worker 数量变化、engine 配置不符或账本无法守恒时，`profile = native` 并返回父动作。

## 四个完整 profile

所有 profile 都从 V37 当前状态开始，保持 feed/care、购买确认、weed repair、R36/R37 debt 和终局清仓不变。

1. `native`：逐字执行 V37，作为安全回退。
2. `premium_convoy`：把已在 shed 或能在 block 内安全送达的 MILK/WOOL/STRAWBERRY/MELON 作为 convoy 货物；分配一名不会承担当日 feed/care barrier 的 worker 回仓，优先填充已有的 SELL slot。原计划回合登记等量 debt，不追加超过 10 个 market orders，也不夺走父策略的 PICKUP/BUY barrier。
3. `staple_buffer`：当低价 WHEAT/CARROT 占据容量或订单槽时，将其销售/搬运推迟到 block 后仍可完成的第一个父 slot，同时先清理已经确认的 premium cargo。该 profile 仍执行全部成熟高价值 HARVEST；只有物理模拟证明某次低价产出会溢出且没有后续生产机会时，才把该次低价 harvest 延后一回合。
4. `endday_runner`：在 day 26–29 的 block 中预留一个现有 worker 做短回仓路径，目标是消除最后一小时携带物与 shed 的叠加；若该 worker 预计会错过 feed/care、成熟 premium harvest 或 R51 fertilizer pickup，则 profile 不合格并回退 `native`。此 profile 改的是完整 worker path，不是单一 step-623/695 harvest guard。

## 最小实现边界

在独立模块实现以下纯函数，先不接入最终导出 `agent`：

```python
def select_dss_profile(obs, parent_action, parent_state, route, block_start): ...
def simulate_dss_block(obs, config, parent_suffix, profile, *, detailed=True): ...
def apply_dss_profile(obs, parent_action, dss_state): ...
```

`simulate_dss_block` 使用当前仓储/单位 engine，在 `block_start..block_start+71` 复制我方可见状态，逐回合执行父 action 和 profile action。它记录每回合：shed、各 actor carried、实际 deposit、产量、SELL 成交量/价格、market slot、未来 barrier 和 overflow。对价格不确定性使用三个公开可复现情景（对手 standing yield 的低/中/高批次），不使用隐藏库存。

`select_dss_profile` 只在边界调用，计算保守分数：

```text
min_scenario(
    sold_value
    - 4 * overflow_units
    - 2 * missed_parent_deposits
    - 1 * missed_premium_units
    - 0.5 * seat_or_profile_variance_proxy
)
```

只有候选 profile 在所有情景中 `overflow_units == 0`、非本 actor 的父 deposit 前缀逐回合不减少、原有 BUY/HIRE/PICKUP barrier 不变，且保守分数严格高于 `native` 时才可选择；差距小于预注册 margin（建议 50 coins）时保持 `native`。`apply_dss_profile` 每次输出三份 telemetry：父 action、profile action、最终送入 engine 的 action，并在原计划 due step 扣除相同数量的 debt。

这是最小可证伪版本：最多四个 profile、每个 block 最多 32 个确定性模拟，先只覆盖 day 12–29；不训练神经网络、不引入新 route tape。若最小版本没有稳定信号，停止该分支，不增加更多 profile 或阈值。

## 验证顺序

1. **工具链与 no-op**：固定 golden replay 重跑逐状态一致；`native` profile 的 action 必须和 V37 逐字相同；`py_compile`、720 steps、零 stderr/timeout。
2. **screening**：至少 15 个未见 seed、Flex/Thomas/Dmitrii 各 10 个 seed、双 seat；使用 common random numbers 与 V37 配对。先看 block-level overflow、premium sold value、父 deposit 前缀和 action-level delta，再看终局 margin。
3. **真实败局机制集**：至少 12 场已收集 loss tape，覆盖轻微、几千分和极端落后；固定 tape 只作因果诊断。必须验证 623/695 的 carried+shed 溢出是否下降，并确认未牺牲后续 MILK/WOOL/STRAWBERRY 产量。
4. **confirmation/holdout**：冻结未参与 profile 选择的 seed、opening、对手族和线上时间段；最终 holdout 还需包含未见 shop 序列。报告 paired mean/median、win/tie/loss、最小 margin、5% 分位、seat 差异和 bootstrap/Wilson 区间。
5. **交互式复验**：固定 tape 有利而自适应对手无收益时淘汰；只在一个 opening、seat 或对手贡献收益时淘汰。任何 runtime、订单非法、账本 mismatch 或 latency 回归都淘汰。

## 预先登记的证伪条件

满足任一条件即冻结并归档，不继续调 profile：

- 两个独立 holdout block 中 paired mean 不高于 native，或新增任意系统性负 margin；
- 5% 分位、最小 margin、seat 方差或负局数明显恶化，即使平均 sold value 上升；
- fixed tape 的收益无法在自适应 Flex/Thomas/Dmitrii 面板复现；
- overflow 减少但 premium 产量/成交量下降，或 R36 debt、BUY/HIRE/PICKUP barrier 改变；
- profile 实际触发率低于 5%，说明假设不可达；需要再加互相覆盖的 gate 才能获得收益；
- 模拟器与 golden/线上 replay 逐状态不一致，或任一局未完成 720 `DONE`、出现 stderr/timeout。

若通过 screening 和 confirmation，候选仍只标记为 `incubating`，生成完整报告、源码/包 hash 和回滚包，等待用户明确授权；本文不授予提交权限。

## 与已有候选的关系

`v37_h5sim95`/`v37_h5sim96` 只改变 horizon 相似度分支，不能代替 H-DSS；它们仍是独立候选并按原报告验证。H-DSS 不修改 `_V231_CAP`、similarity threshold、MILK 单品 gate、全局 623/695 guard，也不采用 cap2。若 H-DSS 不能稳定超过冻结 V37，线上基线保持 V37，停止继续局部修补。

