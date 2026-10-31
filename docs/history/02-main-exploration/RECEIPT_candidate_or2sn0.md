# 收据：candidate_or2sn0（OR2 对手预判窗口 120 → 0）

## 配方

`panel_runs/f2b/arms/CH99.py`，**仅两处常量**：`_OR2_SN_H = 120` → `0`（第 4755、8046 行）。
其余全部层原样保留（含 OR2 的槽位重排逻辑 `_OR2_SLOT_H=6` 与 10 门限）。

包：`candidate_or2sn0.tar.gz`
* tar sha256 `ab78b203177ad9850bf1df8ccf67888ca2fa2d164276b470209ebd76457a5906`
* main.py sha256 `0561c121facb69ed660b98ece3a0e772737495ecb5b99dadce1b958e014f7ea2`
* 与 CH99 差异：**2 行常量**（diff 已验证）

备选保守版：`candidate_or2sn24.tar.gz`（`_OR2_SN_H=24`）
tar `c6cf18378d7b8ea9ab8dbebddb72bba1b27f5b9cdbf3bccc976b99fe3085273d`，
main.py `3a99275058ce0ab542de2d55c9a4da5a5b2ba1dce2063c0f9ed3548b17fdfecf`。

## 门表（n=300 双确认）

| 门/池 | ch99 | sn0 | sn24 | 配对 Δ（变体−ch99） | t | 判定 |
|---|---|---|---|---|---|---|
| **G2 2400+ 池** | +8,299（97.3%） | **+8,728（98.3%）** | +8,547（98.0%） | **+429.7 / +248.0** | **5.32 / 9.33** | ✅ 两者均过 |
| G2（n=150） | +7,810 | +8,309 | +8,044 | +499.7 / +234.5 | 6.07 / 6.50 | ✅ |
| **G3 低段 1400–1900** | +10,082（98.3%） | **+10,522（97.3%）** | +10,300（98.7%） | **+439.5 / +217.5** | **5.13 / 10.09** | ✅ 两者均过 |
| 硬池（193 局真实 2400–3000 败局） | +1,523 | +1,173 | +1,463 | −350（t=1.48，**不显著**） / −60（t=1.54，不显著） | | ⚠️ 披露 |
| 官方引擎 seed1/2（vs ch99） | — | −802 / +46，**exact=True，DONE/DONE** | — | | | |

参考：完全绕过 OR2 的版本（`candidate_or2off`）G2/G3 为 +276/+287，但硬池 **−718（t=3.03，显著变差）**，
因此 **sn0 / sn24 取代 or2off 作为主候选**。

## 机制（一句话）

OR2 用 120 步长程"对手卖出预判"压制我们自己的卖单（`_OR2_SN_H` 用在计划卖单的债务回落循环里）；
在真实池里这个对手模型频繁误判（对手是真人/冻结磁带，不是我们的镜像），把该窗口归零即可
——保留 OR2 的槽位重排，去掉错误压制。窗口 24 步是保守中间档。

## 复跑

```bash
PY=/root/miniconda3/envs/kaggle-eval/bin/python
$PY pool_georgy_band.py --arms ch99=panel_runs/f2b/arms/CH99.py sn0=panel_arms/gate/or2_sn0.py --lo 2400 --hi 10000 --n 300
$PY pool_georgy_band.py --arms ch99=panel_runs/f2b/arms/CH99.py sn0=panel_arms/gate/or2_sn0.py --lo 1400 --hi 1900 --n 300
$PY pool_hard_losses.py --arms ch99=panel_runs/f2b/arms/CH99.py sn0=panel_arms/gate/or2_sn0.py --band-lo 2400 --band-hi 3000
```

状态：**未提交**（零提交）。
