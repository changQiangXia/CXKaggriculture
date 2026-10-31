# Kaggriculture: exact-search distillation and VinePPO on top of Pipe-16 (~1,140 / 10,148)

*Final rank pending the post-deadline Bradley–Terry fit. Code, weights and a rebuild notebook are released below.*

## TL;DR

- I did not write a new farming strategy. I put a small **reinforcement-learning layer on top of the public Pipe-16 agent**
  that makes four macro decisions per game (days 0, 8, 15 and 23: which of 8 strategy options to run for the next stage).
- **Plain PPO/GRPO failed, and the reason is measurable**: a stage decision moves the final margin by about **$42** (median),
  while seed-to-seed noise is about **$665**. With a signal-to-noise ratio of 0.06, you need roughly 1,000 games per
  decision to learn its sign from sampled returns.
- What worked was **removing the noise instead of averaging it**: fork the exact simulator at every decision, play each
  of the 8 options to the end against the live opponent, and train on those exact counterfactual outcomes
  (search distillation first, then VinePPO).
- The final agent (v9b) won 14 / lost 7 paired games against my previous best, with all of the gain coming from close
  mirror matches against Pipe-16 copies. Live, it settled about **100 rating points above** that previous best.
- The most useful finding may be a negative one: **most "obvious" improvements had no headroom on this base**, and
  copying top-10 strategies into it made things worse in every one of ~500 paired games.

## 1. Setup

**Simulator.** I used debmalyaroy's Rust re-implementation of the engine, byte-identical to the official one. Two tricks
made it the backbone of everything:

- **Exact branching.** `os.fork()` plus loading the engine state gives a perfect copy of a running game, including both
  agents' memory. Any decision can be replayed with every alternative, against the same opponent, on the same seed.
- **Replay worlds.** Taking an opponent's recorded actions from a ladder replay and replaying them on the recorded seed
  reproduced **66 / 66** of my ladder losses exactly. That gave me a test set made of the real ladder, not just my own
  panel of agents.

**Base agent.** The public Pipe-16 / best_latest_harvest lineage beat every agent in my panel in 56 / 56 local games,
so
everything below is a layer on top of it. Credits are at the end; license notices are kept in the released source.

**Evaluation.** Every comparison is **paired**: both agents play the same seed and seat against the same opponent, and I
count games where one does better than the other (exact sign test). Plain win rates were far too noisy to rank variants.

## 2. What I tried, in order

| Step | Idea | Result |
|---|---|---|
| Lever screens | Herd type, carrot ratio, hires, sell timing, fertilizer routing, wheat carry trade, etc. | Almost no lever had headroom on the base; most constant changes lost |
| Constant search | Evolution strategies over 76 numeric constants of the base | Best combination +6 / −3 of 60 paired games: noise |
| GRPO / PPO stage policy | Learn the 8-option stage choice from game outcomes | Stalled. Diagnosed as the SNR problem below |
| **Exact search teacher** | Fork at each stage, play all 8 options to the end, commit the best | Ceiling: score **0.714 → 0.881** over 210 games (~6,700 full-game rollouts) |
| Distillation (v5) | Train the stage head to imitate the search | Held-out gain only **+0.009 per decision**; blew up against an unseen opponent style |
| v5-safe | v5 with the risky wheat-carry options masked | **8 better / 2 worse** of 105 paired games vs v4 |
| **VinePPO (v8/v9)** | On-policy PPO where every decision's advantage comes from exact forked rollouts, not sampled returns | v9b: **14 better / 7 worse** of 150 vs v5-safe; +0.2 win rate against Pipe-16 copies |

### Why PPO stalled: signal vs noise

Across 6,760 ladder games and every exact search decision, I measured:

- a stage decision changes the final margin by a median of **$42**;
- the same agent's margin varies by about **$665** across seeds;
- only **5.6%** of stage decisions have *any* option that flips the game result;
- whether a flip exists **cannot be predicted** from the 136 policy features (94.6% accuracy vs a 94.2% base rate).

