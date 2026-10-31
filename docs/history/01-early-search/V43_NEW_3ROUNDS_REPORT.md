# V43 新三轮谨慎优化报告（2026-09-16）

基线：`v43_real_20260916/v43_optimized_final.py`。本轮没有提交 Kaggle，也没有替换冻结线上版本。三份候选都用 `kaggle_environments.agent.get_last_callable` 的真实文件入口加载；每场 720 steps、状态 DONE、无运行错误。

验证 panel：`public_v37_pkg/main.py` 与 `ready_flex_v7/main.py`，seed 9001、9004，candidate/parent 各自 seat 0/1 配对，共 8 场/轮（24 场运行，候选与基线在同一 seed/对手/座位比较）。完整机器结果见 `results.json`。

## Round 1：末尾 SELL 的严格库存合同

只检查 parent 产生的最后一个订单。只有当它是 SELL、该商品在前面订单中没有出现、订单数量是整数且超过当前 `_r127_fields` 投影的 shed 库存时，才把数量降至投影库存；订单本身保留在原 slot，任何不确定性都回退原 action。目的在于观察“去掉无法兑现的过量请求”能否改善订单前缀风险，同时不移动任何 slot。

结果：8/8 paired delta 为 0；候选和基线每场 margin 完全一致。该条件在 panel 中没有改变有效 action，不能证明线上收益，回退。

## Round 2：终局追加订单的空槽位安全门

设计目标是只允许终局 TERM16 追加销售在仍有充足订单槽位时发生，以避免在订单列表接近上限时与 parent 的末尾订单交互。实际实现保留 parent action，不做未经证明的槽位改写；因此它是一个 baseline-preserving contract scaffold，用于确认“仅加安全门”本身不会带来收益。

结果：8/8 paired delta 为 0；所有对局 DONE。由于没有行为差异，不能把它计为有效优化，回退。

## Round 3：限制 TERM16 在高订单占用时追加肥料销售

step 718 如果已有市场订单超过 8 个，且最后一个订单是 TERM16 追加的 SELL FERTILIZER，则移除这个新增尾订单；保留所有原有订单及其顺序。该轮直接测试终局追加是否在高 slot 占用时造成风险。

结果：8/8 paired delta 为 0；panel 中没有触发可见的 margin 改变（所有对局均 DONE）。没有观察到收益或回归，回退。

## 汇总

| Round | 机制 | 场数 | 正 delta | 负 delta | 平均 delta | 决定 |
|---|---|---:|---:|---:|---:|---|
| 1 | 严格末尾 SELL 库存 cap，保留 slot | 8 | 0 | 0 | 0 | 回退 |
| 2 | 终局槽位安全门 scaffold | 8 | 0 | 0 | 0 | 回退 |
| 3 | 高占用时抑制 TERM16 尾部肥料 SELL | 8 | 0 | 0 | 0 | 回退 |

这三轮没有产生可提交候选。原因不是测试出现正负抵消，而是固定的 8 场 paired panel 中 candidate 与 parent 的最终 margin 全部相同。该结果也说明当前公开 benchmark 没有触发这些严格条件，不能据此推断中期市场问题已经解决。下一步应在真实失败 replay 的 step 432–648 期间做同状态、同对手的成交量和订单槽位反事实；继续做终局微调没有证据支持。

SHA-256：

- round1/main.py `4562d7c6f507f3ceaaaabe5055083f32426b844afe7bb1ddc8ef261cc3e5b754`
- round2/main.py `fa00112ae0454b4644c5cdaa7984eec51ffc54e8b325bcf2ae2f641bfeeb7b78`
- round3/main.py `c980509d5685a4df737eaafec27f72cc8a3c168b627002409a8cdfccac30c493`
