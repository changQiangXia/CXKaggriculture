# Online Q20/Q25 status (read-only snapshot, 2026-09-16 21:38 UTC)

Commands used the Kaggle CLI in `/root/miniconda3/envs/kaggle-cli/bin/` and did not submit anything:

```text
kaggle competitions submissions kaggriculture --csv
kaggle competitions team-submissions 16870342 --format json
kaggle competitions episodes 56287548 --format json
kaggle competitions episodes 56287561 --format json
kaggle competitions replay <episode_id>
```

## Submission state

| submission | archive | state | current public score | public episodes | validation episodes |
|---:|---|---|---:|---:|---:|
| `56287548` | `candidate_v45_q20.tar.gz` | `COMPLETE` | **780.9** | 1 | 1 |
| `56287561` | `candidate_v45_q25.tar.gz` | `COMPLETE` | **792.6** | 2 | 1 |
| `56278920` | `submission_competitive_v45.tar.gz` | `COMPLETE` | **2596.4** | 112 (at API snapshot) | 1 |

The two Q candidates have only three competitive games combined. Their 780.9/792.6 values are early dynamic ratings and are not evidence that they beat the established 2.6k score. The active queue endpoint currently contains only Q25 and Q20. In the historical submissions list, V45 (`56278920`) is 2596.4; older rows also show `56257428` at 2646.8 and `56238321` at 2687.9, but those older submissions are no longer active two-slot candidates.

The top public leaderboard page (200 rows) currently starts at 3189.0 and ends at 2783.1; team `CHEN Xiang` is not in this returned top-200 page. This is a competition-wide reference, not a claim that a Q candidate has converged.

## Public replay outcomes

All three replays report engine module `1.32.7`, 720 steps, and both agents active through the episode. In every replay `CHEN Xiang` is seat 1. The numeric episode IDs below are the IDs returned by the episodes endpoint; replay JSON's internal `id` is a UUID.

| submission / episode | opponent | seed | rewards [seat0, seat1] | CHEN result | margin |
|---|---|---:|---:|---|---:|
| Q20 / `109807347` | Taha Alselwi | 565875933 | `[39387, 120234]` | **W** | +80847 |
| Q25 / `109807349` | knadithyavr | 665922589 | `[70179, 174195]` | **W** | +104016 |
| Q25 / `109808405` | ChrisVas123 | 46769190 | `[115716, 159827]` | **W** | +44111 |

Each Q candidate's validation replay (`109806169` for Q20 and `109806172` for Q25) is a self-play check and is excluded from competitive counts.

## Opening observations

The candidate's first non-empty market action is exactly the expected wrapper:

- Q20: `BUY_PRODUCT WHEAT 20`, `SELL WHEAT 20` at step 1.
- Q25: `BUY_PRODUCT WHEAT 25`, `SELL WHEAT 25` at step 1 (both public Q25 episodes).

Opponent first market actions:

- Taha (`109807347`): step 1 buys WHEAT 8, hires 6, buys MELON seed 6, buys SHEEP 2, buys WHEAT seed 15; step 2 buys COW 2 and sells WHEAT 6. This is an animal/production opening, not a Q round trip.
- knadithyavr (`109807349`): step 1 hires 6, buys WHEAT 6, buys two SHEEP, buys STRAWBERRY seed 6; thereafter alternates WHEAT sell/buy 6 with MELON seed purchases. This is a low-quantity production opening.
- ChrisVas123 (`109808405`): step 1 hires 2, buys WHEAT 10, MELON seed 2 + 6, COW 3, SHEEP 2; step 2 hires, sells WHEAT 6, buys CARROT seed 6. This is a mixed animal/seed opening.

No replay contains a candidate loss or tie, and no evidence here indicates that the opening wrapper caused a failure. The sample is too small to infer a converged online rating or to prove improvement over V45; continue paired local evaluation and wait for substantially more Q-candidate competitive games before making that claim.
