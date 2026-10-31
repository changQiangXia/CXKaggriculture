# 候选回执：`cand_ca_buf12`（2026-09-30 10:20 北京）

**一句话**：这是今天唯一"字面通过全部本地闸门"的变体，但效应量只有 +1 局 / 184
（+0.6pp），低于可信区间；**默认不建议提交**（详见第 4 节）。

## 1. 物件

* 路径：`/root/autodl-tmp/farm2945_dev/cand_ca_buf12.tar.gz`
* tar sha256：`f5f5d2ad93f6fa0bc11842668d6a91a1eb4bb8c0b0cd169d8b1442aca6a1f578`
* main.py sha256：`1bff3716ff2eb447a3b357fde340ed5769f3b58cacafffb231d7642f286aadd1`
* smoke：我方收益 89,685（门槛 50,000）、statuses `['DONE','DONE']` → OK
* 臂源码：`/root/autodl-tmp/georgy_arena/arms/ca_buf12/main.py`
* 唯一改动：`_CA_BUFFER` 8 → 12（胡萝卜主互换时保留的缓冲量；其余与 `cand_snk6_cam30` 完全一致）

## 2. 验证矩阵（vs cam30，同局配对）

| 池 | cam30 | ca_buf12 | 净翻转 |
|---|---|---|---|
| live184（最新线上 184 局） | 119/65 | **120/64** | **+1**（1 翻回 / 0 吐出） |
| arena400 | 378/22 | 378/22 | 0 |
| fresh62 | 59/3 | 59/3 | 0 |
| cur163 | 90/73 | 90/73 | 0（1/1） |
| nem14 | 3/11 | 3/11 | 0 |
| cam30-112 | 84/28 | 84/28 | 0 |
| <2000 段（live184） | 29/1 | 29/1 | 0（无干净回归） |
| 2000-2400 段（live184） | 89/63 | **90/62** | +1 |

## 3. 闸门核对

* 胜场净 ≥0：✅（全池非负）
* 2000-2400 ≥ cam30：✅（+1）
* <2000 零干净回归：✅
* 跨池不留负：✅
* **但**：净效应 +1 局落在今天新发现的"面板不可信区间"（±2 净翻转）内
  —— 同面板上 gate2 也比 cam30 高 +1，线上 6h 实测却低 65 分（2274 vs 2209）。

## 4. 提交建议（需负责人批准）

* **默认不交**：FIFO 会先顶掉当前最强的 cam30 槽（2274 分），新槽需 4-6 小时爬回平台，
  而期望收益 ≈ 0；两张牌的成本远大于 +1 局的期望。
* 若负责人要"买彩票"：单发即可（顶掉 cam30 槽），队列变 `[gate2, ca_buf12]`；
  不建议连发两枚（会同时失去两台已验证的槽位）。
* 提交命令（需批准后执行）：
  ```
  /root/miniconda3/envs/kaggle-cli/bin/kaggle competitions submit \
    -c kaggriculture -f /root/autodl-tmp/farm2945_dev/cand_ca_buf12.tar.gz \
    -m "ca_buf12 (CA_BUFFER 8->12): live184 +1 win, 0 regressions across 6 pools"
  ```
