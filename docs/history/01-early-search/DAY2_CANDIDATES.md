# Day 2 候选与录像研究

## 线上录像观察

最新 active 队列为 `56190357`（h5room623，public score 当前约 2714.4）和 `56185929`（h5sim96，约 2744.4）。监控脚本现已恢复为单实例，PID 1639，间隔 600 秒，覆盖这两个 submission。

56190357 新收集到的近期对局中，已核验 13 场：1 场小胜（+388），其余多数为小幅 loss（约 -256 到 -4555），另有一场大幅 loss（-49779）。所有回放均 720 steps DONE，agent 日志无 stderr，调用耗时低于 0.5 秒。终局动作统计显示：

- 普通路线多为 8 只动物、约 400 次 SELL，差距主要在 premium 商品成交时序；
- 大幅 loss 对局出现 `BUY_SEED TOMATO=10`、10 个 TOMATO 地块和较少的动物资产，说明 day-6 路由分叉在某些市场/对手组合下风险很高；
- 小幅 loss 的终局资产结构与 V37 接近，仍然是共享市场顺序造成的现金差，不是运行时失败；
- 线上分数 h5sim96 持续高于 h5room623，说明 step-623 容量保护尚未证明能提高 rating。

## 三个未提交候选

A. `candidate_A_h5room623.tar.gz`：当前线上版本的 step-623 窄容量保护。已在 V37 22 局、Flex 20 局、Thomas 20 局、Dmitrii 20 局本地验证，均 720 steps DONE；适合继续观察容量溢出是否长期相关。

B. `candidate_B_h5sim96.tar.gz`：去除 room guard、保留 0.96 相似度五回合销售预留。线上当前分数高于 A；此前 V37 面板 22/22 胜，公开对手面板全胜或近全胜；真实 replay 证明它的主要问题仍是市场时序。

C. `candidate_C_h5roomlow.tar.gz`：step-623 容量保护下按低机会成本顺序出售库存，优先 FERTILIZER/WHEAT/CARROT/EGG，保护 MILK/STRAWBERRY/WOOL。Thomas 面板 20/20 胜，较 A 的 19/20 略稳；真实 loss replay 未翻盘，因此仍需保守看待。

三者均只生成本地归档，未执行提交。

## 当前判断

若目标是前 100 而不是针对单一公开对手，优先保留 B 作为基线，A 作为容量机制实验，C 作为 Thomas 类对手的稳定性备选。下一轮应重点复盘 TOMATO 路由触发条件以及大幅 loss 的 premium SELL 时序，避免用单场终局金币差直接改动主路线。
