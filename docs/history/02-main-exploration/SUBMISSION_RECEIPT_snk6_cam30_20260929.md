# 提交回执：`cand_snk6_cam30.tar.gz`（ref **56663288**）

**提交时间**：2026-09-29 04:59:32 UTC（北京 12:59:32）
**提交命令**：`kaggle competitions submit kaggriculture -f cand_snk6_cam30.tar.gz -m "cand_snk6_cam30 CA_FROM=8 SN_K=6 CAM=-30"`
**状态**：`SubmissionStatus.PENDING`（T0+6h 读分点 ≈ 2026-09-29 10:59 UTC / 北京 18:59）
**今日配额**：提交后剩 **4 发**

| 项 | 值 |
|---|---|
| tar sha256 | `c278a0671963bffb084840cc3a4141fc7caac7ddc9859e081a8722a4750bd9a2` |
| main.py sha256 | `25e00db7e23e1074a0922363106ad1235c22ca9fc5acb4e1c20a7196aa51ac3e` |
| 官方 smoke | 89,675（门槛 50,000）statuses `['DONE','DONE']` |
| 交前校验 | tar 内仅 `main.py`；`kaggle_entry` OK；包内 main.py 与评测文件 sha 逐位一致 |

## 槽位变化

* 原两槽：**56649573**（cand_slh48，public 2340.3）+ **56641864**（rmax96 rerun，public 2338.8）；
* 新提交 **56663288** 顶掉最老的 **56641864** ⇒ 现两槽 = 56663288（PENDING）+ 56649573（2340.3）。

## 本地证据（提交依据）

* **当前对手池面板（163 局，双方 ≥2300，fid≥0.95）**：slh48 69W/94L（42.3%）→ 本候选 **83W/80L（50.9%）**；
  拆 ref：56649573 面板 +5（35/35）、56641864 面板 +10（48/45）。
* 旧面板：global719 **599W/120L**（+8）、v4family546 **488W/58L**（+11）、b1600_2000 **211W/19L**（+3）、
  live92/tier167 持平、<1600 原始持平。
* 闭环 gauntlet（24 世界×2 座）vs slh48：**16W/16L，均值 +23**（不劣）；对公开 2945农场 24-0、Metav4 20-4、tetsutani 24-0。
* 机制（遥测实证）：CARROT2 互换 16.4→22.5 次/局（麦 −5.9 格 / 萝卜 +5.9 格，收获 −19.8/+18.0 件）；
  OR2 抢先卖 −13 件/局；增益为阈值形态（16 次 L→W vs 2 次 W→L）。

**下一发**：等 PENDING→COMPLETE 后按 6h 均值口径评估；本候选与 56649573 的对局可增量拉取用于更新"当前池"面板。
