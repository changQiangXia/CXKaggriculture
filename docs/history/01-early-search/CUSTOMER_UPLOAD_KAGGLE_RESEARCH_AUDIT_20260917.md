# `customerUpload/kaggle` 研究审计（2026-09-17）

审计对象是目录中的五个 notebook 和用户的整合总结：

- `beyond-48-0-128-128-worlds-with-95-cis.ipynb`
- `kaggriculture-cloning-agent.ipynb`（V45）
- `kaggriculture-v44-winning-the-same-turn-sale-race.ipynb`
- `kaggriculture-pipe-7-wheat-microstructure.ipynb`
- `kaggriculture.ipynb`（Evolution，V17→V19）
- `对文件夹中的文件的研究.md`

## 结论先行

这批文件对“第 0 回合小麦 round-trip 利用共享市场报价”的**机制**提供了足够清楚的源码证据，也把若干有价值的失败模式记录了下来。但是，文件并没有留下产生大多数性能数字的对局、种子、runner 或 bootstrap 原始数据。因此现在可以确认的是：候选确实实现了哪些规则，以及这些规则之间的源码谱系；不能把 notebook 中的 `128-0`、`179-1-0`、`2760`、95% CI 或数量扫描表当成已经独立复现的事实。

更关键的是，这不是五个独立实验：

1. V45 是 V44 源码末尾增加一个 step-0 wrapper 的版本。
2. Evolution 的 V19 是 V45 的再打包复制，不是外部独立确认。
3. Pipe-7 与 `kaggriculture.ipynb` 的主体逐字相同，实质只把 `_OPEN_UNITS` 从 70 改成 5。
4. Beyond 48-0 的 K0006 仍然以 Ahmed 的 V43 农场计划为父本，只在外面叠加市场 wrapper。

所以这批材料最适合被视为一条**同一 lineage 的机制研究记录**，而不是五次相互独立的验证。

## 可以直接从文件核对的证据

### V44 → V45 的谱系

从两个 notebook 的 cell 4 还原 `SOURCE_BYTES` 并重新计算得到：

| 版本 | `main.py` 字节数 | `main.py` SHA-256 | archive SHA-256 |
|---|---:|---|---|
| V44 | 327,314 | `797d9bca309d481e18cdbb675ce6d6de9967d266cbafb4c2352c68fb10264e2f` | `f5e41bd0ddad50a109f12381cc532cdc10b9e9d93dd6c6ab37cff47dfbc4916e` |
| V45 | 329,112 | `2536d41ed5a00c75204b6350f1c76c54259c774cb065ba2a3a0072eedf210d94` | `b8c2f5aab88faf2332e45f721ec83e5f9e7bec3d0a995cc0dce318badd884ed0` |

逐行 diff 显示 V45 保留了 V44 的完整源码，只在末尾加入约 28 行 opening wrapper：

```python
_OPEN_UNITS = 70
if standard and step == 0 and action.get("market") == [
    ["BUY_PRODUCT", "WHEAT", 5],
    ["BUY_PRODUCT", "WHEAT", 10],
    ["SELL", "WHEAT", 60],
]:
    action["market"] = [
        ["BUY_PRODUCT", "WHEAT", _OPEN_UNITS],
        ["SELL", "WHEAT", _OPEN_UNITS],
    ]
```

它还把 step 1 的 feed buy 从 5 改写为 5 的条件分支；除此以外没有新的农场规划器。V45 的 notebook 自己称这是“一处 market change”，源码 diff 与这一说法一致。

### Evolution notebook 不是独立样本

Evolution 的 cell 2 写出的 325,680 字节源码，与 V45 的嵌入源码逐行相同（差别只有写文件时的换行形式和首行 `%%writefile`）。其表格明确写着 `V19 = V45 copy`，并把 `2760` 标成作者结果。该 notebook 只有写文件和打包输出，没有对局执行代码。因此它可作为“另一位作者如何理解并复制 V45”的文档，不能作为 V45 的独立外部验证。

### Pipe-7 的真实改动范围

Pipe-7 解压出的源码 SHA-256 是：

`6150b7f9a953fc54d17a0f762a4c6ba5d2afe25a1851876eeb7681719d34a200`

在源码中可以核对：

```python
_R42_OPENING = [
    ["BUY_PRODUCT", "WHEAT", 5],
    ["BUY_PRODUCT", "WHEAT", 10],
    ["SELL", "WHEAT", 60],
]
_OPEN_UNITS = 5
```

