# Q20/Q25 confidence audit (2026-09-17)

## Scope

The selected candidates modify only V45's step-0 wheat round trip, `_OPEN_UNITS=70` to 20 or 25. No route, race, terminal, or middle-game code differs from `customerUpload/kaggle/v45_extracted.py`.

## New validation evidence

* Exact online-style custom opening `[BUY_PRODUCT WHEAT 5, BUY_PRODUCT WHEAT 10, SELL WHEAT 60]`, seeds 9026–9029, both seats: Q20 8/8 parent→candidate `W→W`; Q25 8/8 `W→W`. Q20's margin delta mean −1169.25 (minimum candidate margin +7); Q25 mean −1010.25 (minimum candidate margin +212). The lower margin is irrelevant to Kaggle's W/L/T rating while it remains positive, but it is a boundary risk.
* Q25 fresh V37/Flex seeds 9020–9023, both seats: every row `W→W`; mean cash deltas −1144.5 and −2124.75 respectively. These are cash reductions, not outcome reductions.
* Q22 control was inferior: fresh V37/Flex/q85 seeds 9024–9025 gave means −2828/−2092.75/+594 and is rejected.
* Q30 control was strongly inferior on V37/Flex seeds 9034–9037: means −5294/−4838.5, 8/8 negative in each family; rejected.
* Q25 seatmix (Q25 on seat 0, Q70 on seat 1) and Q20/Q25 dual seatmix both produced large old-lineage downside and are rejected.

## Outcome interpretation

The 90 replay opening distribution for V45 is: custom 28, Q70 25 (3W/17T/5L), Q5 7, V37-style 5, single-BUY5 5, single-BUY6 3, `[13,SELL13,13]` 3, and smaller families. Q20/Q25 preserve all tested custom, V37, V44, Nathan, Flex, and actual single-BUY5 outcome classes. Synthetic Q70 consistently changes `T→W`; synthetic Q50 changes `L→W`; Q5 remains `L→L` and therefore gains no direct outcome points.

## Decision boundary

These results establish a plausible upside: the dominant observed Q70 mirror class can be converted from ties to wins while already-won custom/V37 matches remain wins in holdout. They do **not** establish a high-confidence probability of exceeding any fixed rating such as 2724. Kaggle's rating is dynamic, the online sample is time-dependent, and local engine 1.25.9 differs from online engine 1.32.7. The strongest defensible choice remains Q20 as balanced primary and Q25 as second candidate; retain the caveat that confidence is directional rather than a guaranteed score increase.
