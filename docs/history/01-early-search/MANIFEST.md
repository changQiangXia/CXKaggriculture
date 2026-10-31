# 两个待提交候选（未提交）

生成时间：2026-09-13。两个归档均只有根目录 `main.py`，已通过 `py_compile`。

## A: h5sim96

- 基于当前线上最高分 submission `56185929` 的源码。
- SHA256: `7122946a224c172ed033533b429fea4c97010d94bdbe8dfd6c10ff8caac265d3`
- 证据：未见 V37 seed 9001–9010 + 镜像 seed 双席 22/22 胜，最小边际 +740；历史 replay seed 双席 30/30 胜，最小 +443；线上当前 126W/77L（截至 monitor state 最近扫描，统计随新对局继续变化）。
- 限制：Thomas 公开面板曾出现单局约 -556，不能宣称对所有对手无风险。

## B: h5sim96_cap2

- 只将 V231 牛替换上限从 4 改为 2；其余策略完全继承 h5sim96。
- SHA256: `54c2802787ffd3deb987f0b40fa04dced4f90e64a20a89e70b959910dd667d38`
- 证据：未见 V37 12001–12010、13001–13005 双席共 50 局全部胜，最小边际约 +769；Flex/Thomas/Dmitrii 各 10 局面板全部胜；E776/E773 顶级公开代码面板 16/16 胜；近期线上 replay 中 cap2 与 cap4 通常行动完全相同。
- 限制：它是低风险多样性候选，没有证据证明能直接修复当前线上共享市场败局；只在一次请求超过 2 头牛时才与 h5sim96 分叉。

## 否证过的候选

- `overflow695`：真实固定线上 action-tape 三局均较父策略少约 259–441 金币。
- `overflow623-only`：Thomas seed 9004 seat1 为 -614。
- `overflow623_big8`：Thomas seed 9004 seat1 仍为 -614。
- `cap2_margin20`：public_v37 面板出现 -455。
- `room623/room623_695`：线上明显回归，额外 SELL 改变共享市场顺序。

## 提交纪律

这里只准备归档，不调用 Kaggle submit。只有收到用户明确提交指令后，才会逐个执行上传，并在每次上传后核验 submission id、状态和 active queue。
