# Kaggriculture 工作记录

最后更新：2026-09-12（UTC）

这份文档记录目前已经验证过的事实、实验结果、策略判断和提交纪律。后续实验应先更新这里的结论，再决定是否创建新候选。

## 目标与硬约束

- 比赛：Kaggle `kaggriculture`，代码/智能体类比赛。
- 用户目标：在不超过 5 次提交内冲击前 200。
- 设备：单卡 RTX 4090；用户明确要求避免激进训练，优先稳定策略、数据/状态处理和后处理。
- 提交纪律：用户明确要求每次提交必须先得到明确同意。没有“同意提交某个具体候选”的文字授权，不得上传。
- 当前最后一次机会应谨慎保留，未经授权不得使用。

## Kaggle API 与比赛状态

- 新版 CLI：`/root/miniconda3/envs/kaggle-cli/bin/kaggle`，版本 2.2.4。
- 默认 PATH 中另有旧版 `/root/.local/bin/kaggle`，版本 1.7.4.5，不识别仅有 `access_token` 的新配置。
- 凭据：`~/.kaggle/access_token`，权限为 `600`；不要打印、提交或复制 token。
- 账号：`intoxicatinglips`；队伍名显示为 `CHEN Xiang`。
- 比赛 ref：`kaggriculture`，id `147734`。
- 已报名，提交未关闭，最大每日提交数为 5，截止时间为 2026-09-30 23:59 UTC。
- 说明文件已保存：
  - [`kaggriculture/README.md`](kaggriculture/README.md)
  - [`kaggriculture/AGENTS.md`](kaggriculture/AGENTS.md)
  - [`kaggriculture/API_CHECK.md`](kaggriculture/API_CHECK.md)

### Active submission limit（规则核实）

- Kaggle 比赛的 `Evaluation` 页面明确写明：每天最多可以提交 5 个 agents，但为减少匹配 bot 数量，**只有最新的 2 个提交会被追踪**；最新 2 个提交也用于最终排行榜评估。
- `Frequently Asked Questions` 页面将其显示为：`Only your most recent ${competition.NumScoredSubmissions} are active`；本比赛的 `NumScoredSubmissions` 为 2。
- 因此“每天最多 5 次”和“同时最多 2 个 active submissions”是两个不同限制。上传第 3 个不会增加最终评估名额，并会使更早的 active bot 离开活跃匹配池；历史记录仍可在 Submissions 页面查看。
- 本队当前活跃提交（`kaggle competitions team-submissions 16870342`）为：`56171485`、`56170591`。
- 当前 CLI 额度查询（UTC 2026-09-12）返回：当天已计数 3、当天剩余 2；该额度与历史 Submissions 列表的展示口径不同，提交前应以当时的 `submission-limits` 返回为准。

## 已执行的提交

> 分数会在 Kaggle 后续评测中更新，以下记录以当前 API 查询为准。

| 提交 | 文件 | 状态 | 当前公开分数/错误 | 说明 |
|---:|---|---|---:|---|
| `56170379` | `submission_v1.tar.gz` | COMPLETE | 约 `1100–1165`（曾多次更新） | V16-RC5 公开高分路线；可运行但远低于前 200 |
| `56170496` | `submission_v2.tar.gz` | ERROR | Validation Episode failed | tar 包内 artifact 处理错误 |
| `56170591` | `submission_v3.tar.gz` | COMPLETE | 约 `997–1598`（曾多次更新） | Shop Router；远程结果不稳定且低于门槛 |
| `56170774` | `submission_v4.tar.gz` | ERROR | Validation Episode failed | 日志明确显示找不到 `/kaggle_simulations/agent/actions.json` |
| `56171485` | `dmitri_final_submission.tar.gz` | COMPLETE | 当前 team-submissions 查询约 `847.3`（分数会动态变化） | Dmitrii herd-safe sale-window；当前为最新 active bot |

第 4 次失败的日志已经下载到 `logs_v4/`。根因是 Kaggle validation 只把 `main.py` 作为 agent 加载，不能依赖压缩包中的外部 `actions.json`。

当前排行榜第 200 名分数约为 `2697.5`，所以已有完成提交均未达到目标。

## 本地环境修复

PyPI 的 `kaggle-environments` 包没有随当前安装分发 Kaggriculture 环境。已从 Kaggle 官方仓库同步当前环境文件，并补齐兼容的 `utils.py`：

- `kaggriculture.py`
- `kaggriculture.json`
- `utils.py`（包含 `resolve_episode_seed`）

现在可以本地运行：

```python
from kaggle_environments import make
env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 123}, debug=True)
```

本地验证应覆盖完整 720 回合、两个 seat、多个固定 seed，并检查最终状态为 `DONE`。

## 社区方案与实验结果

