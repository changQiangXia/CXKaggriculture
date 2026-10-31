# 候选回执：`cand_comb_pp_race`（消融候选，2026-09-30 21:20 北京）

## 1. 改动（相对 w2_120，只关两层，其它不动）

* 关闭 `_V92_P`（用历史回放库预测对手高价品卖单并"抢先卖"的前置层，
  PREDICT v9/2，作用品 MILK/WOOL/STRAWBERRY）；
* 关闭 `_V9_RACE`（同类的前置卖出/竞速层，作用品 CARROT/TOMATO/STRAWBERRY/MELON/EGG/MILK/WOOL）。
* 来源：对 w2_120 全层做 32 个模块的**消融矩阵**（每层旁路化），在最新 96 局面板上筛出。

## 2. 物件

* tar：`/root/autodl-tmp/farm2945_dev/cand_comb_pp_race.tar.gz`
* tar sha256：`a2639054ef21fcc89c8be47c0e51644de803e4ac1318faf847bbffe69bc2e4dd`
* main.py sha256：`0fcc9bedb1bf02ebad53764ecc730452a462ee96f7aeca325d77abd196fcad1d`
* 入口检查：`entry = kaggle_entry OK`
* 官方 smoke：我方收益 **89,310**（门槛 50,000），statuses `['DONE','DONE']` → OK
* 臂源码：`/tmp/abl/comb_pp_race/main.py`（打包副本 `pkg_comb_pp_race/main.py`）

## 3. 证据（同局配对，clean-both fid≥0.95，vs 现役 w2_120）

| 池 | n(clean) | w2_120 | comb | 翻转 | 净 |
|---|---|---|---|---|---|
| **fresh96（最新 96 局，本槽真实对局）** | 96 | 55W/41L | **60W/36L** | F6/B1 | **+5** |
| **live_all242（主选池）** | 205 | 135W | **145W** | **F10/B0** | **+10** |
| cur163（当前档） | 163 | 108W | 107W | F6/B7 | −1 |
| 合计 | 464 | — | — | F22/B8 | **+14** |

* 翻转局 9/10 是"硬币局"（原 −20 ~ −1,569 的小负 → 小胜），说明关掉的是**系统性小税**，不是靠极值局；
* live_all242 上 **零回归**（F10/B0）；
* 组件拆分（242 池）：单关 V9_RACE +7、单关 V92_P +4、两层同关 +10。

## 4. 已知风险（必须记录）

* **自博弈（镜像尺子）方向相反**：w2_120 vs comb = 45W/19L（comb 负）。
  解释：两层在"对镜像/同血统对手"时是真实的先手优势，但对一般天梯对手是净税。
  本候选赌的是："天梯对手以一般对手为主"——由 242 池 +10/无回归、最新 96 局 +5 支撑。
* cur163 上 −1（中性），无其它池为负。

## 5. 提交建议（需批准）

* FIFO：单发顶掉较老的 gate2 槽（当前 2140.9）→ 队列变 `[w2_120, comb_pp_race]`；
* 计分口径证据：最新榜单我方（rank 348）显示 2233.6 = w2_120 峰值，而 gate2 当时 2158
  ⇒ 队伍分取两槽**最好成绩**，换掉 gate2 是"免费期权"（下限仍为 w2_120）；
* 命令：
  ```
  /root/miniconda3/envs/kaggle-cli/bin/kaggle competitions submit -c kaggriculture \
    -f /root/autodl-tmp/farm2945_dev/cand_comb_pp_race.tar.gz \
    -m "comb_pp_race: w2_120 minus V92_P/V9_RACE front-run layers; +14 net flips over 501 games (fresh96 +5, 242p +10, cur163 -1)"
  ```

## 6. 提交记录（已执行，负责人批准 2026-09-30 21:25 北京）

* **ref 56708604**，提交时间 2026-09-30 13:25:23 UTC，状态 PENDING；
* 队列：`[56697965 w2_120, 56708604 comb_pp_race]`（gate2 56685653 被顶出）；
* 当日剩余配额：3 发。

## 7. 发布后追加实验（同晚）

* **二阶消融**（comb 基底再扫 32 层）：**无新增收益**，最高仅与 comb 打平（60W/36L）；
  必需层得到二次确认：`CA` −15、`OR2` −17、`V9_OPENING` −40、`R70` −7、`CH` −5；
* **卖侧/开关重扫**（9 项）：无收益；`clamp_sells=True` −40、`hand_align=False` −47、
  `sell_lead=False` −7（均为必需）；`front_run/dead_stock/room_guard/terminal_liquidation`
  惰性；窗口 `W2=112`（w1_104 式）在 comb 基底上 −5；
* ⇒ comb 在"层 × 旋钮 × 窗口"三维上已是局部最优；剩余可选动作只有
  ① 242 池高功效复扫（低预期）② 等线上数据。
