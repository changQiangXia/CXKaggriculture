# 第 2 轮：修改阶段详细计划（只写方案，不在本轮改代码）

## 目标和基线

修改阶段以当前 `no-R128 V42` 作为唯一冻结基线：

- 源码基线：`incubated_candidates/v42_ablations/no_r128/main.py`；
- 不重新打开 R128，也不触碰 opening、route selector、R127、R124、weed repair、预算和物理终局 planner；
- 研究得到的共同约束是“状态满足时做一个窄修正，否则精确返回父动作”；不复制整条高手 tape，不做全局 SELL 合并；
- 每个候选只启用一个新开关。只有单开关通过确认面板，才允许测试二者组合；组合不通过时保留各自单开关结果，不能把失败归因到另一个开关。

第 1 轮（列计划/研究）应先产出三个开关的 activation 统计和 replay 证据；第 2 轮按以下顺序实现 A、B、C 三个独立分支。每个分支都必须保留 `BASELINE` 目录和 `DIFF` 补丁，不能直接覆盖基线文件。

## 候选 A：晚期、需求感知的一步 premium front-run

### 动机

高分录像在 day 18–29 仍然使用拆分、交错的产品销售。公开代码中最可迁移的机制是 bounded one-turn front-run：利用下一回合可见 SELL 压力提前卖出一小批，同时为下一回合的 pickup 和父计划留出库存。线上日志没有支持无条件前移；因此此候选必须比现有通用 `_front_run` 更窄。

### 插入点和实现边界

1. 复制 `no_r128/main.py` 为 `incubated_candidates/v42_ablations/mod_front_run/main.py`，新增配置键 `premium_front_run_v2=False`，默认关闭。
2. 在 `Chassis.act()` 中保持原调用顺序，开关只包住 `_front_run` 调用（约 `act()` 中 `if cfg["front_run"] ...` 一段），不改 `_apply_suppression` 的债务语义。
3. 新增独立函数 `_premium_front_run_v2(action, view, projected, route, step, next_sup)`，不要重写父 `_front_run`；便于逐开关 paired diff。
4. 只允许 day 24–28（`step // turns_per_day`）且 `step % 4 != 0`；step 718/719 由终局层处理，不能提前占用其槽位。
5. 商品先限定为 `MILK`, `WOOL`, `MELON`, `STRAWBERRY`。数量为以下各项最小值：
   - 当前 `projected` 中扣除本回合已排 SELL 后的库存；
   - 下一回合对手同商品 SELL 的数量；
   - 父 route 下一回合同商品 SELL 数量；
   - `pickup_reserve` 后的可用量；
   - 每个商品单回合最多 4 单位，且不得超过父计划未来两回合该商品 SELL 总量的 1/2。
6. 只在市场公开价格高于现有 `min_sell_price`、town demand 不在本回合结算、下一回合仍有 market slot 时触发。不得读取对手 shed 等隐藏状态；只使用 observation 中公开的 `market`、`town`、父 route 和可投影库存。
7. 追加 SELL 时固定使用 `merge=False`，保持市场槽位和 SELL 顺序；下一回合通过已有 `next_sup["suppress"]` 偿还，数量不足时回退父动作并记 telemetry，不强行削减非同商品订单。
8. telemetry 至少记录：触发 step/day、商品、前移数量、价格差估计、town-demand gate、pickup-reserve、因无槽位/库存不足而拒绝的次数、下一回合 repayment 是否完整。

### A 的变体和顺序

- A0：仅加入 day 24–28 和商品过滤，数量上限 1，作为安全实现；
- A1：A0 + `pickup_reserve` 和父 route 两回合上限；
- A2：A1 + 依据公开市场曲线计算的 price-pressure gate。

先跑 A0；A0 通过后才实现 A1，A1 通过后才实现 A2。不得同时调节 `min_sell_price`、商品集合和数量上限。

## 候选 B：晚期连续 SELL 块内的收益排序

### 动机