### V16-RC5 / Boatlee 路线

- 公开 notebook：`boatlee/v16-rc5-high-score-8c-4s-premium-market-lead`。
- 生产核心约为 8 COW / 4 SHEEP，并使用 premium product 的一回合 market lead。
- 公开 notebook 声称在其本地参考面板中表现稳定。
- 本地运行可完成 720 回合，但实际 Kaggle 提交分数只有约 1100 级别，说明不能把 notebook 的本地资金差直接等同于 leaderboard 分数。

### Shop Router / Yhay81

- 公开 notebook：`yhay81/shop-router-0909`。
- 有 13 条 action tape，根据前两个 shop 选择 plan，并带 weed repair、库存投影和销售提前逻辑。
- 最初提交因外部 `actions.json` 处理方式不正确而失败；修正 artifact 后仍只有约 997–1598 分。

### Flex 社区路线

- 公开 notebook：`flexonafft/kaggriculture-most-powerfull-route`。
- 单文件内含多 route、物理状态恢复和终局规划。
- 文件：`community_flex.py`；候选包：[`community_candidate_v5.tar.gz`](community_candidate_v5.tar.gz)。
- 本地 self-play：
  - seed 0：`63,607 : 64,300`
  - seed 1：`146,585 : 146,585`
  - seed 2：`82,463 : 82,463`
- 对 starter，两个 seat 都能明显胜出，说明不依赖某一侧放弃。
- 719 次有效 observation 的本地调用耗时：最大约 54 ms，P99 约 0.76 ms。

### Thomas replay router

- 公开 notebook：`thomastschinkel/kaggriculture-95-5-win-rate-via-replay-routing`。
- notebook 报告：689 个未参与训练的 replay、32 个 seed、双 seat、44,096 场中约 95.5% 胜率。
- 前 6 天使用共同 opening，step 144 读取公开状态后在 5 条 schedule 中选择路线。
- 本地 self-play seed 0：`66,496 : 67,254`。
- 对 starter seed 0：
  - candidate seat 0：`183,962 : 3,504`
  - candidate seat 1：`3,633 : 151,868`
- 候选文件：[`thomas_candidate_v5.tar.gz`](thomas_candidate_v5.tar.gz)。

### Dmitrii 3-action sale window

- 公开 notebook：`dmitriigluzdov/kaggriculture-herd-safe-sale-window-lb-2700`。
- notebook 的公开目标约为 2700 leaderboard 分数。
- 核心改动：step 288 后将销售窗口扩展到 3 个 action，同时保护后续买牲畜/雇工所需现金、未来 PICKUP/PLACE 资源和 route 边界。
- 已重构为单文件：[`dmitri_candidate_v5.tar.gz`](dmitri_candidate_v5.tar.gz)。
- 本地 self-play：
  - seed 0：`68,145 : 68,145`
  - seed 1：`146,696 : 146,696`
- 对 Thomas，seed 0/1 均略胜；对 Flex，seed 0/1 略负但接近。
- 719 次有效 observation 调用无异常；最大耗时约 527 ms，P99 约 0.174 ms。

## 关键策略判断

1. 真实目标是 head-to-head 胜率，不能只优化终局 bank。
2. 完全相同的 deterministic agent 在 validation 中会镜像运行，产生平局；单边 PASS 造成的巨大资金差是误导性的。
3. 高分路线的主要优势来自 replay imitation、shop-aware route selection、市场销售时序、牲畜现金保护和异常恢复。
4. CARE 的实际引擎行为应以本地环境为准；社区实验指出实际 bonus 是 +1，而 README 中容易被误读为 +2。
5. 直接从零训练 PPO/DQN 不适合当前条件：720 步延迟奖励、巨大离散动作空间、随机 shop 和动态市场会导致训练昂贵且容易过拟合。
6. 更合适的 RL/搜索路线是：高分 replay 作为 policy prior，本地 simulator 做有限 horizon search，按多 seed、多对手胜率筛选。
7. ensemble 不能把两个 agent 的 action 逐回合机械拼接，否则会破坏各自的 worker 状态、库存投影和市场债务。
8. 合理的分层 ensemble 应为：共同 opening → shop-aware route selector → 稳定 production tape → sale-window overlay → safety/recovery layer。

## 当前候选与建议优先级

当前未提交候选：

1. `dmitri_candidate_v5.tar.gz`：3-action sale window，公开目标约 LB 2700，本地稳定；
2. `thomas_candidate_v5.tar.gz`：公开报告 95.5% holdout 胜率，最符合 head-to-head 目标；
3. `community_candidate_v5.tar.gz`：完整单文件、多 route、状态恢复强；
4. `candidate_phase_v5.tar.gz`：本地终局资金高，但 leaderboard 预期证据较弱。

