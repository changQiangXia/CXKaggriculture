# 事故报告：56617204 线上崩到 386（入口函数被劫持）

## 1. 现象

| 项 | 值 |
|---|---|
| 提交 | 56617204 `cand_am_y2_mid112_qc_fs`（09-27 19:06 UTC） |
| 线上 | **2 局全负，我方收益恒为 3,000**，对手 120,073 / 66,954，评分 600 → **386** |
| 对照 | 同族底座 `cand_am_y2_mid112`（56595299）91 局，收益 58k~161k，分数 2085 |

收益恰好 = 起始资金 3,000 ⇒ **我方 agent 全程没有行动**（等价于 PASS）。

## 2. 根因（已在本地用 Kaggle 自己的加载器复现）

Kaggle 装载提交不是找符号 `agent`，而是**取模块命名空间里"最后加入的可调用对象"**
（`kaggle_environments.agent.get_last_callable`）。

* 我们今天的两个包是**追加式包装器**：`def _qc_compact(...)` / `def _s793_reorder(...)` 是**新名字**，
  而 `agent` 这个名字在基础包里**早就存在**——之后再 `def agent(...)` 只是**覆盖**，
  它在命名空间里的**插入位置不变**。
* 结果：命名空间最后加入的可调用对象变成了 `_qc_compact` / `_s793_reorder`（**两个参数的辅助函数**）。
* Kaggle 以 `fn(observation, configuration)` 调用它 ⇒ 崩 ⇒ 整局按 PASS 处理 ⇒ 收益 3,000。

**复现证据**：
```
get_last_callable(被提交的 main.py) -> _s793_reorder
用该入口跑官方引擎一局 -> rewards=[3000.0, 186029.0]      ← 与线上完全一致
补一个入口 shim 后再跑   -> rewards=[78955.0, 80435.0]     ← 恢复正常
```

**影响面审计**：42 个候选 tar 中**只有 2 个**中招——今天新建的
`cand_am_y2_mid112_qc.tar.gz`（`_qc_compact`）和 `cand_am_y2_mid112_qc_fs.tar.gz`（`_s793_reorder`）。
**此前所有已提交过的包都解析为 `*_agent`，安全**（这也是为什么只有这一次崩）。

## 3. 修复（已完成）

1. 给三个受影响包（qc / qc_fs / ch99_qc_fs）末尾追加**新名字**入口：
   ```python
   def kaggle_entry(observation, configuration=None):
       return agent(observation, configuration)
   ```
   新名字必然排在命名空间最后 ⇒ 加载器必然取到它。
2. 重新打包，新哈希：
   * `cand_am_y2_mid112_qc.tar.gz` → sha(前24) `b840c86664ba5a8d213c9efa`
   * `cand_am_y2_mid112_qc_fs.tar.gz` → sha(前24) `11a54cd400c185de159cb4ad`
3. 校验：两个包 `get_last_callable → kaggle_entry`，并用官方引擎对 ch99 跑满一局，
   收益 78,978/80,425 与 78,955/80,435，status 均 DONE。

## 4. 新增的提交前检查（永久生效）

任何包在提交前必须过：
1. `get_last_callable(main.py) -> <函数名>` 且函数名以 `_agent`/`kaggle_entry` 结尾；
2. 用**该解析出来的入口**（不是手动 import 的 `agent`）跑一局官方引擎，收益量级正常（≥5 万）；
3. tar 根目录仅 `main.py`。
