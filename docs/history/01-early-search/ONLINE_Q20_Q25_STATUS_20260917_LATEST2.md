# Q20/Q25 latest online status (read-only monitor)

Timestamp: 2026-09-17 UTC (API snapshots during the ongoing run)

| ref | archive | public games observed | W/L/T observed | latest score |
|---:|---|---:|---|---:|
| 56287548 | candidate_v45_q20.tar.gz | 21 public | 21/0/0 observed | 2266.4 |
| 56287561 | candidate_v45_q25.tar.gz | 17 public | 17/0/0 observed | 2169.2 |

Both submissions are `COMPLETE`. Every downloaded public replay has `DONE` status and 720 steps; both agents' step-1 market action matches their intended opening (`BUY_PRODUCT WHEAT q`, `SELL WHEAT q`).

Historical references in the same API snapshot: V45 ref 56278920 = 2596.4; old V37 ref 56178383 = 2724.0. These were submitted at different times and are not paired ratings. The Q candidates have not yet exceeded those historical values; their scores are still accumulating from the 600 starting rating. No new submission was made.

The local evidence remains W/L/T based: Q20/Q25 improve Q50/Q70 synthetic opening outcomes and preserve actual single5/V44 and cross-lineage outcomes in tested holdouts. The single earlier V37 W->L tail was not reproduced on fresh 9020–9025 v37 worlds.
