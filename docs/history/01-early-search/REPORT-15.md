# V43 新三轮谨慎实验（2026-09-16）

基线为 `v43_real_20260916/v43_optimized_final.py`。三轮均用真实 `get_last_callable` 加载，`public_v37`/`ready_flex_v7`、seed 9001/9004、双 seat，共 8 个 candidate-parent paired games/轮；全部 720 steps、DONE、无错误。结果保存在 `results.json`。

## Round 1：严格末尾 SELL 库存合同

仅当最后一个 SELL 商品此前没有同商品订单，且当前 shed 库存可精确计算时，才把过量数量收紧到当前库存；保留订单槽位和所有前缀，任何不确定状态都回退。8 对 paired delta 全为 0，说明该场景没有触发或不改变成交；没有收益证据，回退。

## Round 2：TERM16 至少保留两个空槽

尝试要求终局 fertilizer append 前至少有两个空订单槽，以降低共享市场交互风险。实现等价于基线，8 对 delta 全为 0；没有新增行为或收益证据，回退。

## Round 3：高槽位时抑制终局 fertilizer append

当 step 718 parent 已有超过 8 个订单时，抑制新增 fertilizer SELL，保留既有订单和槽位。8 对 delta 全为 0；该条件在 panel 中未产生可见差异，不能证明泛化收益，回退。

## 结论

三轮没有发现稳定优于冻结 V43 的改动；没有新 tar 推荐，也没有提交线上。当前应继续冻结原 V43，下一轮应直接做中期市场成交的同 seed 反事实记录，重点是 step 432–648 的实际成交量、价格和订单配对，而不是继续堆叠终局保护条件。
