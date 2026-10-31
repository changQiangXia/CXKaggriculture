# The complete story

One document covering the whole competition: what we set out to do, everything
we tried, what worked, what did not, and what we still do not know.

Scope: **2026-07-30** (competition opened) through **2026-10-02** (this
writing, two days after submissions closed).  Work in earnest began
**09-12**.  Raw notes for every day are in `history/`.

---

## 1. Setting

**Kaggriculture** — Kaggle Featured competition, $50,000 prize pool.

Two agents farm a 10×10 board for 720 turns (30 in-game days).  They plant and
water crops, raise livestock, hire hands, and trade on a **shared market**
whose prices move with a common inventory.  Score = final bank.

The constraints that shaped every decision:

| constraint | consequence |
|---|---|
| **5 submissions/day but only the latest 2 are active** | every submission evicts one; nothing can be hoarded |
| the ladder is slow (a bot plays a few games per hour) and noisy | you cannot tune on live results |
| episodes are matched by skill rating | who you play depends on where you are |
| final standing = **two-week Bradley-Terry rerun** after submissions close | your score keeps moving after you stop |

**Submissions closed 2026-09-30 23:59 UTC** (Beijing 10-01 08:00).  The
leaderboard then kept playing until **2026-10-14 23:59 UTC**.

**The user's goals, stated at the outset and held throughout:**

1. reach the **top 200** (the 200th-place score was ~2697 when we started);
2. **never submit without explicit approval** — five chances a day was the
   scarce resource, not compute;
3. prefer stable strategy work over aggressive training (single RTX 4090).

Those three rules governed the entire project.  There is no submission in this
archive's history that was pushed without an explicit instruction.

---

## 2. The one-paragraph version

We began by evaluating public bots and building a local evaluator we could
trust.  That evaluator — a behavioural replica of the official engine plus
panels of recorded opponents — became the project's centre of gravity, and the
single hardest problem turned out to be **making it tell the truth about
live strength**.  Over three weeks we evolved a "tape + policy layers"
architecture, mapped the field band by band, and generated hundreds of
candidates, most of which died under fidelity-filtered paired testing.  In the
final 38 hours we swept sixty constants and found exactly **one** genuine
untaken switch, worth +84 margin per game, which had previously been discarded
because the first sweep had used win/loss counts.  The submission built on it
scored **2098.7 — top 4.6% of 10,246 teams, silver-medal band, but short of the
top-200 goal.**  A direct self-play duel then contradicted the replay harness
about which of our own candidates was better, and the ladder sided with the
duel.  That contradiction is the archive's outstanding open question.

---

## 3. Phase 1 — building something we could trust (09-12 .. 09-18)

### 3.1 First act: audit the engine

Before optimising anything we checked whether local results meant anything.
Online replays report `module_version=1.32.7`; the installed package said
`1.25.9`.  So we replayed four online episodes action-by-action through the
local interpreter and compared **every semantic observation** after every
transition.

| replay | steps compared | first divergence |
|---|---|---|
| 108204611 | 720 | none |
| 108205627 | 720 | none |
| 108206966 | 720 | none |
| 108208668 | 720 | none |

Zero divergence, identical final rewards.  The version-string gap was
cosmetic.  **This is the audit the rest of the project rests on** — without it,
three weeks of local numbers would have been unfalsifiable.

### 3.2 The evaluator

The ladder gives you a handful of games per hour.  To iterate at all we needed
a local substitute, and it had to be honest.  The protocol that emerged:

* **seeds from public notebooks** rather than self-chosen ones, so we could
  not tune into a friendly corner: `7000-7002`, `8000-8002`, `9001-9014`,
  `184901-184902`, `70117`, `20260907`, `451781128`;
* each candidate played full 720-step games against public reference bots
  (Flex, Thomas, Dmitrii) **in both seat orders**;
* accepted metrics: W/L/T, mean and worst bank margin, seat asymmetry, DONE
  rate, action latency, standalone load-after-unpack;
* every candidate had to load from a tar containing **only `main.py`**.

That last rule came from a failure.  Our second submission errored in
validation because it expected an external `actions.json`; Kaggle loads only
`main.py`.  After that, packaging was part of the acceptance test.

### 3.3 First submissions

