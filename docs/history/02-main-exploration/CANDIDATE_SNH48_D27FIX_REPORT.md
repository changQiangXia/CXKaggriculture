# candidate_snh48_d27fix 报告（2026-09-23）

底座：v54_sweep3_snh48.py（线上 56456489，2716.4，此前最高）。
新增：D27 麦种浮仓修复层（busyaprime seed-leak 思路的本土化，season-long 扩展）。

## 根因
- CARROT2 换株（麦→萝卜，pays_now 价差判定，day6-28）与 tape 提前 1 小时
  的 BUY_SEED WHEAT 时序错配，spare_wheat 补偿追不上，麦种浮仓跨天累积；
  day27 又为即将换株的麦照买，终局 5-11 粒麦种纯浪费。

## 修复内容
- day6-26：麦种浮仓封顶 = 当日剩余 tape 麦株 + 2 粒 hedge（不预测换株，
  只砍跨天多余库存，数学上不会饿死麦株）。
- day27：换株感知精确修剪（用 CARROT2 自身 pays_now 预测换株，need_w/need_c
  重算，short_c 兜底 + 2 粒 hedge）。
- 只改 market 的 BUY_SEED 数量，砍掉的订单留空槽，unit 动作与市场竞速
  位置不变。

## 验证
- 镜像 h2h 双座位（vs 底座）：40W/2L/18D，81.7%，mean +9.2（33000-33029）。
- 257 真实板：234W/20L → 235W/20L；总 margin +1970（+7.7/局）；255 局仅 1 局
  -30，其余 0/+10/+20/+50/+70。
- 终局残种：33008 11→4、7000 5→4、33000 5→4。
- loader：官方拾取 `_d27_agent`；720 步完整赛季 QA 通过。

## 提交物
- candidate_snh48_d27fix.tar.gz（main.py sha256
  6e154a837c809f44d3b775fe3f4e701b522866498ea9ae7b9da746db8449ca0f）

状态：未提交（等用户点头）。
