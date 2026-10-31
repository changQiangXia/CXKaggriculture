# Ahmed V43 — 五轮深入研究（2026-09-15 UTC）

研究对象：[Kaggriculture V43: Recovering Lost Harvests](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v43-recovering-lost-harvests)。Notebook 已通过 Kaggle CLI 拉取并解码为 `decoded_main.py`，源文件 3,366 行、SHA-256 `919fc1d61050cd96f799979e49177ae3ac7bce98ec9835724238bea73f4a08ed`。

## 第 1 轮：作者自述、目标与边界

Ahmed 将 V43 定义为一次针对仓库溢出的定向修复：farm hand 在黎明返回时，携带货物可能超过共享 shed 容量，超出的货物会被丢弃。作者的核心承诺是只在“本来会被替换并丢弃”的情况下提前销售现有库存，并使第二天完整库存向量保持不变；原有田间动作和 market-order 前缀保持不变。作者明确说明 notebook 不需要数据集、GPU、互联网或安装，也不会自动提交。

作者还把性能优化与策略改动分开：普通 Python 容器的复制和距离计算被专门化，但声称每个动作保持不变。V43 的说明强调这是一个仓库损失恢复机制，而不是新的生产经济学。

## 第 2 轮：实现机制审计

解码源包含完整 route/chassis，并在 `_r148_overflow` 中根据当前 shed、未来返回货物和订单前缀估计 dawn 后库存；只有能证明销售不会改变次日库存向量时才插入销售。`_r148_atomic` 处理种子不足时的原子种植请求，删除无法满足的请求以避免引擎取消整批种植。后段还保留 route proposal planner、seed prefunding、服务和 terminal 保护等历史层。

wrapper 通过 `_R148_REPORT` 记录 overflow turns、reclaimed units、contract checks/errors 和 atomic counters，并在 step 0 重置 per-episode 状态。默认配置要求标准 board/turn/day/shed/order 上限；异常时回退原动作。代码不读取对手私有 shed/inventory，也没有外部网络依赖。

## 第 3 轮：作者实验与统计主张

作者报告的表格显示：Development V43 为 99/0/13，Development V42 为 87/3/22；Independent V43 为 412/10/26，Independent V42 为 375/14/59；直接独立 V43 对 V42 为 39/3/22、严格胜率 60.94%、平均现金差 +116.86。作者还报告 32 个 reserved worlds 上 own cash +96.14、relative margin +124.88、match points +4.58 个百分点，并给出 bootstrap 95% 区间。

作者明确提醒 reacting panel 的七个配置不是七个独立精英队伍，历史录制不能对改变后的动作作出反应；排除 V42 后，384 局结果的 match-point 增益只有约 +0.65 个百分点。作者称 448 个 candidate/control pairs 通过现金和产品账本核对，仓库损失从 5,713 降到 4,376 单位。原始 EXP277/278 的 Windows timing 检查失败，发布的 EXP279 才通过单独进程测量。

## 第 4 轮：本地复核与泛化风险

本地使用 `kaggle-environments 1.25.9`、`debug=False`、720 steps 对解码 Ahmed 源做了可运行性验证；源可编译，能在 engine 中完整结束。与 Nathan 的 pipe-4 解码源在相同 seed 的直接对局中，四个 seed、双 seat 全部 `DONE/720`，双方最终现金只差 1，说明两者大部分 chassis 行为等价，差异主要来自 turn-1 route opening。

风险在于作者的收益主要是小幅现金和仓库损失改善，不能直接推断 leaderboard 大幅提升；历史录制和 reacting panel 的相关性会夸大统计独立性。overflow 合同依赖对未来返回和 dawn 替换的正确估计，任何 route 动态改写、配置变化、订单排序变化都可能使守护层回退或失效。作者自己也把 V43 描述为 targeted improvement，而非保证 rating 的新经济系统。

## 第 5 轮：可迁移结论

可迁移的范式是“先做物理账本，再做动作改写”：在插入销售前验证 shed 容量、返回货物、市场顺序和次日库存向量；失败就保留 parent 动作。第二个范式是把原子操作拆成可验证的请求并记录确认，而不是盲目增加动作。第三个范式是将性能重构与策略修改分离，用动作级 replay 和最终 reward 双重等价性证明没有意外行为变化。

对我们的模型研究，V43 最值得吸收的是 contract-based overflow guard 和 action-preserving fallback；最不应直接复制的是未经同分布 holdout 验证的统计胜率，以及依赖静态 route suffix 的局部销售时机。作者的完整 attribution/Apache-2.0 说明保留了多个上游来源，并明确“credits do not imply endorsement”。
