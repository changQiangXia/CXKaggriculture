# V37 optional input planner weed guard

候选：[candidate_v37_weedguard.tar.gz](/root/autodl-tmp/candidate_v37_weedguard.tar.gz)

规则：当对手公开 WEED 数量达到 3 且 day>=12 时，禁用可选 `_R51` fertilizer/input worker expansion，V37 其他路线保持不变。该规则只使用公开 farm，默认关闭。

9001–9005 双 seat 对 V37 的快速实验：`1 胜 / 7 负 / 2 平`，平均差 `-347`，最差 `-1809`。因此“对手杂草多就停止 input planner”会直接损害 V37，立即淘汰。

结论：日志足以支持针对性硬编码，但不能把相关性直接当成因果；杂草应该继续由 V37 自己的 weed_repair 和物理阻塞检查处理，不能用对手 WEED 数量作为全局禁用信号。

