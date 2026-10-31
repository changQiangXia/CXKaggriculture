# 负结论：MPX（跌价前抢跑层）——预测惰性，效应是"多卖"本身

来源：公开 notebook `haideptry/the-2965-master-hybrid-engine`（V59.v7）里的 `_V7_MPX`
"Microstructure Price Defense"。移植实现见 `make_port_arm.py --layer mpx`。

## 1. 三个变体 + 一个对照，四组数字

| 臂 | 机制 | 镜像 Δ（新种子 257–768，n=512） | 池子 Δ（300 局真强队磁带，配对 vs archplus） | AM107 |
|---|---|---:|---:|---:|
| `mpx_t6` | 有价格预测，多卖（take=6） | **+258.9（t=18.33）** | **−85.5（t=−6.42）** | 74/107 |
| `mpx_t3` | 剂量 3 | +267.7（t=18.04） | −69.3（t=−5.89） | — |
| `mpx_t2` | 剂量 2 | **+270.6（t=18.31）** | −59.7（t=−5.54） | — |
| `mpxcred` | **同量早卖**（信用账本：早卖多少就从后续计划卖单扣多少） | **+257.6（t=18.22）** | **−84.6（t=−6.39）** | — |
| `mpxctrl` | **去掉价格预测**（无条件多卖，量同 t6） | **+258.9（t=18.33）** | **−85.6（t=−6.43）** | **75/107** |

独立种子块复核（1000–1500，n=501）：mpx_t6 = **+247.8（t=17.43）** ✓ 两段一致。

## 2. 结论

1. **价格预测是惰性的**：把预测条件删掉（`mpxctrl`）后，镜像、池子、AM107 三项与 MPX 逐项相同
   （+258.9 / −85.6 / 75 vs 74）⇒ MPX 的全部效应来自**"在 12–23 时多卖"**这一 generic 攻击性，
   与"预测跌价"无关。
2. **池子惩罚与体积无关**：同量早卖（`mpxcred`）仍是 −84.6，与体积版 −85.5、对照 −85.6 无异
   ⇒ 冻结磁带池惩罚的是**"比录制方更早卖"**这件事本身（对手不反击时，早卖只是把价格砸在自己脚上）。
3. **剂量不改变方向**：镜像收益在 take=2 就饱和（+270.6），池子代价随剂量略降（−59.7）但不转正。

## 3. 判定（按 goal 纪律）

* goal 明文："禁止用加量代替机制假设"。MPX 的机制假设（跌价前抢跑）**已被对照实验否证**；
  剩下的只是"多卖/早卖"这一加量效应 ⇒ **不作为候选**，记负结论。
* 该实验同时**证伪了 G3 门在抢跑类机制上的有效性**：三种机制完全不同的臂拿到几乎相同的池子 Δ
  （−85.5 / −84.6 / −85.6），说明该门无法区分机制，只能检测"是否比录制方更早卖"。
  后续若要做抢跑类机制，必须先把 G3 的对手换成**反应型**（`pool_ladder_nn.py` 原型：状态最近邻策略，
  目前因对手农场状态依赖过强而不可用，需要重做特征/动作合法性过滤）。

## 4. 复跑

```bash
PY=/root/miniconda3/envs/kaggle-eval/bin/python
$PY make_port_arm.py panel_runs/f2b/arms/CH99.py /tmp/mpx.py --layer mpx --take 6
$PY make_port_arm.py panel_runs/f2b/arms/CH99.py /tmp/ctrl.py --layer mpxctrl --take 6
$PY panel_selfplay.py --a /tmp/mpx.py --b panel_arms/rkey/o_archetype_plus.py --seeds 257..768 --workers 12
$PY pool_ladder_top.py --arms mpx=/tmp/mpx.py ap=panel_arms/rkey/o_archetype_plus.py --min-score 2900 --n 300
```
