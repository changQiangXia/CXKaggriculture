# 当前两个 submission 日志与 V43 十轮实际变更审计（2026-09-16 UTC）

本审计只读取 Kaggle 当前 submission/episode 元数据、已下载 replay，以及本地 parent 和已提交源码；没有修改模型，也没有再次提交。重点是回答：十轮优化到底改变了什么，为什么线上结果没有达到预期。

## 线上当前事实

Kaggle API（`/root/miniconda3/envs/kaggle-cli/bin/python`）当前返回：

| submission | artifact | public score | episodes | 胜/负/和 | 平均自身−对手 reward | 最差局 |
|---|---|---:|---:|---:|---:|---:|
| `56260878` | `v43_optimized_final.tar.gz` | **2272.8** | 101 | 85/14/2* | +19,188 | −7,801（episode `109430701`） |
| `56257428` | `nathan_cautious_final.tar.gz` | **2644.5** | 127 | 74/46/7* | +3,745 | −6,564（episode `109437616`） |

\* 和计数按 margin=0 统计；表内 episodes 是可见 competitive episodes。两者使用不同时间段、对手池、匹配 rating，不能把 public score 或平均 margin 当成严格 paired 因果比较。V43 的 score 比 Nathan 低 371.7 分，足以说明当前 V43 候选没有形成线上优势，但不能单独证明 TERM16 是负收益来源。

V43 最差两场是：

- episode `109430701`：V43 `108430`，对手 `116231`，margin `−7801`，对手 Sadettin Şamil Verdil；
- episode `109438141`：V43 `80212`，对手 `84678`，margin `−4466`，对手 LH-and-FPGA。

所有已查询 episodes 状态为 `COMPLETED`；此前两 submission 的失败日志也没有 stderr、超时或 720-step 中断迹象。因此目前没有“十轮代码导致加载崩溃”的证据。

## 十轮实际提交代码的差异

已冻结 parent：[research_kaggle_ahmed/decoded_main.py](/root/autodl-tmp/research_kaggle_ahmed/decoded_main.py)，SHA-256：

```text
919fc1d61050cd96f799979e49177ae3ac7bce98ec9835724238bea73f4a08ed
```

已提交 candidate：[v43_optimized_final.py](/root/autodl-tmp/v43_real_20260916/v43_optimized_final.py)，SHA-256：

```text
38f65166f5241fa73d78fea781cd3f98de62772805292a75396b76a7db43a3bd
```

两个文件逐行 diff 显示：candidate 的前 3,366 行与 parent 完全一致，candidate 只在末尾增加 102 行 `TERM16` wrapper。也就是说，十轮中第 1–8 轮的 loader 审计、market-slot 反例、atomic/prefund/append-only 消融没有作为 gameplay 机制进入最终包；它们是测试和拒绝记录。最终真正留下的玩法改变只有一个：终局肥料回收。

关键代码位置（candidate）：

- line 3371：`_TERM16_PARENT = agent`，父 controller 被保存；
- lines 3385–3416：step 717 收集 fertilizer 的尝试；
- lines 3411–3412：只有 parent market 全部是合法 `SELL` PRODUCTS 时才继续；
- lines 3400–3409：完整字段重放，要求 parent shed/seeds 不变、精确 inventory 增量、总容量不超过 100；
- lines 3418–3448：step 718 验证预留位置/库存，调用 parent，并将预留 actor 改成 `DROP`；
- line 3445：在原 market order 列表末尾追加 `['SELL','FERTILIZER',extra]`；
- lines 3450–3465：只在 step 717/718 激活，其他 step 原样调用 parent；
- line 3468：`agent=globals().pop('agent')`，确保文件 loader 取到最终 wrapper。

因此 TERM16 不能改变早期种植、雇工、动物购买、feed/care、shop route、普通销售时序，也不能修复日志中 step 403–409 或 step 575 之后发生的长期现金分叉。它最多在最后两次 callback 恢复一个每名合资格 actor 的 fertilizer 单位，并为该单位增加一个末端 SELL slot。

## 为什么十轮优化没有带来好的线上结果

第一，修改和问题的时间尺度不匹配。之前日志暴露的 Nathan 近镜像败局，首个现金差集中在 step 403/404/409 的 SELL 时序；inspired 的大败局从 step 575 后扩大。TERM16 只观察 717/718，既不能改变这些分叉，也不能改变前 29 天的库存和现金路径。即使每次成功 salvages 1 fertilizer，金额上限也只是一个单位的销售收益加其对市场价格的微小影响，远小于 −4,466/−7,801 的败局差距。

第二，激活条件很窄。代码要求 idle、空库存、站在四个 shed access tile、动物 tile 上有未收集 fertilizer，而且 parent 本回合的所有 market rows 必须是合法 SELL；step 718 还要求 parent orders 小于 10。这些约束是安全证书，却把机制变成稀疏补丁。此前本地 16 局 panel 只有 seed `162017` 双 seat 各激活 1 单位；其他 14 局零激活。线上 candidate 的低分不能由“机制普遍生效”解释，因为它大部分对局仍然等于 parent。

