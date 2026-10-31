# 金牌区策略迁移实验

## 公共高分信息

通过 Kaggle kernels 拉取并审阅了高票公开 notebook：

- `indarkarhana/shape-the-shop-work-the-pasture-top-10`：可见状态需求对齐、保守的牛羊替换、逐步资金/库存/放置验证、失败则回退父策略；报告给出 136/150 paired blocks 的 post-freeze diagnostic，但强调不能把录像 action tape 当作私有适应策略。
- `prvsiyan/kaggriculture-frontier-the-moon-counts-melons`：四回合销售预留、严格 stock/purchase/pickup barrier；milk/cow 替换只在多商店需求、价格条件、数量和运输状态都满足时触发。其公开负例显示供给预测 precision 很低，固定 replay 会受到杂草随机数和商店重抽的严重偏差。
- `tetsutani/market-smart-farming-kaggriculture`：强调 bounded five-turn sale reservation、72-turn shop block boundary、债务记录和终端安全。
- 讨论区 740792/740022/740588：建议双席平均、保留未见 seed block；对手识别只使用可见农场；搜索式 value target 比盲目 RL 更可靠；直接复制对手会因共享市场顺序导致 flood 和 tie/loss。

## 新实验

先用公开 Top-10 E776 archive 做基准对照：其 latent-pasture 多层 guarded policy 在冻结 V37 的 8 局双席测试中为 `0/8` 胜，平均边际 `-15,163`；这说明将金牌区完整方案原样移植并不能迁移，原因是依赖其原始 action tape、隐藏 farm occupancy 和不同随机轨迹。

随后对 h5sim96 的动物控制器做了保守多样性实验：

- `h5sim96_cap2.py`：将已有 V231 visible-demand 牛替换上限从 4 降到 2；V37 8 seeds 双席 `16/16` 胜，平均边际 `+1901.3`，最低 `+740`。
- `h5sim96_cap0.py`：关闭该牛替换控制；V37 8 seeds 双席 `14/16` 胜，平均边际 `+1631.7`，最低 `-455`。

cap2 的改善是初步信号，样本只有 8 seeds，不足以证明 public rating 提升；它比完整 gold-zone archive 更适合迁移，因为只改变一个可见状态门控，保留 h5sim96 的路线、销售和终端安全。

## 当前未提交候选

1. `day2_gold_variants/h5sim96_cap2.tar.gz`：首选探索候选，已有 `16/16` 冻结 V37 胜。
2. `ready_candidates_day2_v2/candidate_1_h5sim96.tar.gz`：线上分数最高的原 h5sim96 基线。
3. `ready_candidates_day2_v2/candidate_3_h5strict.tar.gz`：五回合门控阈值 0.995 的 private-risk 保守版。

三个候选均未提交。继续用未见 seed block、真实线上 replay 和新高分录像做验证后，仍需用户明确授权才可提交。
