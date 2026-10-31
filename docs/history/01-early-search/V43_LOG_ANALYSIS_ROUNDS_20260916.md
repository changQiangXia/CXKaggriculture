# V43 优化前日志分析：两轮，2026-09-16

生成时间：2026-09-15T18:21:02.821018+00:00。本轮仅对 Kaggle 作只读调用；未提交、未修改现有模型。API 使用 `/root/miniconda3/envs/kaggle-cli/bin/python` 对应环境。本地回放用 `/root/miniconda3/bin/python`。

## 第一轮：恢复事实、检查运行、重建样本边界

### 1. 必须纠正上一轮“线上失败”结论

最初接口显示的 Nathan 600.0、inspired 683.1 并不是冻结的最终表现。此次第一次查询 Nathan 为 2646.0，紧随其后的持久化快照为 **2638.5**；inspired 为 **2172.4**。多了一场负 1 币对局时 rating 就已再次变化，说明 COMPLETE 不能解释成“评分从此不再变”。因此此前以 600/683 断言压缩包不兼容、环境崩溃、线上已经证伪 parent safety，证据不成立，应撤回。

保存的 submissions 快照还包含 highscore-terminal 2634.2、no-R128 2687.9。不同提交对手池、对局数、时间不同；这些 rating 和原始胜率不能直接当 paired trial 比较。

### 2. 全量可见对局

从此次 episodes API 下载全部可见对局：Nathan 50（49 competitive + 1 self-validation），inspired 62（61 competitive + 1 self-validation），总计 112 replay。两场 self-validation 从胜负统计剔除。110 场 competitive 全部 720 states、两席 DONE、module_version 1.32.7。

| submission | competitive | 胜/负/平 | 平均资金差 | 中位资金差 | 最差资金差 | 5%下尾均值 |
|---|---:|---|---:|---:|---:|---:|
| Nathan cautious 56257428 | 49 | 38/11/0 | 10114.1 | 1766.0 | -3445 | -2262.3 |
| inspired premium 56256349 | 61 | 55/6/0 | 17582.4 | 8927.0 | -8026 | -4496.0 |

**此表不能证明 inspired 比 Nathan 强**。它们不是同 seed/seat/opponent 配对，线上匹配会随 rating 变化。单场 reward 是现金；publicScore 是对局评分，量纲也不同。

### 3. 时间分块暴露 benchmark 漂移

按每个提交对局时间均分为早、中、晚三块，Nathan：

| 块 | 局数 | 胜/负 | 平均资金差 | 前144动作与对手平均相同数 |
|---|---:|---|---:|---:|
| 早 | 16 | 16/0 | 28229.4 | 58.25/144 |
| 中 | 16 | 14/2 | 1694.2 | 141.06/144 |
| 晚 | 17 | 8/9 | 988.9 | 141.76/144 |

早期 16 连胜随后变为晚期 8 胜 9 负；晚期对手前 144 动作约 98% 一致，早期仅约 40%。这与进入更接近的策略族相符，但不能只凭该表断言匹配算法。检验新 V43 时必须含当代 V43/Nathan、近镜像对手、不同生产族和双席，不能仅对旧弱公开 agent。

### 4. 运行日志与终局库存

全部 17 场败局下载了 own-seat call logs，共 **12,223 次调用**。stderr/stdout 均空，最大单次耗时 **0.536724 秒**；各局 p99 介于 0.006370–0.014719 秒，没有超时证据。110 场自身季末 shed + actors carry 全为空；单纯“忘记季末卖出库存”不是这批失败的共性。这里不把动物设施当现金库存，不把满仓步数直接当丢弃量。

## 第二轮：动作入口审计、失败机制与泛化约束

### 1. 已证实：文件加载绕过最终 wrapper

本地 `kaggle_environments/agent.py:39–58` 的 `get_last_callable` 执行 Python 文件后取 namespace 中最后一个 callable。Python 重复赋值 `agent` 不改变 dict 的插入次序；父函数别名若在它后面新建，就可能成为真正入口。

- Nathan cautious：真正最后 callable 为 **`_NC_PARENT`**，不是最终的 `agent`；新增清理/telemetry wrapper 被绕过。
- inspired：真正最后 callable 为 **`_INS2_PARENT`**，不是最终 `agent`；repayment wrapper 被绕过。
- 两个 tar 的 main.py SHA 均与工作目录文件一致，不是打包陈旧文件：Nathan `07717b2aa316ebf78f7248daa9de6ba6ab6f73621dbe3d391a494c9cb8cbc89e`，inspired `91d5a7147ab648e2d86b91425c8d7c0d6e4a704ad73433dad58577577b2c2079`。

取 6 条线上 observation sequence，每条运行 719 callback，分别调用 named `agent` 和文件 loader 所选函数，共 12 次完整动作回放：

| submission/episode | seat | named agent 与线上不同行数 | file loader 与线上不同行数 |
|---|---:|---:|---:|
| 56257428/109372791 | 1 | 4 | 1 |
| 56257428/109348403 | 0 | 1 | 0 |
| 56257428/109372756 | 0 | 3 | 0 |
| 56256349/109355094 | 0 | 0 | 0 |
| 56256349/109326171 | 0 | 0 | 0 |
| 56256349/109373000 | 1 | 0 | 0 |

