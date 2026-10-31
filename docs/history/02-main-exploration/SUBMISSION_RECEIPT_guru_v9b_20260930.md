# 提交回执：`cand_guru_v9b_prun.tar.gz`（ref **56676198**）

**提交时间**：2026-09-29 13:01:09 UTC（北京 21:01）
**提交命令**：`kaggle competitions submit kaggriculture -f cand_guru_v9b_prun.tar.gz -m "cand_guru_v9b_prun (GURU new lineage): v8b+D27+s793+PRUN. cur163 clean 52.3% mean+5116; pool 105/63 (+1 win); holdout 342/39; smoke 88773"`
**状态**：`SubmissionStatus.PENDING`（首个可读均值点 ≈ UTC 19:01 / 北京 03:01，按"4h 稳定 + 前推 2h"口径）
**今日配额**：提交后剩 **3 发**

## 包信息

| 项 | 值 |
|---|---|
| tar sha256 | `3c44ae8c49aeb396a51a5a368bba8a83e57459e24ba5cd59e4b4b54c0208c894` |
| smoke | 88,773（双 DONE）、entry=`kaggle_entry`、打包=调参版对拍一致 |
| 谱系 | GURU master-engine-v3 → v1…v8（frontload 移植）→ v8b（f29+s752）→ **v9b（+D27+s793+PRUN）** |

## 队列（FIFO）

* 提交前：56663288（snk6_cam30，2138.4）+ 56649573（slh48，2317.3）
* 本次 56676198 入队 ⇒ 顶掉最老的 **56649573**（slh48）
* 现两槽 = 56676198（PENDING）+ 56663288（2138.4）

## 本轮提交依据（本地全证据）

* **cur163（最新 meta 直尺）**：干净口径 **105/58（64.4% raw、逐位对比旧血统最强 83/80）**、
  mean +5,249；对照：snk6_cam30 83/80、−1,931。
* pool 168：**105/63**（+1 胜 vs v8b）；holdout 381：342/39（−1 胜，ep114654807 回吐）；
  七面板综合：v8 代全绿、v9b 净 +1 胜、margin 全正。
* 机制：GURU 编译器 + 我们全部移植/自研层（镜像门、midband 准镜像带、OR2K/SLOT_H 家族门、
  机会主义 CARE/COLLECT、`_ax_frontload`、f29、s752、D27 天花板、s793 槽位重排、PRUN 剪枝）。

## 评估计划

* 等 PENDING→COMPLETE 后按 6h 均值口径读数（北京 03:01 左右首读）；
* 若爬分曲线明显优于 56663288（snk6 系）同期，则新血统路线继续加码；
  否则回退旧血统为主、GURU 线留档。
