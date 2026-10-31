# Kaggriculture · CHEN Xiang 参赛归档

> **最终成绩：509 / 10,148（前 5.02%），private 4513.5**
> 银牌线为第 507 名 / 4514.5 分 —— **差 1.0 分、2 个名次。**

这是一份比赛归档，也是一份 write-up：记录我们怎么做的、试过什么、为什么
止步于此，以及如果重来一次会怎么做。所有原始笔记、33 篇参赛者公开 write-up、
两份终局提交的可执行文件都在这个仓库里。

> **口径说明：** 当前事实、术语与证据等级以
> [`docs/08-evidence-and-scope.md`](docs/08-evidence-and-scope.md) 为准。
> `COMPLETE-STORY.md`、`experiment-log.md` 和 `retrospective.md` 保留历史
> 快照，其中的临时分数与强措辞不自动代表最终结论。

**推荐阅读顺序：**

1. 本页 §3–§8：先掌握终局方案、关键发现、优势、不足和失败边界；
2. [`docs/06-our-agent.md`](docs/06-our-agent.md)：看 Router、41 条路线和
   约 60 个包装/控制点的代码级结构；
3. [`docs/07-top-teams.md`](docs/07-top-teams.md)：深读前 10 名及单卡金牌
   方案，理解高手为何选择 BC、PPO、联赛或规划器；
4. [`docs/08-evidence-and-scope.md`](docs/08-evidence-and-scope.md)：
   查看全仓库的证据分级、指标口径和措辞边界；
5. [`docs/01-timeline.md`](docs/01-timeline.md)：按日期看判断如何变化；
6. [`docs/02-experiments.md`](docs/02-experiments.md)：查各组实验的规模、
   结果和证据强度；
7. [`docs/history/CHRONOLOGY.md`](docs/history/CHRONOLOGY.md)：需要原始细节时，
   从 521 份逐日笔记继续追溯。

---

## 0. 一句话总结

我们用一个**41 条路线组成的动作磁带库 + 约 60 个包装/控制点**的架构，在
约 60 个常量里找到唯一一个真正卡在错误一侧的开关
（`V9_FERT_FIRST_DAY 14 → 12`，+84 分/局），把它推到了**前 5.02%**；
在同类磁带路线（553 名的队伍）以及我们自己的实验中，市场层收益持续缩小；
**剩余差距主要落在生产和计划执行，而不是继续优化卖单。** 头部选手则把强 replay 学成
条件策略：前 3 名用不同强度的自博弈 PPO，第 4、7、17、19、27 名等以 BC
为主并配合少量规则拿到前四或金牌。BC 是共同地基，PPO 只是有条件时使用的
第二轮放大器。

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

* 在这套磁带中，日程接近饱和（在归档日志的不同统计口径下约为
  74%–97%，取决于是否把移动或无效动作计入），因此新增行为经常被机会成本吃掉；
* 在这套 tape 的高杠杆区域中，改动主要是**参数与开关**（时机、阈值）；
* 每层要么自己付账，要么是税；应同时用配对测试、胜负翻转和线上结果判断。

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

### 3.3 终局常量扫描中最强的正向开关

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

线上读数：提交后的首个观测为 **2109.3**；同一天稍早的父本 `comb` 为
1943.9。两者不是严格同时刻的配对 A/B，因此 **165 分只能作为支持性证据，
不能单独证明全部差异来自这 6 行代码**。

### 3.4 我们做对了什么（方法论）

这一节比上面的结果更重要，因为**本轮常量扫描中最强的信号差点被扔掉**。

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
| **包装点消融**（60/60） | 在该面板中两处前置市场层为负收益，多数其余包装点承重 |
| **拼接 / 路线 × 窗口搜索** | 现役配置即联合最优 |
| **市场流合成**（约 350 个变体） | 在归档面板中均为负或惰性 |
| **动物逃逸修复**（3 个补喂算子） | 救回 154 只羊、花掉 35k 劳动价值换 77k 资本，**净亏** |
| **棚屋溢出** | 机制确会销毁，但实测仅 154 分/局，属噪声 |
| **RL / PPO**（本地沙盒 40 轮） | 零泛化 |
| **行为克隆我们自己的路由器** | 100% 复现教师，但只复现、不提升 |
| **长期常量扫描** | 约 60 个里只有 1 个正向开关 |

