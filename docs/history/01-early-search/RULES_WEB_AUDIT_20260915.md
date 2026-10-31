# Kaggriculture 规则网页审计（2026-09-15）

审计对象：<https://www.kaggle.com/competitions/kaggriculture/overview>。本报告按三轮完成：官方文件/网页元数据核验、逐条规则与本地引擎交叉核对、对模型泛化与实验设计的影响审查。全程只读，没有提交或修改候选。

## 第 1 轮：官方网页与下载文件核验

Kaggle overview 页面是 JavaScript shell，HTML 本身只包含标题和简介；完整规则由 competition files 提供。通过当前可用的 Kaggle CLI 下载了官方 `README.md` 和 `AGENTS.md`：

```text
kaggle competitions files -c kaggriculture
README.md   26824 bytes
AGENTS.md   13708 bytes
```

官方文件与工作区副本的 SHA-256 完全相同：

| 文件 | 官方下载 hash | 本地 hash | 结论 |
|---|---|---|---|
| README.md | `3081e52baf8e…c4ade00` | 相同 | 本地规则正文未过时 |
| AGENTS.md | `e1a80501a7b0…8fe22` | 相同 | 本地 CLI/提交说明未过时 |

对应本地文件：

- [Kaggriculture_README.md](/root/autodl-tmp/Kaggriculture_README.md)
- [Kaggriculture_AGENTS.md](/root/autodl-tmp/Kaggriculture_AGENTS.md)
- [kaggriculture/README.md](/root/autodl-tmp/kaggriculture/README.md)
- [kaggriculture/AGENTS.md](/root/autodl-tmp/kaggriculture/AGENTS.md)

通过 Kaggle CompetitionService 查询到的当前网页元数据：

- competition id：147734
- 开放时间：2026-07-30 16:15:52 UTC
- 截止时间：2026-09-30 23:59:00 UTC
- simulation：true
- file-based submissions：true
- evaluation：环境型 metric，最大化（`isMax=true`）
- 每日最多提交：5
- 页面记录的已计分提交数：2
- 最大队伍：5
- 当前队伍数：9119，参赛者数：9864
- 每队 submission archive 限制：20,480 MB
- rulesRequired：true
- 需要身份验证：true
- team merger / 新参赛者截止：2026-09-23 23:59 UTC
- kernel publishing disabled deadline：2026-09-23 23:59 UTC

这些是查询时的竞赛状态，不把动态队伍数、排名或 submission 次数当成游戏规则常数。原始查询保存于 [rules_web_metadata_20260915.json](/root/autodl-tmp/rules_web_metadata_20260915.json)。

本轮结论：网页当前可访问的官方规则文件与本地研究基线一致，没有发现“本地 README 已经过时”的证据。网页公开简介只说“最大化 farming income”，不能代替 README 的逐条机制。

本机实际加载的 Kaggriculture engine 文件 hash 也已记录（用于复现实验环境）：`kaggriculture.py` = `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`，`kaggriculture.json` = `a82c89c1a2315b93f39775d8e025471a01b738647c9772658368ee6b1b6f4867`。`episodeSteps=720` 的实测 callback 为 719 次（step 0..718）。

## 第 2 轮：规则与引擎语义交叉核对

### 时间和动作边界

- 默认 30 天 × 每天 24 turns = 720 steps。
- agent 在 0-indexed step 上返回动作；720 步结束后给出 `DONE`/final reward。
- 在当前本地 `kaggle-environments` 实测中，`episodeSteps=720` 产生 719 次 agent callback，观测 step 为 0..718，随后 engine 结束并给出最终状态；因此 terminal wrapper 的最后可执行回调是 step 718，不能自行追加 step 719。
- 每个 farmer/hand 每 turn 一个物理动作；market 是每玩家最多 10 个有序订单，超出部分静默丢弃。
- 两个玩家的物理动作同时记录；随后按双方有序队列逐单位处理 market orders，再处理 town 消耗，最后做 day refresh、market refresh、income update 和 farm update。
- `step 719` 不是一个额外的可用普通 turn。任何 terminal wrapper 必须尊重实际 episode length 和 engine 的最后一个回调。

### 可见性和信息边界

observation 可见：

- 双方 farm tiles、farmer/hands 位置、unlocked quadrants、hires_today；
- 共享 market inventory/prices；
- town.unlocked_shops（重复 shop 名称表示独立实例）。

只有自己可见：

- shed；
- seeds；
- farmer/hand inventories。

因此可以根据公开 farm 和共享市场估计对手的生产压力，但不能读取对手 shed、inventory、未来 SELL 或隐藏路线。任何从 replay 得到的对手未来动作只属于离线诊断，不能在提交 agent 中当作实时可见信息。

### 物理、容量和照料约束

