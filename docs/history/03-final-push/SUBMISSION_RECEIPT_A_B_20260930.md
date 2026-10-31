# 提交回执：cam30 重交 + tl_gate2（线上 A/B，2026-09-29 19:17 UTC）

## 56685648 — `cand_snk6_cam30.tar.gz`（重交，A/B 对照）

* 提交时间：**2026-09-29 19:17:01.633 UTC**（北京 09-30 03:17）
* tar sha256 `c278a0671963bffb084840cc3a4141fc7caac7ddc9859e081a8722a4750bd9a2`
* main.py sha256 `25e00db7e23e1074a0922363106ad1235c22ca9fc5acb4e1c20a7196aa51ac3e`
* smoke 89,675 双 DONE；状态 PENDING → 完成后进入队列
* 与旧槽 56663288 同代码；重交目的是把它变成"较新槽"，让第二发顶掉最老的 guru 槽

## 56685653 — `cand_snk6_tl_gate2.tar.gz`

* 提交时间：**2026-09-29 19:17:13.703 UTC**（北京 09-30 03:17）
* tar sha256 `1a6c01b0d3d1a0c4ce3bbf14bb2dc4ee3bccb5a4338a1e12f4361642d43dc570`
* main.py sha256 `493fe5352d55fbcea58ec4e1dcfafad7ba0b93b217c1d9b02a90c0443b33d68d`
* smoke 89,471 双 DONE；状态 PENDING
* 本地五池证据（vs cam30）：cam30 112 局 raw +7 / clean +5；cur163 +23/+10；
  nem14 +8/+3；georgy arena +5/+2；fresh62 −3/−1；去重 762 局 raw +39 / clean +19

## 队列效果

原队列（旧→新）：56663288（cam30，2198.2）+ 56676198（guru v9b，1605.4）。
两发之后：**56685648（cam30）+ 56685653（gate2）** 成为两个活跃槽，
旧的 cam30 与 guru 槽被顶掉。今日剩余配额 **1 发**。

## 观察口径

* 4 小时到平台期；第一次可信均值取提交后 6 小时的"前 2 小时均值"；
* 重点看：两槽的分差随时间变化（同池 A/B），以及 gate2 在 <1600 段是否出现低分翻车。
