# V50 指纹门控反镜像候选（v50_finger）探索记录

时间线：2026-09-20 UTC（按文件时间戳还原）

- 11:42 313 池快照（v50_adaptive / v50_adv10 / farm2945）跑完，两者池上打平 88.5%。
- 11:56~12:25 开局指纹采集、`v50_finger.py` 实现、lead12 验证（V50/V49/V48）。
- 12:25 打包 `candidate_v50_finger.tar.gz`（未提交）。
- 12:25~ 继续优化：farm2945 系 lead 扫描、6 个微开关池扫描。

## 1. 问题

V50 底座（Ahmed 公开 V50）是目前最强底座（313 池 87.9%）。它有两个已知弱点：

1. **V 系镜像平局**：V50 打 V50 基本全平（2W/2L/44T）。`v50_adaptive` 用
   `_R44_PROBES['matched'] 或 RACE level>=mirror` 切 lead10，打 V50 镜像 96.9%，
   但对 farm2945 家族误判（布局相似度>=0.95 且四回合资金增量相等），错误切
   lead10，打 timed174/racepx 只剩 **12.5%**（V50 底座本身是 31.25%/25%）。
2. **farm2945 系本就压制 V50**：V50 底座打 farm2945 系只有 25~31%。

## 2. 关键发现：开局指纹把两大谱系干净分开

对每个谱系跑真实引擎、记录 step 0/1/2 的公开观测（双方现金、小麦报价）：

| 谱系 | step0 市场单 | step1 现金差(rival-own) | step2 现金差 |
|---|---|---|---|
| V48/V49/V50 | [BUY WHEAT 7, SELL WHEAT 2]（EXP284） | **0** | **0**（双方都做 BUY30 攻击） |
| farm2945/timed174/racepx/flood50/gate | [BUY WHEAT 20, SELL WHEAT 15]（V9） | **−6** | **±895**（他们不做我们的 BUY30） |
| 旧 V 开局 [BUY5,BUY10,SELL60] | — | +137 | +2835 |

- 两种开局的小麦净流量恰好都是 −5，所以 step1 小麦报价都是 28，**只有现金差能区分**。
- 座位对称：rival−own 的现金差不随座位翻转。
- 步 1 现金差 0 只能由“逐字节相同 step0”产生，即 V 系克隆；这是 100% 可靠的镜像判定。

## 3. 实现（相对 V50 main.py 的全部改动）

`farm2945_dev/v50_finger.py`：

- `_lin_classify(obs, conf)`：step1 `abs(dm)<0.5 → 'V'`；`dm≈−6 且小麦28 → '2945_tent'`；
  step2 `abs(dm)<0.5 → 'V'`，`2945_tent 且 abs(dm)>800 → '2945'`；其余 `unknown`。
  仅标准配置（board 10/24 回合/3000 起始金）下分类，否则全部 unknown。
- 原 `_mirror = probe_matched or race_level>=24` 改为：
  `_mirror = family=='V' and (probe_matched or race_level>=24)`。
- `_ADV_LOOK_NOW = _ADV_LOOK_MIRROR(=12) if _mirror else (_ADV_LOOK_FARM(=3) if family=='2945' else 3)`。

效果：V 系 → lead12；farm2945 系/unknown → 与 V50 底座完全一致（lead3）。

## 4. lead 选择

8 世界扫描（对 V50 镜像）：lead4..12 全胜，12 平均 margin 最高（904）。
128 世界验证：

| 候选 | 对 V50 | 对 V49 | 对 V48 |
|---|---|---|---|
| lead10（adv10） | 119W/9L 92.97%，mean 403 | — | — |
| **lead12** | **125W/3L 97.66%，mean 505** | **122W/6L 95.3%，mean 2685** | **127W/1L 99.2%，mean 3236** |
| lead16 | 14W/2L（16 世界） | — | — |

lead12 胜出。lead12 输掉的两个种子（302409/302463）是镜像世界里超前抢卖的
反噬世界，座位对称，无法运行时规避。

## 5. 验证

与 v50_adaptive / V50 底座同种子对比（32 世界）：

