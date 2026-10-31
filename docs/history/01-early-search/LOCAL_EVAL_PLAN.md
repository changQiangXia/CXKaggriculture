# Kaggriculture 本地对抗验证计划

## Seed 来源

为避免只在自选 seed 上调参，验证集合来自已下载的公开高分 notebook：

- Ray Kretzschmar rank-your-agent：tuning `[7000,7001,7002]`、holdout `[8000,8001,8002]`，以及建议的 `[9001..9020]`。
- Tetsutani adaptive farming：展示/回归 seed `70117`。
- Dmitrii herd-safe sale window：公开回归 seed `184901,184902`。
- Boatlee V16-RC5：公开归档 smoke seed `451781128`。
- Thomas replay-routing：公开引擎 smoke seed `20260907`。

当前组合集合为：

```text
7000,7001,7002,8000,8001,8002,
9001..9014,184901,184902,20260907,451781128,70117
```

这些 seed 只用于本地验证，未用于任何未来信息读取或线上提交。

## 运行门槛

每个候选与 Flex、Thomas、Dmitrii 三个公开方案进行 720 步完整对局，并在两个 seat 顺序运行。保留：

- 胜/负/平和平均资金差；
- 最差资金差与 seat 差异；
- `DONE` 完成率、异常数和 action latency；
- 单文件解压后的独立加载结果。

公开讨论建议同时保留完全未调参的 holdout seed，并警告不要把初始 rating 或单次 bank 当作最终强度；因此只有跨来源 seed、双 seat、多个对手一致改善的候选才进入待提交清单。

## 当前运行

V37 候选的扩展面板已在后台运行，结果写入 `/tmp/v37_panel.out`。这只是本地证据收集，不会调用 Kaggle submit；提交仍需用户明确点名候选并授权。
