# V37 horizon-5 pre-648 candidate

## Change

The only policy change is the existing guarded sale reservation horizon:

- steps 288–647: reserve already-planned sales up to five own future actions;
- steps 648–695: retain the V37 four-action horizon;
- preserve the existing 72-step shop boundary, stock/pickup/purchase barriers,
  debt ledger, quote ordering, weed repair, finite projects and terminal planner.

This isolates the higher-risk common-route late phase while testing the public
five-action reservation pattern in the earlier phase.

## Artifact

- source: `candidate_v37_h5pre_pkg/main.py`
- archive: `candidate_v37_h5pre.tar.gz`
- source SHA-256: `c92056b01612eb2385965d0213a1ab14bb1476b41c879c94fd99fd2c095cad53`
- archive SHA-256: `cad74e14e026ce17bc7f766447a0444160add4e2d9b62abb1acbf8bfbc2756ae`

## Current local evidence

On seeds 9001–9010 plus mirror seed 1495252849, both seat orders, the
candidate beat the frozen V37 in 22/22 games. Margins were all positive; the
minimum was +740. Every game completed 720 steps without stderr.

The broader cross-opponent panel is complete on seeds 9001–9010, both seats:

- Flex: 20/20 wins, mean margin +5047.4, minimum +2491;
- Thomas: 19/20 wins, one loss −942 (seed 9004, seat 1), mean +5811.4;
- Dmitrii: 20/20 wins, mean +6394.0, minimum +2739.

The single Thomas loss means the candidate does not pass the zero-negative
gate. A narrower 288–575 window was also tested; it regressed on the V37
panel (41 wins, 1 loss, mean +1165.9, minimum −2026), so it is rejected.
This file is a local research record only. No Kaggle submission has been made.
