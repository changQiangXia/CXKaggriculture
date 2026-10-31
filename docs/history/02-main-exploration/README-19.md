# RL 线（局部 RL）——启动说明

## 状态（2026-09-19 晚）

- 代码已验证可训练：GPU 版 torch 2.6.0+cu124 已装，主进程 PPO 更新用 cuda，
  rollout worker 用 cpu（fork 进程不能初始化 CUDA，见 rollout.py worker_init）。
- 已确认 `--games 48 --workers 11` 正常（it30 healthy 48/48，约 100s/iter）。
- 当前已按用户要求停止训练，随时可重启。

## 启动命令（resume 最新 checkpoint）

```bash
cd /root/autodl-tmp/rl_assault
/root/miniconda3/envs/kaggle-eval/bin/python train.py \
  --stages "starter:4,farm:200,mixed:60" \
  --games 48 --workers 11 \
  --outdir run3 --resume run3/ckpt_s1_i29.pt
```

说明：
- `starter:4,farm:200,mixed:60` = 阶段制：starter 预热 4 迭代 → farm2945 主训
  200 迭代 → farm/timed174/gate_m100u 混池 60 迭代。
- `mixed` 每局随机抽 farm2945/timed174/gate_m100u 之一作对手。
- 每 10 迭代 eval 12 局并保存 checkpoint（ckpt_s{stage}_i{iter}.pt）。
- 预计 farm 主训 + mixed 约 3-4 小时（100s/iter × 260）。

## 自测（验证闭环正常，跑 1 个迭代即停）

```bash
cd /root/autodl-tmp/rl_assault
/root/miniconda3/envs/kaggle-eval/bin/python train.py \
  --stages "starter:1" --games 8 --workers 4 --outdir smoke_test
```

预期输出一行 `[0:starter it0] healthy=8/8 ...`，且 nvidia-smi 显存非零。

## 训练会改什么

只改 day 1~27 的卖出决策（9 商品卖出阈值 + 每日卖出量，18 维连续动作），
替代 farm2945 RACEGATE/RACEPX 的静态门槛。田间生产/雇佣/开局/末局清仓
全保留。最终形态：RL 卖出模块打进 timed174 底座 -> timed174-RL 候选。

## 里程碑

- M1 闭环 + loss 下降（已过）
- M2 打赢 starter
- M3 不输 farm2945（镜像局卖点学习）
- M4 313 池 + 镜像双验收，对标 timed174（池 83.7%、镜像 75-78%）
