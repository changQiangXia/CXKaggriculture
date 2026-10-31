# georgy-09h 同池竞技场（5 臂对抗用）

**冻结时间**：2026-09-30（UTC）；抽样种子 `20260930`，清单见 `arena_episodes.json`（400 局）。

## 组成

| 波段（按双方较高分） | 局数 | 队伍上限 | 同对局上限 |
|---|---|---|---|
| 2400-2600 | 180 | 12 | 3 |
| 2000-2400 | 120 | 6 | 2 |
| 2600+ | 40 | 24 | 6 |
| 1600-2000 | 60 | 6 | 2 |

* 来源：`public_intel/georgy_dataset/replays_2026-09h.parquet`（8,198 局，Sep 28）;
* 过滤：COMPLETED、双方评分齐全、分差 ≤400、排除 live_corpus 与历史面板已用过的 id（仅 3 局重叠）；
* 座向：按 episode 排序后奇偶交替 → 我方座 0 / 座 1 各 200 局；5 个臂共享完全相同的对手、种子与座向；
* 规模：400 条磁带共 202.8 MB；397 支不同队伍，最大单队出现 47 局（跨波段累计），最大重复对局 2 次。

## 文件

```
index.json            panel_fid 用的 mini index（含 our_seat / our_reward / opp_initial / band）
arena_episodes.json   400 局 id 清单（冻结）
replays/              episode-<id>-replay.json.gz 磁带
guards/fresh62.json   两个活跃槽最新 62 局（走 live_corpus 默认 index/replays）
guards/cur163.json    当前档 163 局
guards/nem14.json     克星 14 局
```

## 跑法

```bash
# 主竞技场（400 局，georgy 包）
panel_fid.py --arm <ARM>/main.py \
  --episodes georgy_arena/arena_episodes.json \
  --index georgy_arena/index.json \
  --replays georgy_arena/replays \
  --workers 12 --out <OUT>.json

# 守门员（走 live_corpus 默认路径）
panel_fid.py --arm <ARM>/main.py --episodes georgy_arena/guards/fresh62.json ...
panel_fid.py --arm <ARM>/main.py --episodes georgy_arena/guards/cur163.json ...
panel_fid.py --arm <ARM>/main.py --episodes georgy_arena/guards/nem14.json ...
```

## 判据（赛前约定）

* 主排名：raw 胜率；副口径：clean（双方 fid≥0.95）胜率与平均 margin；
* clean 为主判据——nemesis 的 +8 有 5 个 flip 是磁带压制虚胜，不能再被骗；
* 两两配对（同局换臂）做 McNemar；若前两名差距 <1.5pp，再对它们做双座复赛。
