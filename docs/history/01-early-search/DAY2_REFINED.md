# 第二天候选精炼记录

基于 `analysis_day2/DAY2_REPLAY_REPORT.md` 与公开讨论区主题 740792、740022、740588 的新信息，完成三候选精炼。讨论区有效线索包括：固定 replay 对手会因杂草随机数和商店重抽而产生表示偏差；应双席平均并保留未见种子块；公开经验更支持有限的对手识别/搜索式价值目标，而不是盲目 RL；销售提前只能在不破坏融资链时使用。

## 候选

1. `candidate_1_h5sim96.tar.gz`：线上分数最高的 h5sim96 基线，保留相似度 0.96 时的五回合销售预留与报价排序。
2. `candidate_2_h5roomlow.tar.gz`：容量保护的低机会成本版本，step 623 溢出时优先出售 FERTILIZER/WHEAT/CARROT/EGG，保护 premium 商品。Thomas 面板 20/20 胜，但真实线上 replay 尚未翻盘，因此作为多样性备选。
3. `candidate_3_h5strict.tar.gz`：将五回合门控阈值提高到 0.995，仅在几乎完全同布局时使用更长预留，降低对手隐藏状态不一致带来的 private shake 风险。

## 验证

在冻结 V37 的 8 局双席快速面板中：

- h5sim96：8/8 胜，平均边际 `+1190.5`，最低 `+740`；
- h5roomlow：保留此前完整面板证据，V37 22/22 胜、Thomas 20/20 胜；
- h5strict：8/8 胜，平均边际 `+1190.5`，最低 `+740`。

另测了去掉报价排序的变体，结果为 6/8 胜、平均 `+321.5`，因此已废弃，不纳入三候选。三份归档均只包含根目录 `main.py`，未提交。

## Gold audit addendum (2026-09-13)
Public Frontier code implements livestock substitution only with strict visible gates: steps 216-227, >=3 shops, exactly one BUY_ANIMAL SHEEP order qty 1-2, >=2 milk shops, no YARN_STORE, MILK price >= WOOL, own counts COW>=4/SHEEP>=2, no animal cargo/shed/pending state; confirms COW purchase via next observation before redirecting PICKUP/PLACE, and credits only physically harvested milk into existing MILK sell slot. A conservative migration tested `h5sim96_cap2_margin20.py`, changing the price gate to MILK >= WOOL+20 while retaining cap=2. On unseen V37 seeds 12001-12010 it was 20/20 wins, mean margin +2273.8 (cap2 baseline +1940.0), with no substitution triggered; therefore no regression but no causal evidence yet. Archive: day2_gold_variants/h5sim96_cap2_margin20.tar.gz SHA256 39abe97b85a536df9cf373465b58c9b0452cbb8faaf73ce3b4d9d4836e979fa9.