step 0 只有在父 tape 与上述 opening 完全相等时才替换成 `[BUY WHEAT 5, SELL WHEAT 5]`，并且只在标准 `10×10 / 24 / 720 / 100 / 10 / 3000` 配置下生效。将 Pipe-7 与 `kaggriculture.ipynb` 的源码统一换行后比较，主体逐字相同，实质改动就是 70→5。Pipe-7 不是从零写出的独立 agent。

Pipe-7 notebook 的 cell 8 只负责解压源码，cell 9 只做 AST/entry-point 检查，cell 11 只打包。没有数量扫描循环、种子清单、对局日志或 colosseum 实现。因而 `5/40/60/65 = 50-0`、`75 = 2-48`、`80 = 0-50`、`179-1-0` 和 `1,754-46` 都是 Markdown 中的作者自报数字。

还有两个容易误读的实现细节：`_OPEN_FEED_STEP1 = 5` 后续条件是 `_OPEN_FEED_STEP1 < 5`，恒为假，所以 Pipe-7 实际只改变 step 0；另外源码解压、AST 检查和打包的 notebook 运行时间约 4 秒，不能是所称 1,800+ 局的执行记录。表格中的 `Elo Rate`、纯胜率和把平局折半的 `Rate` 也不是同一统计量，不能直接横比。

### Beyond 48-0/K0006 的实现证据

从 cell 12 解压并核对的源码为：

- `main.py` SHA-256：`4757f3f5b28db8a2f4614bb08993a8a567a7d49bae1ac324fbcfbcc1af60e95e`
- archive SHA-256：`66ee4fd7a169c10c3a313c9696b96b8661be9eea691736d0ffaa7b1a71e66582`

源码明确包含：

- `_R37_HORIZONS` 的包装视图，把父级至少 4 turn 的 reservation 改为 `HORIZON = 24`；
- step-0 只有在父 V43 opening 完全匹配时，才替换为 `BUY/SELL WHEAT 50`；
- `frontload` 市场列表重排；
- `LOOKAHEAD = 2` 的纯现金销售提前。

源码头部保留了父 V43 的完整大段源文本和父 SHA `919fc1d6...`，因此它是 V43 农场计划加 wrapper，而不是独立农场策略。

这里还有一个实现层限制：`frontload` 的 `_simulate` 维护的是聚合 shed/inventory，并没有完整地按产品检查玩家库存；它是一个安全筛选近似，不等价于官方引擎逐产品、逐订单的执行语义。源码存在不代表其“每单完整执行”安全论证已经被官方 runner 证明。

更具体地说，模拟器对订单索引交错、对手压力和最低价格的处理是简化模型，不能把它当作 engine 的形式证明；任何 front-load 候选都必须在真实 runner 中检查逐订单执行、库存、shared inventory 和订单失败。

## 作者报告的数字，哪些不能由 notebook 复跑

### Beyond 48-0

该 notebook 的可执行 cell 只有说明性导入和 cell 12 的“解压、重建 archive、SHA 检查、调用一次 agent”。没有实际 `env.run`、数量 sweep、horizon sweep、world 划分、bootstrap 或官方 runner 审计代码。

Markdown 报告了：

- 24 seeds × 双座位对 V45 为 `48-0`；
- 64 worlds × 双座位对 V45 为 `128-0`，margin `+2,087`，CI `[+1,950,+2,240]`；
- 数量扫描中 25–50 平台、85+ 自伤；
- horizon 24 最优；
- 持续整季 wheat funding 攻击 30 为 `0-16`、50 为 `2-14`；
- wrapper opponent 造成虚假 `+167,366`，打包后约 `+1,328`。

这些叙述对我们设计复核很有用，但当前文件没有 seed、逐局 margin、world 映射、bootstrap 重采样、stderr、episode log 或 runner 输出，不能独立确认这些数字。

我们另外用本机 `kaggle_environments` 1.25.9、解压后的单文件 K0006 与其 V43 父本做了两个 seed 的官方 runner spot check：候选方对父本的 cash margin 分别为 `+650`、`+1,132`，720 steps 完成、无错误；同一候选与自身镜像在两个 seed 均严格平局。这只能证明 archive 可执行及共享 opening 的对称性，不能验证公开的 48/128 局结果。源码 docstring 声称的 engine 版本为 1.32.7，与本机 1.25.9 不同，完整复核前必须固定版本。