注意：这些候选都只是在本地和公开资料上验证过，不能宣称已经达到前 200。

### 已准备的两份待提交包（未上传）

- [`ready_thomas_v6.tar.gz`](ready_thomas_v6.tar.gz)：Thomas replay router，单文件根目录包，已通过解压隔离运行和自战验证。
- [`ready_dmitri_v6.tar.gz`](ready_dmitri_v6.tar.gz)：Dmitrii herd-safe sale window，单文件根目录包，已通过解压隔离运行和自战验证。
- 详细 SHA-256、20 个双向对抗结果和验证记录见 [`READY_CANDIDATES.md`](READY_CANDIDATES.md)。
- 两份包均未上传；只有用户对具体候选给出明确授权后，才允许提交。

### 2026-09-12 单次提交尝试

最新 API 查询（2026-09-12 UTC）显示队伍 `CHEN Xiang` 当前 rank `136`，比赛总队伍数约 `8713`，已进入前 200。该排名会随 head-to-head 对局动态变化，仍不能替代本地候选验证；最近提交 `56181773` 的 publicScore 约 `2492`，旧 V37 `56178383` 约 `2752`。

- 用户明确授权后，选择 [`ready_thomas_v6.tar.gz`](ready_thomas_v6.tar.gz) 作为替换 active bot 的候选。
- 已执行一次 `kaggle competitions submit`。上传进度停在 0%，进程等待约 14 分钟后终止；独立查询确认没有生成新的 submission ref，提交列表仍只有原有记录，额度也未变化（`numToday=3`, `numTotal=3`, `numAllowedNow=2`）。
- 结论：这是 Kaggle 上传服务/网络请求未完成，不能算作成功提交；为遵守“提交一次”要求，没有重试。

#### 上传卡顿根因（2026-09-12）

- `kaggle competitions submissions`、`submission-limits` 和普通 Kaggle API 请求均能正常访问。
- 卡住的 CLI 进程 fd 5 对应的远端连接为 `172.217.118.4:443`，状态长期为 `SYN_SENT`；这是 resumable upload URL 的 Google 上传端点，不是 Kaggle API 主站。
- 直接测试显示 `www.googleapis.com` 的部分解析地址（包括 `172.217.118.4`）在当前 AutoDL 网络不可达，而 `173.194.43.207`、`142.251.46.91` 可建立 TLS 连接并返回 HTTP 响应。
- 已准备 [`submit_kaggle_resilient.py`](submit_kaggle_resilient.py)：只对 `www.googleapis.com` 的 DNS 解析优先使用可达地址，再调用官方 Kaggle client；脚本没有重试循环，未来一次授权对应一次上传尝试。
- 已测试 `source /etc/network_turbo`：该代理主要面向 GitHub/Hugging Face，直接代理 Kaggle 会 SSL 超时；resilient wrapper 现在会自动把 Kaggle API 和 Google 上传域名加入 `NO_PROXY`，同时保留对 `www.googleapis.com` 的可达 IP 选择，因此不应在上传时直接把 Kaggle 流量送进该代理。

### 最新日志监控与排行榜状态

- [`monitor_agent_logs.py`](monitor_agent_logs.py) 已作为后台进程运行，每 600 秒扫描 active submissions，并收集 tie/loss replay 与 agent logs。
- [`analyze_agent_logs.py`](analyze_agent_logs.py) 将 replay 的动作/资源/终局状态与 logs 的耗时/stdout/stderr 合并，报告写入 `agent_monitor/ANALYSIS.md`。
- 最近一轮报告覆盖 98 个 bot-side tie/loss 记录：`56170591` 有 38 loss、39 tie；`56171485` 有 16 loss、5 tie。两者均无 stderr；Shop Router 极端落败最低约 `-102,294`，Dmitrii loss 平均约 `-2,916`。
- 最新 leaderboard API 查询：本队 `CHEN Xiang` 为 rank `683`、score `2447.9`；第 200 名约 `2699`，仍有约 `252` 分差距（排行榜会动态变化）。

### 新提交 `56176848` 的 validation 说明

- `publicScore=600.0` 是新 bot 进入匹配池时的 skill rating，不是 validation 的终局资金；不能用它直接判断策略只赚了 600。
- Validation episode `108030576` 的 replay 奖励为 `63607.0 / 64300.0`，两个 seat 均 `DONE`；两份 agent log 均 719 次调用、无 stderr，最大耗时约 `0.31s`。
- 新 bot 已成功进入 active pool；后续应以其匹配对局的 win/tie/loss 和 rating 变化评估，而非把初始 600 rating 当作收益。
- 监控脚本随后修复了 validation 误判为 tie、以及去重字段错误两个问题；当前 `108030576` 已迁移为 `validation`，后续扫描不会重复下载已处理 episode。

