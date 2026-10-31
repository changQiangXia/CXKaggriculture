# Nathan pipe-4 vs Ahmed V43 对比

## 结论

目前没有足够证据宣布一个稳定赢家。

- 按作者自报的 200 局 colosseum：Nathan pipe-4 声称显著强于 raw V43（96.5% Elo rate）。
- 按可独立审计的本地 engine：两者几乎完全相同；16 个 seed、双 seat 的 32 局中，15 个 seed 的差异约为 ±1，只有 seed 9004 出现 +1512 的单点优势，seed 717171 出现约 −80。总体平均 +89.4，但被一个异常 seed 主导，不能视为稳定收益。
- 因此，Ahmed V43 是证据更完整、风险更低的基线；Nathan pipe-4 是有一个可能有效的 turn-1 假设的研究变体，暂时不能确认更强。

## 建议的检测办法

1. **源码和依赖冻结**：记录两个解码源的 SHA、route 数量、配置和所有 wrapper；确保每个进程重新加载模块，避免跨 episode 状态污染。
2. **共同随机数 paired panel**：相同 seed、相同 seat、相同 opponent，分别运行 Nathan/Ahmed；比较最终 bank coins、relative margin、W/L/T、stderr 和 720-step 完成率。
3. **分层统计**：按 seed、seat、route、shop opening 和对手策略族分层；报告均值、中位数、5% 分位数、负局数和 seat variance，禁止只看聚合 Elo。
4. **动作级差分**：在每个回合记录两模型 action，定位第一处 divergence；检查差异是否只发生在 route[0]/route[1]，以及后续是否引发 hires、animals、feed、shed 或 terminal 行为变化。
5. **机制消融**：至少比较 raw Ahmed V43、Nathan 的 bakery-only flip、所有 route minimal-wheat、minimal-wheat 加 early hires 四个版本；每个版本使用同一 seed panel。
6. **泛化 holdout**：开发 seed 与确认 seed 分离，执行 leave-one-opponent-out、leave-one-time-block-out、未见公开 agent、双 seat；最终 holdout 只运行一次。
7. **物理账本审计**：核对 market order cap、cash、seed、animal purchase、shed capacity、dawn overflow、feeding 和 final liquidation；作者声称的 cluster/replay 结果不能替代这些可复核检查。
8. **线上验证**：只有通过本地 holdout 后才提交一个版本，提交后读取 episode/replay/log；若线上分数与本地差异巨大，先定位环境或 runtime 兼容问题，不继续盲目改策略。

## 当前本地结果

| seed | Nathan−Ahmed（seat 0） | Nathan−Ahmed（seat 1） |
|---:|---:|---:|
| 9001 | +1 | −1 |
| 9002 | +1 | −1 |
| 9003 | +1 | −1 |
| 9004 | +1512 | +1510 |
| 9005 | +1 | −1 |
| 9006 | +1 | −1 |
| 9007 | +1 | −1 |
| 9008 | +1 | −1 |
| 70117 | +1 | −1 |
| 184901 | +1 | −1 |
| 717171 | −79 | −81 |
| 其他 5 个 seed | +1 | −1 |

32 局全部 `DONE/720`。完整结果在 `/root/autodl-tmp/public_compare_panel.json`。
