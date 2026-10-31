# HANDOFF — Kaggriculture（2026-09-24，给下一个完全无记忆的会话）

这是一份自包含交接。下一个 agent 没有任何对话记忆，请按顺序读完全文再动手。
工作目录约定：`/root/autodl-tmp`（默认 cwd）。

---

## 0. 一句话现状

我们参加 Kaggle 竞赛 **Kaggriculture**
（https://www.kaggle.com/competitions/kaggriculture，队伍 **CHEN Xiang**，
team_id 16870342）。项目主线是"用数学建模法开发原创变现机制"。
结论：**市场结算律已 bit-exact 逆向；在该模型上求解出的最优变现控制器 =
线上底座本身；八条原创变现机制全部实测证伪或平价；变现空间已榨干。**
当前 active goal 状态为 **blocked**，解除需要用户授权扩大目标范围（生产/
固定成本结构）或等新对手数据（georgy 09g 波次还没发布）。

---

## 1. 游戏与评分（必须记住的规则）

- 1 局 = 720 步 = 30 天 × 每天 24 步（step 0..719）。双人对战，共享市场。
- 9 种商品：WHEAT/CARROT/TOMATO/STRAWBERRY/MELON/EGG/MILK/WOOL/FERTILIZER，
  各自独立库存 I（初始 10000）、独立价格函数 p(I)。
- 每步市场订单 ≤10 槽；**逐单位锁步结算**：同一槽同一单位下标，双方先用同一
  快照价报价、再按玩家序（p0 先）提交。同一步的镜像卖单实现**相同单价**，
  因此相对胜负只可能来自"步级"时机差。
- 关键结算语义（官方源码
  `/root/miniconda3/envs/kaggle-eval/lib/python3.11/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`）：
  - 价格取整是 Python 银行家舍入 `int(round(v))`，底价 1；
  - SELL 报价 p(I)，且 **price==1 的卖单不增加库存**；BUY_PRODUCT 报价
    p(I−1)（同价往返净零），且**仅 WHEAT/FERTILIZER 合法**、shed 容量 100
    装满即拒；
  - HIRE 成本 = farmHandCostMult × fib(hires_today)，fib=1,1,2,3,5…；
  - **空订单是槽位占位符**，处理订单时不能过滤空列表，否则双方槽位错位、
    锁步交错会错；
  - 需求是**确定性**的：step%4==0 每家已解锁商店按其菜单消费（单品店×2），
    step%24==0 镇中心每非肥料商品 −1。商店解锁是 `random.Random((seed*1e6+3)^day)`
    抽取，但列表在观测里可见，所以需求可完全重建。
- **终局计分 = 现金**（官方：`s.reward = farm.money`），shed 库存不值钱——
  所有"持有到终点"的策略都是错的。
- 初始 3000 金；买地 1000/2000/4000；种子 10/20/50/100/80；动物 300/400/500。

## 2. 运行环境（直接用，别重装）

- 本机三个 conda 环境（全部实测，按用途选，别混用）：
  - **kaggle-eval**：`/root/miniconda3/envs/kaggle-eval/bin/python`
    （Python 3.11.16）。唯一带本地引擎 **kagsim 1.32.7** 的环境；另有
    kaggle_environments、torch 2.6.0+cu124（CUDA 可用）、pandas、pyarrow。
    **没有 `kaggle` pip 包**（所以 `meta_pipeline/intel_harvest.py` 用它跑会
    ImportError，要用 §8 的 urllib 直连方式）。
  - **base**：`/root/miniconda3/bin/python`（Python 3.10.8）。有 `kaggle`
    pip 包（装在 `~/.local/lib/python3.10/site-packages`，KaggleApi 可用）、
    kaggle_environments、torch、pandas；**没有 kagsim、没有 pyarrow**。
  - **kaggle-cli**：只有 CLI 二进制 `/root/miniconda3/envs/kaggle-cli/bin/kaggle`
    （2.2.4），用于 `kaggle competitions replay <eid> --path <dir>` 拉完整
    replay JSON；其 python 解释器不装任何数据包。
- 跑 kagsim 反事实/验证一律用 **kaggle-eval**；拉 Kaggle API 数据用 base 的
  KaggleApi 或任意 env 的 urllib（Bearer token）；拉 replay 用 kaggle-cli。
- Kaggle API 认证：Bearer 在 `/root/.kaggle/access_token`；内部 RPC 用
  `/root/.kaggle/kaggle.json` 的 Basic auth。
- CPU 上限 **12 核**（用户要求），别把内存/CPU 打爆；parquet 大文件要流式读。
- **未经用户明确批准，不得提交任何东西到 Kaggle。**

本地引擎用法（全项目通用，很重要）：
```python
import kagsim
sim = kagsim.Game(seed)            # 719 次迭代，step 0..718，终态 step 719
while not sim.done:
    o0 = sim.observe(0) or {}; o0["player"] = 0
    o1 = sim.observe(1) or {}; o1["player"] = 1
    sim.step(a0(o0), a1(o1))       # 动作 dict: farmer/hands/market
obs = sim.observe(seat) or {}      # farms[i]["money"] = 现金（即分数）
```

**回放约定（曾反复踩坑，钉死）**：`steps[0]` 是初始观测，`steps[0]['action']`
是哑动作；对 i≥1，`steps[i]['observation']` = 第 i−1 步处理后的状态（即第 i
步动作**之前**的观测），`steps[i]['action']` = 第 i−1 步的动作。因此 replay
对手 tape = `[steps[i][opp]['action'] for i in range(1,720)]`，第 n 次循环
（游戏步 n）喂 `acts[n]`。

**loader 规则**：Kaggle 环境/本项目加载 agent 文件时取模块字典里
`[v for v in m.__dict__.values() if callable(v)][-1]`（最后一个 callable）。
在文件尾部重新绑定 `agent` 名字时，名字在字典里的位置不变——要用仓库惯用
手法 `agent = globals().pop('agent')` 把名字挪到末尾，否则 loader 拾到旧函数。

## 3. goal 对象（当前 blocked，不要擅自改目标或提交）

用户设定的 objective（原样）：
> 目标：用数学建模法开发原创变现机制并孵化候选。
>   Phase 1 逆向并 bit-exact 复现市场结算律（逐单位价格/库存/现金更新、
>   日耗、交错顺序、取整与底价），输出 market_model.py，对拍 100+ 局逐步全等；
>   Phase 2 在该模型上求解共享库存-价格动力学下的最优变现控制器（含对手
>   卖出流预测/自博弈），移植到 herdfix 底座，做成带开关的独立层；
>   Phase 3 过四门：257 池 P(win) 不退化、107 最新线上败局零负 delta、
>   镜像 90 板零新增负局、loader 打包 tar。CPU 上限 12核、不得提交

完成度与阻塞原因：
- **Phase 1 完成**（见 §4）。
- **Phase 2 完成**：解出的最优变现控制器 = 线上底座本身（见 §5 八条机制
  总账），控制器已带开关移植。
- **Phase 3 不可达**：四门里"107 零负 delta + 镜像 90 零负板"等价于要求
  一个处处不劣于底座的**非平凡**改动；八条机制的完整反事实证据表明它不存在。
  唯一能过门的"候选"是底座自己（等于没孵化），违背目标本意。
- 阻塞条件已连续 3 个 goal turn 重复，按规则已 `update_goal(status="blocked")`。
  解除需要：用户授权扩目标到生产/固定成本结构，或新对手数据到来（09g）。
  若用户回复授权，重新激活目标并照做；不要自行扩大范围。

## 4. Phase 1：bit-exact 市场模型（已完成，最硬资产）

文件 `/root/autodl-tmp/farm2945_dev/market_model.py`：
- `price(item, inventory)`、`settle_step(inv, cash, shed, o0, o1, shops=,
  hires=, quads=, shed_capacity=100, hire_mult=1)`、`demand_tick(inv, step,
  shops)`、`hire_cost(n)`。语义与官方引擎逐单位全等。

验证 `/root/autodl-tmp/farm2945_dev/validate_market_model.py`：
- 结果 **365 局 / 262,800 步：现金 0 错、库存 0 错**（覆盖 soft9/gate12v2/
  s1s/fresh/pairgate/v54pg/batch3 + 20260923/24 全部败局目录）。
- 唯一例外 1 格：episode-111639163 终局（step 718）双方把 120 单位物资 DROP
  进容量 100 的 shed、切断点落在某工人身上；回放序列化把库存字典按字母序
  排序、丢失引擎拾取插入序，差 3 单位。已用"小麦优先"重排实验证实是数据
  不可复原，不是模型错。
- 运行：`/root/miniconda3/envs/kaggle-eval/bin/python
  /root/autodl-tmp/farm2945_dev/validate_market_model.py`

历史坑（旧文档曾写错，已更正）：需求曾被误判为 RNG；配对买入价曾用快照
p(I)（应为 p(I−1)）；旧模型把 HIRE 按手数计价（应按 hires_today）；价格取整
曾用四舍五入（应银行家舍入）；空订单曾过滤（破坏槽位对齐）。这些更正记录在
`MARKET_MODEL_PHASE0.md` 的"重要更正"一节。

## 5. Phase 2：八条变现机制总账（全部实测）

详情：`/root/autodl-tmp/farm2945_dev/REALIZATION_SOLUTION.md`。
口径：21 局最新败局 tape 反事实（kagsim，对手动作冻结、我方换策略）。

| 机制 | 21 局合计 delta | 判定 |
|---|---|---|
| 持有+卖最便宜（v1 / 底座 hold 旋钮） | −94,212 / −527,677 | 证伪 |
| ER 前插窗口 er 504/696 | +109 | 平价 |
| 小麦价格砍单 th=44 | −1 | 中性 |
| 小麦搭便车（对手流条件） | 与 λ 无关 | 结构失效（同回合镜像在决策时刻不可见） |
| 速率抢跑 rz2_pre | −160 ~ −765 | 证伪（卖进对手砸盘坑里） |
| advance-sales adv=1, lookahead 1..4 | +275 峰值 | 平价（shipped 底座默认 adv=0） |
| 相位锁定抢跑 | 无信号（79% 同回合、非零相位对称噪声） | 不可行 |
| room/dead/liq 旋钮关闭 | +0 | 不触发 |

神谕上界（完美预判抢跑）= +58,083，但拆解后大部分物理不可达：58% 跟卖事件
是同回合镜像（锁步同价），对手 dump 当步我方有货可前插的事件仅 86 个。

三通道归因（`attribution2.py`，bit-exact、残差 0）：21 局总卖出赤字
+145,655、19/21 局卖出收入落后于对手；赤字 95% 是**小麦成交量差**（对手
多买 1,609 单位、多卖 1,752 单位，净 +3.2k）；逐商品有效均价与对手几乎相等
⇒ 卖出时机已打平。剩余体量在固定成本/生产结构（约 1,054/局：雇佣节奏、
小麦产能、买端时机）——**不属于"变现控制器"自由度**。

## 5.5 百次迭代记录索引（下一个 agent 必须知道的历史文档）

上一版 handoff 漏了这条，补上。整个项目的"100+ 次迭代记录"散落在这几处，
动手前先按顺序扫一遍，避免重复已验证的结论：

1. **主迭代日志（最重要，127 轮）**
   `/root/autodl-tmp/farm2945_dev/V53_PREDICT_RESEARCH_20260921.md`
   （3251 行、209KB，更新到 2026-09-24 02:08）。从 V53 PREDICT 深度研究
   （目标 EV 93%+）一路记到"第一百二十七轮：GA 收线——96% 镜像安全不可达
   + 最终四门 + 证据链交付"。所有机制的"证平/证伪/首翻正"判定都在里面，
   每轮带验证数字。**下一个 agent 应把它当权威历史，别再重新扫已验证过的
   旋钮。**
2. **farm2945 反镜像探索日志**
   `/root/autodl-tmp/farm2945_dev/EXPLORATION_LOG.md`（2026-09-19）：
   从"照搬 2945 Farm"到 flood50（RACEGATE/RACEPX 门槛 −100 + 0.5 地板）
   再到 timed174 两阶段定时切换的完整推导；镜像死锁与军备竞赛的结论。
3. **每日迭代工作流定义** `/root/autodl-tmp/meta_pipeline/DAILY_CYCLE.md`：
   情报收割 → 指纹差分 → 低风险层脚手架 → 竞技场守门 → 提交（需用户授权）
   的每小时循环；其中 arena_gate 的判定口径。
4. **提交回执（每个 live 提交的来历与分数，共 9 份）**
   `/root/autodl-tmp/farm2945_dev/SUBMISSION_RECEIPT_*.md`：
   FLOOD50、TIMED174、NPF4、V54PAIRGATE、V54PAIRGATE_V2、S1S、S1SD、
   SNH48、AM。另有 `/root/autodl-tmp/v48_candidate/SUBMISSION_RECEIPT_20260918.md`
   和 `/root/autodl-tmp/v48_candidate/CANDIDATE_ADV20_H10_REPORT.md`。
5. **候选报告** `/root/autodl-tmp/farm2945_dev/CANDIDATE_*.md`（FLOOD50、
   V54_STACK_S1S、SNH48_D27FIX、SNH48_HERDFIX、PROTOCOL 等）与
   `/root/autodl-tmp/farm2945_dev/GA_SEARCH_FINAL_REPORT.md`（island-GA 收线）。
6. **早期阶段（Sep 15-18，v37/2945 之前的原始迭代）**
   `/root/autodl-tmp/` 顶层大量 `*.md`：`DAY2_CANDIDATES.md`、`DAY2_REFINED.md`、
   `GOLD_ZONE_*.md`、`CANDIDATE_V37_*.md`（约 10 份 v37 变体报告）、
   `CURRENT_TWO_SUBMISSION_LOG_DIAGNOSIS_20260916.md`、
   `CUSTOMER_UPLOAD_KAGGLE_RESEARCH_AUDIT_20260917.md`、
   `BASELINE_COMPETITION_RESEARCH_20260916.md` 等。这些是 v37 时代及其前的
   记录，只有在追溯早期决策时才需要。
7. **本轮（数学建模变现线）文档**：`MARKET_MODEL_PHASE0.md`、
   `REALIZATION_SOLUTION.md`（即本 handoff §4/§5 的出处）。

## 6. 底座/候选文件（farm2945_dev/）

- `v54_sweep3_snh48_realize.py`：herdfix 底座 + d27 + ER + rz2 变现层（带
  `_RUN_CFG` 开关：rz2_wheat_px、rz2_wheat_rival、rz2_pre_win/lam/k、
  er_from/er_to/er_dump_min/er_min、lookahead、adv_protect）。loader 拾取
  已修（文件尾部 `agent = globals().pop('agent')`）。
- `v54_sweep3_snh48_herdfix_cfg.py`：无 rz2 层的 herdfix 底座（_UNIT_NS 用于
  单位动作重建）。
