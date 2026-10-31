# Kaggriculture 后续研究准则

更新时间：2026-09-14 UTC  
适用范围：从 v37/cap2 之后的所有本地实验、候选整理、线上日志分析和提交决策。

这份文档是恢复研究时的入口准则。它记录已经验证的事实、尚未解决的问题和必须遵守的工作流程。当前研究目标已暂停；只读日志监控可以继续运行，但不会因为监控结果自动创建候选、训练或提交。

## 目标与当前基线

目标是稳定进入前 200，优先降低跨对手、跨 seed 和跨 seat 的尾部风险。单卡 RTX 4090 的资源约束意味着训练要保持低维、可复现、可解释，不能用激进的完整 RL 追逐少量 public 分数。

研究基线和线上历史对照分开保存：

- `h5sim96/v37`：后续研究的唯一主要父策略，用于代码分支、机制实验和 action-level 对照。
- `h5sim96_cap2`：线上历史对照，submission `56209639`，只将 V231 cattle substitution 上限改为 2。由于线上表现已被判断为不理想，它不再作为新实验的默认父策略或晋级目标；保留它是为了比较线上 rating、回放和回滚风险。

`cap3`、`qty1`、strict similarity、简单 MILK 提前销售、全局 overflow guard、quote floor、route splice、直接复制高手 action tape 等方向均不能视为已证实改进。MILKLEAD 在公开面板上约有个位数收益，但在 Thomas 面板出现负边际，且其门控位于父层重排之后，可能改变 SELL slot 和 debt 语义；它只能留在研究档案，不得晋级或提交。

线上 public score 是带噪声的相对 rating，不是固定测试集的绝对分数。必须把策略实力、对手池变化、seed/seat 分布和 rating 更新分开估计，不能用一次分数变化证明模型升降。

## 不可违反的约束

1. **未经用户明确授权不提交。** 本地通过门槛只意味着“待授权”，不意味着可以上传。任何脚本、定时任务和监控都不得调用 submit。
2. **先本地验证，再考虑线上。** 每个候选必须经过配对 seed、双 seat、多个对手和异常检查；固定 tape 只能做机制诊断，不能替代交互式对局。
3. **不把少数败局改成全局规则。** 一个 loss 只有在多个 seed、对手和 seat 中复现出同一机制，才有资格形成实验假设。
4. **不以平均分掩盖尾部退化。** 最小 margin、负局数、5% 分位 margin、seat 方差和强对手结果与均值同等重要。
5. **每次实验只改一个可识别变量。** 代码、阈值、父层条件和 route planner 的 step 条件不能在同一实验中同时变化。
6. **任何新 gate 都必须有 kill switch、telemetry 和父动作回退。** 状态字段缺失、账本不一致或配置异常时立即执行父策略动作。
7. **尊重比赛规则与公开信息边界。** 只使用 observation 中可见的状态和公开 replay；禁止读取对手 private、未来 action、未来随机数或线上未公开数据。

## 先确认环境和可复现性

在运行新实验前，必须确认：

- Kaggriculture skill 和项目 `AGENTS.md` 已阅读，使用规定的本地 engine 和打包方式；
- 每个 agent 在独立进程/独立模块状态中运行，全局缓存、随机数和 debt ledger 在每局开始时清空；
- `replay["info"]["seed"]` 是实际随机种子；不能使用经常为 `None` 的 `replay["configuration"]["seed"]`；
- observation 的 `step=t` 对应 replay `steps[t+1]["action"]`；固定对手 tape 错一回合会使所有反事实结论失效；
- 同一 replay 重跑能逐步复现 observation、action、库存、现金和终局 reward；
- 本地 engine 与线上日志在 golden replay 上的终局和关键中间状态一致；
- 每局均完成 720 steps、状态为 `DONE`、无 stderr，且 callback 延迟没有接近比赛限制；
- tar 包解压后可以在无当前工作目录依赖的情况下独立加载，源码和产物有 hash 记录。
- 锁定 Python、`kaggle-environments`、engine hash 和依赖版本；记录 CPU/内存、action latency 分位数和超时率。
- 先运行 `py_compile` 和短 smoke，再运行完整面板；4090 的训练时间、显存和运行时预算预先写入实验记录，超预算即停止。

