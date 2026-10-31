# 公开区情报：ALPEREN AYDIN 与 YUSUKE HAYASHI 的推进轨迹（2026-09-25）

## 0. 一句话结论

两条线的共同点：**都不自己造生产引擎，而是"从公开对局里挖路线 + 在开仓/售卖侧做薄层优化"**。
ALPEREN 是 Ahmed 底盘上的薄层优化者（09-13 → 09-19 五连发，改动全部集中在**开仓压力与卖单时序**）；
YUSUKE 是"磁带 / 区块路由"这一学派的开创者（08-30 → 09-13），我们底座的开局谱系就出自他，
09-13 之后他停止公开发布（0910/0911 的部分已转私人）。

两人的公开 agent 我们都实测了：**全部弱于我们底座，更弱于 archplus**；
可迁移的是**方法**（配对区块 A/B、种子簇 bootstrap、等销量败局诊断、硬尾分层、暴露前沿公式），
不是代码。唯一一条曾经看起来最有价值的"开仓压力"机制，移植到我们底盘后是**确定性 −335/局**。

---

## 1. 取件与留档

全部用 `/root/miniconda3/envs/kaggle-cli/bin/kaggle` + Bearer 认证拉取（`KAGGLE_CONFIG_DIR=/root/.kaggle`）。

| 内容 | 位置 |
|---|---|
| ALPEREN 5 篇 notebook 原件 | `public_intel/kaggriculture-*/`、`public_intel/turn-one-market-advantage-kaggriculture/` |
| ALPEREN 解码后的 agent（5 支） | `farm2945_dev/panel_arms/alperen/{metacounter_r1,turn_one,ready_stock,first_in_line,market_rhythm}.py` |
| ALPEREN markdown 摘录 | `farm2945_dev/alperen_notes/*.txt` |
| YUSUKE 11 篇 notebook 原件 | `public_intel/yhay81_pull/<ref>/` |
| YUSUKE markdown 摘录 | `farm2945_dev/yhay_notes/*.txt` |
| YUSUKE 三个比赛相关 dataset | `public_intel/yhay81_datasets/{six-day-public-state-agent-source,shopforge-fieldbook-tapes,kaggriculture-cpp-environment}/` |
| 本次面板结果 | `farm2945_dev/panel_runs/compare/alp_*_{mirror,strong}.json` |

解码校验：`turn_one` payload sha256 `7a37397fdb29cb…` 与 notebook 内声明一致；
另外三支（ready_stock / first_in_line / market_rhythm）来自各自 notebook 的 B85+GZIP `main.py`。

---

## 2. ALPEREN AYDIN（`alperen5252525`）：五连发时间线

| 日期 | notebook（票） | 底是谁 | 他改了什么 | 他自己报的数 |
|---|---|---|---|---|
| 09-13 | `kaggriculture-metacounter-r1-scored-agent`（27） | Ahmed V39 系 + **yhay81/shop-router-0913 的原生班表**（EXP239/240/242） | EXP241：**按前两个商店里 YARN_STORE 的个数二选一**（V39 vs EXP240），五折整队留出学习；终局救援 | 无面板数字（脚本式 notebook） |
| 09-15 | `turn-one-market-advantage`（13） | Ahmed V43 | **263 队聚成 33 簇 → 发现 C9（5 队，与 V40 系 84% 相似）在第 1 回合不做小麦翻转**；`pipe-4` = V43 + 条件开局（非 BAKERY 路线只买 5 小麦） | 200 局/对手：vs pipe-3 148-25-27（80.8%）、vs V43 raw 193-7（96.5%）、vs V42 192-8 |
| 09-17 | `kaggriculture-ready-stock-earlier-sales`（23） | Ahmed V46 | 只把 `_ADV_LOOK` 3 → **6**（卖单前瞻） | 64 局：advance6 56-8-0，旧版 48-16-0，V46 42-8-14 |
| 09-18 | `kaggriculture-first-in-line-stock-into-income`（59，他的最高票） | Ahmed **V48** | `_ADV_LOOK` → **8** + 可执行现金卖单的**队列清理** + 黎明前库存压力记账（引自 Arlene Farming Score V2） | 144 局确认：136-8-0（均值 +7,608）；对未改 V48 16-8；**排除两个弱对手后的受限面板**：对 R2 均值 +889.25（种子簇 bootstrap CI +708…+1,067）；官方引擎响应局 4-0 |
| 09-19 | `kaggriculture-market-rhythm-sale-policy`（18） | First in Line R3 | ①计划内现金卖单**最多提前 24 回合**（按推断对手存量自适应 8/16/24）②**相邻交换的卖单排序搜索**（3 个对手队列场景，目标 `mean(own_rev) − 0.25×spread`）③开仓小麦压力 30 → **10** | 576 局：132-12-0（均值 +657.5）；**但队列搜索相对 opening10 的配对增益只有 +20.8，CI −19.0…+62.7（含 0）** |

