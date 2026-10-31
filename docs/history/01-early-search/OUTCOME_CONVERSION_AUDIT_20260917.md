# Q20/Q25 outcome conversion audit (2026-09-17)

This audit maps each paired run from the V45 parent outcome to candidate outcome using final cash margin (`W` if >0, `L` if <0, `T` if 0). A cash-margin delta alone is not treated as a leaderboard regression: Kaggle rating is driven by W/L/T.

## Actual-opening and v44 checks

- `q20_actual_openings_9018_9021.json`: 16 paired rows (single5 and v44, seeds 9018-9021), all healthy. Parent→Q20: `13 W→W`, `3 L→L`; zero outcome regressions or upgrades. 
- `q20_vs_v44_9014_9017.json`: 8 rows, all `W→W`. Q20's average final margin is about +134 versus V45 +1300 (delta −1166), so this is a cash-margin reduction with no win/loss change.

## Broad holdout (q50/q85/v37/flex/Nathan)

`broad_q20_9016_9019.json` and `broad_q25_9016_9019.json` each contain 40 healthy rows and have the same outcome transitions:

| Parent → candidate | Q20 | Q25 |
|---|---:|---:|
| W→W | 30 | 30 |
| L→L | 3 | 3 |
| L→W | 6 | 6 |
| W→L | 1 | 1 |

The sole regression is `v37`, seed 9019, seat 0: parent +3691 → candidate −1304 (delta −4995). The six upgrades are all Q50 (parent losses become candidate wins). No Q25 outcome difference appears in this broad panel, though cash margins differ against Q85.

## Synthetic opening holdouts

- Q20, `q20_opening_holdout_9010_9013.json` (32 rows): q5 `L→L`×8; q50 `L→W`×8; q70 `T→W`×8; q85 `W→W`×8.
- Q25, `q25_opening_holdout_9007_9008.json` (16 rows): same four transition classes, ×4 each.

## Interpretation

Both candidates preserve outcomes against the observed actual single5/v44 openings. They reliably repair parent losses/ties in synthetic q50/q70, but retain a measured tail risk against v37-style openings (one W→L in the broad 40-row panel). Existing nonclone holdouts (`q20_nonclone_holdout_9010_9013.json`, `q25_nonclone_holdout_9010_9011.json`) show only W→W, but are small. Q25 has no demonstrated outcome-level advantage over Q20 in the tested panels; its main advantage is a modest cash-margin improvement against q85 in earlier opening tests.

Do not claim either candidate is strictly dominant. The evidence supports Q20 as high-upside primary and Q25 as a second candidate, contingent on accepting the single observed W→L tail. Submit only after explicit user authorization.

## Fresh follow-up seeds

- `q20_v37_fresh_9020_9023.json`: 8 rows, all `W→W`; cash delta mean −1144.5 (worst −3156), with no outcome regression. This makes the single v37 W→L at seed 9019 look isolated rather than a repeatable outcome failure.
- `q20_q85_fresh_9020_9023.json`: 8 rows, all `W→W`; delta mean +58.5, worst +58.
- `q25_q85_fresh_9020_9023.json`: 8 rows, all `W→W`; delta mean +234.5, worst +161. Q25 therefore has a clear fresh-seed cash advantage over Q20 on q85 while preserving the same outcome.