若复现性检查失败，先修复工具链；在 engine 不可信时不得解释模型优劣。

## 日志数据规范

监控脚本保持单实例运行，启动或重启前先检查 `pgrep`、`monitor.pid` 和 heartbeat，防止重复下载。active 队列按比赛规则只维护当前有效的两个 submission；最旧提交被替换时，在 manifest 中记录替换关系、文件 hash 和时间。

每个 episode 统一保存以下字段：

- submission、episode、seed、对手标识/策略族、我方 seat、时间段；
- opening shop fingerprint、完整 shop 序列和关键商品出现回合；
- step 0/12/144/216/288/360/480/623/648/695 的 money、shed room、carried、库存、工人、动物、weed、订单槽和已解锁土地；
- 每种商品的首次生产、首次 SELL、成交量、成交价轨迹、最后销售回合；
- BUY_SEED、BUY_ANIMAL、BUY_LAND、HIRE、PICKUP、PLACE 的回合和现金断点；
- 原始父策略 action、候选 action、最终送入 engine 的 action，以及 action-level delta；
- `shed` 与 carried 的容量、step 623/695 的丢弃量、终局剩余库存；
- 最终双方 reward、margin、win/tie/loss、DONE/stderr、最大 action latency。

败局自动先分为四类，再允许细分：

1. 生产/收获价值不足；
2. shared market 成交时点、价格轨迹或 SELL slot 顺序；
3. carried/shed 容量和 shed 丢弃；
4. 投资、融资、土地、雇工、weed 或终局清仓路线。

分类必须由中间状态和反事实支持。特别是 `shed=100` 不等于“应该停止 harvest”；要同时看 carried、未来 SELL 义务、价格下滑和后续产出机会。

监控的工程约束如下：

- 只读调用 API，持久化 watched IDs、source、last successful scan、PID/heartbeat 和连续失败次数；绝不触发提交。
- 只对已完成且 rewards/status 完整的 episode 分类；pending、validation、空 rewards 或 transient unknown 留到下一轮重试，不能永久写成未知结果。
- episode 主键使用 `submission_id + episode_id`，原子写入 state，去重并校验缓存；同时保存胜局、平局和败局 replay，以及双方日志、stderr 和 latency。
- `team-submissions` 失败时可用 `COMPLETE` 仅采集数据，但报告必须标注 fallback；fallback 期间不更新实力判断，恢复后核对队列变更。
- 设置超过两个扫描周期的 stale watchdog、磁盘配额、API 限速/重试和缺日志告警；校验 team 名称和 agent index。

## 数据泄漏和评估污染防线

策略在回合 `t` 只能使用当时 observation 中可见的状态。禁止读取对手 private、未来 observation、replay 后续 action、终局 reward、未来随机数或按 seed/episode ID 硬编码分支。固定 opponent tape 只在离线反事实脚本中使用，不能进入 agent 的在线决策。

数据集分为三层：

1. **screening 集**：用于快速筛选和调试；
2. **confirmation 集**：未参与阈值调参，用于确认机制；
3. **最终 holdout 集**：按 seed、opening、对手族、seat 和时间切割，并对线上反馈设置 embargo。

参与过调参的 seed、opening 或线上 episode 永远不能回流最终 holdout。公开高分代码、replay 和 rating 只能产生机制假设，不能当作测试标签或真实强度。每个实验预先登记假设、唯一干预、反事实变量、最大运行预算和证伪条件；达到证伪条件后停止，不在同一 replay 上反复调参。

## 实验设计：先做可证伪的因果对照

每个候选都从冻结的 v37/cap2 副本开始，并使用 common random numbers：同一 seed、同一对手、同一 seat 运行 parent 和 candidate，再交换 seat。候选和 parent 必须在新加载模块中分别运行，避免状态泄漏。

对每项改动至少保留以下对照：

- parent 原策略；
- candidate 单变量改动；
- no-op 或零触发版本，确认代码路径不会改变 action；
- parent-layer ablation，必要时分别关闭 R36 reserve、R37 reorder、V231 等父层，以确认交互归因；
- 固定 opponent tape 的 action-level 反事实；
- 自适应交互式对手面板。

