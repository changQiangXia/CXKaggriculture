# Day‑2 active replay report (2026‑09‑13)

本报告只分析已有 active submission，未执行提交。监控目标当前为 `56190357`（h5room623）与 `56185929`（h5sim96）。

## 当前结果

| submission | competitive games in cache | wins | losses | ties | mean signed margin (wins/losses by own seat) | public score |
|---:|---:|---:|---:|---:|---:|---:|
| 56190357 | 13 | 5 | 8 | 0 | −4,370 (signed reward margin mean) (loss-heavy; one −49,779) | 2714.4 |
| 56185929 | 79 | 63 | 16 | 0 | (not recomputed; 63/79 wins) overall | 2744.4 |

`56190357` was accepted only recently, therefore sample size is small, but its first 13 competitive games are materially worse than the older h5sim96 queue. Do not use this as a final rating estimate yet; it is nevertheless a strong regression signal.

## h5room623 loss evidence

All eight currently cached losses were replayed. At decision step 623 (day-end), the candidate frequently inserts an extra capacity-protection `SELL` while the farmer is carrying 82–105 items and shed has only 13–28 items. At the next recorded state the carried inventory is zero and shed is ~89–100, proving that the guard changes the market before automatic drop. Examples:

- episode `108330866`: step 623 `SELL WOOL 100`; shed 15 + carried 85. At 624 shed 98, carried 0; final margin −2965.
- `108331848`: step 623 `SELL FERTILIZER 2`; shed 14 + carried 105. At 624 shed 100, carried 0; margin −256.
- `108333303`: step 623 `SELL FERTILIZER 2`; shed 28 + carried 86. At 624 shed 89, carried 0; margin −49,779 (strong opponent).
- `108347674`: step 623 `SELL FERTILIZER 2`; shed 13 + carried 99. At 624 shed 100, carried 0; margin −1,929.
- `108348534`: step 623 `SELL FERTILIZER 2`; shed 14 + carried 105. At 624 shed 100, carried 0; margin −1,181.
- `108350906`: step 623 `SELL WOOL 100`; shed 16 + carried 82. At 624 shed 99, carried 0; margin +4,555 in our favor (a win by reward, despite state label from an earlier seat check; verify seat when aggregating).
- `108351343`: step 623 `SELL FERTILIZER 2`; shed 16 + carried 99. At 624 shed 100, carried 0; margin −458.
- `108355982`: step 623 `SELL FERTILIZER 2`; shed 13 + carried 99. At 624 shed 100, carried 0; margin −755.

At step 695 the candidate also emits bulk sells (`WHEAT 1000`, `FERTILIZER 998`, `EGG 996`) as part of final liquidation; this is inherited behavior, not the new guard. The key new behavior is the day‑end step‑623 sell, which reorders shared market transactions and can lower/raise both players' prices. In fixed real-opponent counterfactuals from prior day, the same guard changed margins inconsistently (Roshan −2126→−2421, hidenov −126→−411, Kostiantyn −1525→−1512).

## Win/loss commonality

The candidate's action counts are almost identical in wins and losses (roughly 1,100–1,220 WATER, 470–516 HARVEST, 367–417 FEED/CARE, 239–249 PLANT, ~370 COLLECT_FERTILIZER). There is no runtime failure: 720 steps, no stderr, normal callback duration. This rules out broken watering, route termination, or timeout as the primary cause.

The differentiator is market interaction. Losses have more SELL calls than wins (about 429 vs 406) and substantially stronger opponents. Premium outputs (MILK/STRAWBERRY/WOOL) are sold on a shared dynamic market; adding the step‑623 sale can shift order position and prices. The catastrophic −49,779 game is opponent strength/outlier, but the repeated small losses around −0.3k to −3k indicate market timing, not capacity overflow alone.

## Recommendation for candidate generation

1. Treat `h5room623` as a regression candidate; do not use it as the baseline for three new submissions.
2. Preserve h5sim96/V37 market order. Build variants that **disable the step‑623 extra sell by default**, or gate it only when a strict predicted overflow remains after all ordinary planned sells and when the item is low opportunity-cost fertilizer/wheat. Test with fixed-action real replays and 30+ local opponent games before considering submission.
3. Keep the existing monitor single-process. It should collect both win and loss replays where possible; logs endpoint is currently downloaded only for tie/loss by design.

