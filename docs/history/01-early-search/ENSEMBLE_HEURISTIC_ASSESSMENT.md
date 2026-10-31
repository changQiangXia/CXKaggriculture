# V37 ensemble 与启发式加固评估

## 结论

让两个完全相同的 V37 对战，主要用途是验证确定性、镜像平局和运行时稳定性。双方使用同一条路线、同一套市场层时，公开状态也相同，结果天然接近镜像，不能提供新的胜率信息。

把多个 V37 做成 ensemble 只有在“策略层”才安全：在第 144/216/648 步根据公开商店、公开农场布局和已经确认的路线证据选择完整 route/profile。不能逐 action 拼接，因为每个 profile 都维护自己的 worker 位置、库存投影、销售 debt、拾取义务和 pending queue；逐步混用会破坏这些状态。

还要区分两种“ensemble”：同一局里选择一个完整 profile，和把两个候选分别作为两个 Kaggle active submissions。后者不会合并成绩，只会让不同对手/随机种子分别遇到不同 agent；在 active submission limit 为 2 时，它更像风险分散。若两个包没有策略差异（例如 V37 与它的重新打包副本），则没有任何分散价值。

当前证据不支持自动 route 切换：内部 route 0 接近基线，route 1 明显退化，route 2 在不同 seat 上方向相反；shadow selector 的所有分组 lower confidence bound 都没有超过 0。因此默认必须保持 V37，只有在未来样本形成正的、跨 seat 的置信优势时才启用 profile 选择。

## 值得继续的启发式层

1. **公开状态路线门控**：第 144 步先按前两个 shop 分类，第 216 步用动物/番茄/杂草公开差异复核，只有置信度达到阈值才切换完整 route；否则回到 V37。
2. **末期联合销售搜索**：在 648–695 步同时考虑自己的真实 shed、下一段 SELL suffix、同品 PICKUP/BUY/PLACE 义务、市场库存和 rival 的公开 standing yield。只移动已计划且真实存在的数量，并保留精确 debt 抑制；单独使用 standing yield、SELL 数量或 WEED 数量都已被实验否定。
3. **有限项目门控**：TOMATO、SHEEP、FERTILIZER 继续采用资金、容量、shop 资格和机会成本门控，并加入冷却期；项目必须证明不会挤占父路线的 hire、feed、pickup 和终局库存。
4. **物理安全层**：继续加固杂草 DIG/replay、shed 容量、无效动作和终局 liquidation。这类规则目标是消除少量确定性损失，不应重排整条路线。

## 已验证的边界

- 全局关闭 sheep overlay、放宽 TOMATO/COW/SHEEP 资格、WEED 触发全局禁用 input planner、单一 late-sale 信号和固定 seat tie-break 都出现负差，不能作为默认策略。
- Tetsutani 的五回合预留值得保留为本地候选，但截至当前 9001–9010 双 seat 面板仍出现 seed 9004 的反向 seat 负差，因此不能提交。
- 当前线上提交不变；任何候选必须先通过多对手、双 seat、720 步 DONE、无 stderr、零负差门槛，再等待用户明确授权提交。