- `rz2_gate.py`：四门终审（257 池 / 107 败局 / 镜像 90 板 / 打包 tar）。
  上轮结果：257 池 cand 0.9216 = base 0.9216（不退化）；107 败局 2 个负
  delta（−1、−3）；镜像 5 块负板（−4~−874）；tar 已产。
- `attribution2.py`：逐渠道归因（用法 `python attribution2.py`）。
- `realize_counterfactual.py`、`rz2_race_sweep.py`、`rz2_wheat_sweep.py`、
  `rz2_pre_sweep.py`：各机制的 21 局扫描器（直接 `python <file>` 跑）。
- `loss_attribution.py <replay.json>`：单局逐步卖出收入归因。
- `pull_losses_smart.py`：拉线上败局 replay（见 §8）。
- `pull_live_episodes.py`：拉线上 episode 摘要（只有 id/seed/agents，**没有
  steps**，别当成 replay 用）。
- 文档：`MARKET_MODEL_PHASE0.md`、`REALIZATION_SOLUTION.md`、
  `GA_SEARCH_FINAL_REPORT.md`（island-GA 线，已提前收尾，勿重跑）。

## 7. 线上状态（两个 live 提交，别动）

- **snh48**（sub 56456489）：分数 2697.4 → **2656.8（−40）**。最新窗口
  （Sep 23 17:41 → Sep 24 01:56）45 局 = 18 胜 27 负，亏损幅度 −80 ~ −9,559、
  均值 −2,324，15/27 场差距 ≤1,500。**这个滑坡是当前最该盯的信号。**
- **AM**（sub 56472390）：2626.2 → 2625.7，基本持平；窗口 37 局 = 19 胜 18
  负，亏损 −29 ~ −15,806、均值 −3,106。
- 败者池（可直接跑反事实）：
  - `/root/autodl-tmp/snh48_losses_20260924/` 38 场；
  - `/root/autodl-tmp/am_losses_20260924/` 28 场；
  - 文件命名 `episode-<id>-replay.json`，是含 steps/info/seed 的完整 replay。
  - 统计文件 `snh48_losses_20260924_stats.json`、`am_losses_20260924_stats.json`
    含每局的 outcome/双方 reward/rating 变化/对手 sub/team。
  - 注意 `/root/autodl-tmp/fresh_live_20260924_0205/` 里 46 个 JSON 是**摘要**
    （无 steps），已被 smart 拉取取代，别用。
- 更早的败局语料目录（20260922/20260923 系列）也在 /root/autodl-tmp/，供做
  更大的池子。

## 8. 常用操作手册（可直接照抄执行）

### 收集最新败局
```bash
cd /root/autodl-tmp/farm2945_dev
/root/miniconda3/envs/kaggle-eval/bin/python pull_losses_smart.py \
  --subs 56456489:snh48_losses_20260924:<snh48当前最大episode_id>,56472390:am_losses_20260924:<am当前最大episode_id> \
  --workers 6
```
取 `<max_id>`：`ls <dir>/episode-*.json | sed 's/.*episode-\([0-9]*\)-replay.json/\1/' | sort -n | tail -1`

### 查线上分数/状态
`/root/autodl-tmp/farm2945_dev/pull_live_episodes.py --subs 56456489,56472390
--since <ISO时间> --only-losses`（只拉摘要）。或者直接看两个 `*_stats.json`
里最新的 `current_score`。

### 对候选打 21/66 败局反事实（tape 对手）
参考 `realize_counterfactual.py` 的结构：每个 replay 取
`seed=info.seed`、`acts=[steps[i][opp]['action'] for i in range(1,len(steps))]`，
用 kagsim 循环（§2），我方换成候选函数，终局读
`sim.observe(our)['farms'][our]['money']` 做 margin。`_RUN_CFG` 通过
`m.__dict__["_RUN_CFG"]["<knob>"]=v` 注入（注意是 `__dict__`，module 不可下标）。

### 分析败局归因
`/root/miniconda3/envs/kaggle-eval/bin/python attribution2.py`（内置 21 局语料）；
单局：`loss_attribution.py <replay.json>`。

### 跑 Phase 1 验证
`/root/miniconda3/envs/kaggle-eval/bin/python validate_market_model.py`

### 逛公开区（情报）
Kaggle API 用 Bearer token（`/root/.kaggle/access_token`）直接 urllib：
- 最新 notebook：`GET https://www.kaggle.com/api/v1/kernels/list?
  competition=kaggriculture&sortBy=dateRun&page=1&pageSize=25`
- notebook 源码：`GET https://www.kaggle.com/api/v1/kernels/pull/<owner>/<slug>`
  → 取 `["blob"]["source"]`（顶层 `source` 字段是空的）。
- 讨论：`GET https://www.kaggle.com/api/v1/competitions/kaggriculture/topics?
  sortBy=recent&page=1` → `["topics"]`。
- 内部 episode RPC：`POST https://www.kaggle.com/api/i/competitions.EpisodeService/
  {ListEpisodes|GetEpisode}`，body `{"competition":"kaggriculture",...}`，
  Basic auth（kaggle.json）或 Bearer。
- 注意：`meta_pipeline/intel_harvest.py` 依赖的 `kaggle` pip 包**已不在任何
  env**，别直接跑它；用上面 urllib 方式。

### 后台进程
- **紧盯 09g 的脚本（正在运行，PID 15057，Sep 23 启动）**
  `/root/autodl-tmp/meta_pipeline/georgy_watch_download.py`，由 base python
  直接跑，cwd 在 `meta_pipeline/`，**每 900 秒（15 分钟）轮询一次**。
  - 干什么：调 `GET /api/v1/datasets/list/georgymamarin/kaggriculture-episodes`
    （Bearer token），对比状态文件里已见过的 `replays_*.parquet` 列表；
    出现**新文件**（预期下一个是 `replays_2026-09g.parquet`，即"g 波次"）时
    自动流式下载（1MB 分块防爆内存）到
    `/root/autodl-tmp/public_intel/georgy_dataset/`，并刷新
    `episodes.csv / agents.csv / teams.csv`，然后写日志 `READY ...`。
  - 状态：`/root/autodl-tmp/meta_pipeline/state/georgy_watch_state.json`
    （`{"have":[...9 个 parquet...]}`；目前最新 = `replays_2026-09f.parquet`，
    **09g 还没来**）。
  - 日志：`/tmp/georgy_watch.log`（每条一行，如
    `no new (latest=replays_2026-09f.parquet)`）。
  - 查活着：`ps aux | grep georgy_watch`（应有 PID 15057）。
  - **若它死了，重启**：
    `cd /root/autodl-tmp/meta_pipeline && nohup /root/miniconda3/bin/python
    georgy_watch_download.py >> /tmp/georgy_watch_daemon.log 2>&1 &`
  - 重要性：09g 一到（日志出现 `NEW FILES`/`READY`），就是解除 goal blocked
    的第二条路径——用新一批真实对局重新校准对手分布；届时应立即跑
    §8 的败局收集 + 面板更新。

## 9. 公开区情报（截至 2026-09-24 09:55 UTC）

详情：`/root/autodl-tmp/meta_pipeline/intel/digest_20260924_0955.md`。

- **当前顶层对手家族：herd_safe / measured_v60 / moon_v1 / route_v44**
  （nihilisticneuralnet "Population-Robust Economy" 点名；他在这些家族上
  也平台期，herd_safe 只能打平 0.5 分）。我们的败局池主要是自家镜像人群
  （snh48/am 系），**与当前顶层分布已经不是一回事**。
- nihilistic 的搜索维度（可借鉴）：pre-overflow 卖、市场响应窗口、番茄浇水
  跳表、小麦卖价地板(31)、race_horizon(44)、HybridOpening、skip_days
  [19,21,23]；tomato-for-cow 开局决定性失败。
- Ahmed 最新公开 = v57（Funding-Order Invariant），我们已用 v57fix 终审过。
- georgy 每日榜面脉搏（2600+ farms：指纹、H2H 非传递表、"运气 vs 配对"）；
  destbreso 45k 已解析配对基准——未来做对手分布面板的现成资产。09f 数据
  本地在 `/root/autodl-tmp/public_intel/georgy_dataset/`（episodes.csv 21.9 万
  行、replays_2026-09f.parquet 1.26GB/10030 行，episode id 最高约 112.18M）。
- graph-RL 笔记本（GNN+Double-DQN 残差、18 局）与"局部 RL 收效甚微"同向。

### 9.1 评论区/公开区需要重点关注的人（及为什么）

- **ahmedberatozer（Ahmed）**：本竞赛公开区最强机制源，几乎每日发新版
  （v46→v57，最近 v57 = Funding-Order Invariant）。他每次都能从公开对局里
  挖出新观点（首回合微观结构、清理队列、funded-sale-timing、lean-flock、
  小麦 productive 等）。**每次逛公开区第一件事：查他有没有新 release，有就
  拉源码逐层读注释找署名与思路。** 历史 dossier 在
  `/root/autodl-tmp/public_intel/ahmed_dossier/`（v56 源码已存）。
- **destbreso**：方法论/审计者，不是打手。产出过 telemetry（catch-what-you-
  lose）、clone/DNA 检测（can-i-clone-you-from-your-dna）、决策树提取
  （97%-predictable）、who-is-beating-you、everyone-is-playing-the-same-opening、
  45k 已解析配对基准（CC0）、weed-spawn 消融（"免费实验"）。他的分析文和
  benchmark 是面板/对手画像的现成资产。用户历史要求"像研究 destbreso 一样
  系统研究 Ahmed"——即把人家的分析范式学过来。
- **georgymamarin**：全量 replay 数据集作者 + 每日榜面脉搏（2600+ farms 指纹、
  who-beats-whom 非传递表、运气 vs 配对）。数据本地已有（09f），09g 波次
  由后台 watcher 盯。
- **nihilisticneuralnet**：Population-Robust Economy（32 票），点名当前顶层
  对手家族 herd_safe/measured_v60/moon_v1/route_v44；"最差家族分优先"的
  鲁棒搜索方法论值得抄作业（但不抄他混淆的 main.py）。
- **leoprovorov**：逆向/机制向（god-s-mode-hacked-stores、a-song-of-ice-and-
  fire fixed-vs-flexible、agent-analytics-tool-agent）。
- **tetsutani**：demand-preserving-turn-sale-timing（已 v84），市场节奏派。
- **shiiin9**：order book 视角（your-market-list-is-an-order-book）。
- **statma / arsgorynich**：herd-safe 线（Herd-Safe Sale Window、V40
  Challenger）——当前最难打的 herd_safe 家族的公开源头。
- **haideptry**：2965 Master Hybrid Engine；**thomastschinkel**：2945 Farm
  （镜像克隆重灾区，历史反镜像线的起点）。
- 讨论区置顶"Beware of scammers asking for source code"：有人冒充要源码，
   任何索要我们代码的私信/话题都别理、别外发。

### 9.2 本机 skill 的调用（下一个 agent 必须按规矩用）

- 本机装了 **agentic-kaggle-skill**：
  `/root/.codex/skills/agentic-kaggle-skill/SKILL.md`（别名 r0）。
  当任务命中 Kaggle 竞赛工作流（scored submission、本地验证、公开
  notebook/discussion 情报、建模调优等）时，**必须**先完整读一遍 SKILL.md，
  再按需读其 references：
  - `references/competition-intel.md`：逛公开区/挖情报前必读（本 handoff §9
    的情报就是这个口径产出的）；
  - `references/information-sharing-policy.md`：对外分享任何东西前必读；
  - `references/submission-endgame.md`：涉及提交前必读。
  - 其余 references（tabular-workflow 等）与本竞赛的 RL 风格不直接相关，
    按需即可。
- 注意：**skill 不跨会话自动延续**——下个会话动手前重新读 SKILL.md，不要
  凭上会话记忆。skill 里的 MCP 情报工具（kaggle-competition-intel）本机
  **不可用**，用 §8 的 urllib API 直连替代。
- 另外的 skill（imagegen/plugin-creator 等）与本项目无关，不用。

## 10. 下个会话的决策点（等用户拍板）

1. **解除 goal 阻塞**：只有两条路——用户授权把目标扩到生产/固定成本结构
   （雇佣节奏、小麦产能、买端时机），或 09g/新对手数据落地。当前 blocked，
   没有授权不要自行改目标、不要提交。
2. **分析 45 场新败局**（尤其 snh48 的 −40 滑坡）：跑 attribution2 + 单局
   归因，确认是不是 herd_safe 等新家族造成的。
3. **按新家族重做面板**：拉 herd_safe/measured_v60/moon_v1/route_v44 近局
   （georgy 09f / 后续波次），替换旧的自家镜像面板，重新校准候选。

---

## 11. 给下一个 agent 的提醒

- 用户风格：只看结果、重证据、讨厌粉饰；失败要公开反事实数字，不要用
  "可以试试"糊弄。评分只认 P(win)/胜点，现金边际只是诊断。
- 历史教训（别再走弯路）：不要重跑已收尾的 island-GA 线；不要提交任何
  东西（未授权）；不要在自家镜像人群上继续扫变现旋钮（已证明平价）；
  处理 replay 时牢记 §2 的时序约定和空订单占位符。

---

## 12. 支线任务结项（2026-09-24 晚）：三份新公开 notebook

详见 [PUBLIC_INTEL_20260924_SIDE_TASK.md](farm2945_dev/PUBLIC_INTEL_20260924_SIDE_TASK.md)。

**结论一句话**：三份 notebook 全部逐字节还原并上面板，全部不如我们底座
（HL −531 / ice&fire −1,313 / V61 −4,314）；它们相对我们"独有"的层搬到
我们底座上全部 ≈ 0（空转或噪声），唯一严格非负的是 HL 的 day-27 种子浮存
裁剪（+20/局，7 胜 0 负 9 平，量级 ≈ 0.02%，不足以改排名）。

**留下的两件真东西**：

1. `farm2945_dev/panel_decomp.py` —— 任一对局的逐日/逐商品/期末结构差分归因
   （自检 A=B 时精确归零）。已用它证明：我们与 HL 的 −531 从 day 17 起累积，
   且期末结构完全相同（动物 17.2 / 雇工 11.3 / 地块 3.2 / 棚余 0），只差钱。
2. `farm2945_dev/icefire_selfcheck.py` —— 冰火度量尺。实测我们底座
   **step 0–143 在 16 个世界逐动作完全一致（纯冰），首个分歧步 = 144**，
   与 THIRD FARM CLUB(145) 同格，而榜首是 M&M&P&Q 1 / SpaTaro 2 / Majkel1337 4。
   这是"我们开局完全不读活体信号"的第一次量化，也解释了为什么 11 条固定
   路由 + 12 个有界生产臂全判负。