Nathan 的 seat0 replay 中，线上保留空 order 或 `BUY_PRODUCT WHEAT 0`，正好对应 wrapper 被绕过；file loader 719/719 匹配。Nathan seat1 episode 109372791 仍有一处差异：action step 527 最后追加的 SELL WHEAT 本地 4、线上 2，且本地回放 overflow contract_errors=1。这是需要进一步查明的局部 shadow/重建差异，不能宣称已完成全环境 parity。

inspired 三局中 premium trigger=0，named 与 file loader 都完全匹配。所以 repayment 没有被实际执行是部署风险；这批回放没有证明它造成当前现金损失。不能把风险直接写成已发生因果。

**下个候选的硬门槛**：文件末尾显式重新插入最终 agent，例如 `agent = globals().pop('agent')`；确保其后没有新 callable。打包解压后用真实文件路径加载，断言 loader 所选函数就是最终 agent；同时保留 named callable 测试作交叉验证。

回放格式也有陷阱：seat1 的 replay observation 不含共享 `step`，需继承 seat0 shared observation 再覆盖 own-seat 字段。最初审计脚本未继承 step，产生虚假的全 PASS 差异；本报告只采用修正重建后结果。

### 2. Nathan 对作者本人：相似生产路径、市场现金兑现不同

Episode **109369661**，seed **1604391597**，我方 seat1，对手 Nathan Jacob；最终 **80219 vs 81766，-1547**。

- 两边开局相同，前 144 动作 143 相同；动物采购申请同为 6 COW、17 SHEEP。
- farmer + hands 命令从 action step0–601 一致；单位行为差异集中于602–620。
- 第一处现金差在403：我方使用 `SELL STRAWBERRY 1000 / SELL WHEAT 1000 / SELL FERTILIZER 1000`，对方只 `SELL STRAWBERRY 12`，我方暂时多104。
- 404对方出售3 fertilizer后差距缩到+2，409后我方变成-26；576时-314、648时-583、672时-1406、季末-1547。
- 我方整个 episode 540条 SELL，对方340条。很多额外订单在 shed 没货时不成交；申报大数量不是实际销量。

这使“在已知同生产范式下优化销售时序/资源保留/订单位置”成为可检验假设。它**不证明**删掉所有多余SELL就会增加1547，也不证明 cow 数不足；简单改 cow 无法解释前602步单位动作一致的事实。应先实现完整市场前缀账本，再比较触发后的实际现金与库存保持合同。

### 3. Nathan 最大败局：生产组合与后期路径

Episode **109372791**，seed **1333321922**，seat1，对 QQ Farming，**60495 vs 63940，-3445**。前144动作142相同。双方动物采购申请分别 8 COW/6 SHEEP/3 GOOSE 与6 COW/6 SHEEP/5 GOOSE。576资金差-1343、648差-1928、672差-3203。这里存在动物组合与路径差异；单条录像不足以证明“牛换鹅”规则。必须以 shop mix、feed、service route、持续产出和终局可回收为状态条件，并做跨 seed/对手族消融。

### 4. inspired 最大败局：从第575步以后落后

Episode **109355094**，seed **1393838439**，seat0，对 extra eclaire，**88530 vs 96556，-8026**。前575个 action 完全相同，第一差异在575；576现金差-244、648差-848、672差-4672、季末-8026。双方动物采购申请相同6 COW/10 SHEEP，季末均无 shed/carry 残留。这指向末周 production/service/sale 路线，而非开局或忘清仓。不能对这条 tape 直接学固定 step；应研究24/72/144步状态证书。

另一败局 **109355104** 对 parv goyal2，-7701，开局就不同，288时我方+7927、576时-6310；这反映中后期持续经济可反转前期领先，不能以短回合现金作为唯一筛选目标。

### 5. 优化顺序和验收门槛

1. 固定 V43 源码、archive 和 loader identity，修复真实入口，再开始收益实验。
2. 以公开 V43/Nathan + no-R128 + 不同生产族组成双席 paired panel；记录各自文件SHA、engine版本、未见seeds。
3. market guard 必须模拟 actor actions、pickup/drop、订单前缀、容量和真实可成交数量；不要只读当前 shed 然后删除订单，因为同turn DROP/harvest/BUY可补货。
4. 优先测试可以解释近镜像后期差距的销售/资源保留合同；每次只改变有限动作。保存 activation/rejection/fallback、delta分布、最差局、5%下尾和seat差异。
5. 日志 seeds 归 discovery。最终 confirmation 使用预先冻结的未见 seeds；对手 tape 仅作固定反应基线，其不能反应改动的局限必须明示。
6. 用源码 named agent、真实文件 loader、解压archive三条路径验证动作和最终reward；只通过其中一条不足以代表上传模型。
7. rating 用带时间的快照，提交后的初始600分不能写成最终失败；至少结合 COMPLETE validation 和新增competitive episodes判断。

## 数据与可复现材料

- `v43_logs_20260916/submissions.json`：本次持久化score快照。
- `episodes_56257428.json`、`episodes_56256349.json`：完整可见episode列表。
- `replay_index.json`：112条replay索引，raw文件在`replays/`。
- `analysis.json`：110 competitive逐局profile、分块、座位和下尾统计。
- `call_logs/`、`call_logs_summary.json`：17败局12223次call日志与摘要。
- `action_replay_equivalence.json`：6条observation sequence × 2个入口的逐步回放结果。

结论边界：本报告确认部署入口不符、历史初始score误读、当前败局运行正常、近镜像后期现金差。它没有独立证明任何拟议策略提高线上rating，也没有把对手事后private记录用于agent决策。
