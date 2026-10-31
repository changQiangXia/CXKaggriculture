> **来源 / Source**：Kaggle Kaggriculture 公开 write-up，第 645 名，队伍 **Hak**。
> **原文**：https://www.kaggle.com/competitions/kaggriculture/writeups/bronze-from-muzero-to-a-measured-hybrid-agent
> 本文为比赛归档的离线副本，仅作技术参考；**版权归原作者所有**。
> 如作者要求撤下，请联系仓库所有者。

# Bronze: from MuZero to a measured hybrid agent

Thanks to Kaggle and the hosts. Kaggriculture looks like a farming game but behaves like a two-player market problem. This write-up covers what we tried in order, the measurement that ended each approach, and what the final agent does. All numbers come from our logs or the engine source.

![A day-24 frame from one of our ladder games](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F14605908%2Ff5b08e1275fb532ab7f3a3584c1b0253%2F00_game_frame.png?generation=1792243076378088&alt=media)
*Episode 115515621, day 24 of 30. Our agent is on the right (rated 2,112); the rival on the left is rated 2,192. We hold all four land plots to their three and trail by $5.6k in cash at this point; we finished $4,134 ahead.*

## Summary

| stage | what we built | what ended it |
|---|---|---|
| Model-based RL | MuZero / MaZero, ~10M and ~1M parameters, MCTS over a masked factorized action space | Compute. The environment ran at 460k steps/s, and 2.4k with the network in the loop. |
| PPO | Factorized policy, league of frozen opponents, potential-based shaping | Gradient signal: about 2.5% at batch 256, so the batch was ~40× too small for our hardware. |
| Behavioral cloning | 1.12M labeled unit actions from 80 replays of top players, 96.7% held-out accuracy | Covariate shift: 0 wins in 18 games when it played on its own. |
| Hybrid | Scripted strategy plus learned executor | Beat our best RL agent by +$11.9k/game, but stayed below the top public scripts |
| Final | Strong public baseline (V78/V79 family) plus gated layers, each with an OFF switch | Over 252 rated ladder games replayed: 32 losses become wins, 0 wins become losses |

## 1. The game

Each player runs a farm for 30 days of 24 turns (720 decisions). A turn controls the farmer, up to a dozen hired hands, crops, animals, land purchases, and up to 10 market rows. Both players trade in **one shared market**. Each product's price is a function of the town's stock, so whatever one player sells lowers the price the other gets.

![Engine price curves](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F14605908%2Ff90e6017f42c731493a2a3122ecb6f2e%2F01_market_curves.png?generation=1792243089589898&alt=media)

These curves come straight from the engine's `MARKET_PARAMS`. Three properties drove most of our decisions:

- **Milk, wool, strawberry and melon collapse to the $1 floor** once the two farms together sell 50–150 units more than the town buys. Selling into a crashed market is the largest single source of lost revenue. At one point a quarter of our wool sold for $1.
- **Hinge products (carrot, tomato, egg)** stay calm until stock runs short, then jump.
- **Volume is zero-sum.** If we cut our own supply to protect the price, the rival sells at the higher price. Supply cuts against a bigger seller lost money every time we measured them.

Shops unlock every three days from a random roster, and the roster changes which products have buyers. The roster alone explained about a third of the margin variance in our tests.

## 2. Compute

We had no GPU cluster for training.

| machine | used for |
|---|---|
| Google Cloud VM, 96 cores | PPO and MuZero training |
| Azure VM (smaller) | long-horizon runs over the full 720 steps |
| Kaggle TPU sessions (96-core EPYC, 396 GB) | overnight training arms, CPU-bound leagues |
| Local PC, 6 cores + WSL | C++ simulator panels, replay analysis |

## 3. MuZero / MaZero

The game has long delays between action and payoff: land bought on day 6 pays out over weeks. That made a learned model plus search the natural first choice.

- **Networks.** Representation, dynamics and prediction heads, at about 10M and about 1M parameters. MCTS ran over a masked, factorized unit/market action space.
- **MaZero.** The multi-agent variant, for the farmer and the hands acting in the same step.
- **Rollout engine.** We rewrote the engine for rollouts and checked it against the published price table (9 of 9 products) and against replays (689 of 689 mid-day state transitions identical).

