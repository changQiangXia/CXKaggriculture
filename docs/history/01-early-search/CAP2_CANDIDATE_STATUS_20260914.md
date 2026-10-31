# cap2 后续候选状态（2026-09-14）

当前基线为已上传的 `56209639` 对应 `h5sim96_cap2`。本地所有后续实验均未提交。

## 已否证

- `cap3`：第三头牛替换在 9001–9005 面板及 6 场线上 loss tape 中均与 cap2 完全相同。
- `strict`（similarity 0.995）：9001–9005 双席逐局与 cap2 完全相同。
- `MILKLEAD`：跨公开面板收益仅 +2.6 到 +8.2；Flex 轻微下降；最近严格 replay 平均 -3；不稳定。
- `EGG/FERT` step-623 guard：9001–9005 双席与 cap2 完全相同，未触发。
- `quote_floor`：最新 5 场 cap2 loss 中 4 场相同、1 场 -69；淘汰。
- 对缺失 `(BAKERY,PET_CAFE)` 显式填入 route 3/5/7：最新 loss 分别恶化约 9.6k–10.4k。

## 当前证据

cap2 新增 5 场 loss 的共同点是 step 623 shed 常达 100，但无 carried inventory；产品价格结构差异很大（有的 MILK 高、有的 MILK 低而 WOOL 高）。因此单一容量阈值或单商品价格阈值无法解释所有败局。

监控进程保持 PID 1670 单实例，每 600 秒扫描 active 队列 `[56209639, 56190357]`。提交权限仍保留给用户；任何候选必须先完成双席公开面板、至少三个高分对手 holdout、严格 replay 对齐和无 stderr 检查。