此外，“64 worlds”按前两个商店的有序 pair 聚类，每个 world 再取一个 seed、打两个座位。两个座位共享 world，不能当成 128 个独立样本；合理的统计单位应是每个 world 的 paired statistic，再对 64 个 world bootstrap。若各 world 的抽样概率和 seed 选择没有公开，CI 还是条件于这 64 个簇的描述，不自动等于比赛分布覆盖率。

数量扫描也只说明作者自建 70-unit 对手上的 8 seeds × 2 seats 形状；它没有覆盖当前公开 opponent lineage。horizon 表同样没有样本、对手、seed 或逐局数据。

### V44/V45

V44 Markdown 报告 32 reserved worlds、`64-0` 的直接 V44 对 V43，以及 `fastclone24` 上仍然 `11-53`；V45 报告独立 V45 `620/20/0`、直接对 V44 `63/1/0`，以及 `mirror_counter` 配对边际 `-1153`。这些数字没有在 notebook 中执行生成：V44 的 code cells 没有输出，V45 的完整游戏检查明确是 optional/skipped。它们应保留为作者实验记录，而不是已被我们复核的结果。

### Pipe-7

`179-1-0` 的算术与“10 agents × 每对 20 局”相符，`1,754-46` 也与九个 opponent 表格相符；但没有 seed、引擎版本、opponent archive、common world、paired margin 或官方 runner 输出。因此样本量大不等于证据独立，尤其所有 opponent 可能属于同一 V43/V45 家族。

## 机制层应如何理解

四个源码确实反复实现同一个机制：市场按订单 list index 锁步处理，同 index 报价使用同一 shared inventory；己方 index-0 的 wheat buy 可以抬高对手后续 index-1 wheat buy 的报价，而己方紧接着的 sell 不承担同样的对手报价路径。它只在对手的 opening 恰好有“第二个 wheat buy”且资金没有余量时造成实际策略分叉。

因此应保留两个边界：

1. 这是“击穿没有 slack 的首日购买”的机制，不是泛化的“让 wheat 变贵就会持续获利”。Beyond notebook 自己报告的整季重复攻击失败，方向上与这个边界一致。
2. opening wrapper 是精确匹配触发器。面对 Two Coins/先卖后买的 opening，V45 已报告负边际；对不使用父 V43 opening 的 agent，改动可能根本不触发。不能把 V45、K0006 或 Pipe-7 的结果外推为任意 opponent 都有效。

## 对用户总结的修正

用户总结中的“发现→实现→扫描→复现→外部验证”作为**研究叙事**是成立的；作为**统计证据链**需要改成：

> 机制发现 → 同一 V43/V44 lineage 的实现 → 作者自报扫描 → 参数单点复制 → 同一 V45 源码的再打包说明。

其中“Pipe-7 独立复现”和“Evolution 外部确认”不能继续按独立证据计数。真正独立的部分是：不同 wrapper 对失败边界的文字记录、对 mirror/Two Coins 的方向性警告，以及源码中可核对的触发条件。

## 下一步可执行的复核协议

在把任何数量（尤其 5、50、70）作为候选前，建议冻结以下清单：

1. 固定正确 engine SHA、`get_last_callable` 入口、单文件 archive、fresh subprocess；禁止 wrapper 相对路径 opponent。
2. 对 `n ∈ {0,5,10,16,20,25,30,40,50,60,65,70,75,80,85,100}` 和 `horizon ∈ {4,8,16,24,36,48}` 做留出 world 评估。
3. 按 opponent opening/行为 lineage 分层：V43/V45 family、Two Coins/mirror counter、Nathan、flex/非同 tape。step-0 改动必须记录是否触发 exact-opening gate。
4. 每个 world 的两个座位合并成一个 paired statistic；报告逐 world margin、胜负、实际交易、action diff、订单失败、错误/慢步和最终 cash。
5. 开发 seeds、未调参 holdout seeds、stress counter 三套分离；数量选择只允许用开发集，最终方向判断看 holdout。
6. 同时运行本地 strict harness 与官方 `kaggle_environments` 单文件审计；两者都通过才升级证据等级。

建议的决策门槛是“机制方向在多个 lineage、未调参 world、两个 runner 上同号”，而不是某个 notebook 的单次 win rate。当前不提交、不构建新候选；先把这些复核结果补齐，再讨论 5/50/70 哪一个值得进入本地候选。
