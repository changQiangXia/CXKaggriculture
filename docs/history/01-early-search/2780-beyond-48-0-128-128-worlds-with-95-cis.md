

<!-- NOTEBOOK CELL 0 -->

<div class="kgb-hero">
<div class="kgb-kick">Kaggriculture &middot; market micro-structure &middot; bootstrap-verified</div>
<h1>Beyond 48-0</h1>
<p><b>Every notebook here reports a win count. None of them report an interval.</b> This one plays 128 games
per claim across 64 independent worlds, publishes a bootstrap 95% CI for each, and shows the worst world
rather than the average — because a mean hides exactly the case that will cost you the ladder.</p>
<p>The agent is Ahmed Berat &Ouml;zer's public <b>V43</b> with four added rules, none of which touch the farm plan.
The half worth more than the agent starts at section 5: <b>every failed experiment</b>, the acceptance suite that
caught three regressions, and <b>three measurement traps that produced completely convincing wrong numbers</b>.
One of them told me a candidate had won by +167,366.</p>
<span class="kgb-chip">64 independent worlds</span><span class="kgb-chip">bootstrap 95% CI</span>
<span class="kgb-chip">official runner audited</span><span class="kgb-chip">single main.py</span>
<span class="kgb-chip">no dataset, no GPU, no internet</span>
</div>

<div class="kgb-num">
<div class="kgb-stat"><div class="k">64 worlds &times; both seats</div><div class="v">128-0</div><div class="s">vs V45 &nbsp;+2,087 &nbsp;CI [+1,950, +2,240]</div></div>
<div class="kgb-stat"><div class="k">worst single world</div><div class="v">+1,289</div><div class="s">not the mean — the floor</div></div>
<div class="kgb-stat"><div class="k">dev set, 24 seeds &times;2</div><div class="v">48-0</div><div class="s">vs V45 and aurax7 v6</div></div>
<div class="kgb-stat"><div class="k">official runner</div><div class="v">16-0</div><div class="s">0 errors, 0 slow turns</div></div>
</div>


<!-- NOTEBOOK CELL 1 -->
## 1. What you are submitting

<div class="kgb-seal">
<div class="h">Artifact identity</div>
<p><b>Every version of this notebook rebuilds the same bytes as version 1.</b> The prose
around it has been rewritten; the artifact has not moved.</p>
<p><code>submission.tar.gz</code> sha256 <code>66ee4fd7a169c10c3a313c9696b96b8661be9eea691736d0ffaa7b1a71e66582</code><br>
<code>main.py</code> sha256 <code>4757f3f5b28db8a2f4614bb08993a8a567a7d49bae1ac324fbcfbcc1af60e95e</code></p>
<p class="fine">The build cell <b>asserts both hashes</b> and stops if either
differs, so this is a check you run rather than a claim you take. These are the exact bytes that played every game
in the table at the top and that carry this notebook's leaderboard score.</p>
</div>


<!-- NOTEBOOK CELL 2 -->
## How to read this

<div class="kgb-road">
<div class="kgb-step"><span class="n">1</span><span class="t">One fact</span><span class="d">The interpreter settles market orders in lockstep by list index. Everything below is a consequence of that single sentence.</span></div>
<div class="kgb-step"><span class="n">2</span><span class="t">Four rules</span><span class="d">Front-loading, a two-turn sale advance, a wider reservation horizon, and one step-0 order. The farm plan is untouched.</span></div>
<div class="kgb-step"><span class="n">3</span><span class="t">What failed</span><span class="d">Eleven experiments that did not survive, including the obvious generalisation of the one that worked.</span></div>
<div class="kgb-step"><span class="n">4</span><span class="t">How I check</span><span class="d">Four tiers ending in a bootstrap interval, because 16-0 on 8 seeds has fooled me more than once.</span></div>
<div class="kgb-step"><span class="n">5</span><span class="t">Three traps</span><span class="d">Measurement bugs that produced numbers I believed. Worth your time even if you skip the agent.</span></div>
</div>


