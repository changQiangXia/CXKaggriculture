# 重复定义常量的"活性地图"（2026-09-28）

**问题**：`pkg_race_rmax96/main.py`（1MB，多层组装产物）里同一常量被赋值多次，
**后者覆盖先前者**。历史上已出现过两处值不一致却照样打包的情况
（`pkg_sn24` 的 `_OR2_SN_K` = L4758:0 / L8048:1）。
用户问：要不要改代码来增加严谨度？

## 方法（不靠推断，靠实测）

每个常量造两条探针臂（只改早处 / 只改晚处），在**家族面板 470 局**上同种子配对，
与现役基线做**逐位比较**（差值恒为 0 才算"死"）。

| 常量 | 早处站点 | 晚处站点 | 只改早处 | 只改晚处 | 判定 |
|---|---|---|---|---|---|
| `_OR2_SN_H` | L4759 (48) | L8050 (48) | **Δ=0.0，470/470 逐位相同** | 生效（89.6%→74.7%） | 早死 / 晚活 |
| `_CA_MARGIN` | L4502 (−5.0) | L8026 (−15.0) | **Δ=0.0 逐位相同** | 生效（89.6%→83.0%） | 早死 / 晚活 |
| `_CA_FEED_DAYS` | L4505 (1) | L8046 (0) | **Δ=0.0 逐位相同** | 生效（89.6%→74.7%） | 早死 / 晚活 |
| `_RACE_HORIZON_CLONE` | L5803 (8) | L6054 (9) | **Δ=0.0 逐位相同** | **Δ=0.0 逐位相同** | **两处全死**（常量从未被读） |
| `_OR2_SN_K` | L4758 | L8048 | —（同源模式，晚处活） | — | 早死 / 晚活 |

原始数据：`panel_runs/w6/probe_dupe_sites.json`、`panel_runs/w6/probe_dupe_three.json`
（复现命令见本文件末尾）。

## 结论：不要改成品；要加护栏

**不推荐改动 `pkg_race_rmax96/main.py`**：

1. **重复不等于错误**。该文件的组装机制就是"每叠一层就重绑一次 `agent`"
   （`agent` 共 51 处重绑），这是**设计**，不是毛病；
   `_OR2_*` 的早处副本是**组装残留**，实测**改它等于没改**（470/470 逐位相同）。
2. **改动没有收益、只有风险**。清理是纯外观收益；而重写一个 1MB 成品会动到
   我们所有实验的**共同底座**，还会使收据/哈希链失效。
3. **真正需要防的是"改错地方"和"静默漂移"这两类事故**，它们由工具解决，不由重写解决。

**推荐做法（已实施 / 待挂接）**：

| 措施 | 状态 | 说明 |
|---|---|---|
| `const_audit.py --pkg` | ✅ 已写 | 列出全部重复/冲突/门控站点与**生效值** |
| `const_audit.py --diff A B` | ✅ 已写 | 区分"生效值变化"与"仅站点漂移（危险）" |
| `const_audit.py --expect K=V` | ✅ 已写 | 建臂后断言生效值 = 预期，防止白跑一轮 |
| 建臂流程统一走 `--expect` | ⬜ 待挂接 | 建议接进 `pack_candidate.py` 之前 |
| 新包采用"末尾唯一 PARAMS 覆盖块" | ⬜ 待办 | 只对**新**包生效，旧包零风险 |

**若坚持要清理**（可选、需授权）：只对**新生成的包**删除早处死代码，
然后在 470 家族 + 719 全局 + 381 holdout（合计约 1,570 局）上证明**逐位等价**，
再重跑 smoke 并重新打包。收益是外观与可读性，代价约 30 分钟算力 + 一次重验证。

## 附：复现命令

```bash
# 建探针（只改一处）后，同种子配对跑家族面板
python pool_live_losses.py --arms base=pkg_race_rmax96/main.py \
    firstOnly=pkg_probe_first/main.py secondOnly=pkg_probe_second/main.py \
    both1=pkg_sn1/main.py --replays /root/autodl-tmp/live_corpus/replays \
    --episodes panel_runs/w6/v4family_episodes.json --only-outcome "" \
    --band-lo 2000 --band-hi 9999 --workers 10 --out panel_runs/w6/probe_dupe_sites.json

# 审计任何包（strict 会在常量站点值冲突时退出码 1）
python const_audit.py --pkg pkg_race_rmax96
python const_audit.py --diff pkg_race_rmax96 pkg_rd64m192
python const_audit.py --pkg pkg_rd64m192 --expect V9_RACE_DEFAULT=64,_OR2_SN_H=48
```