报告不能只给终局 margin，必须分解为价格、成交量、产量、容量丢失、订单槽位置、资产投资和现金变化。对 SELL gate 尤其要记录原 action、父层最终 action、gate action 三份结果，MILK/WOOL/STRAWBERRY 的实际成交量，原有 debt/reservation 数量和同回合 SELL 的相对顺序。

MILK 或其它销售 gate 若继续研究，必须满足下列结构条件：

- 不在父层最终重排后盲目 append 新 SELL；应在重排前插入，或精确替换原商品 slot；
- 与 R36 reserve/debt ledger 同步，避免下一回合重复抑制或重复售卖；
- 对 lead、hold、no-price 三路做对照；
- 当前 shed 中确有库存，提前销售会在原计划回合扣减同一数量；
- 固定 loss tape 的现金不得下降，交互式强对手不能出现系统性负 margin。

## 验证面板和统计门槛

验证集合必须按 seed、opening、对手族和 seat 隔离，不能随机切分相邻 episode。最低面板包括：

- 至少 15 个未见 seed，全部双 seat；
- Flex、Thomas、Dmitrii 等强公开方案，每类至少 10 个 seed、双 seat；
- 已收集的真实 loss tape 至少 12 场，覆盖轻微落后、几千分落后和极端落后；
- 未见 opening/shop 序列和不同时间段线上 replay。

每次报告至少包含 paired mean/median margin、win/tie/loss、最小 margin、5% 分位、95% bootstrap 区间、Wilson/Beta 胜率区间、seat 差异、对手分层结果和异常数。候选不得依靠一个 seed、一个 seat 或单一对手贡献全部收益。

固定 tape 的收益只能证明某个机制在给定状态下的方向；只有自适应对手面板也改善，才可视为策略层证据。固定 tape 与交互式结果方向相反时，候选淘汰或回到结构审计。

## 策略重建方向

如果要突破 v37，优先重建完整策略族，而不是继续堆叠局部门控。每个专家从 opening、资产投资、生产、库存、销售到终局清仓保持内部一致，建议至少包含：

- 保守现金流/低库存风险专家；
- 前期投资、后期兑现专家；
- 高价市场窗口交易专家；
- 高生产/高库存压力下的反制专家；
- 不利 opening 或座位下的防守专家。

只在 step 144/216/288 等阶段边界依据公开状态选择专家，设置滞回避免频繁切换。专家必须声明状态契约：现金下限、库存区间、工人/动物数量、订单槽占用、未来 PICKUP/BUY barrier 和 debt ledger。若状态不满足契约，回退到 v37/cap2，不拼接互相不兼容的单回合 action。

建立统一的可见状态账本，至少包含实际 shed、每个 worker carried、未来已承诺 SELL、未来 PICKUP/BUY barrier、订单槽余量、容量余量和父层 debt。所有 gate 只在账本上做局部且可撤销的修改，并输出 telemetry。

## RL 的安全使用范围

当前数据规模和 private shake 风险不支持完整 PPO/DQN 或直接 self-play policy。RL 只允许用于：

- 从高分 replay 做 behavior cloning 的阶段级 route/profile 选择；
- 用精确本地 engine 做短 horizon value refinement；
- 对二元或少量离散决策进行离线 value ranking，例如“提前/保持一批 MILK”或“抑制一次特定 harvest”。

训练必须使用真实 replay 加引擎反事实，按 seed/opening 留出 holdout，加入价格、对手策略和 seat 扰动。状态覆盖不足、Q 值差距过小或账本不一致时强制回退 incumbent。目标函数同时惩罚负局数、最差 margin、跨 seat 方差和 5% 分位退化，不能只优化平均 reward。

## 社区方案的使用方式

公开 notebook、讨论区和高分提交只提供机制假设，不直接搬运 action tape 或耦合代码。为每个方案建立机制卡片：改变的阶段、依赖的规则、opening 假设、库存/价格假设、是否可能对特定对手池过拟合、可移植部分和规则风险。一次只移植一个机制，做单变量消融，并保留来源、版本和本地验证记录。

## 候选晋级、提交和回滚

