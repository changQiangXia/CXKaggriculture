# V37 / V43 / competitive V45 / Nathan 的竞争性研究与本地方向协议

## 当前问题

随着公开高质量 agent 增多，历史线上绝对分数和名次会随对手池漂移。V37 曾接近 2800 并进入约 150 名附近，competitive V45 首次完成时 public score 曾显示 1820.8，但用户观察到它随后升到约 2480；这说明正在处理的 public score 不能当作固定模型质量标签。不同提交时间的分数不能直接横比，研究目标应改为预测“候选相对父版本在当前对手分布中的方向”。

四个重点对象按行为族整理：

- **V37/V43**：同一作者和相同 route-tape lineage，生产/服务 chassis 相近，不能在统计上当成两个独立对手族。V43 在 V37 的基础上累积了供料、服务、市场 reservation、quote/reorder、terminal 等层。
- **Nathan corrected**：固定 route + sales-first / budget / service 层；corrected 主要修正最终 loader 和 market list 入口，旧配对中 action 与父策略一致，不能把加载修复称成策略增益。
- **competitive V45**：V44 继承策略上增加 clone-gated race horizon 和 step-0 wheat round trip。它的核心是共享市场 index 的相互作用，属于特殊 opening exploit，不是一般生产策略。
- **动态/异构族**：flex、Thomas、Dmitrii 等不依赖同一固定 tape，应作为独立泛化压力测试。

## 已证实的失败模式

### V43

完整账本显示，近镜像失败局有“双方产量和总成交量相同、销售时机不同”的案例；另一类失败局则是扩张成本过高，销售收入增加仍不足以覆盖 HIRE/LAND/ANIMAL/投入品支出。固定 horizon 4→8 在 64 场配对上总平均约 −150.5，说明无条件扩大预留窗口不可泛化。

### Nathan

近同族 replay 的落后集中在约 300–650 步的商品级小批量 SELL 和订单槽位变化。`_v224_sales_first` 会影响双方共享 market index；只保护末尾列表或只做小库存/价格/town gate 的本地候选均出现跨族负 delta。单纯关闭 sales-first 也在部分路线明显变差，说明该层可能是竞争性相互作用，不应按单边账本归因。

### competitive V45

step-0 round trip 的实际动作变化是：`BUY WHEAT 5 + BUY WHEAT 10 + SELL WHEAT 60` → `BUY WHEAT 70 + SELL WHEAT 70`。它针对第二槽继续 BUY wheat 的 route-tape；若对手先 SELL 再 BUY，优势可能反转。第一回合改变共享 market 和后续 RNG，固定 tape replay 不适合评估收益。用户观察到线上分数从早期约 1820 继续上升到约 2480，说明它可能在更长时间的对手池中恢复，但这仍不能证明 notebook 宣称的开发集 uplift 可直接泛化。

## 新的紧致本地验证协议

详细协议见 [VALIDATION_PROTOCOL_DIRECTION_20260916.md](/root/autodl-tmp/VALIDATION_PROTOCOL_DIRECTION_20260916.md)，执行脚本见 [strict_paired_eval.py](/root/autodl-tmp/strict_paired_eval.py)。关键设计：

1. **先冻结**：记录父源码、候选源码、引擎 SHA、改动开关、用过的 seed/replay，不得看到 holdout 后继续调参。
2. **按策略族而非文件名分层**：V37/V43 合并；Nathan 单独；V45 opening/clone 单独；flex/Thomas/Dmitrii 作为异构压力；最后加冻结后才选择的时间外公开模型。
3. **common initial world 配对**：候选和父版本使用相同 seed、相同对手、相同 seat，各自从干净加载开始跑完整 720 步。候选动作改变后允许后续市场、生产、town、RNG 自然分叉；不重放固定 tape。
4. **指标不只看最终 margin**：记录 own/opp reward、margin delta、24/72 步现金、实际 SELL 成交量与收入、BUY/HIRE/LAND/ANIMAL/SEED/FERT 成本、产量、overflow、首次 action diff、触发率、完成率和 stderr。
5. **共享市场改动单独分层**：V45 这类 step-0 改动需要按对手 opening 分成“第二槽 BUY wheat”“先 SELL 再 BUY”“无 wheat round trip”三层，同时记录实际报价、第二天 MELON seed、shop/产量变化。
6. **按 seed 聚类统计**：每个族报告均值、中位数、P10、最差三场、W/L/T，并用 seed 聚类 bootstrap CI；同一个 seed 的两个 seat不能当成两个独立世界。

## 两阶段门槛

### Pilot

每族先跑 8 seed × 2 seat。任一非目标族均值 < −100、任何灾难局 < −2,000、或出现运行异常，候选淘汰。Pilot 只能决定是否值得做 confirm。

### Confirm

候选冻结后，每族跑 16–24 个未见 seed × 2 seat，并增加一组冻结后选取的时间外模型。晋级要求：

- 策略族等权平均 paired delta > +150，seed-cluster bootstrap 95% CI 下界 > 0；
- 至少 3/4 主要族均值 ≥ −50，任何族 CI 下界 ≥ −300；
- 总体 P10 ≥ −1,000，最差局 ≥ −2,000；
- 胜率下降不超过 5 个百分点，完成率 100%，无新增异常；
- 收益不能来自单一 seed、单一 callback 或少于 5% 的偶发触发。

若候选明确只针对某个 opening 族，则只能标为 exploit；其他族必须没有实质退化，才可进入线上候选。

## 当前工作结论

下一步不应继续复制公开模型的完整代码，也不应把每个局部 patch 直接当成候选。更可行的路线是：选择一个强父版本（优先 competitive V45 或 Nathan/V43 中经过线上校准的版本），每次只改变一个可解释机制，先用 shadow telemetry 检查触发率和实际成交，再按上述跨族协议判断方向。这样得到的不是“公开代码的另一个包装”，而是能够解释其竞争交互、并能在时间外对手上验证的微调。

## 新增 jaxa623 / K0006 样本

`jaxa623/beyond-48-0-128-128-worlds-with-95-cis` 已加入研究阵营。精确复原的 K0006 不是新 farm lineage，而是嵌入 Ahmed raw V43 的市场 wrapper，新增 front-loading、two-turn sale advance、horizon24 和 opening50。它公开失败实验与两个评估陷阱，研究价值高于单纯公布胜率；但作者的 64-world 原始 seeds/ledger 未随 notebook 提供，不能直接复核其 CI。

独立小面板显示 K0006 相对其 raw V43 parent 在 V45/V43/Nathan 上平均正 delta，但在 flex 上 4/4 场严重负 delta，故其 market 微边缘属于同 route/opening 条件机制，不是跨架构通用增强。后续将把 K0006 的“原列表/重排列表完整执行 + 不改数量”作为可借鉴的安全约束，把 horizon24、opening50 分开消融，不直接复制整包。
