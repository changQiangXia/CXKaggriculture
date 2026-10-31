# 高分录像带研究·第 2 轮（2026-09-15）

本轮把两条官方回放（NiklitaCheporev episode 101408728、Kenjo1209 episode 102192548）和公开 top10 archive 中的 E749–E776 代码放在同一框架下检查。代码仅作机制取证，没有复制到候选模型，也没有提交。

## 录像带到状态机制的对应关系

- 两条录像的 opening（step 0–23）完全相同：8 个单件 WHEAT SELL。之后 SELL 被拆成多次、多个商品和不同批量；不存在“所有同商品订单全局合并”的稳定证据。
- Niklita 在 step 432–455 记录了 17 个 SELL、160 单位（含 WHEAT 91）；Kenjo 同段只有 7 个 SELL、57 单位。到了 step 576–599，Niklita 为 12 个 SELL/156 单位，Kenjo 为 11 个 SELL/70 单位。两者终局都继续保留产品专属批次，说明数量与顺序由库存、价格和路线共同决定，不能从单条录像推出固定批量。
- 高分行为可迁移的部分是条件：保留 pickup、BUY/HIRE 和路径占用，再在已有 SELL 节点内按可见状态排序或小幅前移；状态不满足时沿用父策略。

## 公开实现中可复用的机制

### Boatlee V16-RC5 premium-market lead

`_front_run` 只查看下一步同商品 SELL 数量（`_future_quantity`），并计算当前 shed 减去本步 pickup reserve 与已有 SELL（`_pickup_reserve + _existing_sell`）。若当前 step 没有 town demand（`_town_demand_now`），且有市场槽位，才把最多目标数量前移；下一步 `_repay` 从原计划 SELL 中扣回已前移单位。它是“一步、有限、可偿还”的时序调整，不是全局合并。风险是未来 tape 偏离、town/shop 需求估计错误，以及前移后价格曲线反而变差；必须在真实引擎做 paired holdout。

### E749A Niklita consensus network

E749 声称六条 Niklita 轨迹的 719/719 physical 与 non-SELL 节点一致，因此把稳定的移动、种植、照料和路径当作骨架，只对可见状态做边缘修复：

- `_project_shed` 按 actor 顺序模拟 shed 的 PICKUP/DROP；E750 扩展同一投影，加入 shed 邻接的 PLACE，避免“当回合放置后库存”被漏算。
- `_cap_sales` 依据投影库存逐个限制 SELL，绝不出售 pickup 已预留或不存在的货物。
- `_assign_sell_slots` 只重排已有 SELL 槽位，按逐单位价格和 `contested_value` 排序；不跨越 BUY/HIRE 结构，也不新造销售节点。
- `_fund_market` 以顺序账本检查现金、shed 容量、雇工、土地和购买成本，按可执行数量截断订单。

这些护栏解释了高分录像中“碎片化但可执行”的销售形态：先保持物理节目和订单槽，再做小范围、可回退的市场修正。

### E773A/E774A/E775A/E776A

- E773 用可见 shop 与 MILK/WOOL 价格构造 dairy/wool pressure，仅在预注册 COW/SHEEP bundle 上替换，设置 cow→sheep 上限 3、sheep→cow 上限 1，并保持 animal count、pasture/land/hands、路线、feed、crop、sale 节点和数量不变。
- E774 只在最终可执行 step 718，对父动作之后的 projected shed 做 MILK/WOOL 终局清理，按逐单位 revenue 排序并受 10 个市场槽位限制。
- E775 在 step 313 以空 pasture、8 个 worker 的固定 spawn geometry、恰好一个 BUY_ANIMAL、3 个 HIRE、现金和容量检查为前提，购买 1 个额外动物，并在 314–317 由新增 hand 运送；任何几何、库存或占位不符就取消。
- E776 修复 E775 的引擎时序：step 314 从 `(5,4)` PICKUP，315 NORTH，316 `(5,3)` PLACE；同样要求 appended hand 可见且父动作未占用。该修复体现了“先确认引擎实际 spawn，再改动作”的原则。

## 对本地研究的结论

最值得继续验证的是三个独立、可关闭的开关：

1. day 24–29 的已有 SELL 槽位按可见逐单位 revenue/contested value 排序；
2. Boatlee 式一步 premium front-run（有 next-turn SELL、无 town demand、扣除 pickup reserve、下一步偿还）；
3. step 718 的 projected-shed MILK/WOOL/CARROT/WHEAT 终局补单。

每个开关都要保留父动作回退，并报告 activation rate、订单槽变化、负对局数、min margin、5% 分位和两 seat 差异。录像证据只支持“条件化、小范围调整”，不足以支持把 E775/E776 结构直接并入当前候选。

## 可复核来源

- [HIGH_SCORE_TAPE_MINING_20260915.md](/root/autodl-tmp/HIGH_SCORE_TAPE_MINING_20260915.md)
- [high_score_profile_features_20260915.json](/root/autodl-tmp/high_score_profile_features_20260915.json)
- `public_code_round2/boatlee_v16-rc5-high-score-8c-4s-premium-market-lead/…ipynb.txt`
- `public_intel/top10_archive/agents/e749a_niklita_consensus_network.py`
- `public_intel/top10_archive/agents/e750a_place_funding_repair.py`
- `public_intel/top10_archive/agents/e773a_demand_aligned_pasture_network.py`
- `public_intel/top10_archive/agents/e774a_terminal_animal_frontier.py`
- `public_intel/top10_archive/agents/e775a_latent_pasture_activation.py`
- `public_intel/top10_archive/agents/e776a_engine_exact_latent_pasture.py`

