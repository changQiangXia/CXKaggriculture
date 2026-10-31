# 提交收据：candidate_pg576mir2（2026-09-26，用户单独批准）

| 项 | 值 |
|---|---|
| ref | **56573362** |
| 时间 | 2026-09-26 07:44:44 UTC（北京 15:44） |
| 包 | `candidate_pg576mir2.tar.gz`（644,347 B） |
| tar sha256 | `c3aa5238708d91b63afdee93477ff00adb9c5dab7149158530039129b229fa50` |
| main.py sha256 | `35526d5cf6f457857e48e8f88a1191d28c7dea39aa66d103e5e605d742de408e` |
| CLI 回执 | `Successfully submitted to Kaggriculture`，今日剩 4 次 |

校验：tar 根目录仅 `main.py`；解包哈希与本地/收据一致；官方引擎 smoke 早前已过（seed1/2 exact=True）。

## 读分口径（用户口径）

600 起爬 → 约 4h 稳定 → 稳定后取**当前时间往前 2h** 的均值。
⇒ **T0 = 07:44:44 UTC，最早干净读数 = T0+6h = 13:44:44 UTC（北京 21:44）**。

读取命令：

```bash
/root/miniconda3/envs/kaggle-eval/bin/python score_history.py \
    --refs 56573362,56554545,56547262,56547267 --hours 2
/root/miniconda3/envs/kaggle-eval/bin/python watch_scores.py --report --hours 2
```

对照基准：`56524401`(archplus) 最近读数、`56554545`(sloth80) 上线后走势。

## 候选自证（提交前已验）

* P0 九项零劣化全绿（镜像 +22.8 且 56/60 平局、AM 胜局 153/153、AM107 75/107、
  硬池 193 +54.4、异族硬池 372 +30.6、Top≥2900 +300.3、新公开 48 +156.0、日包池 ≥ m2）。
* P1：G2 2400+ n=300 Δ+451.4（t=13.26）；G3 低段 n=300 Δ+409.8（t=12.81）。
* 机制归因：OR2 预约窗口 SN_H 120→late-8 + 近镜像护甲（收据 `RECEIPT_candidate_pg576mir2.md`）。
