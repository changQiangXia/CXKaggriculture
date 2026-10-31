# v37 / V43 / competitive_v45 / Nathan corrected 行为族比较

## 执行入口与源码身份

| 模型 | 当前基线文件 | SHA-256（source） | 本地解包后的最终入口 | route 数 | 主要额外层 |
|---|---|---|---|---:|---|
| v37 | `public_v37_pkg/main.py` | `94c1c2c05ae7cde8fca9ee3957b01112c1cbab82c7434aae6a5f24fa7485bc4c` | 最后重新插入的 `agent` | 13 | 基础 chassis、shop route、R36/R37 sales、V233 sheep、R51 input/warehouse、R53 labor |
| V43 | `v43_real_20260916/v43_optimized_final.py` | `38f65166f5241fa73d78fea781cd3f98de62772805292a75396b76a7db43a3bd` | 最后 `agent`，包含 TERM16 | 41 | V37 全部主要层 + R85/R86/R88/R95/R97/R124/R127/R128/R148 + terminal planner/TERM16 |
| competitive_v45 | `submission_competitive_v45.tar.gz`（研究副本 `v45_research_20260916/v45_no_open.py`） | archive `b8c2f5aab88faf2332e45f721ec83e5f9e7bec3d0a995cc0dce318badd884ed0`；no-open source `5f1b35883484f050599f091e459f3ad70f2bf49f30a42dfc7b8ac781aa2a49be` | 最后 `agent`，线上包在 V43 之上加入 race 与 opening | 41 | V43 基础 + clone-gated horizon 8/24 race + step-0 WHEAT round-trip opening |
| Nathan corrected | `nathan_3rounds_20260916/corrected/main.py` / tar | source `fe906789dc90062989983477ae272d246c07ffb4aa1cf468ab55331022e12052`；archive `c7d8ed1f5da2f047eeb3d9ae96eb3774a178647374d7cd16fb07425d7e3893f1` | 最后 `_NC2` wrapper（并显式 `agent=globals().pop('agent')`） | 41 | V43 基础 + Pipe-3 route-specific opening + corrected loader/槽位截断保护 |

四者都以同一 Kaggriculture 1.32.7 engine 语义为目标，使用固定 route tape 作为主策略，再以 observation wrapper 做局部修补。任何“关闭某层后分数变化”的结论必须通过 Kaggle `get_last_callable` 文件入口复核，不能只 import 后调用命名 `agent`。

## 稳定的共同范式

1. **路线 replay + 第 6 天 shop 路由切换。** v37 只有 13 条 route，主要把包含 `YARN_STORE` 的 shop pair 映射到旧路线；V43、V45、Nathan 使用 41 条 route 和 27 个新 shop 计划，并在 step 144 左右根据前两个公开 shop 选择 route，step 648 强制 terminal route 2。这是跨版本最稳定、最可能泛化的生产范式：观察需求后选择一整条生产路线，而不是对单局 tape 做一个动作替换。
2. **保守的供料/服务层。** `hand_align`、`weed_repair`、R36 future-sell reservation、R85 feed/fertilizer economics、R86 reachability、R95 replenishment、R97 wheat supply、R124 atomic opening/seed budget、R127 last-hour field safety、R128 next-day service/sale-credit 在 V43/V45/Nathan 中都存在。它们在满足状态证书时改动作，否则返回 parent action；`budget_guard`、`room_guard`、`clamp_sells`、`dead_stock`、`front_run` 仍关闭。共同经验是“小而可证书化的修补”比全局风险开关更可靠。
3. **实际成交与槽位优先。** 引擎按同一 market index 逐槽处理双方订单；删除零量订单或向前移动 SELL 会改变双方配对。因此任何候选都必须记录原始前 10 槽、有效成交量、barrier 和现金变化。V37/V43/V45/Nathan 的 nominal `SELL ... 1000` 不能当作实际成交量。
4. **终局 route-2 / cargo closure 是共同结构，收益证据较弱。** V43 的 TERM16 和 Nathan 的 terminal rescue 只在最后回合或 step 712–718 的物理状态满足时动作；它们不能解释中段长期差距，也不应作为主要优化方向。

## 有明确差异、且可能对手特化的机制

### v37 → V43：覆盖面扩大而非单一手法

