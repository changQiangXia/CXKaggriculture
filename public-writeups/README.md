# 公开区方案索引（33 篇）

比赛结束后从 Kaggle 抓取的参赛者公开 write-up。这里保存可定位到的 33 篇，
不代表所有高排名队伍都发布了方案。原文以 Markdown 保存，
每篇顶部保留原始链接与作者/队名。抓取工具：`NVIDIA/nvidia-kaggle` 的
`fetch_leaderboard_writeups.py` 与 `fetch_writeup.py`。

> 这些是**他人的方案**，归档目的是技术参考。原文版权归各作者所有。

完整比较、逐队案例和训练/评测细节见
[`../docs/07-top-teams.md`](../docs/07-top-teams.md)。本页保留文章索引；
深读页回答“为什么这些方法有效、哪些结论可迁移”。
证据等级与统一口径见
[`../docs/08-evidence-and-scope.md`](../docs/08-evidence-and-scope.md)。

> 这一页的数字是**作者自报**。除非另有说明，本仓库没有重训或独立复现
> 这些方案。

---

## 一句话读完全部 33 篇

> **在有公开 write-up 的头部队伍中，强 replay/行为克隆是共同地基，但终局
> 路线并不相同：前 3 名使用不同强度的 PPO/自博弈；第 4、5、7、9、17、19、
> 27 名的最终主力是 BC/SFT-first，且可能带有少量规则。单卡和低预算也能拿到金牌。我们的公开磁带
> 派生路线最终为 509 名。**

| 方法族 | 代表名次 |
|---|---|
| BC 后接自博弈/联赛 PPO | 1、2、3、6、10、12、13、22 |
| **最终以 BC/SFT 为主，无持续 PPO（可含薄规则）** | **4、5、7、9、17、19、24、27、51、70** |
| BC/RL 与规划器混合 | 26、28 |
| 磁带 / 重放 + 手写层 | **116、509（我们）、553** |
| 手写规划器 | 573 |
| 其他（搜索蒸馏、MuZero 等） | 1231、645、3726 |

---

## 前 10 名中有公开 write-up 的逐条

### 1 名 · M & M & P & Q — BC 与自博弈 PPO 交替
`001_rank_1st-place-solution-our-journey-to-becoming-profe.md`

- 10.2M Transformer（12 层、宽 256、8 头），两个终局提交都是这个规模。
- **自博弈约 830 万 / 904 万局**（每局 1,438 个转移）。
- 四点和别人不同：(1) 发现策略缺失时插入**短 BC 阶段**再重启 PPO；
  (2) **从公开信息估计对手隐藏库存**；(3) **2D RoPE 只在同一农场内使用**；
  (4) 把推理期修正规则**通过 action masking 注入 PPO rollout**。
- 奖励只有终局 +1/0/−1；γ=1、GAE λ=0.97。
- 反直觉实测：用 34 个提交训练的 BC 初始策略，对早期自有提交
  **10 胜 90 负**；窄教师池训练的是 82 胜 18 负——但他们仍选宽池作为
  探索起点，因为多样性对后续 PPO 更有用。
- 作者同时明确说明：这组实验没有做 RL-from-scratch 或匹配 PPO 对照，
  **不能证明教师多样性带来因果收益**。更稳妥的读法是“宽池初始更弱，
  但为后续探索保留更多行为模式”。

### 2 名 · Victor @ Tufa Labs — 37M encoder-decoder + 小麦交易
`002_rank_trading-clutch-no-b200.md`

- **只用 30 个 RTX 5090 小时**。19M encoder + 17M decoder。
- BC 25 小时 → 单队微调 1 分钟 → PPO 2 小时 10 分。
- 亮点是**小麦交易算法**：单独就值 +$700；在该队两份终局提交的 A/B 重放中，
  对冠军的胜率从 9% 提到 39%。
- 但他同时警告：小麦交易是"**有吸引力的局部最优**"，会诱使你把算力浪费在
  "抢在对手前面卖 $10"而不是"多产番茄"。

### 3 名 · DSM — 10.4M Transformer，重 PPO
`003_rank_kaggriculture-3rd-place-dsm-solution.md`

- 266 个 token（200 地块 + 40 单位 + 16 商店 + 9 物品 + 1 全局）。
- 最终 run 约 **360M 步 / 12.7 万局**；整个训练 campaign 约
  **20.1B 位置 / 21M 局 / 1,883 代**，最多 23 张 A100。
- 关键技巧：**预热 critic**、按决策裁剪 ratio、**反对称 critic**
  （联赛胜率 0.359 → 0.542）。
- **推理期后处理不动模型**：只修"确定无效"的动作和"会被丢弃"的物品。
  在 7 个自家反应式对手、每臂 1,792 局的评测中，基础后处理对终局策略
  +5.0pp；加入甜瓜反制后再 +8.2pp，整链从 74.2% 到 **87.8%**。
