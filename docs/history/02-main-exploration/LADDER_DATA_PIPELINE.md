# 天梯数据自产通道（记录，2026-09-25）

> 用途：georgy 的"每日 replay 数据集"（d/e/f/g 波次）停更时，我们**自己**从天梯按
> episode id 采样拉取，得到同一类材料（含非我方对局），只读、可控、可复现。
> **本文件只记录这条数据线；优化线的结论见 `GATE_DECISION_PACKET_20260925.md` 与 HANDOFF。**

## 1. 已验证的事实（实测）

| 项 | 实测值 |
|---|---|
| 任意 id 抓取 | ✅ `kaggle competitions replay <id>` 能拉**非我方**对局（试点：Sai Reddy Pothireddy vs vinceybb 等） |
| 吞吐 | 60 局 / **73 秒**（8 并发 ≈ **1.2 s/局**） |
| 体积 | 原始 33–35 MB/局 → **gz 0.35 MB/局**（1MB 分块流式，内存峰值 ~1MB） |
| 头部 id 标定 | **head ≈ 113,187,500**（2026-09-25 ~07:05 UTC）；id 增速 ≈ **17k/小时** |
| 榜单 join | `/api/v1/datasets/list` 与 `kaggle competitions leaderboard --download` 均可；名字→分数 join 成功 |
| 失败率 | 2/60（未发布/未完成 id，自动跳过，不重试风暴） |

## 2. 榜单快照（2026-09-25 07:02 UTC，**已存**）

`public_intel/leaderboard/kaggriculture-publicleaderboard-2026-09-25T07:02:13.csv`

```
9,995 队；我们 CHEN Xiang = 2662.6 → #118
#1 3028.7 | #10 2926.6 | #50 2757.3 | #100 2684.8 | #250 2579.1 | #500 2468.1
距 #100 +22 / 距 #50 +95 / 距 #1 +366
最近 24h 提交过 2132 队（≥2700 的 74 队）
```

## 3. 脚本（可复现）

```bash
# 随机采样头部窗口（代表性快照；1,000 局 ≈ 20 分钟、~350 MB）
python farm2945_dev/pull_ladder_wave.py --n 1000 --head <最新id> --span 7500 \
       --leaderboard /root/autodl-tmp/public_intel/leaderboard --tag wave1

# 指定 id 列表（顶队专供；见 §4）
python farm2945_dev/pull_ladder_wave.py --ids-file <ids.txt> --leaderboard ... --tag top20
```

产物：`/root/autodl-tmp/ladder_waves/{replays/*.json.gz, index.jsonl, tops/<tag>_geNNNN.json}`
（index.jsonl 每行：episode / names / rewards / seed / team_scores / best_score）

## 4. 顶队专供（已定位，随时可抓）

用 georgy `episodes.csv`（截至 09-23 的 226,594 局元数据，字段含 `team_0/team_1`、`rating_*`）
与**新榜单 TeamId** join，得到前 20 队的对局 id 清单 → `farm2945_dev/ladder_top20_episodes.json`

| 队 | 分 | 可抓局数 |
|---|---:|---:|
| Boey | 3028.7 | 3 |
| DECEM | 3019.3 | 193 |
| Unknown Mother-Goose | 3011.2 | 123 |
| M & M & P & Q | 2998.3 | 155 |
| **Fourth Quadrant**（88 株大作物型） | 2970.6 | **8** |
| Vadim Vasilenko | 2959.9 | 2 |
| Kaggledew Valley 🏆 | 2918.7 | 629 |
| Densike | 2926.6 | 202 |
| Arda Ceylan / tetsuya&yuanzhe&guoqin / THIRD FARM CLUB / mtmr_s1 / Smackaveli … | 2870–2930 | 62–135 各 |
| **合计（前 20 队）** | — | **2,020 局** |

⚠️ 榜首几人（Boey/Vadim/IsaiahP）公开对局极少（0–3 局）；顶队 tape 只能按"可得的来"。

## 5. georgy 波次监控（仍在跑）

