# candidate_v45_q25.py source audit (2026-09-18)

This is a read-only audit of the current source. It does not change the candidate.

## Safe insertion point

The exported callable is assembled in layers. The current final layer is `_OPEN_PARENT`
at line 3476, the wrapper `agent` at lines 3480--3494, and the export guard
`agent=globals().pop('agent')` at line 3496. A new short-window experiment should be
appended after line 3496 as another parent/wrapper pair, and should end with the same
export guard. This makes it observe the complete parent decision (R128, R148, R149,
R150, RACE, and OPEN layers) and prevents later layers from rewriting its output.

Do not insert the experiment before the R36/R37/R128/R148 layers. Those layers append
orders, change quantities, and maintain state that a later layer can invalidate.

## Existing market-order mutations

* `_v224_sales_first`, lines 1478--1494, moves SELL orders left across non-SELL orders;
  it stops at a SELL or a same-item `BUY_PRODUCT`/`BUY_ANIMAL` barrier.
* `_r36_reserve`, lines 1660--1704, appends reservations and records due quantities in
  the chassis `sell_state` (`r36_debts`). The monkey patches at lines 1657--1658 alter
  suppression globally.
* `_r37_reorder_sales`, lines 1807--1826, sorts only contiguous SELL blocks with
  distinct products. It is called by the R37 wrapper at lines 1893--1903.
* The later R97/R128/R148 layers may add or resize grain, seed, and overflow orders
  (roughly lines 2743--3329). Therefore a new order experiment must preserve every
  operation/item/quantity and only permute orders under strict barriers. It must not
  remove, duplicate, or resize an order, and must not move an order across HIRE,
  BUY_LAND, or a same-item BUY barrier.

The current order-only candidate should call the parent first, copy the market list,
apply a bounded permutation, and return the original action on any exception or failed
safety check. Do not build a second market simulator; use the official kernel oracle
for offline evaluation.

## Worker movement call sites

* `_v219_worker`, lines 1339--1391. The nearest-task choice is line 1387. It is
  installed by the V219 wrapper at lines 1429--1445, which also records worker state
  in `_V219_STATES` (line 1228).
* `_v233_worker`, lines 1998--2029. The nearest-task choice is lines 2025--2027. It
  is installed by the V233 wrapper at lines 2082--2100 and uses `_V233_STATES` (line
  1936).
* `_r51_input_path`, lines 2167--2196, already has a bounded beam (width 8, depth 8)
  for fertilizer input paths. `_r53_labor_assignment`, lines 2347--2374, enumerates
  worker-group permutations only during days 26--28, hours 0--2.

Do not replace `_v219_worker` or `_v233_worker` in place for the first experiment.
Their wrappers maintain pending hires, fertilizer loading, harvest credits, and
next-callback confirmations. A changed route can desynchronize those state machines.
If worker planning is later tested, limit it to one actor and a very short suffix,
abstain when R128 service swaps or R148 pending overflow contracts exist, and require
zero overflow plus per-actor deposit dominance against the parent action.

## Existing terminal planner is not reusable for a general window

The planner embedded around lines 1004--1102 is explicitly constrained to steps
712--718. `_shadow_terminal` requires step 711 and route 2; `_PLANNER_NS['simulate']`
rejects other horizons. It is safe only as the existing terminal experiment and should
not be called for mid-game market/order planning.

## Runtime and state hazards

`Chassis.act`, lines 460--501, rebuilds the observation view each callback but keeps
per-player `pending` and `sell_state` in `_IMPL.chassis.players`. The new wrapper should
keep an independent per-player state keyed by `player`, reset on `step == 0` or a
non-increasing step, and avoid mutating `_IMPL.chassis.players`.

The source replaces `copy` with `_R149CopyProxy` at lines 3331--3360. `copy.deepcopy`
continues to work, but repeated full-board clones in every callback are a runtime risk.
Use a trigger gate and a small simulation budget. Always retain the final
`agent=globals().pop('agent')` guard.

