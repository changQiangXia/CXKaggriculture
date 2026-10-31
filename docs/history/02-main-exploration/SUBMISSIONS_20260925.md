# 提交收据 2026-09-25（用户批准的两次机会）

## 0. 追加提交（2026-09-25 15:46 UTC，用户单独批准）

| 顺序 | 时间 (UTC) | ref | 包 | tar sha256 | main.py sha256(前16) |
|---:|---|---|---|---|---|
| 3 | 2026-09-25 15:46:32 | **56554545** | `candidate_sloth80.tar.gz` | `9af1e32744ab4c19…` | `9299efa31f7133b5…` |

配方 = archplus + SN_H 48→120 + CXD 800→3200 + CH_SHED 97→99 + **`_OR2_SLOT_H` 8→80**。
门表见 `GOAL_RECEIPT_final_two.md`：镜像 +385.9（t=23.6）与第二独立块 +383.3（t=21.4）、
Top-20 真强队池 795 局合并 +89.4（t=5.41）、AM107 73/107、AM 胜局 150/153、强池 +45、新公开池 +77、异族池 +28。
官方引擎 smoke：seed1 +630、seed2 −14，均 DONE/DONE。

* **T0 = 2026-09-25 15:46:32 UTC**，最早干净 2h 均值读数 = **T0+6h = 21:46 UTC（北京 05:46）**
* 今日额度：5 → 用掉 3（56547262、56547267、56554545）→ **剩 2**
* ref 已写入 `/root/autodl-tmp/live_corpus/refs.txt`（增量监听）

## 1. 提交内容

| 顺序 | 时间 (UTC) | ref | 包 | tar sha256 | main.py sha256(前16) |
|---:|---|---|---|---|---|
| 1 | 2026-09-25 09:39:26 | **56547262** | `candidate_archplus.tar.gz` | `9d2b834b3c1dd6a7…` | `96ac067d5f6be0e5` |
| 2 | 2026-09-25 09:39:36 | **56547267** | `candidate_h120ch99.tar.gz` | `4abb7ba82bf01963…` | `8e7cbc4485314d65` |

两次都是 `Successfully submitted to Kaggriculture`；今日额度从 5 → **剩 3**。
提交前已按协议核对：tar 根目录含 `main.py`，解包哈希与本地文件一致；官方引擎 smoke 通过。

## 2. 读分口径（用户口径）

新提交 600 起爬 → 约 **4h** 稳定 → 稳定后取**当前时间往前 2h** 的均值。
⇒ **最早干净的读音时点 = T0 + 6h = 2026-09-25 15:39 UTC（北京时间 23:39）**。

```bash
/root/miniconda3/envs/kaggle-eval/bin/python score_history.py      --refs 56547262,56547267,56524401,56530265 --hours 2
/root/miniconda3/envs/kaggle-eval/bin/python watch_scores.py --report --hours 2
```

注意：`watch_scores.py` 只登记**已经有分数**的提交，所以两个新 ref 会在首批对局出分后才出现在
`/root/autodl-tmp/score_watch/scores.jsonl`（守护进程已重启，每 600 s 采样一次）。

## 3. 提交前完成的增量拉取（渐进式）

| ref | 包 | 本次新增 | 语料累计 | 其中败局 | 新拉回放 |
|---|---:|---:|---:|---:|---:|
| 56530265 | candidate_final | +19 局 | 126 局（W71/L55） | 55 | — |
| 56524401 | archplus | +12 局 | 137 局（W83/L54） | 54 | — |

合计新下载 **31** 个回放（即时 gzip；`live_corpus/replays/` 现 263 个 gz 文件），
败局农场已展开：`/root/autodl-tmp/live_56530265_losses`（+12）、`live_56524401_losses`（+8）。
两个新 ref（56547262 / 56547267）已写入 `/root/autodl-tmp/live_corpus/refs.txt`，
后续可直接 `live_pull.sh` 增量补充（游标机制保证不重下）。

## 4. A/B 读法

槽位 1 = AP 同窗口参照（56547262），槽位 2 = 新候选（56547267）。
两者同一分钟提交，因此爬坡曲线可直接对消；预期读出：

* 若 56547267 的 2h 均值比 56547262 高 **≥ +10 分**：与"镜像 +54.7 ⇒ 线上 +18 分"的预测方向一致；
* 若两者差在 ±10 分内：说明镜像→天梯的斜率（目前只有 n=1 锚点）被高估，需要重新标定；
* 若 56547267 更低：本轮的"镜像优先"结论需要推翻重来。
