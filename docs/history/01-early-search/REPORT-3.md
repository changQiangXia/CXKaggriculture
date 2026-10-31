# v37_h5roomlow

基底：`public_v37_pkg/main.py`。候选保留 h5sim96 的阶段 horizon 规则，并额外启用原有 `room_guard` 的低机会成本容量排序：step 623 预测跨日容量压力时优先处理 FERTILIZER/WHEAT/CARROT/EGG 等低机会成本库存，保护 MILK/STRAWBERRY/WOOL。它不是全局停止 harvest 规则。

源码 SHA256：`92fec7730a31cfe006dd6e4b4112476a16329495d1589b157752ddaf98b4f2fd`  
候选包 SHA256：`0aae4a0f8160e446ae22e4aed2ad5ca3006c1b0801b8045092555ad749273a87`

## 证据状态

历史 [H5ROOMLOW_VALIDATION.md](/root/autodl-tmp/H5ROOMLOW_VALIDATION.md) 报告了冻结 V37 22/22、Thomas 20/20 的旧面板，但这些结果没有完整保存 stderr、最终 status、latency，也没有 candidate/parent 的 common-random-number 配对，因此只能作为研究线索，不能作为晋级证据。

当前 `run_paired_audit.py` 正在对该候选和冻结 v37 使用同 seed、同 seat、同对手运行，并保存双方 reward、margin、paired delta、DONE/status、stderr、最大 action duration、源码路径和 SHA。结果落盘前不作结论。

## 当前判定

`rejected_tail_and_runtime`。新的可信 paired audit 已发现 v37 对照 seed 70117、seat 0 的 candidate margin `-4`（父策略自对局为 0，paired delta `-4`），且最大 action duration `2.60s`。这违反零负 margin 和运行时安全门槛；其余面板仍会完成以归档失败边界，但该候选不得晋级。
