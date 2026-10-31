# Candidate v48 (V47 base) — validation report

## Artifact

- Archive: `candidate_v48.tar.gz`
- Root member: `main.py` (single file)
- main.py SHA-256: `f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`
- archive SHA-256: `4eca246c13c9399ff0b5c2969f38f17c54875689092827403d740fa9931f53ef`
- Source: Ahmed Berat Özer public V47 "Reactive Market Coordination" (verified against the notebook's declared hash).

## Engine

- Local evaluation env: kaggle-environments 1.32.7 (Python 3.11, `kaggle-eval`).
- Tier-0 equivalence: all 58 recorded online episodes reproduce with 0 field mismatches (see `tier0_engine_check.py`).
- Loader: official `get_last_callable` path verified; self-play exact tie (82191:82191) matches the `.py` source byte-for-byte.

## Runtime

- Full self-play season: 1438 callbacks, max 0.215 s, p99 0.0105 s, 0 callbacks over the 1 s `actTimeout`.

## Confirm panel (fresh seeds 400001-400064, both seats, 720 steps, 128 games per family)

| Opponent | W/L/T | Win rate | Mean margin | Worst margin |
|---|---:|---:|---:|---:|
| q25_active (current active best) | 128/0/0 | 100.0% | +2820.5 | +636 |
| v45 | 125/3/0 | 97.7% | +2723.6 | -1045 |
| v46 | 126/2/0 | 98.4% | +1659.6 | -3270 |
| v37 (historical 2724) | 126/2/0 | 98.4% | +4997.5 | -2232 |
| seyit2820 | 117/11/0 | 91.4% | +907.0 | -3497 |
| pipe7 | 126/2/0 | 98.4% | +2459.2 | -3186 |
| pipe8 | 126/2/0 | 98.4% | +2231.8 | -3066 |
| martsmart | 124/4/0 | 96.9% | +1551.2 | -3303 |
| reactive7 | 126/2/0 | 98.4% | +1715.9 | -3288 |
| beyond (K0006) | 127/1/0 | 99.2% | +2212.8 | -795 |

Total: 1251 W / 29 L / 0 T over 1280 games (97.7%).

## Interpretation

- The candidate dominates the current active submission (Q25) in every one of 128 paired games with a worst-case margin of +636.
- It also beats the account's historical best (V37, 2724) 126/128 with mean +4997.5.
- The only close family is seyit2820 (91.4%), the donor of several of V47's layers.
- Local evidence cannot guarantee an online rating, but this is the strongest-evidence candidate the workspace has produced; it is the strongest available build of our parent lineage.
