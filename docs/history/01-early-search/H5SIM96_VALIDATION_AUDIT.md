# H5SIM96 本地验证证据审计

审计对象为 submission 56185929 的本地候选，不修改生产代码或提交包，不执行提交。审计时间：2026-09-12 UTC。

## 结论

已有证据支持“这个改动善于击败冻结 V37”，不支持“对线上整体对手分布显著强于 V37”。旧报告存在 seed 范围写错、混用不同阈值的结果、将历史败局的 seed 对战误解释成原败局修复，以及未真实检查 stderr 等问题。以下是实际文件能证明的内容。

## 产物一致性

- V37 `public_v37_pkg/main.py` SHA-256：`94c1c2c05ae7cde8fca9ee3957b01112c1cbab82c7434aae6a5f24fa7485bc4c`。
- H5SIM96 `candidate_v37_h5sim96_pkg/main.py` SHA-256：`ba08548ba46b3f6dda6dffc716aa1402fcfc75c69238e53a291fb04f07f463b4`。
- H5SIM96 archive SHA-256：`634e3fe26c72d83c5b9e3187bf793361f24993b40b26233fb506e37a12e7048d`。
- 两个 archive（`public_v37_candidate_replay.tar.gz`、`candidate_v37_h5sim96.tar.gz`）都只有根目录 `main.py`，提取内容 SHA 与对应源文件完全相符。未发现打包内容错配。
- 唯一源差异在候选第 1878–1879 行：288 <= step < 696 时，`step < 648 and _r37_similarity(observation) >= 0.96` 才将 horizon 从 4 改成 5。
- `_r37_similarity`（第 1750 行）比较双方公开农场中同位置的 crop/animal 类型与解锁地块；不比较对手 shed、销售意图、市场订单、yield 或农作物年龄。因此布局相似不等于销售策略相同。

## 原始验证结果及错误

| 原始脚本 / 输出 | 实际候选 | 对手与样本 | 可确认结果 |
|---|---|---|---|
| `/tmp/h5sim96.py`、`/tmp/h5sim96.out` | H5SIM96，阈值 0.96 | 冻结 V37；9001–9010 + 1495252849，共 11 seed × 双 seat = 22 局 | 22 胜；mean +2218.9545；min +740 |
| 同上 | H5SIM96，阈值 0.96 | `ready_thomas_v6/main.py`；9001–9010，共 10 seed × 双 seat = 20 局 | 19 胜 1 负；mean +6272.6；min −556（9004，seat 1） |
| `/tmp/real_loss_panel.py`、`/tmp/real_loss_panel.out` | H5SIM96，阈值 0.96 | 冻结 V37；15 个历史线上败局 seed × 双 seat = 30 局 | 30 胜；mean +2390.8667；min +443 |
| `/tmp/h5sim_panel.py`、`/tmp/h5sim.out` | H5SIM，阈值 **0.90** | V37、Thomas、Flex、Dmitrii；22 + 20 + 20 + 20 = 82 局 | Flex 20 胜 mean +5048.8；Dmitrii 20 胜 mean +6396.95；这些是 0.90 的结果 |
| `/tmp/h5pre_panel.py` | H5PRE，无相似度门控 | V37；9001–9010 + 1495252849，共 22 局 | 脚本直接把 `stderr` 字段写死为 `False` |

`CANDIDATE_V37_H5SIM_REPORT.md` 第 13 行的“9001–9020 plus 1495252849，双 seat，22 局”是算术与原脚本都不相符的错误；正确为 **9001–9010**，11 个 seed。若真是 9001–9020 + 1，应有 42 局。

该报告第 15、19 行 Flex / Dmitrii 数字精确来自 `/tmp/h5sim.out` 的 **0.90** 版本，`/tmp/h5sim96.py` 实际只重新测 V37、Thomas。未找到针对最终 **0.96** 版本完整重跑 Flex / Dmitrii 的证据，因此不能将它们直接标作最终提交结果。

多个脚本均写入 `h5sim_<opponent>.json`，文件名未含候选版本或 SHA，后续版本可覆盖前版。当前 `h5sim_public_v37_pkg.json` 与 `h5sim_ready_thomas_v6.json` 来自 0.96；Flex / Dmitrii 的同名前缀 JSON 仍来自 0.90。`/tmp/h5sim99.py` 也使用同样输出命名，但现有 `.out` 只有 7 场 seat 0 输出，没有完成 summary，不能当完整 0.99 面板。

