# 收据：candidate_pge（低段零闪失版）

配方 = candidate_h120ch99 + **分期门控 `_OR2_SLOT_H`：step<480 用 80，step≥480 用 8**
（实现：`make_phase_gate_arm.py` 直接补丁槽位逻辑的两处读取点，避免 wrapper 递归）。

包：`candidate_pge.tar.gz`（tar sha `4f8f34fa26ef21ec…`，main.py sha `90304163cd2e1036…`）
官方引擎：seed1 **+73**、seed2 **+10**，均 DONE/DONE。

## 门表（全部通过）

| 门 | 数字 | 对照 |
|---|---|---|
| 镜像（新种子 257–768, n=512） | **+106.9（t=+12.4，392胜/93负）** | ch99 +54.7、sloth20 +203.5、sloth80 +385.9 |
| **低段池（300 局 1400–1900，真实天梯）** | **−9.0 vs ch99（t=1.72，不显著）** | sloth20 −56、sloth80 −102 |
| 硬池（110 局真实败局） | +9.6 vs ch99（t=0.88） | sloth80 +44 |
| 真强队池（300 局 ≥2900） | **+35.2（t=+2.69，150胜/114负）** | sloth80 +31.7 |
| AM107 | **74/107**（全家族最高） | ch99/s20/s80 都是 73 |
| AM 胜局（153 局） | **153/153（100%）** | sloth80 150/153 |
| 强池（n=256） | +65.6（t=3.27） | sloth20 +89、sloth80 +45 |
| 新公开池（n=256） | +105.5（t=4.13） | sloth20 +73、sloth80 +77 |
| 异族池（24 家 × 3 种子） | 边际 −787（t=−1.56，**138胜/0负**） | 差额来自 2 个家族的边际，非闪失 |

## 机制（一句话）

高 `_OR2_SLOT_H`（槽位保留地平线）的收益与代价**都只发生在末期（day≥20）**；把它限制在
**前期**（step<480）即可拿到 +52 镜像而几乎不付低段代价（day 0–16 逐位相同）。

## 复跑

```bash
PY=/root/miniconda3/envs/kaggle-eval/bin/python
$PY make_phase_gate_arm.py panel_arms/gate/sloth80.py /tmp/pge.py --early 80 --late 8 --step 480
$PY panel_selfplay.py --a /tmp/pge.py --b panel_arms/rkey/o_archetype_plus.py --seeds 257..768 --workers 12
$PY pool_georgy_band.py --arms pge=/tmp/pge.py ch99=panel_runs/f2b/arms/CH99.py --lo 1400 --hi 1900 --n 300
```
