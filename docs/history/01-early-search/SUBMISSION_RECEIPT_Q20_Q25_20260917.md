# Q20/Q25 submission receipt — 2026-09-17

## Submitted artifacts

| Candidate | Archive SHA-256 | Source SHA-256 | Kaggle ref | Initial status | Initial public score |
|---|---|---|---:|---|---:|
| Q20 | `c9a1789a5c65119d4a5779c72c7b7554f2f5a5522053c10897a5b6aca3be9751` | `ea2ca3b2875534b7e7a5941339e43c610564dfe7af4b3eb33bad7fcbc7aabc6d` | `56287548` | COMPLETE | 600.0 (early dynamic value) |
| Q25 | `a53bc374f5bc8e33ace631c178b7c46e359c449d7a6a31b83ca0f9ff6185a95b` | `80b0c33bbb0c33626374cd18dd7922a82b6d7133798a2e5d5b5008cae1a20fde` | `56287561` | COMPLETE | 600.0 (early dynamic value) |

Both archives contain exactly one root-level `main.py`, and the extracted bytes match the frozen source. The Kaggle CLI environment Python was used:

`/root/miniconda3/envs/kaggle-cli/bin/python submit_kaggle_resilient.py ...`

The resilient submit wrapper rewrote Kaggle's resumable upload host from `www.googleapis.com` to `storage.googleapis.com` for both uploads.

## Validation basis

- Synthetic opening holdout: Q20 and Q25 convert Q50 losses to wins and Q70 ties to wins, while preserving Q5/Q85 outcomes on the tested seeds.
- Actual opening holdout: no W/L/T regressions against single-BUY5 or V44 on fresh seeds.
- Cross-lineage panel: both candidates preserve parent W/L outcomes for v37, flex, V44, and Nathan on fresh 9022–9023 seeds; all 64 games completed 720 steps with no stderr.
- Fresh v37 Q20 panel 9020–9023: 8/8 parent-W to candidate-W.
- Fresh Q25 Q85 panel 9020–9023: 8/8 parent-W to candidate-W, positive cash deltas.

The selection criterion was W/L/T conversion because the competition rating is based on game outcomes. Cash-margin changes are retained as diagnostics and are not treated as a direct leaderboard prediction.

## Caveat

One earlier v37 seed (9019) produced an isolated parent-W to candidate-L conversion; it did not recur in fresh v37 seeds 9020–9023 or in the broader cross-lineage panel. The candidates remain opening-quantity variants, so their online rating must be judged after sufficient games accumulate.
