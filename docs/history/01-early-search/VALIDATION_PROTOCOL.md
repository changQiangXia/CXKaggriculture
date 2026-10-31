# 两个候选的验证记录

本轮以 `public_v37_pkg/main.py` 为父策略，遵循 `RESEARCH_CRITERIA.md`。每个候选只改变 `_R37_HORIZONS` 的相似度门槛，使用同 seed、同 seat、同 opponent 的 paired 对局；每局 720 steps，要求 `DONE` 且无 stderr。

## 分层数据

- screening：9001–9010 双 seat，对 v37、Flex、Thomas、Dmitrii。
- confirmation：9001–9020 加 1495252849、70117、184901、184902、20260907、451781128 的历史归档结果。
- real-loss holdout：从 v37 线上 loss 提取的 15 个 seed，双 seat；只用于已完成候选的独立回放核验。

候选规则冻结后不得根据 confirmation/holdout 回调阈值。固定 tape 只用于 action-level 机制诊断；强对手交互式对局才用于策略晋级。

## 当前判定

候选池当前保留 h5sim96 与 h5sim95 两个 v37 派生版本。旧 Thomas 面板分别有 `-556`/`-582`，旧 Flex/Dmitrii 文件来自其它阈值或缺少运行时元数据，不能作为确认。当前运行新的 `run_serial_resumable.py`：它对 h5sim96 与 h5sim95 执行 candidate-vs-v37 配对、同 seed/seat/opponent、记录 status/stderr/max_duration 和 SHA。h5roomlow 已因 seed 70117 的 `-4` paired 反例和 2.60s runtime 降级为失败档案。只有 h5sim96/h5sim95 的新审计及后续 confirmation/holdout 完成后才更新晋级状态。