### 2.1 代码级事实（这三条决定了他真正的杠杆在哪）

* 他的开仓（metacounter）：`[BUY WHEAT 13, BUY WHEAT 30, SELL WHEAT 30]` —— 和**我们底座的开仓一字不差**
  （`v54_sweep3_snh48_herdfix_cfg.py:988`）。
* `market_rhythm` 跑到我们这边实测出的开局是：
  ```
  step0 [BUY WHEAT 7, SELL WHEAT 2]
  step1 [BUY WHEAT 10, HIRE ×5, BUY_ANIMAL COW 2, BUY_ANIMAL SHEEP 2]   ← "pressure 10"
  step2 [SELL WHEAT 10]                                                  ← 下一回合回卖
  ```
  也就是说：**他的"turn-one 优势"（step1 立刻雇 5 人 + 买牛羊）我们底座和 archplus 早就在做**，
  他独特的只有 step1 买 10 小麦、step2 卖掉这个"压力往返"。
* 他 screen 表里 pressure 的敏感性很高：0 → 16-0、**10/20 → 20-0**、30（继承值，≈ 他当时的 live）→ 6-14、40 → 0-20（均值 −11,461）。
  这条数看起来像大杠杆，但注意它同时删掉了他 tape 里一条**本来就亏的** `SELL 13 + BUY 5`，
  所以"pressure10 很强"里混着"修掉一条坏单"的收益。
* his own `ownqueue24`（用自己库存当对手存量代理）= 8-12，比用公开 yield 场景差很多 —— 说明**对手存量估计的口径**比搜索本身重要。

### 2.2 我们对他五支 agent 的实测（同池同种子，全部可复跑）

镜像面板 = 与 `v54_sweep3_snh48_herdfix_cfg.py` 同种子双座位（seeds 33…56，24 种子 = 48 局，A−B）；
强池 = `pool_strong.txt`（HL / icefire / v61 / v48）× 同一种子块 × 双座位 = 192 局。

| 他的 agent | 镜像（vs 我们底座） | 强池 W-L | 强池累计分差 | 强池均值/局 |
|---|---|---|---|---|
| `market_rhythm`（他最新最强） | **0 胜 24 负**，均值 −4,171.7 | 98-94 | −108,298 | −564 |
| `first_in_line` | 0 胜 24 负，−4,682.7 | 96-96 | −239,973 | −1,250 |
| `ready_stock` | 0 胜 24 负，−4,624.9 | 92-100 | −239,143 | −1,246 |
| `turn_one`（pipe-4） | 0 胜 24 负，−4,352.0 | 54-138 | −423,238 | −2,204 |
| `metacounter_r1` | 0 胜 24 负，−4,643.5 | 1-191 | −1,936,215 | −10,084 |

同口径对照（同一强池、同一种子块）：

| arm | W-L | 累计分差 | 均值/局 | 分对手（HL / icefire / v61 / v48） |
|---|---|---|---|---|
| 我们底座 | 174-18 | +540,062 | +2,813 | 31-17 / 47-1 / 48-0 / 48-0 |
| **archplus（已提交）** | **187-5** | **+1,362,553** | **+7,097** | **48-0 / 43-5 / 48-0 / 48-0** |
| alp.market_rhythm | 98-94 | −108,298 | −564 | 2-46 / 2-46 / 47-1 / 47-1 |
| alp.first_in_line | 96-96 | −239,973 | −1,250 | 0-48 / 2-46 / 47-1 / 47-1 |

读法：**他的公开线对 v61 / v48 这种"同谱系公开对手"能赢 47-1，但对我们两个私有强对手是 2-46 / 0-48。**
这就是 cha22 那张"market_rhythm 是最难对手（83.3%）"表的真相：那是**在 cha22 的弱底盘上**的相对强度；
在我们底座面前它连一场镜像都赢不到。

### 2.3 移植实验：把"pressure 10"搬到 archplus 上 → 确定性 −335/局

臂：`panel_arms/rkey/archplus_wheatpressure.py`（archplus + step1 `BUY WHEAT 10`（现金≥2860 才做）+ step2 `SELL WHEAT 10`）。

```
种子 33-36 镜像 vs archplus：4 对座位全负，逐局 -335（四个种子、两个座位完全同值 → 确定性往返亏损）
```

