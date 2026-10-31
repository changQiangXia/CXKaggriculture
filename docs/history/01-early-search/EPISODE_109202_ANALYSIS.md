# Episodes 109202620 / 109202449 / 109202960

Replay-level analysis (all 720 steps, no runtime errors observed).

| episode | submission | seed | our seat | rewards (ours/opponent) | margin |
|---|---:|---:|---:|---:|---:|
| 109202620 | no-R128 56238321 | 894103020 | 1 | 107,436 / 109,313 | **-1,877** |
| 109202449 | no-R128 56238321 | 1,894,944,939 | 0 | 78,495 / 81,321 | **-2,826** |
| 109202960 | V42 56234455 | 1,598,150,974 | 0 | 111,111 / 111,588 | **-477** |

## First divergence and trajectories

All three games diverge at step 1 (day 0 hour 1), because the opponent uses a different opening market order. Our opening is the V42 `BUY_PRODUCT WHEAT 5 + BUY_PRODUCT WHEAT 10 + SELL WHEAT 60`. Opponent openings were:

* 109202620: `BUY_PRODUCT WHEAT 8` (then step 2 sells WHEAT 8 versus our 13).
* 109202449: `BUY_PRODUCT WHEAT 13 + BUY_PRODUCT WHEAT 30 + SELL WHEAT 30` (then sells 13 at step 2).
* 109202960: same V42-like buys, but `SELL WHEAT 15` (step 2 opponent `SELL WHEAT 0`).

After opening, 109202620 remains nearly synchronized until the first substantive market differences around step 257 (day 10), while 109202449 has small action drift around steps 21–43 and larger drift from day 10 onward. V42 109202960 diverges gradually (266 differing action records), with major resource/route differences around days 7–10 and day 24 onward.

## Margins by phase

* **109202620 no-R128:** cash is close through day 18; our side leads slightly at day 12 (+74), trails by day 15 (-53), then falls to -1,832 by day 26 and finishes -1,877. At day 27–29 both players execute almost identical bulk liquidation (1,000-unit SELL orders); remaining gap is mostly pre-existing market/inventory timing, not terminal planner failure.
* **109202449 no-R128:** opponent leads progressively during days 24–29 (about -2.0k at day 24, -2.4k day 25, -2.3k day 26, -2.7k day 27, -2.9k day 28), finishing -2,826. Both sides' day 28–29 bulk liquidation is effectively identical, so terminal wrapper is not the cause.
* **109202960 V42:** near tie overall. Opponent gains a large temporary lead around day 26 (our -7.3k at day 26 hour 23), then gap narrows during liquidation; final -477. This is tactical market/production timing rather than systemic loss.

## Mechanism clues

1. **Opening is the dominant causal fork.** Every episode differs at step 1 because opponents submit different initial WHEAT quantities. In 109202620, our extra early sell (60+13 versus opponent 8+8) does not create an immediate lasting lead; later trajectories are almost mirrors and finish within 1.9k. In 109202449, the opponent's larger initial buy/sell path precedes a stable 2.8k advantage. These episodes support opening sensitivity but do not justify changing the validated V42 opening from three samples.
2. **Shared market SELL order/timing remains the likely source of residual gaps.** Once trajectories diverge, farmer/hand actions are mostly the same; differences are predominantly market order presence and quantities (e.g., extra SELL MILK/WOOL/FERTILIZER or WHEAT, and occasional BUY_PRODUCT WHEAT). This is consistent with queue-order effects and inventory carried between sales.
3. **No evidence of no-R128 wrapper effect.** 109202620 no-R128 and 109202960 V42 both use the same R128-era terminal liquidation pattern. Bulk SELL sequences at days 27–29 are identical or near-identical. The no-R128 losses therefore do not implicate removing R128; rating/opponent opening and market path are stronger explanations.
4. **Terminal liquidation is not failing.** In all three episodes both agents issue the same 1,000-unit SELL sweeps near steps 680–718 and end with tiny residual quantities (WHEAT/CARROT/WOOL). Differences are already present before liquidation; avoid modifying terminal planner based on these losses.
5. **Action-level anomalies are normal market synchronization noise.** Some records contain zero-quantity SELL/BUY orders (e.g., opponent in V42 at step 2 `SELL WHEAT 0`, step 120 `SELL FERTILIZER 0`), but no stderr/timeout and no broad execution failure. Do not add guards from isolated zero orders.

## Recommendation

Treat these as adaptive-opponent/opening panel evidence, not a confirmed policy regression. Preserve V42/no-R128 code. For mechanism work, index day 10–18 and day 24–29 SELL events with market inventory/price and carried/shed state, then run fixed-tape counterfactuals that change one SELL merge/order at a time. In particular, test whether splitting versus merging same-product SELLs around day 24–27 explains the transient ±2–7k gaps. No submission or policy change is warranted from these episodes alone.
