# Kaggriculture · CHEN Xiang 参赛归档

> **最终成绩：509 / 10,148（前 5.02%），private 4513.5**
> 银牌线为第 507 名 / 4514.5 分 —— **差 1.0 分、2 个名次。**

这是一份比赛归档，也是一份 write-up：记录我们怎么做的、试过什么、为什么
止步于此，以及如果重来一次会怎么做。所有原始笔记、33 篇顶级公开 write-up、
两份终局提交的可执行文件都在这个仓库里。

**推荐阅读顺序：**

1. 本页 §3–§7：先掌握终局方案、关键发现和失败边界；
2. [`docs/06-our-agent.md`](docs/06-our-agent.md)：看 Router、41 条路线和
   约 60 个包装/控制点的代码级结构；
3. [`docs/01-timeline.md`](docs/01-timeline.md)：按日期看判断如何变化；
4. [`docs/02-experiments.md`](docs/02-experiments.md)：查各组实验的规模、
   结果和证据强度；
5. [`docs/history/CHRONOLOGY.md`](docs/history/CHRONOLOGY.md)：需要原始细节时，
   从 521 份逐日笔记继续追溯。

---

## 0. 一句话总结

我们用一个**41 条路线组成的动作磁带库 + 约 60 个包装/控制点**的架构，在
约 60 个常量里找到唯一一个真正卡在错误一侧的开关
（`V9_FERT_FIRST_DAY 14 → 12`，+84 分/局），把它推到了**前 5.02%**；
但同类路线（553 名的队伍）和我们自己都撞上了同一面墙：
**市场层有天花板，剩下的差距在产能。** 而真正的头部选手，用的是
**行为克隆 + 自博弈 PPO 训练出来的 Transformer 策略**，与我们是两个物种。

---

## 1. 比赛与规则

**Kaggriculture**（Kaggle Featured，$50,000，10,148 队）：

两名智能体在 10×10 棋盘上经营 30 个游戏日（720 步）——种植、浇水、养牲畜、
雇工，并在一个**共享市场**上交易。双方订单逐格撮合，价格随共同库存变动。
得分 = 最终资金。

**决定打法形态的四条规则：**

| 规则 | 后果 |
|---|---|
| 每天最多 5 次提交，但**只追踪最新 2 份** | 新提交会**顶掉**旧的，发错一次就少一个槽位 |
| 提交关闭（09-30 23:59 UTC）后**继续跑局两周**（到 10-14） | 截止时的名次不是最终名次 |
| 最终排名 = **Bradley–Terry 重算**，只看胜负 | 金额差、早期快照都不算数 |
| 新提交从**基线评分**起步 | 提交当下看到的分数毫无意义 |

---

## 2. 最终提交（完整归档）

只追踪最新两份，所以最终代表我们的是这两份：

| 槽位 | Kaggle ref | 文件 | public | **private（终局）** |
|---|---|---|---|---|
| 1 | `56718170` | **`cand_comb2b.tar.gz`** | 2089.3 | **4513.5** ← 团队分 |
| 2 | `56716540` | `cand_w2_120.tar.gz` | 2072.3 | 4510.7 |

另有两份提交已不在追踪槽内，但仍完整保留以便复现：

| ref | 文件 | public | 说明 |
|---|---|---|---|
| `56708604` | `cand_comb_pp_race.tar.gz` | 1943.9 | 中途提交，被顶出 |
| `56697965` | `cand_w2_120.tar.gz` | 2203.1 | **同一文件**的早期提交 |

两个对照变体（**未提交**，只用于本地实验）：
`cand_fert12.tar.gz`（1 处常量改动）、`cand_varA_keepRACE.tar.gz`（恢复一层）。

**校验**：`candidates/SHA256SUMS`。每个包内只有单个自包含 `main.py`，
不导入引擎、不联网、不依赖外部文件。

> 完整提交档案、逐份改动与验证证据见 [`docs/03-final-submissions.md`](docs/03-final-submissions.md)。

