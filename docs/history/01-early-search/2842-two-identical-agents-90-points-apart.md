

<!-- NOTEBOOK CELL 0 -->

<div class="kgb-hero">
<div class="kgb-kick">Kaggriculture &middot; ladder measurement &middot; a negative result</div>
<h1>Two Identical Agents, 90 Points Apart</h1>
<p><b>I submitted the same bytes twice. The two copies settled 90 rating points apart.</b>
That number is the noise floor of this ladder, and almost every A/B comparison I have seen posted
&mdash; including two of my own &mdash; is smaller than it.</p>
<p>So this notebook is not "here is my agent and it is good". It is the measurement I had to build
before any of my numbers meant anything, the <b>sweep that found a real optimum</b>, and the
<b>negative result where that optimum lost anyway</b> on the live ladder. The agent is included,
byte-exact, at the bottom.</p>
<span class="kgb-chip">90-point noise floor, measured</span><span class="kgb-chip">attack-size sweep</span>
<span class="kgb-chip">a negative result, kept</span><span class="kgb-chip">single main.py</span>
<span class="kgb-chip">no dataset, no GPU</span>
</div>
<div class="kgb-num">
<div class="kgb-stat"><div class="k">same bytes, two entries</div><div class="v">90</div><div class="s">rating points apart &mdash; 2,857 vs 2,767</div></div>
<div class="kgb-stat"><div class="k">self-play said</div><div class="v">n = 10</div><div class="s">the only size that never lost</div></div>
<div class="kgb-stat"><div class="k">the ladder said</div><div class="v">&minus;24</div><div class="s">n=10 scored BELOW n=50</div></div>
<div class="kgb-stat"><div class="k">so the honest answer</div><div class="v">unproven</div><div class="s">24 &lt; 90. It is noise.</div></div>
</div>


<!-- NOTEBOOK CELL 1 -->
## 1. What you are submitting

<div class="kgb-seal">
<div class="h">Artifact identity &mdash; check this first</div>
<p><b>This notebook is the one that made the submission.</b> Its first version produced the archive
that is playing on the leaderboard right now &mdash; the score badge at the top of this page is that
run. Every version since rebuilds the <b>same bytes</b>: the prose has been revised, the artifact has
not moved. These hashes are not my claim about my own build; they are what <b>Kaggle's run of this
notebook produced</b>, read back with <code>kaggle kernels output</code>.</p>
<p><code>submission.tar.gz</code> sha256 <code>c85b86269fdac3b967b6d7adc90b4d30d7f7c49264157fa3893910568d77cd4a</code><br>
<code>main.py</code> sha256 <code>944aa64c5ae1296a9a17eb7961ed8d5a96d0b80183d41e954389983d73420a56</code></p>
<p class="fine">The build cell in section 6 <b>asserts both hashes</b> and stops if either differs, so this
is a check you run rather than a claim you take. These are the exact bytes that played every game
below and that carry this notebook's leaderboard score.</p>
</div>


<!-- NOTEBOOK CELL 2 -->
## 2. The number that invalidated two of my own conclusions

Simulation ladders give you a rating, and a rating feels like a measurement. It is not one until you
know its noise floor. Mine came free, by accident: I had **the same archive live under two entries**
&mdash; byte-identical, same sha256, same everything.

```
entry A (56272485)   91 games   W73 L18        rating 2857
entry B (56276050)  119 games   W88 L26 T4     rating 2786   ... peaked ~2767 at equal game count
```

Same agent. Same bytes. **About 90 rating points apart.** Nothing separates them except which
opponents they happened to be drawn against and when.

<div class="kgb-grid">
<div class="kgb-card rose"><div class="e">What this costs you</div><b>Any ladder A/B smaller than ~90 points is not evidence.</b>
<span>It is a draw you have mistaken for a result. This is not a small correction: it deleted a
conclusion I had already acted on, and it should make you suspicious of every "version N beats
version N&minus;1 by 30 points" claim on the forum, mine included.</span></div>
<div class="kgb-card teal"><div class="e">Why it is so large</div><b>Ratings move in whole wins, against a changing opponent pool.</b>
<span>A win pays about +4 and a loss costs about &minus;6 at this level, and the pool you are drawn
against changes hour by hour as people submit. Two copies of one agent simply do not meet the same
field, so they do not converge to the same number in any practical number of games.</span></div>
</div>

