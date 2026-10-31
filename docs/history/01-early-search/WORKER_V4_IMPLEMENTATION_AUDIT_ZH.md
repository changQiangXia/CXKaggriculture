# worker v4 实现审计

日期：2026-09-17。构建文件 `build_worker_v4.py`，输出 `candidate_v45_q25_worker_v4.py`。原单点价值贪心草稿已保存为 `worker_greedy_draft.py`。本文件描述当前冻结实现，优先于较早的概念设计稿。

## 已修正的草稿问题

1. 草稿只对单个目标算 value/distance，属于换了一套贪心评分，不能称为路线搜索。当前枚举最多 120 个深度不超过 3 的目标前缀，再按父 nearest 规则补齐**全部**剩余目标，对完整路线计费。
2. 草稿在父 agent 调用后判断 standard config；父动态解析 `_v219_worker`，导致非标准 config 已经执行了搜索。当前 gate 在调用父 agent **之前**生效，并以 finally 恢复。
3. 草稿对 nearest 的同距离目标用分数排序，不等于父 `targets.index` 平局规则。当前严格使用角色 target 的原 ordinal，并要求算出的基线下一命令与真实父命令相同才搜索。
4. 草稿到仓库的距离使用“当前位置的 home”，并遗漏 DROP 的操作回合。当前针对路线终点求四个 shed-access 格的最小距离，携货必须加 1 个 DROP 回合。
5. 草稿最后一天可用步数按 `24-hour` 计算，忽略最后 callback 是 718。当前 day 29 用 `719-step`，其余日保守按 `24-hour`。
6. 草稿 `any(inventory)>0` 使首次 HARVEST 之后全部搜索被禁用。当前允许 TOMATO cargo；其他商品或 inputs 仍回退父规则。
7. 草稿只看到 WATER/HARVEST，可能跳过 FERTILIZE 义务。当前整个 `role['needs_fertilizer']` 期间不搜索，加载流程保持父行为。
8. 草稿外层异常直接返回全 PASS，可能隐藏父异常或丢失合法 market。当前只捕获搜索层异常并返回真实父 worker command；父 agent 本身保留原有安全处理。
9. 草稿计数没有检查 `walk != base`。当前只有实际动作变化才累计 accepts/changed。
10. 已确认 Q25 中全局 `MOVES` 定义存在（N/S/E/W 字典），不存在该名称编译缺失。

## 当前算法

仅对 V219 已确认 crop worker、day 19–29、无施肥义务、当前父命令为移动的局面运行。每个 role 最多 10 个目标，目标必须为棋盘内互不重复的整型坐标，且每个目标仍为 TOMATO PLANT；缺失或损毁时回退父层。

一个目标 bundle 是：当前未浇水且非最后日则 WATER；当前有合法成熟产量则 HARVEST。WATER 和 HARVEST 各计 1 个 callback。搜索不能放弃这些 bundle，也不把舍弃浇水换来的现金评分称为改进。

候选池最多 6 个目标（最近 4 个加最多 2 个较远目标）；枚举深度最多 3 的前缀；每个前缀按原 nearest + ordinal 规则补齐其他目标。评分只使用完整任务总步数（移动 + 必需操作 + 携货时返仓 DROP），必须严格短于真实父路线。相同长度保留先前最优，基线始终是初始最优；最多评估 120 个不同路线。只有路线首个移动命令与父命令不同、完整路线能在剩余 callback 内完成且搜索耗时未超过 8 ms 时才修改动作。

这是**确定数量限制下的路线前缀枚举 + 贪心补全**，属于局部启发式搜索。它不是真正完整 720-step planning，也不是全体工人的联合 beam；既没有隐藏未来状态，也没有将分数优势当作胜率优势。

当前实现滚动只执行一步；没有保存期望未来状态，也没有声称拥有 expected-state guard。下一回合从真实观察重新生成 bundle。专属 actor 的任务不依赖普通 tape 的固定坐标，因此不需要修改普通 farmer/hands 路线。

## 预算与 telemetry

新增 telemetry 包括 search_calls、eligible、accepts/changed、routes/max_routes、baseline_steps、candidate_steps、saved_steps、overflow_rejects、deadline_rejects、base_mismatch、errors、budget_fallbacks、max_ms。

`baseline_steps`/`candidate_steps`/`saved_steps` 是**接受当时的完整路线估计总和**，同一日多个 callback 会重复计算余程，不能解释为整局真实节省回合数。真实任务完成/单位投入/货物收益应在完整官方引擎游戏上统计。

`worker_search_max_ms` 统计搜索函数本身的执行时间，不包括先执行的父 `_v219_worker`；整 agent 的 callback 耗时仍需配对评估器量测。

观察库存保护使用当前 shed + 所有 actor 已携带商品 + 本角色待收获 TOMATO，超过 100 时拒绝。它不是对未来 PURCHASE 或其他 actor 后续收获的确定性容量证书。父仓库保护仍在后续运行；应靠完整真实游戏检查容量回归。

## 已完成的机制检查

* 构建输出通过 `py_compile`。
* 500 个固定随机种子的 V219 2x5 几何问题：全部保留所有目标、候选总成本不高于基线、搜索不超过 120 个路线；其中 228 个有严格短路，最大单次 4.82 ms。
* 结果保存在 `route_geometry_smoke.json`。

这些仅证明生成器存在非平凡路线空间与有界计算，不证明 agent 在真实局面触发，也不证明终局变强。正式门槛仍是官方 `_apply_unit_action` 的整日滚动任务完成测试、V219 commit 机制对局、随后真实双边完整配对测试。旧 9060–9069 等已用 seed 只能作为机制诊断/开发，不可重新称为未见 holdout。

## 尚需关注

* 滚动重算可能改变后续选路，静态完整路线更短不自动保证日内实际执行更短；必须用整日官方动作模拟检验。
* 即使收获总量相同，交货时间变化仍可能影响卖价、其他 worker 仓库空间和对手响应。严格路线缩短仍不是无回归定理。
* 搜索只针对 V219 投资成功的分支。此前确认 panel 的 V219 commit 很少；若完整对局变化为零，应报告触发范围不足，而不是据零回归宣称安全。
* 8 ms 预算回退受到机器负载影响。稳定性测试应检查同 seed 重跑的 command hashes；出现预算回退时先减少固定路线数量再测，不应宽松解释可重复性。
