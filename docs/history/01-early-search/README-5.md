# v37 pressure shift (rejected)

This branch tests one falsifiable intervention on frozen v37: during the final
liquidation window (steps 648--694), if the current turn contains only SELL
orders, a visible rival has at least eight ripe units of a premium product, and
the native next turn sells that product, move at most eight physically available
units one turn earlier. A debt entry is written into v37's existing `r36_debts`
ledger so the native next-turn sale is suppressed, preserving quantity and
avoiding speculative stock. No opponent private state is read, no purchase or
barrier turn is touched, and all malformed/ambiguous states fall back to v37.

The branch is rejected and retained only as a negative research record. A
structural audit found that its implementation mutates the post-reorder parent
action and does not prove that the next turn is barrier-free. It must not be
submitted or used as evidence of an improvement.