**移植臂（可复跑，A=移植臂 B=底座，16 种子双座）**：
`panel_arms/t_v61_r124.py`(+0.0 空转)、`t_v61_r132.py`(+21.1 噪声)、
`t_v61_r134.py`(+21.1 空转)、`t_v61_r127r128.py`(双包装递归崩溃)、
`t_hl_dsmca.py`(+21.8 平局 3W/3L/10split)、`t_hl_33sf.py`(+11.2 7W0L9平分)。

**纪律**：本轮无任何 Kaggle 提交；seed 101..112 holdout 未触碰。

---

## 13. 新方向已启动（2026-09-24 深夜）：世界条件化缺口

完整报告：[NEW_DIRECTION_20260924.md](farm2945_dev/NEW_DIRECTION_20260924.md)

**新基础设施（全部可用）**：
`panel_pool.py`（对手池打分，配 `pool_public.txt` 9 对手 / `pool_strong.txt` 4 强对手）、
`race_probe.py`（引擎卖单竞赛实测）、`endgame_trace.py`（末段逐 step 双边卖单）、
`shop_index.py`+`shop_index.json`（1000 种子→商店对，232 个含 YARN）、
`corpus_volume_diff.py` / `corpus_structure.py` / `revenue_decomp.py`。

**已确立的事实**：

* 引擎卖单竞赛实测：早一步或早一个 slot = **+76 / 100 单位**（WHEAT），
  自然价格漂移只有 **+7/步**；抢跑收益约为等待的 10 倍。
* 微观结构线**已榨干**：VQ 镜像 +59 但对手池 +17（≈0）；ADV −49.9；
  末段抢跑精确 0.0（末段货当天才进棚）；"抄赢家全清" −12.7k~−71k
  （毁掉 day-27 番茄的 day-29 高价窗口）；YARN 回退旧路由 −157.5。
* **YARN 世界是语料里最大的系统性缺口**（旧提交 120 负 + 161 胜）：
  含 YARN_STORE 的世界胜率 **37.3%**（75 局，−1,238）vs 非 YARN **64.6%**
  （206 局，+1,274）。对手构成随机（75 局 70 个不同对手），对手终局钱只高 3%。
  机制：旧提交的**我方终局钱与世无争**（YARN 99,465 / 非 YARN 98,891），
  而对手在 YARN 多赚 3.1k；YARN 世界羊毛价格 day10-18 高达 216-233
  （非 YARN 早就压到 50-74），我们 day18 领先 7.7k 却在最后 11 天全吐回。
* **但当前底座已部分修好**：活体对手池（4 强对手 × 24 种子）YARN 组
  +2,741（174胜18负）vs 非 YARN +3,117（181胜11负），只差 376；
  镜像绝对值 YARN 92,375 vs 非 YARN 90,990（**+1,385**，旧提交是 +574 反向）。
  残余缺口约 1.7k/局 × 23% 的世界。

**下一步（下次开工直接做）**：把同一套"钱曲线 + 结构 + 世界类型"拆解套到
**顶队公开 replay** 上——本地已有现成语料：
`public_intel/georgy_dataset/replays_2026-09{d,e,f}.parquet`（1.4/2.5/1.3 GB）、
`top_replay_mining/replays_2026-09{c,d}.parquet`（2.3/0.97 GB）、
`fresh_pool/replays_2026-09e.parquet`（1.5 GB）。
目标：找出顶队比我们多赚 12-20k 是**在哪几天、哪些世界类型、哪些品类**赚到的。
纪律：parquet 一律 `iter_batches` 流式；先镜像/池子/世界类型三口径验证再谈候选。

---

## 14. 新方向第二轮（2026-09-24 更晚）：顶层是"执行赛"，镜像正收益必须过池子

（细节见 [NEW_DIRECTION_20260924.md](farm2945_dev/NEW_DIRECTION_20260924.md) §3.1–3.5）

**一句话**：当前天梯顶层（评分 >2400，也就是我们所在的层）**结构完全同质、
分差中位 ~892**，胜负只由执行差决定；镜像面板上的正收益大多是假阳性，
必须用**同池同种子配对统计**复核。

关键数字（都可复跑）：

* 评分分层典型分差：<1500 → 7,206；1500-2000 → 5,716；2000-2400 → 1,137；
  **>2400 → 892**。赢家-输家结构差（09f 窗口 512 局）≈ 0。
* 赢家领先逐日：`+321(d17) +158(d20) +356(d21) +419(d27) +374(d28) +584(d29)`。
* `t_topup_notom_648`（保留底座卖单、只补卖其他品类）：镜像 **+94**，
  强池配对 **−292 ± 33（t=−8.95）**、公开池 **−165 ± 40（t=−4.15）** → 判负。
* `t_hold_dump`（底座里从未启用的 `hold`+终局清算开关）：镜像 **−85,237**
  （它连买单一起掐、棚容 100 溢出；末段棚存本来 ≈0，机会被物理锁死）。
* 修正：早先"全清臂把番茄提前低价卖"的判断是**错的**——那一层是把底座
  排好的番茄卖单**整段删掉**（番茄 day27 卖 653-707/单位）。
* 底座在强池上**只输给最新一代**：HL 最差 −653、icefire −263；对 v61/v48 从未落后。

**新工具**：`panel_compare.py`（配对差 + SE + t + 置信区间）、
`panel_hard.py`（难例闸：自动取每个对手最差 35% 种子）、
`recent_structure.py`（流式抽 09f parquet 的钱曲线/结构，后台跑 `recent_09f_full.jsonl`）、
`replay_endgame_diff.py`（真实 replay 末段逐 step 双边卖单）、
`top_team_structure.py`、`race_probe.py`、`endgame_trace.py`。

**下次接着做**：
1. 等 `recent_09f_full.jsonl` 跑完（10,030 局），按**配对边际**（而不是绝对钱）
   排出当前窗口的真实强队，逐日对比它们的钱曲线，找它们在哪几天多赚。
2. 任何候选一律走 **镜像 → 强池配对 → 难例闸** 三道；只看镜像的结论不算数。
3. 顶层既然无结构套利，唯一可累积的就是执行差：卖单 slot 顺序、买/卖同一
   step 内的相对位置、以及 day27-29 的尾波（增益最大的窗口）。

---

## 15. 新方向第三轮：真实败局可逐帧复现 + 一个已验证的"黎明现金保险层"

（细节见 [NEW_DIRECTION_20260924.md](farm2945_dev/NEW_DIRECTION_20260924.md) §7）

**新工具 `realworld_panel.py`**：replay 带 `info.seed`，两侧动作流齐全，所以真实天梯对局
可以**逐帧精确复现**。对齐规则（暴力搜索、以市场库存零失配为准）：**引擎第 t 步提交
`steps[t+1].action`，状态对应 `steps[t]`**。

```
--self-test：120 败局 + 161 胜局，世界漂移 0 天，终局分差与录像一致（279/281 精确）
当前底座重打同样世界：−3,303（录像 −3,333）/ +3,549（录像 +3,538）
```

**限制（必读）**：录像 tape 是盲放的。任何改变我们行为的臂都会让世界漂移、对手 tape 失效
（o_archetype 在 24 局里漂移 28 天，名义 +10,766 是假的）。此门只可用于
①诊断 ②小扰动（漂移 0）验证；大改动必须回镜像/池子。

**发现（已验证）**：

* 24 局全败的"克星指纹" `(1053.0, 9989)` 根因是**我们自己的现金缺陷**：
  day1 黎明现金=1、提交 3 个 HIRE、只成交 1 个（对手 3/3）→ day1 少 2 个人手日
  → day2 少 1 只动物 → 滚成 −4,316。源头是底座开局用 ~1,900/3,000 现金囤 43 单位小麦。
* 该缺陷**不是个案**：扫描 281 局真实对局——**40/120 败局（33.3%）**、21/161 胜局（13.0%）
  在 day1 存在"钱不够雇工"，合计 96 / 27 个雇工没成交。
* **修复层 `panel_arms/t_daybreak_cash.py`**（黎明若雇工钱不够，先卖 1–3 单位棚存再雇）：
  - 人为触发对照：`o_buy80 + 修复` vs `o_buy80` = **+10,736.8（12/12 全胜）**；
    未触发的 `o_buy60` 对照 = **+0.0**。
  - 镜像 16 种子 / 强池 4×8 / 公开池 9×8 全部 **+0.0**（逐场相同，零回归）。
  ⇒ **零成本保险**：不触发时完全一致，触发时救回上万；覆盖三分之一的真实败局类型。
* 改开局囤粮量（`panel_arms/rkey/o_buy*.py`、`o_archetype.py`）的扫描：多囤三口全负且单调；
  少囤在公开池上赚（+5,377）但镜像/强池略亏；`o_archetype`（13 单位）镜像 +3,892、
  强池 +3,968，但公开池 −3,733（对 kaito −35.8k，因为低囤粮会让畜群爬坡崩掉：
  day8 动物 7 vs 底座 12）。**没有一只臂三口同时占优**，故未采纳。

**下一步**：把"钱不够"的扫描推广到其它指令类型（BUY_ANIMAL/BUY_SEED/BUY_LAND），
若同样普遍则做一个通用现金守卫层；`t_daybreak_cash` 可作为**待提交候选**（需用户批准提交）。

---

## 16. 新方向第四轮：静默失败全量扫描（已完成）+ 候选定版

（细节见 [NEW_DIRECTION_20260924.md](farm2945_dev/NEW_DIRECTION_20260924.md) §7.6）

`scan_unfunded.py`（对齐已修正：动作取 `steps[t]`、余额取 `steps[t-1]` 观测、按 slot 顺序
模拟现金）扫 281 局真实对局：

| 指令 | 败局 | 胜局 | 缺口 |
|---|---|---|---|
| BUY_PRODUCT | 114/120 (95%) | 158/161 (98%) | 22 / 9，多在 day1 |
| **BUY_ANIMAL** | **28/120 (23.3%)** | **0/161 (0%)** | 36，多在 day3 |
| BUY_SEED | 9/120 (7.5%) | 15/161 (9.3%) | 32 / 3 |
| HIRE（前一轮） | 40/120 (33.3%) | 21/161 (13.0%) | ~2，全在 day1 |

**通用现金守卫**（`panel_arms/t_cash_guard.py`，对 HIRE/BUY_ANIMAL/BUY_SEED/BUY_LAND 都补钱）
vs **专用黎明层**（`panel_arms/t_daybreak_cash.py`，只修 dawn 雇工）：

```
人为触发对照(heavy80+层 vs heavy80): 通用 +6,173.8 (11/12)   专用 +10,736.8 (12/12)
镜像16 / 强池4×8 / 公开池9×8:        通用 +0.0               专用 +0.0
同局遥测:                            通用 触发17次/卖47单位   专用 该种子未触发
```

⇒ **推荐候选 = `panel_arms/t_daybreak_cash.py`**（干扰面最小、对照收益最高、零回归）。
通用层覆盖更广但干扰多、收益低，留作后续；动物类缺口（23% 败局）目前无法活体验证。

**待办（按优先级）**：
1. 用户批准后提交 `t_daybreak_cash`（或其他候选）以获取真实天梯反馈——这是唯一
   能验证"它到底翻回多少胜率"的途径；**未获批准前不得提交**。
2. 继续找同类"静默失败"：棚容上限导致的溢出丢弃、HIRE 之外的 capacity 拒绝等。
3. `recent_09f_full.jsonl`（10,030 局结构/钱曲线）后台仍在完成，可用于按配对边际筛强队。

---

## 17. 新方向第五轮：单位动作浪费扫描（否定）+ 买动物缺口暂挂

（细节见 [NEW_DIRECTION_20260924.md](farm2945_dev/NEW_DIRECTION_20260924.md) §7.8–7.9）

* `scan_waste.py`：逐个单位指令判"是否可能无效果"扫 281 局，再用同规则复查当前底座活体。
  结果：旧版败局特征 `CARE_no_animal`（8.46 vs 1.13 每局）与 `FEED_no_animal`（6.92 vs 0.61）
  **当前底座已基本消除**（活体 2.0 / 0.3，镜像 0）；当前最大浪费 `DIG_no_weed` 17.7/局
  但**败局胜局同频**（17.91 vs 18.19）⇒ 与胜负无关。**单位动作没有新杠杆。**
* 买动物缺口（败局 23.3% / 胜局 0%）构造可控复现失败：缺陷臂在镜像里从不触发
  （day3 现金充足），缺陷+守卫 vs 缺陷 = +0.5。通用守卫虽能覆盖，但在雇工对照里
  干扰大收益低（+6,174 vs 专用 +10,737），**不采纳**。若日后要动，需写专用
  "只在 BUY_ANIMAL 缺钱时补"的层再验证。
* 10k 局全量语料已完成（`recent_09f_full.jsonl`）：强队 vs 大众唯一显著结构差异是
  番茄种植数 5.2 vs 1.7，但**我们底座自己就有 ~3.3**，差距仅约 2 次种植（空间有限）。

**当前唯一待提交候选**：`panel_arms/t_daybreak_cash.py`（黎明雇工现金保险）。
**不得提交，等用户批准。**

---

## 18. 同口径对比表（2026-09-25）：线上提交 vs 本地未提交 vs 新保险层

完整版见 [COMPARISON_20260925.md](farm2945_dev/COMPARISON_20260925.md)。

**线上（Kaggle）**：AM `v57_advmirror.py` **2613.1**（09-22 19:12）；
snh48 **2643.8**（09-22 06:55）；s1sd **2676.0**（近期最高）。
两个 main.py 已在本地字节级校验（AM sha a2d15ffd4a66 / snh48 4c6572a8dd34），
解包在 `panel_arms/live/`（snh48/am_v57/herdfix/d27fix/rz2/ga_default/ga236）。

**本地同口径（底座 = `v54_sweep3_snh48_herdfix_cfg.py`）**：

| 模型 | 镜像 Δ | 强池（底座 +2974） | 公开池（底座 +30817） | 真实 120 败局世界（录像 −3333） |
|---|---|---|---|---|
| snh48 | −7.5 | +2968 | +30830 | −3333（精确） |
| **AM** | **+77.7** | +2997 | +30854 | −3313 |
| herdfix | 0.0 | +2974 | +30817 | −3303 |
| rz2 | +25.2 | +3010 | +30794 | −3281 |
| ga_default / d27fix | 0.0 | +2974 | — | — |
| **t_daybreak_cash / t_cash_guard_plus** | **0.0** | **+2974（0）** | **+30817（0）** | 触发型 |

**新层触发态对照**：daybreak 雇工缺陷 **+10,736.8**(12/12)；guard_plus
雇工 **+6,173.8**(11/12) / 动物 **+11,028.2**(12/12)。

**最重要的一条结论**：**本地面板不能预测天梯分数**——本地最好的 AM（+77.7 镜像）
线上分反而最低（2613.1 < snh48 2643.8 < s1sd 2676.0）。所以任何"本地看起来更强"
都不足以支撑提交决策；而新保险层的下行风险经实测为 0（所有活体口径逐场相同），
上行只能由天梯数据回答。