损失日志显示局部差异来自共享市场的逐单位处理和 SELL 顺序；高分录像不支持把同商品订单全局合并。可以研究非常窄的“只在连续 SELL 块内换序”，保留订单数量、非 SELL barrier、槽位和父计划不变。

### 插入点和实现边界

1. 复制基线为 `incubated_candidates/v42_ablations/mod_sell_order/main.py`，新增 `late_sell_order_v1=False`。
2. 在现有 `_r37_reorder_sales` 所在的 market wrapper 位置接入；不得修改 `_sell_lead`、`_front_run`、R36 reservation 或 terminal planner。
3. 仅处理 day 18–28；day 29 和 step 718 保持父动作，以免和终局 liquidation 交互。
4. 仅当连续区块全部是 SELL、区块长度为 2–4、商品不重复、前后没有 BUY/HIRE/BUY_LAND/BUY_ANIMAL barrier 时排序；任何重复商品、零量订单或混合区块均原样返回。
5. 排序键使用公开、可复算的逐单位 quote-pressure（当前 inventory、market params、对手可见成熟产量的上限估计）；禁止使用 hidden rival shed。若两个商品估计收益差小于 2%，保持父顺序，避免噪声换序。
6. 数量不变，不合并，不拆分，不创建新订单；若排序后 `market` 与父动作不同，记录 block 起止、商品序列、估计收益差。
7. 增加保护：本回合存在父计划 repayment debt、pickup、town consumption boundary 或待处理购买时直接 abstain。

### B 的变体

- B0：只处理长度 2 的 SELL block；
- B1：扩展到长度 3–4；
- B2：加入 2% quote-pressure margin。

B0 是唯一默认起点。B1/B2 只有在 B0 的 paired 结果非劣且 activation 足够时才实现。

## 候选 C：718 终局商品补单的槽位受限版本

### 动机

`highscore-terminal V42` 已提交，不能修改或重提交。本地研究只能建立独立实验分支，验证公开录像中的终局产品专属销售是否比简单“全 shed liquidation”稳定。候选 C 不改变线上已提交包，也不自动提交。

### 插入点和实现边界

1. 从 `no_r128/main.py` 复制为 `incubated_candidates/v42_ablations/mod_terminal718/main.py`；如果需要比较 highscore wrapper，只把它作为参考，不直接编辑 `highscore_terminal_v42.py`。
2. 在最终 agent wrapper 的 `step >= 718` 分支（约 `_shadow_terminal`/terminal rescue 调用点）增加 `terminal_product_slots_v1=False`。
3. 先运行父 terminal action，重新计算 physical projected shed；只在父 action 已有 SELL 槽位未满时追加订单，绝不删除父 action 的 farmer/hands 或已有 BUY/SELL。
4. 候选商品优先 `MILK`, `WOOL`, `EGG`，其次按公开价格×可售单位排序；每种商品最多一个订单，最多使用剩余槽位。不能制造库存，必须通过当前 observation 的 shed/inventory 和 parent action 投影证明数量可售。
5. 如果新增订单会超过 10 个 market orders、改变已存在 SELL 的顺序、或与 `terminal_action` 的 expected state 不一致，则完全回退父 terminal action，并记录 rejection reason。
6. telemetry 记录追加商品、数量、剩余槽位、父/候选 projected shed、追加后是否全部 `DONE/720`。不做跨回合 repayment；step 718 只允许局部、可证明的终局操作。

### C 的变体

- C0：仅追加 MILK/WOOL，且每种最多 1 单；
- C1：加入 EGG；
- C2：加入价格排序但不改变既有订单。

先验证 C0。若 C0 没有明确物理收益或产生任何容量/终局异常，C1/C2 直接停止。

## 修改阶段验证面板

所有变体都按同一顺序验证，结果写入各自 `results.json`、`telemetry.json` 和 `DIFF.md`。

### 0. 静态和 smoke 门

- `python -m py_compile`；
- 导入 agent，检查默认开关为关闭；
- v37 对手，seed 9001、9002，双 seat，共 4 局；
- 每局必须 `DONE`、720 steps、stderr=0、timeout=0；
- 记录 callback p50/p95/max、开关触发次数、回退次数；任何异常立即删除该变体。

