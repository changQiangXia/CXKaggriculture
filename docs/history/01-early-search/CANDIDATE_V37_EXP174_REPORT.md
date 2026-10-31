# EXP-174 local candidate screening (2026-09-12)

Scope: low-risk ablations of `public_v37_pkg/main.py`; no Kaggle submission. Source package remains unchanged.

## Motivation from latest Flex losses

Replays 108058678 and 108059677 (submission 56176848) show losses of only 907 and 114 funds, with normal 720-step completion and no stderr. Flex's final sales differ in quantity/order (395–450 SELL orders), while action counts otherwise mirror the stable route. This points to shared-market timing and terminal inventory handling rather than runtime faults. Candidate changes were therefore limited to disabling existing narrow overlays.

## Candidates

- `candidate_v37_nosheep.tar.gz` (`a209d0a3...`): disables V233 six-sheep eligibility by overriding `_v233_eligible`; all other V37 logic unchanged. `py_compile` passes. On seeds 9001–9003 versus Flex, rewards were identical to baseline V37 for every run; the branch did not trigger under these seeds. This is behaviorally equivalent on the tested panel and provides no demonstrated gain.
- `candidate_v37_noquote.tar.gz` (`2581c021...`): disables V37 visible-rival quote sale reordering (`_R37_QUOTE=False`). `py_compile` passes. Versus Flex:
  - seed 9001: baseline `109922:108137`; noquote `109310:108553` (seat0 −612, seat1 +416)
  - seed 9002: baseline `64433:61971`; noquote `63436:62913` (seat0 −997, seat1 +942)
  - seed 9003: baseline `60679:58365`; noquote `59144:59864` (seat0 −1535, seat1 +1499)
  The change shifts advantage to seat1 but loses substantial seat0 value; not robust and rejected.

Control runs used official local `kaggle_environments` 1.25.9, 720 steps, all status `DONE`. No candidate demonstrated a clear improvement over V37. Keep both archives for traceability only; do not submit without fresh evidence and explicit authorization.
