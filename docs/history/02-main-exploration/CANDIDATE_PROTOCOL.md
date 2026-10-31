# 下一候选验收协议（第 87 轮定稿）

所有孵化候选必须按此顺序过门；任一维度退化一票否决，宁可保留 snh48。
验收维度（用户"拉开差距"判据）：胜率之外必须看 **mean/median margin**、
**>1k 决定性胜占比**、**±1k 抛硬币占比**。

## 0. 环境
- Python: `/root/miniconda3/envs/kaggle-eval/bin/python`（kagsim C++ 引擎已装，~1s/局）。
- 机器：12 核 / 62GB 内存 cgroup / 150G 盘。**并发 ≤8、数据流式读**（禁止全量
  载入 parquet JSON 列，曾 OOM）。
- 提交剩余额度 3（勿探测性提交）。

## 1. 快扫（机制级信号，h2h 双座位）
`python ax_h2h.py 'CAND=w_cand.py' '@OPP=w_s1sdoca_rgs8f_snk1_snh48.py' --seeds <30个> --procs 6`
- 硬纪律：**共享市场策略必须 h2h 双座位裁决，自对弈银行差会系统性高估**（三次
  实锤：鹅线、all-101、SETomato7）。

## 2. 扩池（257 局）
`python panel_kagsim.py 'base:path' 'cand:path'`（~110-120s）——不得低于 snh48 的
92.1%（V 桶 84%）。

## 3. 真实板配对（新门槛，157→177 个线上真实 seed）
`python real_seed_pair.py --base v54_sweep3_snh48.py --cands 'tag=path' --procs 8`
- 通过线：mean/median margin 实质为正 + >1k 决定性胜占比提高 + 抛硬币占比下降。

## 4. live 矩阵终审
`python onearena/arena.py --challenger TAG=wrapper --vs-only --since 2026-09-17 --worlds 64 --procs 12`

## 5. 提交前
- 归档 tar 内 main.py 与本地文件 hashlib 比对 + 官方 loader 拾取确认；
- `kaggle competitions submit`（需用户明确点头）。

## 磁带落地时（georgy 更新）
`python meta_pipeline/georgy_monitor.py` → `python meta_pipeline/analyze_new_tapes.py <新parquet>`
→ 自动冻结重放 snh48 vs Densike/Ghost Rule/HowardLeeTW/zeyu_lau/sonny_01。

## 当前基线
- snh48（ref 56456489）：线上 2713.8、77% 胜、近期均差 +4867；本地 live 全矩阵
  95.1%、扩池 92.1%、177 真实板。
- 决定性克星（磁带待取）：Densike(88% 胜)/Ghost Rule(70%)/zeyu_lau(-6134)/
  sonny_01(-4582)，均私有代码。