- locked quadrant 可以通行；普通 tile action 在 locked tile 上是 no-op。shed 的四个中心邻接格即便属于 locked quadrant 也可执行 PICKUP/PLACE/DROP。
- shed 非 seed 容量默认 100；end-of-day drop 和 mid-day PLACE 都受容量限制，溢出直接丢失。seeds 独立存储，不占容量，也不能用 PICKUP 取出。
- 植物连续两次 end-of-day 未浇水会变 weed；新种植当天 `consecutive_unwatered=1`，当天不浇水可以当晚直接失效。
- 文本同时使用“每天浇水”和“至少每隔一天”两种表述：前者是获得每日 watering/yield bonus 的最优照料要求，后者是生存下限（连续两次 end-of-day 未浇水才变 weed）。模型评估必须分开记录 survival 与 yield，不能把隔日浇水误当成无损等价于每日浇水。
- 动物连续两次未 feed 会逃逸；新放置动物的首日 `consecutive_unfed=0`。
- CARE 的 bonus 只有在当天 fed 且下一次 scheduled production 时兑现；生产日未 fed 会产生 base 1，但清空已存 bonus。
- animal `max_held` 是 tile 上未收获产物上限，不是 lifetime 产量上限。
- market sell 是逐单位、双方并发、有序的共享状态更新。premium 商品在供给过量时可能快速到 $1 floor；shop 是公共市场排水，不是直接指定买家。
- town shops 每 3 天随机 with replacement 解锁，最多 8 个实例；town center 每 24 turns 消耗每种非 fertilizer 产品 1 单位，shop 每 4 turns 独立消耗需求，单品 shop 2×。
- win/reward 只按季末 bank coins；未卖出 shed/inventory 商品不计入最终 reward。

### 与现有本地研究的差异核对

已有 [RULES_RESEARCH_ROUND1_20260915.md](/root/autodl-tmp/RULES_RESEARCH_ROUND1_20260915.md)、[RULES_RESEARCH_ROUND2_20260915.md](/root/autodl-tmp/RULES_RESEARCH_ROUND2_20260915.md)、[RULES_RESEARCH_ROUND3_20260915.md](/root/autodl-tmp/RULES_RESEARCH_ROUND3_20260915.md) 覆盖了上述核心语义。官方文件 hash 一致，未发现需要撤销的结论。

需要保持谨慎的地方：

1. README 的 turn-processing order 规定了 market/town/day refresh/income/farm update 的先后；只看最终 replay 无法可靠重建中间顺序。
2. “动作合法”不等于“动作生效”：无效 action 和超出 market order 上限通常是 silent no-op，必须记录状态变化和有效订单数。
3. `seed=null` 是配置默认值，研究 panel 必须显式固定 seed；否则 shop unlock、weed spawn 和市场随机流不能做 paired 对照。
4. README 允许 episode configuration 改 marketParams 等旋钮；线上 submission 使用默认配置，不能把本地自定义参数实验结果当成线上证据。
5. 页面上的当前 public score、rank、队伍数和 submission 次数是动态状态，不是可复现实验规则。

## 第 3 轮：对模型泛化和 log 修改的直接约束

### 1. 从 log 学“状态范式”，不能学固定 tape

线上 log 只能作为假设发现资料。允许提取：

- day/step 阶段；
- 可见 price、market inventory、shop pressure；
- 自己的 shed/carried、未来自家 route barrier、订单槽；
- 对手公开 farm 的生产压力；
- 当前动作后 24–72 steps 的现金、库存和容量变化。

不能直接编码：

- 某个 episode 的固定 step；
- 某个选手的未来 SELL 顺序；
- 对手隐藏 shed/inventory；
- 只因一次 loss 就做全局商品禁售或全局 SELL merge。

任何 log-derived 修改必须在真实 engine 中做单动作/单 SELL block 反事实，再经过未见 seed、双 seat、多个公开对手族和状态扰动。

### 2. 必须验证的泛化切分

- discovery：线上 loss replay 与近期公开高分 agent，仅提出机制；
- development：旧 V37/Flex/Thomas/Dmitrii 加一部分公开 router；
- holdout：未参与发现的公开 agent、未见 seed、另一 seat；
- stress：改变 market inventory、town shop 组合、对手公开产出压力和 SELL 顺序。

候选只有在未触发条件时与 parent action 完全等价、触发时跨策略族方向一致、且 72-step 长时域不破坏 pickup/容量/sale debt/terminal liquidation，才可称为泛化。

### 3. 当前 benchmark 不能只看平均终局分

规则决定 reward 只看最终 bank，因此本地报告除了 mean margin，必须包含：

- DONE/720、stderr、timeout；
- 有效 action 与 market order 数；
- negative games、min margin、5% quantile、CVaR；
- 两个 seat 与 opponent family 分层；
- activation/rejection/fallback 原因；
- shed overflow、未偿还 sale debt、未来 72-step cash/inventory 影响。

### 4. 对当前候选研究的影响

- `slot_rank` 只能在同一连续 SELL block、数量不变、无 PICKUP/BUY/HIRE/PLACE barrier 时尝试，并保留 parent fallback。
- `premium front-run` 必须使用当时可见的 market/town/shed/future 自家 route，不得假设对手 future tape。
- `terminal` 逻辑只能在 engine 真实最后阶段触发，不能把 step 719 当额外动作；补单前要重新投影 shed、market slots 和 capacity。
- 任何候选若在当前 V42 parent 上 activation=0，只能说明对象不匹配，不能当成机制无效。
- 由于提交是 simulation/file-based、每日最多 5 次且存在两个 active agent 约束，提交前必须先完成完整本地 paired/holdout 审查；本报告不触发提交。

## 审计结论

截至 2026-09-15，给定 Kaggle overview 对应的官方 README/AGENTS 已经下载核对，和本地副本逐字 hash 一致。我们对 720 turns、市场逐单位并发、town 随机消耗、private/public observation、shed/animal/plant 物理约束、环境型最大化 reward 和 file-based submission 流程有足够细的规则理解。

真正仍需持续验证的是策略的泛化，不是规则文本来源：log-derived 改动必须通过状态契约、父动作等价、未见对手/seed、状态扰动和长时域反事实；任何线上提交仍需用户明确授权。