<!-- NOTEBOOK CELL 3 -->
## 2. The one fact the market gives you

The interpreter settles market orders **in lockstep by list index**:

```
order[0] of player 0 -> order[0] of player 1 -> order[1] of player 0 -> order[1] of player 1 -> ...
```

Two consequences, and every edge below is one of them.

<div class="kgb-grid">
<div class="kgb-card"><div class="e">Consequence A</div><b>Every executed unit moves the shared inventory.</b>
<span>So the <i>first</i> SELL of a product is quoted before the glut it creates, and the <i>first</i> BUY_PRODUCT
before the squeeze it creates. If your sells sit at index 5 and your rival's at index 0, you are selling into a
market they already pushed down — a few dollars a unit, every day, for thirty days.</span></div>
<div class="kgb-card teal"><div class="e">Consequence B</div><b>Same-index orders of both players quote at the same inventory.</b>
<span>Your <code>BUY_PRODUCT WHEAT n</code> at index 0 therefore does not make <i>your own</i> index-0 order dearer.
It makes the rival's <b>index-1</b> order dearer. That asymmetry is the whole step-0 attack.</span></div>
</div>

V43's own tapes routinely list `HIRE`, `BUY_SEED`, `BUY_LAND` before the day's sells. Against a rival running the
same tape, whoever's sells sit earlier wins the day. That is the entire thesis.

Nothing here changes what is planted, watered, harvested or hired. Only the **order** of the market list, the
**timing** of sales, and **one step-0 order**.


<!-- NOTEBOOK CELL 4 -->
## 3. The four rules

<div class="kgb-grid">
<div class="kgb-card"><div class="e">Rule 1 &middot; front-loading</div><b>Move the SELLs to the front — but only if a simulation says the list still executes in full.</b>
<span>Rewritten as <code>[non-wash SELLs] + [BUY_PRODUCT + wash SELLs] + [everything else]</code>, kept only when a
per-unit simulation of <i>both</i> lists — cash, shed capacity, hire costs, land prices, once solo and once under
lockstep pressure — agrees. It never adds, removes or resizes an order. That clause is the whole safety argument:
a reorder that makes an order fail is worse than no reorder, because V43's plan assumes every order lands.
Alone: <b>16-0 vs V43 (+476)</b>.</span></div>

<div class="kgb-card teal"><div class="e">Rule 2 &middot; two-turn sale advance</div><b>I did not design this one. I found it by re-simulating losses I could not explain.</b>
<span>Games where both agents produced <i>identical</i> daily order sets, and I still lost. Replaying them against
the opponent's recorded actions showed it: they were selling the same lots <b>two turns earlier</b>, before the
town's consumption tick had been eaten into. So for pure cash products, look ahead in V43's own tape and bring the
sale forward. <code>advance_declined_full</code> counts the times the look-ahead refused because the earlier sale
would not have executed in full.</span></div>

<div class="kgb-card amber"><div class="e">Rule 3 &middot; reservation horizon</div><b>24 is a real optimum, not a bigger-is-better dial.</b>
<span>V43 reserves tape sales up to 4 turns ahead. Sweeping it: 8 &rarr; 2-14, 16 &rarr; 8-8, <b>24 &rarr; best</b>,
36 &rarr; 10-4-2, 48 &rarr; loses mirror games to plain V43. Past 24 you are committing produce you have not
harvested and V43's own recovery logic starts fighting you. I re-swept this after changing the opening, because an
optimum found under one configuration does not have to survive another.</span></div>

<div class="kgb-card rose"><div class="e">Rule 4 &middot; the step-0 round trip</div><b>The published size is on the far shoulder of a plateau.</b>
<span>The mechanism is Ahmed's, from V45: at step 0 replace the opening list with <code>[BUY_PRODUCT WHEAT n,
SELL WHEAT n]</code>. By consequence B this leaves your own sell unharmed and makes the rival's index-1 wheat buy
~60 dearer — which, for a rival whose day-0 plan is exactly funded, costs them a melon seed. On day 0. For the rest
of the season. See the sweep below for why the size matters more than it looks.</span></div>
</div>

