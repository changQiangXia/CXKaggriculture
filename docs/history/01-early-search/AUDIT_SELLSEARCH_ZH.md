# Q25-SellSearch 独立审计

审计对象是 [candidate_v45_q25_sellsearch_v2.py](/root/autodl-tmp/q25_search_20260917_055120UTC/candidate_v45_q25_sellsearch_v2.py)，源文件 SHA-256 为 `bcf664c9a60f9ae8753302c84c09dc1622b680f500cafe6a6924078a8ec66e19`。审计也回看了 v1、官方 `kaggriculture.py` 的 `_process_market`，以及独立实现 [sell_sim.py](/root/autodl-tmp/q25_search_20260917_055120UTC/search/sell_sim.py)。审计没有修改候选源码。

## 结论

v2 的官方市场语义已经修正，四个 SELL 槽以内的搜索运行开销在当前测试上可接受，且不会跨 BUY/HIRE/BUY_LAND 屏障、不改变数量或工人动作。它可以作为**本地实验候选**继续测，但目前不能作为“已证明泛化”的提交候选，也不能依据有限压力面把它解释为鲁棒收益。

有两个边界必须保留在最终报告中：

1. v1 的真实对局结果不能证明 v1 搜索正确。v1 的 `_q25ss_sim` 使用两边独立 cursor，一边的当前订单结束后就进入下一订单；官方引擎按订单索引锁步，必须等双方当前索引的订单都结束后才进入下一个索引。v1 在满库存的合法例子上已经出现差异：自己的 `[SELL WHEAT 3, SELL CARROT 1]`、对手 `[SELL WHEAT 1, SELL CARROT 3]`、每项库存充足时，v1 模拟收入为 106，官方语义为 108。v1 的 `sellsearch_pilot`、`sellsearch_holdout` 只能保留为“旧实现完整对局观测”，不能作为搜索推演验证。
2. v2 只在少量 SELL 对手情景上选序。对手 BUY_PRODUCT、空槽、不同数量的多批 SELL、超过 24 单位的批量，以及真实对手私有库存均没有进入 oracle。因此 `best_key` 非负只表示这些情景下的非劣，不表示实际对局非劣。

## 1. `_q25ss_sim` 与官方引擎的一致性

v2 的循环外层是 `index in range(max(len(own_orders), len(rival_orders)))`，每个索引内先为双方当前单位报价，再按玩家顺序提交。这与官方 `_process_market` 的关键规则一致：

- 报价在双方提交之前完成，玩家 0 的提交不会改变玩家 1 同一单位的报价；
- SELL 成功后只有价格大于 1 才增加共享市场库存；
- 一方当前订单结束后保持空闲，另一方继续处理同一订单索引；
- 进入下一个订单索引前，当前索引双方的剩余数量都已经结束。

在 [test_candidate_sim.py](/root/autodl-tmp/q25_search_20260917_055120UTC/search/test_candidate_sim.py) 中执行了 500 组随机官方引擎差分和上述满库存跨槽回归，结果为：

```
candidate_v45_q25_sellsearch_v2.py: actual runtime oracle passed
500 official engine differential cases + slot regression
```

独立的 `sell_sim.py` 也有自己的 500 组差分测试；这证明独立模拟器和 v2 内嵌 oracle 各自经过测试，但不能把 v1 的结果倒推为正确。引擎本身的价格参数在 v2 中从 `_R37_MARKET_PARAMS` 复制，并合并 observation 中的 `market.params`，常规配置下与当前引擎价格公式一致。

仍有一个适用范围：v2 oracle 只接受产品 SELL。候选的入口门控确保整张 `market` 列表是纯 SELL 且第一个槽是 SELL；若形状异常，外层异常处理会退回父动作。它没有尝试模拟 BUY_PRODUCT、BUY_SEED、BUY_ANIMAL 或原子 HIRE/BUY_LAND，这是有意的安全边界，不是完整市场模拟器。

## 2. 门控与状态不变量

`_q25ss_reorder` 的主要门控如下：

- `market` 少于两个订单、首单不是 SELL、或列表含任何非 SELL 时直接返回父动作；
- 含有未知产品、非正数量或无法解析的订单时不进入搜索；
- 订单数大于 4 时 v2 直接 abstain；
- `_r127_fields` 先应用当前工人动作，再读取自己的 shed；
- 所有被搜索订单的总数量超过该产品当前 shed 时 abstain；
- 返回值只重排订单列表，保留每笔订单的产品和数量，未增删市场订单，也未改变 farmer/hands。

这些门控保住了最重要的物理不变量：在纯 SELL 块中候选与父动作消耗相同的自有库存，且不把未来尚未获得的货物当成可卖库存。`_q25ss_stock` 的前序订单参数目前固定为 0，因为只有“初始纯 SELL 块”才会进入门控；因此它不会误把 BUY 的未来到货算进块内库存。

