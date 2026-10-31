# V37 TOMATO qualification weed gate

候选包：[candidate_v37_tomato_weed.tar.gz](/root/autodl-tmp/candidate_v37_tomato_weed.tar.gz)

规则：只有在 TOMATO qualification 的原有条件全部满足且我方公开 farm 没有 WEED 时，才允许新的 TOMATO commitment；默认关闭，启用环境变量 `V37_HYBRID_ENABLE=1`。

9001–9005 双 seat 对 V37 自战：`1 胜 / 1 负 / 8 平`，平均差 `0`，最差 `-1581`，和 V37 没有稳定差异。该门控在当前块基本不可达，不能作为升级证据。

结论：杂草处理必须针对即将执行的目标 tile 和自身路径，不能只在 TOMATO commitment 时用一个全局 weed count 作为决策。

