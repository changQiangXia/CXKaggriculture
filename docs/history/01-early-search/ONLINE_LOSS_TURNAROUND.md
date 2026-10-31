# 线上败局扭转分析（2026-09-13）

当前 active 队列仍为 `56190357` 与 `56185929`，监控进程 PID 3246 持续运行。最新自动报告覆盖 317 个 bot-side tie/lose 记录，其中 `56185929` 近期 37 场 loss 平均边际约 `-2842`，`56190357` 45 场 loss 平均约 `-4920`。

## 已确认的败因

1. 没有运行时故障：对局都完成 720 steps，日志无 stderr；主要差异来自共享市场中的 SELL 顺序、价格恢复速度和隐藏对手库存。
2. 早期三场逐步核算发现 step 623（有一场还包括 695）终日自动归仓溢出，实际丢失 4–6 EGG 及 2 FERTILIZER。问题是 carried inventory 与当轮 HARVEST 叠加，而不是只看 shed 当前库存。
3. 三场中 MILK、WOOL、STRAWBERRY 的卖出数量基本相同，收入差来自成交时点；因此只增加产量或全局延长 horizon 没有针对性。
4. TOMATO day-6 分支在少数线上局面出现高方差，终局可见 10 个 TOMATO 地块并伴随大额落后，应该作为风险门控研究对象，但目前证据不足以直接关闭该分支。
5. V231/cap2 动物替换在近期 loss 中通常只请求 1 头牛，cap2 与 cap4 行为相同，不能解释这些败局。

## 当前最有希望的修复顺序

- 先做 step-623 物理溢出反事实：只抑制会导致溢出的最低价格 HARVEST/COLLECT，保留原 market 数组和订单位置；在所有已收集 loss replay 上逐局重放，统计新增可存货、EGG/FERTILIZER 丢失量、现金和对手固定 action-tape 的变化。
- 再做商品级销售门控：只在可见库存、当前价格斜率和已有 SELL slot 同时满足时提前/延后一小批 MILK/WOOL/STRAWBERRY；每次只改一个商品和一个窗口，禁止全局销售重排。
- 对 TOMATO 只做“低现金/高库存/剩余收获不可完成”时的窄门控，并用未见 seed + 三个公开高分对手验证；若出现任一负 margin，立即淘汰。
- 将 RL 限制为离线局部参数选择或搜索式 value target，不训练完整 action policy。训练标签使用公开 observation 与引擎反事实，避免读取对手私有信息，也避免把少量线上败局过拟合成 private shake。

## 实验纪律

所有新候选必须与 h5sim96 父版本逐 seed、双 seat 对照；每局 720 steps/DONE、零 stderr；先跑冻结 V37 和公开 Flex/Thomas/Dmitrii，再检查真实 loss replay。任何候选在对手面板出现负 margin 都只保留为研究档案，不进入提交队列。当前没有执行 Kaggle 提交。

## 增量实验结果

对 `public_v37` 的 seeds 9001–9010 双席，三个容量候选均为 20/20 胜、720 steps DONE、零错误：

- `overflow623`：平均 +1773.15，最小 +368；
- `overflow695`：平均 +1842.45，最小 +466；
- `overflow623_695`：平均 +1773.15，和 623 版本逐局相同。

在 Flex/Thomas/Dmitrii 的 9001–9003 双席小面板上，`overflow695` 分别为 6/6 胜，平均边际 +3607、+7201、+5373。这个版本是目前最值得进入真实 loss replay 反事实的候选，但相对父 h5sim96 的公开面板提升只有约几十分，不能把它当作 rating 提升证据。

因此下一步先做固定线上对手 action-tape 的 695 反事实，确认它确实减少 MILK/STRAWBERRY/WOOL 等商品的丢失，并检查市场成交是否因跳过 HARVEST 而产生更大的收入损失。只有在真实 loss 样本中现金差不恶化、且减少溢出稳定成立后，才考虑将它和 623 版本并列保留。
