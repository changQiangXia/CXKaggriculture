# 再发掘的三个潜在机制（2026-09-19，第二批）

全部来自 kaggle_environments 源码的精确规则，且与前一批（锁步配对、相位
偏移、供给预测）不重复。前一批的验证结论：nosf（配对探测）负、anticipate
（供给预测）无效、RACEPX lead 0/2 负——timed174 仍是最稳。

## 机制 4：动物肥料的免费产链全量收集

**规则依据**（`_daily_refresh_animals` 第 831 行）：
`tile["fertilizer_available"] = True` 每天**无条件**执行——每只存活动物每天
免费产出 1 个肥料（市场 base 价 100），只要 worker 走到动物身边
`COLLECT_FERTILIZER` 就能拿走，**零成本、零投入**。

**现状量化**（timed174 mirror 局 seed 302401）：单方 17 只动物，实际收集
~186 次/局，按平均存活 20 天估算理论产量 ~340——**收集率约 55%**，每天浪费
~8 个免费肥料。若提到 90%，每局多 ~120 肥料 × (50~100) = **+6k~12k 收入**。

**机制**：提高收集频率（空闲 worker 就近收集），代价是走路时间挤占
浇水/收获/喂食。这是一个"劳动重排"优化：把 tape 里低价值的 PASS/低效移动
换成就近的 COLLECT_FERTILIZER。

**验证**：改 tape 或加 wrapper 提高收集频率 → 镜像局 + 313 池，看收入是否
净增（收集收益 vs 挤占生产损失）。

## 机制 5：CARE bonus 的生产日对齐

**规则依据**（`_daily_refresh_animals` 第 822-827 行）：
- `cared_today and fed_today` → `pending_care_bonus += 1`（每天 +1，无上限）。
- 生产日（`days_since_first % interval == 0`）：`bonus = pop(pending_care_bonus)
  if fed_today else 0`——**bonus 只在"喂了的生产日"消费**；若该天没喂，
  bonus 被下一行无条件清 0，**永久丢失**。

**机制**：把 CARE 的节奏与动物 interval 精确对齐——GOOSE（interval 1）每天
产，每天 fed+CARE 即可每天 +1 蛋；COW（interval 2）/SHEEP（interval 3）的
CARE 要在生产日前一天给（保证生产日 bonus 已累积）。同时确保生产日当天
必喂（否则丢 bonus 且连续不喂 2 天动物逃跑）。

**验证**：镜像局无差异（双方同 tape），真实池 vs 节奏差的对手；或改 tape
的 CARE 计划后看动物产出量是否上升。

## 机制 6：ongoing 作物的生命周期排程（草莓/番茄）

**规则依据**（`_daily_refresh_plants` 第 788-798 行）：
ongoing 作物（草莓 interval 2、番茄 interval 1）产量在
`production_count == max_yield` 时设置 `max_lifespan_step`——**草莓产满 4 单位
（约第 8 天）后必死变 weed**；HARVEST 只清 `yield_units`，不重置
`production_count`，所以生命周期不可延长。

**机制**：草莓的完整生命周期 = 8 天产 4 单位，之后浪费。排程两个维度：
(1) 种植日错峰，让收获窗口不重叠、worker 不拥堵；(2) 在 lifespan 到期前的
最后一次收获后立即 DIG 重新种植，不浪费"死亡格"的空窗。

**验证**：镜像局 + 池子；检查当前 tape 的草莓死亡格空窗时长，量化可回收的
产量。

## 优先级

4 > 5 > 6。机制 4 有明确的收入缺口（+6k~12k/局）且零风险（只是劳动重排），
最值得先做。
