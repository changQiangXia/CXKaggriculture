# Nathan pipe-4 谨慎优化五轮记录

Parent 是 Nathan Jacob 的 pipe-4 解码源码，SHA-256 为 `7a37397fdb29cbbb17aaf7577352bef910fb4dd0f19bf763b9dcaff68595da54`。没有读取对手私有状态、没有引入线上 log、没有复制新的固定 tape，也没有提交 Kaggle。

## 第 1 轮：基线和可观测性

先确认 pipe-4 的差异集中在 step 0–1 的 conditional opening，并对源码做 `py_compile` 和完整 720-step smoke。新增的第一轮 wrapper 只增加 per-episode `calls/errors` telemetry，不改变任何有效 action。seed 9001 和 9004 对 Ahmed V43 均 `DONE/720`。

## 第 2 轮：market action 边界

增加严格的 malformed-order guard：保留合法订单，删除数量小于等于 0 或非列表订单，最终截断到最多 10 条；合法 parent action 不改写。该修改针对 Kaggriculture 的 ordered market 和 silent overflow 规则，避免 wrapper 或 route 产生无效订单。

## 第 3 轮：配置和 route 安全

增加标准配置检查。遇到非标准 board、turns/day、shed capacity 或 market order limit 时不尝试额外逻辑，回退安全 PASS 结构。标准 Kaggriculture 配置的动作保持不变。四场 smoke 均正常完成；没有观察到额外回退。

## 第 4 轮：day 9–11 cow 假设消融

Nathan 在 Notebook 中指出 C9 可能在 day 9–11 购买更多 cow。先做 guarded ablation，只统计该窗口，不注入 cow 订单；随后测试了基于实际 route future wheat demand 的动态 bakery gate，只有 route 自己明确需要至少 15 单位 wheat 时才恢复 wheat flip。该 gate 在 smoke panel 上没有改变最终动作或现金，因此没有把未经证实的 cow tape 或 route 替换合入最终版。

## 第 5 轮：最终保守版本

最终版本只保留第 2 轮的合法订单 guard 和 per-episode telemetry，删除 speculative cow injection 与不必要的 route 改写。有效 parent action 保持等价，降低线上 runtime 风险。

最终文件：[main.py](nathan_cautious_final/main.py)。压缩包：[nathan_cautious_final.tar.gz](nathan_cautious_final/nathan_cautious_final.tar.gz)。

## 测试结果

对每个 round variant 使用 seed 9001、9004、双 seat 与 Ahmed V43 运行，共 40 场（5 个版本 × 2 seed × 2 seat；另含动态 bakery 消融），全部 `DONE/720`。最终 round-5：

| seed | seat 0 candidate cash | seat 0 Ahmed cash | seat 1 candidate cash | seat 1 Ahmed cash |
|---:|---:|---:|---:|---:|
| 9001 | 109,226 | 109,225 | 109,225 | 109,226 |
| 9004 | 91,665 | 90,153 | 91,664 | 90,154 |

结果与 parent pipe-4 一致，没有新增负差。engine 输出的 `pokerkit`/`pydantic` warnings 来自未使用的可选环境，不影响 Kaggriculture 运行。

## 当前判断

这五轮没有找到可证明提高最终资金的安全 gameplay 改动；找到的是一个更容易审计的候选包装和 action guard。seed 9004 的 +1512 仍然是 Nathan 开局相对 Ahmed 的单点差异，不能视为泛化收益。下一轮若要继续提升，应针对 day 9–11 cow preference 建立独立 route/seed holdout，再决定是否做真正动作修改。

**未提交 Kaggle。**