---

## 19. 候选端到端验证完成（2026-09-25）：28/28 真实缺陷局修复

`t_daybreak_cash`（黎明雇工现金保险）三重验证齐备：

1. **机制（真实世界，最强证据）**：在 120 局真实败局里筛出确实触发 dawn 缺陷的
   **28 局**，只测 day-1 结果（不受后续 tape 漂移影响）：
   `snh48 = 0.96 人` → **`t_daybreak_cash = 3.00 人（满编）`，改善 28 / 持平 0 / 变差 0**。
2. **量级（触发态对照）**：`o_buy80 + 修复` vs `o_buy80` = **+10,736.8（12/12 全胜）**；
   未触发的 `o_buy60` 对照 = +0.0。
3. **下行（活体口径）**：镜像 16 种子 / 强池 4×8 / 公开池 9×8 **全部逐场 0.00**。

第二类缺陷（买动物缺口）用宽松口径筛出 120 局，day3+6 现金 snh48 192 vs
`t_cash_guard_plus` 227（+35），口径太宽**不足以判定**，该层仍列未采纳。

**顺带修掉一个历史 bug**：200 条历史 mined tape 用 `TAPE[step-1]`，而正确对齐是
**K=+1**（第 t 步提交 `steps[t+1]`）。同世界重放 −77,197 → −58,363（3/3 改善），
但 tape 在别人世界里仍废（差 40–60k）——这是当年"198 崩/2 平价"的根因。

**状态：`panel_arms/t_daybreak_cash.py` 是唯一三重验证齐备的候选，等用户批准提交。**

---

## 20. 打包完成 + 一个会让提交白费的 loader bug（2026-09-25）

**提交包已就绪、未提交**：`farm2945_dev/candidate_daybreak_cash.tar.gz`
（tar sha `2babf1c46d70a43d…`，唯一成员 main.py 1,081,331 B，
main sha `c71e21590f5acc3a…`，解包回读一致）。收据见
[SUBMISSION_RECEIPT_DAYBREAK_20260925.md](farm2945_dev/SUBMISSION_RECEIPT_DAYBREAK_20260925.md)。

**抓到一个关键打包 bug**：Kaggle 官方 loader 取"模块里最后一个 callable"；
而 `agent = 包装函数` 是**重绑定已有键**，不会移动到字典末尾 ⇒ 朴素追加的层会被
loader 忽略，实际跑的是底座本体（等于白交一次额度）。
已在 `t_daybreak_cash.py` / `t_cash_guard.py` / `t_cash_guard_plus.py` 末尾补
`agent = globals().pop('agent')` 封印，并**从 tar 解出后**验证：
`loader entrypoint: agent, telemetry=True`，冒烟 719 步正常。
（对照：历史上用官方块 `agent=globals().pop('agent')` 收尾的移植臂本来就正确，
所以那些臂的面板数据仍然有效——面板走的是"按名字取 agent"。）

**封印后复验**：28 局真实缺陷世界仍是 **28/28 满编修复**（0.96 → 3.00 人）。

**抢价扫描（否定）**：后期窗口同 step 同商品的先卖比例——我们 9.6% vs 对手 17.2%，
但**胜局与败局完全相同**（9.6% vs 17.7% / 9.6% vs 16.7%）⇒ 是结构性劣势、
不是胜负判别项，这条线不动。

---

## 21. 最强候选 archplus（开局重排 + 黎明保险层）——两个独立种子块复现

收据：[SUBMISSION_RECEIPT_ARCHPLUS_20260925.md](farm2945_dev/SUBMISSION_RECEIPT_ARCHPLUS_20260925.md)
包：`candidate_archplus.tar.gz`（tar sha `9d2b834b3c1dd6a7…`，
main.py sha `96ac067d5f6be0e5…`，loader 入口校验通过、镜像冒烟对称）

组成：① 开局由 `BUY13+BUY30+SELL30` 改为 `BUY8+SELL8+BUY5+BUY_SEED1`（少囤 30 单位小麦）；
② 黎明现金保险层（买不起 HIRE 时先卖 1–3 单位再雇）。

**新鲜种子（未参与任何调参）两块的胜负**：

| 种子块 | 口径 | 底座 | archplus |
|---|---|---|---|
| 33–56 | 强池 4×24=192 | 174W/18L | **187W/5L** |
| 33–56 | 公开池 9×24=432 | 414W/18L | **427W/5L** |
| 57–80 | 强池 | 170W/22L | **187W/5L** |
| 57–80 | 公开池 | 410W/22L | **427W/5L** |

合计：强池 344W/40L→**374W/10L**；公开池 820W/44L→**854W/10L**。
配对分差：强池 +4,284±599（t=7.15）；难例闸 +3,873±1,212（t=3.19，21好/11差）。

**归因（必须一起看）**：

| 臂 | 强池 | 公开池 |
|---|---|---|
| 底座 | 174W/18L | 414W/18L |
| 只改开局 | 187W/5L | **385W/47L** |
| 开局+保险层 | 187W/5L | **427W/5L** |

⇒ 开局负责"HL 17 负→0 负"，但会让公开池多 42 场败局；保险层把 42 场全救回。
真实缺陷局 28/28 仍被修复（0.96→3.00 人）。

**真实世界重放（120 败局世界）**：名义 +15,059，但 drift 18 天 ⇒ 数值不可信，
只作机制参考（tape 对手被打崩）。**这条不能当作 +15k 的证据。**

**结论**：archplus 是本项目第一个在**独立新种子上复现的胜率提升**（两池各 +30~34 净胜）
且通过难例闸的候选。若只提交一个，建议 archplus 优先于 daybreak-only。
**仍未提交，等用户批准（剩余额度约 2–3 次）。**

### 21.1 机制修正与开局量扫描（同日晚些）

**修正**：底座的实际开局不是"囤 43 单位小麦"。底座自带的 **V9 层**（主文件 3374-3393 行）
把路线 tape 的 `BUY13+BUY30+SELL30`（毛往返 73、净 +5）替换成 `BUY20+SELL15`
（毛往返 35、净 +5），且**只在 tape 开局完全匹配 `V9_OPENING_TAPE` 时才替换**，
否则 `return action  # the tape's opening was changed upstream`。
archplus 改的是路线 tape 的开局 → **V9 守卫放行** → 三者净买量都是 +5，
差别只在**毛往返与 slot 序列**。

**机制（活体逐日验过）**：改动是**对同谱系开局的价格路径压制**：

```
底座 vs HL    : 我方 d0 现金12 / d1 人手3    HL 12 / 3（镜像）
archplus vs HL: 我方 d0 现金13 / d1 人手3    HL  1 / 1 → HL 畜群 d8 8只 vs 我们12只
```

HL 仍按 V9 的 `BUY20+SELL15` 走，在同 slot 价格路径吃亏 → day0 现金 1 → day1 雇工只成 1 个
→ 畜群崩。**与 24 局"全败克星"是同一条缺陷链，只是这次由我们施加**。

**开局量扫描（种子 33–56，两池，单调）**：

| 第三笔买量 | 强池 192 局 | 公开池 432 局 |
|---|---|---|
| **5（archplus）** | **187/5，+7,097** | **427/5，+36,461** |
| 10 | 153/39，+5,493 | 391/41，+34,483 |
| 15 | 115/77，+2,873 | 347/85，+31,886 |
| 20（≈V9 净量） | 88/104，−14 | 320/112，+30,504 |
| 25 | 48/144，−2,437 | 258/174，+27,114 |
| 底座 | 174/18，+2,813 | 414/18，+31,026 |

**风险（写进收据 H 条）**：V9 守卫是作者用 6,648 条录制开局验证过的**自我保护**，
archplus 绕过它换进攻性；对路由器型对手（pubrouter）分差掉 ~19k（仍全胜）。
若天梯有强的非 V9 谱系对手，这是弱点。**下一步可选**：做"step0 小往返 + step1 按对手
市场指纹条件补回保护"的折中版。

### 21.2 中盘线（当晚收尾）：两个注入臂全部灾难性判负

| 臂（archplus 之上） | 强池 33–56（192 局） | 公开池 33–56（432 局） |
|---|---|---|
| archplus（基准） | **187胜5负 / +7,097** | **427胜5负 / +36,461** |
| 中盘饲料预囤（day10–20 黎明补到 30 单位小麦） | **51胜141负 / −9,253** | 227胜205负 / +20,046 |
| 中盘番茄补种（day12–18 每天 ≤2 个 PLANT_WHEAT→TOMATO） | **37胜155负 / −7,046** | 231胜201负 / +21,868 |

结论：**番茄 3.2× 是相关不是杠杆**（与用户"番茄试过多次不顺"一致）；中盘注入会挤掉
tape 的关键市场档位、打断饲料链与工人路由 ⇒ 底座只允许 ①开局交互 ②不改动作的补丁。

新工具留档：`opening_arena.py`（281 条真实对手开局 × 任意候选序列，秒级粗筛；
**不能排序**，完整对局面板才是判据）、`opening_grid.json`（180 序列结果）。

### 21.3 扩展对手池（21 对手 / 408 局 / 新鲜种子 33–44）——决定性确认

把公开对手池从 9 扩到 **21**（新增 14 个来自本地 41 个仓库、冒烟通过的真实 agent；
`pool_big.txt`）：

| 模型 | 胜负 | 聚合 |
|---|---|---|
| 底座 | 385胜23负（94.4%） | +43,858 |
| **archplus** | **405胜3负（99.3%）** | **+46,982** |

**败局结构**：底座 23 场 = DataGuy 9 + danilchil 5 + HL 5 + Wangyh 3 + icefire 1；
**archplus 3 场全部只对 icefire**（−2740/−625/−625）。
⇒ archplus **把"同谱系开局对手"整类败局清零**。

**机制范围实测**：四个大增益对手（DataGuy/danilchil/Wangyh/HL）step0 全部是
`BUY20+SELL15+BUY_SEED1`（同谱系）；pubrouter 是 `BUY13`（不往返）→ 只掉分差不掉胜负；
kaito 空开局 → 无影响；其余 14 个新对手 ±1k 内。

**结论**：archplus 目前证据链=两个原始池独立种子块 + 扩展 21 池 + 难例闸 + 机制逐日可复现。
唯一保留：本地面板不能预测天梯分（AM 教训）；故仍需一次提交换真实反馈。

### 21.4 真实天梯上的机制测量 + 预期收益估算

**天梯对手开局分布（snh48 281 局真实对局）**：

| 对手开局类 | 局数 | 占比 | 我们对它胜率 | 均分差 |
|---|---|---|---|---|
| **V9 谱系（BUY20/SELL15）** | 123 | **43.8%** | **64.2%** | +317 |
| 其他开局 | 152 | 54.1% | 52.6% | +254 |
| 不交易小麦 | 6 | 2.1% | 33.3% | +15,338 |

**在真实 281 世界里只换我们的模型（对手仍为录像，day1 前不漂移）**：

| 类别 | 模型 | 我方 现金/人手 | 对手 现金/人手 |
|---|---|---|---|
| V9 谱系 123 局 | snh48 | 8 / 3.00 | 10 / **2.96** |
| | **archplus** | 9 / 3.00 | **1 / 1.37** |
| 其他 158 局 | snh48 | 6 / **2.64** | 23 / 2.97 |
| | **archplus** | **18 / 3.00** | 17 / 2.97 |

⇒ ① 谱系压制在真实天梯上**照样生效**（对手 day1 人手 2.96→1.37）；
② 保险层把我们在"其他开局"类的 day1 人手从 2.64 补到满编（正是 40/120 败局那类缺陷）。

**预期收益（粗略）**：谱系类 44 场败局；扩展池里同类败局被翻转 **22/22**。
若天梯上只翻转其中一半 → +22 胜 / 281 局 ≈ **+7.8 个百分点的胜率**。
对照：我们当前线上胜率 57.3%（161/281），AM/snh48/s1sd 三个提交的分数差仅 63 分。
**这是本方向最接近"重大突破"的一步**，但翻转率只能由提交换取。


---

## 22. 已提交 archplus（用户批准，2026-09-24 14:56 UTC）

- **ref 56524401** · `candidate_archplus.tar.gz` · 状态 PENDING · 当日剩余额度 4 次
- 收据：[SUBMISSION_RECEIPT_ARCHPLUS_SUBMITTED_20260924.md](farm2945_dev/SUBMISSION_RECEIPT_ARCHPLUS_SUBMITTED_20260924.md)
- 提交时同批次分数：AM 2601.7 / snh48 2633.6 / s1sd 2676.0 / s1s 2590.9
- **盯分**：`watch_submission.py 56524401`（后台，日志 `submission_watch.log`，10 分钟一条）
- **提交后验证工具**：`post_submission_check.py`（对新 replay 输出：黎明雇工缺口比例、
  对手 day0 现金≤2 比例、对手开局类别构成）；已在 snh48 语料校准。

**口径更正（重要）**：修正对齐后，"day1 黎明现金不足导致 HIRE 被拒"是
**28/120 败局、0/161 胜局的完美判别项**（此前 40/120 与 21/161 是错位一步的产物）。
若新败局里该指标归零 → 保险层线上生效；若"对手 day0 现金≤2"的比例显著上升 →
开局压制线上生效。

**提交后继续研究的两条线**：
1. "其他开局"类（占天梯 54%，我们只赢 51.9%）的 day8–15 窗口——差异零散
   （胜者多卖蛋/多卖麦/多建鸡舍），暂无单一杠杆；
2. step1 卖粮实验判负（胜负不变、分差 −293），已排除。

---

## 23. 新方向结项（2026-09-24 深夜）

**目标「开始新方向」完成**。交付物与证据全部落在本机，可直接复跑：

### 23.1 已上线候选 archplus（ref 56524401）
- 包：`farm2945_dev/candidate_archplus.tar.gz`（tar sha `9d2b834b3c1dd6a7…`，
  main.py sha `96ac067d5f6be0e5…`），收据：
  [SUBMISSION_RECEIPT_ARCHPLUS_SUBMITTED_20260924.md](farm2945_dev/SUBMISSION_RECEIPT_ARCHPLUS_SUBMITTED_20260924.md)（300 行，含全部对照数据）
- 两个机制：**谱系开局压制**（开局 `B8/S8/B5`，使 V9 守卫放行，压掉同谱系对手 day0 现金
  10→1、day1 人手 2.96→1.37）+ **黎明现金保险**（真实缺陷局 28/28 满编修复）。
- 本地证据：两个独立种子块 187胜5负×2（强池）/ 427胜5负×2（公开池）；
  扩展 21 对手池 **385胜23负 → 405胜3负**；难例闸 +3,873（t=3.19）；
  200 镜像种子 0 异常、0 局低于 3 万。
- **线上实时**：`games=8, classified=7, W=7, L=0`，分数 600→1466.3 上升中。

