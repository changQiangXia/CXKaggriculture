
CELL 0
# Beyond 48-0 · 128/128 Worlds with 95% CIs | Market Micro-Edges + the Traps That Faked Them

**TL;DR.** This is Ahmed Berat Özer's public **[V43 "Recovering Lost Harvests"](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v43-recovering-lost-harvests)** (Apache-2.0 — it does all the actual farming here) with **four added rules, none of which touch the farm plan**. Every one of them exploits the same single fact about the market, explained in section 1.

| tier | opponents | result |
|---|---|---|
| 24 seeds × both seats | V45 / aurax7 v6 | **48-0** (+2,384) |
| 24 seeds × both seats | V44 / V43 | 47-1 (+1,257) / **48-0** (+1,282) |
| stress clones (counters I built against myself) | open78 / fast24 / open70_h24 | 48-0 / 47-1 / 48-0 |
| **64 independent worlds × both seats** | V45 | **128-0**, +2,087, bootstrap 95% CI **[+1,950, +2,240]** |
| official `kaggle_environments` runner | V45 / V43 | 16-0 / 16-0, 0 errors, 0 slow turns |

The half I think is worth more than the agent is everything after section 5: **the full experiment log including what failed**, the acceptance suite that stopped me shipping three of those failures, and **two measurement traps that produced completely convincing wrong numbers**. One of them told me a candidate had won by +167,366.

Runs on the standard Kaggle image. No datasets, no GPU, no internet.

> If the acceptance suite or the traps save you a day, an upvote helps. Please also upvote [V43](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v43-recovering-lost-harvests) — this notebook is a thin shell around it.


CELL 1
## 1. The one fact the market gives you

The interpreter settles market orders **in lockstep by list index**:

```
order[0] of player 0 → order[0] of player 1 → order[1] of player 0 → order[1] of player 1 → …
```

Two consequences, and everything below is one of them:

**(a) Every executed unit moves the shared inventory.** So the *first* SELL of a product in a turn is quoted before the glut it creates, and the *first* BUY_PRODUCT is quoted before the squeeze it creates. If your sells sit at index 5 and your opponent's sit at index 0, you are selling into a market they already pushed down — a few dollars per unit, every day, for 30 days.

**(b) Same-index orders of both players are quoted at the same inventory.** This is what makes the step-0 attack in section 5 work: your `BUY_PRODUCT WHEAT n` at index 0 does not make *your own* index-0 order dearer — it makes the opponent's **index-1** order dearer.

V43's own tapes routinely list `HIRE`, `BUY_SEED`, `BUY_LAND` before the day's sells. Against a rival running the same tape, whoever's sells sit earlier wins the day. That is the entire thesis.

Nothing here changes what is planted, watered, harvested or hired. The farm plan is V43's. Only the **order of the market list**, the **timing** of sales, and **one step-0 order** are different.


CELL 2
### Watch it happen

The cell below plays V43 against V43-with-the-orders-reordered on a few seeds. Same farm plan, same everything — only the position of the SELL orders in the list differs.


CELL 4
## 2. Edge 1 — market front-loading

Rewrite each turn's market list as:

```
[SELLs that are not wash trades] + [BUY_PRODUCT + the wash SELLs] + [everything else]
```

and keep the original list unless a per-unit simulation of **both** lists — cash, shed capacity, hire costs, land prices, once solo and once under lockstep pressure — says the reordered list still executes in full. It never adds, removes or resizes an order.

That last clause is the whole safety argument. A reorder that makes an order fail is worse than no reorder: V43's plan assumes every order lands.

Measured alone, on top of plain V43: **16-0 vs V43 (+476)**, 16-0 against every public bot I tested (V41, Farming Score V5, Shop Router Reactive V5, V40 Challenger). On the ladder it is a tie-breaker against the V43 family, which is most of the 2,500–2,700 band.


CELL 5
## 3. Edge 2 — the two-turn sale advance

This one I did not design. I found it by re-simulating losses I could not explain.

I kept losing games where both agents produced **identical daily order sets**. Same crops, same volumes, same everything. Re-playing those episodes with the opponent's recorded actions showed the difference: they were selling the same lots **two turns earlier**. Selling earlier means selling before the town's consumption tick has been eaten into by the other player.

