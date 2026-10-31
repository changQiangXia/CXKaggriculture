# 基于线上 log 的修改：泛化性研究第 2 轮（落地审计）

本轮把第 1 轮设计应用到当前日志和候选历史结果，形成可执行的筛选协议。

## 当前日志能支持什么

`agent_monitor/state.json` 中两份近期提交的非 validation episode 为：

| submission | episodes | 时间范围（UTC） | win/loss/tie |
|---|---:|---|---|
| no-R128 `56238321` | 125 | 2026-09-14 20:11 – 2026-09-15 07:40 | 69/38/18 |
| v42_pkg `56234455` | 128 | 2026-09-14 15:50 – 2026-09-15 07:27 | 117/10/1 |

按时间三等分后，no-R128 的 loss 数为 `4/14/20`，v42_pkg 为 `2/1/7`。这说明线上窗口和对手池在变化，不能把末段 loss 直接当成稳定标签。已有缓存的 loss/tie replay 都完成 720 steps 且无 stderr，但 replay 是对某个对手和市场随机流的条件样本，不是独立测试集。

## 两类修改的实际泛化风险

1. **SELL 顺序/slot 调整**：历史 `slot_rank` 在当前 parent 上确实触发，但 paired 终局几乎为零差；这说明“观察到 SELL 交错”并不等于顺序重排有经济价值。它可以作为 parent-equivalence 和 no-op 安全基线，不能宣称泛化收益。
2. **premium front-run / terminal 补单**：此前 activation 为零，候选与 parent 相同。零 delta 不能证明机制无效，只能证明旧接口或当前 route 没有覆盖该状态。必须先做 activation profiling，再跑评价面板。

## 当前可执行的两阶段面板

**阶段 A：机制验证（不看最终 holdout）**

- discovery：已有 loss/tie replay，抽取状态模式；
- development：公开强对手的多 seed 双 seat；
- 每个候选做 8 局 smoke，要求真实触发且 parent/candidate action delta 可审计；
- 触发率低于预注册下限（建议所有候选合计至少 5 个独立 seed、两个策略族触发）时停止扩面板，先修状态接口；
- 固定 replay 只用于 24/72/144-step 反事实，不计入胜率。

**阶段 B：泛化确认**

- 至少 6–8 个公开对手，按 tape/router/runtime 分族；
- 每个对手至少 8 个未见 seed、双 seat；
- 至少一个未参与机制发现的公开对手族；
- 另留 5 个 seed × 双 seat 的最终 holdout，规则冻结后才运行；
- 对历史线上 loss 的行为只做压力测试，不把原 episode 当训练标签。

每一局记录 action-level delta、trigger/reject reason、price、成交量、现金、shed/carried、pickup、capacity、debt、terminal inventory、latency、DONE/stderr。候选与 parent 必须在独立 fresh process 中运行。

## 通过门槛和证伪条件

建议预注册：

- 所有局 `DONE/720`，stderr、timeout、非法 action 均为 0；
- 至少 3 个对手族的 paired mean delta 不为负，且不能由单一 seed/seat 贡献；
- 95% bootstrap 下界不显示系统性退化；
- 5% quantile、CVaR、min delta 和 negative-game count 不恶化；
- 两个 seat 的方向一致，seat 差异不超过预设容忍值；
- 触发局收益必须能由中间状态解释，未触发局 action 与 parent 完全一致；
- 任意一个独立 holdout block 出现系统性负尾，立即冻结并淘汰该规则，不继续调阈值。

## 防止反馈污染

线上新 log 不得在同一轮同时做发现、调参和确认。建议采用时间 embargo：抓取日之后的新 episode 至少等一个完整评估周期才进入 discovery；一旦用于调参，就从 final holdout 永久移除。提交后的 public score 只能更新“外部结果”栏，不能回写本地规则阈值。

## 最终决策

在当前证据下，log-derived 修改暂时只能产生研究候选，不能直接变成线上提交：`slot_rank` 已证明安全但没有稳定收益，premium/terminal 尚未证明真实触发。下一步应先刷新当前 V42 route 的状态账本和 activation telemetry，再按本协议跑跨策略族、未见 seed、双 seat 的交互式确认。只有通过确认和最终 holdout，才可说修改具有泛化性；即使通过，也只生成待用户授权的本地 archive。
