# Candidate V37 late-sale asymmetry gate

Candidate archive: `candidate_v37_latesale_gate.tar.gz`  
Source SHA-256: `008d5dc4ffd206c9c5049778ff5ae73f8046b83269ef40058cba4b8afdb75827`  
Archive SHA-256: `53e26dd3585ac7ea22ad52d4d0e00ac0b4c3a3f5ba1bb669a33bdebf808f6ae1`

The candidate layers a narrow public-state rule on the frozen V37 policy. Between steps 648 and 695, it considers each product whose visible rival standing yield exceeds ours by at least four units. If the next route turn sells that product, the current turn has no worker or purchase barrier, no pending chassis queue, and the item is already present in the private shed. At most eight units are sold early; an item debt suppresses the corresponding quantity on the next route turn. Zero-quantity orders remain in the market list to preserve lockstep ordering. The layer is enabled by default for local evaluation and can be disabled with `V37_LATESALE_GATE=0`; it never reads rival private state.

## Local panel

Compared with `public_v37_pkg/main.py`, using Kaggle's local `kaggriculture` engine, seeds 9001--9010 plus 1495252849, both seats:

- 22 games: 1 win, 1 loss, 20 ties
- Mean margin: 0.0
- Minimum margin: -1581
- Every game completed 720 steps with no stderr

The sole positive and negative margins occur on seed 9004 in opposite seats, so the rule has no demonstrated aggregate gain and retains a seat-dependent downside. Treat this archive as a research candidate only; do not submit without a broader holdout showing zero negative margins.