| ref | file | result |
|---|---|---|
| 56170379 | `submission_v1.tar.gz` | complete, ~1100–1165 — far below target |
| 56170496 | `submission_v2.tar.gz` | **ERROR** — tar artifact handling |
| 56170591 | `submission_v3.tar.gz` | complete, ~997–1598 — unstable |
| 56170774 | `submission_v4.tar.gz` | **ERROR** — expected `/kaggle_simulations/agent/actions.json` |
| 56171485 | `dmitri_final_submission.tar.gz` | complete, ~847 climbing |

Top-200 sat at ~2697.  We were nowhere near it, and the first real lesson had
already arrived: **the distance between "works locally" and "scores on the
ladder" is not a detail, it is the problem.**

### 3.4 The mirror problem

A public write-up ("The 2945 Farm: 96% vs the Top-10 Public Bots") was the
strongest thing available.  The user's read of it was sharp and became a
recurring theme:

> the stronger a public bot is, the more of the ladder is running a clone of
> it — so *copying it* means your most common opponent is yourself.

Mirror games against a near-identical policy end in near-exact ties, and ties
cost a high-rated account rating.  So merely adopting the best public bot was
self-defeating.  We measured it: farm2945 against itself, 36 worlds →
**3W / 3L / 66 ties**, the small asymmetries worth only ±78–125 bank.

