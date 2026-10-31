# 两个备选模型的两轮编写/审阅总记录（2026-09-15 12:56:15 UTC）

## guts_（规则独立模型）

Round 1 从 README/AGENTS 和官方 engine 语义独立实现观察驱动的 crop economy：优先 water/harvest，melons→wheat，有限 hire、shed sell、移动任务分配；未读取公开 agent、replay 或其他模型。Round 1 审阅发现 harvest-before-water 和 melon selector 的边界错误。

Round 2 修复上述问题，保留 parent-safe fallback 和合法 action 形状。`round2_main.py` 与最终 `main.py` SHA256 前缀 `c41cbbe3`。真实 engine smoke：seed9001 vs pass、seed9002 vs starter 均 DONE/720，资金分别 15548、15594。它是独立范式候选，不代表已超过 V42。

## inspired_

Round 1 以 no-R128 V42 为父策略，吸收优秀公开提交的 bounded one-turn premium timing 思路；只读当前 observation、父 route future SELL、town shops 和 shed，不读对手隐藏状态。Round 1 审阅指出必须加入 repayment debt，否则会凭空增加销量。

Round 2 加入 next-turn 同商品 repayment ledger，偿还不足回退 parent；继续限制 day24–28、非四回合边界、premium 商品和每次一单位。审阅又发现 telemetry 静态字典问题，已改为共享计数并通过 py_compile。真实 engine smoke seed9001 对 pass 完成 DONE/720；当前触发为 0，说明需要后续 activation profiling，不能宣称有收益。

两个模型都未提交 Kaggle。下一步只在 engine 正确、对象新鲜、未见对手 holdout 上做测试。
