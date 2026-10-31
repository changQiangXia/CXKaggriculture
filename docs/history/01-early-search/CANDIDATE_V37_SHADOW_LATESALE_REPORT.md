# V37 shadow late-sale candidate

候选包：[candidate_v37_latesale.tar.gz](/root/autodl-tmp/candidate_v37_latesale.tar.gz)

该包以 V37 原包为基底，增加了一个默认关闭的 public-state late-sale overlay。只有设置 `V37_HYBRID_ENABLE=1` 才会启用；正常 Kaggle 运行和默认本地运行都保持原 V37 行为。

overlay 的限制：

- 只检查 step 648–695；
- 只读双方公开 farm tile、当前自己的 shed projection 和下一步公开 tape；
- 不读取对手 private inventory、未来价格或随机状态；
- 只在对手可见 standing yield 比自己高至少 4、自己已有真实库存、下一步本来就会 SELL 时提议提前最多 8 单位；
- 遇到 PICKUP/PLACE/BUY/HIRE、未知配置、状态异常时回退原 V37；
- 在原销售回合记录 debt 并只扣除本 overlay 提前的数量。

## 当前验证

- `py_compile` 通过；tar 包只有根目录 `main.py`。
- 默认关闭（`V37_HYBRID_ENABLE=0`）对 seed 9001 的 V37 自战结果为 `109901:109901`，720 步 `DONE`，telemetry 无错误。
- 开启 overlay 对 seeds 9001–9005、双 seat 共 10 局：`1 胜 / 1 负 / 8 平`，平均差 `0`，最差 `-1581`，全部 720 步 `DONE`。
- 这 10 局中 overlay 没有实际应用（`applied=0`）；因此当前 gate 太保守，尚未证明有收益，也不能提交。

## 结论

候选保留为 shadow 实验档案，不进入提交队列。下一步若继续，应先离线统计 step 648–695 的公开 tile 产量信号，确认信号在真实 loss 中可见，再单独测试“standing yield”定义；不能直接放宽阈值或把它上传。任何新候选必须在 9001–9020 加 tie seed、双 seat、Flex/Thomas/Dmitrii panel 中相对 V37 零负差后，重新向用户报告。

