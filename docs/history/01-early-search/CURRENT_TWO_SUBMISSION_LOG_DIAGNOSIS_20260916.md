# 当前两份 submission 日志诊断（2026-09-16）

本次检查只读 Kaggle API、replay 和调用日志，没有修改模型，也没有提交新版本。API 使用 `/root/miniconda3/envs/kaggle-cli/bin/python`。当前队列确认如下：

| submission | 文件 | publicScore（刷新时） | 可见对局 |
|---|---|---:|---:|
| 56260878 | `v43_optimized_final.tar.gz` | 2272.8 | 101 public + 1 validation |
| 56257428 | `nathan_cautious_final.tar.gz` | 2644.5 | 127 public + 1 validation |

两份 submission 的分数不能直接当 paired 实验：提交时间、对手池、座位和匹配阶段不同。它们仍然可以用来定位失败发生在哪个阶段，以及检查是否存在运行器故障。

## 先看事实：不是崩溃或超时

两份 submission 的 episodes 都是 `COMPLETED`，每局 720 steps、两席完成。当前下载到的失败 callback 记录中，V43 有 14 场败局、10,066 次 callback，Nathan 有 7 场败局、5,033 次 callback；stderr 均为空，最大耗时分别约 0.527 秒和 0.724 秒，整体 p99 约 0.011 秒，不能解释资金落后。没有 timeout、异常回退或环境不兼容证据。个别 Nathan episode 的日志文件为空或缺失，因此 Nathan 的耗时统计只覆盖实际下载到的记录。

Nathan 的 replay 也全部完成；其当前新 call-log 下载尚未在本快照中完成，因此 Nathan 的运行时间结论只采用 replay 状态和历史日志，不把未下载部分写成已测事实。

## 代码审计解释了为什么“十轮修改”没有带来收益

逐行比较实际上传的 V43 源码与 Ahmed parent 后，前 3366 行完全相同；真正改变 gameplay 的只有末尾约 102 行 `TERM16` wrapper：

1. step 717 仅当一个空手、空闲、恰在 shed 相邻位置的单位发现可收集肥料时，改成 `COLLECT_FERTILIZER`；
2. step 718 通过状态合同后把该单位 `DROP`，并在市场订单未满时追加 `SELL FERTILIZER`。

这不是普遍的生产、动物组合、浇水、种植或销售策略。此前十轮中多数实验没有合入最终 gameplay；因此它不可能覆盖 432–648 步已经形成的中期经济差。

此外，V43 的 loader 末尾已正确重新插入 `agent`，所以本次低分不能归因于最终 wrapper 被绕过。相反，Nathan 上传包的真实 loader 仍选中了 `_NC_PARENT`，五轮 cautious wrapper 被绕过；这解释了为什么 Nathan 线上实际行为等于 raw Nathan，而不是报告中描述的包装行为。

## V43：失败的时间位置和机制

刷新到的全量 metadata 为 101 public 局：85 胜、14 负、2 平，平均资金差约 +19,188；这个均值受大量大胜局影响，不能掩盖 14 个尾部失败。最差局如下：

| episode | 对手 | 最终资金差（我方−对手） | 观察到的变化 |
|---:|---|---:|---|
| 109430701 | Sadettin Şamil Verdil | −7,801 | t288 已到 −1,599；t576 曾反超 +5,006，t696 又降至 −5,170，终局 −7,801 |
| 109438141 | LH-and-FPGA | −4,466 | t576 约 −4,324，t708 约 −7,955 |
| 109477519 | FunLegendGaming | −2,221 | 与镜像策略动作高度接近，差距在市场兑现阶段扩大 |
| 109399843 | Junliang Ye | −1,962 | 中后期差距，非启动故障 |
| 109482442 | FunLegendGaming | −1,593 | 与上一局同类的订单/数量敏感性 |
| 109519380 | WeAreFarmers | −1,349 | 终局肥料补收确实触发，但只能改善约数百币 |

