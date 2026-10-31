# Kaggriculture RL 线设计（v0）

## v0.1 更新（2026-09-19 晚，首次落地后的修订）

落地时对 v0 做了三处收紧，均已实现并跑通 smoke：

1. **动作空间 34 → 18 维，只学 SELL**。底座 farm2945 的 BUY_SEED/BUY_ANIMAL/
   HIRE/BUY_LAND 与田间计划全部保留，RL 只接管 9 种商品的
   `(卖出阈值[0,300], 每日卖出量[0,30])`。理由：镜像战的胜负手全部在
   sell 时机（flood/timed 的结论），更小空间样本效率更高，对底座内部
   记账的扰动最小。
2. **接管窗口 = day 1..27**。day 0 的开局轮转（`_R42_OPENING`）与
   day 28-29 的终端清仓保留底座原逻辑，避免开局资金链与末局清算被 RL
   学坏。决策粒度仍为每天 1 次（27 决策/局）。
3. **reward = 每日资金差分**（`money[t+1] - money[t]`，最后一个决策的
   reward 为终局 money 差）。回报严格叠加为 `终局money - 初始money`，
   与比赛评分一致，同时给 PPO 稠密的日粒度信用分配。

实现文件（本目录）：
- `env_wrapper.py`：obs→62 维特征（时间/价格/库存/双方田块统计）、
  18 维动作解码、SELL 订单执行、`RlAgent`。
- `ppo.py`：双隐层 256 MLP + 对角高斯 + value head，GAE/PPO 更新。
- `rollout.py`：多进程对局采样（每局重载底座模块，规避跨局全局态污染）。
- `train.py`：阶段制训练（starter 预热 → farm2945 主训），日志 jsonl +
  checkpoint + 定期确定性 eval。

smoke 结果（warm-start 策略，阈值≈36/量≈15）：
- vs starter：4/4 healthy，终局 money 133k~154k（底座 vs starter 为 141k，
  同量级，说明接管 sell 未破坏底座生产）。
- vs farm2945：2/2 healthy，80k/115k（预期内弱于底座 140k+，待学习）。
- PPO 更新循环、GAE、checkpoint 全链路无异常。

## 目标
训练在线决策策略，本地双重验收逼近/超越 timed174：
- 313 场真实对手池：83.7%（262W/51L）
- 镜像局：vs farm2945 本体 75-78%，vs 激进克隆 70-72%

## 环境事实（kaggle-environments 1.32.7）
- 2 玩家、720 step（30 天 × 24 turn）。
- 终局 reward = 玩家金钱；DONE 于最后一帧。
- observation：
  - `farms[i]`（公开双方）：money、10×10 tiles、farmer/hands 位置、unlocked_quadrants、hires_today。
  - `private`（仅我方）：shed 库存（9 商品+3 动物）、seeds（5 作物）、inventories（farmer + hands）。
  - `market`（共享）：9 商品 inventory + prices。
  - `town`：unlocked_shops（有放回重复）。
  - `day`/`hour`/`step`。
- action：`{"farmer":[op,...],"hands":[[...],...],"market":[[...],...]}`
  - unit ops: NORTH/SOUTH/EAST/WEST/PASS/PICKUP/PLANT/WATER/HARVEST/FERTILIZE/BUILD_*/DIG/PLACE/FEED/COLLECT_FERTILIZER/CARE/DROP
  - market ops: BUY_SEED/BUY_PRODUCT/BUY_ANIMAL/SELL/HIRE/BUY_LAND；每步最多 10 条。
- 非法动作静默 no-op。

## v0 架构：分层（RL 只学市场阈值，田间执行复用 farm2945）

动机：farm2945/timed174 的田间操作（移动/种植/浇水/收获/喂养）已经可靠；
镜像战的胜负手在市场层（抢卖时机/数量）。让 RL 只输出市场策略，缩小决策空间、
提升样本效率，且保留底座的生产实力（保底）。

- 决策粒度：每天 1 次（30 决策/局），RL 输出连续向量：
  - 每商品 sell threshold（0..300）+ sell qty（0..30）
  - 每作物 buy-seed threshold + qty
  - 每动物 buy-animal threshold + qty
  → 共 (9×2) + (5×2) + (3×2) = 34 维连续动作。
- 执行：当天内每步，由脚本按阈值+当前价/库存生成 market 订单（其余订单，如
  HIRE/BUY_LAND/端局清仓，沿用 farm2945 原逻辑）。
- 实现：monkey-patch 方式调用 farm2945.py 的 agent，替换其返回的 `market` 字段。
  若发现其内部计划状态与替换后订单不一致导致错乱，再改为深度改写。

## 训练管线
1. `env_wrapper.py`：obs → flat 特征向量（市场 18 维 + shed/seeds 17 维 +
   farm 摘要 ~20 维 + day/hour 2 维 ≈ 57 维）；连续动作 → market 订单。
2. `ppo.py`：torch 手写 PPO，MLP 对角高斯策略（34 维），GAE，clip 目标。
3. `rollout.py`：多进程 rollout（ke 对局 CPU 串行，用 multiprocessing 并行
   对局采样），对手支持：starter/random/farm2945/timed174/gate_m100u。
4. 训练分三阶段：
   - S1 对手=starter_agent：验证闭环与 loss 下降（M1/M2）。
   - S2 self-play：对手=farm2945 脚本 + 自身历史 checkpoint 混池（M3）。
   - S3 对手=timed174 + 真实池重放：冲击 M4 双重验收。

## 里程碑
- M1 训练循环能跑、loss 下降。
- M2 打赢内置 starter。
- M3 self-play 不输 farm2945。
- M4 313 池 + 镜像双重验收对标 timed174。

## 资源纪律
- GPU：RTX 4080 32G（策略网络训练）。
- CPU 12 核与 8C/4S 线共享：rollout workers ≤ 6。
- 产物目录 /root/autodl-tmp/rl_assault/；不动 farm2945_dev 现有候选。
- 绝不提交 Kaggle。
