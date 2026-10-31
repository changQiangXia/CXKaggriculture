# V37 vs sheep-overlay ablation holdout

本轮在官方本地引擎中，以完整 V37 为 seat 0/1 对手，`ready_flex_v7`（关闭罕见 V233 sheep overlay）为另一方，使用 seeds 9006–9010 和镜像 seed `1495252849`，共 12 个 seat-run。

V37 相对该消融版的结果为：`12 胜 / 0 负 / 0 平`，平均资金差 `+3670.0`，最小 `+1463.0`；全部对局 720 步 `DONE`。

这说明关闭 sheep overlay 不是 V37 的稳定升级，至少在该 holdout 上仍明显弱于完整 V37。它也支持保留 V233，但应继续收紧其异常/容量/资金确认，而不是全局移除。