### 23.2 极限探索：所有剩余轴全部惰性或负
开局 180 格竞技场 + 7 变体 / 番茄（门槛·启动日·规模）/ 施肥（作物·年龄·起始日）/
底盘 6 开关（单独与全开）/ 中盘注入 / 卖单时序 5 变体 / 单位·容量浪费 / 未喂动物 /
世界类型 —— 每条都有对照数据，**没有第二个可压制的系统性弱点**
（按开局签名分组：仅两类 0% 胜率，其中一类正是我们已采用的 `B8/S8/B5`）。

### 23.3 唯一未解决缺口（留给后续）
私有顶队的"16–27 格番茄经济 + 与主经济解耦的专属劳力" —— 需要重建生产计划
（`V219` 是同类机制的窄版，三个维度均已证明调不动）。本项目评估：从零重写成本过高。

### 23.4 新工具（全部可复用）
`panel_pool.py` / `panel_compare.py` / `panel_hard.py` / `realworld_panel.py`（真实对局逐帧复现，
对齐 K=+1）/ `opening_arena.py`（281 开局 × 任意序列，秒级粗筛）/ `scan_hire.py` /
`scan_unfunded.py` / `scan_waste.py` / `scan_capacity.py` / `scan_race.py` /
`post_submission_check.py` / `watch_submission.py` / `watch_episodes.py`。

## 24. 公开区情报：ALPEREN AYDIN 与 YUSUKE HAYASHI 推进轨迹（2026-09-25）

完整报告：`farm2945_dev/PUBLIC_INTEL_ALPEREN_YHAY81_20260925.md`（含全部数字与复跑命令）。

### 24.1 两句话结论

* **ALPEREN（alperen5252525）**：Ahmed 底盘上的**薄层优化者**，09-13→09-19 五连发全部集中在
  **开仓压力 + 卖单时序**（`_ADV_LOOK` 3→6→8→自适应 8/16/24、卖单队列相邻交换搜索、开仓压力 30→10）。
  他最像样的一次自评就写着队列搜索 **+20.8（CI −19.0…+62.7，含 0）**；他的开仓 `[13,30,30]` 与**我们底座一字不差**。
* **YUSUKE（yhay81）**：**磁带/区块路由学派的开创者**，08-30→09-13 十一篇把"公开历史当策略 + 商店边界切块 +
  边界预算守卫"整条路公开（我们底座的开局谱系就是 0909），09-11 起核心精修转私人（0910 一天 top-30），
  09-13 后公开区停更。他还公开了竞赛机制情报：**每日公开样本的暴露前沿 ≈ 2,700（触发）/ 2,500（安全）**，
  要挤掉强提交在 Kaggle **latest-two 追踪集**里的位置必须交**两个更新的低分提交**。

### 24.2 实测（同池同种子，本次新跑）

强池 = `pool_strong.txt` × seeds 33–56 × 双座位 = 192 局；镜像 = 与底座同种子双座位 48 局。

| arm | 镜像 vs 底座 | 强池 W-L | 均值/局 |
|---|---|---|---|
| 我们底座 | — | 174-18 | +2,813 |
| **archplus（已提交）** | — | **187-5** | **+7,097** |
| alp.market_rhythm（他最强） | **0-24** | 98-94 | −564 |
| alp.first_in_line | 0-24 | 96-96 | −1,250 |
| alp.ready_stock | 0-24 | 92-100 | −1,246 |
| alp.turn_one（pipe-4） | 0-24 | 54-138 | −2,204 |
| alp.metacounter_r1 | 0-24 | 1-191 | −10,084 |

分对手看：他的 agent 对 v61 / v48 能 47-1，但对 HL 是 **2-46**、icefire **2-46**（ready_stock/turn_one 是 0-48）。
cha22 那张"market_rhythm 最难打（83.3%）"的表，只是**在 cha22 的弱底盘上**的相对强度。

### 24.3 移植实验：开仓压力 10 → 确定性 −335/局

臂 `panel_arms/rkey/archplus_wheatpressure.py`（archplus + step1 `BUY WHEAT 10`、step2 `SELL WHEAT 10`，
复刻他在 market_rhythm 里"pressure 10"的做法）：seeds 33–36 镜像 vs archplus，
**4 个种子 × 2 个座位全部 −335（同值 ⇒ 确定性往返亏损）**。
他的收益来自修掉继承 tape 里那条本来就亏的 `SELL 13 + BUY 5`，不是往返本身。

### 24.4 结论

* 两人整条公开线**都不足以做候选臂**（镜像 0-24 全败）；可迁移的是方法：
  同边界区块 A/B、种子簇 bootstrap + worst-rival 选型、等销量败局诊断（先问产销量是否已相同，
  再只在价格/队列位置找因）、硬尾分层（常规/硬尾两桶点率）、暴露前沿公式。
* 明确不做：卖单队列搜索（他自评含 0；我们移植 cha22 抢跑族 187-5 → 187-5 惰性）、
  开仓压力往返（−335/局）、继续挖公开磁带（他本人写的天花板，我们已做到 187-5）。
* 新增留档：`panel_arms/alperen/*.py`（5 支）、`public_intel/yhay81_pull/`（11 篇原件）、
  `alperen_notes/`、`yhay_notes/`、`panel_runs/compare/alp_*.json`（10 份）。
* **本次零 Kaggle 提交，未改动 main.py 与任何现役候选。**

### 24.5 ✅ 项目根的两个危险文件已隔离（2026-09-25，用户授权）

`farm2945_dev/main.py` 与 `farm2945_dev/submission.tar.gz`（解码 ALPEREN notebook 时落错地方）
**已改名隔离**到 `_quarantine_alperen_20260925/farm2945_dev_root/`：
`alperen_market_rhythm.source.py`（sha `f3be6392671608e9a575145c…`）与
`alperen_market_rhythm.archive.tar.gz`（sha `015d1a895533c262…`，包内同一份），移动前后哈希已复核。
项目根现在没有 `main.py` / `submission*`，任何 `**/main.py` glob 都碰不到他的代码。

新增两道闸（打包前必跑）：

```bash
cd /root/autodl-tmp/farm2945_dev && python check_no_alperen.py     # 命中即非零退出
python check_no_alperen.py --scan-dir /root/autodl-tmp             # 全仓 328 个打包位，当前 ✅ clean
```

`panel_arms/alperen/__DO_NOT_SUBMIT.md` 写清来源 sha 与"永不作打包输入"的规则；
完整记录（12 处命中清单、保留项与理由、恢复/彻底清除命令、影响面确认）见
[DELETION_LOG_ALPEREN_20260925.md](farm2945_dev/DELETION_LOG_ALPEREN_20260925.md)。
保留的只有**评测/情报路径**（`panel_arms/alperen/` 5 支研究臂、`onearena/agents/` 3 支对手、
`public_intel/` 原件留档），它们不在任何打包链上（`build_*.py` / `ga_gate.py` / `rz2_gate.py`
都按显式路径组装）。本次**零 Kaggle 提交**。

### 24.6 与他公开资料的交叉验证

* 我们底盘 `Chassis` 的 `budget_guard`（`_block_requirements/_budget_guard`，base 695-760 行）
  就是 yhay81 `six_day_budget_guard.hpp` 的逐行移植（默认开启）；`weed_repair` / `sell_lead` /
  `room_guard` / `clamp_sells` / `dead_stock` / `terminal_liquidation` 同属 fieldbook 那一批层。
  ⇒ **他的公开机制我们已经全部内化**，没有再移植的空间。
* 他 08-30 公开的 C++ 环境（1.32.7，788 行）已被我们自己的 `onearena/kagsim-0.5.0`（968 行，
  快照/分支设计）覆盖；`shopforge-fieldbook-tapes`、`six-day-public-state-agent-source`
  是 09-01/09-02 旧版。他的公开区在 09-13 之后停更。

### 24.7 仓库里已有的 4 局"我们 vs ALPEREN"真实 replay（09-16 前后）

| replay | 我方 step1 开仓 | 他方 step1 开仓 | 终局 |
|---|---|---|---|
| `agent_monitor/replays/episode-109035476` | `BUY 5, BUY 10, SELL 60` | `BUY 13, SELL 13, BUY 13` | 我们 +6,154 |
| `agent_monitor/replays/episode-109139801` | `BUY 5, BUY 10, SELL 60` | `BUY 43, SELL 20, SELL 22` | 我们 +6,902 |
| `.../episode-109460826`、`.../episode-109507881` | `BUY WHEAT 5` | `BUY WHEAT 5` | **逐步完全相同 → 两局全平（104,585 / 68,898）** |

后两局说明：当时他的天梯 agent 与我们的提交**开局行为等价**（同一条公开谱系的分支），
镜像对称世界里直接打出同分；前两局我们的旧翻转开仓对他当时版本两战两胜。

## 25. 2026-09-25 增量：新公开池复测 + 两个负面结论

### 25.1 第 102 轮那条"day27 种子泄漏"开口：已量化 → 噪声（关闭）

工具 `scan_late_seeds.py`（新，只测量不改 agent），seeds 33–48 × 双座位 = 32 局/臂：

| 臂 | 终局剩余种子面值（均值/局） | day27 之后买种花费（均值/局） |
|---|---|---|
| 底座 `v54_sweep3_snh48_herdfix_cfg` | **22.5**（中位 40，最大 40） | 89.4 |
| archplus | **23.8**（中位 40，最大 50） | 80.6 |

剩余的全部是小麦 4–5 粒（≈ 40 币）——占 ~10 万终局现金的 0.02%。
**结论：不值得为它做候选臂；第 102 轮的"待用户点头"项关闭。**

### 25.2 最新公开区（09-22 之后）复测：archplus 仍然全面压制

新拉 3 篇（`public_intel/fresh_0925/`）并解包（`nb_extract_agent.py`，新工具）：
`arsgorynich/herd-safe-v3-experimental-risk-aware-feed`、
`haideptry/the-shepherds-ledger-herd-safe-sovereign`、`hanifnoerrofiq/pioneers-of-kaggle-town-candidate-2`
（后者入口是 `agent(obs,cfg)` 无默认值，已加 `.adapted.py` 适配器），加上已研究的 cha22 组成 `pool_new.txt`。
seeds 33–56 × 4 对手 × 双座 = 192 局：

| 臂 | 战绩 | 均值/局 | 分对手（W-L） |
|---|---|---|---|
| **archplus** | **162-30** | **+5,411** | hanif 48-0(+19,250) / arsgorynich 39-9(+1,143) / **haideptry 31-17(+709)** / cha22 44-4(+541) |
| 底座 | 147-45 | +790 | hanif 33-15(+835) / arsgorynich 39-9(+1,136) / haideptry 31-17(+672) / cha22 44-4(+515) |

⇒ 公开区（含 09-24 的 cha22）没有新东西能威胁 archplus；新批次里最难的是 haideptry 的
Shepherds Ledger（双方都是 31-17）。

### 25.3 "按商店对条件化开局"假设：用现有两种子块直接否掉

把 48 个种子（33–56 与 57–80）按首两商店分类，比较 archplus−底座的净分（4 强对手 × 双座）：
**34 个商店对类别全部为正**，最小 +4,491（PIZZA_SHOP+ICE_CREAM_SHOP），最大 +66,511；
全局净 **+729,151**。

具体看那两个 archplus 对 icefire 的回归种子（44、53：底座各 +1,760/+2,809，archplus −625/−1,042）：
同一世界里 archplus 对 HL 是 **+15,743 / +24,540**（底座只有 +949 / +1,522）——
**回归被同世界的巨大增益覆盖，不存在"回退到旧开局更好"的类别**。
⇒ "按商店对/家族条件化开局"这条路（ALPEREN EXP241 那类）在我们底座上无净收益，关闭。

### 25.4 现在真正剩下的口子

1. **archplus 自己的天梯败局**（watcher `watch_episodes.py 56524401` 在跑）——攒够一二十局后
   用 `collect_recent_losses.py` + 既有扫描器做缺陷分类；这是唯一能带来新候选的活水源。
2. **09g 日更语料**（watcher `georgy_watch_download.py` 在跑）——落地后可做"顶层行为差分"。
3. **重定义门脚本化**（净胜/胜率口径，active goal 的交付物之一）——纯工程，30 分钟可完成。

## 26. archplus 深挖（2026-09-25）：OR2 卖单窗口 48 → 8，两块独立确认

完整报告：`farm2945_dev/CANDIDATE_SNH8_REPORT_20260925.md`。**未提交**。

### 26.1 找到的东西

* `layer_census.py` 普查：archplus 里 **11 个层在 6 个对手 36 局里零触发**（`_CT/_OV/_PG/_ROOM_STATS/
  _SL/_V233/_V92_Q/_VE/_VT/_Y/_v9_racegate`）。逐个读闸门：多数是与 SHEDROOM 同级的冗余，
  唯一有战略含义的是 `_CT`（`(对手现金, 小麦库存) → 反制下单`表，键值陈旧，281 局只命中 1 局）。
* 真实语料（281 局）对手开局族：老底座只输给"同类白手往返"族（`10/10` 族 18 局我们胜率 22%，
  `8/8/5` 族 12 局 0%）；并且 **227/281 局的对手 step-1 现金在 2900–2920，只有 25 局 ≥3000**
  ⇒ archplus 的开局判别器阈值 `_O_DISCRIM_THRESHOLD=2950` **只对 8.9% 的真实对手生效**
  （阈值本身扫 2800/3100 是噪声，要扩展只能换状态键，不是挪阈值）。
* `knob_sweep.py` 扫 30+ 旋钮：**主发现 `_OR2_SN_H` 48 → 8**（OR2 层"把未来计划卖单提前"的窗口）。

### 26.2 主结论（配对，同池同种子双座位）

| 变体 | 33–48（n=128） | 57–80（n=192） |
|---|---|---|
| `_OR2_SN_H=4` | +442 (t=5.3) | +463 (t=7.4) |
| **`_OR2_SN_H=8`** | **+536 (t=7.6)** | **+543 (t=10.4)** |
| `_OR2_SN_H=12` | +322 (t=4.7) | +395 (t=9.2) |
| `_OR2_SN_H=24` | +204 (t=5.1) | +172 (t=5.5) |
| 组合（+CAP20/SLOT12/CA−10/CH95） | +581 | **+598 (t=8.9)，强池 189-3** |

曲线：0:+212 / 4:+442 / 8:+536 / 12:+322 / 16:+237 / 24:+204 / 40:+119 / 48:0
⇒ **提前几回合卖对，提前一两天卖错**；上游把 24 改成 48 是调错方向。

### 26.3 闸门（候选 `snh8_combo`）

