# RL 线第一晚探索报告（2026-09-19 ~ 09-20）

## 目标与结论一句话
搭建分层 RL（farm2945 底座 + 学卖出偏差），训练后**验证了真实学习信号**，
但一晚上训练的绝对强度未超过手工候选 timed174；不构成提交候选。

## 架构（最终版）
- 底座：farm2945 生产/路线/喂养/清仓全部保留。
- RL 偏差层：day 1..27，每商品 `(追加卖出阈值, 追加量)`，18 维连续动作，
  每天决策一次。中性参数严格复现底座（逐局奖励一致）。
- 62 维特征（价格/库存/shed/种子/双方 farm 摘要/时间）→ MLP(256,256) 高斯策略 + value。
- 手写 PPO（GAE 0.99/0.95、clip 0.2、4 epochs）；多进程 rollout 每局独立加载
  脚本 agent 模块（杜绝 farm2945 全局状态串扰）。
- 课程：starter 4 → farm2945 200 → mixed(farm/timed174/gate) 60，32 局/it，
  每 10 it checkpoint + 确定性 eval。supervisor 断点续训（平台周期性杀进程）。

## 三个关键设计陷阱（已排除）
1. 全接管 SELL：不卖货会让 farm2945 现金流断裂（money 2k），起点永远不是平局。
2. 中性 warm-start（阈值 298）落在 sigmoid 饱和区：探索噪声无效，训练 55 轮
   仍是纯平局（3W/3L/24T）。
3. value 目标未归一化：money ~1e5 尺度导致 v_loss 数十亿、GAE 被 value 项主导。

## 最终成绩（ckpt_s2_i59，mixed 阶段结束）
| 验收 | RL 策略 | 基线对照 |
|---|---:|---:|
| vs farm2945 镜像（64 局） | 24W/10L/28T（38.7%） | 本体打自己=全平局；flood50=76.6% |
| vs timed174（64 局） | 16W/46L（25.8%） | timed174 打本体 75-78% |
| vs gate_m100u 激进克隆（64 局） | 14W/48L（22.6%） | timed174 打激进 70.3% |
| 325 场真实池 | 250W/75L（76.9%） | 本体 79.6% / timed174 81.2% / flood50 82.7% |

镜像局从"纯平局"进步到 24W/10L（非平局局 70.6% 胜率），证明 RL 学到了真实的
抢卖相位收益；但打不过更精细的 timed174 与激进克隆，池子略低于本体基线。

## 策略解读（inspect_policy.py 输出）
RL 独立学到的规则：
- MELON：早中期大量追加（thr 190→84，qty 14-18）。
- WOOL：全天候稳定追加（thr 215，qty 10）。
- TOMATO/EGG：前后期相位切换；CARROT 仅 day16+ 高价（288）追加。
- **MILK 不追加**——独立复现了手工消融 milk_native 的结论（牛奶价格缓慢恢复，
  抢卖亏损），这是 RL 信号真实性的强证据。

## 蒸馏验证（timed174 + 蒸馏规则）
- vs timed174 镜像：10W/4L/50T（微弱正收益，但 50 局平局）。
- vs farm2945：49W/15L（76.6%），与 flood50 相当。
- vs gate_m100u：42W/22L（65.6%），略低于 timed174 的 70.3%。
- **325 池：264W/61L，与 timed174 完全一致（零差异）**——池中 timed174 的
  库存已被其 RACE 层卖尽，蒸馏追加层无可追加库存，无净效果。

## 裁决与下一步
- RL v0 不作为提交候选；timed174 仍是当前最强本地候选。
- RL 的长期改进路线（如需继续）：决策粒度每天 4-6 次（覆盖小时级相位）、
  更长训练与更大样本、对手池更接近线上镜像分布、或把 per-world 条件化
  （以 shop 组合/对手签名做输入）做进策略。
- 蒸馏方向单点可再试：把 MELON 追加层做成 per-world 条件（仅 YARN/特定店组合），
  但当前证据不支持无条件移植。

## 产物
- 训练/验收/导出：train.py、ppo.py、rollout.py、env_wrapper.py、
  rl_eval.py、rl_pool_eval.py、pool_compare.py、inspect_policy.py、
  export_policy.py、supervise.sh。
- checkpoint：run4/ckpt_s2_i59.pt（最终）。
- 蒸馏变体：timed174_rldistill.py（池上与 timed174 等价，不推荐）。
