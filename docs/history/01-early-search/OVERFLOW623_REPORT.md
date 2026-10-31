# h5sim96 step-623 overflow guard（未提交）

## 目的

线上旧败局的精确引擎核算显示，step 623 终日自动归仓前会出现 carried inventory + 当轮 HARVEST/收集产物超过 shed 容量，造成 EGG/FERTILIZER 丢失。只改 step 623，避免 room guard 在每个日末额外添加 SELL 而改变共享市场顺序。

候选从 `candidate_v37_h5sim96_pkg/main.py` 派生。step 623 若预测 `shed + carried + 当轮产出 > 99`，按可见价格从低到高把当轮 HARVEST/COLLECT_FERTILIZER 改为 PASS，直到预估不溢出；不改 market 数组，不读取对手私有状态。其它 719 个决策保持父策略。

## 本地验证

环境为本机 `kaggle-environments`、720 steps、双 seat。

- 对 `public_v37_pkg/main.py`，seeds 9001–9010 共 20 局：20/20 胜，平均边际 `+1773.15`，中位数 `+1560`，最小 `+368`；全部 `DONE`。
- 同一对手和 seeds 的 h5sim96 父版本（9001–9005 双 seat）：10/10 胜，平均边际 `+1815.1`，最小 `+740`。
- 因此 step-623 guard 在这组 public_v37 面板相对父版本略低约 42 分，不能宣称提升 rating；它的价值在于直接覆盖已核实的线上溢出机制，需继续用真实 loss replay 做反事实核验。

归档 SHA256：`da8db108d795b91c5af09ccc85f8bdde2613643f87903565a4fb0f22144a7778`。

没有执行任何 Kaggle 提交。
