
CELL 0
# Why Every V45 Fork Still Loses $1 Per Game

**TL;DR**: Two synergistic opening changes. 173 wins, 7 losses across a 10-agent tournament. Beats Pipe-7 head-to-head 191-9 over 200 games.

Fork this, submit, and read how a 6-step pipeline found what 224 teams in our cluster missed.

---

**What this notebook does:**
1. Embeds the complete agent (no external datasets, no GPU)
2. Writes `main.py` and packages `submission.tar.gz`
3. Fork → Submit → Done

**Full Gauntlet (200 games × 9 opponents = 1,800 games):**

| Opponent | W-L | Rate |
|----------|-----|------|
| Pipe-7 (previous best) | 191-9 | 95.5% |
| V44 | 189-11 | 94.5% |
| V43 | 195-5 | 97.5% |
| V40 | 198-2 | 99.0% |
| thomastschinkel | 200-0 | 100% |
| alperen v62 | 198-2 | 99.0% |
| degnonguidi | 194-6 | 97.0% |
| renjistarfall | 192-8 | 96.0% |
| more-yield | 196-4 | 98.0% |
| **Total** | **1,753-47** | **97.4%** |

CELL 1
---

## How We Found It: The Pipeline Decides

Same 6-step Autoloop that found pipe-7. The pipeline is the coach; we're just the hands.

1. **Tournament Input** — Ranked all agents from the last colosseum
2. **Cluster Engine** — 794 teams fingerprinted into 60 strategy clusters
3. **Twin Graph** — Found **224 superior twins** above our Elo (top: "Catalyst" at Elo 2969, 98.6% similarity to us)
4. **Tape Diff Tracer** — Diffed pipe-7's action tape against every available target
5. **Targeted Replay** — Pre-screen against anti-targets
6. **Colosseum** — Full statistical validation

### What the tape diff found:

| Target Agent | Diffs | Where |
|---|---|---|
| V45 | 0 | Expected — pipe-7 ≈ V45 |
| Alperen (turn-one-market-advantage) | 60 | Steps 0-1 only: they skip the round-trip |
| Nusrati (2650-score) | 13 | Step 0 only: different wheat quantities |
| degnonguidi | 0 | V45 clone |

All the diffs are in the **opening**. 224 teams above us, and the only structural difference is how they handle step 0 and step 1.

