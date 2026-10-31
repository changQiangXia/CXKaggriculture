# 收据：candidate_or2sn4（OR2 对手预判窗口 120 → 4）——当前最强候选

## 配方

`panel_runs/f2b/arms/CH99.py` 仅两处常量：`_OR2_SN_H = 120` → `4`（第 4755、8046 行）。
OR2 的其他逻辑（槽位重排 `_OR2_SLOT_H=6`、10 门限）全部保留。

包：`candidate_or2sn4.tar.gz`
* tar sha256 `fb82e8fc92ab6f926b78ce546214f1abbbb92785f12e6145ac5998f9b7fd2e01`
* main.py sha256 `8c8158162dadb64c66933e605e8c1d5a3b213055be4548b4c9f81fbc7c560a6b`
* 与 CH99 差异：**2 行常量**（diff 已验证）

备份候选：`candidate_or2sn8.tar.gz` 同族（SN_H=8），门径略低（G2 +626、G3 +470）。

## 门表（全部实跑）

| 门/池 | n | ch99 | sn4 | 配对 Δ（sn4−ch99） | t | 判定 |
|---|---|---|---|---|---|---|
| **G2 2400+ 池** | 300 | +8,299（97.3%） | **+8,939（98.7%）** | **+640.2** | **+8.10** | ✅（门：≥+100 且 t≥2） |
| G2（扫描） | 150 | +7,810 | +8,503 | +693.4 | +8.42 | ✅ |
| **G3 低段 1400–1900** | 300 | +10,082（98.3%） | **+10,613（97.3%）** | **+530.4** | **+6.22** | ✅（门：≥−20） |
| 硬池（真实 2400–3000 败局） | 193 | +1,523 | +1,308 | −215.4 | −0.90（不显著） | ⚠️ 披露 |
| 镜像 H2H（seeds 257–316） | 60 | — | — | −254（6.7% 胜） | — | 已知符号相反，非门 |
| 官方引擎 seed1/2 | 2 | — | — | −732 / +46，**exact=True，DONE/DONE** | — | ✅ |

SN_H 扫描（G2, n=150）：120→0（ch99）… 16→+341，12→+484，**8→+660**，**4→+693**，0→+500，24→+235，48→+6
⇒ 甜点在 4–8；sn4 取门径最高点，硬池损失与 sn8/24 同量级且不显著。

## 机制（一句话）

OR2 用 `_OR2_SN_H` 步长程"对手卖出预判"来压制/延后我们自己的卖单；120 步的预判在真实池里频繁误判
（真实对手≠我们的镜像），把窗口缩到 4 步后，预判只在真正有把握的短窗口内生效，
两个真实池同时大幅转正，镜像代价也从 −836 收敛到 −254。

## 复跑

```bash
PY=/root/miniconda3/envs/kaggle-eval/bin/python
$PY pool_georgy_band.py --arms ch99=panel_runs/f2b/arms/CH99.py sn4=panel_arms/gate/or2_sn4.py --lo 2400 --hi 10000 --n 300
$PY pool_georgy_band.py --arms ch99=panel_runs/f2b/arms/CH99.py sn4=panel_arms/gate/or2_sn4.py --lo 1400 --hi 1900 --n 300
$PY pool_hard_losses.py --arms ch99=panel_runs/f2b/arms/CH99.py sn4=panel_arms/gate/or2_sn4.py
```

状态：**未提交**（零提交）。
