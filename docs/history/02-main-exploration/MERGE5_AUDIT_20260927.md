# 合体候选（merge5）漏洞审计 — 2026-09-27

对象：`panel_arms/gate/merge5.py` = `pkg_merge5/main.py`（两者 byte-identical，1,079,676 B），
包 `cand_merge5.tar.gz`。审计工具：`audit_undefined_globals.py`（symtable 静态未定义全局名）、
`audit_merge_structure.py splice|stack|freeze`（拼接重建 / 层栈 / 导入期冻结）、
`verify_arm_telemetry.py`（本地 rust 引擎逐局 telemetry）。

## TL;DR

1. **确证漏洞（致命、静默）**：`_RUN_CFG` 未定义 → D27 层 100% 抛 `NameError` 被 `except` 吞掉，
   整层从不生效（seed 23：`d27_errors=135, d27_turns=0`；archplus 同局为 `0 / 1`）。已修（`pkg_merge5fix`）。
2. **结构性遗漏（比 1 更重要）**：merge5 只从 archplus 拷了**尾部 220 行**，丢掉 archplus 相对 s1sd 的
   另外 3 处机制改动（窗口期囤货 hold、开盘序列 R42、六羊防逃 herd-fix）。**"五合一"实际只合了 2.5 层**：
   `room_guard` + `D27`（死的）+ `DB`（低频）。
3. 已构造**真·超集** `pkg_merge6` = archplus（唯一同时携带 hold/R42/herd-fix/D27/DB 的臂）+ s1sd 的 6 个常数。
   官方引擎 seed1/2 **exact=true**。
4. 其他类缺陷已逐项排除：39 个候选文件里只有 merge5/merge_revert 有未定义全局名；7 个常数无导入期冻结；
   入口封口（`agent = globals().pop('agent')`）与官方 `get_last_callable` 语义一致；`cfg` 改写是每步读取，真实生效。

## 1. 拼接方式（逐行证明）

`audit_merge_structure.py splice pkg_s1sd/main.py pkg_merge5/main.py pkg_archplus/main.py`：

```
common prefix with pkg_s1sd/main.py :  7990 lines
common suffix with pkg_archplus     :   220 lines
merged lines: 8237 ; unreconciled middle: 27 lines (7991-8017)
```

即 `merge5 = s1sd 全文 + 27 行手写块（簇A常数 + roomguard 使能/包装）+ archplus[8045:8264]（D27 + DB + 封口）`。

`_RUN_CFG = {}` 位于 archplus **第 7056 行**（ER 层参数化钩子），落在 220 行拷贝窗口之外 →
尾部 `_d27_agent` 两处 `_RUN_CFG.get('hedge', _D27_HEDGE)`（merge5 8099/8139 行）必然 `NameError`。

## 2. 机制台账（按源码逐字节核对）

| 机制 | s1s | s1sd | snh48 | am | archplus | h120ch99 | **merge5** |
|---|---|---|---|---|---|---|---|
| 窗口期 hold（d25-29 抑制卖出，718 清算） | – | – | – | – | ✔ | ✔ | **–** |
| 开盘序列 R42 改写 | – | – | – | – | ✔ | ✔ | **–** |
| 六羊防逃 herd-fix（`at_risk` + day≥24 不塌缩单工） | – | – | – | – | ✔ | ✔ | **–** |
| D27 种子浮存修剪 | – | – | – | – | ✔ | ✔ | **✔（修前死）** |
| DB 黎明现金（低频） | – | – | – | – | ✔ | ✔ | ✔ |
| roomguard / dead_stock cfg 使能 | – | – | ✔ | ✔ | ✔ | ✔ | ✔ |
| `_RUN_CFG` 参数化 | – | – | – | – | ✔ | ✔ | **✘（缺定义）** |

⇒ archplus = s1sd + 6 处机制改动；**merge5 只继承了后 3 行**。此前的"层清单（26/27/29 层）"只统计了
入口重绑定次数，未统计这些**就地编辑型机制**，所以低估了差距。

## 3. 实机证据（seed 23 / 7 / 99，seat 0，被动对手）