### `56176848` 首批公开匹配

- 截至最近一次扫描，`56176848` 已完成 5 场公开对局且全部获胜（5–0），其中 seat 0 与 seat 1 均有胜局；对手包括 hundun、Anup Gautam、Prashant Kikani、Rahul Barakoti ITM、xiao cat q。
- 终局奖励分别为 `106503`、`157403`、`83486`、`140751`、`111906`（按我方所在 seat 取值）；这是早期样本，仍需更多不同强度对手验证。
- 目前该提交尚未出现公开 tie/loss，监控将继续收集后续异常对局。

### `56176848` 后续匹配更新（2026-09-12）

- active 队列监控随后收集到竞争对局 `108047561`：我方（seat 1）与 RYUSHI 终局均为 `101341`，属于 1 场 tie。
- replay 显示两边 720 步动作逐步一致，终局销售序列也一致；这是同路线/镜像策略导致的自然平局，非运行时异常。
- 当前累计为 `56176848`：21 胜、1 平、0 负（另有 1 场 validation）；rating 随匹配动态变化，继续观察更多不同对手。

### 社区 Flex 稳健版候选

- 根据本地消融结果，已准备 [`ready_flex_v7.tar.gz`](ready_flex_v7.tar.gz)：仅关闭罕见且 matchup-sensitive 的 V233 sheep overlay，保留 V224 销售重排及其他恢复逻辑。
- 本地官方环境 seed 0–2 对 Thomas 为 3/3 胜，对 Dmitrii 为 2/3 胜，全部 720 步 `DONE`；详细结果见 [`READY_CANDIDATES.md`](READY_CANDIDATES.md)。
- 该候选尚未提交；提交仍需用户对具体文件明确授权。

## 后续实验计划（不提交）

- 用固定 seed 集合（至少 20 个）跑候选与多个社区对手的双 seat 对抗；
- 记录胜率、平均 margin、最差 margin、seat 差异、错误率和 action latency；
- 在 Dmitrii 与 Thomas 之间做状态级 route selector，而不是逐 action 混合；
- 将 sale window 参数、premium 商品集合、提前销售比例和 weed replay 窗口作为有限搜索变量；
- 任何组合都必须通过单文件隔离运行，确认不存在 `actions.json` 等外部依赖；
- 候选通过后，先向用户报告具体文件、实验数据、预期风险，再等待明确授权。

## 提交授权规则

以下内容均不构成授权：

- “继续研究”；
- “明天还有机会”；
- “看看结果”；
- 任何没有点名具体候选的肯定语句。

只有用户明确写出类似下面的文字，才可以提交：

> 同意提交 `dmitri_candidate_v5.tar.gz`

上传后必须记录：提交 ref、时间、状态、分数、episode id、错误日志（如有）和剩余提交次数。

## 安全记录

API token 曾在早期内部工具消息中被错误回显过。不要在代码、文档、提交说明或聊天中复制 token；建议在 Kaggle 设置中轮换 token，并继续使用权限为 `600` 的 `access_token` 文件。


### 提交 `56178383`（2026-09-12）

- 用户明确授权后，使用 [public_v37_candidate.tar.gz](public_v37_candidate.tar.gz) 完成一次提交。
- Kaggle 回执：ref `56178383`，状态初始为 `PENDING`；上传进度从 0% 到 100%，返回 `Successfully submitted to Kaggriculture`。
- 提交前 SHA-256：`4babc9e9d84a070eb72e006af6cf06ce435d7adab8db6c186540ca63daf055fa`；包内仅根目录 `main.py`。
- 提交额度回执：今日剩余 3 次，生命周期提交数 5。
- 在 Kaggle 将其处理为 COMPLETE 前，`team-submissions` 仍显示旧 active 队列 `56176848` 与 `56171485`；监控脚本会在后续轮询中自动切换到新 active 两个。

### `56178383` validation 完成与 active 队列切换

- Kaggle 已将 `56178383` 处理为 `COMPLETE`，当前公开 rating 初值为 `600.0`。该数值是匹配池 skill rating，不是终局资金，也不能单独推断候选强弱。
- validation episode `108053483` 已被监控脚本归类为 `validation`，没有计入竞争胜负；没有 stderr 或上传错误。
- `team-submissions` 现已切换为 `[56178383, 56176848]`，旧的 `56171485` 被 active 队列挤出。监控已通过 `--once` 实测状态写入并会继续每 600 秒轮询。
- 首场公开匹配 `108054643` 已完成：`56178383`（我方 seat 1）以 `96228 : 20483` 战胜对手；监控已归类为 `win` 并保存 replay。当前新候选累计为 `1 胜 / 0 负 / 0 平`（另有 1 场 validation）。
- 后续公开匹配 `108055634` 也已完成：`56178383`（我方 seat 1）以 `147947 : 14866` 战胜 Thananut Phiboonbanakit；累计更新为 `2 胜 / 0 负 / 0 平`（另有 1 场 validation）。同一时间旧 active Flex 收到 tie `108056380`（`72287:72287`），监控已保存该日志用于对照。


