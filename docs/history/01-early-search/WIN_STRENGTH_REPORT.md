# V37 胜局优势统计

本报告基于监控缓存中 282 个 V37 competitive win replay，使用关键 step 的双方公开 farm 状态和我方动作统计。它用于保护已验证的 V37 优势，不能单独证明新候选优于 V37。

## 稳定结构

- step 144：胜局中公开状态几乎固定为 COW=4、SHEEP=2、MELON=12、STRAWBERRY=4、WHEAT=3。
- step 216：COW 平均 7.54（中位数 8），SHEEP 平均 4.46（中位数 4），MELON 约 12，STRAWBERRY 约 20，WHEAT 约 5。
- step 288 以后：COW 与 SHEEP 生产线在所有胜局中持续存在；STRAWBERRY 和 WHEAT 生产量保持高位。
- step 648–696：终局前的 CARROT、STRAWBERRY、WHEAT 销售准备高度稳定；不要因为对手 WEED 多而关闭 input planner。
- 终局：282 个胜局全部有 COW 和 SHEEP；约 78% 有 GOOSE；只有 37 局进入 TOMATO=10 分支。这支持“番茄是条件项目”的设计。

## 动作闭环

按总调用次数排序，优势路线依赖 WATER、HARVEST、CARE、COLLECT_FERTILIZER、FEED、PLANT、PICKUP、PLACE 和受控 SELL 的完整闭环。单独增加销售或单独改变动物门控，都没有足够证据替代该闭环。

## 对硬编码的约束

1. 保留 V37 的主 route、quote-aware 销售排序、weed repair、容量检查、购买/拾取屏障、销售 debt 和终局 liquidation。
2. TOMATO、SHEEP、FERTILIZER 只能作为资金、容量、shop 资格和机会成本都满足时的有限项目。
3. route/profile 切换必须在公开状态节点一次性选择完整 profile；不能逐 action 拼接多个 V37。
4. 任何销售时序改动都要同时检查真实 shed、未来 SELL suffix、同品 PICKUP/BUY/PLACE/HIRE 义务和 72-step shop 边界。

## 当前候选结论

五回合预留候选在 V37 面板 22/22 胜，但跨对手仍有 Thomas −942；更早窗口也有 −2026。因此它继续作为研究候选，尚未达到零负差提交门槛。
