# Log 修改泛化研究·第 2 轮：留一对手、时间切分与尾部审查

将公开强 agent 和线上 loss-derived 行为按作者/策略族/时间分组。用 discovery 集发现状态谓词；development 集只调阈值；最新公开 agent、未见 seed、另一 seat 和最近线上对手留作 holdout。采用 leave-one-opponent-out：每次去掉一个发现对手，规则仍须在剩余策略族和未见对手上成立。

每次候选运行 candidate/parent paired panel，固定 seed、seat、opponent、engine 和 runner。除旧 V37/Flex/Thomas/Dmitrii 外，加入近期公开 tape、shop/router、runtime/economy 三类 agent。按 phase（opening、day6–12、day18、day24–29、terminal）和对手族报告 mean/median Δmargin、min、5% quantile、CVaR、negative games、seat variance、activation rate、fallback/error rate、未来 72-step inventory/cash/route 完整性和 callback max。

为了判断 benchmark 是否具有线上预测力，先回测历史变化（no-R128、no-R127、merge648、weedguard、surplus timing、late-sale 等），检查本地排序是否能复现已知线上方向。若不能，则降低该 benchmark 族权重，不据其结果晋级。若候选只在 discovery 族收益、在最新 holdout 或扰动集退化，判为过拟合并淘汰。

晋级需同时满足：所有局 DONE/720、stderr/timeout 为 0；至少 3 个对手族 paired mean 不负；5% 分位和 min margin 不恶化；不新增负局；两 seat 方向一致；activation 足够且未触发时 parent-equivalent；收益在去掉任一发现对手后仍保持。否则只保留为研究假设，不提交。
