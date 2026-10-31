# V37 作为后续研究基底的审计

## 审计结论

V37 应恢复为唯一线上研究基线。cap2 的动物替换改动已经在线上表现不佳，不能作为父策略。V37 的优势来自一条耦合的完整路线（opening tape、day-6 shop-aware route、四回合 reservation、smarter labor、weed repair、V219/V231/V233/V51 物理确认和终局 planner），后续改动必须保留这条闭环，禁止把单个 guard 当作独立收益来源。

公开面板证据显示 V37 在 31 个跨来源 seed、双 seat、720 步对局中，对 Flex 为 61-1、对 Thomas 为 61-1、对 Dmitrii 为 62-0；平均资金差分别约 +2961、+7505、+6120。282 场线上胜局的共同结构是 COW 与 SHEEP 持续存在，约 78% 有 GOOSE，TOMATO 只有少数局进入；step 144/216 的资产状态高度稳定。所有已审计对局均完成 720 步，stderr 为零，callback 通常远低于 1 秒，因此当前瓶颈是共享市场和路线交互，而非运行时性能。

## 已知强项与不可破坏的约束

- 生产闭环：WATER、HARVEST、CARE、FEED、COLLECT_FERTILIZER、受控 SELL 以及最终清仓互相依赖，不能孤立调一个动作。
- 动物结构：胜局几乎都保留 COW/SHEEP，GOOSE 是条件性扩展；不得因为少数 TOMATO 或 WEED 败局而永久关闭主路线。
- 物理安全：hand alignment、weed repair、真实 shed/projected shed、购买/放置确认、sale debt 和终局 liquidation 应继续存在。
- 销售层：V37 的 quote-aware 排序和四回合预留能稳定击败公开路线；销售时序必须和真实库存、未来 SELL suffix、PICKUP/BUY/PLACE/HIRE 义务一起评估。
- 稳定性：镜像 tie 是确定性的共享市场镜像；只重排 SELL 顺序不能把 tie 变成 win，固定 seat 偏置不可作为策略。

## 已证伪或暂时淘汰的方向

以下方向已经出现零增益、seat-dependent 负差或大幅回归，不应再次作为默认基线：

- cap2/cap3/qty1 牛替换、strict similarity 和相近阈值扫描；cap2 线上明显差，cap3 与父策略逐局相同。
- 从开局强制 route 1/2 或迁移 Top-10 完整 tape；route 1 大幅退化，route 2 无稳定优势，Top-10 archive 对 V37 约 -15k。
- reserve144、固定 seat tie-break、quote floor、简单 latesale、surplus timing、全局 room623/695 overflow guard；公开面板漂亮但真实 replay 或反向 seat 负差。
- 单一 standing-yield、SELL 数量、WEED 数量或容量阈值门控；容量和市场机会成本耦合，抑制 HARVEST 会损失后续产出。
- 无条件 TOMATO/SHEEP 投资、weedguard、直接复制对手 action tape、完整 PPO/DQN 或 self-play；均有明显分布外和 private shake 风险。

## 最值得优先重建的完整策略级假设

### A. 市场流量与物理库存联合策略（最高优先级）

保持 V37 生产路线，从 day 12/18 和 day 27--29 建立统一的 market-state profile：以自己的真实 shed、携带库存、未来 route SELL suffix、市场 inventory/price 斜率、下一次回 shed 时间、订单槽和公开对手 standing yield 为状态，联合决定 HARVEST/DROP/PICKUP 与一小批 SELL 的时点。候选动作只能来自已确认存在的库存；每次干预要记录 sale debt，并在原计划回合扣除相同数量。它不是“提前一回合卖某商品”的局部规则，而是一个守住生产闭环的完整销售/运输 profile。

先在真实 loss replay 上做固定 tape 因果实验，再在交互式对手面板验证。接受条件是减少 623/695 实际 overflow 且不牺牲后续高价值产出、双 seat 无负差；若固定 tape 与交互式结果方向相反，立即淘汰。

### B. 阶段级 opening/动物/TOMATO 策略族

保留 V37 主 route 作为默认专家，在 step 144（首两次 shop）和 step 216/288（资产、资金、公开对手农场）只选择一次完整 profile：标准 COW/SHEEP 现金流、保守 GOOSE 扩展、条件 TOMATO 投资或高 SELL 压力防守。切换必须满足现金、shed room、shop 资格、可完成收获和购买/运输义务；状态不满足时回退 V37。不要强行使用现有 route id 1/2，它们是不同 tape 的整体行为且已被证伪。先用 replay 聚类和 behavior cloning 学 profile，再做短 horizon engine value refinement。

### C. 日末容量-劳动联合规划

针对 623/695 的 carried+ shed 超过 100，重建一个阶段级 labor reservation：在 day 24/27 提前预留一名单位执行回仓/销售，按商品价值和下一个生产窗口决定哪些 HARVEST/COLLECT_FERTILIZER 延后，必要时减少低价商品而保留 MILK/WOOL/STRAWBERRY 等高价值产出。规划必须模拟完整 72-step block（含 hire、feed、pickup、drop、market queue），而不是看到容量高就全局禁 harvest；所有改变都要通过零 overflow、非负后续 deposit 和库存机会成本证书。

## 实验前必须核验的文件与面板

1. 基线文件：[public_v37_pkg/main.py](public_v37_pkg/main.py) 及 [public_v37_candidate.tar.gz](public_v37_candidate.tar.gz)；重新计算源文件和 archive SHA-256，确认 archive 根目录只有 `main.py`。
2. 引擎可复现性：[experiments/h5_engine_audit/ENGINE_PARITY_REPORT.md](experiments/h5_engine_audit/ENGINE_PARITY_REPORT.md)、`installed_parity.json`、`h5_engine_version_audit.json`；确认实际 Kaggriculture 模块 SHA 和 `env.info['seed']`，不要以 framework 版本号替代机制核验。
3. 面板脚本和结果：[V37_PANEL_RESULTS.md](V37_PANEL_RESULTS.md)、[LOCAL_EVAL_PLAN.md](LOCAL_EVAL_PLAN.md)、`experiments/*results.json`；所有新结果必须绑定候选 SHA、对手 SHA、seed、seat、720 步 DONE、status、stderr 和 latency。
4. 败局/胜局数据：[LATEST_V37_LOSS_TIE_SUMMARY.md](LATEST_V37_LOSS_TIE_SUMMARY.md)、[WIN_STRENGTH_REPORT.md](WIN_STRENGTH_REPORT.md)、`local_evals/v37_context_dataset.jsonl`、`local_evals/shadow_profile_table.json`；确认 context 只含当前及历史公开 observation，不含对手 private 或未来 action。
5. 真实日志：`agent_monitor/logs/` 和 replay 缓存；按 submission、对手、seed、seat、opening、结果分层，区分 rating/opponent-pool 漂移和策略退化。

在上述核验完成前，不启动大规模训练、不创建提交包、不提交 Kaggle。恢复研究时先做 A/B/C 各一个最小可证伪实验，再决定是否值得建立完整策略族；任何晋级候选都必须回到用户批准流程。