| 对手 | v50_finger | v50_adaptive | V50 底座 |
|---|---|---|---|
| V50 | 31W/1L 96.9%，mean 690 | 31W/1L 96.9%，mean 524 | 44T 平局 |
| timed174 | **31.25%**（=底座） | 12.5% | 31.25% |
| racepx_demand | **25%**（=底座） | 12.5% | 25% |
| gate_m100u（64 世界） | **28.1%**（=底座） | — | 28.1% |
| flood50（64 世界） | 37.5% | — | — |

313 真实对手池快照（固定录像带重放）：

- **v50_finger 278W/35L 88.8%，mean 3330（候选第一）**
- v50_adaptive / v50_adv10 277W/36L 88.5%，mean 3301/3300
- farm2945 249W/64L 79.6%

结论：finger 严格支配 adaptive（farm2945 系 +19/17 个百分点、V 系 margin 更高、
池 +1 胜 +29 mean），并且对 V 系镜像把平局变 96%+ 胜。

## 6. 继续优化中

- **farm2945 系 lead 扫描**：lead2 在种子集 A 上 +4 胜，但种子集 B 上 net −4，
  不复现；保留 lead3（底座行为）。
- **6 个微开关池扫描**（313 池，确定性重放）：`_ADV_PROTECT=False` 一举把池从
  88.8% 拉到 **91.1%**（285W/28L，+7 胜）；`_ADV_FRONT=False` 掉到 83.7%（证明
  frontload 重要）；`_OPEN_ATTACK=40` 崩到 26.2%（证明 30 是紧耦合值）；
  `BOOK/SUBTRACT_DEBTS/atk25` 各 +1 胜或持平。
- 候选下一步方向：条件攻击量（按步 1 指纹决定 BUY30 攻击规模）、farm2945 系
  败局机制解剖。

### 6.1 noprot 全维度复验（v50_finger_noprot.py，SHA 826338fd…）

`_ADV_PROTECT=False`：不再豁免“下一个回合的首个 SELL”（原本为保护
sale-credit 买饲料而豁免）。复验结果：

- V50 镜像：123W/5L 96.1%，mean 553（finger 为 125W/3L 97.7%，mean 505；
  少 2 胜但 margin 更高）
- V49：122W/6L 95.3%；V48：127W/1L 99.2%（与 finger 一致）
- farm2945 系（64 世界，种子集 B）：timed174 34.4%（+6.3pt）、racepx 34.4%
  （+3.1pt）、gate 34.4%（+6.3pt）、flood 39.1%（+1.6pt）
- 313 池两次独立运行均 285W/28L 91.1%（确定性 +7 胜）

镜像少了 2 胜、但池 +7 胜 + farm 系 +2~4 胜，净收益明确。攻击量 25 与 30
在所有胜负上逐局相同（只改 margin；线上 rating 制不计 margin），故保持 30。

### 6.2 当前最强候选

`farm2945_dev/v50_finger_noprot.py`（打包 `candidate_v50_noprot.tar.gz`，
内含 main.py，SHA 826338fdfc0664dc12cc05c5b90b5f373d7bfcd3618cf7a5dbc45fe5d73b74bc）。
打包件冒烟测试通过（720 步、DONE、0 stderr；自对局精确平局，符合 V 系镜像对称预期）。

375 局全量池（含 flood50_new 40 局 + timed174_new 22 局最新在线败局）：

| 候选 | W/L | pts | mean |
|---|---|---|---|
| **finger_noprot** | **316W/59L** | **84.3%** | **2905** |
| v50_finger | 311W/64L | 82.9% | 2846 |
| v50_adv10 | 305W/70L | 81.3% | 2749 |
| racepx_demand | 287W/88L | 76.5% | 2826 |

结论：noprot 在 313 池、375 全量池、farm2945 系直连三个维度都显著领先，
V 系镜像保持 95%+，是当前最有把握超过线上最高分（flood50 ~2732）的候选。
**未提交，等用户授权。**

## 8. 待办

- noprot 下 V50 镜像的 lead 微扫（10/11/13/14/16），尝试找回 2 个镜像败局种子。
- farm2945 系（34~39%）仍是最大已知短板：解剖 V50 vs timed174/racepx 的败局
  机制，或按步 1 指纹做条件攻击量。
