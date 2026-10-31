# Q20/Q25 规则、资源与泛化审计（2026-09-17）

## 审计范围

对象为 `candidate_v45_q20.py`、`candidate_v45_q25.py`，冻结控制为
`customerUpload/kaggle/v45_extracted.py`。审计同时检查已有 opening matrix、
非 opening 原型、线上 replay fingerprint、官方 README/AGENTS 和本地引擎
parity 记录。未修改候选，未执行 Kaggle 提交。

## 代码身份和实际行为

对三个源码做了 AST 解析和逐文件 diff。Q20/Q25 与 V45 的唯一差异分别为：

```text
_OPEN_UNITS = 70  -> 20 / 25
```

当前冻结校验值：Q20 source `ea2ca3b2875534b7e7a5941339e43c610564dfe7af4b3eb33bad7fcbc7aabc6d`、archive `c9a1789a5c65119d4a5779c72c7b7554f2f5a5522053c10897a5b6aca3be9751`；Q25 source `80b0c33bbb0c33626374cd18dd7922a82b6d7133798a2e5d5b5008cae1a20fde`、archive `a53bc374f5bc8e33ace631c178b7c46e359c449d7a6a31b83ca0f9ff6185a95b`。两个 archive 都只含根目录 `main.py`，解包后与 source 逐字一致。

两个包都保留 V45 的 route library、R124/R127/R128 供料和服务层、clone-gated
race、terminal planner 以及 fallback。因而候选相对 V45 的 paired delta 可以
主要解释为首回合 opening 造成的共享市场和随机流变化；不能把差异归功于
任何新的中后期生产或销售方法。

## 规则约束的直接影响

官方 README/AGENTS 与工作区副本 hash 一致。比赛默认 720 turns，最后 callback
为 step 718；market 每玩家每回合最多 10 个有序订单，订单按双方同 index
逐单位处理；town/shop 消耗、shop unlock 和部分市场行为使用同一随机流。
因此首回合把父动作

```text
BUY_PRODUCT WHEAT 5; BUY_PRODUCT WHEAT 10; SELL WHEAT 60
```

改为单一 20 或 25 单位 round trip，会改变双方后续报价顺序，并可能改变
后续 shop draw、route 分支、产量和价格。它不是“自家买卖净额为零”的局部
改动。公开 tape 可以发现这种机制，但不能证明在另一策略或另一 seed 上仍
有同号收益。

## 现有证据的强度

### 目标 opening 家族

严格 paired matrix 使用相同 seed/world、双 seat、720 steps，所有局 DONE 且无
stderr。Q20 在已跑的 Q5/Q50/Q70/Q85 synthetic opening 上均为正（均值约
`+205/+2640/+1340/+59`）；Q25 的对应均值约 `+200/+2700/+1400/+208`。
这些结果说明数量 20–25 能稳定解除当前 Q70 mirror，并削弱 Q5 对 Q85 的
风险。但这些 opponent 文件只固定首回合 opening，不能替代完整公开 agent
lineage，也没有覆盖 sell-first、非 wheat 或自适应首回合。

### 非 clone lineage holdout

Q20 fresh seeds 9010–9013（双 seat）：

| lineage | mean Δ | P10 | 最差 | 正/负 |
|---|---:|---:|---:|---:|
| V37 | -1856.75 | -3816 | -3816 | 2/6 |
| Flex | -2265.75 | -4603 | -4603 | 2/6 |
| Nathan | 0 | 0 | 0 | 0/0 |

Q25 seeds 9010–9011（双 seat）：V37 mean `-727`、最差 `-3259`（2/4 正）；
Flex mean `-1714.5`、最差 `-4603`（2/4 正）。这些结果属于完整交互的
非 opening synthetic holdout，显示首回合扰动在不同路线下可放大为数千现金
损失，已经不能满足既定 Confirm 门槛（族均值正、P10/最差风险受限）。

### 线上混合粗估

当前收集的 36 局中 Q70 22、Q5 round-trip/single 9、Q50 2、Q85 1，其余
非标准 2。按已测 synthetic opening delta、对未知 opening 设为 0，Q20/Q25
的已知部分约 `+1018/+1061`；未知 opening 每局惩罚 `-2000` 时仍约
`+907/+950`。这不是置信区间：36 局包含 17 个高度相关 mirror tie，Q85
比例 Wilson 上界 14.2%，且未知 opening 的真实 delta 没有观测。将 V37/Flex
负尾纳入后，整体方向无法保证。

## 非 opening 资源审查

已有原型没有形成第二条稳健改进路线：

* `slot_rank_v1` 相对 no-R128 parent 的 64 个 paired rows 只有 1 个正差，
  63 个为零，均值约 `+0.52`；
* `premium_front_run_v1` 和 `terminal_product_slots_v1` 各 64/64 为零；
* `inspired_premium_v1` 32/32 为零，且静态 future route 不能代表 R128 实际
  改写动作，存在 debt 误识别/repayment 失配风险（已见 `agent_review_notes.md`）。

V45 的 race 层不是新的候选变量。已有小型消融显示其相对关闭 race 在 V43
约 `+1347`、Nathan `+1909`、V37 `+4.8`、Flex `-31`，效应依赖同路线程度，
不能用来证明跨族稳健提升。

## 结论和晋级建议

Q20/Q25 有明确的 anti-Q70 opening 机制证据，但证据只支持“当前观测 opening
池上的条件 exploit”。完整 lineage holdout 已显示显著负尾，故目前不能说
二者有较大把握把线上最高分从约 2650 再提高，也不能用本地 synthetic matrix
的高胜率替代线上泛化证明。Q25 在 Q85 层比 Q20 更稳，Q20 数量更保守；二者
只是风险不同的 opening 版本，并非两个独立范式。

提交前至少需要冻结代码后对 V37、Flex、一个动态非 wheat opening 和一个
sell-first opening 各做 16–24 个未调参 seed cluster、双 seat，并记录
baseline/realized opening migration、有效 market 成交、shop/产量路径和
72-step 账本。未通过族均值、尾部和 leave-one-lineage-out 门槛前，不应宣称
“高把握超过 2650”，更不应在未经用户许可时提交。
