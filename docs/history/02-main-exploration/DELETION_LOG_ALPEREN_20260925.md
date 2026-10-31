# 删除/隔离记录：ALPEREN AYDIN 的 agent 副本（2026-09-25，用户授权）

## 1. 触发原因

`farm2945_dev/main.py` 与 `farm2945_dev/submission.tar.gz` 是解码 ALPEREN notebook 时落错的副本：

* `main.py` sha256 = `f3be6392671608e9a575145c6caba4ab2f76d44b7ed64cdc086c8bcf845b541a`
  = ALPEREN `kaggriculture-market-rhythm-sale-policy` 自我声明的源码哈希；
* `submission.tar.gz` sha256 = `015d1a895533c262a52534c5ff157efb99ee3aedcfdd889dc349606e2ac46ad8`，
  包内唯一成员 `main.py` 与上面同一份。

任何"从项目根打包 `main.py`"或"上传项目根 `submission.tar.gz`"的流程都会**把他的 agent 当成我们的提交**。

## 2. 已执行的动作（可恢复的隔离，不是不可逆删除）

| 原路径 | 现在位置 | 移动前 sha256（移动后已复核一致） |
|---|---|---|
| `farm2945_dev/main.py` (361,915 B) | `_quarantine_alperen_20260925/farm2945_dev_root/alperen_market_rhythm.source.py` | `f3be6392671608e9a575145c6caba4ab2f76d44b7ed64cdc086c8bcf845b541a` |
| `farm2945_dev/submission.tar.gz` (147,768 B) | `_quarantine_alperen_20260925/farm2945_dev_root/alperen_market_rhythm.archive.tar.gz` | `015d1a895533c262a52534c5ff157efb99ee3aedcfdd889dc349606e2ac46ad8` |

隔离时**同时改名**（去掉 `main.py` / `submission*` 这两个会被打包 glob 命中的名字），
所以任何 `**/main.py`、`submission*.tar.gz` 的扫描都不会再碰到它们。

## 3. 全仓指纹扫描（改名前，12 处命中）

指纹 = 5 个解码 payload 的 sha256；扫描范围 `/root/autodl-tmp`（排除 site-packages / .git / GitHub 镜像包）。

| 位置 | 内容 | 处置 |
|---|---|---|
| `farm2945_dev/main.py` | market_rhythm | **隔离**（见上） |
| `farm2945_dev/submission.tar.gz` | market_rhythm | **隔离**（见上） |
| `farm2945_dev/panel_arms/alperen/{market_rhythm,first_in_line,ready_stock,turn_one,metacounter_r1}.py` | 5 支研究臂 | **保留**（评测输入，非打包路径；已加 `__DO_NOT_SUBMIT.md`） |
| `onearena/agents/alperen5252525-*.py`（3 支） | 对手池 | **保留**（`arena.py` / `bank_fingerprint_scan.py` 的评测输入，非打包路径） |
| `public_intel/kaggriculture-metacounter-r1-scored-agent/*.py` | 原件留档 | **保留**（情报留档） |
| `onearena/agents/nathanjacob-beyond-v43-what-top-clusters.py` | 与 `turn_one` payload **同字节** | **保留**（它是 Nathan Jacob 的 agent —— 说明 ALPEREN 的 turn-one 篇是转发 Nathan 的 pipe-4，不是他的原创） |

保留项都在 `check_no_alperen.py` 的显式白名单路径里；白名单之外任何一处命中都会让打包前检查**非零退出**。

## 4. 新增的两道闸

1. `farm2945_dev/check_no_alperen.py`
   ```
   python check_no_alperen.py                  # 扫 farm2945_dev（52 个打包位文件）
   python check_no_alperen.py --scan-dir /root/autodl-tmp   # 全仓（328 个）
   ```
   结果：**✅ clean（无 ALPEREN payload 处于 main.py / submission* / *.tar.gz 位置）**，exit 0。
2. `farm2945_dev/panel_arms/alperen/__DO_NOT_SUBMIT.md`：写清来源 sha、实测结论（镜像 0-24 全败、强池 98-94 起）、
   以及"不要复制成 main.py / 不要进 pkg_*"的规则。

## 5. 恢复与彻底清除

```bash
# 需要原件时（例如复跑面板）
cp /root/autodl-tmp/_quarantine_alperen_20260925/farm2945_dev_root/alperen_market_rhythm.source.py \
   /root/autodl-tmp/farm2945_dev/panel_arms/alperen/market_rhythm.py     # 内容同 sha

# 想彻底删掉隔离副本（这一步才是不可逆）
rm -rf /root/autodl-tmp/_quarantine_alperen_20260925
```

## 6. 影响面确认

* 我们的候选包目录（`pkg_*/main.py`、`candidate_*.tar.gz`）未被触碰 —— 打包链是按**显式路径**组装
  （`build_*.py` / `ga_gate.py` / `rz2_gate.py`），不读项目根 `main.py`。
* 已提交的 archplus（main.py 1,081,355 B，sha `96ac067d5f6be0e5…`）与本次操作无关。
* 本次**没有任何 Kaggle 提交**；只做了本地文件移动 + 检查脚本。
