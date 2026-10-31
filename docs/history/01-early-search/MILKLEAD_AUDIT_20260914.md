# MILKLEAD 证据审计（2026-09-14）

这份审计只核对已经做过的本地实验和 replay harness，不修改候选源码、归档包或监控进程。结论是：原来的 `MILKLEAD_EVAL_20260913.md` 将几个不同面板的均值混在了一起；`cap2_replay_cf.json` 也不是 MILKLEAD 的配对证据。

## 数值更正

`/tmp/cap2base.out` 是 cap2 与 `public_v37` 在 seeds 9001–9005、双 seat 的完整 10 局结果：

```
cap2:       10 胜 / 0 负 / 0 和，mean margin 1815.1，min 740
```

该均值由 10 个数直接计算得到：

```
1702, 1702, 1233, 1233, 2453, 2453, 4546, 1349, 740, 740
```

因此，若比较的是这一个 9001–9005 双 seat 面板，基线确实是 **1815.1**，不是报告中所写的“约 2050”。旧报告里的 `+2050` 没有对应到一个可追溯的完整 cap2 输出，应视为记录错误。

已存在的 `h5sim96_cap2_milklead.py` 同面板输出为：

```
MILKLEAD:  10 胜 / 0 负 / 0 和，mean margin 1817.7，min 740
相对 cap2: +2.6 mean（总和只多 26）
```

该版本在完整 9001–9010 双 seat 的另一份输出中是 cap2 `2114.25` 对 MILKLEAD `2122.45`，差值 `+8.20`；这个 `+8.20` 本身对应 20 局面板，但不能拿来描述 9001–9005 的 10 局结果。两组数字都保留，使用时必须注明面板范围。

`h5sim96_cap2_milklead_allsteps.py` 的 9001–9005 双 seat 输出是 `mean 1935.5`、10/10 胜、min 1192；相对 1815.1 为 `+120.4`。不过它**不是 MILK 单变量实验**：与 `h5sim96_cap2_milklead.py` 的源码 diff 同时改了两个位置：

1. 父级 route planner 去掉了 `step % 4 == 0` 的跳过条件；
2. MILKLEAD 自身也去掉了 `step % 4 == 0` 的稀疏条件。

所以 `+120.4` 不能归因于 MILK 提前销售，亦不能作为 cap2 上稳定提升的证据。当前唯一干净的 MILKLEAD 对照是 `+2.6` 的 9001–9005 面板和 `+8.2` 的 9001–9010 面板；两者都很小，且公开对手 holdout 中 Flex 轻微下降、Thomas 保留同一负边际，故不满足提交门槛。

## Replay seed 审计

在线 replay 的 `configuration.seed` 通常是 `null`，实际随机种子在 `info.seed`。抽查到的例子：

| replay | `configuration.seed` | `info.seed` |
|---|---:|---:|
| 108577135（validation） | `None` | `0` |
| 108587805 | `None` | `841334472` |
| 108400163 | `None` | `1079744235` |

固定 replay 反事实必须复制配置后显式设置：

```python
cfg = dict(replay["configuration"])
cfg["seed"] = replay["info"]["seed"]
```

此前 engine parity 审计已经用这一规则在四个独立线上 replay 上逐状态比对，720 个状态均无语义分歧，且本地最终 reward 与线上 reward 完全相同。这一部分说明 seed 选择是必要条件，而不是可省略的实现细节。

## Replay action 的时间校准

replay 的 index 0 是 reset observation 和占位动作。环境在 observation `step=t` 调用 agent，动作被记录在**下一条** replay row `steps[t+1]`；因此固定对手 tape 应写成：

```python
def fixed_opponent(obs, config=None):
    t = int(obs.get("step", 0))
    return copy.deepcopy(tape[min(t + 1, len(tape) - 1)])
```

这与 `experiments/h5_engine_audit/ENGINE_PARITY_REPORT.md` 中“action at index `i` is applied from state `i-1`”一致，也由本地短环境调用顺序复核：agent 首次看到 `step=0`，而 row 0 仍是 reset 占位动作，随后 `step=1` 的 row 1 才包含 step 0 决策。

因此：

- `/tmp/replay_cf_cap2.py` 和 `/tmp/replay_cf_cap2_new.out` 所采用的 `t+1` 对齐是正确方向；
- `/tmp/replay_counterfactual.py`、`/tmp/cf_one.py`、`/tmp/cf_compare.py` 使用 `tape[t]`，会把对手动作错一回合，不能用来估计 MILKLEAD 的收益；
- `day2_gold_variants/cap2_replay_cf.json` 使用的是旧 **cap2**（不是 `h5sim96_cap2_milklead.py`），即便其 12 局 replay 对齐正确，也不能证明 MILKLEAD 有收益。它只能作为 cap2 机制诊断档案。

## 审计结论与后续使用规则

当前没有可据此提交的 MILKLEAD 证据。下一次 MILK 实验若要作为候选依据，必须同时满足：

1. 父级 route planner 不变，只改变一个 MILK 门控条件；
2. seed 使用 `info.seed`，并把 action tape 对齐到 `t+1`；
3. 至少报告 cap2 与候选的同一 seeds、同一 seat、同一对手，以及逐局 margin；
4. 公开面板、三份高分对手面板和真实 loss replay 分开报告，不能合并均值；
5. 真实 replay 结果只作为机制诊断，不能替代自适应交互面板。

在满足这些条件并出现稳定、跨面板的正边际之前，MILKLEAD 保持研究状态，不进入待提交队列。