- 结构化贸易对手（Mother-Goose 等）的 −11k 碾压局目前无解，继续收集败局。

## 9. 第二轮（2026-09-20 下午）

### 9.1 lead 微扫（noprot 下 V50 镜像，128 世界各）

L12 仍最优：12=96.1% > 10=91.4% ≈ 11=91.4% > 13=90.6% > 14=89.8% > 16=87.5%。
保持 lead12，未找回的 2 个镜像败局种子无法用 lead 参数解决。

### 9.2 败局池按语料拆解（noprot）

老语料我们赢 89~94%；**最新两个语料是瓶颈**：flood50_new 40 局只有 45.0%、
timed174_new 22 局 59.1%。对赢家做指纹分类：绝大多数是 farm2945 系变体
（V9 开局 `[BUY20,SELL15]` + 卖 WHEAT~17k/CARROT~17k/FERT~10k/MILK~8k 的
同族 tape），夹杂少量 V 系镜像与贸易型。本地 farm2945 系四变体的卖出画像与
线上赢家逐项吻合，可当代理靶子。racepx 打这 62 局只有 25%/18.2%，证明
V50 底盘是正确底座。

### 9.3 败局解剖

输局 razor-thin（±几百/7.5 万）：对手在 day16 前后领先 1~3k，我们逐步追平。
对手靠 CARROT/TOMATO/MELON/WHEAT/EGG 的大额倒卖吃价差；我方强项是
STRAWBERRY/WOOL/FERTILIZER。

### 9.4 farm 系门控微调（fresh-62 真实语料）

对 `_ADV_ITEMS`/`_ADV_FRONT`/`_ADV_LOOK` 做 family=='2945' 专用门控：

| 变体 | fresh-62 |
|---|---|
| farm lead4 | **32W/30L 51.6%，mean +476** |
| farm 门控 nofront | 32W/30L 51.6%，mean +375 |
| 两者叠加 | 32W/30L 51.6%，mean +415 |
| noprot 基线 | 31W/31L 50.0%，mean +436 |
| farm lead2 / race_items / hold_items | 43~48% |

lead4 与 nofront 翻转的是同一局（不叠加）。farm lead4 的 mean 最高，正在
375 全量池 + 本地 farm 代理 128 世界复验中。

### 9.5 farm lead4 复验通过，晋升为新一代底座（v50_np_farm4b.py）

| 验证面 | farm4b | noprot |
|---|---|---|
| 375 全量池 | **317W/58L 84.5%，mean 2913** | 316W/59L 84.3%，mean 2905 |
| fresh-62 | **32W/30L 51.6%，mean +476** | 31W/31L 50.0%，mean +436 |
| timed174（128 世界） | 46W/82L 35.9% | 47W/81L 36.7%（−1） |
| racepx（128 世界） | **48W/80L 37.5%** | 45W/83L 35.2%（+3） |
| V50 镜像（32 世界冒烟） | 31W/1L 96.9%，mean 740 | 同代码路径，不受影响 |

四组共 693 局净 +4，无显著退化。打包 `candidate_v50_npf4.tar.gz`
（内含 main.py，SHA 8c69203991b5d7b44ad796dd051fc09da62661c2d7a0f74bcde9c7f14ba48bf9），
冒烟测试通过。**未提交。**

### 9.6 fresh-62 败局差距分布

30 个败局：5 个 −5k~−12k（贸易/结构型，短期无解）；25 个 −2~−3.5k，其中
**13 个差距 ≤448**（-2/-15/-36/-169/-177/-197/-240/-374/-395/-432/-448…），
终局相位还有可翻空间。下一步主攻：终局清仓相位（`_y_preguard`/day-23 守仓/
terminal 712-718）的 farm 系门控微调，目标是把 ≤448 的薄局翻一半。

## 7. 提交纪律

**未提交。** 用户明确要求没有授权不得提交；打包件
`farm2945_dev/candidate_v50_finger.tar.gz`（内含 main.py，SHA
36ffc85fc7acba836faf9536b3de3dd864aa1918c21a9f15613ef53b688f1c12）
仅作候选，等用户授权。
