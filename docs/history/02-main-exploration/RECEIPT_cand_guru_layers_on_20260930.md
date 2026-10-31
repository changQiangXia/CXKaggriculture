# 收据：cand_guru_layers_on（GURU 底盘 × 镜像门 × rmax96 × 自带五层全开）

**日期**：2026-09-30　**血统**：GURU route-replay 编译器底盘 + 我们的两层移植
+ 他底盘自带的 5 个反应层重新启用。**未提交**。

## 1. 与 v1（cand_guru_mirror_rmax96）的差异

他底盘源码里 `_SETTINGS` 把自己设计的五个反应层关掉了：
`budget_guard / room_guard / clamp_sells / dead_stock / terminal_liquidation = False`。
本候选把它们全部打开（`hand_align / weed_repair / sell_lead` 本来就开着）。

## 2. 实测（三件套 + 分解）

| 仪器 | 底盘基线 | v1（镜像+rmax96） | **v2（五层全开）** |
|---|---:|---:|---:|
| 当前池 168 局（raw） | 94W/74L +4,498 | 97W/71L +4,539 | **99W/69L +4,851** |
| 当前池（fid≥0.95 过滤） | 51W/64L | 53W/60L | **54W/58L** |
| 对原底盘（镜像 H2H，24 局） | — | 20W/4L +502 | 18W/6L +414 |
| 对 slh48（16 世界×双座） | 0-32 −1,089 | 2-30 −1,072 | 2-30 −1,099 |
| 1600-2000 门 | — | 179W/51L | **183W/47L（79.6%）** |
| <1600 门 | — | 163W/3L | 162W/4L（97.6%） |

**层分解**（当前池 168 局）：
* layA = budget_guard + room_guard：97W/71L **+4,707**（胜数不变、margin +168）；
* layB = clamp_sells + dead_stock + terminal_liquidation：**99W/69L +4,690**（+2 胜）；
* 五层全开：**99W/69L +4,851**（+2 胜、+312 margin）⇒ 采纳全开。

其他筛查（均为惰性/负，留档）：
* `_HD2_OPTIONS` 加 GOOSE（蛋特化）：H2H 2-2/20 平、池子 97/71 不变 ⇒ 惰性；
* 定线扫描 41 条路线：当前 router ≈ route 0 最优，其余全差 ⇒ 改路由证伪（见 v1 收据 §7）；
* 路由覆盖：`rkey→128` 惰性；清 YARN→9 改走 R108 表更差（95/73）。

## 3. 包

* `cand_guru_layers_on.tar.gz`
  * tar sha256 `49758bdedd576f20d3b96dfaac6ae33465b55ee771678b7f08645cc169d46650`
  * main.py sha256 `370422d72d5a3e456801bc3f0187b6a9c579deaf6cde0ff011b5868822f9d3cb`
  * `kcheck`：entry = `kaggle_entry` OK；smoke 88,582（门槛 50,000）双 DONE。
* 变体留档：`cand_guru_hd2goose`、`cand_guru_layers_on`（=v2）、
  `cand_guru_mirror_rmax96`（=v1）、`cand_guru_mirror_m150/m200`、`cand_guru_v_sloth16` 等。

## 4. 下一步

* 剩余结构缺口：大败局里对手 **小麦 −129 / 鸡蛋 −69 / 番茄 −25**（both_flow 168 局）；
  五层全开已回收 +2 胜，但产出结构未变（路线固定、41 条路线全部 TOMATO=0）。
* 下一步优先级：① 尝试 `V9_HERD` 系（羊↔牛）参数微调与鹅的进一步扩展；
  ② 编译器级：给 route 0/110 插入番茄轮作（用空闲动作槽）；
  ③ 继续在池子上筛我们方剩余端点（V9_CARROT/V9_FERT/OR2 组合）。
* 纪律照旧：任何改动必须过「当前池 + slh48 + 低分段门」；提交需用户批准。
