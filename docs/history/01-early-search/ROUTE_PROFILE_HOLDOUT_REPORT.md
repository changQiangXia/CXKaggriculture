# V37 route profile smoke test

为判断是否可以用硬编码 route-level selector，强制 V37 从开局使用各个已有 tape route，并与正常 V37 对战。每个 route 用 seeds 9001–9003 双 seat；这是筛选测试，不代表最终 panel。

- route 0：margin `-3, -3, -4, -4, -6, -6`，基本等价于 baseline；
- route 1：margin `-21811, -21811, -9590, -9590, -9063, -9063`，明显淘汰；
- route 2：margin `-408, -408, +41, +41, +41, +41`，平均约 `-108.7`，没有稳定超过 V37。

所有已完成对局都是 720 步 `DONE`。结论是现有 tape route 不能直接作为从开局切换的 profile；如果继续做 route selector，只能在 day 6/9 的公开状态确认后切换，并且必须让 selector 保留 V37 默认路线，不能在低置信度时强制 route 1/2。

