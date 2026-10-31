# Kaggriculture 规则研究·第 2 轮：市场、价格和 town 消耗

市场销售按双方有序队列逐单位并发处理：同一回合双方同时卖同商品时，每个单位先按当前价格成交，再把卖出的单位加入 inventory，影响后续单位价格。$1 price floor 下仍成交但不继续增加 inventory。BUY_PRODUCT 只允许 WHEAT/FERTILIZER，且买价按 post-buy inventory 报价；立即 buy→sell 在不变市场下净值为零。

价格不是固定 base：以 I0=10000、资源独立 T 和两侧 shape/target 计算。供给超过 I0 后 premium 商品（STRAWBERRY、MELON、MILK、WOOL）会快速跌到 $1；短缺侧和过量侧的曲线可以完全不同。不能用 headline base price 代替当前逐单位 quote，也不能把不同资源的价格斜率混在一起。

Town center 每天消耗每种非 fertilizer 产品 1 单位；shops 每 3 天随机 with replacement 解锁，最多 8 个实例，每个实例每 4 turns 消耗其需求，单品店为 2×。shop 是公共市场排水，不是直接指定买家；重复店实例会线性增加需求。

因此销售策略必须联合考虑：当前 market inventory/prices、公开 shop demand、未来自家 production、shed/pickup、对手公开 production 压力和剩余 season horizon。全局 SELL merge 或看到 shop 就倾销，均违反价格曲线和队列机制的实际结构。
