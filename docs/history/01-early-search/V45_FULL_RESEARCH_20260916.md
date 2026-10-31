# degnonguidi cloning-agent V45 全方位研究（2026-09-16）

## 提交与来源

公开 notebook `degnonguidi/kaggriculture-cloning-agent` 已用 `/root/miniconda3/envs/kaggle-cli/bin/python` 拉取。其 pinned source 生成：

- `main.py` SHA-256 `2536d41ed5a00c75204b6350f1c76c54259c774cb065ba2a3a0072eedf210d94`
- `submission_competitive_v45.tar.gz` SHA-256 `b8c2f5aab88faf2332e45f721ec83e5f9e7bec3d0a995cc0dce318badd884ed0`
- Kaggle submission ref `56278920`
- 上传 URL 已按要求从 `www.googleapis.com` 改写为 `storage.googleapis.com`
- 最终状态 `COMPLETE`，public score **1820.8**

提交 receipt 在 [V45_SUBMISSION_RECEIPT_20260916.md](/root/autodl-tmp/V45_SUBMISSION_RECEIPT_20260916.md)。

## V45 实际改动

Notebook 说明 V45 保留 V44 的完整生产、服务和 clone-gated sale pre-emption，只新增 EXP284 的 step-0 market arm：父策略原本发出

```text
BUY_PRODUCT WHEAT 5
BUY_PRODUCT WHEAT 10
SELL WHEAT 60
```

V45 改为

```text
BUY_PRODUCT WHEAT 70
SELL WHEAT 70
```

round trip 在市场总量上接近中性，但会改变同一 market index 上双方每单位报价的库存顺序。该改变的目的，是让采用“第二次 wheat purchase”开局的 route-tape 对手在其第二个槽位面对更高的 wheat scarcity，从而可能少买一批 MELON seed。V45 只在 step 0 且父动作精确匹配时替换，step 1 还有一个极窄的 wheat feed 修正。

V45 还包含 EXP283 的 clone-gated race arm。它只使用公开 farms、公开市场库存/价格、shops 和动作，不读取对手 private shed。检测到双方连续 4 个窗口高度相似后，先把销售 reservation horizon 设为 8；若观察到对手在自身库存刚进入 shed 的同一回合卖出，而我方没有卖，则将 horizon 提升到 24。它在一次本地 V45 vs V43、seed 9001 的完整局中触发了 476 个 clone-horizon 回合，但没有 race escalation。

## 独立本地验证

本地使用 engine SHA `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`，720 steps，所有局均 `DONE/DONE`。V45 对 4 个本地对手、4 个 seed、双 seat 的 32 场独立对局如下。这里是 V45 自身最终 margin，不是与 V44 同世界的因果 paired delta：

| 对手 | 场数 | 平均 margin | 胜/负 |
|---|---:|---:|---:|
| 当前 V43 | 8 | +1,967 | 7/1 |
| corrected Nathan | 8 | +1,301 | 8/0 |
| public v37 | 8 | +9,216 | 8/0 |
| ready flex | 8 | +11,926 | 8/0 |

另外，starter 对手 seed 7/1234 两局均完成，V45 reward 分别为 `[172566, 3484]`、`[183271, 3531]`；V45 self-play、完整 720-step smoke 和源码入口检查均通过。

## 机制消融

### Opening arm

将 step-0 round trip 关闭后重新运行的对照只能作为诊断，不能当作严格因果实验，因为 step-0 市场动作会改变后续 market 和 town RNG 的消耗。该诊断仍显示 opening arm 是行为差异的主要来源：对 v37/flex 的多场 margin 变化很大，而对 Nathan 几乎没有差异。它证明 V45 不是“只换一个无影响的订单格式”，而是主动选择了特定 route-tape 的 shared-market interaction。

因此应把 notebook 的“对旧 route-tape 家族有效”理解为条件性假设，而不是泛化结论。若线上对手更常采用相反的 opening（先卖 wheat 再买），round trip 会把价格优势转给对手；notebook 自己也承认这一 trade-off。

### Race arm

将 race horizon 和 escalation 都压回 4 的局部消融，在 8 场 V45/V43、Nathan、v37、flex 对局上得到：

- 对 V43：开启 race arm 平均高 1,347；
- 对 Nathan：平均高 1,909；
- 对 v37：平均高 4.8，基本不触发有效差异；
- 对 flex：平均低 31.3。

样本很小且不是同世界反事实，但说明 race arm 的影响主要集中在与 V45 路线高度相似的策略，面对 flex 可能轻微伤害；它不是线上低分的唯一解释。

## 代码与安全审计

通过 AST 和源码检查，V45 使用 stdlib `copy/base64/json/zlib/math/itertools`，没有 requests、网络调用、动态下载或读取对手 private state 的代码路径。内嵌 engine source 标注为 kaggle-environments 1.32.7，SHA 与本机正确游戏模块一致。clone/race 特征来自公开 `farms`、market 和 town，符合不使用对手私有库存的约束。

代码仍然有明显的策略风险：

1. step-0 market arm 依赖对手的开局族分布。它改变共享 market index 和未来 RNG，不是自家独立交易。
2. race arm 的“刚掉货、对手在同回合卖出”是从公开市场变化反推对手动作模式，可能对同类策略有效，却会在异类策略上触发错误 horizon。
3. horizon 24 的销售预留比基础 4 步窗口激进，虽然有 clone gate，但一旦误判 clone，会提前锁定错误商品的销售数量。
4. notebook 声称 1,280 个独立世界、640 个完整 ledger audit 和很大的 V44→V45 uplift；公开 notebook 只携带结果文字和 source blob，本地没有这些世界的原始 seeds、逐局账本或可复算脚本，因此这些数字不能被独立复核。
5. notebook 明确承认 first-turn change 会重新抽取 shared shop draws，因此普通固定 tape replay 不适用于这项改动。这也限制了从少量失败录像推断原因的可信度。

## 线上结果与研究判断

线上 public score 为 **1820.8**，明显低于 notebook 宣称的 development/independent mean margin 与当前已提交 Nathan/V43 的 contemporaneous score。由于 Kaggle 分数受时间和对手池影响，不能把它当作严格 paired proof；但它足以否定“本地公开 route-tape 面板的高胜率就代表线上泛化”的假设。

当前最可信的解释是：V45 的 step-0 round trip 过度依赖特定 route-tape/opening 家族。它可能在 notebook 选择的镜像或克隆对手上制造共享 market 优势，但线上未知对手的 opening 分布不同，且第一回合改变 RNG 后会改变后续 shops、产量和价格路径。race arm 的影响相对局部，不能单独解释低分。

后续若继续研究，应该先把 step-0 机制拆成至少三组独立对手族：

- 第二槽继续 BUY wheat 的 route-tape；
- 先 SELL wheat 再 BUY 的 Two Coins opening；
- 不进行 wheat round trip 的动态/非镜像 opening。

对每组都要记录第一回合实际每单位成交价格、第二回合 MELON seed 是否真的少买、后续 shop/产量变化，以及完整 cash/product ledger。只有在三类对手中都不显著恶化，才有资格把 opening arm 作为泛化策略；否则应把它视为特定对手族的 exploit，而不是模型范式。
