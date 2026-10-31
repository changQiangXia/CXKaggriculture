# Online Q20/Q25 status (read-only latest snapshot, 2026-09-16 21:48 UTC)

Read-only commands used `/root/miniconda3/envs/kaggle-cli/bin/kaggle`; no submission was performed. Replay and status data were refreshed through the monitor.

## Current status

| ref | artifact | state | public score | public games (W/L/T) | validation |
|---:|---|---|---:|---|---:|
| 56287548 | candidate_v45_q20.tar.gz | COMPLETE | 931.1 | 4 (4/0/0) | 1 |
| 56287561 | candidate_v45_q25.tar.gz | COMPLETE | 1054.8 | 5 (5/0/0) | 1 |

The active team queue (`team-submissions 16870342`) currently contains Q25 and Q20 only. Q20 has four public games and Q25 five; every one is a win. Scores around 931 and 1055 are early dynamic ratings, not evidence of beating V45 or the older 2.6–2.7k historical submissions. Historical rows at this snapshot: V45 `56278920` 2596.4, Nathan `56257428` 2646.8, no-R128 `56238321` 2687.9 (older rows are no longer active).

## Public replay outcomes

| candidate / episode | opponent | seed | rewards [seat0, seat1] | CHEN seat | result | margin |
|---|---|---|---:|---:|---|---:|
| Q20 / `109807347` | Taha Alselwi | 565875933 | `[39387.0, 120234.0]` | 1 | **WIN** | +80847 |
| Q25 / `109807349` | knadithyavr | 665922589 | `[70179.0, 174195.0]` | 1 | **WIN** | +104016 |
| Q20 / `109808399` | remi_hr | 1012522616 | `[90903.0, 171737.0]` | 1 | **WIN** | +80834 |
| Q25 / `109808405` | ChrisVas123 | 46769190 | `[115716.0, 159827.0]` | 1 | **WIN** | +44111 |
| Q25 / `109809456` | Soomana1z | 380912457 | `[102604.0, 155840.0]` | 1 | **WIN** | +53236 |
| Q20 / `109809458` | batuhan kalem | 1282480228 | `[165794.0, 125066.0]` | 0 | **WIN** | +40728 |
| Q25 / `109810516` | galaxyhunter | 19547580 | `[79235.0, 131426.0]` | 1 | **WIN** | +52191 |
| Q20 / `109810519` | Vespidae | 1841170518 | `[106047.0, 24693.0]` | 0 | **WIN** | +81354 |
| Q25 / `109811567` | Marco DG | 2095815627 | `[116439.0, 26197.0]` | 0 | **WIN** | +90242 |

All replays completed 720 steps under engine module 1.32.7. Candidate validation episodes are self-play and excluded above.

## Opening and failure check

Every Q replay emitted the wrapper at step 1 (Q20: BUY_PRODUCT WHEAT 20 then SELL WHEAT 20; Q25: quantity 25). Opponent openings were ordinary hire/animal/seed/low-WHEAT routes, with no exact mirrored Q round trip. No candidate loss or tie has appeared, and no opening-induced failure is visible in this sample. Nine public games remain far too few to infer a converged online rating or establish improvement over a 2.6–2.7k baseline; continue local paired holdouts and wait for larger samples.

Artifacts: replays in `agent_monitor/replays/`; own agent logs under `agent_monitor/logs/{56287548,56287561}/win/`. Opponent log downloads return HTTP 403 from Kaggle.
