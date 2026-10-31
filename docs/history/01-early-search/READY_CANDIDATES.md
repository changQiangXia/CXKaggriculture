# Kaggriculture 待提交候选（仅本地准备）

更新时间：2026-09-12 UTC

这两份压缩包已经准备好。用户随后明确授权尝试提交 Thomas 包；上传请求因 Kaggle 服务/网络长时间停在 0% 而未完成，当前仍没有新的 submission ref。没有新的明确授权前不得再次执行 `kaggle competitions submit`。

## 候选 A：Thomas replay router

- 文件：[ready_thomas_v6.tar.gz](ready_thomas_v6.tar.gz)
- SHA-256：`8da95498ef14755625a8f88f276b204c163259d03bbd01e2ceb4806f599c7000`
- 包内容：仅根目录 `main.py`
- 策略特点：公开 replay 路由、shop-aware schedule 选择、完整状态恢复和终局处理。
- 隔离运行（解压后直接以文件路径加载，seed 0，对 starter）：两个 seat 均 `DONE`，奖励 `183962.0 / 3504.0`。
- 隔离自战（seed 0）：两个 seat 均 `DONE`，奖励 `66496.0 / 67254.0`。

## 候选 B：Dmitrii herd-safe sale window

- 文件：[ready_dmitri_v6.tar.gz](ready_dmitri_v6.tar.gz)
- SHA-256：`a795fb4fd34361e2eed2032381f736773ea2d48fdf493746c0545b119fc87ee8`
- 包内容：仅根目录 `main.py`
- 策略特点：现金保护、后续 `PICKUP`/`PLACE` 资源保护、3-action sale window、状态级终局清仓。
- 隔离运行（解压后直接以文件路径加载，seed 0，对 starter）：两个 seat 均 `DONE`，奖励 `180394.0 / 3510.0`。
- 隔离自战（seed 0）：两个 seat 均 `DONE`，奖励 `69506.0 / 69506.0`。

## 候选 C：community_flex 稳健版（关闭罕见羊群分支）

- 文件：[ready_flex_v7.tar.gz](ready_flex_v7.tar.gz)
- SHA-256：`155573354f2c41d4d52ea2d5f0f1c41fd0b88cca9fb3965f75645847fdc52f38`
- 改动：仅将 V233 sheep discovery overlay 的资格判断关闭；保留原有 route、状态恢复和 V224 销售重排。
- 理由：羊群分支在强对手上触发稀少且增加 matchup 方差；此前消融显示关闭后多数 seed 不降，部分强对局提升。
- 新回归（本地官方环境、seed 0–2）：对 Thomas `3/3` 胜（资金分别 `64414:61902`、`107092:101751`、`104257:102100`）；对 Dmitrii `2/3` 胜（`63942:64197`、`147178:145651`、`100702:98922`）。全部状态 `DONE`。
- 该包只含根目录 `main.py`，尚未上传。

## 候选 D：Ahmed V37 more-yield / smarter-labor 派生版（已提交 ref 56178383）

- 文件：[public_v37_candidate.tar.gz](public_v37_candidate.tar.gz)
- SHA-256：`4babc9e9d84a070eb72e006af6cf06ce435d7adab8db6c186540ca63daf055fa`
- 包内容：仅根目录 `main.py`，无外部 `actions.json` 或模型权重依赖。
- 来源：公开 V37 notebook（source SHA-256 `94c1c2c05ae7cde8fca9ee3957b01112c1cbab82c7434aae6a5f24fa7485bc4c`），保留其四回合 stock reservation 与 smarter-labor 门控；作为本地衍生候选，不是原样提交。
- 社区报告：在 reacting 1856 局中相对 V36 为 `1786/70/0`，但独立 elite 136 局为 `81/55` 且 qualification gate 未通过，因此只能视为有希望的低风险实验，不能把公开数字当成保证。
- 扩展本地面板（公开调参/holdout/smoke seed 共 31 个，每个对手双 seat，共 62 场）结果：对 Flex `61-1-0`、平均差 `+2960.7`，对 Thomas `61-1-0`、平均差 `+7504.9`，对 Dmitrii `62-0-0`、平均差 `+6120.2`；最差差值分别为 `-1146`（seed 9019）和 `-550`（seed 9004），全部 `DONE`、无运行时错误。详见 [V37_PANEL_RESULTS.md](V37_PANEL_RESULTS.md)。这仍是本地证据，不能直接等同线上排名。

基于该扩展面板，V37 暂列本地验证首位（对三个候选合计 `184-2-0`，无错误）；由于公开 elite panel 未增加胜局，仍保留风险标记，必须等用户明确授权后才可提交。

## 双向对抗验证（本地官方环境，seed 0–4）

| 对局 | seat 0 胜/负/平 | 平均资金差（seat 0 - seat 1） | 最差资金差 |
|---|---:|---:|---:|
| Thomas vs Flex | 0 / 5 / 0 | -4206.4 | -5803 |
| Flex vs Thomas | 5 / 0 / 0 | +3835.8 | +383 |
| Thomas vs Dmitrii | 1 / 4 / 0 | -3044.8 | -5232 |
| Dmitrii vs Thomas | 4 / 1 / 0 | +2944.6 | -1143 |

所有上述 20 个 seat-run 都完成 720 步且状态为 `DONE`。本地资金差只用于稳定性和错误检查，不能直接等价为 Kaggle leaderboard 分数；比赛实际按 head-to-head 胜率匹配。

## 打包检查

- 两个 tar 包都可由 `tar -tzf` 正常读取。
- 每个包都只有 `main.py`，不存在 `actions.json`、模型权重或外部相对路径依赖。
- 两个候选均通过解压后隔离加载测试和完整 720 步运行。
- 当前没有执行提交命令，也没有消耗新的提交额度。
