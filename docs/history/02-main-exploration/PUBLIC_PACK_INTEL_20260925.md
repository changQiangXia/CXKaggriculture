# 公开包情报：haideptry 两篇 notebook（2026-09-25 支线）

来源（Kaggle public notebooks，已用 `kaggle kernels pull` 拉下并解出内嵌源码）：

| notebook | 内嵌 main.py | 行数 | sha256(前16) |
|---|---|---:|---|
| `haideptry/the-2965-master-hybrid-engine` | 1,045,228 B | 7,374 | `cda529cb6b359fc4` |
| `haideptry/the-shepherds-ledger-herd-safe-sovereign` | 1,051,849 B | 7,455 | `8378f73c82db7624` |

## 1. 和我们什么关系

两份都是**我们这一脉的分支**：模块级常量与 archplus 重合 **309/344** 与 **316/348**，
函数重合 **146/165** 与 **149/167**。它们的"新东西"只有 4–6 个附加层。

## 2. 它们的自我宣传 vs 我们的实测

Notebook 声称："Outperforms the legacy 2950 baseline by +$928/game on Seed 102"、
"dominates legacy V54 by +$1,800/game"、"2965+ Master SOTA"。

我们用同一套 h2h 面板测（A = 公开包，B = 我们的 **archplus**）：

| 公开包 | 种子 | 配对均值 | sd | t | 胜/负 |
|---|---:|---:|---:|---:|---|
| master-hybrid | 1..16 | **−12,429/局** | 3,315 | −15.00 | **0 / 16** |
| shepherds-ledger | 1..16 | −387/局 | 778 | −1.99 | 4 / 12 |

官方引擎交叉复核（`make("kaggriculture")`, seed 1, 720 步）：

```
master_hybrid = 100,830   archplus = 114,434   margin = −13,604
kagsim 同一局：      −13,604        ← 逐位一致
```

⇒ 两件事：(1) 公开包的"2965"是营销数字，**不要整体采用**；
(2) 我们的 kagsim 与官方引擎在这类对局上**逐位一致**，测量管线可信。

## 3. 它们有、我们没有的层（机制摘要）

### master-hybrid (`V59.3 / v7`)
| 层 | 机制 |
|---|---|
| `_V7_CXD`（**= 我们的 `_CXD`**） | 回合内**现金卖单位置置换搜索**，保持买/雇/空槽不动，取实现收入最大者。他们的预算 `_V7_CXD_BUDGET = 800`；我们扫出 **3200 更好（镜像 +9）** |
| `_V7_MPX`（Microstructure Price Defense） | 用"推断的对手卖量 + `_r37_market_price()`"预测**下回合价跌**，只对 MILK/STRAWBERRY/WOOL、每天 12–23 时、step≥144 抢跑卖出 |
| `_V7_IG`（queue close） | 把"卖 0 单位"的死单变成空槽，再把有效卖单左移填槽（**对我们几乎无用**：实测死单仅 0.14/回合、空槽常年 8.8/10） |
| `_V7_SM`（milk-shop cash shield） | 若有 PIZZA/ICE_CREAM/SMOOTHIE 店，预测本回合结束现金 <0 时，按价格从高到低**追加卖出**补足现金缺口，避免买不起而停摆 |
| `_V7_E402`（late seed cut） | step ≥ 624 时，把 WHEAT/CARROT 种子购买量削减到"剩余 tape 真正还会种的数量"，避免买死种子 |

### shepherds-ledger (`HS4`)
| 层 | 机制 |
|---|---|
| `_HS4_T4`（bounded 1–2 turn mirror preemption + credit ledger） | 只提前 **1（或 2）回合**：若 tape 在 step+1/+2 有 MILK/WOOL/STRAWBERRY 卖单，就现在抢跑同样数量（4≤qty<100），并用"信用账本"抵扣未来计划卖单 |
| `_CXTB`（tomato counter-table） | **状态键反制表**：按城镇店表 + 对手番茄日供（0.75/格/天）+ 我们 day26–29 的 20 单位，估算期望收入，≥9000 才在末期开番茄 |
| `_HP` / `opening_liquidity` | 开局"投机往返陷阱"防护：保留 5 小麦 + 1 种子，减少 turn-1 洗单 |

## 4. 对我们有用的三条（已排期/已验证）

1. **订单簿预算**：他们在 800，我们已扫到 **3200 更优**（镜像 +9.1，t 从 5.39→6.00）——采用。
2. **抢跑窗口**：他们只提前 1–4 回合；我们实测**提前到 120 回合**最好（镜像 +69，t=5.4；160/200 饱和）——
   说明"更早卖"在我们的对局结构里更值钱，不必照抄他们的窗口。
3. **开局洗单**：他们主张"减少开局投机往返"，而我们对 2850–2950 现金带**加洗单**是有正收益的（+11 镜像）；
   两者不矛盾（他们说的是减少**无差别**往返，我们只在带内施压）。

| 暂不采用 | 原因 |
|---|---|
| IG 队列收口 | 实测死单 0.14/回合、空槽 8.8/10 ⇒ 收益上限极低 |
| 整体 V7 / HS4 层组 | 头对头比 archplus 低 12,429 / 387 每局 |
| MPX / T4 | 机制方向与我们的 SN_H=120 重叠，待用"插层生成器"（`make_port_arm.py`）单独测 |
