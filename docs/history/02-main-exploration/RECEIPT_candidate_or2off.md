# 收据：candidate_or2off（绕过 _OR2 对手预判/市场抽取层）

配方：`panel_runs/f2b/arms/CH99.py` + **一行** `agent = _OR2_PARENT`
（插在 `_CH_PARENT = agent` 之前），即**跳过 _OR2 层的 wrapper**，其余层原样保留。

包：`candidate_or2off.tar.gz`
* tar sha256 `4baadcd88fbcff0b49915d0b0c57923cfe51d5c9da3185851e5a33558938d104`
* main.py sha256 `49183f17d27166d473d99002a2c14124c164d7c1b98cc5f7bfde31c6fe510dfa`
* 与 CH99 的差异：**仅 1 行插入**（`diff` 已验证）

## 门表

| 门 | 口径 | ch99 | or2off | 配对 Δ（or2off−ch99） | t | 判定 |
|---|---|---|---|---|---|---|
| **G2** | 2400+ 池 n=300（真实天梯冻结磁带） | +8,299（97.3%） | **+8,575（98.3%）** | **+276.2** | **+3.40** | ✅ 过（≥+100 且 t≥2） |
| G2（复现） | 2400+ 池 n=150 | +7,810 | +8,142 | +332.3 | +3.82 | ✅ |
| **G3** | 低段池 1400–1900 n=300 | +10,082（98.3%） | **+10,370（96.7%）** | **+287.2** | **+3.22** | ✅ 过（≥−20） |
| G3（复现） | 低段池 n=150 | +10,693 | +11,050 | +356.5 | +3.14 | ✅ |
| 镜像 H2H（诚实披露，非门） | 60 局 seeds 257–316 vs ch99 | — | — | **−836**（0/60 胜） | — | 已知"镜像与真实池符号相反"现象 |

官方引擎校验（`kaggsim.gauntlet.verify_official`，KAGG_BIN=/root/autodl-tmp/rust_sim/kagg）：
seed1 银行 [149,097 / 150,252]、seed2 [77,749 / 78,728]，**官方引擎与 Rust 引擎逐分相同（exact=True）**，
两局均 DONE/DONE。对 ch99 直连：−1,155 / −979（与镜像 H2H 同号）。

## 机制（一句话）

_OR2 是"城市抽取预测 + 对手产出预判 → 重排市场单"的层（`_or2_draw` / `_or2_tiles` / `_or2_exposure`）；
真实池里它的对手模型（我们的镜像打法）与真实对手（冻结磁带/真人）经常错配，反而压低我们的卖出时序；
绕过它后**两个真实池同时正收益**（+276/+287）。它在镜像里确实有效（H2H 会输），因此这是一个
"真实池 +、镜像 −"的候选，符合 goal 用真实池定门的口径。

## 同批消融证据（都在 2400+ 池 n=150）

* `_CA` 层：绕过 −547（t=4.36）⇒ 保留
* `_CH` 层：绕过 −240（t=8.88）⇒ 保留
* `_CS` 层：绕过 −102（t=1.92）⇒ 保留
* `_R37` / `_RACE`：绕过 Δ=0（惰性）
* `_SR` / `_HD2`：绕过 −20 / +31（噪声级）

## 复跑

```bash
PY=/root/miniconda3/envs/kaggle-eval/bin/python
$PY make_layer_off_arm.py panel_runs/f2b/arms/CH99.py /tmp/or2off.py --restore _OR2_PARENT --before _CH_PARENT
$PY pool_georgy_band.py --arms ch99=panel_runs/f2b/arms/CH99.py or2off=/tmp/or2off.py --lo 2400 --hi 10000 --n 300
$PY pool_georgy_band.py --arms ch99=panel_runs/f2b/arms/CH99.py or2off=/tmp/or2off.py --lo 1400 --hi 1900 --n 300
```

状态：**未提交**（零提交）。产物：`panel_runs/g2_or2off_300.json`、`panel_runs/g3_or2off_300.json`、
`panel_runs/g2_layer_batch2.json`、`panel_runs/g3_or2off_low.json`。