* 数据集 `georgymamarin/kaggriculture-episodes`：**lastUpdated = 2026-09-23 23:22 UTC**（≈32 h 未更新）；
  最新文件仍是 `replays_2026-09f.parquet`（1.26 GB，09e 是 2.54 GB ⇒ 流量在腰斩）。
* 监控进程：`georgy_watch_download.py` **PID 3071**，每 15 分钟轮询，日志 `/tmp/georgy_watch.log`；
  到货即自动流式下载 + 刷新 CSV + 写 `NEW FILES/READY`。
* 若进程死亡：`cd /root/autodl-tmp/meta_pipeline && nohup /root/miniconda3/bin/python georgy_watch_download.py >> /tmp/georgy_watch_daemon.log 2>&1 &`

## 6. 计划（P0/P1/P2；**尚未执行，等指示**）

* **P0（零下载，30–60 分钟）**：用已有 georgy 语料做"**2900+ 队 vs 我们 2600–2700 带**"的分层对比
  （开局首 3 单 / d6-12-18-24 结构 / 逐日×逐品卖出流与均价 / 现金轨迹）→ 产出"顶队多赚的 300+ 分落在哪"。
* **P1（~40 分钟，700 MB，只读）**：抓前 20 队 2,020 局 → `pool_ladder_top.txt`（**第一个公平外部对手池**）
  → base vs `stack5`/`e2d_i`/`e2d_t_v224off` 的第一张"对真强队"表。
* **P2（按 P0/P1 分叉）**：差距在结构→最小生产改动；差距在执行→按顶队行为校准 e2d/OR2；
  最后留 1 次提交做"候选 vs 2662.6 包"的对照。

## 7. 纪律

只读抓取 + 429 退避；原始 replay 即时 gz 删；parquet 一律 `iter_batches`；磁盘红线 20 G；
**未经批准零提交**；`candidate_final` 与已提交产物只读。

---

## 8. 分数口径（2026-09-25 追加，用户定标准）

**口径 = 近 4 小时均值（回填重建，不是从now攒）**。工具：`farm2945_dev/score_history.py`
（默认 `--hours 4`，自动剔除提交后评分爬坡 `--min-rating 2000`）。

原理：`live_corpus/index.json` 的每条 episode 元数据都带**该局前后我们的评分**
（`our_initial → our_updated`）+ 时间戳 ⇒ 任意历史窗口都能精确重建。
校验：最后一局的 `our_updated` 与官网显示分**逐位一致**（archplus 2665.7 / candidate_final 2556.6）。

实测窗口稳定性（2026-09-25 08:10Z）：

| 窗口 | archplus | candidate_final |
|---|---:|---:|
| 0.5h | 2665.7 | 2554.4 |
| 1h | 2668.0 (n=2) | 2555.1 (n=3) |
| 2h | 2665.1 (n=5) | 2566.6 (n=11) |
| **4h（标准）** | **2662.6 (n=11, sd=4.1)** | **2574.2 (n=19, sd=11.8)** |
| 6h | 2664.5 (n=18) | 2576.8 (n=31) |
| 12h | 2670.4 (n=49, sd=6.6) | 2529.6（**被爬坡污染**） |
| 24h | **2484.0（爬坡污染）** | 2417.6（污染） |

⇒ 4h 是稳态窗口（窗口内 sd 4.1/11.8，均值稳定）；>6h 起出现小漂移，>12h 必须先过滤爬坡。

**同窗口判决**：archplus **2662.6** vs candidate_final **2574.2** ⇒ **candidate_final 真退步 ≈ −88 分**
（2h 口径 −98.5，单点 −109；三个口径同向）。

**A/B 协议（用于下一次提交）**：保持 `archplus` 在活跃槽作参考，把待测包放另一槽；
提交后 **≥4 小时**用 `score_history.py --refs <新ref>,56524401` 比 4h 均值（活跃包约 2.5–5.5 局/小时 ⇒ 4h 有 10–22 个样本）。
另：`watch_scores.py --daemon --interval 600` 正在后台做正向采样交叉验证。