---

## 3. 我们的方法

### 3.1 架构：磁带 + 策略层

最终 agent 是一个**路线条件化的冻结动作回放器**。包内有 41 条完整路线，
每条包含 719 个可执行 step（0–718，覆盖 720 步 episode）。第 6 天读取前两个
解锁商店，从 64 行映射表中选择世界专属路线；第 12、20、27 天再切到固定的
中后段和末期路线：

| step 范围 | day | 路线行为 |
|---|---:|---|
| 0–143 | 0–5 | 统一开局路线 |
| 144–287 | 6–11 | 按前两个解锁商店选择路线 |
| 288–479 | 12–19 | 固定路线 104 |
| 480–647 | 20–26 | 固定路线 120 |
| 648–718 | 27–29 | 固定路线 2 |

路线外再串联约 60 个包装/控制点，在特定条件下改写具体决策——市场订单、
劳动力分配、牲畜选择、种子浮动和终局清货。这里的“60”是源码中的可消融
包装标记数，不是 60 个独立模型；部分层是安全保护，部分层只在特定世界触发。

这个架构的性质决定了后面的一切：

* 磁带的日程是**饱和**的（劳动利用率约 95%），所以**加行为**几乎总是被机会成本吃掉；
* 能动的只有**参数与开关**（时机、阈值）；
* 每层要么自己付账，要么是税——唯一判据是配对测试。

完整拆解——包括 Router 伪代码、每类策略层、三层候选血统和源码审计方法——
见 [`docs/06-our-agent.md`](docs/06-our-agent.md)。

### 3.2 路由为什么这样选

路线选择只依赖公开状态：

1. step 2 记录对手开局资金与小麦库存；
2. step 144 读取前两个解锁商店；
3. 无羊毛店时使用 EXP240 的 64 行新商店表，有羊毛店时使用 V39 的
   64 行旧商店表；
4. 15 组含羊毛店的组合再被 V92 表覆盖，另有一个开局特征例外；
5. 最后按 day 12/day 20/day 27 三个边界切到 104/120/2。

`w2_120` 的名字来自“第二个中后段窗口使用路线 120”。我们没有继续叠一个
学习分类器，因为 day-6 表留一法重拟合、27 组合路线边界扫描和固定开局替换
都没有稳定超过这个确定性路由。

### 3.3 唯一真正有效的改动

我们扫了约 60 个常量与阈值家族。绝大多数是**死代码**（改动后产生逐字节相同的
对局）或**已经站在悬崖正确一侧**。只有一个是真正卡在错误一侧的：

```
V9_FERT_FIRST_DAY   14 -> 12      +84 边际分/局
```

在三个独立对手池上验证：+84（t=5.10）、+82（t=4.67）、+94（t=2.47）。
阈值扫描显示它是**开关而非连续量**：12 与 13 逐局完全相同（delta=0.00），
14 恰好错过窗口。

再加上两个较小的常量（`_R37_PRICE_FLOOR 1→2`、`_R37_HINGE_GAIN 8→6`），
得到终局提交 `comb2b`：三池效应 **+112 / +108 / +113**，t = 2.8–5.6，
而改动只有 **6 行 diff**。

线上验证：开分 **2109.3**，比它的父本高 165 分。

### 3.4 我们做对了什么（方法论）

这一节比上面的结果更重要，因为**唯一有效的发现差点被扔掉**。

**① 配对评估把噪声压掉 65 倍。**

| | 标准差 |
|---|---|
| 单局金额差 | **13,129** |
| 配对差（同对手、同世界、同种子） | **201** |

**② 胜负判据会漏掉真实信号。**

同一个 `V9_FERT_FIRST_DAY 14→12`：

| 判据 | 结论 |
|---|---|
| 胜负计数 | 76 胜 vs 77 胜 → 「毫无变化，甚至更差」 |
| 配对边际 | **+82/局，t = 4.67** |

