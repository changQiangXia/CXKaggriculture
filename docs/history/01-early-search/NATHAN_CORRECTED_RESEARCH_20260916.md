# Nathan corrected candidate 研究记录

研究对象：`nathan_cautious_corrected_candidate.tar.gz`，tar SHA-256 `c7d8ed1f5da2f047eeb3d9ae96eb3774a178647374d7cd16fb07425d7e3893f1`，解包源码 `corrected/main.py` SHA-256 `fe906789...e12052`。

## 先确认它到底改了什么

原线上 Nathan (`nathan_cautious_final/main.py`) 的末尾 wrapper 没有被 Kaggle 的 `get_last_callable` 选中，实际调用的是 `_NC_PARENT`。修正版重新插入导出边界，实际调用 `_NC2` wrapper；它保留原始 market list 槽位，只在超过 10 个订单时截断，不再删除零量订单。

这是一项运行一致性修复，不是策略改良。两个旧败局的 719 callback action 与 recorded tape 完全一致；v37/flex、9011/9014、双座共 8 场配对实验均为 delta=0。修正版目前没有可量化的策略收益证据。

## 线上败局的时间窗

从已有完整 replay 的现金窗口看，Nathan 的主要差距在中后段形成，而不是终局：

| episode | 对手 | margin@288 | @432 | @576 | @648 | final | 首个明显市场分叉 |
|---|---|---:|---:|---:|---:|---:|---|
| 109437616 | kobayasi | +726 | −620 | −5,900 | −6,305 | −5,381 | callback 298，Nathan SELL MILK 6，对手当步无市场单；随后销售节奏分叉 |
| 109518675 | Inzilbêth | +1 | −163 | −1,849 | −2,592 | −2,971 | callback 313，对手先 SELL MILK 6，Nathan 先 HIRE |
| 109502811 | Howon Kang | +1 | −155 | −539 | −1,512 | −2,665 | callback 316，对手先 SELL MILK 6 |
| 109516516 | NikolaiLeukhin | +1 | −255 | −673 | −1,514 | −2,296 | callback 313，双方订单槽位中 SELL MILK 位置不同 |
| 109491442 | nasubiman | +1 | −17 | −1,119 | −1,469 | −1,720 | callback 293，对手先 SELL WOOL 12 |

这些例子只能说明需要研究“销售时序与订单槽位竞争”，不能把对手某一回合的 SELL 直接搬进 Nathan。动作改变后，后续市场库存、随机数和生产路径都会变。

## 对代码结构的判断

Nathan 是固定 route/tape 加多层 market 修补的架构。当前需要重点审计三类交互：

1. `sell_lead` / `dead_stock` 与 town 每 4 步消耗、后续生产和取货之间的时序冲突；
2. `budget_guard` 在 72 步边界使用计划销售估计现金，未必等于实际成交，且可能受订单槽位竞争影响；
3. `room_guard` / 日末清仓按当前价格卖货，可能把下一周期的服务库存或生产输入提前卖掉。

固定 route 的购买、雇工、土地和动物扩张计划也可能与实时现金、库存偏差累积。对于 Nathan，先做“扩张成本—剩余回合回收”账本，比继续增加终局销售 wrapper 更有价值。

## 建议讨论的改进顺序

**方向 A：商品级、条件化的销售提前。**

不改变 route 和生产动作，只在满足以下条件时允许比原计划早一个销售窗口：库存已经真实存在；未来 5–8 步无同商品 PICKUP/BUY；当前价格显著高于商品基准；town 下一次消耗后仍满足服务；订单槽位不会挤掉 BUY_PRODUCT 或 HIRE。每次触发记录 action diff、实际成交量、成交价和下一次库存。先做 shadow telemetry，再做候选。

**方向 B：订单槽位保护。**

Nathan 的失败窗口经常是同一时段双方销售槽位不同。可以测试只对连续 SELL block 做商品排序，但必须保留非 SELL barrier，并验证实际成交和产量不变。不能删除零量订单，也不能仅凭名义 SELL 数量调整槽位。

**方向 C：扩张回本门槛。**

在新增 HIRE、LAND 或 ANIMAL 前估算剩余回合的可实现产出毛利，扣除 feed、seed、fertilizer 和必要服务成本；若无法覆盖边际成本和安全现金缓冲，则延迟扩张。该方向应优先针对 109437616 类大败局做机制复盘，再用未见 seed 和多种对手族验证。

当前建议优先 A 的可观测版本和 C 的账本版本，暂不修改线上包，也不提交新的 Nathan。只有当候选在同一对手/seed/seat 配对中同时满足 action 可解释、实际成交改善、生产路径未恶化、最差分位数不下降，才进入下一轮策略修改。

## 新发现：槽位保护并不完整

进一步追踪调用链发现，`_v224_sales_first` 在 `_NC2` 最终 wrapper 之前已经执行，并会先把空量订单删除、再把 SELL 向前移动。因而 corrected 的 `_NC2` 只能保护它收到的最终列表，无法恢复上游已经删除或重排的槽位。Nathan 的“修正版”仍可能改变同一 market index 上双方订单的配对关系。

这使“订单槽位保护”成为比单纯保留列表更具体的实验方向：需要单独做 `sales_first` 开/关消融，冻结非市场动作，逐步记录实际成交、订单 index、现金和生产路径。若关闭后在多个对手族不降，再考虑把 SELL 重排限制在没有 BUY/HIRE/LAND barrier 且不会改变有效订单 index 的连续区间；若只对镜像对手有效，则必须增加状态条件。

现有线上窗口研究属于原 Nathan 56257428 的回放。56270791（corrected）目前只有上传 receipt，没有可用线上回放，因此不能声称修正版已经线上验证。