即：**在我们的底盘上，这个机制不是"赚钱的往返"，而是"每局固定送 335 分"。**
他的收益来自修掉自己继承的坏单（30 单位 + 失败的 SELL 13），不是这个往返本身。

### 2.4 真实天梯里我们与他的四次交手（旧留档，09-16 前后）

仓库里已有 4 局我们 vs 他两个账号（`Alperen Aydın` / `Alperen Söylen`）的真实 replay：

| 文件 | 种子 | 我方 step1 开仓 | 他方 step1 开仓 | 终局（我们 / 他） |
|---|---|---|---|---|
| `agent_monitor/replays/episode-109035476-replay.json` | 1767353210 | `BUY 5, BUY 10, SELL 60` | `BUY 13, SELL 13, BUY 13` | **98,290 / 92,136（+6,154）** |
| `agent_monitor/replays/episode-109139801-replay.json` | 928385262 | `BUY 5, BUY 10, SELL 60` | `BUY 43, SELL 20, SELL 22` | **148,869 / 141,967（+6,902）** |
| `current_submission_diagnosis_20260916/replays/episode-109460826-replay.json` | 2060032018 | `BUY WHEAT 5` | `BUY WHEAT 5`（**逐步完全相同**） | 104,585 / 104,585（平） |
| `current_submission_diagnosis_20260916/replays/episode-109507881-replay.json` | 1723442598 | `BUY WHEAT 5` | `BUY WHEAT 5`（**逐步完全相同**） | 68,898 / 68,898（平） |

后两局是**行动流逐帧一致、终局分完全相等**（镜像对称世界的签名）——
说明那个时候他的天梯 agent 与我们的提交**在开局行为上等价**（双方都是同一条公开 Ahmed 谱系的分支）。
前两局我们的旧开仓（`5/10/60` 翻转）对他当时的开仓，两局都赢 ~6-7k。

---

## 3. YUSUKE HAYASHI（`yhay81`）：从磁带矿区到区块路由

### 3.1 时间线（公开区全部 11 篇）

| 日期 | notebook（票） | 干了什么 | 关键数字 |
|---|---|---|---|
| 08-30 | `public-match-history-router-rating-2929-aug-30`（6） | ShopForge CR2（当时第 3 名，rating 2929）缩成"两商店路由"的可复现版：top-20 的 2,129 条完整历史 → 去重 1,446 条；**用前两个商店（8×8=64 对）做路由**，23 对留下专家历史，共 10 条历史 | 单条最强 tape 对 Kaito v48：64 局 49-15（0.7656，均值 +4,746）；4,096 个全新种子上 one-shop → two-shop：**0.678263 → 0.814412**（+0.136149，种子级 95% CI [+0.1245, +0.1482]） |
| 08-30 | `replay-public-episode-actions-across-seeds-in-c`（7） | 把 nikital7 的 4000× C++ 引擎升到 `kaggle-environments 1.32.7`，加**逐步状态对照**与大吞吐评估 | 15+1 局、**11,520 个状态**逐字段对齐；价格表覆盖 −10,000…30,000 全整数；10,000 局吞吐测试 |
| 09-01 | `fieldbook-commit-for-three-days`（70） | "三天区块"思想：**只在商店开启时换计划，然后三天不动**；把公开对局在商店边界切块、按商店与状态拼接 | 明确写下"只靠挖公开磁带最终会落后"，下一步必须是**可分支的三天区块**（结束时现金/位置/库存要能接上下一段） |
| 09-02 | `six-day-public-state-fieldbook`（131） | 5 个 144 回合区块（1×2×1×3×5 = 30 条可能路径，8 条路线 tape），4 个决策点用公开状态树；**边界预算守卫**：钱不够时只卖多余库存、按现价从高到低卖，保护饲料/化肥 | 188 对手 × 64 新种子 × 双座位 = 24,064 局：22,795-58-1,211 = **0.9485**（CI [0.9371, 0.9565]）；两块新种子 0.9503（36,096 局）；**常规 164 对手 0.9948 vs 硬尾 24 对手 0.6322** |
| 09-03 | `three-day-shop-router`（123） | turn 360 处按条件替换 360-431 区块：`BAKERY 且化肥库存 ≤ 10232` 或 `PET_CAFE 且对手已种 ≤ 64 格` | 同上预算守卫 |
| 09-08 | `shop-router-0908`（90） | 1,326 条公开历史 → 1,313 条唯一 tape；**像马赛克一样拼接**各段最强区块；只留两个分支点（day6 看 Yarn Store、day27 看鸡蛋存量）；约 **21,000,000 局**候选比较 | 明确写"tape 假设对手重复历史，对会反应的活体 agent 不是完整模拟" |
| 09-09 | `shop-router-0909`（136，最高票） | **step 144 用前两个已公开商店选 13 条完整 719 回合计划之一**；杂草挡路时插 DIG（只延迟该工人当天剩余动作）；**合格卖单提前一回合 + 最后一回合清仓**；step 648 起共用收尾（卖单时序 credit 给 aurax7） | 我们底座的开局谱系来源就是这一篇 |
| 09-11 | `shop-router-0911-simple`（9） | 公开"简化版"：只保留 **64 条预计算商店对路线** + 切换规则，删掉全部修补层 | 自述：公开 0909 随环境变强开始掉分，而**私人 0910 版整整一天留在 top 30** → 部分精修转私人 |
| 09-13 | `shop-router-0913`（4） | public-only simple：固定 tape + 观察商店切换 | 之后公开区再无 router 新版本 |
| 09-07 | `exact-reconstruction-of-the-ev-source-dataset`（13）※别的比赛 | 用 `RandomState(101)` **逐调用复现整条随机流**，把 10,000 行标签变成硬不等式，反推精确系数 | 150,000 格 0 错配；"多一次随机调用整条流就崩" |
| 09-08 | `when-do-daily-top-episodes-see-your-agent`（3） | 28,201 局 / 53 个 manifest：**你的 agent 什么时候开始出现在每日公开 top episodes 里** | 操作触发线 **2,700**；缓冲安全线 **2,500**；要挤掉强提交在 Kaggle **latest-two 追踪集**里的位置，必须交**两个更新的低分提交**；被挤出每日样本**不等于**别人拿不到你的对局——公开 Episode API 仍可单条取回 |