### The size sweep, and the shape that matters

Swept against a 70-unit build (paired margin, 8 seeds &times; 2 seats):

| n | 0 | 10 | 16 | 20 | 25 | 30 | 40 | 45 | 50 | 70 | 85 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| margin | &minus;1,300 | +1,286 | +1,324 | +1,340 | +1,358 | **+1,367** | +1,359 | +1,348 | +1,328 | base | &minus;1,318 | &minus;1,345 |

Three regions, and the shape is the point:

- **below ~10** — a cliff. Too small to break the rival's day-0 funding, so you pay the spread for nothing.
- **25&ndash;50** — a plateau. **The damage saturates**: once their funding is broken, breaking it harder buys nothing.
- **85 and up** — self-harm. Real spread on a large round trip, for damage you already caused at 30.

The published 70 is not wrong; it sits on the far shoulder, and the shoulder is where an opponent shift hurts.

**The part I got wrong first, and the general lesson:** I read that cliff as a property of the dial. It is a
property of the *opponent*. The attack works by breaking a plan that is exactly funded, so the size it needs
depends on how much cash the rival has left — which depends on *their* opening size. Against a 70-unit rival,
n = 10 is already over the cliff. Against a 50-unit rival it is barely over it. **An optimum measured against one
opponent is not an optimum.** If you take one thing from this notebook, take that rather than a number.


<!-- NOTEBOOK CELL 5 -->
## 4. The experiment log, failures included

Published notebooks show what worked. The negatives cost the same hours and are more useful, so here they all are.

| # | idea | result | kept? |
|---|---|---|---|
| 1 | market front-loading | 16-0 vs V43 (+476) | **yes** |
| 2 | two-turn sale advance **alone** | no ladder gain | no — only pays combined with front-loading |
| 3 | + reservation horizon 8 | 2,695 on the ladder | superseded |
| 4 | + step-0 round trip at 70 | 2,597 | superseded |
| 5 | round trip re-sized, horizon 24 | 2,857 | **yes** |
| 6 | animal SHEEP&harr;COW substitution | &minus;6 wins | no |
| 7 | feed sweeper | negative | no |
| 8 | route re-selection | negative | no |
| 9 | seed recovery | negative | no |
| 10 | pipe-4 C9 opening | +$1/game — noise | no |
| 11 | horizons 36 / 48 | lose mirror games to plain V43 | no |

### The one worth writing up: the season-long funding attack

If the step-0 round trip works *because* wheat is market-priced and the rival's plan is exactly funded, then
repeating it on **every** turn whose tape buys wheat for feed should raise their cost all season and eventually
starve an animal. It is the obvious generalisation. I built it — 26&ndash;28 attacks a game — and it lost:

| attack size | result vs the unattacked build |
|---|---|
| 30 | **0-16** (&minus;594) |
| 50 | **2-14** (&minus;1,091) |

It also weakened the agent against V45 (+1,311 instead of +2,384).

**Why it fails:** day 0 works because the rival's purchase is *tightly funded*. By mid-season both farms hold
enough cash that the same price bump changes nothing — so you pay the spread 27 times and buy nothing. The edge was
never "make wheat expensive"; it was "break a purchase with no slack". Dropped.


<!-- NOTEBOOK CELL 6 -->
## 5. Why "16-0 on 8 seeds" is not evidence

Eight seeds &times; two seats is 16 games of a 720-turn stochastic game. I have been comfortably fooled by 16-0.
The suite that stopped me shipping three regressions:

