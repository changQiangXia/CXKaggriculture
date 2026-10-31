# candidate_snh48_herdfix 报告（2026-09-23）

底座：v54_sweep3_snh48.py（= 线上 56456489，现分 2707）。
组成：d27 麦种泄漏修复 + herd-fix（v233 六羊濒危再武装）。

## herd-fix 机制
- 六羊 SE 投资的工人因 `_v233_request` 的 hour/native-hire 门槛在 day26+ 停摆，
  六羊连续两天未喂集体逃脱；SL compact 单工进一步断粮。
- 只在 SE 羊已 `consecutive_unfed>=1` 且今日未喂时：解除门槛、允许当天再武装、
  保留双工。其余世界字节级不变（镜像零扰动）。

## 验证
- 世界复现 1584880307：17/17 羊保住（base 11）、羊毛 168→204、+1593。
- 33 最新败局反事实：19W/0L/14T，mean +95.3，无负 delta（forever young +2965）。
- 镜像 h2h 双座：+9.2 / +7.7，无新增负局。
- 257 真实板：235W/20L（base 234W/20L），unknown mean +9178（+58），零退化。

## 提交物
- candidate_snh48_herdfix.tar.gz（main.py sha256
  9bb950f60f65903b53bf754763764c7bbf357608a7ddbfbbcd9972f244a253cc）

状态：未提交（等用户令）。AM 底座未移植。
