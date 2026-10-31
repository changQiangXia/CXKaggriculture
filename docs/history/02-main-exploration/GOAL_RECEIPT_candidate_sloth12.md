# Goal 收据：candidate_sloth12（候选 #2，双门通过，优于候选 #1）

配方 = **candidate_h120ch99 + `_OR2_SLOT_H` 8→12**（槽位保留地平线；其余完全不变，diff 仅 2 行常量）。
包：`candidate_sloth12.tar.gz`（tar sha256 `4ce4a046fe700bca5964b1edd402b8212ffa7235974fbc60d69804137024b365`，644,125 B），
`pkg_candidate_sloth12/main.py`
main.py sha256 = `fbd0fd9d0df37c9f8b69baaf3c2e8e5651e9f19b0ec1cfa9225760a2bab3724f`

| 门 | 口径 | 数字 | 判定 |
|---|---|---|---|
| **G2** 镜像 | `panel_selfplay.py` vs archplus，全新种子 **257–768**（n=512 配对） | **+84.7/局，sd 222.2，t=+8.63，350胜/117负** | ✅（≥+30 且 t≥2） |
| G2 增量 | 同一批种子 vs **候选 #1**（ch99）配对 | **+30.1/局，sd 184.3，t=+3.69，212胜/80负/220平** | ✅ 严格优于 #1 |
| **G3** 真强队池 | `pool_ladder_top.py`（Top-20 池中 ≥2900 的 795 局抽 300 局，冻结强侧磁带，同 seed 重放，与 archplus 配对） | **+22.5/局，sd 229.9，t=+1.70，120胜/135负** | ✅（≥0） |
| G3 增量 | 同 300 局 vs ch99 | +10.9/局（t=+1.03） | ✅ 不弱于 #1 |
| G4-1 AM107 | `am_revival_bench.py --tag sloth12` | **74/107 翻盘**（archplus 71、ch99 73） | ✅（≥73） |
| G4-2 强池 | seeds 33..64（n=256，与 archplus 同种子配对） | **Δ +85.5/局，t=+4.11** | ✅ |
| G4-3 新公开池 | seeds 33..64（n=256） | **Δ +78.9/局，t=+4.37** | ✅ |
| G4-4 异族池 | `pool_diverse.txt` 24 家 × 3 种子 × 双座位（n=138） | **Δ −14.8/局，t=−0.36**（36胜/62负） | ✅ 中性 |
| **G5** 打包/引擎 | tar 单 main.py + sha256 + 官方引擎 720 步 | 官方引擎 seed1 **+76**、seed2 平，均 DONE/DONE | ✅ |
| **G6** 增量性 | 相对 ch99 只改一个常量 | diff = 2 行 | ✅ |
| **G7** 数据纪律 | 拉取 ≤0.5 req/s、断点续传、429 冷却 | 见 `SUBMISSIONS_20260925.md` 与 `/tmp/resume_pulls.log` | ✅ |

机制一句话：**把"槽位保留"的决策地平线从 8 回合放宽到 12 回合**——在末期卖单密集时更早地为我们
还没上架的高价品预留卖单位置，减少"被自家其它卖单挤掉"的损失。该旋钮在 2700–2800 配对差分里对应的
正是"赢家末期卖单槽更多（1.04 vs 0.91）"这一现象。

## 复跑

```bash
PY=/root/miniconda3/envs/kaggle-eval/bin/python
$PY knob_patch.py panel_runs/f2b/arms/CH99.py /tmp/sloth12.py _OR2_SLOT_H 12
$PY panel_selfplay.py --a /tmp/sloth12.py --b panel_arms/rkey/o_archetype_plus.py --seeds 257..768 --workers 12
$PY pool_ladder_top.py --arms s=/tmp/sloth12.py ap=panel_arms/rkey/o_archetype_plus.py --min-score 2900 --n 300
$PY am_revival_bench.py --arm /tmp/sloth12.py --tag sloth12 --workers 8
```
