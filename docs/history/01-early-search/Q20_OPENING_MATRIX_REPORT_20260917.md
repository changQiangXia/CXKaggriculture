# Q20 opening matrix (2026-09-17)

The Q20 candidate changes only the V45/V70 step-0 round trip from 70 units to 20 (`BUY_PRODUCT WHEAT 20`, `SELL WHEAT 20`). The rest of the parent controller is unchanged. Evaluation used `strict_paired_eval.py`, local Kaggriculture engine, 720 steps, common worlds and both seats. `Δ` is Q20 margin minus the opening-Q70 parent margin.

| opponent family | worlds/seats | mean Δ | p10 | worst | W/L/T | bootstrap |
|---|---:|---:|---:|---:|---:|---:|
| Q70 (9005,9006) | 4 | +1321.0 | +1286.8 | +1264 | 4/0/0 | [+1302,+1340] |
| Q70 (9007,9008) | 4 | +1381.5 | +1340.0 | +1340 | 4/0/0 | [+1340,+1423] |
| Q50 (9005--9008) | 8 | +2640.5 | +2542.0 | +2542 | 8/0/0 | [+2561,+2742.5] |
| Q5 (9005--9008) | 8 | +204.75 | +197.0 | +197 | 8/0/0 | [+197,+212.5] |
| Q85 (9005,9006) | 4 | +58.5 | +58.0 | +58 | 4/0/0 | [+58,+59] |
| V37 (9006) | 2 | +2206.5 | +1378.9 | +1172 | 2/0/0 | one seed |
| flex (9006) | 2 | +2463.0 | +1051.0 | +698 | 2/0/0 | one seed |

All rows completed 720 steps with `DONE/DONE`, no stderr (healthy rate 100%). Raw JSON files are in this directory (`q20_screen.json`, `q20_vs_q50_9005_9008.json`, `q20_vs_q5_9005_9008.json`, `q20_vs_q70_9007_9008.json`, `q20_nonclone_9006.json`).

The Q20 signal is substantially more robust than Q5 in this opening-only test: Q5 has a large negative Q85 stratum, while Q20 is positive in every tested opening and the two preliminary non-clone families. V37/flex use one world each and therefore are evidence rather than confirmation. Before any submission, freeze the exact source/archive and repeat a larger lineage-stratified holdout with the online engine version if available. No submission was made.
