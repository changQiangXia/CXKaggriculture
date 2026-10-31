# v37 pressure shift report (2026-09-14)

## Hypothesis
A high visible rival production pressure immediately before terminal
liquidation can make one-turn-earlier premium sales profitable. The intervention
is limited to MILK, WOOL, STRAWBERRY and CARROT, requires current market prices
(MILK >= 140, WOOL >= 180, STRAWBERRY >= 100, CARROT >= 30), visible rival ripe
yield >= 8, and a native SELL of the same item on the following turn. At most
8 units are shifted, bounded by current projected shed stock.

## Safety contract

- Steps 648--694 only; no changes during production or purchase windows.
- Current action must be non-empty and SELL-only, with no existing sale for the
  selected item.
- The next native route action must contain a positive SELL quantity.
- Shifted quantity is bounded by projected own stock and written to the parent
  `r36_debts` ledger; native suppression removes exactly that quantity next turn.
- Uses only public rival tiles (`yield_units`), never rival private inventory.
- Exceptions return the unmodified parent action.

## Validation completed

- `python -m py_compile main.py`: PASS.
- Synthetic unit test exercised a 5-unit MILK shift and verified debt
  `{649: {'MILK': 5}}`: PASS.
- No Kaggle upload was attempted.

## Status

`rejected_structural_violation`: the branch is archived and must not be
treated as a submission candidate. Structural audit found that it appends a
SELL after the parent R36 reserve and V224 sales reorder, does not require the
next turn to be barrier-free, relies on an implicit route-2 side effect, and
mutates the parent market/debt objects in place. Its exception path therefore
cannot guarantee an unchanged v37 fallback. A single Flex screening trace
also showed a -2 paired margin; no further panel is warranted for this
implementation.