- 明确写下我们踩过的规则：**最终排名由截止后两周的 Bradley–Terry 决定，
  每队最新 2 份提交计入。**

### 4 名 · Farmcore — BC + 喂食规则，无自博弈
`004_rank_farmcore-a-one-pass-transformer-trained-on-what-t.md`

**对我们最有参考价值的一篇。**

- **行为克隆 + 一条喂食保护规则**，无推理期搜索、无自博弈数据，
  **约 5.5 A100·小时**。
- 最大增益来自**修标签而不是修模型**：
  **模仿「引擎实际执行的」而不是「玩家下单的」**。
  强玩家会超量下单让引擎静默丢弃。同一个网络：3/24 → **12/24**；
  再加一条喂食规则 → **23/24**。
- 整回合一次前向出全部决策，然后一个 6 层 corrector 做全局协调。
- 预训练 67 个提交 → 单队微调 → **两个微调权重平均**（稳定 +$1k，最好 +$3.3k）。
- 警告：**整回合验证准确率与金额负相关（rank corr −0.86）**，
  只能按配对 seed 的金额选 checkpoint。
- 完赛后才发现的市场机制：**订单按列表位置配对，先挂的先成交**
  （+$4 或 −$10 每单位）。

### 5 名 · 有辣条有权 — "It's SFT all the way down"
`005_rank_its-sft-all-the-way-down.md`

- 结论直接写在标题里：**一路 SFT（监督微调）**。
- 更大、训练更久的 B-even 模型排在 N-flow 之前，并决定了队伍名次。

### 6 名 · CDE — 重放条件模仿 + PPO
`006_rank_6th-place-write-up.md`

- 初始 incumbent 来自 BC 模型，每 25 代用当前策略快照替换。

### 7 名 · DECEM — 只做 BC + 两条小规则
`007_rank_7th-place-my-solution-only-behavior-cloning-t.md`

- 最终 **5459.9 分，第 7 名**。8.2M 实体 Transformer。
- **纯 NumPy 推理，约 0.1 秒/回合**——至少说明原始前向计算不是主要瓶颈；
  数据构建与评测仍需要显著工程投入。
- "**前七周都在做启发式，最后九天转 BC。**"
- **新数据比什么都重要**：头部不断发新版本，最新对局权重最高，
  推理时告诉模型"按最强团队的最新版本打"。
- 作者报告最后阶段的**单队专家微调**是学会新开局的必要条件；这里保留为
  其训练条件下的经验，不当作普遍规律。
- 对 RL 的评价："有帮助，但算清它能翻几局之后就停了。"

### 9 名 · tetsuya & yuanzhe & guoqin — 从 RL 回到 BC
`009_rank_from-reinforcement-learning-to-a-final-bc-agent.md`

- **18.4M Transformer + CNN，最终仍以 BC 为主。**

### 10 名 · KawattaTaido — 单张 RTX 5090 上的 BC + PPO
`010_rank_10th-place-bc-ppo-on-a-single-rtx-5090.md`

- 单卡 5090 拿到第 10。每 210 次 PPO 迭代替换一次 KL 教师。

---

## 中段里最值得读的几篇

| 名次 | 文件 | 为什么值得读 |
|---|---|---|
| 17 | `017_rank_gold-medalist-with-70-of-compute.md` | 金牌，**算力不到 \$60**。实测"验证损失最低的 checkpoint 在四轮联赛里排最后" |
| 19 | `019_rank_19th-place-solo-gold-a-behaviour-clone.md` | **BC + 3 条清货规则**，克隆 1/3/7 名，**12 个小网络概率平均**，无 RL |
| 22 | `022_rank_behavior-cloning-and-ppo-with-diverse...md` | "用强玩家对局做的版本最终超过了持续 PPO 训练" |
| 24 | `024_rank_cloning-the-best-farmer-on-one-rtx-5070.md` | 单张 **5070** 的克隆实验 |
| 28 | `028_rank_28th-place-gold-solution-how-we-taught-a-farm-to.md` | 金牌，74KB 长文 |
| 48 | `048_rank_48th-place-solution-policy-basin-hopping-with-ex.md` | 单人第 48，"策略盆地跳跃" |

## 头部警告我们别踩的坑

**第 2 名**（小麦交易）：
> 小麦交易是**很有吸引力又很烦人的局部最优**，充满自博弈循环。
> 你可能浪费大量 GPU 时间，只为抢在对手前面卖小麦赚 \$10，
> 而不是去多产番茄。

**第 4 名**（验证集）：
> 整回合验证准确率与金额**负相关**（rank corr −0.86），
> 我们最好的验证集来自一次数据泄漏。
> **只能按配对 seed 的金额选 checkpoint。**

**第 7 名**（RL）：
> RL 有帮助，但当我算清它能翻几局之后就停了。