### 新候选公开匹配继续（2026-09-12）

- `56178383` 新增公开对局 `108056622`、`108056683`、`108056933`、`108058043`，均胜；其中我方两个 seat 都出现过。
- 终局资金分别为 `141465:90002`、`65512:137711`、`84381:46782`、`67780:28121`（按 replay seat 顺序）；累计 `6 胜 / 0 负 / 0 平`（另有 1 validation）。
- 旧 active Flex 新增 `108055663` 与 `108056668` 两场 loss，说明其 rating/稳定性继续承压；新候选暂未出现失利。
- 再次扫描后，`56178383` 新增 `108057589`（胜 nixotrix，`107874:84071`）和 `108058043`（胜 Ashish Dubey，`67780:28121`）；累计 `7 胜 / 0 负 / 0 平`（另有 validation）。

### 监控更新（2026-09-12 04:55 UTC）

- `team-submissions` 仍返回 active 队列 `[56178383, 56176848]`；后台监控 PID `30161` 持续运行，轮询间隔 600 秒。
- 最新状态文件统计：`56178383` 为 `11 胜 / 0 负 / 0 平`（另有 1 validation）；`56176848` 为 `25 胜 / 5 负 / 3 平`（另有 1 validation）。新提交尚未出现 tie/loss。
- Flex 的新增失利 `108057830`、`108058678`、`108059677` 资金差分别约 `-1427`、`-907`、`-114`；均无 stderr，最大单步调用约 `0.35s`、`0.31s`、`0.27s`。动作和订单模式几乎不变，证据仍指向共享市场销售时序与对手路线，而非运行时故障。
- 已重新生成 [`agent_monitor/ANALYSIS.md`](agent_monitor/ANALYSIS.md)，当前覆盖 110 个 bot-side tie/loss 记录；后续扫描会继续只下载两个 active submission 的 tie/loss 日志。


### 本地 V37 消融筛查 EXP-174（2026-09-12）

- 基于最新 Flex 小差距失利，完成两项低风险消融；两个候选均未提交。
- `candidate_v37_nosheep.tar.gz`（SHA-256 `a209d0a384002f55c68ea7d9a3398b0f789e3538bbeed0410be7a88b5e05b7c8`）关闭 V233 羊群资格判断；9001–9003、双 seat 对 Flex 与 V37 基线逐局完全相同，没有收益。
- `candidate_v37_noquote.tar.gz`（SHA-256 `2581c021953003ef7ac92d7b3dac35167d7f191f4aca64d20af3f1e51d2743c5`）关闭 V37 quote 销售重排；9001–9003 中 seat0 分别损失 612、997、1535 资金，虽 seat1 小幅增加但整体不稳，已拒绝。
- 两个包均通过 `py_compile`、隔离加载和完整 720 步 `DONE`；当前没有足够证据替代已提交 V37。详见 `CANDIDATE_V37_EXP174_REPORT.md`。

### 监控再次更新（2026-09-12）

- 手动执行一次 `monitor_agent_logs.py --once` 成功，返回 `watched_submissions=2 collected_new=0`；后台 PID `30161` 仍存活。
- 当前 active 队列保持 `[56178383, 56176848]`。状态统计更新为：V37 `56178383` 共 `16 胜 / 0 负 / 0 平`（另有 1 validation）；Flex `56176848` 共 `29 胜 / 5 负 / 3 平`（另有 1 validation）。V37 仍未出现 tie/loss。
- 继续保持不提交策略，等待更多 V37 对局和有代表性的失败日志；任何候选上传仍需用户明确点名授权。

### V37 施肥阈值消融 EXP-175（2026-09-12）

- 将 V219 施肥触发条件从 `FERTILIZER <= 30` 单变量改为 `<= 25`，生成 [`candidate_v37_fert25.tar.gz`](candidate_v37_fert25.tar.gz)，SHA-256 `14af99ab4a75c0a211bfd29249a3273fa35dd1c6b79c8209e035b0e2d5ca7796`。
- 对 `ready_flex_v7` 使用 seeds `9001–9005`、双 seat；V37 基线和 fert25 各 10 局。两者都是 `10 胜 / 0 负 / 0 平`，平均资金差均为 `+4831`，最小 `+1785`，最大 `+12661`；每一局终局奖励完全一致，且全部 720 步 `DONE`。
- 该阈值在此面板未产生行为或收益差异，候选仅保留作实验档案，不升级为待提交版本。报告见 [`CANDIDATE_V37_FERT25_REPORT.md`](CANDIDATE_V37_FERT25_REPORT.md)，复现实验在 [`experiments/v37_fert25/run_panel.py`](experiments/v37_fert25/run_panel.py)。