So: for pure cash products, look ahead in V43's own tape, and if a sale is planned within the next 2 turns and the goods are already in the shed, bring it forward.

`advance_declined_full` in the telemetry counts the times the look-ahead refused because the earlier sale would not have executed in full.


CELL 6
## 4. Edge 3 — the sale-reservation horizon, and its optimum

V43 reserves (pre-sells) tape sales up to **4 turns** ahead in its 288–696 window. Widening that horizon means committing produce to the market earlier, which is the same race as edge 2 but structural rather than opportunistic.

Sweeping it (paired margin, both seats):

| horizon | result |
|---|---|
| 8 | 2-14 (−404) |
| 16 | 8-8 (−645) |
| **24** | **baseline — optimal** |
| 36 | 10-4-2 (+19) |
| 48 | loses mirror games to plain V43 |

**24 is a genuine optimum, not a bigger-is-better dial.** Past it you are committing produce you have not harvested yet, and V43's own recovery logic starts fighting you. I re-swept this after changing the opening in section 5, because an optimum found under one configuration does not have to survive another — it did.


CELL 7
## 5. Edge 4 — the step-0 wheat round trip, and why 70 is the wrong size

The mechanism is Ahmed's, from his public V45 notebook: at step 0, replace V43's opening market list with a single round trip, `[BUY_PRODUCT WHEAT n, SELL WHEAT n]`. Your index-0 buy lifts the wheat price; because same-index orders quote at the same inventory, **your own sell at index 1 is unharmed but the rival's index-1 wheat buy is ~60 dearer** — which, for a V43-family rival whose day-0 plan is exactly funded, costs them one melon seed. On day 0. For the rest of the season.

V45 ships `n = 70`. I swept it against my own 70-unit build (paired margin, 8 seeds × 2 seats):

| n | 0 | 10 | 16 | 20 | 25 | 30 | 40 | 45 | 50 | 70 | 85 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| margin | −1,300 | +1,286 | +1,324 | +1,340 | +1,358 | +1,367 | +1,359 | +1,348 | **+1,328** | base | −1,318 | −1,345 |

Three regions, and the shape is the interesting part:

- **below ~10** — a cliff. The round trip is too small to break the rival's day-0 funding, so you pay the spread for nothing.
- **25–50** — a plateau. **The damage saturates**: once their funding is broken, breaking it harder buys nothing.
- **85 and above** — self-harm. You are now paying real spread on a large round trip for damage you already caused at 30.

I picked **50**, inside the plateau but with margin above the lower cliff rather than at its optimum, because the cliff is the dangerous side: the opponent pool changes, and a plateau edge that slips below 10 is worth −1,300.

This is the sort of thing that makes a published number worth re-measuring. 70 is not wrong — it is on the far shoulder of a plateau, and the shoulder is where an opponent shift hurts.


CELL 8
## 6. The experiment log — including everything that failed

Published notebooks show what worked. The negatives cost the same GPU-hours and are more useful, so here they all are.

| # | idea | result | kept? |
|---|---|---|---|
| K0002 | market front-loading | 16-0 vs V43 (+476) | **yes** |
| K0003 | two-turn sale advance **alone** | no ladder win gain | no — only pays combined with front-loading |
| K0004 | + sale-reservation horizon 8 | 2,695 on the ladder | superseded |
| K0005 | + step-0 round trip at 70 | 2,597 | superseded |
| K0006 | round trip re-sized to 50, horizon 24 | 2,663 and climbing at the time of writing | **yes** |
| — | animal SHEEP↔COW substitution | −6 wins | no |
| — | feed sweeper | negative | no |
| — | route re-selection | negative | no |
| — | seed recovery | negative | no |
| — | pipe-4 C9 opening | +$1/game — noise | no |
| — | horizons 36 / 48 | lose mirror games to plain V43 | no |

### The one worth writing up: the season-long funding attack

If the step-0 round trip works *because* wheat is market-priced and the rival's plan is exactly funded, then repeating it on **every** turn whose tape buys wheat for feed should raise their feed cost all season and eventually starve an animal. It is the obvious generalisation. I built it (26–28 attacks per game) and it lost:

