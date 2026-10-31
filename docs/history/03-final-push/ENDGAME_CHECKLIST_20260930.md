# 收官清单（2026-09-30 10:40 北京）

## 0. 关键时间（北京）

| 时刻 | 事项 |
|---|---|
| **09-30 22:00** | **最后有效提交窗口**（之后提交来不及爬分，按 goal 规则不再新开） |
| 10-01 07:59 | 比赛截止（= 09-30 23:59 UTC） |
| 每日 08:00 | 配额刷新（今日 5 发，已用 0） |

## 1. 当前两槽（截至 6h 判读 09:11 北京）

| 槽 | 内容 | 分数 | 战绩 | 2000+ 胜率 | <2000 |
|---|---|---|---|---|---|
| 56685648（较老） | `cand_snk6_cam30.tar.gz`（tar sha `c278a067…`） | **2274.1** | 57-36（61.3%） | **53.8%** | 15-0 |
| 56685653（较新） | `cand_snk6_tl_gate2.tar.gz`（tar sha `1a6c01b0…`） | 2208.8 | 49-42（53.8%） | 44.7% | 15-0 |

* FIFO：**下一发先顶掉 cam30（较老）槽**；再一发顶掉 gate2。
* cam30 的 93 局实测里**对 <2000 对手 0 负**（低分防守成立）。
* 面板里那唯一一局"<2000 败局"（ep115389786）是 **fid=1.68 的伪影**（真实战绩是胜），
  按 clean-both 规则剔除 ⇒ **真实低分战绩 30-0**。

## 2. 本地证据一句话总结

* 新鲜 184 局面板：cam30 119-65（2000-2400 段 89-63 = 58.6%）。
* 今天扫过 **22 个变体 + 3 个老候选**：无一真正超过 cam30；
  最强"字面过门"者是 `ca_buf12`（+1 局 / 184，五池零回归，已打包 + smoke）。
* **校准结论**：面板在 ±2 净翻转内与线上排名相反（gate2 面板 +1、线上 −65 分）
  ⇒ 不要为 +1 级别的候选花配额。

## 3. 提交选项（都要负责人批准；默认 = 不做）

**0. 首选（12:45 北京新增）：`cand_w2_120`（三段式结构拼接）**
   * 改动：d12-19 → 路线 104、d20-26 → 路线 120（原为整段 112）；
   * 证据：7 池 1342 局 **+43 净翻转**（51 翻回 / 8 吐出），主战场 2000-2400 段
     **59.9% → 66.7%**；live184 +10、cur163 +18、nem14 +5、arena +2、b2000_2400 +5、fresh62 0；
     两个新鲜守卫**低分零干净回归**；
   * 物件：`cand_w2_120.tar.gz`（tar sha `efb63eb6…`，smoke 89,571 双 DONE）；
   * 命令见 `RECEIPT_cand_w2_120_20260930.md`；FIFO 顶掉较老 cam30 槽 → `[gate2, w2_120]`。
2. **守槽（保守）**：两槽不动。等待 4h/6h 后再读一次分数，评估是否需要在 22:00 前动作。
3. **双 cam30**（2 发）：[cam30] → [cam30, cam30]。适合"只求稳、不要 A/B"；
   代价：新槽从 600 爬 4-6h，失去 gate2 对照。
4. **彩票单发**：`cand_ca_buf12.tar.gz`（tar sha `f5f5d2ad…`，smoke 89,685 双 DONE），
   顶掉 cam30 槽 → [gate2, ca_buf12]。期望 ≈ 0，仅当想赌"新槽爬得比老槽高"。
5. **不推荐**：rmax96 / slh48 / h120ch99 / gate2b / mid104 / w1_104（后者已被 w2_120 支配）。

## 4. 执行命令（批准后用）

```
# 双 cam30
/root/miniconda3/envs/kaggle-cli/bin/kaggle competitions submit -c kaggriculture \
  -f /root/autodl-tmp/farm2945_dev/cand_snk6_cam30.tar.gz -m "cam30 resubmit #1 (double-cam30)"
/root/miniconda3/envs/kaggle-cli/bin/kaggle competitions submit -c kaggriculture \
  -f /root/autodl-tmp/farm2945_dev/cand_snk6_cam30.tar.gz -m "cam30 resubmit #2 (double-cam30)"

# 彩票单发
/root/miniconda3/envs/kaggle-cli/bin/kaggle competitions submit -c kaggriculture \
  -f /root/autodl-tmp/farm2945_dev/cand_ca_buf12.tar.gz -m "ca_buf12: +1/184, 0 regressions across 6 pools"
```

## 5. 禁止事项（本 goal 纪律）

* 未经批准不得提交；不得轮询线上分数（由负责人盯）；
* 不再对 <2000 段有任何干净回归的候选抱希望（一票否决）；
* 不删除 `live_corpus` / `runs/` / 收据 / 文档。