![this-is-fine](https://i.kym-cdn.com/entries/icons/facebook/000/018/012/this_is_fine.jpg)

*Us at Elo 2690, realizing 224 teams above us are running nearly identical code*

CELL 2
---

## The Experiment: Both Changes Required (Or Else)

Alperen's agent does `[BUY 5]` at step 0 (no sell) and `[HIRE×5, COW 2, SHEEP 2]` at step 1 (no wheat trades). Our pipe-7 does `[BUY 5, SELL 5]` at step 0 and `[SELL 13, BUY 5, HIRE×5, COW 2, SHEEP 2]` at step 1.

We tested every combination:

| Variant | Step 0 | Step 1 | vs Pipe-7 (50 games) |
|---------|--------|--------|----------------------|
| **A (winner)** | **BUY 5 only** | **HIRE+COW+SHEEP** | **47W-3L (94%)** |
| B (step 0 only) | BUY 5 only | Original (SELL 13, BUY 5, ...) | 2W-48L **(4%)** |
| C (step 1 only) | BUY 5, SELL 5 | HIRE+COW+SHEEP | 0W-50L **(0%)** |

**Neither change works alone.** Both together = 94%. Either alone = catastrophic failure.

We also tested quantity:

| Step 0 Quantity | vs Pipe-7 |
|-----------------|-----------|
| BUY 3 | 0W-50L (0%) |
| **BUY 5** | **47W-3L (94%)** |
| BUY 10 | 4W-46L (8%) |
| +GOOSE at step 1 | 0W-50L (0%) |

The 30 wrapper layers are a Swiss watch. BUY 4 and BUY 6 are untested but BUY 3 and BUY 10 are both catastrophic. Don't touch what works.

![domino](https://i.imgflip.com/2oo7h0.jpg)

*Small domino: "remove one SELL order." Big domino: "94% win rate against all V45 forks"*

CELL 3
---

## Why It Works: Market Microstructure, Again

Pipe-7 found that buying 70 wheat loses money due to market impact. Pipe-8 takes this further: **even a round-trip of 5 costs you**.

The sell at step 0 pushes the wheat price down by a tiny amount. The buy-back at step 1 pushes it up. These fractions compound into a **$1 per game** disadvantage that the opponent exploits.

The evidence is in the colosseum data: in 182 of 200 games against pipe-7, pipe-8 wins by **exactly $1**. The agents play identically from step 2 onwards — same routes, same reactive layers, same terminal planner. That $1 comes from the opening spread savings.

The ~5% of games where pipe-7 wins are seeds where the wheat inventory from the round-trip provides a specific advantage that outweighs the $1 cost.

![galaxy-brain](https://i.imgflip.com/38e4q5.jpg)

*Pipe-7: "Buy less wheat." Pipe-8: "Don't sell wheat you don't need to sell."*

CELL 4
---

## The Journey: 8 Generations

| Gen | Key Change | Gauntlet Rate | Method |
|-----|-----------|---------------|--------|
| Pipe-1 | Base agent | 81.8% | Pipeline discovery |
| Pipe-2 | +sell timing | 83.0% | Pipeline discovery |
| Pipe-3 | +opening (REGRESSED) | 78.0% | Bypassed pipeline |
| Pipe-4 | +reactive layers | 85.0% | Pipeline recovery |
| Pipe-5 | +terminal optimization | 89.0% | Pipeline discovery |
| Pipe-6 | =V45 (identical) | 89.0% | Tape diff confirmed |
| Pipe-7 | Wheat quantity 70→5 | 97.4% | Pipeline + colosseum |
| **Pipe-8** | **Eliminate round-trip** | **97.4%** | **Pipeline + colosseum** |

The lesson keeps repeating: simple parameter changes beat complex reactive modifications. The pipeline finds them, the colosseum validates them.

Pipe-3 is still the cautionary tale — the one time we bypassed the pipeline, we regressed.

CELL 5
---

## Build the Agent

No datasets, no internet, no GPU. The complete agent is embedded below.

CELL 9
## Build the Submission Archive

CELL 11
---

# Attribution and License

This agent is a derivative work. Credit where credit is due:

### Base agent: Ahmed Berat Ozer
- V45: First Turn Wheat Round Trip
- V40-V44 progression
- Apache-2.0

### Opening insight:
- **alperen5252525**: Turn One Market Advantage — the tape diff target that showed the clean opening pattern

### Key contributions incorporated:
- **thomastschinkel**: Public State Router chassis
- **yhay81**: Shop router action tapes (shop-router-0908, 0909, 0911, 0913)
- **prvsiyan**: V221B/V224C production/timing lineage
- **aurax7**: Reactive V4/V5 reservation activation, day-end storage guard
- **Dmitrii Gluzdov**: Physical terminal rescue, Two Coins simulation planner
- **tetsutani**: Weed repair, room guard, clamp sells, dead stock layers
- **destbreso, lucifer19**: Additional capabilities
- **Rayk Kretzschmar**: Opening assignment from Rank Your Agent
- **degnonguidi**: Cloning agent packaging reference
- **leoprovorov**: Two Coins Mirror Counter probe

All upstream Apache-2.0 notices are retained in the agent source.

---

*8 generations, 6,400+ games tested, and the winning move was to stop selling wheat we didn't need to sell.*

*If you found this useful, an upvote helps!*

![take-my-money](https://i.imgflip.com/ipd6l.jpg)

*"I tested 6 variants, 3 quantities, and 1 goose to get here"*