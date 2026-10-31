# 三篇公开帖复查（2026-09-27）— Idle Seller / Ice&Fire / God's mode

## 1. 更新状态（用载荷 SHA / 文件 SHA 逐字节核对）

| 帖子 | 结论 |
|---|---|
| **lynnsakurai / farmer-john-and-the-idle-seller** | **真更新：v57 → v59**。main.py 1,059,936 B（sha `1cb133e9…`）→ 868,890 B（sha `59a1ef9b…`） |
| leoprovorov / a-song-of-ice-and-fire-fixed-flexible | **agent 无变化**：新载荷 sha `12ad317ecac6c07f…` = 我们 09-24 已存的 `panel_arms/ref_song_icefire.py`（MarketShock-M1-WR1K） |
| leoprovorov / god-s-mode-hacked-stores | **无内容变化**：payload 四个文件（main/base_agent/shop_predictor/shop_overlay）SHA256 完全一致，只有 cell 顺序变了 |

## 2. v59 的增删（相对 v57）

**新增**：`_FF_*`（"Generalized composition: failure-atomic opening plus executable SELL closure"）
* `_ff_field_guard`：只服务于其自有的 `EarlyCycle` 备选开局（step 29 修 pasture、49-57 跳过期插入动作）→ 与我们 `HybridOpening` 不通用；
* `_ff_close_queue`：**通用**——把"0 执行"的现金品 SELL 置空，再把后面可执行的 SELL 前拉填洞
  （计数 `zeroed_orders / pulled_orders / pulled_slots`）。
* 常量改动：`_CA_FEED_DAYS` 1→2、`_OR2_SLOT_MARGIN` 20→50、`_SR_MARGIN` 8→4、`_SR_HOURS` (21,22,23)→(22,23)、`_ALT_MODE` HybridOpening→EarlyCycle。

**删除**：`_RACE_*`（race 克隆/丢赛/升级）、`_R127_*`（优先粮单）、`r36_reserve`。

## 3. 我们的栈 vs v59

| 机制 | 我们有？ | 在我们语料里的活性（576 局 sweep） |
|---|---|---|
| `_SR_*`（SHEDROOM 夜间溢出） | ✔ | sr_turns 883 / sr_units 5,035 |
| `_V92_P_*`（卖出预测库） | ✔ | pred_units 401,001 / pred_fires 90,118 |
| `_CXD_*`（订单簿精确重排） | ✔ | 2,819 次重排 / 增益 99,756 |
| `_RACE_*` | ✔ | **race 计数全 0**（只有共享的 cs_* 活）→ v59 删它有道理 |
| `_R127_*` | ✔ | priority_grain 全 0（只有 last_hour_plants_dropped 429） |
| **`_FF_*`** | **✘** | 见下 |

## 4. 实测：v59 的常量与机制在我们这里都不划算

（以 am_y2 为底，198 局硬语料配对）

| 变更 | 均值 | 胜率 | 配对 |
|---|---:|---:|---|
| `_OR2_SLOT_MARGIN` 8→50 | +3,575 | **63.6%** | −1.2 (t=−0.08) |
| `_SR_MARGIN` 8→4 | +3,570 | 62.6% | +4.7 (t=1.58) |
| `_SR_HOURS`→(22,23) | +3,572 | 62.6% | +2.5 (t=1.42) |
| `_CA_FEED_DAYS` 0→2 | +3,383 | 62.1% | **+191 (t=+4.57) 明显更差** |

**`_ff_close_queue` 头程探针**（`variants6/probe_ff.py`，240 局真实磁带，只计数不改行为）：
* 0 执行卖单 **12.2 个/局**（2,935 总），但**可前拉填洞仅 0.18 个/局**（40/240 局），槽位位移 0.39/局
⇒ "卖单收口"能改的东西约等于 0；我们的 `_CXD` 层已在做同类工作（3,091 万次评估）。

## 5. 结论

* 三篇里只有 Idle Seller 有真更新，且其**唯一可移植的新机制在我们身上没有头程**；其新旋钮值也都不适用于我们的血统。
* 我们已具备它其余的机制（SR / V92_P / CXD），而它删掉的 RACE/R127 在我们语料里本就近乎静默。
* 因此**当前最优路径不变**：`am_y2` / `snh48_y2` / `s1sd_y2`（YARN v2 修）+ 底座选择；公开区这一波没有提供新的增量。
