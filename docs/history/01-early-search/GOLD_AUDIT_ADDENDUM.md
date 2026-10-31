# Gold-zone public strategy audit (2026-09-13)

## Transferable logic

Frontier public code (`public_intel/frontier_main.py`, V231) uses a narrow, observable livestock substitution. Trigger only at steps 216–227 and when all visible gates hold:

- at least 3 unlocked shops; exactly one `BUY_ANIMAL SHEEP` order, quantity 1–2;
- at least 2 milk shops (`PIZZA_SHOP`, `ICE_CREAM_SHOP`, `SMOOTHIE_SHOP`), no `YARN_STORE`;
- visible MILK price >= WOOL price (margin variant uses +20);
- own visible animal counts COW >=4 and SHEEP >=2;
- no animal cargo, shed animals, reserved/carrying/pending placements;
- confirmation of purchased COW in next observation before redirecting any PICKUP/PLACE SHEEP actions.

On failed purchase or placement it records a failure and leaves parent action semantics intact. It adds harvested milk only to an existing MILK sale slot, never creating a speculative market order. This is transferable because it uses only current own farm, public shops/prices, and next-observation confirmation.

Do not transfer: action tapes, hidden occupancy, future opponent SELL, or broad RL labels; these were not robust under replay due shared market order and weed RNG.

## Tested narrow variants

`day2_gold_variants/h5sim96_cap2_margin20.py` changes only the visible price gate from `MILK >= WOOL` to `MILK >= WOOL + 20`, keeping h5sim96 and cap=2. Archive: `h5sim96_cap2_margin20.tar.gz`; SHA256 `39abe97b85a536df9cf373465b58c9b0452cbb8faaf73ce3b4d9d4836e979fa9`.

`h5sim96_cap2_qty1.py` changes only animal substitution to quantity exactly 1; archive SHA256 `05c34140f80b96c8ff58d88108e248f99060ebef17a67878199a367f2c6749f5`.

Unseen V37 baseline panel (seeds 12001–12010, both seats):

- cap2: 20/20 wins, mean margin +1940.0, minimum +889; substitution requested 2 games / 2 units.
- margin20: 20/20 wins, mean margin +2273.8, minimum +889; substitution requested 0 games (gate did not trigger).
- qty1: 20/20 wins, mean/min same as cap2 (+1940.0/+889); requested same 2 units.

Extended seeds 13001–13010, both seats (all three variants had 20/20 wins): cap2 and margin20/qty1 mean margin +1579.5, minimum +769; no substitutions triggered in this block.

These are no-regression checks, not proof of rating improvement. Margin20 is the most conservative, low-trigger candidate for further local opponent panels, with cap2 as higher-diversity candidate. No submission has been made.