**它早期就是被「−1 胜」扔掉的。** 逐局看：111 局更好、20 局更差——85% 的局在
改善，但多数只改善几十到几百，不足以把「输 8000」变成「赢」。

**③ 先验证仪表，再相信数字。**

这一轮我们至少犯过 5 次仪器错误（读错观测时点、把「触及上限」当成「浪费」、
把跨 bot 方差当测量误差……）。每个都被第二个独立口径纠正。
工程上最值钱的一件事是**开工第一天就审计本地引擎与线上的等价性**——
我们做了（4 局逐状态比对，零分歧），之后三周的所有本地数字才有意义。

---

## 4. 我们试过但没成功的（大部分工作量在这里）

| 方向 | 结果 |
|---|---|
| **层消融**（60 层全扫） | 只有两处前置市场层是真税，其余承重 |
| **拼接 / 路线 × 窗口搜索** | 现役配置即联合最优 |
| **市场流合成**（约 350 个变体） | 全部为负或惰性 |
| **动物逃逸修复**（3 个补喂算子） | 救回 154 只羊、花掉 35k 劳动价值换 77k 资本，**净亏** |
| **棚屋溢出** | 机制确会销毁，但实测仅 154 分/局，属噪声 |
| **RL / PPO**（本地沙盒 40 轮） | 零泛化 |
| **行为克隆我们自己的路由器** | 100% 复现教师，但只复现、不提升 |
| **长期常量扫描** | 约 60 个里只有 1 个正向开关 |

**结构性发现**：磁带型 agent 是一台**满负荷调度器**。每只牲畜每天约需
2.2 个动作，劳动利用率约 95%。所以「它让一部分牲畜逃逸」不是 bug，而是在
固定劳动预算下的**最优主动淘汰**。任何「加一件事」的算子都会被它自身的
机会成本吃掉。

---

## 5. 一个没有解决的矛盾

比赛最后一天，我们跑了**直接对打**（两个 agent 同世界、双向座位、128 个世界）：

| 测试方式 | 排序 |
|---|---|
| 冻结回放配对（996 局） | `comb2b` > `comb` > `w2_120`，+238，t=13.5 |
| **直接对打（256 局）** | **`w2_120` 反向胜出 67–80%** |
| 线上天梯 | `comb2b` > `w2_120` |

两者结论相反。我们的解释是：**冻结对手无法对我们的市场操作做出反应**，
而 `comb` 系去掉的正是两个针对活对手的市场层——把对手冻住再测，等于先把
防守方绑起来再判定防守没用。但我们**没能在比赛窗口内证明这一点**。

详见 [`docs/04-lessons.md`](docs/04-lessons.md)。

---

## 6. 公开区顶级选手做了什么

我们把**33 篇公开 write-up** 全部抓取归档（`public-writeups/`），并把前几名的
方法摘录在 [`public-writeups/README.md`](public-writeups/README.md)。

**一句话概括头部：全是「行为克隆 + 自博弈 PPO」的 Transformer。**

| 名次 | 方法 | 训练规模 |
|---|---|---|
| 1 | Transformer 10.2M + BC/PPO 交替（BC 引入新策略） | ~8.3M–9.0M 自博弈局 |
| 2 | 37M encoder-decoder，纯 BC + 短 PPO | **30 GPU·小时**（RTX 5090） |
| 3 | Transformer 10.4M + 重 PPO | 360M 步 / 20.1B 位置 / 21M 局 |
| **4** | **纯 BC，无自博弈** | **~5.5 A100·小时** |

第 4 名的结论对我们最有参考价值：**数据与标签选择比模型规模值钱十倍**。
他们把「模仿玩家下的单」换成「模仿引擎实际执行的单」，同一个网络从 3/24 提到 12/24。

---

## 7. 如果重来一次

完整推演见 [`docs/05-next-time.md`](docs/05-next-time.md)。三条最硬的：

