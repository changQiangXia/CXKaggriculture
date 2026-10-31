# v37 备选孵化阶段最终审计

日期：2026-09-14 UTC

本轮以冻结 `public_v37_pkg/main.py` 为父策略，孵化并实际打包了两个 horizon 备选：

- `v37_h5sim96`：step 288–647、公开相似度 ≥0.96 时 horizon=5；
- `v37_h5sim95`：step 288–647、公开相似度 ≥0.95 时 horizon=5。

两者均通过 `py_compile`，tar 根目录只有 `main.py`，源码和包 hash 已记录在各自 `MANIFEST.json`。没有调用 Kaggle submit。

## 可信 paired 结果

每局重新加载 candidate 和 parent，固定相同 seed、对手和 seat，保存双方 reward、margin、最终 status、stderr、720 步、最大 action duration 和耗时。结果文件为各候选的 `serial_audit.jsonl`，摘要为 `FINAL_AUDIT_SUMMARY.json`。

| 候选 | paired 场次 | 对手 | paired 平均 delta | 最小 delta | 负 paired |
|---|---:|---|---:|---:|---:|
| h5sim96 | 30 | v37 16、Flex 14 | +1545.5 | -511 | 2 |
| h5sim95 | 22 | v37 16、Flex 6 | +1650.9 | -511 | 1 |

负例集中在同一机制场景：Flex、seed 9004、seat 0/1。h5sim96 分别为 `-511`、`-421`；h5sim95 seat 0 为 `-511`。这些不是 candidate 输掉的局，但相对 v37 的资金差明显下降，违反“负局数/尾部不恶化”门槛。h5sim96 的历史 Thomas 面板还有 `-556`，h5sim95 有 `-582`；旧 Flex/Dmitrii JSON 因阈值错配已排除。

所有已完成的本轮 paired 局均为 720 steps、双方 `DONE`、stderr 为空；历史 JSON 缺少完整 runtime 字段，不能用来替代本轮审计。

## 决策

两个候选均标记为 `rejected_tail_regression`，保留完整源码、tar、JSONL 和摘要作为研究档案。审计进程已在触发预注册 kill switch 后停止，避免继续消耗 4090 资源；不把未完成的 Thomas/Dmitrii 对局伪装成通过验证。

这轮孵化的结论是：单纯扫描 h5 horizon 相似度阈值不能稳定突破 v37，且两个阈值点不是互补的独立策略族。若重启研究，应按 `design_review.md` 的 H-DSS 方案重建阶段级现金–货运账本，再进行新的 confirmation/holdout；不能继续在 0.95/0.96 附近调阈值。
