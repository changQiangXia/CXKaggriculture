# 公开强对手核验简报（2026-09-17）

本轮通过 Kaggle API（`/root/miniconda3/envs/kaggle-cli/bin/python`）拉取了三个近期公开 notebook 的导出产物，未执行整本 notebook，也没有上传或提交。公开性、来源和许可证据、源码与归档哈希记录在 [PUBLIC_OPPONENT_METADATA_20260917.json](./PUBLIC_OPPONENT_METADATA_20260917.json)。三个 `main.py` 均通过 Python AST 语法检查，不能据此推断完整对局结果。

## V46：当前最应该加入面板的近期强对手

`ahmedberatozer/kaggriculture-v46-first-turn-microstructure-and-s` 的可执行文件位于 [v46/main.py](./v46/main.py)，源码 SHA-256 为 `735c370383b70d3bf3aac792f2c147e0afc99166fc9f253ede10e8a030acedb6`，归档为 [submission_competitive_v46.tar.gz](./v46/submission_competitive_v46.tar.gz)，SHA-256 为 `7cfb4ab837e7d809a89ba4876a8508533e115c51556e82c97888069138659a6b`。该 notebook 的公开后记曾报告 V46 对其 Beyond48 公布构建为 52 胜、12 负，而其前一版本为 0 胜、64 负；同一后记还报告 24 个 seed、双座位下 V46 对 n=10 版本 40–8、对 n=50 版本 42–6。这些数字来自作者描述，尚未由我们独立复现。

从实际源码可核对到的变化包括：首回合只买 7 单位小麦并卖出 2 单位，净保留 5 单位饲料；第二回合在索引 0 买 30 单位小麦，第三回合卖回；将未来最多三回合的纯现金商品销售前移；销售优先于产品采购；在识别到同谱系对手提前销售时，把竞赛预留窗口升到 24。V46 的公开 evaluation 表还显示，它在某些同源对手上反而比 predecessor 少赢，例如 exact_v43、fastclone24、v43_open78、v45_open5；作者自己也说明，放弃原先 70 单位攻击换取开局鲁棒性。这正是我们需要的压力测试：V46 不是简单地被所有旧策略支配。

V46 的 manifest 明确写出 isolated runtime `passed=false`，最大 85.08 ms，并注明为 step-712 终局规划器取得了本地 50 ms 规则豁免；完整游戏检查在构建日志中是 skipped。故应把它作为**高优先级可执行对手**，但不能把作者的 17.80 个百分点或公开胜率当成已经独立验证的结论。

## Pipe-8：开局清理的独立压力变体

`nathanjacob/kaggriculture-pipe-8-clean-opening` 的源码位于 [pipe8/main.py](./pipe8/main.py)，SHA-256 为 `bdebd4ea8aafb727aa025b2ebe7ec19509571d4501759d537da54ec4ab152c6c`，归档 SHA-256 为 `13ac9e1f34cd91fa612964fc09c790d5973ff80cf876a80e9bbec6f37ad849746`。它实际把 V45/V45-family 的首回合拆分动作改成 `[BUY_PRODUCT, WHEAT, 5]`，第二回合删除小麦 SELL/BUY，保留五次雇佣和 `COW 2 + SHEEP 2`。源码末端标注这是 `EXP300 pipe-8`。

Notebook 声称 1,800 局总计 1753 胜、47 负（97.4%），并报告对 Pipe-7 191–9；这些是作者发布的数据，不能直接作为我们的本地分数。因为 Pipe-8 主要保留 V45 的完整农场路线和反应层，它与 V46/V45 属于高度同源开局谱系。建议把它列为**开局专项压力测试**，不要把它作为独立策略家族单独计权。

## Reactive V7：近期可执行但证据较弱的混合层

`aurax7/kaggriculture-shop-router-reactive-v7` 的源码位于 [reactive_v7/main.py](./reactive_v7/main.py)，SHA-256 为 `e221f4875daff8b03e8f0ec7c86bd3a2a72c0768b049d4c25064abd5301a532b`，归档为 [submission.tar.gz](./reactive_v7/submission.tar.gz)，SHA-256 为 `11fd4428d5f3a4fe9540cc87685fdb47eb4cb9fd7b635775c6bd3fcecee6660a`。源码能直接核对：V45 chassis、V44 竞赛升级、two-turn sale advance、front-loading、`OPEN_UNITS=10` 和 horizon 24 覆盖。

该 notebook 没有在导出结果中提供可核验的完整胜负表，因此不应赋予与 V46 相同的证据权重。它适合作为近期的**混合机制压力样本**，但应归入 V45/V44/Aurax/Beyond 相关谱系，而不是新的独立家族。

## 建议的去重后验证面板

建议把面板按机制家族而非文件名计权：

| 家族 | 建议成员 | 用途 | 计权建议 |
|---|---|---|---|
| Ahmed V45/V46 | V46、V45/Q25 父本、V44/V43 | 当前同谱系竞赛与镜像 | 1 个家族；不同开局作为专项层 |
| Nathan clean opening | Pipe-8、Pipe-7/open5 | 开局取消小麦回程、第二回合清理 | 1 个家族；保留双变体 |
| Beyond/Jaxa | Beyond10、Beyond50、已核验 Beyond duplicate | 销售前移、front-load、24 horizon | 1 个家族；去掉源码/归档完全相同副本 |
| Aurax reactive | Reactive V7、Reactive V5 | 反应式订单、horizon 覆盖 | 1 个家族；V7 可作为最新成员 |
| 旧异构路线 | public V37、Flex、Nathan 其他不同路线 | 泛化与胜转负护栏 | 分别核对 hash 后再计权，不能按名称自动独立 |

首轮应至少加入 V46、Pipe-8、Beyond50、V37 和一个真正异构的 Flex/Nathan 路线；V46 与 Pipe-8 需要双座位、未见 seed 的直接 Q25 对比。公开胜负声称只能帮助提出假设，晋级仍应依赖我们自己的官方 runner 和逐商品账本。
