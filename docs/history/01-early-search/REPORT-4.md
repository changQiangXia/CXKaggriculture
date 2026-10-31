# v37_h5sim95

基底：`public_v37_pkg/main.py`。

单一改动：step 288-647 且 similarity >= 0.95 时 horizon=5，否则 horizon=4。

源码 SHA256：`d9777ac2090aef87d7bceafe8d7f298d2ecb0960e215bc8a08f22c3a7d30ee34`  预测包 SHA256：`8578ee9200d359006a468f3b05007e9ecfb66d5136e58a295fa1e0ae6a1a3ede`

## 已有本地证据

| 数据集 | 场次 | 胜 | 负 | 平 | 平均 margin | 最差 margin | 720/DONE |
|---|---:|---:|---:|---:|---:|---:|---:|
| `h5sim95_public_v37_pkg.json` | 22 | 22 | 0 | 0 | 2218.95 | 740.0 | 22/22 |
| `h5sim95_ready_thomas_v6.json` | 20 | 19 | 1 | 0 | 6271.3 | -582.0 | 20/20 |

## 解释和限制

- 所有结果均为本地 Kaggriculture engine 的可追溯 JSON；固定对手 tape 只作为机制证据。
- 旧 public/Thomas 归档是 0.95 版本结果，且 Thomas 有一场 `-582`；旧 Flex/Dmitrii 文件来自其它 threshold，已排除。
- 当前已启动带 runtime 元数据的 candidate/parent paired audit，结果落盘到 `serial_audit.jsonl`；完成前不能替代 confirmation/holdout。
- 两个包均通过 `py_compile`，并在当前工作树重新打包；没有网络调用、submit 调用或隐藏未来状态。
- 该分支已触发 kill switch：Flex seed 9004 seat 0 的 paired delta 为 `-511`，因此不进入 confirmation/holdout，也不晋级。完整证据见 [FINAL_AUDIT_SUMMARY.json](FINAL_AUDIT_SUMMARY.json)。

## 最终 paired audit 进度

详见 [PROGRESS.json](PROGRESS.json)。截至最近一次汇总，v37 对照已完成 16 个 paired，Flex 已完成 6 个 paired。Flex seed 9004 seat 0 已出现 paired delta `-511`，与 h5sim96 相同；当前整体 paired delta 均值约 `+1629.2`、最小 `-511`。Thomas/Dmitrii 和最终 holdout 尚未完成，不能外推到 private leaderboard。
