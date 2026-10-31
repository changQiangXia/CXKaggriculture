# Q30 opening variant rejection

`candidate_v45_q30.py` changes only `_OPEN_UNITS` from 70 to 30. A 9030–9031 screen looked attractive on synthetic openings (Q70 +1366, Q85 +306.5), but the independent cross-lineage holdout on seeds 9034–9037 shows severe consistent degradation:

| lineage | mean Δmargin | P10 | worst | sign count |
|---|---:|---:|---:|---:|
| V37 | -5294 | -8011 | -8011 | 8 negative / 0 positive |
| Flex | -4838.5 | -6116 | -6116 | 8 negative / 0 positive |

All 16 rows completed at 720 steps with no stderr. Reject Q30; the larger opening quantity amplifies the route/RNG perturbation for non-clone lineages. The two existing Q20 and Q25 candidates remain the selected pair.
