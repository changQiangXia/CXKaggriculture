# 56185929（h5sim96）线上对局分析

更新时间：2026-09-12 UTC。该报告回答为什么新提交的 rating 暂时比 V37 低约 200 分，并记录目前可证实的败因。

## 当前结果

官方 `competitions submissions` 查询：

- h5sim96 `56185929`：`2574.3`
- V37 replay 基线 `56181773`：`2705.8`

差距已经从约 200 分缩小到约 131 分。新提交当前有 41 场 public episode：35 胜、6 负、0 平，另有 1 场 validation。双方每场均完成 720 steps；已抽查的 loss 日志均为 719 次调用、空 stdout/stderr、最大耗时约 0.25–0.37 秒。最新两场 loss 为：

| episode | 对手 | 我方 seat | 我方:对手 | 差值 |
|---|---|---:|---:|---:|
| 108205627 | Roshan Roy | 1 | 73869:75995 | −2126 |
| 108208668 | hidenov | 1 | 59138:59264 | −126 |
| 108209687 | Kostiantyn Isaienkov | 0 | 101130:102655 | −1525 |
| 108214831 | presucc | 1 | 118965:120900 | −1935 |
| 108217834 | yurunougyou! | 1 | 67658:68149 | −491 |
| 108219413 | Tim Zagrebelny | 1 | 73593:73846 | −253 |

所有这些 loss 都是正常完成的比赛，不是超时、异常恢复或打包错误。

## 为什么总体胜率很好，rating 仍低于 V37

比赛 Evaluation 页面明确说明：rating 只看胜、负、平，不看终局金币差；而且新 bot 会以默认 rating 加入匹配池，先与相近 rating 的 bot 逐步匹配，最终 rating 需要更多比赛才能降低不确定性。

h5sim96 的 41 场并不是同一强度样本。前 24 场全胜，对手大多是刚加入匹配池的低 rating bot；从后面进入约 2400+ 对手段后，记录是约 6 胜 4 负，2500+ 对手段为 2 胜 3 负。当前记录的总体 35 胜 6 负（85.4%）被前期低强度对手明显抬高，不能外推成对 2700 bot 的 85% 胜率。

因此当前约 131 分差距的主要解释是：

1. 新提交从默认 rating 开始，早期胜局主要是在爬梯，不等于已经证明达到 V37 的 rating 层级；
2. 接近 2500–2700 的对手中已经出现明显败局，rating 会按胜负逐步修正；
3. h5sim96 最近仍在上升，曾从约 2528.5 升到 2574.3；这说明它还没有“收敛到最终强度”；
4. V37 已有约百场比赛，rating 估计稳定得多。当前两者不能只用一次 publicScore 横向比较。

## 三场可重建败局的真实原因

[LOSS_MECHANISMS.md](analysis_h5_20260912/LOSS_MECHANISMS.md) 对前三场 loss 做了逐回合核验：线上候选源码在三场中均逐字重现 719/719 个 action；本地按线上 replay 的工人行动和市场规则重建了 4314 个现金状态，残差全部为 0。

三场的 `_r37_similarity` 在 step 288–647 每一轮都是 1.0，所以相似度门控 360/360 轮全部打开。这个相似度只看同坐标的 crop/animal 类型和解锁区，完全看不到对手的销售时机、分批数量、市场 order 位置、carried inventory 或 pending obligation。因此 h5 门控无法识别这些“农场一样、销售打法不同”的对手。

实际损失主要来自高价商品销售时机，而不是生产量：

- Roshan：MILK/STR AWBERRY/WOOL/EGG 收入差分别约 `−536/−683/−1441/−240`；对手 step 385/387 卖 14 WOOL 得 796，我方 step 392 卖同量只得 68；
- hidenov：同量 STRAWBERRY 和 MILK 的时序造成主要差额，最终只差 126；
- Kostiantyn：MILK/WOOL/STRAWBERRY 收入差约 `−1454/−979/−598`，但也存在我方等待反而更赚的草莓片段，所以不能简单把 horizon 全局拉长。

另外三场都发现 step 623 终日入库前容量溢出：carried inventory 加 shed 超过 100，丢失约 `EGG 4–6` 和 `FERTILIZER 2`；hidenov 局 step 695 又丢 2 fertilizer。这个问题此前的“容量保护完备”判断不准确，应该作为下一轮本地实验的第一优先级。

第四场 `presucc` loss 的终局公开农场显示对手有 TOMATO=10，而 h5 仍是标准 COW/SHEEP/GOOSE 路线；这与 TOMATO 路线门控的已知风险一致，但尚未做成候选与 V37 的配对反事实。

## 对验证证据的纠正

先前 `CANDIDATE_V37_H5SIM_REPORT.md` 中有三处表述过强，已由 [H5SIM96_VALIDATION_AUDIT.md](H5SIM96_VALIDATION_AUDIT.md) 纠正：

- V37 面板实际是 seeds `9001–9010 + 1495252849`，即 11 seeds × 2 seats = 22 局，并非 `9001–9020`；
- Flex/Dmitrii 的保存数字来自旧的 similarity `0.90` 实验，不是最终 `0.96` 候选的完整重测；
- 15 个线上 loss seed 的 30 局实验是候选对冻结 V37，不是候选对原线上真实对手，因此不能宣称“修复了线上败局”。

本机 engine parity 另已用 4 个线上 replay 做逐状态比对：本地 kaggle-environments 1.25.9 与线上标记 1.32.7 的 Kaggriculture 机制在 720/720 状态上完全一致，不能把当前差距归咎于本地引擎版本。

## 结论与下一步

当前低于 V37 约 131 分是“新 rating 尚未完全爬升 + 对高 rating 对手仍有真实策略缺口”的共同结果，不是单纯的 public 样本抖动，也没有证据说明 h5sim96 已经稳定强于 V37。

应优先在本地做可证伪的容量修复：在 step 623/695 的 end-of-day 入库前，把 carried inventory 与 shed 一起纳入 projection，优先对已存在且即将被丢弃的 EGG/FERTILIZER 做安全销售或 PLACE，并在真实交互的 TOMATO、早卖 premium、分批销售对手面板上验证。修复候选必须重新跑双 seat 全 panel、真实对手 panel 和 latency/error 检查；当前不自动提交。
