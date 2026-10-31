# Q20 candidate

Frozen source is `candidate_v45_q20.py`, derived from V45 by changing only `_OPEN_UNITS=70` to `20`; all routing, race, horizon, terminal, and guards remain unchanged. This is a deterministic opening policy and does not inspect seed or opponent actions.

Screening on local Kaggle engine 1.25.9 (720 steps, paired common worlds, both seats):

- Q70 clone, seeds 9005/9006: deltas +1340,+1340,+1340,+1264; mean +1321, worst +1264, 4/4 positive.
- Q85, same seeds: deltas +59,+59,+58,+58; mean +58.5, worst +58, 4/4 positive.
- Q50, same seeds: deltas +2618,+2618,+2542,+2542; mean +2579, 4/4 positive.
- V37, seed 9005: -4239 in both seats.
- flex, seed 9005: -4808 in both seats.

Every completed game was DONE at 720 steps with empty stderr. The non-clone result is only one world and is not confirmation; expand V37/flex/Nathan holdout before selection. Engine differs from online 1.32.7, so this is directional evidence only.
