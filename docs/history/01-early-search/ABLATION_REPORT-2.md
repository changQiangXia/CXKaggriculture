# V43 atomic-only / prefund-only 实验报告 — 2026-09-16 UTC

本轮没有提交 Kaggle，也没有修改冻结 parent。parent 是 `/root/autodl-tmp/research_kaggle_ahmed/decoded_main.py`，运行前 SHA-256 精确校验为 `919fc1d61050cd96f799979e49177ea3ac7bce98ec9835724238bea73f4a08ed`。实际源文件字节 SHA 以 manifest 中记录为准（见父文件的审计 manifest）；运行采用 `kaggle_environments.agent.get_last_callable` 文件入口，而非 `module.agent`。

## 变体定义

- `atomic_only/main.py`：把冻结 parent 最终 wrapper 中的
  `if _R148_SEEDS: action=_r148_seed_prefund(observation,_r148_atomic(observation,action))`
  替换为只执行 `_r148_atomic(observation,action)`。
- `prefund_only/main.py`：只执行 `_r148_seed_prefund(observation,action)`。
- 两者都保留 parent 的 overflow 机制；没有隐式同时开启另一个机制。

AST 检查确认最终 wrapper 只含对应的一项调用。每个变体都重新从文件源码加载；结果记录 `loader_is_named_agent`、action hash、telemetry、错误计数和每局状态。

## 实验矩阵

- seed：`16091601, 16091602, 16091603, 16091604`
- seat：0、1
- 对手：Nathan cautious 的实际文件入口、Flex 公开策略
- 每个组合运行 parent、atomic-only、prefund-only
- 每个变体 16 局；总计 48 场；所有局均 720 steps、DONE、stderr 空

原始明细：[results.json](results.json)；paired 汇总：[summary.json](summary.json)。

## 结果

| 变体 | paired 局数 | 平均 cash Δ | 平均 margin Δ | 最小 Δ | 最大 Δ | 负局 | 激活次数 | errors | 结论 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| atomic-only | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **reject_inactive** |
| prefund-only | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **reject_inactive** |

每一局的 candidate action hash 与 parent 相同。因而没有收益、没有伤害，但也没有任何线上可迁移证据；两个变体均拒绝进入 V43 提交候选。

## 机制单元测试

完整 panel 没有自然触发 seed shortage，故额外运行真实 engine contract fixture：[atomic_contract_fixture.json](atomic_contract_fixture.json)。该 fixture 构造两个单位同一回合请求 1 个 WHEAT，而 private seeds 只有 1：

- parent raw action：engine 的 atomic rule 丢掉两个请求，WHEAT births=0，seed remains=1；
- atomic-only repair：保留一个合法请求，把另一个改为 PASS，WHEAT births=1，seed remains=0。

这证明 atomic-only 代码路径本身可激活且语义符合预期，但自然 panel 未遇到该状态。prefund-only 没有对应的自然 activation；在当前 route/action 下没有满足“下一回合有效 PLANT 且可预算购买”的机会。

## 决策

两项实际独立实验都完成，但在新 seed、双 seat、两个对手上完全不活跃。保持 parent，不合并、不提交。若要继续研究，应先建立受控而不泄露未来信息的 activation panel，再评估 24/72-step 后续现金与库存，而不是把零差值当成改进。
