

<!-- NOTEBOOK CELL 0 -->
# The $250 Bug That Beat Every V45 Fork

**TL;DR**: One parameter change. 179 wins, 1 loss, 0 ties across a 10-agent tournament.
Fork this, submit, and read on to learn how 1,800+ games of testing found what
everyone else missed.

![wheat](https://i.imgflip.com/4/2wifmk.jpg)
*"I used to buy 70 wheat. Then I took a spreadsheet to the knee."*

---

**What this notebook does:**
1. Embeds the complete agent (no external datasets, no GPU)
2. Writes `main.py` and packages `submission.tar.gz`
3. Fork -> Submit -> Done

**Tournament Results (10 agents, 20 games per matchup, 900 total games):**

| Rank | Agent | W-L-T | Elo Rate |
|------|-------|-------|----------|
| **#1** | **Pipe-7 (this notebook)** | **179-1-0** | **99.4%** |
| #2 | V45 Clone (degnonguidi) | 141-20-19 | 78.3% |
| #3 | V45 (Ahmed) | 138-23-19 | 76.7% |
| #4 | V44 (Ahmed) | 120-60-0 | 66.7% |
| #5 | Pipe-5 (our previous) | 92-87-1 | 51.1% |

*Single loss: 1 game to V44 out of 180. Everything else was 20-0.*

<!-- NOTEBOOK CELL 1 -->
---

## How We Found It: The Pipeline

We didn't guess. We ran a 6-step automated pipeline (the "Autoloop") that:

1. **Tournament Input** - Ranked all known agents from previous tournaments
2. **Cluster Engine** - Grouped 200+ LB teams by strategy fingerprint (Union-Find, 90% similarity)
3. **Twin Graph** - Found 224 superior twins with higher Elo
4. **Tape Diff Tracer** - Compared our agent's action tape against every target, byte by byte
5. **Targeted Replay** - Pre-screened candidates against anti-targets
6. **Colosseum** - Full 200-game statistical validation. The colosseum DECIDES, not us.

### What the pipeline told us:

> *"pipe-6 = v45. Zero tape differences. Zero settings differences. You ARE v45."*

So we couldn't copy anyone. Pipe-7 had to be **original**.

![fine](https://i.imgflip.com/4/1qhzb6.jpg)
*The pipeline after scanning 63 agents and finding nothing to copy*

<!-- NOTEBOOK CELL 2 -->
---

## What We Tried (And What Blew Up)

We tested 6 different modifications. The colosseum was merciless:

| Change | vs V45 (50 games) | Verdict |
|--------|-------------------|---------|
| Enable `clamp_sells` | 2W-48L (4%) | Broke the sell-lead timing chain |
| Enable `dead_stock` | 19W-27L (42%) | Sold inventory the wrapper layers needed |
| R37 horizon 4->5 | 2W-0L-48T (52%) | Block boundaries already cap the window |
| Expand terminal planner | 2W-3L-45T (49%) | Router converges to route 2 at step 648 anyway |
| Unlock V219/V233 terminal | 1W-13L-36T (38%) | Planner can't model committed workers |
| Always use R108 routing | 29W-31L-140T (49.5%) | New routes aren't better than old ones |

**Key lesson**: V45 has 30 reactive wrapper layers calibrated together like a Swiss watch.
Change one gear and the whole thing breaks.

![domino](https://i.imgflip.com/4/22o40i.jpg)
*Me enabling `clamp_sells=True` and watching 96% of games turn into losses*

<!-- NOTEBOOK CELL 3 -->
---

## The Breakthrough: Market Microstructure

After all the complex reactive layer experiments failed, we went back to basics.

The V45 opening does a **wheat round-trip** at step 0: buy wheat, sell wheat, pocket the spread.
Everyone uses quantity 70 because that's what V45 ships with.

But here's the thing about market microstructure:

> **Each additional unit you buy pushes the price UP against you.**
> **Each additional unit you sell pushes the price DOWN against you.**

At quantity 70, you're moving the market so hard against yourself that the spread
*costs* you money instead of making it. The market impact exceeds the profit.

We tested every quantity from 0 to 80:

| Quantity | vs Q=70 (50 games) | Notes |
|----------|-------------------|-------|
| 5 | **50W-0L** (100%) | Sweet spot |
| 40 | 50W-0L (100%) | Still dominates |
| 60 | 50W-0L (100%) | Still dominates |
| 65 | 50W-0L (100%) | Still dominates |
| 70 | — | This is V45 |
| 75 | 2W-48L (4%) | Now YOU'RE overpaying |
| 80 | 0W-50L (0%) | Complete collapse |

The cliff at 70 is steep: below it you win, above it you lose. V45 sits right on the edge.

**One parameter. ~$250 per game. 99.4% tournament win rate.**

![galaxy-brain](https://i.imgflip.com/4/2fzidi.jpg)
*"What if... we just buy less wheat?"*

<!-- NOTEBOOK CELL 4 -->
---

## Validation: 1,800 Games Don't Lie

We validated pipe-7 across 9 opponents at 200 games each:

| Opponent | W-L | Rate |
|----------|-----|------|
| V45 (the mirror) | 197-3 | 98.5% |
| V44 | 188-12 | 94.0% |
| V43 | 200-0 | 100% |
| V42 | 196-4 | 98.0% |
| thomastschinkel | 200-0 | 100% |
| alperen v62 | 198-2 | 99.0% |
| degnonguidi | 192-8 | 96.0% |
| renjistarfall | 190-10 | 95.0% |
| more-yield | 193-7 | 96.5% |
| **Total** | **1,754-46** | **97.4%** |

Self-play (pipe-7 vs pipe-7): 1W-1L-18T. Stable equilibrium.
The improvement is structural, not noise.

<!-- NOTEBOOK CELL 5 -->
---

## The Journey: 7 Generations

| Gen | Key Change | Gauntlet Rate | Method |
|-----|-----------|---------------|--------|
| Pipe-1 | Base agent | 81.8% | Pipeline discovery |
| Pipe-2 | +sell timing | 83.0% | Pipeline discovery |
| Pipe-3 | +opening (REGRESSED) | 78.0% | Bypassed pipeline |
| Pipe-4 | +reactive layers | 85.0% | Pipeline recovery |
| Pipe-5 | +terminal optimization | 89.0% | Pipeline discovery |
| Pipe-6 | =V45 (identical) | 89.0% | Tape diff confirmed |
| **Pipe-7** | **Market microstructure** | **97.4%** | **Pipeline + colosseum** |

Pipe-3 is the cautionary tale: we bypassed the pipeline and regressed.
Every successful generation came FROM the pipeline.

<!-- NOTEBOOK CELL 6 -->
---

## Build the Agent

No datasets, no internet, no GPU. The complete agent is embedded below.

<!-- NOTEBOOK CELL 10 -->
## Build the Submission Archive

<!-- NOTEBOOK CELL 12 -->
---

# Attribution and License

This agent is a derivative work. Credit where credit is due:

### Base agent: Ahmed Berat Ozer
- V45: First Turn Wheat Round Trip
- V40-V44 progression
- Apache-2.0

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
*7 generations, 4,600+ games, 1 parameter change that mattered. If you found this useful, an upvote helps!*

![upvote](https://i.imgflip.com/4/65939r.jpg)
*"I survived 30 reactive wrapper layers and all I got was this wheat optimization"*