第三，实验验收存在收益上限与配对不足。原报告中 `+4` 的局部收益来自 1 fertilizer/seat；没有证明该收益跨 seed、route、对手族、双 seat 稳定存在。线上 V43 和 Nathan 没有同 seed/同对手配对，不能用两者 score 直接估计 TERM16 delta。正确验证需要同一 observation/seed/对手的 candidate-parent action replay，统计 activation、step 717/718 的真实成交数、24/72-step 后现金与库存，以及最差分位数。

第四，十轮的“数量”主要是审查轮次，不是十个独立的策略改进。源码 diff 是硬证据：atomic-only、seed-prefund-only 和 append-only terminal sales 均被拒绝，未进入最终文件。将“做了十轮审计”写成“十轮优化带来十轮玩法变化”会高估候选实际改变。

## `_TERM16` 状态机的审计结论

已确认的安全点：

- 保存父 controller，并在最终 line 3468 重新插入命名 `agent`，避免旧 callable 被 file loader 选中；
- 不读取对手 private shed/inventory；
- 不重排 parent market order 前缀；
- step 718 对预留位置、库存、shed/seeds replay 和容量作验证，失败回退 parent；
- 只追加 `SELL FERTILIZER`，不使用不存在的 `SELL_ANIMAL`。

仍然存在的收益/覆盖限制：

- `_term16_collect` line 3412 拒绝任何含 BUY 或其他非 SELL 的 parent market action，故许多正常终局状态直接不触发；
- line 3445 新增 SELL 虽保留己方前缀，但仍会改变共享 market 的库存/价格，不能由“前缀未变”推出整局等价；
- 只比较 parent shed/seeds 和本地 inventory 预期，没有跨 717→718→719 的完整 opponent market 反事实证书；
- reservation 依赖连续 callback step 717→718 且以 player 为 key。正常 Kaggle agent 进程满足这一点，但独立多 episode 同进程重入时必须确认 step 0 reset 与 seat 隔离；
- `_TERM16_STATS` 是模块级共享 dict，只能作诊断，不能作为 reward 证据；
- 机制只覆盖 fertilizer，不覆盖日志里更大的动物组合、服务、销售时序和 day 9–11 生产差异。

## 当前应如何解释日志

当前证据支持的说法是：V43 candidate 运行完成但线上 score 低于 Nathan；十轮最终提交只增加了一个极窄的终局 fertilizer salvage；该机制的激活频率和理论收益都不足以修复线上主要败局。最合理的下一步是先用同 seed/同对手把 candidate 与 raw Ahmed V43 做动作级 paired replay，确认 717/718 是否实际激活及激活后的真实成交量，然后把研究重点转回 403–409 SELL 时序、575 之后的 production/service/capacity 路线。不要直接针对某一败局硬编码 step tape，也不要因 score 差异把所有问题归咎于 TERM16。

证据 JSON：[actual_changes_audit.json](actual_changes_audit.json)。

## 四场最差 V43 replay 的终局检查

已下载 V43 最差局的 replay，并按 episode API 的 own seat 检查 step 717–719：

| episode | margin | own seat | step 717 | step 718 | step 719 | TERM16 激活迹象 |
|---:|---:|---:|---|---|---|---|
| `109430701` | −7,801 | 0 | hand 11=`PASS` | hand 1=`COLLECT_FERTILIZER` | hand 1=`DROP` | **无**：717 没有 wrapper 插入的 `COLLECT_FERTILIZER` |
| `109438141` | −4,466 | 0 | hand 11=`PASS` | hand 1=`COLLECT_FERTILIZER` | hand 1=`DROP` | **无** |
| `109477519` | −2,221 | 0 | hand 1=`DROP`, hand 8=`COLLECT_FERTILIZER` | hand 8=`DROP` | 无额外 fertilizer sell | **无** |
| `109399843` | −1,962 | 1 | hand 8=`DROP`, hand 11=`COLLECT_FERTILIZER` | hand 8/9/10=`DROP` | 无额外 fertilizer sell | **无** |

TERM16 若激活，step 717 必须把一个原本 `PASS` 的、空库存且站在 shed access tile 的 actor 改为 `COLLECT_FERTILIZER`，并在 step 718 对同一 reservation 做 `DROP`，同时追加一个小数量 `SELL FERTILIZER`。这四场最差局没有这种 717→718→追加 SELL 的链条。因此它们的损失不能归因于 TERM16 的错误回收；候选与 parent 的差距仍应在更早的生产、动物、服务、容量或销售路线中寻找。

四个 V43 own-agent logs 均为 719 callbacks、stderr/stdout 为空。首 callback 约 0.36–0.50 秒，p99 约 0.008–0.014 秒，只有首 callback 超过 0.2 秒；没有 timeout/异常证据。完整日志存于 `current_submission_diagnosis_20260916/logs/`。