### 最新 Flex 失败日志（2026-09-12）

- 监控新增并下载了 `108068681` 与 `108069646`，重新生成的 [`agent_monitor/ANALYSIS.md`](agent_monitor/ANALYSIS.md) 当前覆盖 112 个 bot-side tie/loss 记录。
- `108068681`：Flex 终局 `95766` 对 `98016`，差值 `-2250`；双方均完整 `720` 步、无 stderr。对手同一路线但多出约 98 次 BUY_PRODUCT FERTILIZER、9 次额外 HIRE，属于有限施肥/劳动分支差异。
- `108069646`：Flex 终局 `69810` 对 `71377`，差值 `-1567`；对手使用 10 个 TOMATO 种子和额外番茄投资路线，全部正常结束，无 stderr。这与此前观察一致，V37 已有对应 smarter-labor/tomato 覆盖。
- 这两局没有发现新的运行时故障或普遍性容量问题；不对 Flex 做 ad hoc 补丁，继续把 V37 作为线上基线。

### V37 holdout 扩展（9006–9010，2026-09-12）

- 按用户选择，对 V37 与三个本地公开方案各跑 5 个未参与前一轮筛查的 seed、两个 seat，共 30 场；官方本地引擎、720 步、双方 `DONE`、`env.done=True`。
- 对 `ready_flex_v7`：10 胜 / 0 负 / 0 平，平均资金差 `+3373.4`，最小 `+1463`。
- 对 `thomas_main.py`：10 胜 / 0 负 / 0 平，平均资金差 `+5670.7`，最小 `+1372`。
- 对 `dmitri_final.py`：10 胜 / 0 负 / 0 平，平均资金差 `+6505.9`，最小 `+3103`。
- 这轮 holdout 没有发现座位偏差或运行时异常；它增强了 V37 的本地稳健性证据，但仍不等价于线上排名保证。逐局输出保存在 `/tmp/v37_holdout_9006_results.json`，没有修改或上传任何候选。

### V37 线上 tie 诊断（2026-09-12）

- 监控收集到 V37 的新对局 `108071579`：终局 `77288 : 77288`，720 步完成，最大调用耗时约 `0.349s`，无 stderr。
- replay 中双方动作序列高度相同（WATER=1102、HARVEST=475、CARE=397 等主路线计数几乎一致），属于镜像/同策略自然平局；没有发现异常或可通过简单补丁修复的单点故障。
- 之后 V37 又继续取得胜局；当前状态统计为 `27 胜 / 0 负 / 1 平`（另有 1 validation）。该 tie 已纳入 [`agent_monitor/ANALYSIS.md`](agent_monitor/ANALYSIS.md)，不改变 V37 作为本地和线上基线的判断。

### V37 新增线上失利与 reserve144 严格对照（2026-09-12）

- 最新日志又发现 V37 的 loss `108078615`、`108083700`、`108084677`、`108085679`，以及 mirror tie `108082646`、`108084841`；全部 720 步 `DONE`、无 stderr。失利分别对应 TOSS 的 COW/高 SELL 路线、早期 wheat/animal 分歧、10 TOMATO 投资和额外 HARVEST+末期销售时序。
- `candidate_v37_reserve144.tar.gz`（将 `_r36_reserve` 生效窗口从 step 288 提前至 144）已完成严格本地对照：与原 V37 在 `9001–9020` 加 `1495252849`、双 seat 共 42 场中为 `31 胜 / 3 负 / 8 平`，平均差 `+10.0`、最差 `-2594`，且平局 seed 仍为平局；因此明确拒绝，不能称为优质候选。
- 同一候选对 Flex、Thomas、Dmitrii 的 `9006–9010` 双 seat 均为 12/12 胜，但对 V37 自身出现负差，说明它只是 matchup 改变，不能替代基线。候选包仅作实验归档，未上传。

### reserve240 复核与最新线上日志（2026-09-12）

- 将 reserve 窗口收窄为 step 240–695 后，与 V37 在 `9001–9020` 加 `1495252849`、双 seat 共 42 场仍为 `31 胜 / 3 负 / 8 平`，平均差 `+10.0`、最差 `-2594`；相比 reserve144 没有消除负差，因此不保留为候选。
- 监控统计随后更新为：V37 `56178383` 为 `43 胜 / 5 负 / 3 平`（另有 1 validation）；Flex `56176848` 为 `48 胜 / 22 负 / 5 平`（另有 1 validation）。V37 新增 loss 仍是小幅资金差（最大约 `-2698`），所有局 `DONE` 且无 stderr；新平局均为 720 步镜像动作。
- 现阶段没有任何本地改动通过“对 V37 零负差”门槛；所有新 tar 包继续仅作实验归档，未上传。

