# High-score replay tape mining (2026-09-15)

This report mines the two preserved high-score action tapes in `public_intel/top10_archive`, rather than treating one tape as a policy to copy. The tapes are official replay-derived controls:

- NiklitaCheporev, episode `101408728`, seat 1, recorded seed `1876309088`;
- Kenjo1209, episode `102192548`, seat 1, recorded seed `2012574366`.

Both tapes contain 719 runtime actions from engine version 1.32.7. The extraction script and machine-readable output are [high_score_tape_mining_20260915.py](/root/autodl-tmp/high_score_tape_mining_20260915.py) and [high_score_tape_mining_20260915.json](/root/autodl-tmp/high_score_tape_mining_20260915.json).

## Cross-tape findings

The opening is identical in both tapes at the action level. It uses movement/plant/water setup and eight one-unit WHEAT sells during day 0. The first meaningful divergence appears around day 3. Across the remainder of the season, only 83 of 719 action dictionaries are byte-identical; this is expected for two fixed tapes with different route choices and does not identify a universally superior route.

The strongest repeated pattern is **fragmented, interleaved selling**. High-score tapes do not globally merge every same-item sale. They repeatedly interleave WHEAT, FERTILIZER, MILK, WOOL and STRAWBERRY sales with quantities ranging from 1 to large batches. For example, around day 22 Niklita sells WHEAT 72 and FERTILIZER 94 in separate market turns, while Kenjo uses smaller product-specific batches. Around day 28 Niklita emits large MILK/STRAWBERRY terminal batches, whereas Kenjo preserves a different sequence and quantity mix. This means a blanket SELL merge can erase price-timing behavior; `merge648` remains a narrow mechanism probe and its current 30 paired rows are all exact no-op versus V42.

The tapes share a stable phase structure:

| phase | recurring behavior |
|---|---|
| opening (day 0) | setup movement, early planting/watering, small WHEAT sales; no evidence for changing the tested V42 opening from these tapes alone |
| day 6–12 | active movement and watering; animal FEED/CARE/COLLECT cycles; WHEAT and FERTILIZER sales fund continued production |
| day 18–24 | high watering/harvest density; animal products enter the market; sale order and batch size vary substantially between tapes |
| day 27–29 | production and harvest continue while sales become product- and inventory-specific; terminal actions include DROP and large liquidation batches |

The most transferable invariant is therefore a **phase-conditioned sale profile**, not a fixed action tape: preserve room for scheduled pickups and future BUY/SELL barriers, then rank sale candidates by visible market price, town demand and projected carried/shed inventory. When confidence is low, retain the V37/V42 parent action.

## Implications for candidates

1. `no-R128 V42` remains the safest candidate because its 120-game four-opponent panel and 40-game V42 holdout show no observed degradation.
2. `no-R127 V42` is an additional low-risk wrapper ablation with a complete 120-game four-opponent panel.
3. `merge648 V42` should not be promoted on tape evidence alone. The high-score tapes demonstrate that fragmentation itself is common; only a state-qualified, local merge at the exact target node is defensible.
4. A future profile experiment should learn only a small ranking among already-valid SELL orders during days 24–29, using visible price/inventory and projected shed/carry state. It must preserve order slots, BUY/HIRE barriers and route commitments, and fall back to the parent on uncertainty.

No high-score tape was copied directly into a submission candidate, and no Kaggle submission was made.

## High-score terminal frontier candidate

A prototype wrapper, [highscore_terminal_v42.py](/root/autodl-tmp/incubated_candidates/v42_ablations/highscore_terminal_v42.py), applies the E774-style terminal idea only at step 718: if a parent action leaves a market slot and visible shed MILK/WOOL absent from existing SELL orders, append those items ordered by current visible price. All earlier actions are inherited from no-R127 V42.

The initial v37 smoke panel (`highscore_terminal_panel.json`) covers seeds 9001–9002 and both seats. All four candidate and parent games reached 720 steps with no stderr. Every paired delta was `0`; candidate maximum callback duration was `0.693 s` and parent maximum was `1.077 s`. The wrapper did not activate in these ordinary games, so this is currently a safety/no-op result rather than an improvement claim. It requires the full four-opponent panel before promotion.

The candidate archive contains a root-level `main.py`; its SHA-256 is recorded below for reproducibility:

```text
975f308b04c9c537342dcd0c31fd9e9c53dd9b569c8ff39bc143b44f1a9151dc
```