**第 17 名**（checkpoint）：
> 验证损失最低的 checkpoint，在四轮联赛里排最后。

**第 1 名**（教师多样性）：
> 用 34 个提交训练的 BC 初始策略，对早期自有提交 10 胜 90 负；
> 窄教师池的是 82 胜 18 负。但我们仍选了宽池——
> 我们认为多样性对后续 PPO 探索更有用。

原文明确说明，这组实验没有做 RL-from-scratch 或匹配 PPO 对照，因此
**不能证明教师多样性带来因果收益**。

---

## 与我们路线最接近的三篇

### 116 名 · Auto Fermers — 直接重放强 bot 的录像
`116_rank_116th-six-weeks-of-llm-coding-agents.md`

- **银牌**。核心洞察：**"录像比 RL 更有价值"**。
- 分析 2,024 局录像，筛约 150 个单局重放 bot，扫描头部 160 队的近期对局，
  **测量每个 bot 对局面的反应强度**。
  多数强 bot 会随资金/价格/对手变化，早期就分叉；
  只有一个 bot 的布局到第 144 步都完全一致，之后几乎是**商店序列的函数**。
  **单局盲重放**就达到 81–83% 胜率（我们最好的底盘只有 67%）。
- 警告：**"用自己旧版本上的胜利意义有限"**——与我们最后的自博弈悖论一致。

### 553 名 · Team 42 — 公开磁带 + 市场层（**与我们同构**）
`553_rank_market-layers-on-a-public-agent.md`

**这是我们的对照组，强烈建议读。**

- 第 553 名，**距银牌 15.3 分 / 46 个名次**（我们距银牌 1.0 分 / 2 个名次）。
- 路线高度相似：公开磁带（cha22）+ 自己的市场层，不是逐文件复刻。
- 他们发现的两条引擎事实，与我们的观察一致：
  **订单逐格撮合**（先挂先成交）；**镇子在市场之后消费**。
- 他们报告，在这套公开 tape 上继续增加市场层已接近收益上限：
  > 最后一次改动在 1,572 局回放上多赢 10 局。
  > **我们仍输掉的局，是输在产能上。**
- 还有一条我们没利用的：**"你展示什么，就会被针对什么"**——
  TICK 策略公开后，半天内其他队伍就在反向交易它，需要一个资金守卫。

### 573 名 · Tim McGarvey — 手写规划器 + 查表
`573_rank_top-6-in-my-first-kaggle-competition-a-hand-writ.md`

- 手写规划器的一个上限参考：**线上曾到 481 名（银牌内），最终 BT 排名第
  573（前 5.7%）**。

---

## 其他

| 名次 | 文件 | 备注 |
|---|---|---|
| 13 | `013_rank_a-good-league-is-all-you-need.md` | "联赛"比算法更重要（1.2KB 短文） |
| 26 | `026_rank_31th-place-currently-our-writeup-macro-bc-d.md` | Macro BC + Day Compiler |
| 27 | `027_rank_monsaraida-27th-place-solution.md` | 单人金牌 |
| 32 | `032_rank_32nd-place-solution-opening-book-and-heuristics.md` | 开局手册 + 启发式 |
| 47 | `047_rank_47th-place-teaching-a-farming-agent-from-replays.md` | 从回放教出一个农场 agent |
| 51 | `051_rank_51st-place-solution-replay-bc.md` | 重放 BC |
| 70 | `070_rank_70th-place-solution-replay-bc-and-teacher-select.md` | 重放 BC + 教师选择 |
| 275 | `275_rank_275th-place-solution-shop-based-farming-heuristics.md` | 基于商店的启发式 |
| 349 | `349_rank_kaggriculture-shawny1b.md` | 40KB 长文 |
| 645 | `645_rank_bronze-from-muzero-to-a-measured-hybrid-agent.md` | MuZero → 混合 agent |
| 692 | `692_rank_kaggriculture-rank-512-bronze-how-my-agent-worke.md` | 与我们名次接近的复盘 |
| 755 | `755_rank_humble-solution.md` | 提到"近 2300 分时约一半对手在跑同一家族的分叉" |
| 1231 | `1231_rank_rl-ppo-light-layer-on-base-layer-elo-ranke-11401.md` | 精确搜索蒸馏 + VinePPO |
| 3726 | `3726_rank_gigpo-kaggriculture.md` | GiGPO 思想实验 |

---

## 抓取与校验

- 来源：Kaggle 比赛 leaderboard 的 `solutionWriteUpUrl` 字段（经 Kaggle 内部
  web service），不是网页爬虫。
- 原始索引（rank / team / url）：`_index.json`。
- 33 篇全部抓取成功，0 失败；每篇 1–74 KB。
- 头部队伍**并非都发了 write-up**（例如第 8、11、14、15、16 名未出现在列表中）。
