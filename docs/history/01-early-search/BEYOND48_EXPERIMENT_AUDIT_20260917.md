# Beyond-48 notebook 实验审计（2026-09-17）

审计对象：`customerUpload/kaggle/beyond-48-0-128-128-worlds-with-95-cis.ipynb`。

## 先给结论

这份 notebook 对市场机制和候选实现给出了可读的说明，但性能数字主要是作者在 Markdown 中自报的结果，文件本身没有保留扫参、对局、bootstrap 或官方 runner 的执行代码。因此当前可确认的是“候选实现确实包含这些规则”，不能从该文件独立确认 `48-0`、`128-0`、数量平台、horizon 最优点或置信区间。

## 文件中可以直接核对的内容

- Cell 0（Markdown 行 5–11）列出 24 seed/双座位、64 worlds、官方 runner 的结果；没有对应可执行结果生成代码。
- Cell 3 是唯一的说明性 runner cell。它只导入 `kaggle_environments.make` 并打印 `env.run(...)` 的示例文字；源代码没有真正调用 `make` 或 `run`。Notebook 输出也只有 OpenSpiel 加载信息。
- Cell 12 解压嵌入的 `main.py`、重建 tar、计算两个 SHA，并调用 `agent` 一次检查入口；它没有做任何对局。执行得到：`main.py` SHA `4757f3f5b28db8a2f4614bb08993a8a567a7d49bae1ac324fbcfbcc1af60e95e`，archive SHA `66ee4fd7a169c10c3a313c9696b96b8661be9eea691736d0ffaa7b1a71e66582`。
- Cell 13（Markdown 行 3–5）再次声称可按 step 145 标注 world、保留每个 world 的 unseen seed 并在 world 层 bootstrap，但实现和 seed/world 数据不随 notebook 提供。

## 嵌入源码的实现证据

从 Cell 12 解压后，源码为 `/tmp/beyond_main.py`（与 cell 中的 `main.py` SHA 一致）。

- 行 1–6：标注为 K0006，父源是 Ahmed V43，父源 SHA `919fc1d61050cd96f799979e49177ae3ac7bce98ec9835724238bea73f4a08ed`；此候选不是独立农场规划器，而是父 V43 加包装层。
- 行 14–27：`HORIZON = 24`、`OPEN_UNITS = 50`，通过 `_Horizons.get` 把父级至少 4-turn reservation 改为 24。
- 行 146–182：`frontload` 按 `SELL`、`BUY_PRODUCT`/wash sell、其它订单分组；先对原顺序和新顺序分别进行 `pressure=0` 与 `pressure=1` 的本地 `_simulate`，任何一边无法完全执行就放弃重排。
- 行 185–255：`advance_sales` 将未来两步（`LOOKAHEAD = 2`）的纯现金产品销售提前；保护第一笔销售，限制库存和订单上限，不能保证未来两个订单全部加入时仅截断 `extra` 并记录 `advance_declined_full`。
- 行 294–315：仅当 step 0 的父市场列表**完全等于** `_V43_OPENING` 时，才替换为 `[BUY_PRODUCT WHEAT 50, SELL WHEAT 50]`；之后调用 advance 与 frontload。该条件支持实现层面的“只改特定 opening”，不支持它在任意对手 opening 下都能触发。

## 性能数字和 bootstrap 的证据等级

### 数量扫描（Cell 7）

作者报告 `n=0,10,...,100`，并称 25–50 为平台、85+ 为自伤；样本写成“paired margin, 8 seeds × 2 seats”，对手是自己的 70-unit build。没有 seed、逐局 margin、胜负表、执行配置或置信区间。结果最多支持“在作者那组未披露的 16 局实验里观察到该形状”，不能外推到现有公开对手池。`n=70` 一栏写作 `base`，不是一个数值，表格无法重算差值。

### horizon 扫描（Cell 6）

作者报告 horizon 8/16/24/36/48 的胜负和 margin，但没有每项的样本数、对手版本、seed 或逐局数据。`24 is a genuine optimum` 是叙述性结论，至少需要在留出 seeds、多个行为 lineage 和当前公开 opponent 上复核。

### 四层 acceptance suite（Cell 9）

Tier 1 的 24 fixed seeds 明确是调参开发集，不能作为判断集；Tier 2 是作者自行构造的 open78/fast24/open70_h24 clone，属于针对性压力测试而非独立 opponent；Tier 3 的 64 worlds 把 ordered first-two-shops 作为簇，并在每簇取一个 `never-tuned` seed、双方座位各打一局。由于每个 world 内两局共享相同 shop world，128 局不能当作 128 个独立样本；world-level bootstrap 的方向是合理的，但缺 seed/world 映射、逐世界 margin、bootstrap 重采样方式，无法核算 `+2,087 [1,950,2,240]` 或 `+1,334 [1,327,1,342]`。

### 官方 runner 与 wrapper trap（Cell 10）

作者报告 wrapper opponent 因相对路径加载失败而 PASS，导致虚假的 `+167,366`；打包 single-file 后得到 `+1,328`，并声称与本地 `+1,333` 及 64-world `+1,334` 一致。这是很有价值的测试卫生提醒，但执行代码、stderr、实际 episode 记录没有保留，三数一致仍是作者自报。需要我们用 `get_last_callable`、fresh subprocess、单文件 opponent 和错误/慢步检查重新做一次。

## 可支持结论与限制

**可支持：** K0006 的归因和源码表明它从 V43 派生；包装层实际实现了 horizon=24、step-0 wheat round-trip 50、market front-loading、两步 sale advance；frontload 具有 solo/pressure 双模拟保护；archive 可被确定性重建且 SHA 可核对；作者意识到 wrapper 加载和模块泄漏会制造假结果。

**暂不能支持：** 市场规则描述在本 notebook 内的完整正确性；n=50 相对 n=70 的泛化收益；24 是跨 opponent 的真实最优；128-0、CI 下界和“最差 world 仍正”；持续 wheat funding 失败数字；官方 runner 0 errors/0 slow turns；这些都应被视为待复验报告，而不是当前验证证据。

## 建议的复核实验

冻结源码 SHA、正确 engine 和 seed manifest；按 shop-world 聚类但报告每个 world 的双座位 paired margin；对 `n∈{0,5,10,16,20,25,30,40,50,70,85,100}` 与 horizon `{4,8,16,24,36,48}` 在至少三个行为 lineage（V43/V45、Nathan、flex）上做留出 world 评估。每个配置同时跑单文件官方 runner 和 fresh subprocess 本地 runner，记录 action/order diff、失败订单、错误/慢步、逐局 margin，并以 world 为 bootstrap 单位。只有当机制方向在未调参 worlds 和多个 lineage 上同号，才把作者数字升级为可用于候选选择的证据。
