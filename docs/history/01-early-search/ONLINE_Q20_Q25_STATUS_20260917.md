# Online Q20/Q25 status (read-only snapshot, 2026-09-16 21:44 UTC)

All commands used `/root/miniconda3/envs/kaggle-cli/bin/kaggle`; no submit command was run. The monitor endpoint and replay downloads were read-only.

## Current status

| ref | artifact | state | public score | public competitive | validation |
|---:|---|---|---:|---:|---:|
| 56287548 | Q20 | COMPLETE | 874.8 | 3 | 1 |
| 56287561 | Q25 | COMPLETE | 895.5 | 3 | 1 |

The active team queue (`team-submissions 16870342`) currently contains only these two candidates. Each has only three public games, all wins, so the ratings around 875–896 are early dynamic values rather than evidence of beating the established V45/historical 2.6–2.7k scores. Historical submission scores at this API snapshot include V45 `56278920` = 2596.4, Nathan `56257428` = 2646.8, and no-R128 `56238321` = 2687.9; the latter two are no longer the active two-slot queue.

## Competitive replay outcomes

| candidate / episode | opponent | seed | rewards [seat0,seat1] | CHEN seat | result | margin |
|---|---|---:|---:|---:|---|---:|
| Q20 / `109807347` | Taha Alselwi | 565875933 | `[39387.0, 120234.0]` | 1 | **W** | +80847 |
| Q25 / `109807349` | knadithyavr | 665922589 | `[70179.0, 174195.0]` | 1 | **W** | +104016 |
| Q20 / `109808399` | remi_hr | 1012522616 | `[90903.0, 171737.0]` | 1 | **W** | +80834 |
| Q25 / `109808405` | ChrisVas123 | 46769190 | `[115716.0, 159827.0]` | 1 | **W** | +44111 |
| Q25 / `109809456` | Soomana1z | 380912457 | `[102604.0, 155840.0]` | 1 | **W** | +53236 |
| Q20 / `109809458` | batuhan kalem | 1282480228 | `[165794.0, 125066.0]` | 0 | **W** | +40728 |

All six public games are W/W/W for each candidate; no Q20/Q25 loss or tie has appeared. Each candidate validation replay is self-play and excluded from competitive counts. Every public replay completed 720 steps under engine module `1.32.7`.

## Opening inspection

The candidate wrapper fired at step 1 in every replay: Q20 emits `BUY_PRODUCT WHEAT 20` then `SELL WHEAT 20`; Q25 emits the corresponding quantity 25. Opponents did not use the exact Q round-trip pattern in these six games; all opened with normal farm/animal/seed routes.
- `109807347` (Q20, Taha Alselwi): first opponent market list `[['BUY_PRODUCT', 'WHEAT', 8], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['BUY_SEED', 'MELON', 6], ['BUY_ANIMAL', 'SHEEP', 2], ['BUY_SEED', 'WHEAT', 15]]`.
- `109807349` (Q25, knadithyavr): first opponent market list `[['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['BUY_PRODUCT', 'WHEAT', 6], ['BUY_ANIMAL', 'SHEEP', 1], ['BUY_ANIMAL', 'SHEEP', 1], ['BUY_SEED', 'STRAWBERRY', 6]]`.
- `109808399` (Q20, remi_hr): first opponent market list `[['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE']]`.
- `109808405` (Q25, ChrisVas123): first opponent market list `[['HIRE'], ['HIRE'], ['BUY_PRODUCT', 'WHEAT', 10], ['BUY_SEED', 'MELON', 2], ['BUY_ANIMAL', 'COW', 3], ['BUY_ANIMAL', 'SHEEP', 1], ['BUY_SEED', 'MELON', 6], ['BUY_ANIMAL', 'SHEEP', 1]]`.
- `109809456` (Q25, Soomana1z): first opponent market list `[['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['BUY_ANIMAL', 'COW', 2], ['BUY_ANIMAL', 'SHEEP', 2], ['BUY_SEED', 'WHEAT', 7], ['BUY_SEED', 'MELON', 12], ['BUY_PRODUCT', 'WHEAT', 6]]`.
- `109809458` (Q20, batuhan kalem): first opponent market list `[['HIRE'], ['HIRE'], ['BUY_ANIMAL', 'COW', 1], ['BUY_SEED', 'MELON', 6], ['BUY_SEED', 'WHEAT', 6], ['SELL', 'WHEAT', 1]]`.

The six wins show no opening-induced failure in this sample. The sample remains too small and selection-biased to establish a converged online rating or prove an improvement over V45; continue local paired holdouts and wait for substantially more games before making that inference.

Artifacts:

- Replays: `agent_monitor/replays/episode-109807347-replay.json`, `109807349`, `109808399`, `109808405`, `109809456`, `109809458`.
- Own-agent logs for the public games are under `agent_monitor/logs/{56287548,56287561}/win/`; opponent logs return HTTP 403 from Kaggle and are unavailable.