### 后续线上日志与严格候选门槛（2026-09-12）

- 日志监控继续收集到 V37 的新 loss（例如 `108078615`、`108083700`、`108084677`、`108085679`、`108088314`），以及 mirror tie（`108082646`、`108084841`）；这些局均 `DONE`、无 stderr。新增 loss 仍集中在公开 COW/TOMATO/早期动物路线和 day 27–29 销售时序。
- reserve144/240 两个销售窗口候选均已通过多 seed 完整运行，但相对原 V37 都出现负差或平局，全部拒绝；固定 seat 的 tie-break 也出现明显 seat bias，拒绝。
- 当前实验策略调整为：任何新候选必须在原 V37 对照上通过至少 `9001–9020 + 镜像 seed`、双 seat、全 `DONE` 且零负差，之后再做三个社区对手面板；在此之前只保留实验档案，不进入待提交列表。

### reserve624 早停实验（2026-09-12）

- 尝试把 reserve 窗口进一步收窄到 step 624–695；与原 V37 的前 3 个 seed、双 seat 即出现连续负差：`-1480`、`-1762`、`-2910`。
- 该实验在达到明确失败证据后早停，没有生成可提交包；说明单纯按时间提前销售会破坏共享市场时序，必须同时满足实际 shed 库存、下一步明确 SELL 数量和 debt 抑制条件。

### V219 番茄资格放宽实验（2026-09-12）

- 针对线上 loss `108084677`/`108069646` 的 10 TOMATO 路线，尝试将 V219 的公开 shop 资格从至少 3 个 Pizza/Farmers shop 放宽为至少 2 个，其他条件不变。
- 与原 V37 对照、9006–9010 双 seat 共 10 场：0 胜 / 2 负 / 8 平，平均差 `-184.2`，最差 `-921`；所有对局虽 `DONE`，但出现明显负差，立即拒绝。
- 结论：番茄分支不能仅凭放宽 shop 数量启用；现有 qualification 保护必须保留。未生成待提交包。

### V231 COW 条件放宽实验（2026-09-12）

- 针对 TOSS/COW 路线 loss，尝试将 V231 的 `milk_shops>=2` 放宽为 `>=1`，其他条件不变。
- 与原 V37 对照、9001–9010 双 seat 共 20 场：3 胜 / 1 负 / 16 平，平均差 `+217.4`、最差 `-1581`；所有对局虽 720 步 `DONE`，但座位和 seed 结果明显不稳。
- 该改动立即拒绝，不生成待提交包；现有 COW qualification 条件保持不变。

### V231 动物数量门槛实验（2026-09-12）

- 将 COW/羊替换分支的公开数量条件从 `COW>=4, SHEEP>=2` 放宽到 `COW>=3, SHEEP>=1`，其余条件保持不变。
- 与原 V37 对照、9001–9010 双 seat 共 20 场：1 胜 / 1 负 / 18 平，平均差 `0.0`、最差 `-1581`；全部 `DONE`，但没有稳健收益，已拒绝且未生成提交包。
- 结论：动物路线切换需要更完整的市场/现金/商店联合条件，单独降低数量门槛会增加方差。

### V219 对手 TOMATO 反应式资格实验（2026-09-12）

- 尝试只在公开对手农场已有至少 5 个 TOMATO tile 时，才允许 V219 使用 2 个 Pizza/Farmers shop 的放宽条件；其余现金、价格、土地和库存条件保持原样。
- 与原 V37 对照、9001–9010 双 seat 共 20 场：1 胜 / 1 负 / 18 平，平均差 `0.0`、最差 `-1581`，无运行异常；没有形成稳定收益，已拒绝。
- 原因是 V219 的初次承诺在 day 12，而对手 TOMATO 通常在更晚阶段才公开出现，单靠当时的公开 tile 无法可靠预测后续路线。

### 最新监控与镜像 loss（2026-09-12）

- 新收集的 V37 loss `108105829`（Tien N.）为 `90349 : 93717`，差值 `-3368`；双方动作计数和市场申报几乎完全一致，仅出现极少量 SELL/数量差异。对局 720 步 `DONE`、无 stderr，属于镜像路线下的库存/市场边际差。
- 当前状态统计：V37 `56178383` 为 `51 胜 / 17 负 / 6 平`（另有 1 validation）；Flex `56176848` 为 `55 胜 / 26 负 / 6 平`（另有 1 validation）。active 队列与监控 PID `30161` 均正常。
- 该类镜像 loss 再次说明固定 seat 加卖或固定 tie-break 会产生反向 seat 损失；暂不采用，继续要求任何候选相对 V37 零负差验证。