<div class="kgb-grid">
<div class="kgb-card"><div class="e">Tier 1</div><b>Development set — 24 fixed seeds, both seats.</b>
<span>Fast enough to run on every candidate. It is also, by construction, the set I tune on — so it cannot be the
set I judge on.</span></div>
<div class="kgb-card teal"><div class="e">Tier 2</div><b>Stress clones — the counter I would build against myself.</b>
<span><code>open78</code> (V43 with a <i>bigger</i> step-0 attack), <code>fast24</code> (V43 with my own horizon),
<code>open70_h24</code> (opening and horizon, no micro-edges). A candidate that only beats the public field has not
met anyone who read this notebook.</span></div>
<div class="kgb-card amber"><div class="e">Tier 3</div><b>64 independent worlds, with a bootstrap interval.</b>
<span>A "world" is the ordered pair of the first two shops — what actually determines the season. There are 64. I
label random seeds by truncating a V43 mirror game at step 145, keep one <b>never-tuned</b> seed per world, play
both seats, and bootstrap the paired margins at the world level.</span></div>
<div class="kgb-card rose"><div class="e">Tier 4</div><b>The official runner, against a packaged file.</b>
<span>Everything above uses my own fast harness. The final audit runs under <code>kaggle_environments</code> itself,
checking errors and slow turns as well as the result. Section 6 explains why the word <i>packaged</i> is doing a lot
of work there.</span></div>
</div>

The interval is the number I decide on:

```
128-0 vs V45,            paired margin +2,087    95% CI [+1,950, +2,240]
128-0 vs the predecessor,               +1,334   95% CI [+1,327, +1,342]
worst single world:                     +1,289
```

A worst-world that is still positive is a far stronger claim than any win count. **An edge whose CI lower bound
touches zero is not an edge, whatever the record says.**


<!-- NOTEBOOK CELL 7 -->
## 6. Three traps that produced convincing wrong numbers

### Trap 1 — auditing against a wrapper gives you a fake landslide

My candidates are built as wrappers: a small file that loads the V43 parent from a relative path and patches it.
Convenient for sweeps. Then I ran the official-runner audit with a *wrapper* as the opponent:

```
candidate vs opponent:  16-0,  margin +167,366
```

which I believed for longer than I would like to admit.

`kaggle_environments` **exec's the agent source** rather than importing the file, so the wrapper's relative-path
parent load fails. The opponent then PASSes every turn and finishes on its 3,000 starting money. You are not
beating it; you are watching it not play.

**Always audit against the packaged single-file `main.py` you would actually submit.** Re-run against the package:
16-0, **+1,328** — matching the local harness (+1,333) and the 64 worlds (+1,334). Three independent numbers
agreeing is the check. One spectacular number is a bug. I now also print the opponent's minimum final money: a
PASSing opponent ends near 3,000, so that one line catches this trap on sight.

### Trap 2 — the evaluation dies exactly when it gets interesting

Long sweeps were OOM-killed at 6 GB, always deep into a run. Each candidate module left ~40 MB in `sys.modules`,
and wrappers load their parent under *the parent's* name, so deleting only my own `ag_*` entries was not enough:

```python
_BASE_MODULES = set(sys.modules)            # at import time

def fresh(path, tag):
    for k in [k for k in sys.modules if k not in _BASE_MODULES]:
        del sys.modules[k]                  # everything any earlier agent dragged in
    gc.collect()
    ...
```

Memory went flat at ~50 MB. Obvious afterwards; it cost a day of sweeps that died at game 200 of 256.

### Trap 3 — a default argument silently replaced the agent under test

The newest one, and the same family as trap 1: *the opponent file was not what I thought it was.*

My build script took an output directory as `argv[1]` and **defaulted to the shipped artifact's directory** when
called with no arguments. One bare invocation later, the packaged agent on disk had been quietly replaced by a
default build with a different horizon — same filename, same size, no error. Every evaluation for the next two
hours played a different opponent than its label claimed.

The tar.gz was untouched, so the original was recoverable and the damage was bounded. Two changes:

```python
if len(sys.argv) < 2:
    raise SystemExit("needs an explicit output dir")      # no silent default
if OUT.name in SHIPPED_ARTIFACTS and "--force" not in sys.argv:
    raise SystemExit(f"refusing to write into {OUT.name}")  # shipped artifacts are read-only
```

