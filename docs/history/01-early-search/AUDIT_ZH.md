# paired_eval runner 审计记录（2026-09-17）

本次审计针对即将用于候选 v2 games 的本地 paired evaluator，重点检查了实际 loader、两席位计时、健康判定、断点续跑和统计输入。审计没有改动候选模型，也没有上传操作。当前代码哈希为：

* `paired_eval.py`：`5edd1fb1aad2745789ef8f6fde96a5b910c012a000846512335717bb5a4bce8f`
* `test_paired_eval.py`：`acf107b2559859c68eaa4d0fbba99ff4f230ce79f6eab3e2a7cd4ac7f3155822`

## 核查结论

`load_final` 仍使用 Kaggle `get_last_callable`，以冻结在内存中的源码执行最后导出的 callable。`.py` 使用原路径，因此保持 sibling import 的官方路径语义；tar 包只读取安全的根目录 `main.py`，拒绝目录穿越、链接和重复根文件。加载在第一次 action 中进行，所以初始化时间会进入 Kaggle Agent 的 action 计时。`_invoke` 按 callable 的 `co_argcount` 传入 observation/configuration，和官方 loader 的 arity 处理一致。

`.py` 的冻结范围是主源码 bytes；如果主文件导入同目录 sibling，导入文件仍从磁盘读取，runner 不会替它们生成递归 hash。因此可复现实验应优先使用包含完整逻辑的单文件或自包含根 `main.py` tar；使用外部 sibling 的 `.py` 时，结果报告只证明主文件 hash 对应，不能声称整个依赖目录已冻结。

单局的 `healthy` 仍然 fail-closed：必须没有异常或外层超时、环境存在且 `done`、步数等于请求的 `episode_steps`、最后两个 seat 都是 `DONE`、整个轨迹没有 `TIMEOUT/ERROR/INVALID`、两个终局 reward 都是有限数，并且没有 stderr。异常行保留在 checkpoint 和结果中；paired row 只有 candidate 与 parent 都健康才健康。

此次修订修复了一个容易误读的计时字段问题。`env.logs` 每个 step 的两个 duration 按环境 seat 分开收集，再根据被测 artifact 的 `seat` 填充：

* `mine_max_action_duration_sec` / `mine_sum_action_duration_sec`：被测 candidate 或 parent 的 action 时间；
* `opponent_max_action_duration_sec` / `opponent_sum_action_duration_sec`：同局对手的 action 时间；
* 原有 `max_action_duration_sec` / `sum_action_duration_sec` 保留兼容，但 `legacy_action_duration_scope` 明确写成 `both_players`。

这意味着 seat=1 的候选不会把 seat=0 对手的慢 action 误报告为候选耗时。计时仍是 Kaggle environment 返回的每次 action duration；它用于诊断和超时审计，不能单凭本地数值证明线上基础设施等价。

统计层现在对不健康 paired row 设置 `cash_delta=null`、`point_delta=null`、`outcome_transition="INVALID"`。汇总时不再把一条失败行的伪造 W/L 标签计入转移表，bootstrap 也只从健康成对 seed cluster 取样。`summary.ok` 仍只是面板可推断资格，不是候选晋级结论。

断点续跑 manifest 已经使用 JSON 原生 list 保存 opponent hash pair，避免 tuple 写入后读回变 list 导致合法 `--resume` 被错误拒绝。resume 会逐行检查 family/seed/seat 范围和重复键，仅补跑缺少的 pair；候选、父模型、对手、seed、超时、权重、engine hash 或 runner hash 任一变化都拒绝继续。

accepted action digest 也做了防御性读取：如果环境在异常路径下产生了不完整 step，runner 会记录 digest 为 null，而不会让结果整理阶段再次崩溃覆盖原始错误。

## 验证

运行：

```bash
/root/miniconda3/bin/python q25_search_20260917_055120UTC/evaluation/test_paired_eval.py
```

结果：`paired_eval unit tests passed`。测试包括：

1. “少输”不会被统计为胜利；两席位会聚合到一个 seed cluster；
2. 不健康行使 summary fail-closed；
3. `.py` 与安全 tar 的最后 callable 语义；
4. fake environment 中候选/对手 duration 的 seat 归属（包括旧兼容字段）；
5. unhealthy paired row 的 delta/transition 清空；
6. 完整 checkpoint → 全部 resume（零重复任务）→ 删除一行后 resume（只补一行）→ 修改 seed manifest 拒绝的完整流程。

另行运行 `py_compile` 通过。测试进程打印的 `open_spiel_env` 缺少 `pokerkit`、`werewolf` 缺少 `pydantic` 是 Kaggle 环境注册时的无关可选环境提示；Kaggriculture 测试本身通过，不能把这两行当作候选运行错误。

## 仍需注意

paired runner 的 candidate 与 parent 是顺序运行的两局真实交互，各自重置环境；共同 seed 提供匹配比较，不是同一局内同时替换策略。每个 family 的 bootstrap 以 seed 为 cluster、先平均两席位；family weight 必须在实验开始前冻结。来源相近的 V46/Pipe8/Beyond 不能因为文件名不同就当成独立家族。

当前旧结果文件保持不变。新的 v2 games 应记录新 runner hash，并优先查看 `mine_*` 字段；旧结果中只有合并的 duration 字段时，不能事后推断候选单独的最大耗时。
