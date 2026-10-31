# 高分录像带研究·第 3 轮（2026-09-15）

本轮把两条 719-step 录像按原始挖掘脚本的窗口对齐（opening 0–23、day6 144–167、day12 288–311、day18 432–455、day24 576–599、day27 648–671、terminal 696–718），建立跨录像的 phase profile。完整明细见 [high_score_profile_features_20260915.json](/root/autodl-tmp/high_score_profile_features_20260915.json)。

## 跨录像数量画像

| 窗口 | Niklita SELL（订单/单位） | Kenjo SELL（订单/单位） | 共同观察 |
|---|---:|---:|---|
| opening | 8 / 8 | 8 / 8 | 两条完全相同，均为单件 WHEAT |
| day6 | 5 / 22 | 8 / 18 | 小批量 FERTILIZER、WOOL，订单数可变 |
| day12 | 8 / 44 | 7 / 44 | 商品集合基本相同，批量和顺序不同 |
| day18 | 17 / 160 | 7 / 57 | Niklita 更密集地拆单并集中 WHEAT/MILK |
| day24 | 12 / 156 | 11 / 70 | Niklita 有 MELON 12；Kenjo 没有该窗口 MELON SELL |
| day27 | 15 / 123 | 7 / 77 | 两者均混合 MILK、WOOL、FERTILIZER、作物 |
| terminal | 24 / 174 | 21 / 186 | 均大量 WHEAT；其余产品次序和数量不同 |

Niklita 的 day18/day24 总销售量明显更高，Kenjo 则在 terminal 保留更多 WHEAT（126 对 110）。这说明“高分”不是某个固定销售总量；销售应由当时库存、价格曲线、shop/town 消耗和下一步路线决定。两条录像 opening 一致但中后段仅 83/719 action dictionaries 完全相同，也不支持复制整条 tape。

## 可转移的阶段规则

**opening（step 0–23）**：保留已验证的移动/种植/浇水和单件 WHEAT 资金链。没有录像证据要求改变当前 V42 opening。

**formation/day6–day12**：以 FEED、CARE、COLLECT_FERTILIZER、WATER 和路线占用为主，销售多为小批量 FERTILIZER/WOOL/WHEAT。任何前移都必须先扣除 pickup reserve，并避免占用 BUY/HIRE 槽。

**productive scale/day18**：产出密度提高，录像间销售差异最大。只在父动作已经给出 SELL 时重排槽位；用逐单位 revenue 或 contested value 排序，保留原数量上限。全局同商品合并会抹掉该窗口的时序信号。

**demand conversion/day24**：出现 MILK、STRAWBERRY、MELON 等高价值商品。适合尝试 Boatlee 式一步 front-run：仅当下一步同商品 SELL>0、当前无 town/shop demand、shed 扣 reserve 后仍有余量且有槽位时前移；下一步必须偿还同等数量。

**harvest/day27**：HARVEST/CARE/WATER 仍在继续，销售产品集合多但批量不固定。保留未来 PICKUP、DROP 和路线承诺；价格信号低置信时不介入。

**terminal（step 718）**：父动作完成后重新投影 shed，若有空槽才追加未计划的可见 MILK/WOOL/CARROT/WHEAT 等 SELL，按逐单位收益排序。step 719 不可执行，不能把终局逻辑提前到 712 等更早节点。

## 建议的研究原型（不等于提交候选）

将录像启发拆成互斥开关，分别跑真实引擎 paired panel：

1. `slot_rank`: day 18–29 只在已有 SELL 槽内按 `_price`/`contested_value` 排序；
2. `premium_front_run`: day 24–29 一步前移，条件为 next-turn SELL、town demand=0、projected shed−pickup reserve−existing SELL>0、market slots<10；状态写入 due，下一 turn 由 `_repay` 扣回；
3. `terminal_frontier`: step 718 完整父动作后再算 projected shed，追加排序后的销售，最多填满剩余槽位。

所有开关必须共享以下拒绝条件：配置与引擎版本不匹配、actor/hands 数量不符、现金或 shed 容量不足、未来动作出现 BUY/HIRE/BUY_LAND barrier、目标数量为零、价格/库存字段缺失。拒绝时返回父动作并记录原因。

## 需要记录的验证指标

除平均 reward 外，记录 activation rate、每局新增/删除 SELL 单位、min margin、5% reward quantile、负局数量、两 seat 差异、对 v37/Flex/Thomas/Dmitrii 的分 opponent 结果，以及 callback 最大耗时。任何单窗口收益都不能越过四 opponent、多 seed 的门槛；本轮没有运行提交，也没有改变候选源码。