**The general shape of all three:** the number was fine; the thing being measured was not what the label said. If
you take a second thing from this notebook, take the habit of printing what the opponent actually *is* — its hash,
its parameters, its final money — next to every result.


<!-- NOTEBOOK CELL 8 -->
## 7. Inside one turn

<div class="kgb-flow">
<span class="d">current observation</span><br>
&nbsp;&nbsp;&darr;<br>
<b>V43 parent</b> <span class="d">— route, planting, watering, harvest, hiring, land, and the day's market list</span><br>
&nbsp;&nbsp;&darr;<br>
<b>step-0 substitution</b> <span class="d">— only on turn 0, and only if the list is exactly V43's opening</span><br>
&nbsp;&nbsp;&darr;<br>
<b>reservation horizon</b> <span class="d">— answers 24 wherever the parent asked for 4</span><br>
&nbsp;&nbsp;&darr;<br>
<b>two-turn advance</b> <span class="d">— brings a planned sale forward when the goods are already in the shed</span><br>
&nbsp;&nbsp;&darr;<br>
<b>front-loading</b> <span class="d">— reorders the list, never resizes it, and reverts if the simulation objects</span><br>
&nbsp;&nbsp;&darr;<br>
<span class="d">action</span>
</div>

Each layer can decline. If every one of them declines, what leaves this agent is exactly what V43 would have played.


<!-- NOTEBOOK CELL 9 -->
## 8. Build the exact archive

`main.py` travels below as a base85+gzip blob. The cell rebuilds the submission archive deterministically — GNU tar, `mtime 0`, mode `0644`, gzip `mtime 0` — and **asserts both sha256 values**, so what lands in `/kaggle/working` is bit-identical to what played the games above. Not a re-export that happens to behave the same: the same bytes.

- `main.py` &rarr; `4757f3f5b28db8a2f4614bb08993a8a567a7d49bae1ac324fbcfbcc1af60e95e`
- `submission_k0006_open50_h24_frontload_advance2_v43.tar.gz` &rarr; `66ee4fd7a169c10c3a313c9696b96b8661be9eea691736d0ffaa7b1a71e66582`

If either assertion fires, the notebook has drifted and you should not trust the table at the top.


<!-- NOTEBOOK CELL 11 -->
## 9. Reproduce, and attribution

The build cell above rebuilt `main.py` and the archive **byte-for-byte** and asserted both hashes — the same bytes
that played every game in the table at the top.

The acceptance suite is small enough to re-implement: label seeds into worlds by truncating a V43 mirror game at
step 145, keep one unseen seed per world, play both seats, bootstrap the paired margins at the world level.

<div class="kgb-grid">
<div class="kgb-card"><div class="e">Base agent</div><b>Ahmed Berat &Ouml;zer &mdash; V43 "Recovering Lost Harvests", Apache-2.0.</b>
<span>Embedded verbatim, all notices retained. <a href="https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v43-recovering-lost-harvests">It is the agent</a>; this notebook is a shell around it. Please upvote it — it does all the actual farming here.</span></div>
<div class="kgb-card teal"><div class="e">Mechanism credit</div><b>The step-0 round trip is also Ahmed's, from his public V45.</b>
<span>The size sweep in section 2, and the finding that the optimum moves with the opponent's cash slack, are mine.</span></div>
<div class="kgb-card amber"><div class="e">Upstream</div><b>V43 itself credits a long chain.</b>
<span>thomastschinkel, yhay81, destbreso, aurax7, tetsutani, prvsiyan, Rayk Kretzschmar and Dmitrii Gluzdov; those
notices are retained in the embedded source.</span></div>
<div class="kgb-card rose"><div class="e">Original here</div><b>Front-loading, the two-turn advance, the horizon sweep, the acceptance suite and the three traps.</b>
<span>2026-09-15/16.</span></div>
</div>

*If the acceptance suite or the traps save you a day, an upvote helps.*
