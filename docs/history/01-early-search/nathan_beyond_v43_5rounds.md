# Nathan Jacob《Beyond V43: What the Top Clusters Do on Turn 1》五轮研究

研究日期：2026-09-15 UTC  
公开笔记本：[Beyond V43: What the Top Clusters Do on Turn 1](https://www.kaggle.com/code/nathanjacob/beyond-v43-what-the-top-clusters-do-on-turn-1)  
作者：Nathan Jacob（Kaggle 用户 `nathanjacob`）  
本地抓取文件：`/tmp/nathan_nb/beyond-v43-what-the-top-clusters-do-on-turn-1.ipynb`；解码源码：`/tmp/nathan_nb/decoded_main.py`。

本报告将作者的文字说明、嵌入源码和本地 Kaggriculture engine 检查分成五轮。所有结论都区分“作者声称的结果”和“本地可以复核的事实”；没有使用该笔记本进行提交。

## 第一轮：作者意图、问题定义和证据边界

### 作者在笔记本中明确表达的想法

开头 TL;DR 是“Fork this, submit, get a top agent”，但作者真正想解释的是：用策略聚类找到一个在第一回合的优化，并声称该优化对 V43 相对 V42 的胜率从 75% 提高到 96%。作者把问题定义成“顶尖队伍在开局 144 个 action 上有什么行为差异”，而不是重新训练一个机器学习模型。

作者的思路链条是：

1. 下载 leaderboard 前 50 队伍的 replay；
2. 用每局前 144 个 action 组成策略指纹；
3. 以 90% 相似度阈值用 Union-Find 合并策略；
4. 在不同 cluster 的胜负局里寻找第一处 action 分歧；
5. 把分歧改成一条很小的规则，再用 200 局 colosseum 做发布门槛。

作者强调 agent 是 self-contained、无数据集、无网络、无 GPU。笔记本 metadata 也确实显示 `dataset_sources=[]`、`kernel_sources=[]`、`enable_gpu=false`、`enable_internet=false`；代码通过 base85+gzip 将完整 `main.py` 嵌入 notebook。

### 可复核事实与边界

- Kaggle 页面返回 `datePublished/dateModified=2026-09-15T07:12:17.73Z`，公开 notebook 可被 `kaggle kernels pull` 下载。
- notebook 有 13 个 cell，其中只有 markdown 说明、源码解码/打包代码；没有把用于聚类的 replay、前 50 队伍名单、逐局结果表或统计检验代码作为输入文件提供。
- 解码源码 SHA-256 为 `7a37397fdb29cbbb17aaf7577352bef910fb4dd0f19bf763b9dcaff68595da54`，与 notebook `EXPECTED_SHA256` 一致，源码 3373 行、322038 字节。
- 因此 cluster 数量、胜负局数量和 p 值是作者报告的实验记录，当前 notebook 本身不能独立重建；可重建的是最终 agent 和其开局逻辑。

### 第一轮判断

作者的核心贡献是一个可解释的“先找群体行为，再做窄改动”的研究流程。证据链的薄弱点是 replay 原始材料不在 notebook 中，且“下载 top 50”与 Kaggle 公开权限/历史版本必须另行核对；不能把 markdown 表格当成已独立复现的统计结果。

## 第二轮：策略聚类和作者对高分行为的解释

### 作者声称的策略地形

作者称 263 个队伍被压缩成 33 个 cluster：

- C0：1 队，平均 Elo 3215，代表 Majkel1337，相似度 40%；
- C1：1 队，Elo 3024，代表 ymg_aq，相似度 50%；
- C2：1 队，Elo 3008，代表 SpaTaro，相似度 42%；
- C4：1 队，Elo 2991，代表 Otter Vibe，相似度 54%；
- C9：5 队，平均 Elo 2931，代表“AI是我的豆包”，与作者策略相似度 84%；
- C15：212 队，平均 Elo 2881，代表 v40 megacluster。

作者的解释是：C15 占 top 50 的 81%，基本都是 Ahmed v40 lineage；真正值得研究的不是最大 cluster，而是与自己有 84% 相似、却持续赢的 C9。差异的 16% 被作者称为潜在 edge。

### 方法上的价值

用前 144 step 做指纹有三个优点：

- 关注启动资本、雇工、动物和首批作物这些能形成复利差异的状态；
- 相似度比单个动作更稳健，能发现策略族而非只看一个 tape；
- Union-Find 使策略簇可视化，便于从 cluster 间的胜负边缘找候选机制。

### 方法上的风险

- 90% 阈值是人工选择；相似度定义、动作规范化和对称座位处理没有在 notebook 中展示。
- 144 step 只覆盖前六天，可能把中后期生产/市场策略误归因于开局。
- cluster 平均 Elo 与“打赢某个 cluster”不是同一统计目标；不同 seed、seat、对手池组成会改变 Elo rate。
- 单个代表队伍不能代表 cluster 内所有 policy。作者自己也承认 top 8 是 singleton，说明“聚类收敛”不等于接近最优。

### 第二轮判断

作者真正的思想不是复制 C9 的 tape，而是把 C9 提炼成一个可检验机制：“在相同路线下，减少低收益的第一回合交易，提前启动生产”。这符合状态范式学习，但 cluster 结果仍需要跨时间、seed、seat 和新鲜公开对手做 holdout。

## 第三轮：Turn-1 机制与 pipe-4 的具体实现

### 作者描述的行为差异

作者给出的 C15（V40–V43 lineage）开局是：

```text
Step 0 market: [BUY_PRODUCT WHEAT 5, BUY_PRODUCT WHEAT 10, SELL WHEAT 60]
```

作者把它称作 wheat flip：低价买 15 wheat、卖出 60 wheat，约产生 900 美元 bridge cash，但占用三个 market order slot，并把雇工/买动物推迟一个 turn。

C9 开局是：

```text
Step 0 market: [BUY_PRODUCT WHEAT 5]
Step 1 market: [HIRE ×5, BUY_ANIMAL COW 2, BUY_ANIMAL SHEEP 2]
```

作者的经济解释是，在 720-step 的复利游戏中，提前一回合启动工人和动物的长期产出，价值可能超过 900 bridge cash。作者保留一个条件例外：BAKERY 路线需要 wheat 做面包，因此继续 wheat flip；其余路线采用 minimal wheat + early hiring。

### 源码核对

解码源码中确实存在如下常量：

```python
_PIPE3_BAKERY_ROUTES = {101,103,104,105,106,107,108,109,111,119,120}
_PIPE3_MINIMAL = [['BUY_PRODUCT','WHEAT',5]]
_PIPE3_WHEAT = [['BUY_PRODUCT','WHEAT',5],['BUY_PRODUCT','WHEAT',10],['SELL','WHEAT',60]]
_PIPE3_STEP2_MIN = [['HIRE']*5, ['BUY_ANIMAL','COW',2], ['BUY_ANIMAL','SHEEP',2]]
```

实际代码以 41 个 route 为基础；这 11 个 bakery route 保留 wheat flip，其他 route 的 route[0] 改为单个 `BUY_PRODUCT WHEAT 5`，route[1] 改为五次 HIRE 加两种动物购买。源码哈希和 notebook 期望值一致，说明该开局改动没有在下载过程中被替换。

### 重要的实现细节

- 路由选择在 step >= 144 根据前两个 `town.unlocked_shops` 选择 route；step >= 648 强制 route 2 做终局。
- 基础 chassis 仍包含 hand alignment、weed repair、sell lead；`budget_guard`、`room_guard`、`clamp_sells`、`dead_stock`、`terminal_liquidation`、`front_run` 在 `_SETTINGS` 中关闭，但后续 wrapper 又加入终局规划和 day-end room guard。
- 终局 step 712–718 运行 shadow simulation 和 bounded planner，只有在“实际交付增加、无 overflow、所有原 worker deposit 前缀保持支配、SELL 单位不负增”时才接受改动；失败则回退 parent。
- 源码内嵌的是 1.32.7 的 unit/decay 语义摘录，且明确说明未包含完整 market RNG/interpreter；这不是一个独立的完整 engine。

### 第三轮判断

Turn-1 改动是窄而清晰的机制实验，不是重新设计整个 agent。它依赖 route ID 与 shop-route 映射正确；如果 route 表过时、shop 顺序变化或 bakery 集合不再适用，条件开局就可能失配。尤其是“Step 1 同时 HIRE×5 + 买 2 cow + 买 2 sheep”对 cash、market order 并发和路线位置有强假设，需要在当前 engine 上逐 route 检查。

## 第四轮：完整代码审计、作者思想与运行安全

### 作者的工程取舍

作者把 V43 描述成三个正交升级层：

1. shed overflow recovery：在第 23 小时提前卖掉 dawn overflow 的货；
2. atomic planting fix：种子不足时只取消超额种植，而不是取消全部 planting command；
3. route proposal planner：终局优化 worker routing。

pipe-4 只改开局 11 行，其余约 3367 行保持 V43 chassis。作者认为这样可以把 C9 opening 与 V43 reactive layers “stack cleanly”，降低改动面和回归风险。作者还公开承认剩余差距：C9 在 day 9–11 买约 3 倍 cow（58 局统计 53 对 18），这不是 11 行开局替换能覆盖的深层 tape 差异。

### 本地静态审计

- `agent(observation, configuration)` 入口存在，源码可编译并可加载。
- action shape 由 chassis 生成；market 订单有显式最多 10 单的约束，终局 liquidation 也检查 order cap。
- 代码读取公开 observation、自己的 farm/private、town shops 和 market；没有发现读取对手 private shed/inventory 的路径。
- planner 只在固定 712–718 窗口工作，并设置 physical-state mismatch、非连续 callback、未知 action、day boundary、order cap 等 abstain/fallback 条件。
- 终局 planner 使用内嵌 unit model 做 shadow simulation；作者已在注释中承认 market price dynamics 不在该模型内，因此其 certificate 只能证明物理库存/交付支配，不能证明真实价格下的全局最优。
- 最终公开 `agent.telemetry` 在本地加载后是 `{}`。内部 `_UPGRADE_STATS`、`_ROOM_STATS` 存在，但最终入口把 telemetry 指向 `_ROOM_STATS`，而终局 planner 计数未暴露。这不影响 action 执行，却削弱线上 activation/abort 可观测性。

### 本地 engine smoke

使用本机 `kaggle_environments 1.25.9`、`debug=False`、`episodeSteps=720` 对 `pass` 运行解码 agent：

| seed | agent seat | 完成状态 | steps | reward |
|---:|---:|---|---:|---:|
| 9001 | 0 | DONE/DONE | 720 | 98,668 |
| 9001 | 1 | DONE/DONE | 720 | 98,668 |
| 9002 | 0 | DONE/DONE | 720 | 166,823 |
| 9002 | 1 | DONE/DONE | 720 | 166,823 |

这证明当前本地 runner 可以执行完整 720 step，未观察到异常；它没有复现作者 200 局 colosseum，也不能由此推出胜率提升。

### 第四轮判断

工程上这是“成熟 parent + 小开局 patch + 多重终局 guard”的保守路线。主要安全风险不是非法 action，而是静态路线知识的过时、终局 planner 对 market 的简化，以及 telemetry 不足导致无法知道改动是否真的被激活。作者的公开自省（剩余差距来自 day 9–11 cows、top singletons 需要创新）比“96%”标题更值得作为后续研究假设。

## 第五轮：实验结果、统计解释、泛化和可借鉴结论

### 作者报告的 colosseum 结果

作者称每个 matchup 运行 200 局（100 局 player 0、100 局 player 1），使用 `kaggle_environments.make('kaggriculture')`、无 debug/config 覆盖，并进行了 binomial test：

| 对手 | W-L-T | Elo rate | Cohen's h | p-value |
|---|---:|---:|---:|---:|
| pipe-3（V42 base + C9 opening） | 148-25-27 | 80.8% | +0.662 | 0.000 |
| V43 raw | 193-7-0 | 96.5% | +1.194 | 0.000 |
| V42 | 192-8-0 | 96.0% | +1.168 | 0.000 |
| V41 | 193-7-0 | 96.5% | +1.194 | 0.000 |
| pipe-1 | 172-28-0 | 86.0% | +0.804 | 0.000 |

作者另报 V43 raw vs V42 为 122-20-58，Elo rate 75.5%，Cohen's h +0.535。其 release gate 是“>96% elo rate”。

### 如何正确解读

- 这些是作者在固定对手和固定 200 局面板上的效果量；“p=0.000”应理解为打印精度造成的极小值，而不是概率真正等于 0。
- pipe-4 对 raw V43 的 96.5% 是相对于作者所选 V43 版本的 paired H2H，不等同于 Kaggle leaderboard private score 提升。
- 对手池包含同一 lineage 的 V41/V42/V43，存在 parent 相似性；不能代表公开新 agent、未来策略族或线上环境漂移。
- 200 局若有大量 ties，Elo rate 的有效信息少于 200 个独立胜负；还应给出按 seed/seat/route 分层的置信区间、负局数、最差分位数和 leave-one-opponent-out 结果。
- notebook 没有提供 raw game logs、seed 清单、route coverage、opening activation count 或价格轨迹，因此无法独立检查“81% C15”“58 局 C9 胜局”“53 vs 18 cows”等统计。

### 泛化实验应该怎样补

将作者的机制转化为可提交候选前，至少补四个层次：

1. **发现集**：保留作者声称的 C9/C15 证据，但只用于提出假设；
2. **开发集**：按 seed、seat、opponent family 分层，比较 wheat flip、minimal wheat、bakery conditional 三个消融；
3. **确认集**：leave-one-opponent-out、leave-one-time-block-out、未见 seed、双 seat，记录平均 delta、5% quantile、负局和 seat variance；
4. **最终 holdout**：使用最近公开高表现 agent，冻结源码和 route map 后只运行一次。

特别要检查：非 bakery route 的 step 1 是否真的能同时完成 5 hires + 2 cow + 2 sheep；初始 cash 不足或 shops/route 映射变化时是否出现 silent no-op；WHEAT 生产/面包路线是否被错误切换；day 9–11 cow preference 是否需要独立机制；开局收益是否被后续 shed capacity、feed、watering 和 terminal liquidation 抵消。

### 第五轮结论与可迁移启发

1. **可迁移范式**：从高分行为中提取状态机制，做最小、条件化、可回退的改动；不要复制整个 tape。
2. **经济学启发**：在强复利环境里，应比较“立即 bridge cash”和“提前一个 turn 的生产启动价值”，而不是只看单回合现金。
3. **条件化很重要**：BAKERY 依赖 wheat，不能把 minimal wheat 无条件推广到所有 route。
4. **证据门槛要更高**：作者的 96% 是有价值的假设生成证据，但在我们当前冻结 no-R128 parent 上必须重新验证；尤其不能把高度相似 parent 的 H2H 当作线上提升。
5. **作者自己的剩余差距提示下一步**：day 9–11 的 cow preference 和 singleton cluster 行为可能比 Turn-1 patch 更有价值，但也更容易过拟合，必须先建立跨策略族 holdout。

## 资料清单

- Kaggle notebook（公开）：https://www.kaggle.com/code/nathanjacob/beyond-v43-what-the-top-clusters-do-on-turn-1
- 本地原始 notebook：`/tmp/nathan_nb/beyond-v43-what-the-top-clusters-do-on-turn-1.ipynb`
- 本地解码源码：`/tmp/nathan_nb/decoded_main.py`
- 源码 SHA-256：`7a37397fdb29cbbb17aaf7577352bef910bf4dd0f19bf763b9dcaff68595da54`
- kernel metadata：`/tmp/nathan_nb/kernel-metadata.json`

**提交状态：未提交。**

## 追加的本地 paired panel（2026-09-15）

为检验 Nathan pipe-4 与 Ahmed V43 的直接差异，使用 16 个 seed、双 seat，共 32 局，均 `DONE/720`。多数 seed 的最终现金差值为 ±1，说明两者在当前本地 engine 上几乎行为等价；seed 9004 出现 Nathan +1512（两个 seat 都是正差），seed 717171 出现约 −80，导致总体平均 +89.4，但该平均完全由单个 seed 的 +1512 异常点驱动。按 seed 配对后，15/16 个 seed 接近零，不能支持稳定优势。

结果明细保存在 `/root/autodl-tmp/public_compare_panel.json`（前两行包含 engine 可选环境的无关 import warning；JSON 主体从第一个 `[` 开始）。该结果进一步说明应报告 seed 分布、seat 对称性和异常点，而不能只报告 200 局聚合 Elo。
