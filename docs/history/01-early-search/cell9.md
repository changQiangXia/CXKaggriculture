## 7. Why "16-0 on 8 seeds" is not evidence

Eight seeds × two seats is 16 games of a 720-turn stochastic game. I have been comfortably fooled by 16-0. The suite that stopped me shipping three regressions:

**Tier 1 — a development set of 24 fixed seeds, both seats.** Fast enough to run on every candidate. It is also, by construction, the set I tune on — so it cannot be the set I judge on.

**Tier 2 — a stress-clone library.** Before an upload I build the counter I would build if I were my opponent, and play against it: `open78` (V43 with a *bigger* step-0 attack), `fast24` (V43 with my own horizon), `open70_h24` (the opening and the horizon, without the micro-edges). A candidate that only beats the public field is a candidate that has not met anyone who has read this notebook.

**Tier 3 — 64 independent worlds with bootstrap confidence intervals.** A "world" here is the ordered pair of the first two shops, which is what actually determines the season. There are 64 of them. I labelled random seeds by truncating a V43 mirror game at step 145, kept one **never-tuned** seed per distinct world, and play both seats in each. Then a **world-level bootstrap** over the paired margins gives a 95% interval.

That interval is the number I make decisions on:

```
128-0 vs V45,       paired margin +2,087   95% CI [+1,950, +2,240]
128-0 vs the predecessor, +1,334           95% CI [+1,327, +1,342]
worst single world: +1,289
```

A worst-world that is still positive is a much stronger claim than any win count. **An edge whose CI lower bound touches zero is not an edge, whatever the record says.**

**Tier 4 — the official runner.** Everything above uses my own fast harness. Before the hash goes out, the final audit runs under `kaggle_environments` itself, checking for errors and slow turns as well as the result. See section 8 for why that matters more than it sounds.