We stopped because of throughput. We compiled the full 720-step episode into one `jax.lax.scan`:

| configuration | game-steps / s (laptop CPU) |
|---|---|
| environment alone | 460,072 |
| environment + observation encoding + network + sampling | 2,440 |

The network costs 190× the environment. The 10M model needs millions of self-play games to learn the economy, and our CPUs could produce only a small fraction of that. The 1M model was cheap enough to train, but in the time we had it did not get close to the scripted agents. With 10–100× the compute this is still the direction we would take.

## 4. PPO

### 4.1 The gradient was mostly noise

PPO plateaued early. To check why, we estimated the gradient on two disjoint halves of each batch and measured the cosine between the two estimates.

![Gradient cosine vs batch size](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F14605908%2F6ed07fc9c9a39d28f3f8e9c9306149dc%2F02_gradient_cosine.png?generation=1792243105288898&alt=media)

- The policy gradient follows `cos ≈ bs / (bs + k)` with k ≈ 10,000.
- At our batch of 256 that is about 2.5% signal, so the batch was roughly 40× too small.
- The value gradient, measured on the same batches, agrees well. That rules out a pipeline bug.
- In the run we diagnosed, 58k of 70k updates made no measurable progress. The dev curve peaked at about 12k updates.

### 4.2 Self-play against a mirror cannot move the margin

| opponent during training | margin / game vs the reference | wins | t |
|---|---|---|---|
| frozen copy of itself | −$1,484 | 46.9% | −0.71 |
| league of frozen past checkpoints | +$102,124 | 100% | 28.9 |

With the same network in both seats the expected margin is zero by symmetry. Any improvement also improves the opponent.

### 4.3 Reward

- **Signal.** The cash-delta reward gave a Monte-Carlo return standard deviation of about $2. Potential-based shaping, with cash plus asset value as the potential, raised it to $212.
- **No change to the objective.** The shaped return telescopes exactly to the true final margin, with a conservation error of 0.0.
- **Audit of the information flow.** Among other problems it found a critic learning rate 100–1000× too low, and a KL anchor that capped rare actions such as land purchases at their prior probability.

## 5. Behavioral cloning

- **Data.** 80 replays of players rated 2,742–3,108, both seats: 113,602 steps, 1.12M unit-action labels.
- **Labels.** Each label went through the exact encoder and action mask used at play time. 1.7% were illegal under our mask. All 124 of 124 land purchases survived extraction.

| head | operation | argument | quantity | market row |
|---|---|---|---|---|
| held-out accuracy | 96.7% | 92.9% | 98.2% | 79.5% |

The clone even bought land twice per game, as the leaders do. When it played on its own it lost all 18 games, by −$113,569 per game on average.

![Action mix, leaders vs clone](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F14605908%2F204e8a6972c9e2f75422ff716db986ca%2F03_bc_action_mix.png?generation=1792243117767655&alt=media)

This is compounding covariate shift:

1. The clone moves like a leader.
2. It arrives one tile off.
3. The action mask forbids the productive action on that tile, so it passes.

Movement shares match exactly. Every action that depends on being in the right place collapses, and PASS triples.

We kept the clone as an initialization and KL prior for RL. We also generated DAgger labels from a scripted expert on the clone's own states.

## 6. Hybrid, then the final agent

- **Diagnosis.** Imported onto a leader's farm mid-game, the RL agent earned about 85% of the leader's daily income. Its execution was fine; its weak part was strategy: land, crew size, animal mix.
- **Hybrid.** A scripted planner took strategy and the learned executor carried it out. That beat our best RL agent by +$11,886/game (95% CI +$8.8k to +$14.9k), with an 82% win rate over 96 paired games.
- **Final agent.** For the last weeks we started from the strongest public script family (V78/V79, Apache-2.0; thanks to its authors) and added our own layers on top:

```
action = baseline(obs)                       # public V78/V79 route (one of 41 recorded strategies)
for layer in [garden_crew, sheep_rules, feed_guard, pump_gate, market_timing]:
    if layer.gate(obs):                      # gate reads only observable state
        action = layer.edit(obs, action)     # gate off => action is byte-identical to the parent
```

