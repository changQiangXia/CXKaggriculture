# V37 / Flex 对局机制审计（2026-09-12）

## 结论

V37 的唯一公开平局 `108071579` 是确定性的镜像局，而不是调用故障：
两个 seat 的 720 个 action 完全相同，动作计数为 `WATER 60 / NORTH 77 /
SOUTH 70 / EAST 81 / WEST 77 / FEED 52 / CARE 51 / HARVEST 53`，市场计数为
`BUY_SEED 189 / SELL 479 / HIRE 281 / BUY_PRODUCT 61 / BUY_ANIMAL 13 /
BUY_LAND 2`。终局两边均为 `77288`，无 stderr，最大 callback 约 `0.349 s`。
对局 seed（来自 replay info）为 `1495252849`；用本地 engine 重放 V37 对 V37
两种 seat 顺序仍为 `77288:77288`。

平局中每个公开 state、路线和市场队列都相同，因此 quote-priority 重排只会
重排同一物品的顺序，不能破除这种镜像。要把 tie 变成 win，必须有条件地改变
某一轮的销售时间或数量；这会改变共享市场 inventory，单纯切换 SELL 顺序没有
经济作用。当前没有足够证据证明一个固定 seat 偏置安全，禁止直接启用。

### 新增线上记录（扫描至 06:30 UTC）

监控随后捕获到 V37 的两场新平局和四场新失利。平局 `108082646`（对手
Xander，seed `1581543147`）的 720 个 action 与 V37 完全一致，终局
`76918:76918`；平局 `108084841`（对手 Yin Li，seed `505835811`）同样
是完全一致的 tomato 资格路线，终局 `85744:85744`。这两局进一步确认：
镜像检测能可靠识别 tie，但想赢必须做会改变市场 inventory 的销售量/时点
变化，且不能用固定 seat 偏置。

新失利的机制边界更清楚：`108078615` 对 TOSS 为 `89381:90759`，对手在
day 6 买 COW 而 V37 买 GOOSE，并以 457 次 SELL 对 V37 的 405 次 SELL
扩大了库存冲击；`108083700` 对韩方选手为 `139922:141033`，差异从 day 0
的 wheat round-trip、day 7/9 的 animal 选择开始，末期市场路线延续；
`108084677` 对 Setu Chokshi 为 `81749:83305`，对手触发了 10 TOMATO
seed 的分支并保留 10 个 TOMATO tile；`108085679` 对 taiseiu 为
`72312:74845`，对手的早期公开订单和多一次 HARVEST 令末期差距达到
2533。四局均 720 步 `DONE`、无 stderr，不能归因于 timeout。

因此 V37 需要针对两个公开 opponent family 做条件化处理：一是较高 SELL
流量/不同动物构成的 TOSS 类，二是 tomato branch 与 V37 争夺相同市场的
路线。只排序 SELL 不足以应对；候选应在 day 6–9 的 animal/wheat round-trip
和 day 26–29 的 tomato、milk、carrot liquidation 上做真实 stock-bounded
时点试验。

## Flex 近期 loss 的共同结构

最近可见失利：

| episode | rewards | 差值（Flex） | 关键差异 |
|---|---:|---:|---|
|108068681|98016:95766|−2250|day 12/13 MILK 销售相差一拍；day 22–26 fertilizer / hire / milk 数量和时序不同；末期逆转约 2250|
|108069646|69810:71377|−1567|对手在 day 18 买 `TOMATO` seed 10；Flex 没有对应产量；day 27–28 tomato/milk/carrot 结算差异|
|108070739|70974:70800|−174|大量同路线订单只在 day 0、7、12–22 的 SELL/HIRE 排列上错位，最终差距很小|
|108072913|121826:121198|−628|day 27–28 milk/strawberry/carrot 的提前销售差异，早期固定 +35 只在末期放大|
|108073749|59913:58916|−997|day 16 wool 销售提前/延后；day 27–28 milk/strawberry/carrot 时序造成主要损失|
|108079092|70687:69361|−1326|对手公开路线明显不同，早期买卖和额外投入带来持续优势；非单一终端故障|

