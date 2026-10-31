# Nathan cautious: targeted three-round local repair (2026-09-16)

This is a local candidate only; it was not submitted to Kaggle.

## Final selection

`final/main.py` is the Round 2 candidate. It includes the real Kaggle file-loader export fix and preserves market order slots. Round 3 was explicitly rejected after a paired smoke test caused a large regression.

## Rounds

1. **Loader fix retained.** The uploaded Nathan package previously ended with a callable `_NC_PARENT`, so `get_last_callable()` bypassed the cautious wrapper. The round appends `agent = globals().pop('agent')`; true loader inspection confirms the selected callable is the final wrapper (`selected.__globals__['agent'] is selected`). No gameplay logic was changed.
2. **Market-slot preservation retained.** The prior wrapper removed zero-quantity/malformed orders, which can shift later order indices in Kaggriculture's index-paired market. This round keeps the parent order list and only enforces the 10-order limit, preserving all existing slots. This is intentionally conservative.
3. **SELL quantity cap rejected.** A trial capped each SELL to the current shed stock while retaining slots. On seed 9001 versus `public_v37`, both seats regressed from parent margin `+3525` to `-27339` (delta `-30864`); telemetry showed 244 capped orders and 84,497 units changed. The mechanism was rolled back and is absent from final/main.py.

## Validation

All three sources pass `py_compile`. True loader checks passed for each: selected callable name `agent`, and its globals `agent` points to itself. A 720-step true-loader run of Round 1 against public_v37 completed `DONE/DONE`, 719 calls, zero errors. The broad Round 1 paired panel (v37/flex/thomas/dmitrii, seeds 9001–9004, both seats) showed identical candidate/parent outcomes where completed; the loader-only change is behavior preserving.

Round 3's regression is recorded in `round3_smoke.json` and was not packaged. The final archive is `nathan_cautious_3rounds_candidate.tar.gz`.