That framing — *you must beat the clones of the thing you are standing on* —
produced the first structural idea: a **two-phase agent**.  Conservative for
the first 200 turns (don't race the animal-product book), then aggressive
(sell everything, no price floor).  It stayed strong against the farm2945
mirror and against aggressive clones, without needing a detector.

### 3.5 What this phase really built

Not a winner — a **measurement capability**.  By 09-18 we had: verified engine,
public-seed protocol, tar-only packaging, seat-symmetric evaluation, and the
first statement of the fidelity problem (a recorded opponent cannot react, so
panels overstate).  Every later result is downstream of these.

---

## 4. Phase 2 — the main exploration (09-19 .. 09-29)

### 4.1 The architecture settles: tape + layers

The agent that carried us to the end is a **frozen action tape**: 720 recorded
turns replayed verbatim, wrapped in roughly sixty hand-written **policy
layers** that intercept and override specific decisions — market orders,
which route to follow, how to allocate hired hands, which animal to buy, when
to sell what.

Why a tape rather than a learned policy?  Because a learned policy was tried
and failed (see 4.4).  The tape encodes three weeks of someone else's
well-tuned micro-decisions; the layers let us change *specific* judgements
without disturbing the rest.  This is a very odd architecture, and its
properties drove everything that followed:

* you can only change **parameters and switches**, not add behaviours, because
  the tape's schedule is saturated;
* a layer either pays for itself or is a tax, and the only way to know is
  paired testing.

### 4.2 Mapping the field

A large share of the middle phase is systematic mapping rather than
optimisation:

* **band-by-band win/loss tables** — our win rate against opponents bucketed
  by their rating band, so we knew exactly where we were losing;
* **census work** — the terminal economy of the opponents we lost to;
* **counter-design** for specific opponent families (anti-milk, anti-wool,
  cow-first, sheep-heavy), and the repeated discovery that a counter which
  helps against its target usually costs more elsewhere.

### 4.3 The fidelity problem becomes explicit

Panels of recorded opponents are cheap and fast, and they lie.  If your agent
starves the recorded opponent's economy — buys the wheat it needed, floods its
sell book — the tape keeps playing its recorded moves into a game that no
longer exists, and you "win" a game the opponent was never allowed to contest.

The fix that stuck was **fidelity filtering**: only count a game if the frozen
opponent finished with ≥95% of the bank it actually earned in that game.
It is crude, but it separated real wins from starvation artefacts and stayed in
the protocol for the rest of the project.

### 4.4 The things that did not work

Recorded honestly, because most of the effort went here:

| approach | outcome |
|---|---|
| **imitation learning** of the tape | could reproduce the hand-tuned router perfectly (100% on holdout) — but reproduces, it does not improve |
| **PPO / RL** after imitation | 40 rounds, zero generalisation on holdout |
| **genetic search** over configuration | converged to hand-tuned-quality, not beyond |
| **plan generator** (D16 design) | specified, not built — needs a different base strategy |
| direct copies of high-scoring public tapes | strong on panels, weak against reactive opponents |
| counters targeting specific opponent families | each helped its target, cost more elsewhere |

The RL result is worth stating precisely, because it is the clearest evidence
that this problem is not one a small training loop solves: a *supervised*
model absorbed the existing policy exactly, and then **no gradient signal
existed to go further**, because the policy's value is in a plan 720 moves
long and the reward is one number at the end.

### 4.5 The paradox appears — and gets recorded, not explained

By 09-27 the notes contain a déjà vu that should have been a warning:

> eight `mid112` candidates, all validated on a 570-game frozen corpus:
> **+457 margin, t = +9.22**, flips 4→24 … and the live score is stuck
> around 2090, with our rank sliding from #322 to #1105.

The same pattern reappears in the final 38 hours, where it became the central
unresolved question.  In hindsight this was the most important signal of the
whole competition, and we treated it as an anomaly both times.

---

## 5. Phase 3 — the last 38 hours (09-30 .. 10-01)

Full detail in `experiment-log.md`; the shape of it:

### 5.1 Exhausting the cheap moves

Layers, constants, splices, market-flow synthesis, animal substitutions,
labour retiming, RL sandboxes, operator ports — sixty-ish distinct families,
almost all negative.  Two structural findings came out of it:

* the tape runs at **~95% labour utilisation**, and every animal costs about
  **2.2 actions/day** in upkeep.  So the agent's habit of *letting some
  animals escape* is not a bug — under a fixed labour budget it is an optimal
  cull.  We rescued 154 sheep and lost money doing it (−35k labour value
  against +77k capital).
* **adding behaviours never pays; only changing parameters does.**  Every
  operator we wrote was eaten by the opportunity cost it created.

### 5.2 The one that mattered

Sixty constants swept.  Of them: about twelve were **dead code** (changing them
produced byte-identical games), several were **already on the correct side of a
cliff**, and exactly one was a genuine untaken switch.

```
V9_FERT_FIRST_DAY   14 -> 12      +84 margin/game
```

Verified on three independent opponent pools: +84 (t=5.10), +82 (t=4.67),
+94 (t=2.47).  The mechanism looks like a timing window: 12 and 13 produce
*identical* games (delta 0.00), 14 and 16 sit one step outside it.

**It had already been tested and thrown away.**  The original sweep logged it
as "−1 win, inert" — because that sweep compared **win/loss counts**.  On the
same 131 games:

| criterion | verdict |
|---|---|
| win/loss | 76 vs 77 → *inert, slightly worse* |
| paired margin | **+82, t = 4.67** |

That is the single most useful methodological result in this archive, and it is
why the last day was spent repairing the ruler before looking through it.

### 5.3 Fixing the ruler

Two changes made the difference measurable:

**Pairing.** Replay both candidates on the same opponents, same worlds, same
seeds.  The shared luck cancels:

```
single-game margin spread   sd = 13,129
paired difference spread    sd =    201      (65x tighter)
```

**Margins, not wins.**  Win/loss quantises a continuous effect into 0 or 1 and
throws away nearly all of it.  In a sample where nothing sits near the
break-even line, a genuine +84/game improvement can flip *zero* wins — and be
declared inert.

### 5.4 The submission

Three constants, three lines:

```
V9_FERT_FIRST_DAY 14 -> 12    (+84, three pools)
_R37_PRICE_FLOOR   1 -> 2     (+29, leave-one-out)
_R37_HINGE_GAIN  8.0 -> 6.0   (+1, harmless)
```

Effect across three independent pools: **+112, +108, +113** margin per game,
t = 2.8 to 5.6.

Submitted as `cand_comb2b` at 20:32 UTC on 09-30, with the user's explicit
approval.  It opened at **2109.3** — 165 points above the candidate it derived
from.

### 5.5 Where it ended up (still moving)

Submissions closed on 09-30, but the competition keeps playing until **10-14**
so the ratings can settle, and the team score is the better of our two tracked
submissions.  The sequence we observed:

| when | `comb2b` | second submission | our rank |
|---|---|---|---|
| submit + 9h (10-01 05:00) | 2109.3 | 2043.1 | ~460 |
| 10-02 02:40 | 2098.7 | 2043.1 | 466 of 10,246 |
| 10-02 14:50 | **2058.5** | **2057.5** | 515 |
| silver cut, 10-02 14:50 | — | — | 512th = 2059.5 |

So the pair converged to essentially the same score, and sat **one point under
the cut** — on the edge of the top 5%, with two weeks still to run.

Earlier in the day the numbers looked calmer (2098.7, 46 places of buffer), and
we had concluded from the preceding 18 hours of near-zero movement that the
board was settled.  It was not: over the next 12 hours `comb2b` lost 40 points
and the second submission gained 14.  **The lesson is in the retrospective**
— "the board is quiet" is not the same as "our position is stable", and a
buffer of 29 points was never as safe as a 4-sigma calculation suggested,
because the relevant sigma is not the calm-period one.

**Target was top-200 (~2697); we finished roughly 400 points short of it.**

---

## 6. The unresolved contradiction

On the last day we ran a **direct duel**: two of our agents in the same world,
both seats, 128 worlds (256 games).  It contradicted the replay harness.

| method | verdict |
|---|---|
| frozen-replay paired harness (996 games) | `comb2b` > `comb` > `w2_120`, +238 margin, t=13.5 |
| direct duel (256 games) | **`w2_120` beats all of them**, 67–80% |
| live ladder, 10-02 02:40 | `comb2b` 2098.7 > `w2_120` 2043.1 |
| live ladder, 10-02 14:50 | `comb2b` 2058.5 ≈ `w2_120` 2057.5 |

(Note how the live column moved during the day — the two submissions converged
to a dead heat, which is itself mildly supportive of the duel's claim that
they are close in strength.)

The duel was not a fluke: 83 of 128 worlds went to the same side twice, seat
order made no difference, and the margin held after dropping outliers.

**Our reading.**  The frozen harness measures how well a candidate exploits a
**non-reactive** opponent — and the layers `comb` removes are precisely the
layers designed to play against a *reactive* one.  Freezing the opponent
therefore penalises exactly the thing the change was for.  But we could not
prove this within the window, and the duel itself is suspect for a different
reason: both agents were built to beat *others*, not each other.

If a future run resolves it, the resolution matters beyond this competition:
it decides whether recorded-opponent panels are a valid instrument for
competitive-agent work at all.

---

## 7. Everything that did not work

Collected in one place, because this is most of the effort:

**Architecture.** Learned policies (imitation saturates at the teacher;
PPO adds nothing), plan generators (specified, not built), cross-game donor
splicing (5–11 wins out of 96), fixed opening substitutions.

**Markets.** ~350 market-flow candidates — per-item mixing, dip-buying,
sell-splitting, stockpiling, order re-ordering, fixed-point local search.
All negative or inert; the model-side gain (+50–100) was two orders of
magnitude below the live noise (±10k).

**Mechanisms.** Shed overflow (real but worth 154/game, i.e. noise), animal
escapes (real, 1631/game, but rescuing them is net negative), tile-cap waste
(does not exist — our first probe was mis-specified), terminal cargo (the tape
already plays it optimally).

**Constants.** ~60 swept, one useful.

---

## 8. What we would keep

1. **Verify the instrument before using it.**  The engine parity audit on day
   one, and the pairing fix on the last day, were worth more than any single
   strategy idea.
2. **Pair, and measure margins.**  65× noise reduction, and it rescued a
   t=4.67 improvement that a win-count sweep had already discarded.
3. **Assume your opponent tape cannot react, and correct for it.**  Fidelity
   filtering; and know that the correction is incomplete.
4. **In a saturated schedule, change parameters, not behaviour.**
5. **Record the paradoxes.**  The offline/live gap appeared on 09-27 and again
   on 10-01; writing them down is why we spotted the second one quickly.

## 9. Open questions, in priority order

1. **Resolve the replay-vs-duel contradiction.**  Run the duel for a third
   candidate pool and correlate the result with each candidate's live history.
2. **Opponent modelling.**  The one capability nobody in the field has: a
   predictor of what the *other* agent will do, trained on the 8.3 GB public
   replay dump.  Framed as *strategy identification* (which recorded policy is
   this?) rather than action prediction, the output space shrinks by ~500×
   and the data stops being the bottleneck.
3. **Single-opponent study.**  Hold one recorded opponent fixed across its
   hundred-plus games: the opponent stops being a variable, and win/loss
   becomes a function of the world alone.
4. **Reverse-engineer a leader.**  We located the tooling (public replays carry
   `info.TeamNames`) but ran out of time before scanning the 8.3 GB dump.

---

## 10. Where everything lives

| | |
|---|---|
| day-by-day raw notes (521 files, 09-12 → 10-02) | `history/` |
| the final 38 hours in detail | `experiment-log.md` |
| mistakes, and how each was caught | `retrospective.md` |
| how to re-run the evaluation | `reproducing.md` |
| the three candidates | `../candidates/` |
| the harness | `../tools/` |
| exact engine constants | `../reference/engine-rules.md` |