| 口径 | archplus | 候选 |
|---|---|---|
| 强池 57–80 | 187-5 / +6,786 | **189-3 / +7,384** |
| 公开池 33–56（432 局） | 427-5 / +36,461 | **431-1 / +36,545** |
| 新公开池 33–56 | 162-30 / +5,411 | **174-18 / +6,140** |
| 镜像 vs 底座 | 23-0-1 / +4,226 | 23-1 / +4,120（唯一负项） |
| 难例闸 | +5,116 (t=3.80) | **+5,229 (t=3.99)** |
| 官方 loader / 官方引擎 | — | sealed `agent`；720 步 DONE/DONE |

### 26.4 产物与未做

* 包：`candidate_snh8.tar.gz`（只改窗口，main.py sha `876d76e707f95195…`）、
  `candidate_snh8_combo.tar.gz`（main.py sha `5a8aadeab21e25a7…`）——**未提交**。
* 新工具：`knob_patch.py` / `knob_sweep.py` / `layer_census.py` / `mock_open_family.py` /
  `corpus_rival_families.py` / `corpus_opening_states.py` / `pack_candidate.py`。
* 未做：9 族对手开局矩阵（工具就绪）、`_OR2_SN_ITEMS` 扩品、把 `_CT` 死表用真实语料重建。

### 26.5 第二轮深挖（同日）：OR2 层榨干 + 全层消融 + 开局带洗单 → `candidate_final`

* **OR2 参数已到局部最优**：以 SN_H=8 为基线扫 17 个变体，最好只有 +11（CAP=16，t=1.9），
  其余平台或负；`_OR2_SN_ITEMS` 加 TOMATO 逐场零差异、加 WHEAT −927；SN 起点推迟 48/96 步逐场零差异
  ⇒ 机制只在 step 24–47 与末段触发。
* **全层消融（20 层）**：**没有一层是净负担**。贡献排序 CA −949(t−5.7) > OR2 −673(t−10.6) >
  CH −293 > HD2 −278 > V9_FERT −220 > V92_P −209 > V9_COURIER −166 > V9_RACE −146 > V9_HERD −99 >
  CS −93 > ORDER −54 > SR −17；`_DB`（黎明保险）+15（面板中性，它本来是为真实天梯缺陷设计的）；
  `_ALT/_CL/_R53/_R70` 与 `_CS_FROM=120`、`_HD2` 边界、`_RACE_HORIZON_ESCALATED/MIRROR` **逐场零差异（死开关）**。
* **新机制：开局带洗单**。真实语料 227/281 局对手 step-1 现金在 2850–2950，现有阈值 2950 完全不管这一段。
  给这一段加 `[BUY 8, SELL 8]` 洗单：**+52/局，32胜0负96平，t=+2.35**；只买不卖 −1447（说明是占槽位而非买麦）。
* **`candidate_final`** = SN_H=8 + CAP16 + SLOT_MARGIN10 + CH_SHED97 + CXD_BUDGET1600 + 开局带洗单：
  * 独立块 57–80：**vs archplus +566/局（t=+10.95，156胜36负，CI +465…+668），强池 189-3**；
    vs 只改窗口版再 +24（t=+3.20，CI +9…+38）。
  * 公开池 431-1 / +36,487；新公开池 174-18 / +6,130；镜像 vs 底座 23-0-1 / +4,112；
    难例闸 +5,286（t=4.03）；官方 loader + 官方引擎 smoke 通过（720 步 DONE/DONE，+6,802）。
  * 包：`candidate_final.tar.gz`（tar sha `90248284b2cd0d16…`，main.py sha `1bcc63041da333fb…`）——**未提交**。
* 新工具：`variant_sweep.py`（常量 + 源码片段 + 整层消融三合一）。报告更新见
  `CANDIDATE_SNH8_REPORT_20260925.md` 附录。

## 27. 状态键反制表 goal（2026-09-25）：K1 无合格桶 → 正常结项（负结论）

完整报告：`farm2945_dev/STATEKEY_COUNTER_REPORT_20260925.md`。**零提交，candidate_final 未改动。**

### 27.1 结论

在候选 `candidate_final` 口径下、用最近一份完整真实天梯语料（281 局 = 120 败 + 161 胜，09-24）
做"活 candidate_final vs 冻结真实对手 tape"的配对面板，**穷举三个键族后没有任何
"局数 ≥25 且胜率 ≤45%" 的桶**（最差有量桶 67.9%–78.1%），故按预注册规则结项。

### 27.2 关键证据

* **键族 A（开局状态）**：step2 的 229/281 局落在同一单元（对手现金 1025–1050、麦价 28、库存 9989），
  该桶胜率 **87.3%**；步号扩到 72–576 后最差有量单元 67.9%。合格桶 0。
* **键族 B（中盘商店×棚存×现金）**：最差 step288 `现金≥3100/PIZZA_SHOP` n=28 → 67.9%。合格桶 0。
* **键族 C（对手生产结构：动物数×作物格数×现金）**：**首次出现真实区分度**——
  step144 对手"动物 2–5"桶胜率 **100%**（n=97，+38,047），"动物 5–8"桶 **78.1%**（n=155，+4,236）。
  合格桶仍为 0，但说明**公开状态能预判谁强，却不能指出可改动点**。
* **灵敏度对照（证明测得出）**：拿 candidate_final 里**已有**的开局带洗单做 A/B，281 局配对
  **+41.6/局（SE 22.3，t=+1.87）**，带内局 +90.6 —— 与活体面板的 +52（t=2.35）一致。
* **败局分布**：47 局败局里 29 局就在那个 87.3% 胜率的主流桶里 —— 胜败共用同一键，公开状态分不开。

### 27.3 为什么这条路在当前 meta 下没有目标

1. 决策点的可观测状态**高度退化**（麦价/库存恒定、现金同桶）：所有人开局做同一件事，残差极小；
2. 真正区分强弱的信号在**产能结构**（键族 C），属生产端差异（几万币量级）；
3. 槽位级反制是**微扰**（几百币量级）——量级上改不动产能差。
   ⇒ "状态键 → 槽位反制"在本 meta 下没有可作用的目标；若继续，应把它改成**分诊**（哪类局该变速），
   而不是反制。

### 27.4 本轮新增资产

* `counter_panel.py`（活 agent vs 冻结真实 tape 的键/胜负采集器，281 局 ≈ 60 秒）
* `corpus_key_table.py`（真实语料键分布统计）
* `rust_sim/`（第三方 **Rust byte-identical 引擎**，已验真：20/20 逐分复现；
  磁带 11.8 局/秒、带 Python agent 1.16 局/秒，均与本机 C++ kagsim 做了同任务对照）
* `panel_runs/counter_k1_*.jsonl`（4 组 × 281 局逐局键与结果）

## 28. 节奏分诊 goal（2026-09-25）：K3′ 未通过 → 负结论结项

完整报告：`farm2945_dev/PACE_TRIAGE_REPORT_20260925.md`。**candidate_final 未改动，零提交。**

* **K1′ 键**（发现语料 281 局，活 candidate_final vs 冻结真实 tape）：合格键 6 个，
  最强是**第 12 天现金差 ≤0 → 68.4% vs ≥1500 → 96.6%（+28.2pp）**；第 6 天现金差 ≤0 → 74.3% vs 90.4%。
  活体面板赢率饱和（99%+），但**分数差**维度分离明确（第 6 天现金差 ≤0：强池 +4,040 vs +11,293；
  均衡池 +2,404 vs +32,507）。
* **K2′ 档位**：`_OR2_SN_H` 拉大（"更早卖"）在弱桶就是负的（−95/−99）；**`_ER_FROM` 528→480 在发现语料上
  弱桶 +15（t=2.19）**，条件臂 `triage_v1` = 第 6 天现金差 ≤0 才切 → 弱桶 +15.0、未触发局逐场 0、全语料 +6.1。
  （修掉一个真 bug：gear 状态必须每局 step 0 重置，否则同进程跨局泄漏，条件臂会退化成"只第一局生效"。）
* **K3′ 未通过**：独立 replay 语料 817 局 → 弱桶 **−0.7（t=−0.12，改变 124 局）**；
  活体强池 81–100 → +27.7（t=+1.86，未达 ≥2）；活体镜像 81–100 → −29（t=−0.91）。
  **高功效判决（2,567 局 = 817 真实 + 1,750 合成世界，SE 5.4→1.2）：弱桶 −2.7（t=−0.77），
  实际改动的 411 局 −5.9（t=−0.77）⇒ 真效应 ≈ 0。**
* **教训（重要）**：n≈114 的弱桶上挑出 +15（t=2.19）是**选择偏置**；放大到 2,567 局即归零。
  今后任何"时机/微扰"类假设都应用 `counter_panel.py --extra-seeds N` 做高功效判决，再谈入候选。
* 新增资产：`pace_key_panel.py`（活体面板采集节奏键）、`make_gear_arm.py`（档位臂生成器 + 每局重置）、
  `counter_panel.py --extra-seeds`（tape × 新种子的高功效判决，SE 可压到 ~1）。

## 29. AM 全量语料已拉回（2026-09-25，用户点名）

`candidate_am.tar.gz`（= `v57_advmirror.py`，线上 ref **56472390**，分数 ~2601.7）的**全部胜局+败局**：

| 项 | 值 |
|---|---|
| 语料目录 | `/root/autodl-tmp/am_all_20260925/`（260 个 replay） |
| 清单/元数据 | `/root/autodl-tmp/am_all_20260925_manifest.json`（含对手 sub/team/评分前后变化） |
| 统计 | `/root/autodl-tmp/am_all_20260925_stats.json`（EpisodeService 原始 listing） |
| 规模 | **260 局 = 153 胜 / 107 负**，0 归类错配；8.57 GB |
| 对手 | **236 个不同 submission**（最大交手次数仅 4 局——没有单一冤家） |
| 对手评分 | 中位 2585 / 均值 2497 / 区间 624–2757 |
| 分层胜率 | <2500：80.9%（n=47，+8,512）· 2500–2650：**60.1%**（n=173，−151）· 2650–2750：**28.2%**（n=39，−1,507）· ≥2750：0%（n=1） |
| 最惨 5 局 | −15,806（对手 2604）、−11,831（2757）、−10,982（2726）、−8,802（2638）、−7,807（2719） |

工具：`pull_all_episodes.py`（通用：任意 submission 的全量胜败拉取 + 复用本地语料 + 429 退避重试）。
旧的四份 `am_losses_*`（共 138 文件）是它的子集。

## 30. 已提交 candidate_final（用户批准，2026-09-24 19:38 UTC）

- **ref `56530265`**，`candidate_final.tar.gz`（tar sha `90248284b2cd0d16…`，main.py sha `1bcc63041da333fb…`），
  状态 PENDING；收据：`SUBMISSION_RECEIPT_CANDIDATE_FINAL_20260925.md`。提交后今日剩 3 次额度。
- 同批次线上分：**archplus 56524401 = 2672.6**（已 COMPLETE）· s1sd 2676.0 · snh48 2633.6 · AM 2602.0。
- 相对 archplus 的本地证据：强池独立块 189-3 / **+598/局（t=+10.95，CI +466…+729）**；
  公开池 431-1；新公开池 174-18；难例闸 +5,286。**唯一负项**：自博弈镜像 vs archplus −289（6/16/2）。
- 提交后流程：① 用户盯分；② `pull_all_episodes.py --submission 56530265` 拉全量胜败；
  ③ 任何新机制先用 `counter_panel.py --extra-seeds` 做 2,000+ 局高功效判决（本轮教训）。

## 31. AM 金矿 goal（2026-09-25）：H1/G2/G4 完成，G3 杠杆全负 → 未孵化出更强候选

完整报告：`farm2945_dev/AM_GOLDMINE_REPORT_20260925.md`。**candidate_final 未改动；零提交**
（用户指示"先别管线上"，方向 4 暂缓）。

### 31.1 H1 基准（新工具，长期复用）

`am_revival_bench.py`：活候选 vs 冻结真实对手 tape。**candidate_final = 77/107（72.0%，+15,334）**、
archplus = 71/107（66.4%）——两者在 AM 矿脉上统计打平（配对 −176.6/局，t=−0.50），
而在强池上 candidate_final 领先 +598/局 ⇒ **两个指标衡量不同能力，AM 基准是唯一非饱和的真实指标**。

### 31.2 G2 解剖：仍输的 30 局

* 4 局结构性大败**不同类**：Fourth Quadrant（对手 4 象限/88 株）、Ryo Hasegawa（20–21 动物）、
  Yannick Schiffner 与 akmr（**结构与我们完全同形**）。
* 全量特征（30 翻不动 vs 77 能翻，σ）：**我们早期领先 +2,131 vs +530**（−0.86σ）、
  对手施肥 128.8 vs 113.1、对手 rating 2638 vs 2588、对手 day18 卖出 1,308 vs 793、对手买入 1,041 vs 439；
  **我们自己的卖出量 234 vs 228（几乎无差）** ⇒ **不是我们卖得少，是对手产得多/买得多**。

### 31.3 G4 画像：高分段对手与我们结构同形，差别在投入强度

2650–2750 段（n=39）：双方 day12 结构**完全同形**（53/17/3），对手施肥 127.6 vs 我们 116.3。
按对手特征分桶的我们胜率：对手买入 300–600 → **32.4%**；对手施肥 160+ → **0/6**。

### 31.4 G3 杠杆搜寻：45 变体全负

| 家族 | 变体 | 最好 |
|---|---|---|
| 现有旋钮 | 20 | 77/107（并列） |
| 时序档（ER/pace） | 5 | 77/107（并列） |
| 施肥轴 | 5 | 77/107（并列）；age2-only 71 |
| 强制路线 | 11 | 6–15/107（灾难） |
| 注入式生产杠杆 | 4 | **从未触发** |

注入失败是**结构性**的：day8 我们现金只有 **521–721**（买地 4,000）→ 没钱扩张；
day10 现金够但**市场 10 槽已满** → 没槽位加单。且**13 条路线 day12 结构完全同形（53/17/3）**
⇒ 我们的路线库根本没有"大作物经济"计划，调参到不了对手的 85 株/4 象限。

### 31.5 结论与下一步

差距在**生产端**（对手高投入→高产出→高换手），而我们**现金紧 + 槽位满 + 无扩张型路线**。
要孵化更强候选，唯一有理论增益的方向是**生产端重写**（把 day12 结构从 53/17/3 提到 ~75+/4 象限，
并配资金流），需单独 goal。**AM 复活赛基准保留为验收闸（不得低于 77/107）**。

### 31.6 全 107 局 bit-exact 三通道（残差 max 0.0）

| 通道 | 判别力 σ | 读法 |
|---|---|---|
| sell_d（对手卖出收入 − 我们） | **+0.69** | 翻不动的局里对手卖得更多 |
| buy_d（对手买入支出 − 我们） | **−0.67** | 同一批局里对手买得更多 |
| fixed_d（雇工/种子/动物/地） | −0.14 | **无判别力**（不是我们乱花钱） |
| money_d | +0.29 | — |

