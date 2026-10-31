# V43 三轮谨慎修补（2026-09-16）

基线为 `v43_real_20260916/v43_optimized_final.py`，所有候选均保留末尾 TERM16 终局保护，并通过真实 Kaggle file loader 入口（文件末尾 `agent=globals().pop('agent')`）加载。未提交线上。

## Round 1：报价重排消融（回退）
将 `_R37_QUOTE` 从 `True` 改为 `False`，禁止中期连续 SELL block 的 quote priority 重排，作为订单槽位风险的保守对照。小 panel 使用 public_v37 与 ready_flex，seed 9001/9004，双 seat，共 8 局。候选结果：public_v37 平均资金差约 20,502.3，ready_flex 约 25,530.8；基线分别约 21,363.3 和 25,997.5。两个对手族均下降，故回退，未采用。

## Round 2：边界 overflow 销售消融（回退）
将 `_R148_OVERFLOW` 从 `True` 改为 `False`，禁止日边界回收被 dawn 丢弃的尾部库存，检查其是否放大市场槽位风险。相同 8 局 panel：public_v37 平均约 20,906.8，ready_flex 约 25,875.5，低于基线；回退。

## Round 3：自适应 horizon probe 消融（中性/回退）
将 `_R37_ADAPTIVE` 从 `True` 改为 `False`，保留 quote ordering 与 TERM16，仅移除相似布局触发的 horizon=3 探针。相同 8 局 panel：public_v37 平均约 20,906.8，ready_flex 约 25,875.5；与 round2 相同，说明该 panel 中 probe 未激活或无行为差异。没有证据支持合入，回退。

## 结论
三轮均为针对性小修补和消融，没有候选在未见 seed、双 seat、两类公开对手上稳定优于基线。最终推荐继续使用冻结 V43 parent，不提交这些回退候选。下一轮应建立同 seed 的 parent/candidate action diff，按 step 288/432/576/648/672 记录实际成交，而不是继续扩大终局或订单重排启发式。

## Loader 检查

使用 `kaggle_environments.agent.get_last_callable` 对 parent 和三份候选的原始 Python 文件逐一加载；四者均返回最终 `agent`，且返回函数 globals 中存在 `_TERM16_PARENT`，确认测试走的是上传时的最后 callable，而不是中间命名的 parent。所有 panel 对局状态均为完成，无异常输出。
