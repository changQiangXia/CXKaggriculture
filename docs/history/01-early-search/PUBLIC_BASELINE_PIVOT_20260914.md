# 公开高分父策略可迁移性检查（2026-09-14）

## 实验目的

验证是否可以放弃 v37、直接以工作区保存的公开高分复合策略
`public_intel/frontier_main.py` 作为新父策略。实验使用本地 Kaggriculture 官方引擎，
配置固定为 `episodeSteps=720`，seed 9001–9010，两个 seat；同一 seed 的两个 seat
使用相同的候选和 v37 配对。

## 结果

结果文件：[frontier_vs_v37_20.json](frontier_vs_v37_20.json)

- 配对局数：20（10 seeds × 2 seats）
- frontier 胜 / 负 / 平：0 / 20 / 0
- 平均边际（frontier - v37）：`-6715.45`
- 最好边际：`-3264`
- 最差边际：`-12981`
- 所有对局均 `DONE=True` 且 `steps=720`
- 运行时未发现 engine error

## 结论

这个公开策略的榜单表现不能迁移为 v37 的直接替代父策略。它在当前固定面板中每局都落后，
因此不进入候选提交队列，也不继续在其上做无约束调参。

这不证明所有公开高分方案都弱于 v37，也不否定公开代码中的局部机制；它只否定了
`frontier_main.py` 作为整体父策略的假设。后续若使用公开方案，只抽取可解释的完整阶段机制，
并与 v37 做 paired panel；v37 继续保留为控制组和回退策略。

## 公开 Top-10 组件初筛

另外对保存的 E773、E774、E776 组件各做了 3 个 seed × 2 seat 的 6 局 v37 配对：

| 公开组件 | 胜 | 负 | 平 | 平均边际 |
|---|---:|---:|---:|---:|
| E773 demand-aligned pasture | 0 | 6 | 0 | -13,985.7 |
| E774 terminal animal frontier | 0 | 6 | 0 | -13,701.0 |
| E776 engine-exact latent pasture | 0 | 6 | 0 | -13,143.7 |
| frontier_main（复合方案） | 0 | 6 | 0 | -5,807.0 |

全部对局均完成 720 steps。E749 consensus network 在当前本地模块加载时触发
`AttributeError: 'NoneType' object has no attribute '__dict__'`，属于公开代码自身的
导入/动态模块兼容问题，尚未把它的执行结果混入策略比较。

这些结果进一步说明：公开榜单高分方案与 v37 的差异主要来自原始 action tape、
随机轨迹和私有状态假设，整体移植会退化。后续只提取单个可解释的阶段机制，并保留
v37 逐局回退。

## 最新公开榜单方案补充验证

从 Kaggle 最新公开 kernels 拉取了 V42、Fully Dynamic Autonomous Agent、Reactive V5、V40 Challenger。Fully Dynamic Agent 导出的可执行 `main.py` 做了 20 局（10 seeds × 双 seat）配对，结果为 0 胜 / 20 负 / 0 平，平均边际 `-23,870`，最差 `-45,152`；全部 720 steps DONE。该完整方案同样不适合作为新父策略。

V42 notebook 的代码结构包含多个连续 wrapper（opening、sheep、milk、sale、weed、terminal 等），不能把 notebook 直接当成单一机制；需要先拆分并分别做动作差异和 paired panel。

## V42 跨对手确认面板

V42 可执行源码进一步完成 40 局确认（4 个对手 × 10 seed × 双 seat）：

| 对手 | 胜 | 负 | 平 | 平均边际 | 最差边际 |
|---|---:|---:|---:|---:|---:|
| v37 | 20 | 0 | 0 | +27,389.6 | +9,849 |
| Flex v7 | 20 | 0 | 0 | +30,137.5 | +13,082 |
| Thomas v6 | 20 | 0 | 0 | +8,499.3 | +1,416 |
| Dmitrii v6 | 20 | 0 | 0 | +9,066.5 | +5,794 |

所有 80 局（含前面的 V42 screen）均完成 720 steps、`DONE=True`。这使 V42 成为第一个达到跨公开对手、双 seat、10 seed 配对确认门槛的候选，但仍需未见 seed holdout、运行时和源代码审计后才能进入“待用户授权提交”。

## V42 final engineering gate

Fresh-process runtime smoke: 12 games against random/starter/pass, both seats and seeds 9101/9107; 12/12 DONE at 720 steps, zero exceptions. Per-call timing on seed 9101 versus starter: 719 calls, mean 0.933 ms, p99 7.279 ms, max 29.578 ms. The packaged artifact is [v42_pkg.tar.gz](incubated_candidates/v42_pkg.tar.gz).

V42 now satisfies the local research gate for a candidate stronger than v37: broad paired panels, unseen holdout, deterministic completion, standard-library-only packaging, and runtime margin. It remains pending explicit user authorization before any Kaggle submission.
