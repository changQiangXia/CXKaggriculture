# Q25 seatmix audit (unsubmitted)

Variant `candidate_v45_q25_seatmix.py` changes the V45 opening wrapper only: player 0 uses a 25-unit wheat round trip, while player 1 retains the original Q70 (70-unit) round trip. This is a hedge experiment, not a submission.

Strict paired local engine 1.25.9, 720 steps, common seeds 9026–9027, both seats, comparing to V45 parent:

| family | mean delta | worst | positive rows | negative rows | ties |
|---|---:|---:|---:|---:|---:|
| q5 | +101.25 | 0 | 2 | 0 | 2 |
| q50 | +1309 | 0 | 2 | 0 | 2 |
| q70 | +678.75 | 0 | 2 | 0 | 2 |
| q85 | +127.5 | 0 | 2 | 0 | 2 |
| v37 | -3344 | -8059 | 0 | 2 | 2 |
| flex | -3864.5 | -8099 | 0 | 2 | 2 |

All 24 rows completed at 720 steps with empty stderr. The modified seat obtains the opening upside, while the unchanged seat is behaviorally identical to the parent. The old-lineage downside is therefore concentrated in one seat and is substantially worse than the previously tested Q20 seatmix (approximately -554/-868 on seeds 9014–9015). Reject this variant; retain Q20/Q25 as the two candidates.
