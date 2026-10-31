# MODEL_FINAL_REVIEW — 2026-09-15 UTC

本轮目标是对两个备选模型做最终一次代码审阅，并在本地 Kaggriculture engine 中验证。没有调用 Kaggle submit，也没有向线上写入任何内容。

## 审阅范围

审阅对象：

- 独立规则模型：[guts/main.py](research_20260915_125615UTC/guts/main.py)，SHA-256 `1af1b93c72c174c008375fa5ebd1f9a935d0ec815cd1972341921988dcf55a1e`。
- 受优秀提交启发的模型：[inspired_premium_v1/main.py](incubated_candidates/v42_ablations/inspired_premium_v1/main.py)，最终 SHA-256 `91d5a7147ab648e2d86b91425c8d7c0d6e4a704ad73433dad58577577b2c2079`；打包文件为 `inspired_premium_v1.tar.gz`，SHA-256 `1a32387645794c2fb6280286236a10dbd37c9e09fc46bdc23d20914aa58ef76b`。
- 冻结 parent：`incubated_candidates/v42_ablations/no_r128/main.py`，SHA-256 `08b6ee9a4e5a4bf2ad6d76140b89426cddac68808d7a623b3f957722ea067716`。

审阅检查了 action shape、720-step 终止、market 最多 10 条、locked tile 行为、private state 边界、seat/episode 状态重置、parent fallback、未来信息来源、SELL 数量和 repayment debt。

## 发现与修复

`guts_` 没有引用公开 agent、replay、线上 log 或对手私有状态，也没有未来 tape 泄漏。它的问题是策略闭环明显不完整：没有动物管理、严格的 shed/cash ledger、复杂 route/pickup/drop 规划和充分的 terminal policy；固定的种植和售卖规则会在强 parent 已经优化的场景中损失大量收益。代码可以稳定运行，但不具备提交竞争力。

`inspired_premium_v1` 的第一次最终审阅发现三个真实风险：Round-2 debt 检测会把 parent 原本的 SELL 误认为 wrapper 新增订单；偿还后可能留下数量为 0 的 SELL；repayment telemetry 跨 episode 累加。最终版本已作如下修复：

1. 用 `_INS_LAST_TRIGGER` 记录本次调用实际追加的商品和数量，只对该订单建立下一回合 debt；
2. repayment 完成后删除数量小于等于 0 的 SELL；
3. step 0 清零 repayment 计数和旧 seat trigger；同时清零 per-episode calls 计数。

该模型仍有一个策略层限制：premium 触发依赖静态 `_IMPL` route suffix，而 parent 后续 wrapper 可能动态改写动作。因此 trigger 为 0 时只能证明当前状态未激活，不能证明机制在所有状态都无效。当前 benchmark 中 trigger 确实为 0，模型与 parent 完全等价。

## 本地测试

运行器使用 `/root/miniconda3/bin/python`、`debug=False`、Kaggriculture `episodeSteps=720`。每场都检查 `DONE`、720 steps 和 stderr。

### guts 全量 paired panel

4 个对手族（v37、Flex、Thomas、Dmitrii），8 个 seed（9001、9002、9003、9004、9005、9006、70117、184901），双 seat，共 128 rows，全部 DONE/720、stderr 为空。相对 no-R128 parent 的 paired margin：

| 对手族 | 局数 | 平均差值 | 最小 | 最大 | 负局数 |
|---|---:|---:|---:|---:|---:|
| v37 | 16 | -157,069.2 | -186,489 | -122,604 | 16 |
| Flex | 16 | -181,132.2 | -218,941 | -137,480 | 16 |
| Thomas | 16 | -156,936.9 | -183,573 | -125,977 | 16 |
| Dmitrii | 16 | -162,643.4 | -191,997 | -122,254 | 16 |

这不是小幅回撤，而是系统性落后；guts 不得进入提交候选。

### inspired_premium_v1 最终 paired panel

最终冻结文件上重新运行 4 个代表 seed（9001、9002、70117、184901）、4 个对手族、双 seat，共 64 rows。全部 DONE/720，stderr 为空，最终文件 SHA 与每一条 candidate row 一致。每个对手族 8 个 paired rows 的平均、最小、最大差值均为 0，非零差值为 0：

| 对手族 | paired rows | 平均差值 | 最小 | 最大 | 非零 |
|---|---:|---:|---:|---:|---:|
| v37 | 8 | 0 | 0 | 0 | 0 |
| Flex | 8 | 0 | 0 | 0 | 0 |
| Thomas | 8 | 0 | 0 | 0 | 0 |
| Dmitrii | 8 | 0 | 0 | 0 | 0 |

单独 smoke：seed 9001 对 pass、seed 9002 对 pass 均 DONE/720、无错误；telemetry 为 `triggered=0`、`repay_attempts=0`、`repay_complete=0`、`repay_fail=0`、`errors=0`。重复 episode 检查确认 step 0 会重置 repayment 计数。

## 决定

- `guts_`：保留为独立范式和失败对照，不提交。
- `inspired_premium_v1`：代码质量和 parent 等价性已达到本轮测试门槛，但当前触发率为 0、收益证据为 0，只能标记为研究分支，暂不提交。
- 当前没有模型获得“可提交”结论。若要形成真正候选，下一轮应先构造可验证的 activation state（确认 future suffix 与最终 parent action 一致），再在未见 seed、未见对手和双 seat 上证明正向 delta；不能把本轮零差值当成线上提升。
