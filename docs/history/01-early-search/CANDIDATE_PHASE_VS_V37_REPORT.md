# candidate_phase_v5 对 V37 的快速淘汰

在官方本地引擎中，以 `candidate_phase_pkg/main.py` 为我方、`public_v37_pkg/main.py` 为对手，跑 seeds 9006–9008 的双 seat：

- seed 9006：`-47880`、`-58439`；
- seed 9007：`-95937`、`-109853`；
- seed 9008 seat 0：`-96209`。

所有已完成对局都是 720 步 `DONE`，但资金差巨大为负，因此立即停止剩余测试并淘汰该候选。它不能作为 V37 的融合底座。