Sampled-return PPO was trying to read a $42 signal through $665 of noise with a handful of games per decision. Forking
fixes that: comparing all options **in the same game state** cancels the seed noise exactly. That's why search plus
VinePPO worked where GRPO didn't. The last point is also the ceiling for this whole approach: a stage policy can only
deviate well if it can tell when deviating helps, and the features couldn't.

### The carry-trade trap

Most of the RL gain came from the wheat **carry** options (buy wheat, sell it later). They win close mirror matches
against Pipe-16 copies, but against one older public agent the same options **collapsed** (15/15 wins → 10/15).
I caught it only because the test panel included opponents the policy never trained against. Lesson: **test against
opponents your training never saw**, and gate on "no collapse against anyone", not on net wins alone.

### Copying the top 10 didn't transfer

Comparing top-10 replays with my own ladder games showed clear differences. The top 10:

- buy **3× the cows and 6× the geese** early;
- sell tomatoes (I sold none);
- make their own fertilizer instead of buying it;
- leave farmhands idle about 180 fewer turns per game.

But injecting those moves into Pipe-16 **improved 0 of ~500 paired games**. Late purchases couldn't be housed, and
early ones broke the cash plan the base depends on. Top-10 behaviour comes from a planner designed around it, not
from a list of moves.

## 3. Results

- **Local:** v9b vs v5-safe: 14 better / 7 worse of 150 paired games (p ≈ 0.19). The gains were against the Pipe-16
  family (0.60 → 0.80), the cost was the known carry collapse against one older agent. Replay worlds: kept 37 / 37
  of the ladder wins.
- **Ladder:** v9b settled about 100 rating points above v5-safe. Final submissions: v9b plus one v5-safe as a backup.
- **Ladder structure:** 66% of my ladder games were decided by under $500. Near the bronze line this competition is
  mostly a **Pipe-16 mirror match**, and the RL layer's job was to win those close mirrors.

## 4. What I'd do differently

1. **Analyse games across strategies first, then evolve the strategy.** I measured the top-10 differences late, and
   by then my only option was patching someone else's plan. Next time I'd mine replays early (which opening,
   investment and selling patterns win against which opponents) and iterate on my **own** base built around those
   findings.
2. **Make the base adaptive to the opponent.** Most games were mirrors, and the decisive signal (when to deviate)
   was invisible to my features. An explicit **opponent-type model**, built from the rival's first days of actions,
   would give the policy what it was missing: deviate against mirrors, play safe against unusual styles.
3. **Start with the noise-free method.** I spent days on sampled-return PPO/GRPO before measuring SNR. Measure the
   effect size against the noise first; if it's tiny, go straight to forked counterfactuals.
4. **Evaluate on the real ladder early.** Replay worlds were the most trustworthy test set I had; I should have
   built them on day one.
5. **Never trust a single score.** Identical bundles moved hundreds of rating points live. Paired local tests and
   repeated runs were the only reliable signal.

## 5. Released

- `kaggriculture_v9b_release.ipynb`: rebuilds the exact submitted agent from readable source (SHA-256 checked),
  plays one game on the official engine.
- `rl_layer.py`: stdlib inference runtime (float16, zlib + base85).
- `ppo_layer.py`: the 8-option stage policy, its features and the embedded weights.
- `v9b_stage_policy.safetensors` / `.json`: the trained weights (26 tensors, ~40k parameters) and their metadata.
- `base_pipe16.py`: the public base, unmodified, with all upstream license notices.

## Credits

The base agent is the public Pipe-16 / best_latest_harvest lineage (Apache-2.0) by thomastschinkel, yhay81,
destbreso, aurax7, tetsutani, prvsiyan, Dmitrii Gluzdov and Ahmed Berat Ozer, among others; the full notices are kept
in the source. The exact simulator is debmalyaroy's Rust re-implementation. Thank you all.