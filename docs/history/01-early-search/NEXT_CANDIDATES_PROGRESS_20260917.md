# V45 后续候选构造与线上 replay 证据（2026-09-17）

## 当前线上行为

从 submission `56278920` 新收集的 28 个 replay（14 tie、14 loss）中：

- 14/14 个 tie 的 market action 序列完全相同，首个 opening 都是 `BUY WHEAT 70; SELL WHEAT 70`。
- tie 的逐步完整 action 相等率均值约 `0.9999`，market 相等率为 `1.0`。
- loss 的完整 action 相等率均值约 `0.9176`，market 相等率约 `0.9311`，明显低于 tie。
- 14 个 loss 对手 opening 分布：Q5 round-trip 5 局、Q70 4 局、Q50 2 局、单 BUY 5 2 局、4/8/12 变体 1 局。
- 当前 replay 的 tie 因此高度支持“V45 在公开同质策略池中形成镜像平局”，而不是 reward 偶然相等。

继续收集后，样本扩大到 36 局：17 tie、19 loss。17/17 tie 仍然是 Q70 exact mirror；19 局 loss 中 Q5 占 7、Q70 占 5、Q50 占 2，其余为单 BUY、split 和 Q85/非标准变体。当前线上 opening 结构已经足够支持把 Q5 作为主要研究方向，但仍不能把 replay 样本当作无偏总体频率。

这批 replay 也显示当前 V45 的实际损失并不全来自单一机制：Q5/Q50/单 BUY 对手占多数，另有少数 Q70 对手在后期 step 34、360、664 等位置发生分歧并造成大 margin。候选必须同时处理 opening 同质化和后期路线差异。

## 已构造候选

所有候选都从已核对的 V45 单文件源码生成，只改 opening wrapper：

| 文件 | 改动 | SHA-256 |
|---|---|---|
| `candidate_v45_q5.py` | `_OPEN_UNITS=5` | `f9a863799113c2cbcadea8e8afcfe5c05c6d36df8a448120c13917e116a2c8b8` |
| `candidate_v45_seatmix.py` | seat 0 使用 Q5，seat 1 保留 Q70 | `31f4f5a7af9dd41d3dc89fddcaf723f5c46fc85ad778f0bad64eaeff8e926363` |

对应本地测试 archive：

- `candidate_v45_q5.tar.gz`：`658a9b5959ee2338f114a8c5fe006272cfb6a12458cb573b64b5e3b722f41a58`
- `candidate_v45_seatmix.tar.gz`：`49a43af2f40f888dc12ad5ea4f885d4724e91b16c1660e5102e8f28e27f76452`

另有 Q10/Q40/Q50/Q65、Q5+race24 和 split-Q70 诊断版本，但它们不是当前优先候选：

- Q40/Q50 相对 V45 在 V43、V37、flex 面板上显著为负；Q40 与 Q50 在当前 engine 上行为相同。
- Q65 不能稳定击败 Q70 clone。
- Q5+race24 在 clone 层略强，但在 V43 层仍出现负 margin。
- 把 Q70 拆成两个 BUY 的 split-Q70 在 clone 上直接损失约 2,077，放弃。

## 关键本地结果

### Q5 对 V45 clone

4 seeds × 2 seats、common seed、严格 720-step runner：

- `8/8` 正 margin；
- 平均 `+544.5`；
- 最差 `+225`；
- seed-cluster bootstrap 区间约 `[+227.75, +1171.75]`。

这说明 Q5 确实能稳定打破 Q70 镜像平局。

### Q5/Q50/Q70/Q85 opening 小型博弈矩阵

在相同 engine、相同 seed、交换 seat 的小面板中，Q5 候选相对 Q70 parent 的 opening 差值如下：

| 对手 opening | Q5 相对 Q70 的平均 paired delta | 解释 |
|---|---:|---|
| Q70 | 约 `+860`（2 seeds、4 seat rows） | 能打破 Q70 镜像 |
| Q50 | 约 `+860` | Q5 对平台中部没有明显 opening 代价 |
| Q85 | 约 `+1349` | 对高数量 round-trip 有优势 |
| Q5 | 约 `+860` 相对 Q70 parent；Q5 对 Q5 自身为平局 | 不再被 Q70 的 opening 反向攻击 |

该矩阵规模很小，不能作为最终置信区间，但它比只做 Q70 self-play 更接近当前线上 opening 分布。它说明 Q5 是“opening 层面的支配性修补”，而不是只对一个特定数字有效。

### Q5 对 V43 / 非同质策略

当前仅有小样本，方向不够稳定：对 V43 4 局平均 `+985.75`，但范围 `-1346` 到 `+5888`；对 Nathan 4 局为 0（opening 不触发）。更多非 clone 试验中，Q5 对 V37 平均约 `-6775`、对 flex 平均约 `-5818`。这意味着 Q5 是强 anti-Q70 exploit，不应未经分层确认就称为通用升级。

### seatmix

seat 0 用 Q5、seat 1 用 Q70。在两个 seed 的 clone/V43 小面板中，clone 平均约 `+115.5`，V43 平均约 `-149.75`，比 Q5 全量更保守，但收益也被减半；样本仍不足以通过确认门槛。

## 当前判断

线上 14 个 tie 全为 Q70 exact mirror，而 14 个 loss 中有 5 个 Q5、2 个 Q50、若干其它 opening。Q5 候选有明确的机会：它能打破 Q70 镜像，并对 Q5 对手至少不会因为 opening 直接处于劣势。但本地非 clone 面板暴露出高方差和严重尾部风险，尚不能证明 Q5 的总体期望 margin 超过当前 V45。

按当前扩大到 36 局的 replay 做一个保守的 opening-only 粗估：Q70 tie/loss 共 22 局，Q5 loss 7 局，其余 opening 7 局。Q5 小矩阵对 Q70/Q50/Q85 的最低正差值约为 `+225`，对 Q5 自身约为 0。只把已观察 opening 层的收益计入，Q5 的保守期望约为 `22×225/36 ≈ +137`。这个数字还没有把 V37/flex 的负尾部纳入，因此只能作为“线上可能超过当前分数”的先验，不能作为确认结论；seatmix 的对应先验大约减半。

因此当前登记的两个研究候选是：

1. `candidate_v45_q5.py`：进攻型 anti-Q70 候选；
2. `candidate_v45_seatmix.py`：风险对冲型候选。

seatmix 的含义是只让 seat 0 使用 Q5，seat 1 保留 Q70。它不是为了制造随机性，而是把 Q5 的潜在收益与 RNG/非 clone 风险减半。当前 2 seed 小面板中，clone 层约 `+115.5`、V43 层约 `-149.75`；这比全量 Q5 保守，但尚未证明总期望为正。

两者都还没有达到“可提交”状态。下一轮应使用至少四个行为 lineage、每族 16–24 个 holdout seed cluster，并把线上 opening 频率作为混合权重，计算 `p_Q70 * Δ_Q70 + (1-p_Q70) * Δ_other` 的保守下界。只有下界为正且尾部风险受控，才有足够把握超过当前约 2650 的线上分数。研究期间不提交。
