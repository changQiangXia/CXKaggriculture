# Online opening mixture and Q5 delta estimate (2026-09-17)

Downloaded submission 56278920: **36 episodes** (17 ties, 19 losses). Opening is the opponent's first non-empty market action in each replay.

## Observed mixture

| family | count | proportion | Wilson 95% interval | observed parent margin |
|---|---:|---:|---:|---:|
| q70 | 22 | 0.611 | [0.449, 0.752] | -470.7 |
| q5rt | 7 | 0.194 | [0.098, 0.350] | -203.9 |
| q5single | 2 | 0.056 | [0.015, 0.181] | -846.5 |
| q50 | 2 | 0.056 | [0.015, 0.181] | -2825.5 |
| q85 | 1 | 0.028 | [0.005, 0.142] | -6670.0 |
| q19_16 | 1 | 0.028 | [0.005, 0.142] | -1489.0 |
| q4_8 | 1 | 0.028 | [0.005, 0.142] | -464.0 |

The q70 mass is 22/36 (17 exact mirror ties plus 5 q70 losses). The q85 family appears once (1/36), so its Wilson upper bound is 14.2%; this tail cannot be treated as negligible.

## Q5 paired-delta evidence

| family | Q5 minus V45 mean delta | source |
|---|---:|---|
| q70 | 228.5 | matrix q5_vs_q70 (4 seeds x 2 seats) |
| q50 | 2026.5 | matrix q5_vs_q50 (4 x 2) |
| q85 | -1093.8 | matrix q5_vs_q85 (4 x 2) |
| q5rt | 226.0 | older q5_vs_openings minimum (2 seeds) |
| q5single | 0.0 | assumed 0 (no direct matrix) |
| q4_8 | -2000.0 | stress assumption |
| q19_16 | -2000.0 | stress assumption |

## Mixture scenarios

| scenario | expected paired delta | episode bootstrap 95% |
|---|---:|---:|
| point_floor | +154.7 | [-81.3, +378.0] |
| pessimistic | -83.7 | [-552.9, +283.3] |
| stress_tail | -280.4 | [-1007.3, +258.5] |

point_floor uses the minimum observed Q5-vs-Q5 opening delta (+226), zero for single-buy Q5, and -2000 for each unmeasured odd opening. pessimistic sets Q5 families to non-positive and unmeasured odd openings to -5000. stress_tail further gives q85 its measured worst (-1173) and harsher unknown-family penalties.

## Interpretation and limits

The empirical point estimate is positive only because q70/q50/q5-round-trip dominate the observed sample. Under the floor assumptions it is about +155 cash per game; the harsher stress case is approximately -280. Thus Q5 has a clear mechanism against the currently common Q70 mirror, but this log alone does not establish a high-confidence online score improvement.

Q85 is the critical tail: the direct matrix is -1093.8 (all 8 paired runs negative, p10 -1173). Reweighting q85 from the observed 2.8% toward its 14.2% Wilson upper bound removes roughly 150-190 cash/game relative to q70, enough to erase the modest mixture gain. The q4+8 and q19/16 families are each singletons and need dedicated holdout runs.

Episode bootstrap intervals are descriptive only. The 17 q70 ties are a correlated deterministic cluster, and the local engine is 1.25.9 versus online 1.32.7; these intervals must not be read as online confidence intervals. No submission was made.
