# 线上语料库（增量式）：使用说明

2026-09-25 建。**只读**拉取我方提交的公开 replay，不做任何提交。

## 目录布局

```
/root/autodl-tmp/live_corpus/
  replays/episode-<id>-replay.json.gz   # 每局一份，gzip-9（约 70×，28MB -> 0.4MB）
  index.json                            # 每局元数据 + 每 ref 游标（max_id / last_pull）
  refs.txt                              # 监视中的 submission ref 列表
  refs/<ref>_wins|_losses|_ties/        # 指向 gz 的软链，便于直接扫目录
/root/autodl-tmp/live_<ref>_losses/     # 按需展开的明文 JSON（给现有分析工具用）
```

## 一条命令做增量补充

```bash
bash /root/autodl-tmp/farm2945_dev/live_pull.sh            # 全部 ref 增量 + 展开败局
bash /root/autodl-tmp/farm2945_dev/live_pull.sh 56530265   # 新增/刷新单个 ref
bash /root/autodl-tmp/farm2945_dev/live_pull.sh --no-expand  # 只拉不展开（最快）
```

底层等价调用：

```bash
python pull_incremental.py --all --workers 8                        # 只拉新增
python pull_incremental.py --refs <ref> --expand losses --dest ...  # 展开某类
python pull_incremental.py --refs <ref> --no-download               # 只看列表
```

## 当前状态（2026-09-25 05:05 UTC）

| ref | 包 | 局数 | 战绩 | max_id |
|---|---|---:|---|---|
| 56530265 | candidate_final | 102 | W63 / L39 | 113151211 |
| 56524401 | archplus | 121 | W76 / L45 | 113147638 |

对手中位分 2,600（最高 2,764）；败局对手中位 2,619 / 2,683（比各自对手总体更强）。

## 空间

* 全网语料 **81 MB**（223 局 gz）；展开的败局明文 2.7 GB（84 局，供分析工具直接读）。
* 天梯增量 ≈ **90 MB/天**（两 ref 合计 200–250 局/天 × 0.36 MB）。
* 需要腾空间时：`snh48_all_*`（8.8 G）、`am_all_*`（8 G）、`github_kaggriculture_repos`（5.7 G）
  都可用同一套 gz 方案压缩（约 70×）。

## 与现有工具衔接

```bash
python am_revival_bench.py --arm ARM.py --corpus /root/autodl-tmp/live_56530265_losses
python am_flowledger.py  --arm ARM.py --corpus /root/autodl-tmp/live_56530265_losses --workers 12
python mix_audit.py      --corpus /root/autodl-tmp/live_56530265_losses
```
