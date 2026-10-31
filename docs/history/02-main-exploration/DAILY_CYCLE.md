# Ahmed 式每日迭代工作流（meta_pipeline）

目标：把「当天公开区 → 当轮候选 → 当轮验证 → 当轮提交」压缩到小时级。
四个步骤对应四个脚本，每步都有产物，断点可续。

## 0. 前置
- 基线底座：`/root/autodl-tmp/farm2945_dev/v54_pairgate.py`（215 池 89.3%）。
- 验证三件套：无偏 215 池 / 对 V54 纯体 h2h / 败局语料重放。
- 提交需用户授权；脚本只负责产出候选与判定，不自动提交。

## 1. 情报收割（每小时可跑）
```bash
/root/miniconda3/envs/kaggle-cli/bin/python meta_pipeline/intel_harvest.py
```
- 拉最新 notebook + 活跃讨论，增量出 `intel/digest_*.md`；
- 重点看 `NEW AHMED RELEASE` 行和带关键词的新 notebook；
- 新机制 → 立刻去 `kaggle kernels pull` 源码、逐层读注释找署名与思路。

## 2. 行为指纹差分（拿到新对局后）
```bash
/root/miniconda3/envs/kaggle-eval/bin/python meta_pipeline/fingerprint_ops.py diff \
    <昨日对局目录> <今日对局目录> CHEN Xiang
```
- 对比作物配比、特殊事件（早扩地/绵羊/番茄分批/低喂食/flood）的频率变化；
- 用 `... one <replay.json> <team>` 单局细看某对手的开局与日级动作。

## 3. 低风险层脚手架
```bash
/root/miniconda3/envs/kaggle-eval/bin/python meta_pipeline/layer_scaffold.py \
    farm2945_dev/v54_pairgate.py mylayer farm2945_dev/v54_pg_mylayer.py
```
- 模板自带 try/except 回退 + telemetry，加层永不崩底盘；
- 机制优先做零位移市场编辑（slot-0 插入、排序），动单位动作必须先用
  replay 证明位移安全（本轮教训：劫持浇水/收获会把池打崩）。

## 4. 竞技场守门（只留赢的）
```bash
/root/miniconda3/envs/kaggle-eval/bin/python meta_pipeline/arena_gate.py \
    parent:farm2945_dev/v54_pairgate.py cand:farm2945_dev/v54_pg_mylayer.py \
    --loss-dirs fresh_losses_batch3 pairgate_live_losses v54pg_live_losses
```
- 判定：215 池胜率不降 >0.5pp；h2h 与败局均分不低；全过才考虑提交；
- 一项不过 → 回滚，机制记入 `farm2945_dev/V53_PREDICT_RESEARCH_*.md` 判负。

## 5. 提交（用户点头后）
- 打包 `main.py`（tar 内只含 main.py，mtime=0，mode 644）；
- `kaggle competitions submit kaggriculture -f <tar> -m "<机制一句话>"`；
- 记回执文件 `SUBMISSION_RECEIPT_*`，并立刻盯爬分（episodes API 每 30 分钟）。

## 循环纪律
1. 每天第一件事跑 step 1，新 Ahmed 版本出现时立刻评估同轮移植；
2. 每轮只加一个机制，宁可小、要可验证；
3. 判负的机制也留档（负面证据防止重复试）；
4. 4-5 小时是 meta 刷新周期，验证超过这个窗口的候选作废重验。