| 臂 | d27_errors | d27_turns | 终局现金 | 备注 |
|---|---:|---:|---:|---|
| merge5（修前） | 135 / 133 / 135 | 0 | 200,926 | 每步抛异常 |
| merge5fix | 0 | 0（无需动作） | 200,926 | 层复活但本局无需裁剪 |
| merge6 | 0 | 1 | 200,926 | 与 archplus 同 |
| archplus | 0 | 1 | 200,926 | 基准 |
| s1sd | – | – | 200,573 | 无 D27 层 |

`_DB_REPORT` 在 **merge5 与 archplus 上同为静默**（被动世界无触发）⇒ DB 静默不是合体引入的 bug，
此前把它归因于 `_RUN_CFG` 是错的。

## 4. 静态审计覆盖面

* `audit_undefined_globals.py` 扫 32 个 `pkg_*/main.py` + 7 个线上臂（h120ch99/sloth80/idleharv/am/snh48/s1s/s1sd）：
  **只有 `pkg_merge5` 与 `pkg_revert` 报未定义全局名（均为 `_RUN_CFG`）**，线上提交过的臂全部干净。
* 导入期冻结检查：`_OR2_SN_H/K`、`_OR2_SLOT_H/MARGIN`、`_CA_MARGIN`、`_CA_FEED_DAYS` 在 merge5 中
  **无任何模块级读取**，尾部的重复赋值是安全的后置覆盖（不存在"赋值前被烘焙进冻结磁带"）。
* 官方加载器：`kaggle_environments/agent.py::get_last_callable` = 源码 `exec` 后取**字典最后一个 callable**，
  与尾部封口 `agent = globals().pop('agent')` 语义一致；`kaggle_submission_agent` 指向旧包装但排在 `agent` 之前，不影响选主。
* `room_guard`/`dead_stock` 在 `_SETTINGS`（951 行）中为 `False`，尾部改 `_IMPL.chassis.cfg[...] = True`，
  而消费点（492/496 行）在**每步**读 cfg ⇒ 真实生效。

## 5. 产物

| 文件 | 说明 | main.py sha256 | tar sha256 |
|---|---|---|---|
| `pkg_merge5fix/main.py` | merge5 + `_RUN_CFG = {}`（+6 行注释） | `f80c3260e13e…` | `66bb90a9ed16…` |
| `cand_merge5fix.tar.gz` | 已打包，官方 exact=true（seed1/2） | — | 同上 |
| `pkg_merge6/main.py` | archplus + 簇A常数（真·超集） | `bb4c5ec5a8bc…` | `fdbd29ed95ff…` |
| `cand_merge6.tar.gz` | 已打包，官方 exact=true（seed1/2） | — | 同上 |

（均为 **未提交** 状态，等用户批准。）

## 6. 本地对打（`panel_runs/tapes_ep0925.jsonl.gz`，120 局×双座=240 场/臂，6 workers）

```
s1sd      +151,439   archplus +151,362   merge5br +151,451
merge5fix +151,458   merge6   +151,458      （全部 100% 胜，池已饱和）
PAIRED merge5fix - merge5br :   +7.2  sd  12.1  t  -9.26
PAIRED merge5fix - s1sd     :  +19.2  sd  63.3  t  -4.71
PAIRED merge6    - merge5fix:   +0.0  sd 2848.0 t  -0.00
PAIRED merge6    - archplus :  +96.6  sd 5537.5 t  -0.27
```

结论：修复本身**可测且为正**（+7.2/局，t=−9.26），但量级极小；静态磁带池**无法分辨**
hold/herd-fix 这类只在特定对手行为下触发的机制（merge6 与 merge5fix 在这些局里逐计数器一致）。
⇒ 静态池只能当"不劣化门"，不能当选型依据；merge6 的价值是**结构完整性**（不丢已验证机制），不是本地增益。

## 7. 建议

1. 保底不变：s1sd / archplus（两次提交额度，需逐次批准）。
2. 若要用合体臂，用 **merge6**（真超集 + s1sd 常数），不要用 merge5fix —— 后者缺 hold/herd-fix；
   若担心 archplus 主干风险，可先用 merge5fix 做低风险对照，但它本质上 ≈ s1sd + roomguard。
3. 下一步的判别手段必须是**活体/动态**口径（同日参照系、4h/6h 同龄排名），静态磁带池没有分辨力。
