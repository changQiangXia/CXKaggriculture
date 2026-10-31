# jaxa623 `Beyond 48-0` 样本研究（2026-09-17）

## 样本身份与复原

Notebook：`jaxa623/beyond-48-0-128-128-worlds-with-95-cis`，本地拉取文件位于 `jaxa623_beyond48/`。

精确复原的候选：

- `jaxa623_beyond48/k0006_main.py`
- main SHA-256 `4757f3f5b28db8a2f4614bb08993a8a567a7d49bae1ac324fbcfbcc1af60e95e`
- archive SHA-256 `66ee4fd7a169c10c3a313c9696b96b8661be9eea691736d0ffaa7b1a71e66582`

它内嵌的是 Ahmed V43 raw parent，SHA `919fc1d...f4a08ed`，不是我们当前冻结的 V43 optimized SHA `38f65166...43a3bd`，也不是 V45 的 parent。故它属于 V37/V43 同一 lineage 的独立 wrapper 研究，不是完全独立的第四种农场模型。

## 它真正研究的机制

样本把四个新增 edge 都限制在 market 层，完全保留 parent farm plan：

1. **front-loading**：把非 wash-trade 的 SELL 放到 market list 前面，把 BUY_PRODUCT 和 wash SELL 保持在中间，其他订单放后面；只有对原列表和重排列表都做 per-unit solo/pressure simulation 且都能完整执行时才重排。它不主动改变数量。
2. **two-turn sale advance**：查看 parent tape 接下来两步的纯现金商品 SELL，把当前 shed 中已经存在的数量提前卖；不提前 WHEAT/FERTILIZER/seed/animal，并避开 dawn turn。若 order slots 不足，记录 decline。
3. **reservation horizon=24**：通过 `_Horizons.get()` 覆盖 parent 288–696 区间原有 4 步 reservation。它明确承认过长 horizon 会承诺尚未收获的产物，因此做了 sweep。
4. **step-0 wheat round trip=50**：把 `[BUY 5, BUY 10, SELL 60]` 改成 `[BUY 50, SELL 50]`。作者认为 70 位于 plateau 的远肩，50 在破坏对手 day-0 funding 后更安全。

关键思想比某个数字更有用：market list index 是双方共享的竞争资源；销售顺序必须以“原订单与重排订单都能实际执行”为安全门；step-0 机制的目标不是赚钱，而是破坏对手没有现金余量的后续采购。

## 作者公开的实验信息

Notebook 报告：

- 24 seeds × 双 seat 对 V45：48-0，+2,384；
- 对 V44/V43：47-1 / 48-0；
- 自建 stress clone：48-0、47-1、48-0；
- 64 independent worlds × 双 seat 对 V45：128-0，paired +2,087，world bootstrap CI [+1,950,+2,240]；
- 公开 sweep 认为 horizon 24 优于 8/16/48；step-0 round trip 的 25–50 区间形成平台，70 是平台远肩，85+ 开始自伤；
- 反复攻击 wheat feed（每局 26–28 次）失败：30 单位 0-16，50 单位 2-14；说明 day-0 funding attack 不能推广成全季涨价攻击；
- sheep↔cow、feed sweeper、route reselection、seed recovery 等失败实验被公开列出。

这些实验叙述比只公布一个 16-0 更可信，因为包含了失败样本和 self-counter。但原始 world seed manifest、逐局 ledger、完整对手源码和独立复算脚本没有随 notebook 提供，所以 CI 和 128-0 仍属于作者报告，不能直接当作我们已复核的证据。

## 我们的独立本地结果

使用正确 `get_last_callable` 和本机 1.32.7 对 720-step 完整局运行 K0006，父版本取其内嵌 raw V43；对手是本地冻结 V45、V43 optimized、corrected Nathan 和 flex，各 2 seeds、双 seat。结果保存在 `jaxa623_beyond48/k0006_panel_4x2.json`。

候选相对其 raw V43 parent 的 paired margin delta：

| 对手 | 场数 | 平均 delta | 改善/变差 | 最差 |
|---|---:|---:|---:|---:|
| competitive V45 | 4 | +1,367.5 | 2/2 | −3,044 |
| V43 optimized | 4 | +967.0 | 3/1 | −395 |
| corrected Nathan | 4 | +610.5 | 3/1 | −219 |
| flex | 4 | **−19,301.0** | 0/4 | **−23,113** |

这些不是 confirm 结果，seed 很少；但 flex 上连续 4 场严重退化足以说明 K0006 不是跨架构通用增强。候选自身对 flex 仍可能取得正 margin，但相对 parent 的损失很大，表明优化改变了强动态对手下的竞争适配，而不是单纯提升农场经济。

## 对评估方法的启发

作者的两个 trap 对我们尤其重要：

- wrapper 对手相对路径加载失败会变成 PASS agent，造成虚假的 +167,366；必须始终用提交包的单文件和官方 `get_last_callable` 入口审计。
- 长 sweep 在同一 Python 进程中加载 wrapper 会造成 `sys.modules`/内存污染；需要真正 subprocess 或清理所有非基线模块。我们原有 strict evaluator 直接 importlib 读取 `mod.agent`，不能视为线上等价 loader。

作者把 world 定义为前两次 shop 的有序 pair，再对 world 聚类 bootstrap。这个思路值得吸收，但不能把两个 seat 当两个独立 world；world label 只是一种方差分层，不能替代完整 seed manifest。

## 当前分类与后续使用

K0006 加入研究阵营，但标签应为：

- lineage：Ahmed V43 raw；
- mechanism：market-index frontload + sale advance + horizon24 + opening50；
- target stratum：同 route / 同 market-order 家族；
- risk stratum：dynamic/flex/不同 opening。

它最适合用来生成“竞争性市场微机制”的候选，而不是直接作为新的农场 baseline。我们自己的下一步应先抽取其 frontload 的两个安全思想：

1. 不删除、不新增、不 resize 订单；
2. 原列表和重排列表必须在单方及压力模拟下完整执行。

再把它们改写为我们自己的、可审计的 wrapper，并在 V45、Nathan、V43 同 lineage 与 flex/Thomas/Dmitrii 异构族之间分层验证。horizon24 和 opening50 不能直接合并，必须分别做机制消融；任何候选先过 pilot，再做时间外 confirm。
