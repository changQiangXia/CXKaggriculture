# V37 public-divergence sheep gate

候选包：[candidate_v37_cond_sheep.tar.gz](/root/autodl-tmp/candidate_v37_cond_sheep.tar.gz)

该候选保留 V37 全部动作，只在 `V37_HYBRID_ENABLE=1` 时把 V233 sheep overlay 的资格判断再加一层公开差异门控：如果对手公开 farm 的 SHEEP 数量或 WEED 数量高于我方，则不开始新的 sheep investment。它不读取对手 private 状态。

本地 9001–9005 双 seat 对 V37 自战：`1 胜 / 1 负 / 8 平`，平均差 `0`，最差 `-1581`，和原始 V37 在这些 seed 上完全没有行为差异；全部 720 步 `DONE`。说明该门控在当前 seed 块中不可达或没有改变 V233 的实际承诺，不能作为改进证据。

结论：不进入待提交队列。后续不能继续堆叠同类不可达门控，应把资源投入到能在 replay 上被观测、并能由本地 simulator 评估的 route-level profile selector。