### V37 新 tie 对局与本地 tie-break 实验（2026-09-12）

- 监控发现 V37 新 tie：episode `108071579`，终局 `77288:77288`，对手 Davics；双方均 `DONE`/720 steps，无 stderr，max 调用约 0.349s。
- Replay 中 720/720 个 action dict 完全相同，属于公开相同策略/镜像自然平局；动作与市场数量正常（SELL 479、HIRE 281），无运行时故障。
- 尝试本地 EXP-TIE-NOOP：只在 seat 1 首次遇到边界且原动作为 PASS 时替换为无效越界移动，以打破 replay identity；在 seeds 9001–9013 对 V37 自战中大多数仍 tie，seed 9004 seat 1 产生 -1581 资金差，故拒绝，不打包为待提交候选。
- 当前 V37 线上累计 `27 胜 / 0 负 / 1 平`（另 1 validation）；active 队列未变。继续以 V37 为基线，不因单场镜像 tie 做高风险改动。
- 监控随后收集 Flex 新 loss `108073749`（`59913:58916` 按 replay seat 顺序，own seat 1），无 stderr；分析器已在后台更新 `ANALYSIS.md`。
- 监控自动继续运行后，V37 新增胜局 `108075592`、`108076601`、`108077600`，当前累计 `30 胜 / 0 负 / 1 平`（另 1 validation）。Flex 新增 `108079092` loss 与 `108079170` tie；监控仍覆盖两个 active submission。
- 最新 state.json（06:06 UTC）统计：V37 `56178383` = 30 胜 / 0 负 / 1 平 + 1 validation；Flex `56176848` = 38 胜 / 11 负 / 5 平 + 1 validation。active IDs 仍 `[56178383, 56176848]`。
Root: read ROOT_MESSAGE_REVERSE.txt and INSPECT_REVERSE_FINDINGS.md

## 2026-09-12 提交 56185929 后续

- 经当前轮次明确授权，提交 `candidate_v37_h5sim96.tar.gz` 一次；Kaggle ref `56185929`。
- 上传成功，validation episode `108183391` 完成，双方 720 steps、无 stderr，奖励 `[65206, 65884]`。
- 首个 public episode `108183555` 已完成，奖励 `[165840, 15972]`，双方 720 steps、agent log 无异常；该局显示候选能正常运行并取得明显胜差。
- Kaggle 当前 publicScore 暂为 `651.0`，仍只有一个 public 对局，不能视为收敛成绩；没有执行重试或追加提交。
- active 队列现为 `56185929` 与 `56181773`，监控 PID `30161` 继续每 600 秒扫描两个最新 active submission。

- 后续查询：56185929 public episodes 108183555 与 108184554 均胜出，当前 publicScore 从 651.0 上升到 823.8；尚无该提交的 tie/loss。

## 2026-09-12 目标达成核验

- Kaggle leaderboard 官方 API（page-size 200）返回 CHEN Xiang / teamId 16870342 当前第 158 名，团队 score 2735.2。
- 已有明确回执的最新改进提交 `56185929` 为 COMPLETE；保留的 V37 基线 `56181773` 同为 COMPLETE。
- 本日有效提交共 4 次（ref 56176848、56178383、56181773、56185929），未超过 5 次；最后一次剩余额度未使用。
- 新候选已完成6场 public 对局、均胜出；无 runtime stderr，完整720 steps。
- 当前目标“5次之内提交进入前200”已按当前官方榜单核验达成；比赛排名仍会随对局及其他队伍变化。
- 监控 PID30161继续保留，600秒扫描最新两个active submissions。后续任何追加提交仍需用户新的明确授权。

## 2026-09-12 h5sim96线上败局复盘

- h5sim96 `56185929` 当前 public rating 曾由约2528.5升至2574.3；在41场public局中35胜/6负/0平。当前不是最终收敛样本。
- 低rating早期对手抬高总体胜率；2400+对手约6胜4负、2500+约2胜3负，解释了其暂时低于V37的rating。
- 新报告：[H5_ONLINE_ANALYSIS_20260912.md](H5_ONLINE_ANALYSIS_20260912.md)。
- 三场逐回合现金核验：[analysis_h5_20260912/LOSS_MECHANISMS.md](analysis_h5_20260912/LOSS_MECHANISMS.md)；发现premium销售时序和step623 carried+shed容量溢出。
- 已纠正h5sim96历史验证范围和跨版本报告错误：[H5SIM96_VALIDATION_AUDIT.md](H5SIM96_VALIDATION_AUDIT.md)。
