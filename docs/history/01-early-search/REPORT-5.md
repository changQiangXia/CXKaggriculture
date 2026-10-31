# v37_h5sim96

基底：`public_v37_pkg/main.py`。

单一改动：step 288-647 且 similarity >= 0.96 时 horizon=5，否则 horizon=4。

源码 SHA256：`ba08548ba46b3f6dda6dffc716aa1402fcfc75c69238e53a291fb04f07f463b4`  预测包 SHA256：`f0eaa2ddaa2a30c3ddc155fc4bfbc7ecf787738d881915fd8ed17a53e7252e47`

## 已有本地证据

| 数据集 | 场次 | 胜 | 负 | 平 | 平均 margin | 最差 margin | 720/DONE |
|---|---:|---:|---:|---:|---:|---:|---:|
| `h5sim_public_v37_pkg.json` | 22 | 22 | 0 | 0 | 2218.95 | 740.0 | 22/22 |
| `h5sim_ready_thomas_v6.json` | 20 | 19 | 1 | 0 | 6272.6 | -556.0 | 20/20 |
| `h5sim96_real_loss_results.json` | 30 | 30 | 0 | 0 | 2390.87 | 443.0 | 30/30 |

## 解释和限制

- 所有结果均为本地 Kaggriculture engine 的可追溯 JSON；固定对手 tape 只作为机制证据。
- 本报告只列 0.96 版本可确认的 v37、Thomas 和 real-loss 归档；旧 Flex/Dmitrii 文件来自 threshold-0.90，已排除。Thomas 仍有负边际。
- real-loss 归档只是复用线上 loss 的环境 seed、把对手替换成冻结 V37 的离线诊断，不是对原线上对手的修复证明；旧 JSON 也没有完整 stderr/status/latency。
- h5sim95 的补全面板即使完成也只是 candidate-only screening（无 paired parent、stderr/latency 元数据），不能替代 confirmation/holdout。
- 两个包均通过 `py_compile`，并在当前工作树重新打包；没有网络调用、submit 调用或隐藏未来状态。
- 该分支已触发 kill switch：Flex seed 9004 双 seat 的 paired delta 分别为 `-511`、`-421`，因此不进入 confirmation/holdout，也不晋级。完整证据见 [FINAL_AUDIT_SUMMARY.json](FINAL_AUDIT_SUMMARY.json)。

## 最终 paired audit 进度

详见 [PROGRESS.json](PROGRESS.json)。截至最近一次汇总，v37 对照已完成 16 个 paired，Flex 已完成 12 个 paired。整体 paired delta 均值约 `+1654.9`、最小 `-511`，负例来自 Flex seed 9004 seat 0；完整强对手面板仍未完成，不能外推到 private leaderboard。