最差两局的 own replay 显示，V43 大量发出数量为 1000 的 SELL 请求；例如 109430701 约 459 个 SELL 请求、请求总量约 86,046，而对手约 302 个、约 1,965；109438141 我方约 118,385，对手约 1,608。请求量不是成交量，市场按订单槽位和双方对应位置处理，超大请求会让不同对手的库存和订单排列产生不同兑现结果。终局 672–718 的 1000 SELL 列表没有把已经形成的 t576/t648 差距修回来。

在 109519380，终局 wrapper 的确改变了 t717/t718，并将差距从约 −1,689（t696）改善到约 −1,349；这证明 wrapper 能在特定触发条件下带来小额收益，也证明它不是 109430701、109438141 等主失败的原因，因为这些局 step 717 没有插入 wrapper 的 `COLLECT_FERTILIZER`。其作用范围太窄，无法解释 publicScore 的下降。

## Nathan：同一类中期市场问题，且线上不是 cautious wrapper

Nathan 的 127 public 局为 74 胜、7 平、46 负，平均资金差约 +3,745；尾部明显比 V43 厚。代表性败局：

* episode 109437616（kobayasi）最终 −6,564：t288 仍约 +726，t432 变 −786，t576 −5,285，t672 −6,823。差异来自中期产出和 SELL/BUY 数量、顺序；终局 1000 SELL 没有恢复。
* 109392182（forever young）−5,600；
* 109372791（QQ Farming）−3,445；
* 109518675（Inzilbêth）−2,971：t432 仅 −163，到 t576 −1,849，之后基本平行；
* 109502811 −2,665、109516516 −2,296、109396329 −1,857，均是 t432–648 逐步扩大，而不是最后两步突然失败。

因此两份 submission 的共同根因是：主体规划在中后期生成的产物、库存和市场订单前缀，对对手的同回合订单排列非常敏感；请求数量和实际成交数量不相等，单纯在末尾清库存或追加肥料无法修复。Nathan 还存在一个独立的部署问题：线上 loader 选 raw parent，包装层的清零订单逻辑没有生效；但 replay 失败模式即使在 raw parent 上也仍是中期市场差，因此不能把所有低分归给 loader。

## 对“为什么十轮没有改善”的结论

1. **优化覆盖面与失败时间尺度错位。** 失败主要在 t432–648 形成，最终提交只改 t717/718。
2. **验证没有覆盖真实入口。** Nathan 的包装层被 loader 绕过；若只调用 `module.agent`，本地结果不能代表上传包。
3. **市场合同不完整。** 只看自己当前 shed、删除零订单或追加订单，忽略了同回合 DROP/HARVEST/BUY、订单槽位和双方配对，会改变成交结果。
4. **benchmark 过于松弛且对手池漂移。** 早期对弱公开 agent 的大胜掩盖了晚期近镜像对手的中期现金分叉；publicScore 还受匹配时间和对手强度影响。
5. **没有证据支持运行时假设。** 所有当前败局均正常完成，日志没有错误或超时。

下一步若要改模型，应先冻结 source/archive/loader 三者一致性；用同一 seed、双 seat、近镜像与不同生产族对手做 paired replay；按 t288/t432/t576/t648/t672/终局记录现金、库存、实际成交量和订单槽位。任何销售或库存改动必须在真实 engine 中验证 prefix 不变、容量不溢出、成交量可解释，并以未见 seed 的下尾而非单一均值作为保留标准。当前证据不足以支持再提交任何候选。

证据文件：

* [`episodes_all.json`](current_submission_diagnosis_20260916/episodes_all.json)
* [`replay_action_summary.json`](current_submission_diagnosis_20260916/replay_action_summary.json)
* [`actual_changes_audit.md`](current_submission_diagnosis_20260916/actual_changes_audit.md)
* [`logs/`](current_submission_diagnosis_20260916/logs/)
