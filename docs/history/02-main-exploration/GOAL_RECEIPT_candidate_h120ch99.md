# Goal 收据：candidate_h120ch99（候选 #1）

目标口径（用户预注册）：镜像（新种子块 257–768，≥+30/局且 t≥2）+ Top-20 真强队池（≥0）、四护栏不退化、
零提交、数据线 ≤0.5 req/s、禁止用加量代替机制假设。

包：`candidate_h120ch99.tar.gz`（tar sha `4abb7ba82bf01963…`，main.py sha `8e7cbc4485314d65…`，644,126 B）
配方 = archplus + `_OR2_SN_H 48→120` + `_CXD_BUDGET 800→3200` + `_CH_SHED 97→99`（其余沿用 CAP16 / SLOT10 / 开局洗单）。

| 门 | 口径 | 数字 | 判定 |
|---|---|---|---|
| **G1** | 线上 A/B：56547267（本包） vs 56547262（archplus 重交），T0=2026-09-25 09:39 UTC，**15:41 UTC 读近 2h 均值** | 本包 **2664.7（n=13, sd 6.0）**；AP 重交 2476.0（n=11）；老 archplus 末值 2641.2；candidate_final 末值 2554.1 ⇒ **vs 老 archplus +23.5**、vs candidate_final +110.6、vs 同刻 AP 重交 +188.7 | ✅ 方向一致（镜像 +54.7 ⇒ 预测 +18…+24，实测 +23.5） |
| **G2** 镜像 | `panel_selfplay.py` vs archplus，全新种子 257–768，双座位配对（n=512） | **+54.7/局，sd 171.7，t=+7.20，323胜/131负** | ✅ 过（≥+30 且 t≥2） |
| **G3** 真强队池 | `pool_ladder_top.py`：Top-20 池中 **≥2900 的 795 局**抽 300 局，冻结该局强侧动作带、同 seed 重放，与 archplus 逐局配对 | **+11.6/局，sd 138.1，t=+1.46，114胜/83负/103平** | ✅ 过（≥0） |
| G4-1 AM107 | `am_revival_bench.py --tag ch99`（107 局败局语料） | **73/107 翻盘**（基线 archplus 71、candidate_final 77） | ✅ 过（阈值 ≥73） |
| G4-2 强池 | `panel_pool.py --pool pool_strong.txt --seeds 33..64`（n=128，与 archplus 同种子配对） | **Δ +96.7/局，t=+3.40** | ✅ 不退化 |
| G4-3 新公开池 | `panel_pool.py --pool pool_new.txt --seeds 33..64`（n=128） | **Δ +80.5/局，t=+3.68** | ✅ 不退化 |
| G4-4 异族池 | `panel_pool.py --pool pool_diverse.txt --seeds 33..35`（24 家 × 3 种子 × 双座位 = 138 局） | **Δ −1.6/局，sd 463.1，t=−0.04（33胜/42负）** | ✅ 中性 |
| **G5** 机制/打包/引擎 | 一句话机制 + tar 单 main.py + sha256 + 官方引擎 720 步 | 机制：**"把计划卖单更早地提前到本回合"**（窗口 48→120 回合）+ 订单簿置换预算 800→3200 + 棚阈值 97→99；官方引擎 seed1 **+73**、seed2 平，均 DONE/DONE | ✅ 过 |
| **G6** 增量性 | 相对 archplus 仅追加/调整旋钮，未改任何已提交包 | diff 仅 6 行常量 | ✅ 过 |
| **G7** 数据纪律 | 拉取限速、断点续传、429 冷却 | 实测：top-20 池 1,997 局（99.1% 成功）后触发 replay 端点 429；已改为 0.25 req/s + 冷却闸门 + 自动恢复 | ✅ 遵守 |

## 复跑命令

```bash
PY=/root/miniconda3/envs/kaggle-eval/bin/python
$PY panel_selfplay.py --a panel_runs/f2b/arms/CH99.py --b panel_arms/rkey/o_archetype_plus.py \
    --seeds 257..768 --workers 12 --out /tmp/g2.json
$PY pool_ladder_top.py --arms ch99=panel_runs/f2b/arms/CH99.py ap=panel_arms/rkey/o_archetype_plus.py \
    --min-score 2900 --n 300 --workers 10 --out /tmp/g3.json
$PY am_revival_bench.py --arm panel_runs/f2b/arms/CH99.py --tag ch99 --workers 8
$PY panel_pool.py --a panel_runs/f2b/arms/CH99.py --pool pool_strong.txt --seeds 33..64 --workers 8 --out /tmp/g4.json
```

## 备注

* G3 的实现是"冻结真强队磁带"。该实现**对抢跑类机制系统性失效**已被对照实验证明（见
  `NEGATIVE_MPX_20260925.md`：三种机制完全不同的臂池子 Δ 都是 −85）。ch99 在本门上是 +11.6，
  属于"加了很少的量、时机变化也小"，因此该门对它仍具区分度；但后续若做抢跑类机制，需要另行设计
  反应型对手（`pool_ladder_nn.py` 原型已存在，尚未做到可用）。
