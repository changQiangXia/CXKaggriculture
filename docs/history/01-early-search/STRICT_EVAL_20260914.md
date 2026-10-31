# cap2 strict similarity gate check

`h5sim96_cap2_strict.py` changes only the five-turn reservation similarity threshold from `0.96` to `0.995`; `_V231_CAP=2` and all other cap2 code remain unchanged.

Public_v37 seeds 9001–9005, both seats (10 games):

- cap2: 10/10 wins, mean margin `1815.1`, min `740`.
- strict: 10/10 wins, mean margin `1815.1`, min `740`.
- Every recorded margin is identical; no measurable gain on this panel.

The stricter threshold is therefore a no-regression/private-risk ablation, not an improvement candidate. It remains unsubmitted.