v2 还在重排后同步 `_RACE_STATE[player]['prev_action']`。这是必要的，因为后续 race 检测要知道真正提交的动作；v1 漏掉这一同步，会让内部上一动作与实际动作不一致。step 0 重置搜索 telemetry，避免同一进程多局累加。

配置检查仍然只显式检查 board size、turns per day、shed capacity、订单上限和 farm-hand multiplier，没有把 `episodeSteps`、`marketParams` 及其它 town 配置作为门控条件。标准比赛配置下没有问题；若将候选用于非标准配置，搜索行为不能自动视为已验证。

## 3. 候选生成和选择逻辑

v2 在最多四个订单上使用 beam 宽度 48。四个互异订单的全排列只有 24 个，所以在最常见的四槽情况 beam 足以保留所有不同排列；同一产品的多笔订单则强制保持它们的父顺序，减少重复状态，但这会排除“交换同产品不同数量批次”的排列。后面补的 `reverse` arm 只加入一个反转结果，不能恢复全部被排除的排列。

前缀 beam 的评分调用完整的 `_q25ss_sim`，但它按当前前缀的订单长度与对手完整情景做索引对齐。前缀分数只是搜索启发式，和最终完整排列的边际价值不具有单调性；因此 beam 可能剪掉最终更好的排列。四槽时多数情况下问题较小，但这不是全局最优保证。

情景面包含：空对手、按自己可见产品顺序的对手 SELL、逆序 SELL，以及每个不同产品的单品 SELL。每笔对手订单最多 24 单位；重复产品会在“可见顺序”情景中重复生成同产品订单。这些情景用于保守筛选有实际意义，但不是从公开录像推断出的真实对手计划，也没有包含订单索引上的空洞或 BUY_PRODUCT 对市场库存的影响。

因此 `best_key[0] >= -1` 和平均压力收益至少 5 只能解释为“在这组人工压力情景下没有明显下降且平均模拟增益达到阈值”。它不应写成“所有对手下不降”或“在线提升已被本地证明”。

为量化这一限制，我用同一 v2 选择逻辑随机生成了满库存块，然后用官方锁步 `sell_sim` 加入 60 或 100 单位的多批对手 SELL。可得到明确反例：

```
父块:   CARROT60, CARROT60, STRAWBERRY24, TOMATO3
面板选: CARROT60, STRAWBERRY24, CARROT60, TOMATO3
压力:   STRAWBERRY100, TOMATO100, CARROT24
候选 - 父收入: -54
```

另一个块 `MILK60, MILK1, TOMATO24, WHEAT10` 在面板上选择移动 TOMATO，面对 `TOMATO60, MILK24, WHEAT100` 时低 33。它们不是当前真实对局的因果证据，只是证明有限情景存在外推风险，必须在报告中披露。

## 4. 运行时

此前 v1 允许最多 10 个槽，满库存 10 槽的纯搜索单次约 3.77 秒，明显不适合 1 秒 actTimeout；v2 已收紧到最多四个槽。使用同一 Python 进程、同一 oracle 的测量结果如下：

| 情形 | 槽数/总单位 | `_q25ss_reorder` 中位耗时 |
|---|---:|---:|
| 常见重复 SELL | 3 / 28 | 7.0 ms |
| 常见重复 SELL | 4 / 29 | 30.5 ms |
| 满容量边界 | 4 / 100 | 87.5 ms |
| 对照：5 槽 | 5 / 100 | 477 ms |
| 对照：6 槽 | 6 / 96 | 870 ms |

四槽上界测量没有包含父模型的完整动作计算和 Python 首次加载，因此不能把 87.5 ms 当作正式 actTimeout 保证。实际 v2 pilot 的完整 action 记录最大约 0.340 秒、40 行均健康；这说明当前测试面有余量，但仍需在候选状态极端化和冷启动路径上留意。`search/audit_runtime_v2.json` 保存了上述原始计时。

## 5. 对 v2 实验结果的解释

`sellsearch_v2_pilot_9060_9063.json` 的 40 个完整 paired 行全部健康，摘要为 candidate 22 胜、parent 20 胜，point delta 点估计 0.05，bootstrap 区间 `[0.00, 0.15]`；现金差点估计约 152.35。这个 pilot 与 v1 使用相同开发 seed 面板，且对手 V46、Pipe8 等存在同源关系，只能作为运行和方向信号，不能作为独立确认。当前尚无 v2 的未见 seed holdout 结果，因此不能据此晋级或提交。

## 最终建议

当前 v2 的适当标签是“修复了市场 oracle 的本地实验候选”。可以继续在预注册的未见 seed、分组后的独立对手族和包含大批量 SELL/BUY 行为的对照面板上测试；如果这些测试失败，应退回 Q25 父模型。即使 holdout 通过，也应把该机制描述为受限的重复 SELL 重排启发式，并把上述大批量压力反例作为泛化风险，不能把 v2 直接作为已获准提交物。当前没有提交授权。