Every layer has a one-line OFF twin. We check that the OFF build reproduces the parent to the dollar, then measure the layer on its own.

| layer | what it does | measured effect |
|---|---|---|
| garden crew | The baseline buys a 25-tile garden and plants only 10. A plant survives one dry night and fertilised tomatoes hold more, so a batch crew can water every second day and tend all 25 tiles for about the labour of 10. | +$656/game where it fires; no game made worse |
| rival-pump gate | Some rivals bought ~70 wheat one step before our wheat round trip and sold right after, taking ~$20 per cycle. A detector built on public market stock skips that one buy. | precision 1.000, recall 0.998 on 478 games; 3 losses → wins, 0 wins → losses |
| feed guard | Buys exactly the missing feed wheat when a FEED action fails, before animals escape after two unfed days | only fires in cash-starved towns |
| sheep rules | Add sheep when a second yarn shop appears; retire sheep from day 24 in towns that never get one | measured separately per roster type |

## 7. Evaluation

We dropped about two dozen ideas because of these measurements.

1. **Exact, faster simulator.** An open-source C++ port of the engine is bit-identical to the official one: 13 of 13 seeds, both seats. It runs about 10× faster, which made 500–1,000-seed paired panels routine.
2. **Paired and seat-swapped.** Each candidate played the same towns against the same 47 opponent agents, in both seats, and was compared with its parent. We report losses → wins and wins → losses alongside the mean.
3. **Pre-registered splits.** Development seeds, then fresh confirmation seeds, then a 40-game held-out set used once per candidate.
4. **Replays of our own ladder games.** We downloaded our rated games and re-ran each one on the official engine. The opponent replays its recorded actions; our side is the candidate. The town roster must be pinned to the live one:
   - the engine draws weeds per empty tile before it draws shops, so any change to our farm re-rolls the town;
   - one unpinned game looked +$533 better, and the pinned replay showed −$1,210.

![Ladder replays](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F14605908%2F56047a90d85037fcdcc7836bbcfc453e%2F04_ladder_replays.png?generation=1792243130483346&alt=media)

On 252 rated games from our last two submissions, the unmodified baseline reproduced the live margin exactly in every game we checked (193 of 193). With our layers:

- wins went from 155 to 187: 32 losses became wins, and no win became a loss;
- the mean margin rose by $571 per game;
- the gain is largest against rivals rated 2,000–2,200.

5. **Static replays mislead for market-timing layers.** A recorded opponent cannot react. A layer that sells ahead of it looks free on replays:
   - an "hour-0 sell" layer flipped 24 of 62 losses on recorded games;
   - against reactive opponents in the simulator it was negative;
   - a live A/B on the ladder showed no effect.

   We left it out.

### What still loses

![Remaining loss gap](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F14605908%2F8f58b6c1beb15add6ab3ed7683438455%2F05_remaining_loss_gap.png?generation=1792243141360799&alt=media)

In the 37 games still lost to rivals rated under 2,300, egg and strawberry account for most of the gap:

- **Egg:** in the games that decide it, the rival keeps more geese than we do.
- **Strawberry:** rivals sell about the same volume at higher prices. Their planting calendar lands harvests on high-price days, and they sell at hour 0 while we sell at hour 1.

Neither gap could be closed with an additive layer. Both need a different opening and a different planting schedule.

## 8. With more compute

- **MuZero / MaZero:** the 10M model with a batch near the k ≈ 10,000 knee, trained against a league, with terminal-margin reward and exact shaping.
- **Openings:** a learned opening. The top agents buy animals and hire on turn 1, and hold all four plots and about 9 geese by day 9.

## 9. Takeaways

- **Measure gradient agreement before tuning the optimizer.** A batch that is 40× too small looks exactly like "RL does not work here".
- **Use a league, not a mirror.** Mirror self-play has zero expected margin.
- **Check imitation in the policy's own rollouts.** High held-out accuracy says nothing about compounding error, so compare the action mix there.
- **Make the simulator exact before making it fast.**
- **Control the randomness in every comparison.** Pair games, swap seats, pre-register the splits, and pin every random draw that your own actions can shift.
- **For market-timing changes, A/B on the ladder.** Neither static replays nor a simulator can judge them.

Questions are welcome in the comments.