⇒ 机制链闭合：**对手是"多买→多产→多卖"的高换手经济**（且 day12 结构与评分段无关地与我们同形 53/17/3），
而我们**现金紧（day8 仅 521–721）+ 槽位满（day10 已 10 单）+ 路线库无扩张型计划**。
杠杆清单（45 变体、含注入式）已在 §31.4 全部判负——**在当前架构内无法孵化更强候选**；
唯一出路是生产端重写（新 goal）。**candidate_final 未改动，零提交。**

### 31.7 产量账本与小麦流（第三轮，同日）：产量相同，差别在"市场流"

* **产量账本（107 局，`am_yield.py`）**：翻不动组里双方**收获单位 1,393 vs 1,430（几乎相同）**、
  WATER/FEED/CARE/PLANT/HARVEST 次数全部几乎相等、动物日/作物日也相同；
  但**卖单量 2,176 vs 3,719（对手 +71%）**（能翻组只差 +18%）。
* **逐商品（`am_item_flow.py`）**：差额集中在 **WHEAT**（卖 923/1,290、买 405/894、收 520/533）与
  FERTILIZER（买 77/147）；其余 7 品几乎完全相等。
* **小麦流能否利用？两个检验都否**：
  ① 纸面回测（买低卖高，4 组阈值）最好 +62/局、**中位 0 笔成交**；
  ② 择时检验：双方买入价分位 0.31 vs 0.32、卖出价分位 0.49 vs 0.50（**择时完全相同**），
  对手只是**单量 $\sim$2.3×**。
  ⇒ "小麦换手"作为杠杆判负（市场有效，无可复制规则）。
* 累计判负清单：现有旋钮 20 + 时序档 5 + 施肥轴 5 + 强制路线 11 + 注入式 4 + 小麦流 2 套检验 = **47 项**。

### 31.8 组合搜索终局（同日第四轮）：57 项无一超过基线 → 判定阻塞

对"小正项"做系统组合（CAP 16/20/24 × SLOT 6/10/12 × CH 92/95/97 × CXD1600 × band on/off × ER480 × mirror24，10 组）：
**全部 77/107**，均值 +15,327…+15,341（基线 +15,334）⇒ **组合空间饱和，无交互增益**。

**Goal 判定 blocked**（同一障碍连续三轮：当前架构内无任何杠杆能超过 77/107）。
解开条件（二选一，均需用户决定）：

1. **下"生产端重写"新 goal**：把 day12 结构从 53/17/3 提到 ~75+/4 象限并配套资金流（唯一有理论增益的方向）；
2. **放开线上数据**（用户此前指示"先别管线上"）：用 `candidate_final`（ref 56530265）的真实败局找新缺陷类——
   历史上两次真正提分（黎明现金保险、开局谱系压制）都出自真实败局，而当前它只有 6 局记录。

产出：`AM_GOLDMINE_REPORT_20260925.md`（含完整 57 项判负表与 bit-exact 三通道）；**candidate_final 未改动、零提交**。

## 32. 生产端重写 goal（2026-09-25）：**前提被数据推翻**，建议改写

审计文件：`farm2945_dev/PRODUCTION_REWRITE_PREMISE_AUDIT.md`。**candidate_final 未改动、零提交。**

* **配对结构对照（n=260，同局同状态）**：day6/12/18/24 的"我们 − 对手"株差**中位全为 0**，
  三项（株/动物/象限）完全相同比例 **94% / 92% / 91% / 88%**；"对手株≥70"的局：
  day12 **1/260**、day18 1/260、day24 2/260（唯一那局就是 ep112558636 的 Fourth Quadrant）。
* 按首个商店分层（8 类，各类 n=24–43）：**双方 day12 结构全是 53/17/3**。
* "翻不动的 30 局"里：对手株≥70 只有 **1/30**、4 象限 **2/30**、双方结构三项全等 **24/30**、株差中位 **0**。
* ⇒ **M2 目标（≥70 株/4 象限）是一个孤例，不是赢家特征**；goal 的前提不成立。
* **顺带修正两个测量错误**（此前报告中已标注）：
  ① "对手卖单 +71%"是伪差（shed-delta 口径把 PICKUP 当卖出）；修正口径（执行量×当步价）后，
  僵局对手收入差 +27,537（能翻 +5,525），其中小麦近中性换手（+452 卖 / +487 买）。
  ② "小麦往返套利"两种规则纸面全亏（绝对阈值最好 +62/局；相对规则 −89…−277/局）。
* 建议：① 把 goal 改为**末期变现/执行差**（唯一可定位的通道）；或 ② 判 AM 矿脉已挖尽、
  放开线上数据找新缺陷类；或 ③ 若要重写生产端，先给出证据支持的目标结构。

## 33. 生产端重写 M1/M2（2026-09-25）：象限达标、株数不可达；判需要"无界重写"

报告：`farm2945_dev/EXPANSION_M1_M2_REPORT.md`。**candidate_final 未改动、零提交。**

* **窗口实测**：day10 h0 现金 2,732 / 槽满 → **day10 h12（step252）现金 10,750、8/8 有空槽** →
  day11 h0 现金 16,352。磁带原计划 day11 买第 3、day20+ 买第 4 象限。
* **`early_land`（day10/11 中午各注入一次 BUY_LAND）**：每局触发 2 次（现金 10.8k/14.9k），
  **day12 象限 3 → 4 ✅**，但站立株数不变（53→53）。
* **`expansion_v1`（小麦补种）**：买种 146/局、补种 15/局 → 株数 +1…+3（小麦 2 天就割，站立数不涨）。
* **`expansion_v2`（甜瓜补种）**：买瓜种 40/局、补种 8.7/局 → +0…+3（空闲工人很少站在新地空格上）。
* **`expansion_v3`（+走路规划）**：补种 41/局，但**占用磁带未来的格子与瓜种** → 磁带 PLANT 失败，
  **站立株数掉到 35–46（比基线 52–53 更差）**。
* ⇒ **M2 判据**：象限半边达成、株数半边（≥70）在现有架构内不可达——瓶颈是**协调劳动/种子/地块的分配**，
  需要完整农场调度器（= 无界重写）。结合上一轮"该结构 1/260 且非赢家特征"，
  **本 goal 的目标值双重不成立**（既无证据支持、也不可达）。
* 建议：改写为"末期变现/执行差"或放开线上数据；否则本 goal 无解。

### 33.1 AM 靶场全量复核（107 局）：四个扩张臂全部更差

| 臂 | 翻盘 | 均值 | Δ vs 基线（77/107，+15,334） |
|---|---|---|---|
| `early_land`（达成 day12 4 象限） | 67/107 | +9,852 | **−5,483/局（t=−4.79），翻盘净 −10** |
| `expansion_v1` | 56/107 | +7,631 | −7,703/局 |
| `expansion_v2` | 54/107 | +2,184 | −13,150/局 |
| `expansion_v3` | **0/107** | −62,042 | 灾难 |

⇒ **提前买地在数据上是有害操作**（抽走现金饿死磁带计划，新象限无人耕种）。
结合 §32（该结构 1/260、非赢家特征），**本 goal 的目标值被双重否定：既无证据支持，也实测有害**。
唯一未尝试的是"完整协调式农场调度器"（= 无界重写，项目此前评估成本过高）。

### 33.2 第五个设计 v4（专属工人）也失败 → 判定 blocked

`expansion_v4` = 提前买地 + **多雇 3 个专属工人**（磁带只寻址其预期工人数，多余由 `hand_align` 填 PASS）
+ 只种最新象限 + 自带瓜种储备：

| 指标 | 结果 |
|---|---|
| day12 结构 | (42–52, 4 象限) ——象限达标，株数仍低于基线 |
| 专属工人产出（10 局） | 种 9 / 浇 10 / 收 0 |
| AM 靶场 107 局 | **36/107（33.6%），均值 −6,935** |
| 配对差 | **−22,269/局（SE 1,306，t=−17.05），翻盘净 −41** |

**六个扩张设计汇总（AM 靶场 107 局）**：

| 臂 | 翻盘 | Δ 均值/局 vs 基线 |
|---|---|---|
| `early_land` | 67/107 | −5,483 |
| `expansion_v1` | 56/107 | −7,703 |
| `expansion_v2` | 54/107 | −13,150 |
| `expansion_v3` | 0/107 | −77,376 |
| `expansion_v4` | 36/107 | −22,269（t=−17.05） |

⇒ **干预越深、损失越大**；磁带计划的 53/17/3 是当前资源包络下的局部最优。
**Goal 判定 blocked**（同一障碍连续三轮：目标结构 1/260 非赢家特征 + 六种有界达成方式全部有害）。
解开条件：① 授权无界"协调式农场调度器"（先给成本/里程碑估计）；② 改写 goal 为末期变现/执行差；
③ 放开线上数据找新缺陷类。**candidate_final 未改动、零提交。**

## 34. 生产端重写（用户授权"1"=无界重写）：协调式调度器 → 中止规则触发（负结论）

报告：`farm2945_dev/FARM_SCHEDULER_REPORT.md`。**candidate_final 未改动、零提交。**

* **S1 装置**（`farm_sched.py`：磁带管市场单 + 调度器管工人）跑通；首版调度器不完整
  （不会 PICKUP/BUILD/PLACE）→ day12 (12–17 株, 0 动物)，现金 7–12k vs 磁带 70–90k。
* **S2 完整流水线**（`farm_sched2.py`：喂/护/收肥/收获/窗口浇水/种植/入棚/取货/建造/安置 + 目标格预留）
  三次迭代：

| 迭代 | day12 结构 | 现金 |
|---|---|---|
| S2a 完整 v1 | (12–17, 0, 2) | 8–12k |
| **S2b 目标格预留 + 动物链** | **(20–26, 0–1, 2)** ← 最好 | 10–18k |
| S2c 窗口浇水 | (0, 0, 1) | 0（回归） |
| S2d 喂食货流修复 | (0, 0, 1) | 0（未恢复） |

* **工人动作普查（整局）**：`PASS 1424 | 移动 121 | PLANT 24 | FEED 63 | CARE 11 | PLACE 7 | BUILD 5 | PICKUP 8 | DROP 3`
  ⇒ **84% 回合在发呆**，同期任务累计 PLANT 412 / FEED 275 / CARE 186 —— 贪心分配与动物/搬运链互相饿死。
* **预注册中止规则**（S2 三次迭代达不到纯磁带 80% 结构 = 42 株）**触发**：
  最好迭代仅 20–26 株（≈40%）、现金损失 ~85%。
* ⇒ **生产端重写在本项目内三路全灭**：① 目标无证据（1/260、非赢家特征）；② 强行达成有害（六臂全负）；
  ③ 无界重写不可达（调度器远不及手工磁带编排）。
* 建议：① 改写 goal 为"末期变现/执行差"；或 ② 放开线上数据找新缺陷类（历史两次提分都出自真实败局）。
并配资金流），需单独 goal。**AM 复活赛基准保留为验收闸（不得低于 77/107）**。

## 35. 末期账本 + 变现/执行差修正层（goal 第一轮，2026-09-25）：21 个新机制臂全负 → 期末变现线穷尽

报告：`farm2945_dev/ENDGAME_LEDGER_REPORT_20260925.md`。**candidate_final 只读未动、零提交。**

### 新仪器（可复用）
* `farm2945_dev/am_flowledger.py`：**官方引擎打桩账本**（`_commit_unit`/`_do_hire`/`_do_buy_land`/
  `_drop_inventories_to_shed`），产出每（天×玩家×商品）真实成交卖出单位/现金、BUY_PRODUCT 花费、
  固定花费、日界溢出销毁、终局携带、每（天×小时×商品）成交与槽位。**107/107 与 kagsim 逐分一致**，
  单轮 ~90 s/12 进程。数据：`panel_runs/am_flowledger_{items,v2,v3}.json`。
* `panel_arms/endgame/`（e2_*、e3_*、e4_*、e5_*、e6_*、cxd0/cxd8k/cxd_late）+ 生成器
  `make_endgame_arm.py` / `make_terminal_arm.py` / `make_e4_arm.py`。

### 30 局败局精确拆解（每局均值 $）
* 分带：d0–9 **+260**、d10–17 −369、d18–23 −293、**d24–29 −1,847**，合计 **−2,249**。
* 商品（全季/d24–29）：STRAWBERRY **−1,697/−952**、TOMATO −535/−350、WHEAT −338/−346、
  WOOL −308/−286、EGG −189/−61、MILK −25/−167、CARROT +166/+418、FERTILIZER +464/+98、FIXED +264/−112。
* **量不是问题**：我方 1,854 单位 vs 对手 2,394，差额全部是小麦往返（+473 单位 @ +0.4/单位）；
  非小麦商品数量几乎相同 ⇒ 差距是**单价/执行**。
* **价格差随胜负变号**（败局我们末期 STRAWBERRY 58.5 vs 83.3；胜局 WOOL 144.3 vs 98.4）
  ⇒ 是镜像竞速结果，不是系统性劣势；争议回合槽位我们领先 51 / 落后 41（不输排队）。
* 修正旧读数：录制局 713–718"65 vs 382 单位"是**申报量**；真实成交 178–207 vs 177–181。
  录制局末期**报价**按小时全平（WHEAT 全天 40）⇒ 无日内套利。

### 机制臂（AM 107 败局，配对）
递延 e2_a…f（+34/+23/+38/**+126**/−209/+2，翻转 74/76/74/76/73/75）· 终局打捞 e3_a=**逐位相同**
（底座最后可执行回合已经 PLACE+SELL 携带货）、e3_b=−243（t=−18.1）· 末期持有 e4_a…d（−28/−44/−42/+32，
翻转 74/74/75/77）· 末日囤货 e5_a/b（−463/−146）、囤草莓到终局 e6_a/b（−415/−415，翻转 69）。
CXD：关掉 −49、8000 −5、只末期 −8（CXD ≈ +50/局，小）· 日界清仓 e7_a/b（−18/−3，77 翻转，溢出量不变）。
**21 臂全部未过门（≥82/107 或配对 ≥+300/局 t≥2）**。

### 结论
"day18 后失血"= 近镜像竞速而非可修 bug；末期变现这一维（更早/更晚/分批/囤货/打捞/槽位）**两侧都已到局部最优**。
25/30 是 ±2,000 内薄局（中位 −764）；剩 5 局大败各有独立成因（ep112558636 对手 88 株大作物经济、
ep112871860 对手末日 72 单位 STRAWBERRY @207 = $14.9k 抛售 —— 但 e6 证明我们照做更差）。
**建议下一轮换失效模式**：(a) 5 局大败的对手类型；(b) 线上真实败局（需用户放行）。

## 36. 末期递延层（同一 goal 续轮，2026-09-25）：找到真实机制，G2 差一点 → 未判完成

报告：`farm2945_dev/ENDGAME_LEDGER_REPORT_20260925.md` 第二段。**零提交；candidate_final 只读。**

