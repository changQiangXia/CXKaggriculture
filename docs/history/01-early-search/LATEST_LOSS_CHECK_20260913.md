# 最新线上败局检查（2026-09-13 约 11:55 UTC 状态）

监控状态：`agent_monitor/state.json` 最后更新 03:55 UTC；队列仍是 56190357 与 56185929。daemon 最近一次实际新增日志为 56190357 episode 108400163（03:25 UTC）；之后多次 scan 结果为 0。当前 monitor.pid 文件对应进程已退出，但没有证据需要重启（此前 daemon 日志已完成当前缓存扫描；root 应自行核验是否按预定持续运行）。

## 结果统计

- 56185929（h5sim96）：143 场（105W/37L/1 validation），最新 loss 到 episode 108396380。按最近可读 replay 的 12 个 loss，平均边际约 -2232；其中 108391650 -4406、108396380 -4081。
- 56190357（room623）：118 场（71W/46L/1 validation），最新 loss 到 episode 108400163。最近可读的 27 个 loss 平均边际约 -5813；108400163 为我方 100018 vs 对手 105494，边际 -5476。

## 败局共同结构

Replay 的 623 和 695 是日末自动归仓前的关键观察点。大量 loss 在 step 623 时 shed+carried 已经超过 100（例如 56185929 的 108391650/108396380 为约 116，56190357 的 108400163 为约 119）；典型差异是 EGG 4–6、FERTILIZER 2、WHEAT 11–15 仍在 carried/shed 中。到 step 695，很多局又有约 111–132 单位待归仓，典型为 MILK 8、STRAWBERRY 17、FERTILIZER 2、WOOL 3、WHEAT 2–6。说明容量压力仍普遍存在，但 replay 中从 623→624、695→696 的数量变化混合了 harvest、DROP 和 SELL，不能单凭总数变化把每个差额都标成丢失。

极端局 56190357/108333303（-49779）终局 10 TOMATO，且 623 处 carried+ shed 约 114；108350906（-4555）和 108375468（-851）也在 695 前后出现 113、132 单位压力。TOMATO 路由与大幅败局相关，但非每个 TOMATO 局都输，不能直接关闭路线。

### 商品订单形态

同一策略在多数 loss 中的申报量几乎固定：普通路径 SELL WHEAT~17334、FERTILIZER 10357、WOOL 6198、MILK 8267、MELON 6072、EGG 8077、STRAWBERRY 6291、CARROT 17048、TOMATO 6000；高产路径则约翻到 WHEAT 24300、FERTILIZER 18343、WOOL 11700、MILK 9330、STRAWBERRY 13280 等。因而败局不是“少生产/少申报”这一类单一错误，仍更像共享市场中 SELL 成交顺序和价格滑落；同商品申报量相同也可能相差数千分。

## 后续计划

1. 对最新 56190357/108400163、108395272 和 56185929/108396380、108391650 做固定对手 action-tape 反事实：逐项记录 step 623 抑制 harvest/collect 后的实际 DROP、shed overflow 和现金差，避免只看库存总数。
2. 继续只测试 step-623 窄 guard；不采用每个日末主动 SELL 的 room623 版本，因为它会改变共享市场队列。候选 `day2_gold_variants/h5sim96_overflow623_pkg` 需要在真实 loss replay 上证明减少实际丢失后才保留。
3. 对 MILK/WOOL/STRAWBERRY 各做一次单商品提前一回合 SELL 门控，保留原 slot 顺序与数量，并在未见 seed + loss tape 上看现金差；任一出现负 margin 就淘汰。
4. 对 TOMATO 只做窄风险门控（现金不足、剩余回合不足、仓库压力已超过阈值），不做全局关闭。暂不进行完整 RL；如需 RL，仅用于上述局部门控的价值排序。
5. 严格本地验证、双 seat 配对、720 steps/DONE、无 stderr；没有用户明确授权不提交。

> 注：当前 shell 核验 `monitor.pid`=2009，但该 PID 不存在，`pgrep` 未发现 monitor_agent_logs 进程；state 最后更新为 03:55 UTC。若期望持续扫描，root 需要确认是否重启单实例 monitor。
