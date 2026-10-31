# Candidate: v54_stack_s1sd — 2026-09-22 探索全纪录（最新冠军）

## 一句话
V54 seedcut 底座 + Ahmed V56 的 E402（带 +2 小麦余量）/E410 + 运行时判别开局（o4）+
aurax7 frontload + day29 肥料闸 + shiiin9 Layer D（卖单槽位精确反排搜索），
是当前证据下最强的候选。s1s（无 Layer D）已上线。
**先不提交，等用户令。**

## 结构（自底向上）
1. V54 共享底座（路由/生产/时序 + 喂食安全层 + pairgate 五层 + seedcut）
2. E402 智能种子节流（step≥624 只砍超出剩余 PLANT 需求的 BUY_SEED，+2 小麦余量）
3. E410 肥料无益跳过（_ca_yield_path 模拟不增产则 FERTILIZE→PASS）
4. o4 判别开局：step1 对手现金 ≥2950（aurax7 家族签名）才加
   [SELL WHEAT 13, BUY_PRODUCT WHEAT 5] 前缀
5. frontload（A/B/C 卖单重排 + 单机现金流安全模拟）
6. day29 停买肥料（busyaprime seed-leak 情报：末日肥料无作物可助）
7. Layer D（shiiin9 订单簿：≤800 种卖单槽位排列，用 _v44y_factor_margin 精确打分
   选最优反排）——frontload 的严格超集，全面正收益。
V9_RACE_DEFAULT 保持 40（41 实测判负）。

## 实测护栏（全部通过）
| 指标 | base(seedcut) | s1f | **s1s** |
|---|---|---|---|
| live 全矩阵 56 agent×64 世界 | 78.4%/+1969 | 92.4%/+2839 | **93.4%/+2916** |
| 257 局扩池（kagsim） | — | 92.4%*(s1s vs base 80.0%) | **85.5% vs base 80.0%** |
| live vs aurax7-v7 | 40.6%/-57 | 97.7%/+4015 | 97.7%/+4068 |
| live vs v53 | 65.6%/+357 | 85.2%/+741 | 85.2%/+744 |
| live vs v56 | 34.4%/-176 | 54.0%/+182 | **56.2%/+186** |
| live vs 2945 | 93.8%/+1672 | 96.1%/+2022 | 96.1%/+2006 |
| live vs koshinm-0921 | 50.4% | 75.8%/+599 | 75.8%/+599 |
| 镜像 | — | +0.0 | +0.0 |

## 关键发现链（详见 V53_PREDICT_RESEARCH 第四十五至四十八轮）
- 修正 arena loader 后：唯一真缺口 = aurax7 家族（63.3% 打我们），且差距按世界极化，
  路由字节却完全相同。
- 根因 = step1 开局微观结构：我们 step1 不报价，aurax7 家族 [SELL13, BUY5] 抢指数 0。
- 判别器：对手 step1 现金 3014（对倒）vs 2854-2867（净买麦），阈值 2950。
- 冻结磁带 vs live 矛盾：4 个翻转局原种子 live 打 aurax7-v7 全赢，冻结为伪影。
- V56 = 共享底座 + V9 41 + E402 + E410（V92 blob 仅编码差异）。
- frontload +v53 13pp；advance_sales 判负；kosh sell_impact_reorder live 微正但
  池 88.4% 判负；YARN+FM 大败 = 座位镜像掷硬币（期望中性）。
- busyaprime 72/96 时界 fork 独立印证 V9=40 平衡点；day27 seed-leak 与 E402 同源，
  其 +2 余量与 day29 肥料闸已采纳。

## 归档
- candidate_v54_stack_s1sd.tar.gz（main.py sha256 a7f4a26d...；官方 loader 验证
  拾取 `_cxd_agent` 全流水线）。
- 未提交。等用户令。