**结构性观察**：在这套磁带里，劳动预算非常紧；每只牲畜每天仍需约
2.2 个动作。若干救回牲畜的实验净亏，支持“逃逸部分是预算剪裁”的解释，
但不能推出所有磁带都处于同一利用率，也不能证明逃逸在所有世界里最优。
新增行为需要重新验证整条生产和现金流链。

---

## 5. 优势与不足

这一节同时评价**策略本身**和**仓库证据质量**。优势是“在已测范围内观察到
有效”，不是对所有类似比赛的保证；不足也不否定 509/10,148 的结果。

### 5.1 方案优势

| 优势 | 具体表现 | 证据边界 |
|---|---|---|
| **完整、自包含、确定性强** | 终局包只有一个 `main.py`，内含 41 条路线、Router 和包装层，无外部模型或网络依赖 | 源码与哈希可核验；不代表计算最优 |
| **保留了完整生产链** | 每条路线覆盖 719 个可执行 step，生产、劳动、搬运和卖单相位已经协调 | 多个包装点会影响执行；静态存在不等于每局触发 |
| **利用公开世界状态做路由** | day 6 用 64 行商店表选路线，并另有 V92/V93 覆盖；day 12/20/27 固定切换 | 路由来自历史世界分布；未必覆盖未来 meta |
| **工程性防守较多** | 杂草修复、工人对齐、提前卖、棚屋保护、终局清货和异常回退 | 部分包装点在面板上惰性；实际价值依赖世界分布 |
| **评估纪律较强** | 同对手/同世界/同 seed 配对、fidelity 过滤、多池复核、直接对打与线上并列报告 | 冻结回放不能模拟反应；尚无一个本地指标完全复现最终 BT |
| **最终改动很小** | `comb2b` 相对 `comb` 只改 3 个常量（6 行 diff），三池均值为 +108～+113/局 | 这是当前三池的配对结果，不是对所有对手的无条件增益 |
| **负结果记录充分** | 60/60 包装点、27 组拼接、约 350 个市场变体以及补喂/RL/算子实验都有结论 | “全部失败”只在各自列出的实验范围内成立 |

### 5.2 方案不足

| 不足 | 具体影响 | 当前判断 |
|---|---|---|
| **固定路线限制长期重规划** | day 12 后主要沿用既定路线；对手大幅改变产能或市场策略时，缺少从当前状态重排整局计划的能力 | 这是当前证据支持的主要结构性瓶颈 |
| **“磁带 + 多包装层”耦合复杂** | 终局源码约 8,444 行、1.06 MB；约 60 个可消融包装点共享同一动作轨迹，局部改动容易改变后续相位 | 可维护性和因果归因明显弱于单策略网络或显式规划器 |
| **对市场 meta 的适应性有限** | 卖单预测和抢卖层被组合、关闭或局部保留；冻结面板无法完整评价会反应的对手 | 冻结回放与直接对打排序相反，尚未解决 |
| **阈值和规则有过拟合风险** | 大量常量只在特定 108 局面板或对手池上测试；少量规则在不同面板上可能由正转负 | 因此只保留跨池一致和确定性的硬边界 |
| **学习型对手建模不足** | 没有训练状态到动作的完整策略；对手隐藏库存、未来销售和生产切换主要靠规则或离线分析 | 与头部 BC/PPO/规划器方案存在能力代差 |
| **最终名次非常贴面** | 509 名与第 510 名同为 4513.5；距第 507 名只差 1.0 分 | 小幅评分或匹配变化即可改变名次，不能把边界结果解释成稳定优势 |
| **性能上限受时间分配影响** | 大部分时间用于优化手写 tape，学习型方案开始较晚 | 这是过程复盘；无法单凭结果量化“如果更早转向一定能到多少名” |