| attack size | result vs the unattacked build |
|---|---|
| 30 | **0-16** (−594) |
| 50 | **2-14** (−1,091) |

It also weakened the agent against V45 (+1,311 instead of +2,384).

**Why it fails:** the day-0 attack works because on day 0 the rival's purchase is *tightly funded*. By mid-season both farms hold enough cash that the same price bump changes nothing — so you pay the spread ~27 times and buy nothing. The edge was never "make wheat expensive"; it was "break a purchase that has no slack". Dropped.


CELL 9
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


CELL 10
## 8. Two traps that produced completely convincing wrong numbers

### Trap 1 — auditing against a wrapper file gives you a fake landslide

My candidates are built as wrappers: a small file that loads the V43 parent from a relative path and patches it. Convenient for sweeps. Then I ran the official-runner audit with a *wrapper* as the opponent and got:

```
candidate vs opponent:  16-0,  margin +167,366
```

which I very nearly believed for longer than I would like to admit.

`kaggle_environments` **exec's the agent source** rather than importing the file, so the wrapper's relative-path parent load fails. The opponent then PASSes every single turn and finishes the season on its 3,000 starting money. You are not beating it; you are watching it not play.

**Always audit against the packaged single-file `main.py` you would actually submit.** Re-run against the package: 16-0, **+1,328** — which matches the local harness (+1,333) and the 64 worlds (+1,334). Three independent numbers agreeing is the check; one spectacular number is a bug.

### Trap 2 — the evaluation dies exactly when it gets interesting

Long sweeps were being OOM-killed at 6 GB, always deep into a run. Each candidate module left ~40 MB in `sys.modules`, and wrappers load their parent under *the parent's* name, so deleting only my own `ag_*` entries was not enough:

```python
_BASE_MODULES = set(sys.modules)            # at import time

def fresh(path, tag):
    for k in [k for k in sys.modules if k not in _BASE_MODULES]:
        del sys.modules[k]                  # everything any earlier agent dragged in
    gc.collect()
    ...
```

Memory went flat at ~50 MB. Obvious afterwards; it cost a day of sweeps that died at game 200 of 256.


CELL 11
## 9. Build the exact archive

`main.py` is carried below as a base85+gzip blob. The cell rebuilds the submission archive deterministically (GNU tar, mtime 0, mode 0644, gzip mtime 0) and asserts both sha256 values, so what you get is bit-identical to what played the games — not a re-export that happens to behave the same.

- `main.py` sha256 `4757f3f5b28db8a2f4614bb08993a8a567a7d49bae1ac324fbcfbcc1af60e95e`
- `submission_k0006_open50_h24_frontload_advance2_v43.tar.gz` sha256 `66ee4fd7a169c10c3a313c9696b96b8661be9eea691736d0ffaa7b1a71e66582`


CELL 13
## 10. Reproduce, and attribution

Section 9 wrote `main.py` and rebuilt the submission archive **byte-for-byte**, asserting both sha256 values. That is the same archive that played the games in the table at the top — you can check the hash against the one printed there.

To point the acceptance suite at your own agent, the structure is small enough to re-implement: label seeds into worlds by truncating a V43 mirror game at step 145, keep one unseen seed per world, play both seats, bootstrap the paired margins at the world level.

### Attribution

- **[V43 "Recovering Lost Harvests"](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v43-recovering-lost-harvests)**, Ahmed Berat Özer, Apache-2.0 — embedded verbatim, all notices retained. It is the agent; this notebook is a shell around it.
- The step-0 round-trip **mechanism** is also Ahmed's, described in his public V45 notebook. The size sweep in section 5, and the finding that 70 sits on the far shoulder of the plateau, are mine.
- V43 itself carries attribution to thomastschinkel, yhay81, destbreso, aurax7, tetsutani, prvsiyan, Rayk Kretzschmar and Dmitrii Gluzdov; those notices are retained in the embedded source.
- Front-loading, the two-turn advance, the horizon sweep, the acceptance suite and the two traps are original work, 2026-09-15/16.