提交风险按“不可变 incumbent + 可回滚 candidate”管理。每个版本保存源码 commit/diff、配置、engine 版本、tar SHA256、评估清单和生成时间；incumbent 包只读保存，candidate 包单独归档。active submission limit 为 2，且新提交会替换最旧项，因此提交前后都要记录队列快照和剩余额度。

上传操作必须幂等：网络超时、CLI 无回执或 URL 异常时，先查询 submissions 和 submission ref，确认是否已创建，禁止盲目重试而消耗机会。tar 根目录必须有 `main.py` 和 `agent`，解压后无隐式外部文件、网络调用或未固定随机依赖。异常、早期 rating 或单场结果都不能触发自动回滚或追加提交；先保留旧 incumbent，等足够终局对局后再按分层统计判断。

候选只有同时满足以下条件，才能进入 `ready` manifest：

- 代码通过 `py_compile`，tar 包可复现并有 hash；
- 未见 seed 双 seat 和 Flex/Thomas/Dmitrii 面板达到统计门槛；
- 至少 12 场真实 loss tape 有机制解释，反事实方向与交互式结果一致；
- 720 steps 全部 `DONE`，零 stderr、零 timeout、无容量/订单非法异常；
- 负局数不增加，最小 margin、5% 分位和 seat 方差没有明显恶化；
- 相对 incumbent 的收益不是由单一 opening、seed、seat 或对手造成；
- 具备一键 kill switch 和回退到 v37/cap2 的路径；
- 已生成候选报告、manifest、replay 复现记录和风险说明。

通过后流程固定为“冻结候选 → 写完整报告 → 等用户明确授权”。上传成功后暂停继续改动，先等待足够线上对局，再按对手/seat 分层分析。若线上明显回归，保留 incumbent 并停止自动替换；不通过门槛的版本不得用提交机会试探。

## 停止条件与研究复盘

每个分支在开始前登记最大实验次数、4090 训练/运行预算和提交机会预算。screening、confirmation 和最终 holdout 的边界在实验开始后保持不变。

以下任一条件触发停止该分支：

- 同一假设在两个独立 holdout block 中失败；
- 改动只在固定 tape 有利，在交互式面板没有收益；
- 平均值上升但尾部指标、强对手或 seat 明显恶化；
- 收益机制无法由 action-level 和中间状态解释；
- 连续多个完整策略族都无法稳定超过 v37/cap2；
- 需要不断增加互相覆盖的 guard 才能维持收益，账本无法保持一致。
- 任一完整面板出现运行时、latency、stderr、打包或规则合规回归。
- 同一分支耗尽预注册的实验次数或资源预算，仍未达到实用的 margin 改善。

达到停止条件后冻结线上基线，把资源转向更高质量日志、机制研究或新的策略族设计。每次复盘必须回答：假设、干预变量、证伪结果、适用分布、是否保留，以及下一步是否仍值得消耗计算或提交机会。

当前默认状态：线上 submission `56209639` 继续由只读 monitor 收集数据；本地研究统一从 v37 分支开始；cap2 只用于历史对照和回滚分析；没有新候选获得提交资格，也没有任何待执行的提交授权。

## 恢复研究时的固定顺序

1. 核验 Kaggle skill、项目规则、Python/engine 版本、monitor 单实例和 active 队列；不改变线上提交。
2. 从胜/平/负 replay 建立结构化数据集，完成 seed/opening/opponent/seat/time 分层，并冻结最终 holdout。
3. 选一个可证伪假设，登记唯一干预、父层消融、预算和证伪条件；先做 no-op 与 golden replay sanity。
4. 在 paired seed、双 seat、多个强对手上进行 screening，记录 action-level delta 和中间经济量；不满足方向一致性立即淘汰。
5. 对通过 screening 的版本运行 confirmation 和 adversarial holdout，计算 paired margin、尾部指标和置信区间；候选冻结后才能查看最终 holdout。
6. 只有达到晋级门槛才生成 ready manifest、回滚包和完整报告，并停在“待用户授权提交”。
7. 用户授权后才上传；上传后暂停代码变化，等待足够终局对局，再按对手、seat、seed 和时间分析线上结果。
