# V37 本地扩展面板结果

环境：本机 `kaggle-environments`，`kaggriculture`，`episodeSteps=720`，每个 seed 运行 V37 与对手两个 seat 顺序。所有 186 场对局均完成 `DONE`，无异常记录。

## Seed 集合来源

组合了公开高分 notebook 中可复现的调参/holdout/smoke seed：

`7000,7001,7002,8000,8001,8002,9001..9020,184901,184902,20260907,451781128,70117`

共 31 个 seed、62 个 seat-run/对手。

## 结果

| 对手 | 胜 | 负 | 平 | 平均资金差 | 最差资金差 |
|---|---:|---:|---:|---:|---:|
| Flex v7 | 61 | 1 | 0 | +2960.7 | -1146 (seed 9019, seat 0) |
| Thomas replay | 61 | 1 | 0 | +7504.9 | -550 (seed 9004, seat 1) |
| Dmitrii v6 | 62 | 0 | 0 | +6120.2 | +1241 |

V37 候选包：[public_v37_candidate.tar.gz](public_v37_candidate.tar.gz)，压缩包 SHA-256 `4babc9e9d84a070eb72e006af6cf06ce435d7adab8db6c186540ca63daf055fa`。

## 评估边界

这是跨公开 seed 的本地筛查，不是 Kaggle 排名保证。V37 的公开 reacting 面板很强，但 elite panel 没有增加胜局；因此保留为高优先级待提交候选，仍需观察现有 active bot 的长期 rating 和对手分布后再决定是否替换。