**The practical rule I now use:** the ladder decides nothing under 90 points. Offline, paired,
same-seed, both-seats comparison decides, and the ladder is only there to confirm you have not
broken something. If you want the offline protocol, it is in
[Beyond 48-0](https://www.kaggle.com/code/jaxa623/beyond-48-0-128-128-worlds-with-95-cis) &mdash;
64 independent worlds with bootstrap intervals.


<!-- NOTEBOOK CELL 3 -->
## 3. The attack-size plane

The mechanism this agent uses at step 0 is [Ahmed Berat &Ouml;zer's](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v45-first-turn-wheat-round-trip),
from his public V45: replace the opening market list with `[BUY_PRODUCT WHEAT n, SELL WHEAT n]`.
Because the interpreter settles orders in lockstep by list index, same-index orders of both players
quote at the same inventory &mdash; so your index-0 buy does not make *your own* sell dearer. It makes
the **rival's index-1 order** dearer, and for a rival whose day-0 plan is exactly funded, that costs
them a seed. On day 0. For the whole season.

The open question was `n`. Swept against a 70-unit build, paired margin, 8 seeds &times; 2 seats:

| n | 0 | 10 | 16 | 20 | 25 | 30 | 40 | 45 | 50 | 70 | 85 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| margin | &minus;1,300 | +1,286 | +1,324 | +1,340 | +1,358 | **+1,367** | +1,359 | +1,348 | +1,328 | base | &minus;1,318 | &minus;1,345 |

Three regions, and the **shape** is the finding, not the peak:

<div class="kgb-grid">
<div class="kgb-card"><div class="e">below ~10</div><b>A cliff.</b><span>Too small to break the rival's day-0 funding, so you pay the spread and buy nothing.</span></div>
<div class="kgb-card teal"><div class="e">25 &ndash; 50</div><b>A plateau &mdash; the damage saturates.</b><span>Once their funding is broken, breaking it harder buys you nothing at all.</span></div>
<div class="kgb-card rose"><div class="e">85 and up</div><b>Self-harm.</b><span>Real spread on a large round trip, for damage you already caused at 30.</span></div>
</div>

### The part that generalises

I first read that cliff as a property of the dial. **It is a property of the opponent.** The attack
works by breaking a plan that is *exactly funded*, so the size it needs depends on how much cash
slack the rival has left &mdash; which depends on *their* opening size. Against a 70-unit rival,
n = 10 is already over the cliff. Against a 50-unit rival it is barely over it.

> **An optimum measured against one opponent is not an optimum.**

If you take one thing from this notebook, take that rather than a number. It is also the reason the
next section went the way it did.


<!-- NOTEBOOK CELL 4 -->
## 4. The negative result: self-play chose n = 10, and the ladder disagreed

Applying the rule above, I stopped sweeping against one opponent and built the full round-robin:
every candidate size against every other size, plus the public field. On that matrix **n = 10 is the
only row with no losses at all** &mdash; 8-0 against n=15, n=50, the public Pipe-7 build, V45 and V43.
n=20, n=30 and n=50 all lose to an opponent playing 15.

Ratings count wins, not margins. A row with zero losses is exactly what you want. So I submitted it.

```
n = 50  (K0006)    rating 2857     <- the incumbent
n = 10  (K0009)    rating 2833     <- the "strictly better" build
```

**It scored lower.** And the honest reading is not "n=10 is worse" &mdash; it is:

<div class="kgb-grid">
<div class="kgb-card amber"><div class="e">the honest reading</div><b>24 points is well inside a 90-point noise floor.</b>
<span>The ladder did not say n=10 is worse. It said <i>nothing</i>, and I nearly wrote it up as a
result in both directions.</span></div>
<div class="kgb-card"><div class="e">the real lesson</div><b>Self-play round-robin is not the ladder field.</b>
<span>My matrix contained the opponents I had thought of. The ladder contains the ones other people
thought of. A build that is unbeatable inside your own hypothesis space has only proved something
about your hypothesis space.</span></div>
</div>

**What I would do differently:** decide offline with paired intervals, submit for confirmation only,
and never read a sub-90-point ladder difference as a direction. That is the whole method, and it cost
me two wrong conclusions to buy.


<!-- NOTEBOOK CELL 5 -->
## 5. What the agent actually is

Deliberately small. It is [Ahmed Berat &Ouml;zer's public V43](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v43-recovering-lost-harvests)
&mdash; which does all the actual farming &mdash; plus four rules that touch only the **order** of the
market list, the **timing** of sales, and **one step-0 order**. Nothing about what is planted,
watered, harvested or hired is changed.

<div class="kgb-grid">
<div class="kgb-card"><div class="e">Rule 1</div><b>Front-loading.</b><span>Sells moved to the front of the market list, but only when a per-unit simulation agrees the list still executes in full. It never adds, removes or resizes an order.</span></div>
<div class="kgb-card teal"><div class="e">Rule 2</div><b>Two-turn sale advance.</b><span>Found by re-simulating losses I could not explain: the opponent was selling the same lots two turns earlier, before the town's consumption tick had been eaten into.</span></div>
<div class="kgb-card amber"><div class="e">Rule 3</div><b>Sale-reservation horizon 24.</b><span>A real optimum, not a bigger-is-better dial: 8, 16, 36 and 48 are all worse, and 48 loses mirror games to plain V43.</span></div>
<div class="kgb-card rose"><div class="e">Rule 4</div><b>Step-0 round trip, n = 10.</b><span>The mechanism is &Ouml;zer's, from V45. The size is the subject of sections 3 and 4 &mdash; and, per section 4, is <i>not</i> established as better than 50.</span></div>
</div>

The derivation of rules 1&ndash;3, the eleven experiments that failed, the four-tier acceptance suite
and three measurement traps that produced convincing wrong numbers are all in the companion notebook,
[Beyond 48-0](https://www.kaggle.com/code/jaxa623/beyond-48-0-128-128-worlds-with-95-cis).


<!-- NOTEBOOK CELL 6 -->
## 6. Postscript: the field answered, and that is the best evidence in this notebook

Publishing an edge arms everyone who reads it. Here is that cost, measured, because it is more
interesting than pretending it did not happen.

On 2026-09-16 Ahmed Berat &Ouml;zer published **V46**, which cites the sale-timing analysis from my
Beyond 48-0 notebook by name and re-implements it over his own chassis, together with a turn-0
opening chosen specifically so that round trips like this one cannot hurt it. His own published
evaluation table contains this row:

| rival | his previous version | V46 | points |
|---|---|---|---|
| `pub_beyond48` (my published build) | **0 / 64 / 0** | 52 / 12 / 0 | **+81.2** |

Two things are true at once and both are worth saying. **His previous version lost 0-64 to my
published build** &mdash; an independent reproduction of my central claim, by the author of the agent
it beat. And **V46 then closed that hole completely**: measured locally, 24 seeds &times; both seats,
V46 beats my n=10 build 40-8 and my n=50 build 42-6.

That is how this is supposed to work. The edge was real, it was published, it was countered within a
day, and the counter is better than what it replaced. If you fork anything from this notebook, fork
the measurement discipline in sections 2 and 4 &mdash; those do not expire when someone reads them.


<!-- NOTEBOOK CELL 7 -->
## 7. Build the exact archive

`main.py` travels below as a base85+gzip blob. The cell rebuilds the archive deterministically (GNU tar, `mtime 0`, mode `0644`, gzip `mtime 0`) and **asserts both sha256 values**, so what lands in `/kaggle/working` is bit-identical to what played every game above.

- `main.py` &rarr; `944aa64c5ae1296a9a17eb7961ed8d5a96d0b80183d41e954389983d73420a56`
- `submission_k0006_open10_h24_frontload_advance2_v43.tar.gz` &rarr; `c85b86269fdac3b967b6d7adc90b4d30d7f7c49264157fa3893910568d77cd4a`


<!-- NOTEBOOK CELL 9 -->
## 8. Reproduce, and attribution

The build cell above rebuilt `main.py` and the archive **byte-for-byte** and asserted both hashes.

<div class="kgb-grid">
<div class="kgb-card"><div class="e">Base agent</div><b>Ahmed Berat &Ouml;zer &mdash; V43, Apache-2.0.</b>
<span>Embedded verbatim, all notices retained. <a href="https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v43-recovering-lost-harvests">It is the agent</a>; this is a shell around it. Please upvote it &mdash; it does all the farming here.</span></div>
<div class="kgb-card teal"><div class="e">Mechanism credit</div><b>The step-0 round trip is &Ouml;zer's, from V45.</b>
<span>The size sweep, the cash-slack generalisation and the negative result in section 4 are mine.</span></div>
<div class="kgb-card amber"><div class="e">Upstream</div><b>V43 credits a long chain.</b>
<span>thomastschinkel, yhay81, destbreso, aurax7, tetsutani, prvsiyan, Rayk Kretzschmar and Dmitrii Gluzdov; those notices are retained in the embedded source.</span></div>
<div class="kgb-card rose"><div class="e">Original here</div><b>The 90-point noise floor, the attack-size plane, and a negative result I could have quietly dropped.</b>
<span>2026-09-15/16.</span></div>
</div>

*If the noise floor in section 2 stops you shipping one wrong conclusion, an upvote helps.*
