# Q85 opening matrix (2026-09-17)

Runner: `strict_paired_eval.py`, local `kaggle_environments`, 720 steps, common seeds 9005--9008, both seats. Each `delta` is candidate margin minus the frozen Q70 parent margin; the two seats are the same world cluster and are not independent bootstrap worlds.

| candidate opening | opponent opening | n | mean Δ | p10 | worst | W/L/T | seed bootstrap |
|---|---:|---:|---:|---:|---:|---:|---:|
| Q5 | Q50 | 8 | +2026.5 | +1433.2 | +1380 | 8/0/0 | [+1430.5,+3181.0] |
| Q5 | Q70 | 8 | +228.5 | +221.0 | +221 | 8/0/0 | [+221,+236] |
| Q5 | Q85 | 8 | -1093.75 | -1173.0 | -1173 | 0/8/0 | [-1148.5,-1057.75] |
| Q85 | Q5 | 8 | -7.0 | -7.0 | -7 | 0/8/0 | [-7,-7] |
| Q85 | Q50 | 8 | -245.5 | -286.2 | -289 | 0/8/0 | [-281,-192.5] |
| Q85 | Q70 | 8 | -1329.25 | -1401.0 | -1401 | 0/8/0 | [-1380.25,-1289.5] |

All rows had 100% healthy completion (DONE, 720 steps, no stderr). The exact row data are in `q5_vs_q*_9005_9008.json`, `q85_vs_q*_9005_9008.json`, and `q85_vs_q5_q50_9005_9008.json`.

## Interpretation

Q85 is not a viable second candidate. Against every tested family it is no better than Q70 and is consistently lower: the Q70 parent wins by about 1.3k against Q85; Q85 gives up that advantage. Against Q5 it is effectively neutral (-7), so it does not hedge Q5's Q85 weakness in a useful way. Keep Q85 only as a stress-stratum opponent.

Q5 remains a targeted exploit: strong against Q50/Q70, uniformly negative against Q85. Any mixture must use an online opening prior and report world-cluster uncertainty. A fixed equal-family average is misleading because the observed online sample has Q85 at only 1/36, while Q70 is 22/36. The observed-prior calculation is in `opening_mixture_estimate_20260917.json`; its Q5 point estimate is positive but its conservative intervals still cross zero.

No submission was made.