- route 从 13 扩到 41；shop pair 不含 Yarn 时，V43 使用新 demand-aware route，显著增加非 Yarn 需求覆盖。
- opening 从 v37 的 `BUY WHEAT 13, BUY WHEAT 30, SELL WHEAT 30` 改成 `BUY 5, BUY 10, SELL 60`。这提供现金和较低输入成本，但会改变共享 market 价格/RNG，不能视为自家独立优化。
- V43 增加 R85–R128 资源约束层，核心增益应优先归因于 route coverage + 可兑现的供料/服务计划；既有面板报告显示 V42/V43 相对 v37 的跨对手优势，但不能把旧公开面板直接外推当前线上。

### V43 → competitive_v45：两项明显条件性 exploit

- **step-0 opening arm：** 精确匹配父动作时改为 `BUY WHEAT 70; SELL WHEAT 70`（随后极窄的 step-1 修正）。目的是利用共同 market index 让采用“第二槽继续买 wheat”的克隆路线少买 MELON seed。它改变公共价格和 RNG；面对先 SELL 再 BUY 或动态 opening，方向可能反转。线上包的公开分数后续上升不能证明该 arm 的因果收益。
- **clone-gated race：** 公开 farms/tiles/shops/market 检测连续相似后 horizon=8；观察到对手在商品刚进入库存的回合销售、己方未销售时升级 horizon=24。它不读取对手 private shed，但依赖“对手与我方是同族 route”的识别；异类策略可能误触发。
- 本地小消融显示 race arm 的影响主要集中在 V43/Nathan 类似路线，对 flex 近中性略负；opening arm 是更大的公共状态扰动，不能从固定 tape 反事实直接估计线上收益。

### V43 → Nathan corrected：opening route 特化 + loader 修复

- Pipe-3 对 route 101、103–109、111、119、120 使用 V43 opening（`BUY 5, BUY 10, SELL 60`）；其余 route step 0 仅 `BUY WHEAT 5`，并在 step 1 放置 5×`HIRE`、`BUY_ANIMAL COW 2`、`BUY_ANIMAL SHEEP 2`。这是按预设 bakery/非 bakery route 的开局分族，属于较强 route 假设。
- corrected `_NC2` 不再压缩上游列表，主要作用是保证 Kaggle 文件 loader 选到最终 wrapper、保留最终收到的 market 槽位并截断至 10；它是执行一致性修复，不是已证明策略增强。已有 8 场配对中 delta=0，不能声称 Nathan corrected 比父策略更强。
- 上游 `_v224_sales_first` 仍可能在 `_NC2` 之前删除/重排订单，因而末尾槽位保护不能恢复已改变的 index；若继续优化 Nathan，应先在上游 sales-first 记录原始槽位并做 barrier 内消融。

## 当前可比较指标（建议作为统一本地筛选门）

只看最终 margin 会把市场价格和 RNG 的公共变化混在一起。四模型应对同一 opponent/seed/seat 成对运行，并同时记录：

- **行为差异：** action hash、改变的 callback 比例、原始/最终前 10 market 槽位、SELL/BUY barrier、实际成交单位与价格；
- **经济账本：** 每 24/72 步窗口的现金差、销售收入、输入购买、HIRE/LAND/ANIMAL 支出、town 消耗前后库存；
- **物理结果：** 产量、死亡/失水/断供、服务成功率、shed overflow、终局可售库存；
- **稳健统计：** mean、median、5% 分位、最差局、胜率、seat 分层和 route/shop 分层；候选不能只靠平均值，至少要求 holdout 对手族最差分位不明显下降、无执行错误、所有订单索引变化可解释。

对 V45 opening 这类改变 shared RNG 的机制，新增三类对手族：`BUY-WHEAT` 第二槽、`SELL-THEN-BUY`、非 wheat 动态 opening。对同族与异族分别报告效果，不能混成一个“平均提升”。对 Nathan 的改进则优先使用不改 shared market index 的局部规则（连续 SELL block 内排序、保留 barrier 和空槽占位），并以实际成交账本确认收益。

## 结论

跨版本真正稳定的资产是 demand-aware route library 与可证书的供料/服务约束；V45 opening/race 和 Nathan Pipe-3 opening 都是基于对手/route 家族的条件策略，可能有效但不属于已证明的通用范式。后续“在高分模型上改进”应从 V43/V45 的稳定层保留开始，只引入一个能通过三类对手族 holdout 的小状态规则；若机制改变共享 market index 或 RNG，必须单独按 opening 家族评估，不能用单局录像或公开 route-tape 面板替代泛化验证。