### 5.3 仓库与证据优势

- **终局可执行物完整**：5 个候选包均有校验和；两份终局提交和两份被顶出、
  两份未提交对照均有出处。
- **实验链条可追踪**：从 521 份原始笔记到逐日索引、实验总账、时间线和
  长文复盘，能追踪“观察到什么、试了什么、怎样推翻”。
- **评估工具与负结果都保留**：不只保存最终赢家，也保留冻结回放、直接对打、
  BT、逃逸、棚屋和 RL 失败实验。
- **公开方案可追溯**：33 篇 write-up 保留原链接、作者或队名及版权说明；
  顶级方案深读区分了作者自报、工程结论和我们的推断。

### 5.4 仓库与证据不足

- **不是完整复现包**：不包含官方 engine、完整 replay 语料或模型权重；
  `tools/` 中的历史脚本可能仍需修改路径和依赖。
- **不能独立复现第三方结果**：33 篇 write-up 没有重训；对头部方案的结论
  来自原文核对和交叉比较，不是独立 benchmark。
- **最终 leaderboard 的完整导出未归档**：仓库只有比赛中途快照；最终
  509 / 10,148、4513.5 来自比赛结束后的最终页面记录。
- **历史材料并非统一口径**：工作日志里有被推翻的数字和绝对化措辞，已加
  时间/证据边界，但原话没有改写成事后正确答案。
- **引擎规则页不是权威全集**：`reference/engine-rules.md` 只是便利摘录；
  关键执行语义应以对应官方 engine 源码和 replay 对账为准。

---

## 6. 一个没有解决的矛盾

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

## 7. 公开区顶级选手做了什么

我们把归档时能定位到的 **33 篇公开 write-up** 保存下来
（`public-writeups/`），并把前几名的
方法摘录在 [`public-writeups/README.md`](public-writeups/README.md)。

**更准确的概括：在有公开 write-up 的头部队伍中，强 replay/行为克隆是共同
地基，但终局路线分成 BC→自博弈 PPO、纯 BC/SFT、以及 BC+显式规划器三类。**

| 路线 | 代表名次 | 关键条件 |
|---|---|---|
| BC → 自博弈/联赛 PPO | 1、2、3、6、10、12、13、22 | 强 critic、反应式联赛、足够新的 replay；规模化收益大 |
| 以 BC/SFT 为主（可含薄规则） | 4、5、7、9、17、19、24、27 | 执行后标签、教师版本一致、按整局选 checkpoint |
| BC/RL + 显式规划器 | 26、28 | 用规划处理生产、劳动、路线、市场和终局约束 |

| 名次 | 方法 | 训练规模 |
|---|---|---|
| 1 | Transformer 10.2M + BC/PPO 交替（BC 引入新策略） | ~8.3M–9.0M 自博弈局 |
| 2 | 37M encoder-decoder，纯 BC + 短 PPO | **30 GPU·小时**（RTX 5090） |
| 3 | Transformer 10.4M + 重 PPO | 最终 run 360M 步；总 campaign 约 21M 局 |
| **4** | **BC + 喂食保护规则，无自博弈** | **~5.5 A100·小时** |
| 7 | 8.2M BC + 两条保护规则，NumPy 推理 | 单张 RTX 5090 |
| 17 | 4M/7M 纯 BC + 薄规则层 | 总成本 <\$60 |

第 4 名的结论对我们最有参考价值：**数据与标签选择比模型规模值钱十倍**。
他们把「模仿玩家下的单」换成「模仿引擎实际执行的单」，同一个网络从 3/24 提到 12/24。
完整逐队比较、PPO 失败条件和低算力复现路线见
[`docs/07-top-teams.md`](docs/07-top-teams.md)。

---

## 8. 如果重来一次

