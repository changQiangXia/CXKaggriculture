# BAKE/PET route splice audit

The latest cap2 loss `108602848` opened with visible shops `BAKERY, PET_CAFE, PIZZA_SHOP, PET_CAFE`. The current router has no explicit `(BAKERY, PET_CAFE)` mapping and therefore uses route 0.

I tested explicit replacements on the exact replay random seed (`info.seed=1966532787`) using the recorded opponent action tape aligned to `steps[t+1]`:

- cap2 route 0: own/opponent `[49830, 47753]`, margin `-2077`.
- route 3 for `(BAKERY, PET_CAFE)`: `[52266, 40622]`, margin `-11644`.
- route 5: `[52048, 41370]`, margin `-10678`.
- route 7: `[52049, 40629]`, margin `-11420`.

All runs completed 720 steps. Every tested donor route made this loss substantially worse against the fixed opponent. The absence of an explicit mapping is therefore safer than a naive splice; no route mapping was added and no submission candidate was created.

This is a mechanism diagnostic only: fixed opponent tapes do not estimate adaptive online rating. It does, however, falsify the tempting “fill the missing BAKE/PET pair with a nearby wool/milk route” idea.
