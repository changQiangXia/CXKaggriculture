# v37 基底备选池

更新时间：2026-09-14 UTC。

本目录保存两个从冻结 `public_v37_pkg/main.py` 派生的候选。它们只改变 R37 horizon 的阶段级选择，保持生产、route、库存、weed、购买屏障、debt 和终局逻辑不变。两个候选均通过语法检查、独立打包检查，并有历史本地 720-step JSON 证据。

| 候选 | 唯一改动 | 当前状态 |
|---|---|---|
| [v37_h5sim96](v37_h5sim96/REPORT.md) | step 288–647、similarity ≥0.96 时 horizon=5 | rejected；Flex seed 9004 双 seat paired 退化 |
| [v37_h5sim95](v37_h5sim95/REPORT.md) | step 288–647、similarity ≥0.95 时 horizon=5 | rejected；Flex seed 9004 seat 0 paired 退化 |
| [v37_h5roomlow](v37_h5roomlow/REPORT.md) | v37_h5sim96 加 step-623 低机会成本容量排序 | rejected；seed 70117 出现 `-4` 且 runtime `2.60s`，保留为失败档案 |

## 验证纪律

- 证据来自本地 Kaggriculture engine，完整局为 720 steps、`DONE`；固定 opponent tape 只用于机制诊断。
- h5sim96 当前可确认的 0.96 证据包括 v37、Thomas 和 15 场 real-loss 归档；旧 Flex/Dmitrii 文件属于 threshold-0.90，不能混用。Thomas 的 `-556` 负边际使它不能晋级。
- h5sim95 的旧 public/Thomas 结果不含完整 runtime 元数据；当前新审计会重新采集 candidate/parent 配对字段。
- h5roomlow 的历史报告显示冻结 V37 22/22、Thomas 20/20，但可信 paired audit 已发现 `-4` 反例和 2.60s runtime，因此不再作为备选。
- 两个候选均未提交，也没有提交授权。后续若继续研究，必须按 `RESEARCH_CRITERIA.md` 补齐 confirmation、adversarial holdout、action-level delta 和尾部统计。
