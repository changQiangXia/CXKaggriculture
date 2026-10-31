# V43 十轮优化与日志审阅记录

## 日志两轮

第一轮读取两份线上提交的 COMPLETE episodes/replays：Nathan 50（49 competitive + 1 validation），inspired 62（61 competitive + 1 validation），共 110 competitive episodes。全部 DONE/720，17 场败局的 12,223 次调用无 stderr，最大 callback 0.536724 s，终局 shed+carry 均为空。早期即时 public score 600/683 是未稳定快照，后续持久化为 Nathan 2638.5、inspired 2172.4，不能称为运行失败。

第二轮做动作级 replay。Nathan 近镜像败局 109369661 的动作到 step 601 基本一致，现金首差位于 step 403/404/409 的 SELL 时序；Nathan 提交了约 540 条 SELL，对手约 340 条，动物采购相同。inspired 败局 109355094 到 step 575 一致，后半程差距扩大到约 -8026。由此确定优先研究销售时序、market slot 和后期物理闭环，拒绝直接复制 cow tape。

## V43 十轮

1. 冻结 Ahmed V43 源码与 SHA，确认标准 file-path loader。
2. 在文件入口末尾重新插入 `agent`，避免旧 parent callable 被选中。
3. 对终局 718/719 callback 做入口审计，保持 parent 行为。
4. 做 market slot 反例，确认不能删除零数量订单或重排 SELL。
5. 加载器/解压包/action-level 三路径一致性检查。
6. 独立测试 atomic-only：机制 fixture 能保留合法种植，但自然 route 4 seed 双席×两对手中激活 0，拒绝合入。
7. 独立测试 seed-prefund-only：自然 route 激活 0、paired delta 0，拒绝合入。
8. 测试 append-only 终局商品回收：原 parent 已清空可售 shed，激活 0，拒绝 R1。
9. 测试严格终局肥料回收：仅 step 717 shed-adjacent、空库存、idle actor、未收集 fertilizer，完整重放要求 shed/seeds 不变；step 718 再验证并保留原 market 前缀，仅追加 SELL FERTILIZER。4 fresh seeds、双 seat 共 16 局全部 DONE/720，只有 seed 162017 激活，每席 1 单位，candidate-parent delta +4，其余 14 行 delta 0，无负局、无 contract error。
10. 冻结最终包，追加最终 `agent=globals().pop('agent')`，使用真实 file-path loader、fresh smoke、源码编译和压缩包根目录检查。

## 最终候选

最终采用第 9 轮的严格终局肥料回收实现：

- [v43_optimized_final.py](v43_real_20260916/v43_optimized_final.py)
- [v43_optimized_final.tar.gz](v43_real_20260916/v43_optimized_final.tar.gz)
- source SHA-256：`38f65166f5241fa73d78fea781cd3f98de62772805292a75396b76a7db43a3bd`
- archive SHA-256：`fc95a90dca94d44fe4283d0f842de745c1be23b171b184543a33981285e627fb`

文件已通过 `/root/miniconda3/bin/python` 的真实 file-path loader smoke：seed 162017 reward 166391 vs pass；seed 16091601 reward 183178 vs pass；两场 DONE/720。与 Nathan 对局 seed 162017 得到 130640 vs 130637，seed 16091601 得到 89818 vs 89819，均 DONE/720。

本候选不读取对手私有状态，不改变原 market order 前缀，不使用 SELL_ANIMAL（该动作在 engine 中不存在）。

提交时使用 `/root/miniconda3/envs/kaggle-cli/bin/python -m kaggle`，并在 kaggle-cli API 的 resumable upload 中把 `www.googleapis.com` 替换为 `storage.googleapis.com`。
