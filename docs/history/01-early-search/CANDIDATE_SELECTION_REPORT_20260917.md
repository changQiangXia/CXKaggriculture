# V45 opening candidates: selection report (2026-09-17)

## Scope

The current online reference is `submission_competitive_v45.tar.gz` (submission `56278920`, observed public score about 2650). The replay fingerprint from 36 collected games is dominated by Q70 round trips (22/36, including 17 exact mirror ties), followed by Q5 round trips (7/36), Q5 single-buy (2/36), Q50 (2/36), Q85 (1/36), and two one-off openings. The candidates below change only the final V45 opening wrapper; all farm planning, race logic, terminal handling, and safety guards remain frozen.

No Kaggle submission was performed.

## Candidates

### Q20 (primary)

- Source: `candidate_v45_q20.py`
- Archive: `candidate_v45_q20.tar.gz`
- Single behavior change: `_OPEN_UNITS = 70 -> 20`.
- Source SHA256: `ea2ca3b2875534b7e7a5941339e43c610564dfe7af4b3eb33bad7fcbc7aabc6d`
- Archive SHA256 (main.py-root package): `c9a1789a5c65119d4a5779c72c7b7554f2f5a5522053c10897a5b6aca3be9751`

### Q25 (diversifying/second candidate)

- Source: `candidate_v45_q25.py`
- Archive: `candidate_v45_q25.tar.gz`
- Single behavior change: `_OPEN_UNITS = 70 -> 25`.
- Source SHA256: `80b0c33bbb0c33626374cd18dd7922a82b6d7133798a2e5d5b5008cae1a20fde`
- Archive SHA256 (main.py-root package): `a53bc374f5bc8e33ace631c178b7c46e359c449d7a6a31b83ca0f9ff6185a95b`

Both are deterministic and do not inspect the opponent, seed, or world hash. This avoids the earlier mix/seat policies' dependence on hidden opponent identity.

## Paired opening-family evidence

The harness uses the same seed/world for candidate and V45 parent, both seats, 720 steps, and requires `DONE`, 720 steps, and empty stderr. Local engine is `kaggriculture` 1.25.9; Kaggle replay metadata indicates online engine 1.32.7, so these are directional local results rather than an online-equivalent confidence interval.

### Q20, fresh holdout seeds 9010–9013 (32 games)

| opponent opening | mean delta (candidate − V45) | p10 | worst | W/L/T |
|---|---:|---:|---:|---:|
| Q5 | +205.25 | +192 | +192 | 8/0/0 |
| Q50 | +2618 | +2618 | +2618 | 8/0/0 |
| Q70 | +1340 | +1340 | +1340 | 8/0/0 |
| Q85 | +58.75 | +58 | +58 | 8/0/0 |

Earlier seeds 9005–9006 gave Q70 +1321 and Q85 +58.5; matrix runs on 9005–9008 gave Q50 about +2640.5 and Q5 about +204.75. All opening-family games completed cleanly.

### Q25, independent seeds 9007–9008 (16 games)

| opponent opening | mean delta | p10 | worst | W/L/T |
|---|---:|---:|---:|---:|
| Q5 | +199.5 | +192 | +192 | 4/0/0 |
| Q50 | +2701 | +2618 | +2618 | 4/0/0 |
| Q70 | +1399 | +1358 | +1358 | 4/0/0 |
| Q85 | +208 | +161 | +161 | 4/0/0 |

The earlier Q25 screen on 9005–9006 was also positive in all four families: Q5 +200, Q50 +2580, Q70 +1338.5, Q85 +267.

## Cross-lineage holdout and limits

Q20 against older non-opening lineages on fresh seeds 9010–9013 was neutral against Nathan, but variable/negative against V37 and flex:

- V37: mean -1856.75, 2/8 positive, worst -3816.
- flex: mean -2265.75, 2/8 positive, worst -4603.
- Nathan: 0, 8/8 ties.

Other one-seed screens show that V37/flex deltas can change sign by world; this is a real generalization risk, not a measurement to hide. Q25 has a similar V37 tail in the available one-seed check (about -1363.5) and should not be described as universal.

The evidence supports a narrower claim: Q20 and Q25 are strong, simple opening candidates for the currently observed Q5/Q50/Q70/Q85 population and remove the Q5 candidate's stable Q85 loss. It does not prove either candidate will beat every historical V37/flex opponent or guarantee an online score above 2650. The current online opening mixture has too few Q85 and one-off samples to identify all future opponent mass.

## Selection

Keep both archives frozen as the two submission candidates:

1. `candidate_v45_q20.tar.gz` — lower opening quantity, strongest balance across tested opening families and the better of the two on the currently available V37 checks, although its expanded V37 holdout is still negative and variable.
2. `candidate_v45_q25.tar.gz` — slightly stronger on Q50/Q70 and materially better Q85 margin in the expanded opening holdout, providing a useful independent alternative. Its V37 evidence is still mixed and must not be treated as a universal upgrade.

The older Q5 archive remains a mechanism probe, not one of the two preferred candidates: it is strong against Q50/Q70 but has a repeatable approximately -1.1k delta against Q85.

Submission remains pending explicit user authorization.

## Same-world older-lineage comparison

A same-seed Q25 run against V37/flex on seeds 9010–9011 produced exactly the same directional pattern as Q20 on those worlds:

- V37: mean `-727` across four seat runs (`+1805` on 9010 and `-3259` on 9011).
- flex: mean `-1714.5` (`+1174` on 9010 and `-4603` on 9011).

The agreement suggests that the V37/flex sensitivity is caused by the opening attack interacting with the opponent's route and market timing, rather than a random packaging failure. It is therefore a selection risk that remains visible in both frozen candidates.


Packaging audit: both preferred archives were repacked with a single `main.py` at archive root, as required by the competition format.

## Risk hedge screened after the primary pair

`candidate_v45_q20_seatmix.py` uses Q20 on seat 0 and the frozen Q70 opening on seat 1. On seeds 9014–9015 it produced opening-family deltas of Q5 `+103.5`, Q50 `+1309`, Q70 `+670`, and Q85 `+29.5`; against V37 it was `-554.25`, and against flex `-868.25`. This reduces the old-lineage loss by roughly half but also gives up roughly half of the opening exploit. It remains a hedge, not a replacement for Q25 as the second high-upside package.

Q18 and Q22 were also screened on Q5/Q50/Q70/Q85/V37 (seeds 9014–9015, 40 games total). Both stayed negative against V37 (`-1108.5`) and did not dominate Q20/Q25, so they were rejected.
