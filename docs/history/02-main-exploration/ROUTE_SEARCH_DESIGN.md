# 路线自搜（island-GA）设计 — 2026-09-23（用户授权，P3）

## 依据
- destbreso island-ga：搜索自己的 schedule 是护城河；但他 repo 的 reference
  executor 只有 27k、其私有 dispatcher 54k——**执行层是乘数且未公开**。
- 我们的执行层现成：41 条 route-replay + 反应层 + cover/advance/d27/herd，
  已在 kagsim 上验证。所以第一阶段不是 spec+compiler（要新建编译器），而是
  **"deltas-over-stream"表示**：对现有执行栈做融资安全的编辑，用岛屿 GA 搜。

## 三阶段
1. **Stage 1（本轮起）**：GA 搜"外层旋钮 + 覆盖表条目"组合：
   基因 = (cover 表候选条目取舍, 镜像门阈值, advance on/off, 条件竞速时界
   on/off, d27 hedge)。评估 = CRN 对 257 池的 screen 半集（同种子同座位同对手，
   配对胜率）；确认 = 另半集 + 86 最新败局 + 镜像块。
2. **Stage 2**：deltas-over-stream 市场编辑（shift/split/defer sell、hire 日
   调整），保持 financing 链（sell 永不移到其融资 buy 之后）。
3. **Stage 3（若前两段不够）**：spec+compiler 全新生产路线（重编译器）。

## 纪律（destbreso screen/confirm）
- 搜索集与确认集 DISJOINT；GA 只用 screen 集排名，赢家才上确认集。
- CRN：所有候选打同一批种子/座位/对手，逐局配对。
- 结束前用作者的方法复现 winner's curse：单种子 +11.3k 在 disjoint 上还回去
  大半——必须查这个缺口。
- 每轮搜索改动一个子系统优先（block crossover 保持 co-adaptation）。

## 交付判据（沿用 goal）
- 257 配对 ≥96%、最新败局无负 delta、镜像零退化、loader 打包，不提交。
