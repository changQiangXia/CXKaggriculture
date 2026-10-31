# Humble Solution

**TL;DR**
- Our final agent is a public agent (tetsutani's *Demand-Preserving Turn Sale Timing* notebook, Sept 27 version, Apache-2.0) plus a few re-tuned constants and a stack of small layers that mostly change the **order** of market orders, not the production plan. Near 2,300 about half of our opponents ran forks of that same agent family, so many games were near-identical "mirror matches" decided by a few hundred dollars. That is where our edge came from.
- Our biggest gain came from **fixing an evaluation mistake**. For three weeks we tested our own agents only against opponents that never react. When we finally played them against the public agents they lost 0–20; switching to a public base took us from ≈1,160 to ≈2,290.
- The part we are proudest of is the **local evaluation harness**: paired comparisons on the official engine, the seed as the unit of analysis, a rival panel weighted by a census of our real opponents, and pre-registered confirmations on fresh seeds.
- The most interesting mechanism: both players' orders execute index by index, interleaved. That turns "buy X extra, resell X at the last index" into a **near-free option**: worth exactly \$0 if nobody trades in between, profitable when a mirror opponent buys in between. Late on, some opponents ran the same trade one index earlier than us; we shipped an in-game detector that switches our option off when it sees that.
- Final: 755th of 10,148 teams, bronze medal (top 7.4%; final rating ≈1,961). Best single-submission rating during the submission window: ≈2,385 (Sept 28). Post-deadline ratings are not directly comparable (§8).

---

## 1. Context: at ~2,300 the ladder was a mirror league

Kaggriculture is a 2-player, 720-step farming game (30 days × 24 steps); the richer farm wins. By late September a large share of the ladder around 2,300 ran forks of one public agent family (tetsutani's notebook and its relatives). We call it **the base family** below. These agents follow precomputed **routes**: production-and-trading scripts chosen by which shops the seed unlocks. So two forks in the same world often issue the same orders on the same steps.

When we classified our real opponents from replays (see §3), **≈50–52% were from the base family**. Consequences:
- Many games are **mirrors**: same route, same world, nearly identical farms. In one sample of 40 real games, **29 were decided by less than \$1,000**, on final farms typically worth \$80k–150k.
- What decides a mirror is **who sells first, and at which price**, not the production plan.
- Win/loss is close to a threshold function of the money margin, so a layer that adds a few hundred dollars per game flips exactly the close ones.

## 2. The mistake that cost us three weeks

Until Sept 23 we submitted our own agents: first a hand-written planner, then **tapes** (fixed action sequences mined from top players' public replays, plus small cash guards and shop-based branching). We evaluated them against a panel of other tapes. A tape replays blindly; it never reacts to you.

- The same tape-based agent won **71.5% locally and ≈40% on the ladder**.
- Local improvements of +2 to +6 pp never showed up in the rating.
- When we finally played our two active agents against public agents in full games where both sides react, they lost **0–20 to each of 7 public agents**, by \$12k–16k per game.

Our harness had only ever compared *our own variants against each other*; it never measured absolute level against the population that actually plays. So we switched: the winner of that local tournament, submitted unchanged (arsgorynich's *Herd-Safe v3*, Apache-2.0), climbed to **≈2,290** within a day, versus ≈1,160 for our agents at the time (our best ever had been ≈1,325). After that we kept tracking the public frontier; on Sept 27 tetsutani's agent overtook it and became our final base. Everything after that is tuning and layers on top of it.

## 3. How we evaluated (the harness)

Our tournament script plays full games on the **official engine** (`kaggle_environments` 1.32.7), loading each agent file exactly as Kaggle does (last callable in the module).

| Concept | Meaning |
|---|---|
| **Seed** | Fixes the game's randomness: which town shops unlock (one every 3 days, up to 8, drawn with replacement), which decides which products are valuable (e.g. a yarn shop makes wool valuable), and where weeds spawn. Same seed + same two agents + fixed `PYTHONHASHSEED` → the exact same game. |
| **Seat** | Playing as player 0 or 1. We always play both. |
| **Cell** | (rival, seed, seat). Candidate and reference play **the same cells**, so each cell gives a paired difference with the world held constant. |

Notation below: **pp** = percentage points of win rate; brackets = 95% CI computed over seeds; a **changed cell** = a cell whose win/loss differs between candidate and reference.

Design choices that mattered:

1. **Win/loss is the primary metric**, because the rating only sees W/L/T. Money margin is a secondary, far more sensitive signal for mirror games.
2. **The seed is the unit of analysis, not the cell.** Both seats of a seed are often literally the same game seen from the other side, so counting every cell as an independent game would be fake precision.
3. **A panel weighted by a census of the real population.** We downloaded our ladder replays, fed each public agent the exact observations our real opponent saw, and counted identical actions to classify every opponent into a family. Weighted deltas estimate the effect on the population we actually face. Hard rule: reject a change if any single family gets clearly worse (95% CI entirely below −10 pp).
4. **Pre-registration and confirmation on fresh seeds.** Variants, rivals, seeds, metric and pass threshold were written down before each confirmation run (sometimes after a small screening pilot). Why: in one pilot of 111 candidates, the winner scored **87.5% and fell to 31%** against a fresh set of opponents and seeds (winner's curse). Not every shipped layer cleared its adoption threshold: several shipped under a weaker pre-declared "promising" rule (point estimate ≥ 0, no family harmed, margin CI > 0), so we also measured each combined agent directly against the previous one (§6).
5. **Controls that the instrument isn't lying:**
   - **Action hashes** per seat: if a layer must not change behavior in some situation, we check it byte for byte.
   - **Determinism:** one whole confirmation was invalidated because a `sorted(set(...))` without a tie-break depended on Python's hash seed. Since then everything runs with `PYTHONHASHSEED=0`. (On Kaggle each agent process gets its own hash seed, which made some "identical" agents diverge.)
   - **Fidelity:** real Kaggle replays reproduced exactly in the local engine (719 actions / 720 states).
   - **Does the change even fire?** In a 24-variant parameter sweep (12 constants, two values each), **18 variants were exactly inert**: those constants are read at import time, so our end-of-module override came too late. We now check in order: does the code path run, does it change the emitted action, does the engine execute it, does it have the intended market effect, and only then do we measure the result.

## 4. The layers

Each step a player submits a list of up to 10 orders (indices 0–9): market buys and sells plus fixed-price orders such as hiring or buying seeds. The engine executes **index 0 of both players, then index 1, and so on**; within an index the two players' units alternate one at a time. So whatever you put at index 9 executes after everything your opponent put at indices 0–8. Every unit sold lowers the price of the next one and every unit bought raises it; curves are steep for milk, wool and strawberries (≈\$2 per unit) and almost flat for wheat and fertilizer (≈\$0.2 per unit). A buy is quoted at inventory − 1, so buying X and reselling X in the same step nets exactly \$0 if nobody trades in between.

None of this lockstep logic is new: the base already uses it to order its sales against a mirror (credited in the code to Seyit Kaan Gunes and shiiin9). Our additions, on top of the base:

**Re-tuned constants** (each confirmed separately): a forecast top-k from 1 to 3 (18–4–10 head-to-head against the unmodified base); a sales look-ahead and a sell margin (together +8.4 pp [+4.3; +12.5]); and a wheat→carrot conversion margin of −22 (+5.3 pp [+1.2; +9.5]), the same value haodou092 had published in *Harvest Ledger*. That last one is a production change; everything else below changes **order, not production**:

| Layer | What it does | Evidence |
|---|---|---|
| **Front-run defense** | In ≈11% of games the route makes one big wheat purchase at a known step. Two opponents bought that wheat one step ahead of us and sold it at index 9, right after our purchase had pushed the price up (−\$8k to −\$11k per game for us). We now buy one step earlier; if the opponent follows the same route, we also buy extra and resell it at index 9. A pre-sell variant sells one step early the wheat the route will sell next step. | +37.2 pp [+26.3; +48.2] in those games (51/51 changed cells in our favor); pre-sell +\$1,934 per game |
| **Mirror-aware sell order** | One extra call of the base's existing best-response sales reorder (shiiin9's "counter D") before our front-run layer | W/L +0.3 pp (CI includes 0); margin +\$80 [+51; +110] vs the base; census-weighted replication +7.3 pp [+1.4; +13.2] † |
| **Shepherd delivers first** | The base's sheep worker picked up fertilizer before delivering wool, so its wool reached the market 3 steps later than some other families'. Wool's price falls fast as units are sold, so it now delivers first. | +2.2 pp [−1.5; +5.8]; on seeds with a yarn shop +2.5 pp [−0.4; +5.5]; 13/13 changed cells in favor; 0/1,120 cells lose margin †. On the ladder: 6–0 in games where it built a 6-sheep flock |
| **Buys before fixed-price orders** | Wheat/fertilizer buys move ahead of hiring, seeds, animals and land (still behind our sales). Small on its own, but it puts our buy early in the list, which the option below relies on. | +\$13 to +\$19 margin vs every family (CI > 0); 5/5 changed cells in favor † |
| **Resale option** (buy side + sell-side twin) | Add X (≤ 90) to our routine wheat/fertilizer buy and resell X at index 9. If the opponent buys the same product in between, it pays the higher price our extra buy created, and its purchase pushes the price up further before our resale, so we sell X for more than we paid. If nobody trades in between, the round trip nets exactly \$0. The sell-side twin sells X extra from stock and buys it back at index 9. | +3.44 pp [+0.95; +5.92]; margin +\$396 per game vs the base family; 0/672 cells with negative margin |

† Shipped under the weaker "promising" rule (§3): the win-rate CI included 0, but no family was harmed and the margin CI was above 0.

The versions we refer to below:

| Name | What it is |
|---|---|
| **Base** | tetsutani's public agent (Sept 27 version) |
| **A** | Base + re-tuned constants + front-run defense + mirror-aware sell order |
| **B** | A + shepherd-first + buys before fixed-price orders + resale option (both sides) |
| **B+guard** | B + the guard from §5 |

## 5. Opponents who raced the option, and the guard

Among the last 33 ladder opponents of B, 8 ran the same trade **one index earlier**: buy X extra at index 0 and resell it at indices 1–8, before our index 9. They won that race and took **\$383 to \$5,914 per game** from us; we lost all 8 games. We cannot tell whether they learned it from our replays or found it independently. We found no public notebook containing it (we checked the 13 notebooks updated on Sept 28–29), so it was presumably private code.

**The guard.** After each step in which our resale option was active, we re-simulate that market step exactly, assuming a "benign" rival: at most one order per product, at any index, with quantities that reproduce the inventory we observed. That gives the least money we could have ended the step with against any benign rival. If we actually ended with less (by more than \$150 once, or by more than \$20 on buy-side steps / \$60 on sell-side steps twice), the rival must have traded the same product in both directions around our orders, so we switch the option off for the rest of the game. When it does not fire, its actions are identical to B's.

| Test | Result |
|---|---|
| Pre-registered confirmation vs 4 synthetic, non-reactive copiers (two closely reproduce real opponents' patterns) | **+44.9 pp [+38.2; +51.2]**; the guard fired in 768/768 cells |
| No false alarms: 7-agent panel, and a wider check vs 30 public agents + self-play | 0/672 and 0/480 cells with any action difference |
| 13 copier variants in total | B+guard beat B against every one |
| Games not used to build the guard: 191 real ladder games of A, re-run with B+guard against each opponent's recorded (non-reactive) actions | +\$142 per game; 1 loss → win, 0 wins → losses; 1 false alarm (cost \$73) |

We also tried a **counter-attack**: after detection, buy at index 0 and resell at index 1, ahead of the other side's resale. Three versions were refuted in two rounds by an adversarial review step (an AI agent tasked with breaking each design): first with a "staircase" pattern taken from a real opponent, then with a fixed-chunk pattern. Each time it lost to the simple guard (in one case 10 wins turned into losses). It is an arms race over indices; the bounded-downside option (switch off) was the robust one.

## 6. Choosing the final pair, and did the harness transfer?

Kaggle scores only your two most recent submissions. On the last day A and B were on the ladder, and B+guard had been confirmed locally.

**Did the harness transfer?** It predicted B > A by **+7.55 pp [+3.80; +11.31]** (29 of 384 cells changed outcome, all 29 in B's favor). On the ladder, over the same time window, B went **23–15** and A **8–26**. A logistic (Elo-style) model using each opponent's current rating put the gap at roughly **+92 to +135 rating points**.

The day before the deadline, before seeing new data, we wrote a decision rule: replace A only if B led it by ≥ 40 rating points (or clearly out-won it in games played after the rule was written), with a recent win rate of at least 45% and no excess of errored games, and with a fallback for a failed validation that could never push B out. The rule was met (+97 points). We then submitted B+guard, which had not played a single ladder game, and kept B. We accepted that because, unless the guard fires, its actions are identical to B's (0 differences in 1,152 local cells against up to 30 public agents). Swapping in the guarded file was an amendment made after its local confirmation; the rule itself was fixed before the new data.

## 7. What did not work

| Idea | Result |
|---|---|
| Selling leftover wool/milk/strawberries early (changes quantities sold) | −2.8 pp [−6.4; +0.8] despite +\$107 mean margin: extra units sold into close games |
| A tomato-instead-of-cow opening | −80 pp |
| Replacing our base with a full public package from another lineage (in our panel, at that time) | −64 pp |
| Letting the herd model count demand from shops not yet unlocked (it swapped geese for cows) | −84 pp |
| Buying first at index 0 (pushes our sales behind the mirror's) | −\$400 to −\$1,000 per game |

The base was already strong on production. Apart from one small production retune (the −22 margin above), the edge we found was in sale timing and market order.

## 8. What we could not solve

- **A private family with a cow opening** (≈6% of opponents near the end): A and B, our two active agents at the time, both went 1–7 against it. It bought its second land plot ≈70 steps earlier than us and scaled production differently. That is a production-plan gap, and our panel could not contain it because the code was not public.
- **The post-deadline drop.** During the final evaluation (until Oct 14) our two final agents slid from ≈2,200 to ≈1,924–1,961. After the deadline every team's two final submissions keep playing each other and ratings across the ladder re-settle; we cannot tell how much of our drop is a stronger pool and how much a shifted scale. Either way, our harness measured improvements relative to what we could see, not the distance to what we could not.

## 9. Lessons

1. Measure absolute level against the best available alternative before tuning.
2. Your offline metric is a proxy: calibrate it against production, and refresh it when it saturates (by the end we were winning ≈95% of the public panel).
3. Most "improvements" are noise: pair your comparisons, pick the right unit of analysis, pre-register, confirm on fresh data.
4. Verify that a change actually fires before measuring its effect.
5. The best hypotheses came from forensic analysis of lost games, not brainstorming.
6. Success changes the environment: once an edge works, someone else runs it too. Prefer changes with bounded downside.

## Credits

Our final agent is the code published in tetsutani's *Demand-Preserving Turn Sale Timing* notebook (Sept 27 version, Apache-2.0) with our changes on top. That code carries attribution to thomastschinkel, yhay81, destbreso, aurax7, prvsiyan, Dmitrii Gluzdov, Ahmed Berat Ozer, Seyit Kaan Gunes (lockstep sale ordering against clones), shiiin9 (the best-response reorder against a copy of ourselves, which our sell-order layer re-applies), lucifer19, Moon and the kaggle-environments contributors. Along the way we also submitted, unmodified, arsgorynich's *Herd-Safe v3* (the agent that first took us to ≈2,290), thomastschinkel's *Metav4 v13* and Abhinav0370's *cha22* agent. Our wheat→carrot margin of −22 is the value haodou092 published in *Harvest Ledger*. All license notices are retained in our submission. Thanks to everyone who published agents and notebooks: this competition was a great example of open iteration.

github: https://github.com/rospeltof/kaggriculture