### 3.2 三条可复用的主线

1. **磁带/区块学派**：一条 719 步的公开历史本身就是策略；在**商店边界**切块、按公开状态选块、
   边界做预算守卫。0908 → 0909 → 0911 → 0913 的差别是"修补层留多少"，而不是换引擎。
2. **评测工程**：C++ 引擎 + 逐步状态对齐 + 同种子双座位 + 种子簇 bootstrap。
   他用 24,064 局做池子回归，同时把结果拆成"常规 0.9948 / 硬尾 0.6322"两桶汇报 —— 这正是我们
   `panel_pool` + `panel_hard` 的等价物。
3. **竞赛机制情报**：暴露前沿公式 `trigger = 当日 p05 比赛均分 − p90 匹配差/2`，
   现价估到 2,700（触发）/ 2,500（安全）。我们线上现役分数 2601.7 / 2633.6 / **2676.0**：
   **最强那支已经贴着这条线**，再往上就是每日公开样本的常客。

### 3.3 他已经公开、而我们底座早就吃进去的东西（这条很关键）

* 我们底盘的 `Chassis` 注释里写得很清楚（`v54_sweep3_snh48_herdfix_cfg.py:225-236`）：
  `hand_align`（fieldbook_logic）、`weed_repair`、`sell_lead`（fieldbook `_lead_sale`）、
  **`budget_guard`（`six_day_budget_guard.hpp`）**、`room_guard`/`clamp_sells`/`dead_stock`（tetsutani）、
  `terminal_liquidation`（fieldbook `_terminal_sale`）—— **默认全开**，
  其中 `_block_requirements / _budget_guard`（base 695-760 行）就是 `six_day_budget_guard.hpp`
  `calculate_six_day_requirements` 的逐行移植（连"每 72 步一个块、只卖静态储备以上的库存"的口径都一样）。
* 商店对路由（step 144 用前两商店选 tape）来自 0909 —— 我们的开局谱系就是这条线。
* 他 08-30 公开的 C++ 环境（`kaggriculture-cpp-environment`，1.32.7）已经被我们自己的
  `onearena/kagsim-0.5.0`（968 行，带快照/分支设计）覆盖；他的 tape 库 `shopforge-fieldbook-tapes`
  与 `six-day-public-state-agent-source` 是 09-01/09-02 的旧版本，没有更新价值。
* **公开活跃度**：Kaggriculture 相关 notebook 最后一篇 09-13，dataset 最后更新 09-02；
  09-11 他自己写了"公开 0909 在掉分、私人 0910 留在 top-30"——**这条线在公开区已经停了**。

---

## 4. 我们能拿走什么（方法 > 代码）

