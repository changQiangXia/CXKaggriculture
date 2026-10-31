# Nathan corrected 线上回放审计（2026-09-16）

## 数据可用性

提交 `56270791` 的 receipt 显示已上传但当前目录没有该 submission 的 episode/replay；因此本报告不把任何旧 replay 当作 corrected 的线上证据。corrected 包只修复 loader 父类指向：`_NC2_PARENT` 改为 `_NC_PARENT`，旧 wrapper 实际绕过，故本地动作级配对未观察到行为变化（8 个同 seed/对手/座位配对 delta=0）。待平台产生回放后，必须重新统计。

## 旧 Nathan 作为窗口基线

从 `current_submission_diagnosis_20260916/replays` 读取原 Nathan `56257428` 的六场大幅落后回放。以 CHEN Xiang 的 money margin（我方减对手）计算每个时间点过去 24/72 步变化：

| episode | 对手 | 最坏 24 步窗口 | 最坏 72 步窗口 | 备注 |
|---|---|---:|---:|---|
| 109437616 | kobayasi | step 410, −3180 | step 458, −5156 | 双方动作高度镜像；约410附近卖单顺序和批量分叉 |
| 109392182 | forever young | step 591, −4251 | step 681, −3981 | 后期累积差距，非单一终局动作 |
| 109518675 | Inzilbêth | step 440, −2000 | step 440, −2012 | 中期销售/生产路径分叉 |
| 109386768 | abozten | step 485, −2586 | step 490, −3091 | 中期持续落后 |
| 109502811 | Howon Kang | step 664, −3730 | step 664, −3593 | 后期扩张或现金投入分叉 |
| 109516516 | NikolaiLeukhin | step 487, −3375 | step 487, −3400 | 中期集中分叉 |

这些数字描述原 Nathan 的失败形态，不能证明 corrected 已改变或改善它们。窗口聚集在 410–490 和 664 左右，适合上线后做分层诊断，不能据此写死 step 规则。

## 后续核查协议

拿到 corrected replay 后：

1. 按对手类型分组，先判断对手是否与 Nathan 同类（动作镜像、相近 shop/投入节奏）。
2. 同类对手：比较 24/72 步 margin 最大下降窗口，检查双方 SELL/PICKUP/扩张顺序。
3. 异类对手：寻找该对手和其他玩家的回放（同 seed/相近 shop 与生产状态优先），比较其在 Nathan 与他人局中是否针对同一资源约束；单局只能提供灵感，不能单独归因。
4. 记录 action hash、实际成交量、现金、库存和生产变化；避免把请求量、未触发 wrapper 或终局单一动作当成收益来源。
