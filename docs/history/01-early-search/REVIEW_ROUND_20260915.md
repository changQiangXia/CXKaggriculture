# 审查轮（Round 3）进行中/阶段性结果

本轮审查使用重启后的设备：16 CPU 配额、128 GiB cgroup 内存、RTX 4090 可见。Kaggriculture engine 为 CPU-bound，GPU 不参与决策。runner 使用 `/root/miniconda3/bin/python`、`debug=False`、8 个受控 worker；每局约 10–11 秒。

## 已完成的正确 paired 审查

`slot_rank_v1` 已使用正确的 no-R128 V42 parent 完成 4 对手 × 8 seeds × 2 seats × candidate/parent，共 128 行。所有行均 DONE/720、stderr 为空。candidate-parent paired delta：

| opponent | paired mean delta | paired min delta |
|---|---:|---:|
| v37 | 0.0 | 0.0 |
| Flex | 0.0 | 0.0 |
| Thomas | +2.06 | 0.0 |
| Dmitrii | 0.0 | 0.0 |

该分支的窄排序在当前 panel 中几乎没有触发可改变终局的动作，属于“安全但未证明有收益”，不晋级为提交候选。

此前使用 v37 作为 parent 的大面板只用于确认三条分支可以稳定完成 720 steps，不能用于策略晋级；该路径已纠正，后续只认 no-R128 V42 parent。

## 正在运行

`premium_front_run_v1` 与 `terminal_product_slots_v1` 正在用相同的 no-R128 parent、4 对手、8 seeds、双 seat 做正确 paired panel。结果写入各自 `paired_no_r128.json`，完成后再计算 mean/min/5% delta、负局和 telemetry。

## 晋级/停止规则

任何 crash、timeout、stderr 或非 720 steps 立即停止该分支。即使平均分提高，如果 5% 分位、min margin、负局数或 seat 方差恶化，也不晋级。所有分支只有本地审查结果，没有 Kaggle 提交授权。

## Activation telemetry 校核

单局 telemetry 复核显示：

- `slot_rank_v1` 在 seed 9001/9002 分别触发 1/5 个 SELL block，说明逻辑确实执行；但正确 paired panel 的终局 delta 基本为 0，仅 Thomas seat-1 出现 +4.12，未达到晋级标准。
- `premium_front_run_v1` 在两个 seed 均 `premium_triggered=0`；父 chassis 没有可用 `opponent_plan`/future tape，A0 的核心条件不可达。
- `terminal_product_slots_v1` 在两个 seed 均 `terminal_triggered=0`；step 718 的父 market 已满或 projected shed 没有可补商品，C0 不可达。

因此后两条分支的零 delta 不能解读为机制过时，只能解读为触发对象已经过时或当前 parent route 不暴露所需 future state。下一步若继续研究，应先更新 route/future-tape 对象并重新做 activation gate，再决定是否跑大面板；不能用零触发面板宣称无收益。
