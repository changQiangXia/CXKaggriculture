# 删除记录 2026-09-26

按 goal P4（"日包一次最多囤 1–2 包且析出轻量 action 流后删 zip（可重下并记录）"）执行。

| 目标 | 大小 | 理由 | 恢复方式 |
|---|---:|---|---|
| `/root/autodl-tmp/public_intel/ep0925/kaggriculture-episodes-2026-09-25.zip` | 805 MB | 已完成析出：`panel_runs/ledger_ep0925.jsonl`(16.7MB)、`panel_runs/tapes_ep0925.jsonl.gz`(16.8MB)，并做过 6 步×2 座位逐字节比对（0 处不一致） | `kaggle datasets download kaggle/kaggriculture-episodes-2026-09-25`（dataset API 不限流）；本地仍留 `dl.log` |
| `/root/autodl-tmp/farm2945_dev/__pycache__` | 467 MB | Python 字节码缓存，自动重建 | 自动 |

释放合计 1.27 GB；`/root/autodl-tmp` 剩余空间 19.0GB → **21.2GB**（满足 ≥21GB 底线）。

未动：`candidate_*`（只读）、`agent_monitor/replays`（35GB，Sep 12–17 旧回放，守护进程已死，
未被现行工具引用——**待用户决定**是否清理）、其余语料与 parquet。

## 追加（L3 复现用第二份日包）

| 目标 | 大小 | 理由 | 恢复方式 |
|---|---:|---|---|
| `/root/autodl-tmp/public_intel/ep0924/kaggriculture-episodes-2026-09-24.zip` | 772 MB | 已析出 `panel_runs/ledger_ep0924.jsonl` + `panel_runs/tapes_ep0924.jsonl.gz`（590 局，4 步×2 座逐字节比对 0 不一致） | `kaggle datasets download -d kaggle/kaggriculture-episodes-2026-09-24` |

## 追加（2026-09-27）：磁盘无损压缩，恢复 21GB 底线
* 未删除任何数据：把 91 个历史大文件 gzip 化（`.json.gz` / `.jsonl.gz` / `.py.gz`），
  共释放 **665 MB**，`/root/autodl-tmp` 从 20.83 GB → **21.49 GB**。
* 涉及：`panel_runs/quad4_routes.json`(27.5→2.06MB) 等 46 个结果 JSON、
  `loss_analysis.json`/`gate_m100u_pool.json`/`flood50_pool.json`(各 61→3.1MB)、
  `ledger_ep0925/0924.jsonl`(16.7→2.3MB)、层扫描臂 `panel_arms/gate/l2/l2*.py`、
  `panel_arms/tourney/*.py` 等。
* 还原：`gunzip -k <file>.gz`。
* 未动：`candidate_*`（只读）、语料 parquet、`agent_monitor`（等用户决定）。