### 机制（`panel_arms/endgame/e2d_*.py`，生成器 `make_endgame_arm.py` 已加 ramp 旋钮）
末期（默认 d20=480 起）对**价格 < floor×base（深过剩）**的商品：每回合挂卖量压到
`cap` 以内、最多持有 `hold` 单位、超过 `horizon` 步滚动释放、d28–29 强制清仓。
只改市场单**数量**（不动槽位、不动工人动作、不新增槽位）。

### 结果（AM 107 败局靶场，配对同种子）
* **最好翻转 81/107**（+5/−2）：e2d_v 456/5/0.70/30/18（Δ **+292**/局 t=+4.43）、
  e2d_t 456/6/0.75/30/18（+268 t=+4.77）、e2d_j3 480/5/0.75/30/18（+220 t=+3.99）。
* **池最安全**：e2d_i 480/6/0.60/20/18 → AM 78/107、+208/局 t=+4.18。
* 高功效（107 tape × 9 seed = 963 局）：e2d_i **+111.5 t=+7.87**、e2d_t +111.2 t=+7.23、
  e2d_v +137.9 t=+7.96（胜率 95.1–95.4% vs 94.9%）。
* 留出半（e2d_v）：奇 +328 / 偶 +262，同号。
* 四池（强192/公开432/新192，判据 −100）：**只有 e2d_i 全过**（−26.5 / +29.8 / −1.0，加权 +9.3）；
  e2d_t 新池 −100.2（压线失败）、e2d_v 强池 −147、e2d_j3 强池 −170。
* 官方引擎冒烟：`candidate_e2d_i.tar.gz`（main.py sha256 `5b34aeea…`）720 步双席位 DONE/DONE。

### 判定
预注册门 **G2 未过**（81<82；+292<+300）→ **goal 不判完成**；G3/G4(e2d_i)/G5 过。
机制存在**单调权衡**：越激进 → AM 越强 → 强池/新池越差。
下一步：在 e2d_i↔e2d_t 之间搜"≥82 或 ≥+300 且三池 ≥−100"的配置并按 G3/G4 复验。

### 36b. 补充（同日）：全 260 局 + 留出胜局语料 + 两个包
* **153 局胜局语料从未参与调参**（留出）：e2d_i 145/153 vs base 142/153（+3，Δ+48 t=1.47）；
  e2d_t 144/153（+2，Δ+45）。
* **全 AM 260 局**：e2d_i 223/260 (85.8%) vs base 219/260 (84.2%)，**+114/局**；
  e2d_t 225/260 (86.5%)，**+137/局**。与高功效 963 局（+112/+111）同号同量级。
* 产物（未提交）：`candidate_e2d_i.tar.gz`（tar `7f92a62e…`）、`candidate_e2d_t.tar.gz`（tar `005138b2…`）；
  官方引擎 720 步双席位 DONE/DONE（e2d_i 已冒烟）。
* 结论不变：**G2 未过**（81<82、+292<+300）→ goal 保持 active；机制已被两条独立证据链验证。

### 36c. 结论（同日第三轮）：**goal 达标** —— `candidate_e2d_t_v224off`
* 配置：`panel_arms/endgame/e2d_t_v224off.py` = candidate_final + **末期递延层**
  （step 456–690；价格 < 0.75×基准价时每回合挂卖 ≤6、持有 ≤30、18 步滚动释放、d28–29 清仓；
  只改市场单数量）+ **关停 V224 sales-first 重排**（step≥144）。
* **G2 过**：AM 败局靶场 **83/107（77.6%）vs 77/107**，+228/局（t=+3.89）；奇 +285／偶 +180 同号。
* **G3 过**：高功效 2,247 局（107 对手 × 21 种子）**+84.4/局 t=+7.89、+14 净胜**。
* **G4 过**：强池块1 −91.9、**强池块2 +28.1**、公开池 −16.6、新公开池 −70.0、难例闸 +13（均 ≥ −100）。
* 额外留出证据：AM 153 胜局语料（调参未看过）145/153 vs 142/153；AM 全 260 局 **228/260=87.7% vs 219/260=84.2%**，+123.7/局。
* 产物（**未提交**）：`candidate_e2d_t_v224off.tar.gz` tar `1a9666ef…` / main.py `8c5bc24c…`；
  官方引擎 720 步双席位 DONE/DONE。收据：`CANDIDATE_E2D_RECEIPT_20260925.md`。
* `candidate_final.tar.gz`（`90248284b2cd0d16…`）与全部已提交产物只读未动；本会话 0 次 Kaggle 调用。

### 36d. AM 败局极限搜索（同日第三轮，170 臂口径）：天花板 83/107
* 在"V224-off + 递延"骨架上继续加码：家族参数 40 组 + 按品分参 4 组 + 趋势门 3 组 +
  价格触发释放 2 组 + 历史消融叠加 8 组 + 旧旋钮叠加 4 组（OR2_SN_H/CXD）+ 小麦层叠加 2 组。
* **上限 = 83/107（77.6%），14 个配置并列**；最好均值为 81 档的 +292/局。
  最好边距的 83 档配置：`panel_arms/endgame/v_off_p3.py`（草莓 floor 0.55，Δ+248.9 t=4.07）。
* 剩余 24 局 = **4 局结构大败**（对手 day12 88/12/4、38/20/3，缺口 −4.8k~−14.9k，市场层够不到）
  + **20 局薄局**（中位 −832；本层救回 8 局、误伤 8 局，净收益已近该维度上限）。
* 已打包候选不变：`candidate_e2d_t_v224off.tar.gz`（83/107、+228/局、三池 ≤ −92、官方冒烟通过）。
  想突破 83 需换维度：生产端（已判负）或新的市场机制（CXD/OR2/前端搭载已饱和）。

## 37. 多样性筛选（方向 ③ 前置，2026-09-25）：本地无异族威胁
报告：`farm2945_dev/DIVERSITY_SCREEN_REPORT_20260925.md` · 池：`farm2945_dev/pool_diverse.txt`
* 流程：7,265 py → 6,208 唯一 → 505 自包含 agent（`scan2.py`+`play_one.py`，子进程硬超时）
  → 抽样 221：可跑 144、真种地 75、**结构不同族 70** → 按 (株,动物) 去重 **24 家 / 42 原型**。
* 原型：57–62 株作物大户、4–11 动物轻畜群、14–17 动物重畜群；但它们 d12 现金仅 700–12,700
  （我们 13,400–19,300）⇒ **全部远弱**。
* 实测（24 家 × 3 种子 × 双座位 = 138 局）：`candidate_final` **138–0 / +68,038**；
  `candidate_e2d_t_v224off` **138–0 / +68,082**；配对 **+43.3/局 t=+0.97（中性）**
  ⇒ 新末期层的代价只出现在**自家血统镜像**对手上，对异族不赔。
* 修正自己仪器 bug：`family_features.py`/`play_one.py` 曾两侧都读 `farms[0]`（假"全同"）；
  修复后 harvestledger(12.8 动物/50.9 株) 与 hanif-pioneers(13.2/49.9) 确属异族，但被 +19k 带走。
* 结论：③ 的靶子只能在**线上真实对手**里；本地这条线到此为止（等用户解锁线上样本）。

## 38. 新长期 goal 第一轮（2026-09-25）：线上取证 + 5 个假设检验，e2d 家族被证明"1:1 兑换"
报告：`farm2945_dev/LIVE_FORENSICS_REPORT_20260925.md` · 语料：`live_56530265_losses`(41)+`live_56524401_losses`(45)
* **G1 基线**：`candidate_final` 线上 86 败局 = **10/86（11.6%）**，均值 −2,955（56530265 组 0/41！自洽回调）。
* **缺陷定位**：末期 d18–29 独占全部缺口（−3,168 / 总 −2,956）；逐商品 TOMATO +1,093、WOOL +772、
  STRAWBERRY +400、EGG +272、MELON +269；**草莓/羊毛/奶销量几乎相同、差在单价**；番茄是量差（我们 d18–23 卖 0）。
* **排除项**（带数字）：劳动强度差<2%、作物配比相同（53.0/17.3 vs 53.4/17.5）、固定项相同、
  "对手大账本"是**申报量截断伪影**（真实买卖只差 5%）。
* **假设检验**：H1 末期小麦账本 −229/−648/−85 **判负**；H2 e2d 族在线上 +99/+78/+139/+33；
  H3 三品超可加（仅奶+48、仅羊毛+69，合起来+139）；H4 强池代价 奶−15/羊毛−78/合计−147，**v48 一家 −310**；
  H5 克隆门控 **判负**（线上增益被杀到 +49，强池仅修到 −115）。
* **前沿（核心负结论）**：线上增益与强池代价近似 **1:1**（+149↔−144、+139↔−147、+99↔−27、+78↔−56）
  ⇒ G4 的 −100 上限把线上增益锁在 +100~110，**够不到 G2a 的 +150**。e2d 家族无法同时过 G2a+G4。
* **下一批假设**：① 末期番茄/蛋的"量"缺口（生产/留存配比）② 对 v48 型镜像**反向提前卖**（`_v44y_reorder` 叠加）
  ③ MELON/EGG 末期定向留存。

### 38b. goal 第二轮（2026-09-25）：三个新方向判负 + e2d 线上前沿定死
* **H6 番茄补种**（对照证据：对手 d9–17 多种 ~1.6 株番茄，番茄通道差 +1,093）：`make_tomato_arm.py`
  d9–14 换种 2 株 → 线上 **−2,406/局**（t2/t2c）/ −2,830（4 株）**判负**（换坑打乱磁带排程、番茄缺水枯死）。
* **H7 保险层缺陷类**：`am_flowledger.py --drops` 逐单位普查 86 局 → 我方 **HIRE/BUY_LAND 静默失败 0.00/局**，
  只剩良性"卖超库存"部分成交；**该缺陷类已被现有层修掉，无目标**。
* **e2d 线上前沿（配对）**：`e2d_i` +100.0（t=1.80，强池 −27 ✅）/ `e2d_t` +79（−56 ✅）/
  `e2d_v` **+139.5（t=2.03，强池 −147 ❌）**/ `mid72` +149（−144 ❌）/ `ws4` +146。
  ⇒ G2a（+150）与 G4（强池 ≥ −100）在 e2d 家族内**同时不可达**（1:1 兑换率）。
* 当前"最接近全门"的两只：`e2d_t_v224off`（AM 83/107、三池全过、线上仅 +33）与
  `e2d_i`（线上 +100、AM 仅 78/107 但 Δ+208、三池全过）——都差 G2a。

### 38c. goal 第三轮（2026-09-25 晚）：对抗门/开局分类/叠奶 全部判负 → e2d 家族"门内不可达"定论
* **H8 对抗回合门**（`--contest N`，用 RACE 流量推断 gating）：线上 +105/+114/+115 < 无门 +139；强池仍 −131（v48 仍 −310），
  且按对手是此消彼长（harvestledger −54→−150）⇒ 判负。
* **H9 开局分类**（226 局线上语料）：前 8 类开局败率 32–47%，唯一 100% 类只有 5 局；day6 落后 41% vs 领先 31% ⇒ 无靶子。
* **H10 叠"奶"**（线上+48/强池−15）到 e2d_i：+85/+45/+91 < 纯 e2d_i +100 ⇒ 分品不可加，判负。
* **定论**：G2a(+150) 与 G4(强池≥−100) 在 e2d 家族内**同时不可达**（前沿 +100↔−27 … +149↔−144；t 已达标）。
  三只"最接近"：`e2d_t_v224off`（AM83/三池过/线上+33）、`e2d_i`（线上+100/AM Δ+208/三池过）、`e2d_v`（线上+139.5 t=2.03/强池−147）。
  需要用户裁决：放宽 G2a 或 G4（v48 系直系祖先是否按满额计入退化），或认领新方向。

### 38d. goal 第四/五轮（2026-09-25）：三指标单调反向 → **结构性冲突**，已挂 blocked 等裁决
* 独立种子块复核（强池 57–80）：`e2d_i` **+45.8（零代价）**、`two1` −120.2 ⇒ "1:1 必然"被推翻，存在高效率偏离。
* 但**同族叠加**证明三指标单调反向（`GATE_DECISION_PACKET_20260925.md` 表）：
  `e2d_i`(+100 live / AM Δ+208 / 强池−27 / 新池−1) → `stack5`(+135 / +200 / −23) → `s6`(+191 / **+64** / 新池 **−194**) → `stack4`(+235 / +80 / −206)。
* 跨 11 配置回归：**live Δ 与强池 Δ 相关 r=−0.907、斜率 −1.01**；对照臂证明线上回调**奖励偏离**
  （AM 中性 cxd8k 线上 +62.5、翻转 21/89；AM 有害 or2h16 线上 +79.9）。
* 现役最接近三只：`stack5`（live+135/AM Δ+200/强池−23，只差 G2a 15）、`e2d_i`（live+100/AM Δ+208/三池全过）、
  `e2d_t_v224off`（AM 83/107/三池全过/live+33）。
* **结论**：G2a+G2b+G4 三条件在实测中互相冲突，需用户裁决（改门 / 用提交校准 / 换语料）。已按 blocked 规则挂起。

## 39. 天梯数据自产通道（2026-09-25，**记录线，未执行 P0/P1/P2**）
详见 `farm2945_dev/LADDER_DATA_PIPELINE.md`。要点：
* **已验证**：任意 episode id 可 `kaggle competitions replay <id>` 只读抓取（含非我方对局）；8 并发 **1.2 s/局**、
  **0.35 MB gz/局**；头部 id ≈ **113,187,500**（≈17k id/h）；榜单可 `--download` 并做名字→分数 join。
* **榜单快照（09-25 07:02 UTC，已存 `public_intel/leaderboard/`）**：9,995 队；**我们 2662.6 = #118**；
  #1 3028.7 / #10 2926.6 / #50 2757.3 / #100 2684.8（我们距 #100 **+22**、距 #1 **+366**）；
  最近 24h 有 2132 队提交（≥2700 的 74 队）。
* **顶队专供已定位**：georgy `episodes.csv`(226,594 局, 至 09-23) × 新榜单 TeamId → 前 20 队 **2,020 局**可抓
  （清单 `farm2945_dev/ladder_top20_episodes.json`；含 Fourth Quadrant 88 株型 8 局；Boey/Vadim 仅 0–3 局）。
* **georgy 停更**：lastUpdated 09-23 23:22 UTC（≈32 h）；09f 1.26 GB（09e 2.54 GB）⇒ 流量腰斩；
  监控 PID 3071 每 15 分钟轮询，到货自动下载。
* **计划（待指示）**：P0 用已有 georgy 语料做"2900+ vs 我们带"的差距结构对比（零下载）；
  P1 抓前 20 队 2,020 局建 `pool_ladder_top.txt`（第一个公平外部池）；P2 按结果分叉。