完整推演见 [`docs/05-next-time.md`](docs/05-next-time.md)。三条最硬的：

**① 把 BC 作为首选主线并尽早建立闭环。**
第 4 名用约 5.5 A100·小时、以 BC 为主并加一条喂食规则拿到第 4。
我们测试的磁带派生路线最终为
509 名；同类路线（553 名）也报告市场层收益衰减、剩余差距在产能。
第 17 名不到 60 美元的纯 BC 金牌进一步说明，初始门槛不在
“必须有 GPU 集群”，而在数据、动作接口与完整局评测；这不意味着算力不决定上限。

**② 评估器要先于模型建立，且必须配对。**
这是我们从第一天就做对、并在整场比赛中持续受益的关键工程决定，也是小幅
真实效应没有完全埋进噪声的主要原因。

**③ 认规则的时间尺度。**
这个比赛的名次由**两周后的 BT 重算**决定。我们曾在 10-02 写下「缓冲 4σ、
接近确定」，12 小时后被推翻；最终也确实只差 1 分。**分数是快照，不是结果。**

---

## 9. 仓库结构

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
│   ├── 07-top-teams.md            ★ 顶级高手方案横向深读
│   ├── 08-evidence-and-scope.md   ★ 证据分级、指标口径与措辞边界
│   ├── COMPLETE-STORY.md          长篇叙事（一份文档讲完整场比赛）
│   ├── experiment-log.md          最后 38 小时的逐小时日志
│   ├── retrospective.md           复盘原文（含被推翻的结论）
│   ├── reproducing.md             复现指南 + 已知陷阱
│   └── history/                   521 份原始工作笔记（按日期分三阶段）
│       ├── README.md              阶段说明
│       └── CHRONOLOGY.md          ★ 逐日实验账本（521 份全索引）
├── public-writeups/               33 篇公开 write-up + 索引与深读
├── candidates/                    5 个候选包 + SHA256SUMS
├── tools/                         15 个评估与诊断脚本
├── evidence/                      榜单快照与样本对局
└── reference/                     引擎规则摘录（非完整权威副本）
```

---

## 10. 数据与规则合规

本仓库**不包含**原始比赛数据、私有数据、模型权重或未公开的他人提交物。
`evidence/` 保留 4 局自采对局样本；`public-writeups/` 和 `candidates/`
只包含公开分享且保留来源/许可说明的文本或代码。

`public-writeups/` 收录的是**参赛者在 Kaggle 公开发表的方案说明**，
仅作技术归档与研究参考；每篇顶部保留原文链接与作者归属，不改变原作者版权。
`candidates/` 内适用的代码派生自允许再利用的公开作品；原文件中的版权、
许可证和竞赛规则声明均予保留。若来源条款有疑义，以对应原文和竞赛规则为准。

完整的证据分级、public/private 与训练规模口径见
[`docs/08-evidence-and-scope.md`](docs/08-evidence-and-scope.md)。

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
hand-building tapes — the 4th-place team reached 4th with BC plus one feeding
rule in ~5.5 A100-hours, and the closest peer to our approach (553rd) reported a similar
bottleneck in its tested route: market-layer gains became small while production
and execution remained. A detailed
technical walkthrough of the route router, layer stack, and lineage is in
`docs/06-our-agent.md`; `docs/07-top-teams.md` compares the top public teams,
separates BC/SFT-only from BC+PPO and hybrid-planner approaches, and explains
which practices transferred to a low-compute rerun. `docs/08-evidence-and-scope.md`
defines the evidence levels and measurement conventions used across the archive.

The system's main strengths are a complete deterministic artifact, coordinated
719-step economic traces, extensive defensive overlays, and unusually careful
paired evaluation and failure documentation. Its main weaknesses are the lack of
long-horizon replanning, the coupling and maintenance cost of a tape plus many
wrappers, limited adaptation to reactive market opponents, and evaluation
evidence that is still inconsistent across frozen replay, direct duels, and the
live ladder.