历史败局 seed 为 `1570771565, 606276766, 1170850889, 1048630715, 838513485, 594403442, 1588330040, 1946300122, 679420063, 1946686316, 1634969403, 489957635, 1670179817, 1609194636, 86191952`。该实验只复用环境随机 seed，**将真正的线上对手替换为冻结 V37**；因此它没有证明击败原线上对手，更没有证明修复这些真实败局。

## 统计与外推限制

这些 `margin` 都是“候选最终资金减对手最终资金”，不是“候选相对 V37 对同一第三方对手的改善”。平均多赢一个弱对手几千资金不能直接映射为 Kaggle rating 增益。V37 原本对这些公开对手的胜率已很高，需固定对手版本、seed、seat 配对比较 V37 与候选的胜负转换及资金差变化。

22 局 V37 面板中 10/11 个 seed 双 seat 资金差完全相同；历史 seed 面板中 14/15 完全相同。因此“52 场赢 V37”是 26 个环境 seed 的双 seat 覆盖，不是 52 个独立对手或 52 个独立环境。双 seat 有价值，但不能当独立抽样估计全局胜率。

## 程序隔离、日志与环境

脚本每场为双方重新执行 `importlib.util.module_from_spec` + `exec_module`，命名不同，不共享候选模块的全局字典。本次动态检查确认双方 `agent`、`Chassis`、`_IMPL`、`_UNIT_NS`、`_R37_HORIZONS`、`_R44_REPORT`、`_V231_STATES`、chassis players/routes 都是不同对象；覆写的 `Chassis._sell_lead` 绑定各自模块 globals。未发现共享 policy 状态污染。

它们确实在同一个 Python 进程里执行，未做独立进程和 Kaggle 容器级隔离。为验证这个疑点，本次对 seed 9005 重跑：独立 module 命名空间与两个独立常驻子进程结果完全一致，H5SIM96 117318 对 V37 116578（+740）；双方 DONE、720 steps、stderr 0。证据：`experiments/h5_namespace_smoke.json`、`experiments/h5_process_smoke.json`、复现脚本 `experiments/h5_process_smoke.py`。这排除了该样本的进程隔离差异，不能推广成全体容器等价证明。

旧面板只存 `done` 和 `steps`，未扫描 `e.logs`、未保存每 agent 最终 status 或耗时。`debug=False` 时 Kaggle framework 会捕获 stdout/stderr 到内部日志，外部 `.out` 没有异常不等于内部 stderr 为零。`/tmp/h5pre_panel.py` 甚至将 `stderr=False` 写死。因此旧报告“所有对局无 stderr”缺乏记录支持；720 steps 与 env.done 为真也不是完整 runtime 审计。

当前系统 Python 框架元数据为 `kaggle_environments.__version__ = 1.25.9`，加载路径 `/root/miniconda3/lib/python3.10/site-packages/kaggle_environments/__init__.py`。CLI 专用 Python 没有安装 kaggle_environments。实际 `make('kaggriculture')` interpreter 加载 `/root/miniconda3/lib/python3.10/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`，SHA-256 为 `bc8a54879ef02c7ea64b8b333d6a976f0ea65c4949149d01f463f23bccee653e`，与 agent 内标注的 1.32.7 原始机制 SHA 完全相符。**不能只凭 framework 的 1.25.9 版本号断言本地游戏机制过旧**；本机显然混合了较早 framework 元数据与较新的 Kaggriculture 模块。上游独立核对结果另存 `experiments/h5_engine_version_audit.json`（记录于 `experiments/h5_engine_version_audit.json`；上游抓取因网络超时未完成）。

实际配置保留指定 seed 于 `env.info['seed']` 并将 `configuration.seed` 清空；本次检验 seed 9001 正常生效。独立 RNG 按 seed/day 生成杂草和商店；未发现面板传 seed 被忽略。

## 下一轮应采用的验证

冻结候选与每个对手的 SHA，结果名包含版本；使用真正未参与阈值选择的 seed 和不同销售风格的强对手，固定 seed/seat 做 `V37 vs O` 与 `candidate vs O` 的配对比较。对真实 replay 做行为机制对照，明确区分“原对手响应策略可运行”与“只回放记录动作”。保存最终 status、异常日志、耗时、每局收益与 action/replay；强制结果绑定源 SHA、环境机制 SHA 与配置。先承认旧验证只证明局部克制，再检验是否存在全局提升。