### 1. 筛选 paired panel（40 局）

- seeds `9001..9005`；
- opponents：V37、Flex、Thomas、Dmitrii；
- 两个 seat；
- 变体和冻结基线使用完全相同的 seed/opponent/seat 顺序；
- 输出终局 margin、money、sold units、market order trace、activation、latency、stderr 和 DONE。

筛选不合格条件：任意一局非 `DONE/720`、stderr 非零、timeout、非法 action、或 callback max 高于基线 2 倍。任何 opponent×seat cell 出现两局以上新增负局，停止该变体。

### 2. 确认 paired panel（120 局）

只对筛选通过的单开关运行：`15 seeds × 4 opponents × 2 seats`，沿用统一 common-seed 清单。必须提供：

- 平均 paired margin delta、median、5% quantile、最小 delta；
- 四对手和两 seat 分层均值、方差、负局数、tie 数；
- day/step 分段 delta（尤其 18–24、24–28、718）；
- activation rate、repayment 完整率、order block 改写数、terminal rejection 数；
- callback p95/max 与基线差异；
- 代表性最大正/负局 replay diff。

### 3. 组合实验（有条件）

仅当 A、B、C 中至少两个单开关各自通过 120 局确认，才允许做一组组合；组合只测试 `A+B` 或 `A+C`，不测试三者全开。组合使用新的 5 seeds × 4 opponents × 2 seats = 40 局 holdout，不得复用筛选 seeds。组合失败不回滚单开关结论。

## 晋级、停止和回退条件

### 硬性停止

出现以下任一项，立即停止当前分支并回到冻结基线：

- 任意非法 action、stderr、timeout、未完成 720 steps；
- 破坏 `DONE`、market order 上限、shed capacity、pickup/buy barrier 或 expected-state guard；
- terminal planner safety failure、repayment debt 未清、或开关异常触发到 day 1–17；
- callback p95 超基线 1.5 倍或 max 超基线 2 倍；
- activation 超过 10% 的 action，或单局改写超过 4 个 market orders，说明机制过宽；
- 40 局筛选中平均 paired delta < 0，5% 分位 < -500，或最小 delta < -2500；
- 任一 opponent×seat cell 平均 delta < -1500，或新增负局数 ≥ 2；
- 120 局确认中任一对手/seat 分层持续退化，且不能用 dormant activation 解释。

### 晋级条件

单开关从筛选晋级确认需满足：全局平均 delta ≥ 0、q05 ≥ -500、无硬性失败、各 opponent×seat cell 平均 ≥ -1000。晋级提交候选池需再满足 120 局：平均 delta ≥ +200、q05 ≥ -300、min delta ≥ -2000、负局数不增加超过 1、两 seat 差异不超过基线的 10%，且 activation/latency 均在范围内。

若没有任何分支达到晋级条件，保留 no-R128 V42 和已提交的 highscore-terminal 作为线上观测，不提交新包；修改轮的结论应记录为“未找到可证明提升”。

## 交付物

每个分支必须交付：源码副本、单一开关 diff、40 局筛选 JSON、120 局确认 JSON（若运行）、telemetry 汇总、最差局 replay diff、`py_compile` 日志和一页结论。整个三轮流程的审查轮再依据这些交付物决定是否形成候选，不在修改轮自动打包或上传。

## 执行记录（2026-09-15）

已按最小安全变体建立三个独立目录：`slot_rank_v1`（B0）、`premium_front_run_v1`（A0）、`terminal_product_slots_v1`（C0）。每个目录含源码副本、`MANIFEST.json` 和 tar.gz。三个源码均通过 `python -m py_compile` 与动态 import smoke。v37/9001/seat0 的单局 smoke 为 DONE/720；其余长局因本地 kaggle engine deepcopy 耗时中断，尚未进入 paired 筛选。所有分支仍处研究状态。