| 编号 | 方法 | 怎么落到我们管线 |
|---|---|---|
| M1 | **同边界区块 A/B**：只在同一个边界（turn 144/288/432/576）换候选区块，同种子同座位比较，而不是比整局 | 比我们现在的整局面板便宜一个数量级，适合"番茄/畜群/中盘"这类区块级假设的粗筛 |
| M2 | **选型规则**：先零错误，再 worst-rival match points，再总点数，再现金均值 | 我们 `panel_hard` 已有难例闸，但选型仍以均值/胜场为主；把"最差对手"前置可减少被单一对手绑架 |
| M3 | **等销量败局诊断**：先问"产销量是不是已经一样"，一样就只在价格/队列位置上找 | ALPEREN 用它把方向从生产端扭到售卖端（5/8 败局总销量相同）。我们 78/120"先领先后失血"局可先用同一条切分 |
| M4 | **硬尾分层汇报**：常规对手 / 硬尾对手两个点率分开报 | 直接对齐我们 `pool_strong`（HL/icefire 就是硬尾）与 `pool_public` 的双桶口径 |
| M5 | **暴露前沿公式**（见 3.1 末行） | 提交策略：一旦有效分越过 ~2,700，我们的路线会进入每日公开样本；若要移出，需要两个更新的低分提交 |
| M6 | **精确性偏执**：把"我觉得是"变成"逐位可复现"（他的 C++ 逐步对齐、随机流重建） | 我们 `realworld_panel`（279/281 精确复现）已经是同一路数，可继续当门 |

---

## 5. 明确不值得做的（都带数字）

1. **不要移植他的卖单队列搜索**：他自己 576 局确认配对增益 +20.8（CI −19.0…+62.7，含 0）；
   我们此前移植 cha22 的抢跑族也是 187-5 → 187-5（惰性）。
2. **不要移植"开仓压力往返"**：archplus + pressure10 = 每局固定 −335（4 种子 × 2 座位同值）。
3. **不要继续从公开磁带里挖新强度**：yhay81 自己在 09-01 版就写了这条路的终点；
   而我们已经把这条线做到极致（开局谱系压制 174-18 → 187-5）。
4. **不要拿他们的 agent 当候选臂**：四支镜像全 0-24；最强的一支（market_rhythm）强池只有 98-94。
5. **不要照抄"最小小麦开局"**：我们的 opening 扫格（buy15/20/25/33/40 → `o_archetype` 8/8+5）
   已经测出比"完全不做往返"更好的点；ALPEREN 的 C9 结论我们早就在做（step1 雇 5 人 + 牛羊），
   archplus 是它的更强版本。

---

## 6. 产物与复跑

```bash
# 他的五支 agent（镜像 + 强池，本次已跑）
PY=/root/miniconda3/envs/kaggle-eval/bin/python
$PY panel_selfplay.py --a panel_arms/alperen/market_rhythm.py \
    --b v54_sweep3_snh48_herdfix_cfg.py --seeds 33..56 --workers 8 \
    --out panel_runs/compare/alp_market_rhythm_mirror.json
$PY panel_pool.py     --a panel_arms/alperen/market_rhythm.py \
    --pool pool_strong.txt --seeds 33..56 --workers 8 \
    --out panel_runs/compare/alp_market_rhythm_strong.json

# 开仓压力移植实验
$PY panel_selfplay.py --a panel_arms/rkey/archplus_wheatpressure.py \
    --b panel_arms/rkey/o_archetype_plus.py --seeds 33..36 --workers 4 --out /tmp/wp.json
# 换数量：WHEAT_PRESSURE_ARM=20 ...
```

新产物：`panel_arms/alperen/*.py`（5）、`panel_arms/rkey/archplus_wheatpressure.py`、
`panel_runs/compare/alp_*_{mirror,strong}.json`（10）、`alperen_notes/`、`yhay_notes/`、
`public_intel/yhay81_pull/`。

**本次没有任何 Kaggle 提交，也没有改动 main.py / 现役候选。**

> ✅ 已处置（2026-09-25，用户授权）：`farm2945_dev/main.py` 与 `farm2945_dev/submission.tar.gz`
> 这两份"落错地方"的 ALPEREN `market_rhythm` 副本已**改名隔离**到
> `_quarantine_alperen_20260925/farm2945_dev_root/`（sha 已复核：文件 `f3be6392671608e9…`、
> tar `015d1a895533c262…`），项目根已干净。
> 新增两道闸：`check_no_alperen.py`（打包前跑，命中即非零退出）与
> `panel_arms/alperen/__DO_NOT_SUBMIT.md`；完整记录见 `DELETION_LOG_ALPEREN_20260925.md`。
