# 提交收据：cand_h120ch99_y2_mid112_t — 2026-09-27

| 项 | 值 |
|---|---|
| ref | **56595871** |
| T0 (UTC) | 2026-09-27 02:54:12 |
| 包 | `cand_h120ch99_y2_mid112_t.tar.gz`（627,xxx B，单 `main.py`） |
| tar sha256 | `d6115fb1a6058c04338eff95fa7449c8d5aead7948dae4453ba75a51f967c891` |
| main.py sha256 | `2a0c343dbfa42ba8aa53ec0125660457eb968e8a87b5ae947f02e795bd3138fa` |
| CLI | `Successfully submitted to Kaggriculture`；今日剩 3 次 |
| 官方引擎 | seed1/seed2 **exact=true** |

## 这是什么

`h120ch99_y2` + **day-12 中盘换路**：
* 默认 112；
* **该底座自己拟合的 11 格例外表**（BRUNCH+FARMERS→103、PIZZA+SMOOTHIE→124、BAKERY+BRUNCH→103、
  YARN+YARN→120、PET_CAFE+PIZZA→103、YARN+FARMERS→2、PET_CAFE+YARN→2、BAKERY+YARN→2、
  SMOOTHIE+BAKERY→120、YARN+PIZZA→2、BAKERY+FARMERS→103），CV +4.0~4.3 胜（比 am 版的 +2.5~3.0 更强）。

## 判据

| 判据 | 结果 |
|---|---|
| ① 胜局不劣化 | 570 局 **467 → 492（+25）**；L→W 29、W→L 4 |
| ② 均值显著为正 | **Δmean +423，t=+9.26**（败局段 +490/t=5.76；胜局段 +387/t=7.26） |
| ③ 稳健性 | 例外表 CV 10/10 次为正；112 部分 5/5 时期为正、200/200 半样本为正（同规则在六底座全部迁移） |
| 静态门 | 0925 +443.5（t=4.20）、0924 +392.7（t=3.21），均 100% 胜；加表后 −8.0 / −4.2（平，无劣化） |

## 为什么选这个底座（与 am_y2_mid112 的对冲）

同龄口径（T0+4h→6h 的 2h 均值）：**h120ch99 2660.2 > am_y2 2434.1（+226 分）**，
而 570 局语料上 am_y2（476）> h120ch99_y2（467）——两个口径排序相反，故两发各押一边。

## 读分口径

* **最早干净 2h 均值读数 = T0+6h = 2026-09-27 08:54 UTC（北京 16:54）**。
* 天梯显示 = 最近两次提交较高者 = max(`56595299 am_y2_mid112`, `56595871 h99t`)。
