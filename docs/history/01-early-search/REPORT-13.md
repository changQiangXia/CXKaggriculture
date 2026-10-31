# v3 线上 2401 分审计

## 结论

Kaggle API 返回 submission `56303424` 为 `COMPLETE`，文件名 `candidate_v45_q25_sellsearch_v3.tar.gz`，141708 bytes，上传时间 `2026-09-17T11:36:06.373Z`，public score `2401.0`。这就是当前工作区 `q25_search_20260917_055120UTC/candidate_v45_q25_sellsearch_v3.tar.gz`：完整 archive SHA-256 为 `4ba0937507b352ec5c9b41b2ad8e4bc766873e0feb5703524bc6cd626d8f7395`；包内 `main.py` 与工作区 v3 源码的完整 SHA-256 均为 `e262fe4f218effbd4bce1f0089f20e86f769b8b181e0c46ba51b0e21ff8c93d9`。文件在本机 `18:42 +0800 = 10:42 UTC`，早于上传，当前证据不支持上传后漂移。

上一版本直接为 submission `56287561` / `candidate_v45_q25.tar.gz`，该次评级快照为 `2582.0`；两次 submission 评级快照相差 `181.0` 分。这个差值不能因果归因于 v3，也不能直接换算成策略强度变化，因为两次评分面对的线上对手池、时间和隐藏配对可能不同。其他参照快照：Q20 2603.3，competitive_v45 2596.4，nathan_cautious_corrected 2448.0。

## 线上回放保真

58 场本地保存回放统计 v3（CHEN Xiang）35 胜、23 负。负局平均分差 -646.1，中位 -532；最大四局为 Debmalya -2899、yukio -1841、Kilupy -1534、Debmalya -1050。针对四个最大负局及两近平局，以包内 root `main.py` 的官方 `get_last_callable` 执行每个 pre-action observation，并按回放的 inventory 键顺序对齐。v3 六场均为 `719/719` action fidelity，错误为 0；对应父 Q25 五场为 `719/719`，一场为 `718/719`，唯一差异在 episode `110101510` callback `575` 的重复 WHEAT SELL 次序（父模型输出 `[1,4]`，回放为 `[4,1]`）。证据见 `fidelity_ordered_results.json` 与 `fidelity_parent_ordered_results.json`。这只是六场抽样的 loader/行为保真检查，不能据此排除所有环境或所有回放中的问题；但它不支持当前六场由压缩包根文件或 loader 错误造成。

## search 实际覆盖

在 58 场 replay pre-action observation 上离线重放 v3，得到 `search_triggers.json`：189 次重复 SELL 搜索回合，41 次离线重排，148 次因无 gain、228 次因库存不足、55 次因订单超过四单而跳过，0 错误。23 负局仅 9 次离线重排（平均 0.39/场），四个最大负局都为 0；35 胜局 32 次离线重排（平均 0.91/场）。这些数字表示在已记录线上观测上运行代码得到的离线重排次数，不是线上 action 接受日志，也不是替换对手的反事实强度证据。

## 为什么分数低

v3 修补的是一个狭窄的重复 SELL 顺序盲点，不能改变生产量、开局资金、雇工数量、动物组成、播种/浇水节奏或大多数市场数量决策。即使本地 paired evaluator 的 72 行（六个对手族、双 seat、9064–9069）中动作确实发生 62/72 次，实际胜负仍完全不变：48/72 `W>W`、24/72 `L>L`，point delta 0；现金平均仅 +5.33（bootstrap 95% 2.94..7.61），属于边际收益。线上大败局的差距在 day16–29 逐渐累计，而 v3 search 在这些局基本不触发，不能补生产和竞争性订单量上的差距。

58 场回放的终局状态字段也已核验：全部 720 steps，双方顶层 `statuses` 均为 `DONE`，CHEN Xiang 最后状态均为 `DONE`。每场观测都有 `remainingOverageTime`，但 58 场从头到尾都为 `60.0`（最小、最大和最终值均为 60.0），因此这些 replay 没有记录可用于比较真实 action overage 消耗的变化；不能据此声称线上 timing 没问题。

两次 submission 评分快照的差异，结合六场有限 fidelity 检查和离线 search 触发覆盖，最符合“父 Q25 本身对当时线上对手池已经落后 + 狭窄排序微调没有覆盖主要差距”的工作假设，而不是已经证明的 artifact/loader 故障排除结论。下一步应针对资金和产出路径做经完整反应对手验证的机制改进，不能继续把 SELL 重排局部收益当成强度提升。
4ba0937507b352ec5c9b41b2ad8e4bc766873e0feb5703524bc6cd626d8f7395  q25_search_20260917_055120UTC/candidate_v45_q25_sellsearch_v3.tar.gz
e262fe4f218effbd4bce1f0089f20e86f769b8b181e0c46ba51b0e21ff8c93d9  q25_search_20260917_055120UTC/package_sellsearch_v3/main.py