**① 造磁带是死路，第一天就该做 BC。**
第 4 名用 5.5 A100·小时、纯 BC 拿到第 4。我们的路线在 509 名撞上天花板，
而同类路线（553 名）的 write-up 结论与我们完全一致：**「市场层有天花板，
剩下的差距在产能」**。

**② 评估器要先于模型建立，且必须配对。**
这是唯一一件我们从第一天就做对的事，也是唯一有效的发现没有变成噪声的原因。

**③ 认规则的时间尺度。**
这个比赛的名次由**两周后的 BT 重算**决定。我们曾在 10-02 写下「缓冲 4σ、
接近确定」，12 小时后被推翻；最终也确实只差 1 分。**分数是快照，不是结果。**

---

## 8. 仓库结构

```
CXKaggriculture/
├── README.md                      ← 你在这里（write-up）
├── docs/
│   ├── 00-overview.md             赛事、规则、最终成绩
│   ├── 01-timeline.md             探索历程（三阶段，带日期）
│   ├── 02-experiments.md          实验总账（做了什么、结论）
│   ├── 03-final-submissions.md    两份终局提交的完整档案
│   ├── 04-lessons.md              教训：哪里判断错了、怎么发现的
│   ├── 05-next-time.md            下次如何做得更好
│   ├── 06-our-agent.md            ★ 我们的方案：路由、层栈与证据
│   ├── COMPLETE-STORY.md          长篇叙事（一份文档讲完整场比赛）
│   ├── experiment-log.md          最后 38 小时的逐小时日志
│   ├── retrospective.md           复盘原文（含被推翻的结论）
│   ├── reproducing.md             复现指南 + 已知陷阱
│   └── history/                   521 份原始工作笔记（按日期分三阶段）
│       ├── README.md              阶段说明
│       └── CHRONOLOGY.md          ★ 逐日实验账本（521 份全索引）
├── public-writeups/               33 篇公开 write-up + 索引摘要
├── candidates/                    5 个候选包 + SHA256SUMS
├── tools/                         15 个评估与诊断脚本
├── evidence/                      榜单快照与样本对局
└── reference/                     引擎规则常量
```

---

## 9. 数据与规则合规

本仓库**不包含**任何比赛数据、对局回放（除 4 局自采样本）、或他人提交物。

`public-writeups/` 收录的是**参赛者公开发表的方案说明**（Kaggle 自动公开的
top episode 与公开 discussion），仅作技术归档与研究参考；每篇顶部保留原文
链接与作者归属。`candidates/` 内的代码派生自公开发布的 MIT/Apache-2.0 作品，
其版权与许可声明原样保留在 `main.py` 内。

如相关竞赛规则要求删除或调整，请联系仓库所有者。

---

## English abstract

**Result: 509th of 10,148 teams (top 5.02%), private score 4513.5 — one point
and two places short of the silver threshold (507th, 4514.5).**

Our agent was a deterministic route-replay policy with 41 complete 719-step
action tapes and roughly 60 wrapper/control points. It selected a route from
the first two unlocked shops on day 6 and switched to routes 104/120/2 in the
day-12–19, day-20–26, and day-27–29 windows. Sweeping ~60 constants found
exactly one genuine untaken switch
(`V9_FERT_FIRST_DAY 14→12`, +84 margin per game, t = 5.10 across three
independent opponent pools); it had been discarded earlier because the first
sweep used win/loss counts instead of paired margins. The final variant
changed six diff lines and was worth +112/+108/+113 across three pools.

The two final submissions are archived in full under `candidates/`. The 33
public solution write-ups from the competition are under `public-writeups/`,
indexed and summarised. `docs/05-next-time.md` lays out what we would do
differently: build the paired evaluator first (we did, and it is why the one
real finding survived), then train a behavioural-cloning policy instead of
hand-building tapes — the 4th-place team reached 4th with pure BC and ~5.5
A100-hours, and the closest peer to our approach (553rd) reported the same
ceiling we hit: market layers run out; production is what remains. A detailed
technical walkthrough of the route router, layer stack, and lineage is in
`docs/06-our-agent.md`.