所有这些局都为 720 步 `DONE`，没有 stderr；因此不应围绕 timeout 或异常
做改动。损失主要发生在 day 27–29 的 liquidation：`MILK`、`STRAWBERRY`、
`CARROT`、`WOOL` 的销售在不同 step 相差 1–2 个 turn，和共享市场库存变化
叠加。day 12/13 的 MILK 一拍错位通常先造成几百资金差，但不是所有失利的
决定因素。

## 可实现但必须本地验证的改动

1. **Terminal-sale two-phase timing（优先）**：仅在 step 648–695、已有实际
   shed stock 且当前 action 没有购买障碍时，把下一步 route 的 MILK/CARROT/
   STRAWBERRY/WOOL SELL 提前一 turn；记录 debt 并在原 step 抑制相同物品。以
   现有 `_r36_reserve` 为基底扩展，严禁 speculative quantities。目标是减少
   Flex 类 day 27–29 错位，同时保留 V37 的物理 stock guard。
2. **Observed-rival sale pressure（谨慎）**：当 visible rival tile yield
   ≥ 8 且 market price > 1 时，只对当前已有 shed stock 的同物品提前销售，
   设单物品上限 8–24；不要读取 rival private shed。V37 的 `_r37_quote_priority`
   已做静态排序，但没有销售时点变化；该版本可作为 A/B 变量。
3. **Conditional tomato branch**：`TOMATO` 10-seed investment 只能在公开 shop
   条件、money ≥ 12k、price ≥ 70 且所有 qualification 成立时触发。Flex loss
   `108069646` 表明这条公开路线有收益，但 V37 的当前五 seed holdout 上
   `fert25` 产生了完全相同的结果；必须扩展到 `9006–9010` 双座和 20 个 holdout
   后再保留。
4. **Tie breaker 仅作实验**：在 `_r37_similarity>=0.99` 且连续 6 step 相同
   时，对一个可观测、低数量的非关键 SELL 做一次 1-turn shift。先在
   `1495252849` 及 9001–9020 双座检查是否把 tie 变为稳定正差；若出现任何
   负差，立即丢弃。固定按 seat 偏置不是可接受的默认策略。

## 已做实验

复制 V37 并把 `_r36_reserve` 的生效窗口从 `step >= 288` 扩展为 `step >= 144`
（其余代码不变）后，扩大面板得到：与 V37 的 20 个普通局（9001–9010 双座）
为 17 胜、1 负、2 平；另加 tie seed `1495252849` 双座均平局。唯一负局是
9004 的 seat 1（seat 0 为其镜像正局，说明差异来自共享市场座位顺序），因此
不是稳健超越。与 Flex 的 20 局则全部获胜，平均差约 3,910，但这只说明该
改动对 Flex 有益，不能证明胜过 V37。候选包为
`candidate_v37_reserve144.tar.gz`（SHA-256
`01aacdcce1a7fea018c21533a5096d79826914fee5e328e26364a39faad20d63`），已通过
编译和完整 720 步检查；仍不建议上传。

## 建议的验证门槛

每个候选单变量、独立文件、`py_compile` 后，至少跑 3 对手（Flex、Thomas、
Dmitrii）× seeds `9006–9010` × 双 seat（30 局），并额外跑 tie seed
`1495252849`。接受条件：无异常、所有 720 步 DONE；相对线上 V37 不得出现
负 margin；在 tie seed 上至少 `+1` 且其余 panel 平均 margin 正。未达到该
门槛的包只保留实验记录，不上传。

### Tie-break 原型实测

为验证“提前一单位销售”是否能破镜像，做了未打包实验：只在 player 0 的
step 648–695 追加下一步非关键产品的一单位 SELL，并在下一步扣除 debt。对
V37 的 tie seed `1495252849` 得到 player 0 `+21`，但把候选放在 player 1
时仍为 `0`；9001–9010 双座中 player 0 多数仅 `+1..35`，9004 player 1
为 `−1581`（对应 player 0 `+1622`）。这证明该原型是 seat-dependent，
不能作为候选默认策略，也不满足“完胜 V37”。
