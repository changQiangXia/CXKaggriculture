# 修改轮（Round 2）执行报告

基线：`incubated_candidates/v42_ablations/no_r128/main.py`。本轮建立三个独立 A0/B0/C0 研究分支，未提交 Kaggle。

## 分支

- `slot_rank_v1/main.py`：B0，day 18–28 连续长度 2 的 SELL block，按公开 quote pressure 排序；不合并、不拆分、不改数量。
- `premium_front_run_v1/main.py`：A0，day 24–28、非 town 边界、MILK/WOOL/MELON/STRAWBERRY，每项最多前移 1 单位，使用下一回合 repayment debt。
- `terminal_product_slots_v1/main.py`：C0，仅 step 718，在父 market 未满槽且 projected shed 有库存时追加最多 1 个 MILK/WOOL SELL。

每个分支均包含 `MANIFEST.json` 和独立 tar.gz，默认开关逻辑在 wrapper 中保持研究性质，不影响原始基线文件。

## 验证

三个分支均通过 `python -m py_compile`，并通过动态 import smoke，telemetry 字段可访问。slot_rank_v1 与 v37 seed 9001 seat 0 的单局运行完成 `DONE`、720 steps、margin +27819；随后运行由于 Kaggle 本地环境深层 deepcopy/engine 运行超过 150 秒而中断，属于验证基础设施耗时，不是候选 action 报错。尚未进行 40/120 局 paired panel，因此任何分支都不可晋级、不可提交。

## 后续

审查轮需先检查 wrapper 与父层 `_R128` 状态、确认每个开关是否真正触发，再运行统一 40 局筛选面板。若出现 timeout、stderr、非法 action、负尾部退化，立即回退 no-R128 基线。
