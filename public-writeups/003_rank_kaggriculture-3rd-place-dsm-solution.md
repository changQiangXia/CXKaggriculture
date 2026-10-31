## 1. Summary

- The final submission is one model (gen70) with several stages of inference-time post-processing on top. The model is a policy that we built by BC from top teams' replays and then strengthened with self-play PPO. The run behind the final submission trained on about 360M steps (about 127k games) and reached generation 70 by promotion.
- Only the timing of plot purchases is constrained, by a rule we derived from top teams' replays. PPO learned to win under that constraint. (A Discussion thread said "4 plots do not work". We kept only the timing rule and left the choice of what to grow to the model.)
- The model is a Transformer (10.4M parameters) that reads the board as 266 tokens. It is an end-to-end policy: every step it directly outputs the moves of all units and the list of market orders. It has no macro actions such as a daily strategy.
- Most of the strength came from PPO. The reward is only the final win/loss. Training only took off once we pre-warmed the critic, clipped the ratio per decision, and used an antisymmetric critic (league win rate 0.359 → 0.542). We ran asynchronous actors and learners on up to 23 A100s and trained on 20.1B positions in total (about 21M games) over 1,883 generations.
- The post-processing does not touch the model. It tentatively applies moves with the official rule functions and fixes only moves that certainly have no effect and items that would be discarded. On the final submission's policy (gen70) it raised the win rate by +5.0pp (gen41: +4.8pp). As a counter to the top teams, we grow melons at the end of the game. A rule decides when to buy melon seeds, and we taught PPO to "grow, harvest, and sell" them with a training-time intervention. On gen70 the melon-seed rule added another +8.2pp; all the post-processing of the final submission together took the win rate from 74.2% to 87.8% (§9.1).
- We made decisions from hundreds to thousands of paired games (same seed, both seats) on fast engines (C++ and Rust) that match the official engine transition by transition.

## 2. Game and constraints

- A two-player farm simulation. A day has 24 steps, and there are 30 days: 720 steps in total. The player with more money at the end wins. The rating moves only on win, loss, or draw; the coin difference does not matter (official Evaluation page).
- The final ranking is decided by Bradley–Terry on the games played over about 2 weeks after the deadline. Each team's latest 2 submissions count (same source).
- Each step has 1 second (actTimeout). Time beyond that comes out of a 60-second overage budget per game (remainingOverageTime). When the budget runs out, the agent gets TIMEOUT (`kaggriculture.json` in kaggle-environments 1.32.7).
- Three things made learning hard: the reward comes only at the end of 720 steps; each step has 31 decisions (20 units + 11 market order slots: up to 10 orders and STOP); and the market is shared, so the same plan can be good or bad depending on how the opponent sells.

## 3. Overview

![01_overview](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F23924550%2F1c3e1df29065e587b3474d4844a9c9be%2Foverview.png?generation=1792139217284684&alt=media)

- The light frames are layers (data → imitation learning → reinforcement learning → evaluation and submission → improvement). The picture inside each box shows that layer's model and evaluation metric.
- The thick green arrows are the training loop (actors → learners → gate → actors). The dashed purple arrows are improvements that come back from replay analysis. Rules that work go back to the actors as training-time interventions (§6.5).

**Submission notes**

- Final 2 submissions: sub125 has no replanting. sub126 is sub125 with melon replanting added as the last stage. Whether replanting helps depended on the situation (§7.1, §9.1), so we submitted one version with it and one without.
- Each post-processing stage takes the action returned by the previous stage and returns an action. Every stage except MELON16 catches exceptions and then returns the action it received unchanged; MELON16, a short rule, has no exception handler.

## 4. Data and preprocessing (BC demonstrations)

- We fetched top teams' public episodes with the Kaggle API and replayed them in our C++ engine to build (board tokens, legal moves, actual move) for each step. We drop any game where encode → decode → engine does not reproduce the official final balance.
- The first demonstration set came from the top 4 teachers (two Team B agents, Team G, and Team H): 2,497 games and 1.795M moves (19 held-out games). We chose the teachers with a round robin between the baked-in teacher IDs.
- Once Team A (1st at the deadline) became strong with its 3-plot style, we fine-tuned on Team A's games (285 seats for training / 55 held-out seats; later, 121 seats and 87k moves from one active submission).
- In a subsequent BC experiment, we used 106 public games from Team A's submission 56640167. We reserved the latest 16 games for validation and used the remaining 90 for training, giving 11,504 validation positions and 64,710 training positions. The split was by game, not by individual position. We checked that the training and validation sets had no overlap in episode IDs or seeds, and that neither set shared seeds with the separate evaluation panel checked at the time.
- Both BC variants started from the same existing policy checkpoint from the Sub112 training run. One used standard market-token cross-entropy; the other used normalized class weights proportional to the inverse square root of each market token's frequency in the training data. The weighted loss increased the contribution of rare orders, including land and seed purchases. Both runs completed with early stopping and saved their best validation-loss checkpoints. We referred to the frequency-weighted variant as MMPQ-BCw.
- The subsequent PPO launch configuration specified the MMPQ-BCw checkpoint as its initial policy and disabled the auxiliary replay-BC loss (AUX_BC=0).
- Earlier, we replaced teacher moves that were illegal under the old mask with a wait. When we stopped doing this, the reproduction of 9 teams × 6 games went from 0/6–5/6 to 6/6 for every team.

## 5. Model

![model](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F23924550%2F12848991c022d8844dfd47e302729076%2FA.png?generation=1792139261697912&alt=media)

- Input: 200 tiles + 20 own units + 20 opponent units + 16 shops + 9 items + 1 global = 266 tokens. IDs (type, crop, coordinates, unit, shop, item, time, day) go through embeddings, numeric values go through a Linear layer, and the results are summed. There is no sequence position embedding.
- Transformer encoder: 6 layers, d=320, 8 heads, FF 1024, pre-norm.
- Unit head: from the tokens of the unit and of the tile under it, the head scores each of 44 candidates (with a legal-move mask). The 24-class quantity is conditioned on the chosen candidate. Units are independent of each other.
- Market head: a 2-layer decoder cross-attends to all 266 tokens and outputs the order list autoregressively until STOP (23 candidates, 132 quantity classes, up to 10 orders).
- 10,441,973 parameters in total. 0.110–0.117 seconds per step on Kaggle.
- The legal-move mask is computed on the board at the start of the step. So it does not include moves that are valid only if another unit's action in the same step runs first (for example, DROP and then sell in the same step). We later moved to a new mask, with a −6 offset on the newly allowed moves. Even then, greedy decoding rarely picks the moves that only the new mask allows.

### 5.1 Architecture choices

- **Network size** came from a BC sweep (09-11 to 12, same teacher data, win rate over 290 greedy games with fixed seeds).

  | Parameters | 1.0M | 2.8M | **10.4M** | 27.8M | 36.2M | 66.3M |
  |---|---|---|---|---|---|---|
  | Win rate | 0.128 | 0.203 | **0.593** | 0.617 | – | – |
  | Held-out loss | 2.078 | 2.048 | 1.917 | 1.909 | overfit | diverged |
  | Inference per step (local CPU) | – | – | 142 ms | – | 383 ms | 590 ms |

  In 2 pairs that differed only in size, 10.4M and 27.8M showed no difference (+604 ± 1,400 coins, −0.031 ± 0.062). 27.8M had the lower loss both times but the same strength, so we decided to choose by games, not by loss. We picked 10.4M, which also leaves margin in inference time under the 1-second limit. We never compared sizes all the way through PPO.
- **Why RL is the base.** A tape that follows a top team's script cannot adapt when the opponent or the shop layout changes. From the start, we decided to use RL to strengthen a policy that learns its own play, instead of copying other teams.
- **Why no macro actions.** In the first week we tried two forms: PPO correcting only the market layer of a scripted player, and PPO choosing a daily strategy vector (12 values). Neither changed the policy's decisions much (§6.3). We switched to directly outputting primitive actions for all units and left the action granularity to training.
- **From CNN to Transformer.** Our earlier CNN fed each ID in as a single number. This imposed an order on IDs that have none. A token sequence with everything embedded handles shops, the market, and units in the same form.

## 6. Training

### 6.1 How BC and PPO learn

![BC and PPO](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F23924550%2Fd94176776dba4e77e22a64aa69758160%2Fbc_ppo.png?generation=1792139340982530&alt=media)

The top row sketches BC and the bottom row PPO (the values are for illustration). BC raises the probability of the teacher's move in each position. PPO uses only the final win/loss as the reward. It spreads the difference from the critic's estimate (the advantage) over the steps, raises the probability of good moves, and lowers the probability of bad ones. To avoid moving too far in one update, it clips the probability ratio (the probability that the updated policy picks the move ÷ the probability that the policy that played the game picked it) to 0.8–1.2.

#### BC loss

For one position `s`, given the teacher's move (candidate `c_u*` and quantity `q_u*` for each unit `u`; the market order list `m_1*, ..., m_L*` with quantities `r_j*`),

$$
\mathcal{L}\_{\mathrm{BC}}(s) = -\sum\_{u} \Big[\log \pi(c\_u^{\ast} \mid s) + 0.5\\,\log \pi(q\_u^{\ast} \mid s, c\_u^{\ast})\Big] - \sum\_{j=1}^{L} \Big[w\_j \log \pi(m\_j^{\ast} \mid s, m\_{\lt j}^{\ast}) + 0.5\\,\log \pi(r\_j^{\ast} \mid s, m\_{\le j}^{\ast})\Big]
$$

- The first term covers each unit's action, and the second covers the market orders. Quantity terms count only for moves that have a quantity (plant, carry, place, buy, sell).
- The market uses teacher forcing. To predict the j-th order, we feed the teacher's orders 1 to j−1 as input. We count up to the first STOP.
- `w_j` is 20 for plot purchases (BUY_LAND) and 1 otherwise, because a game has only a few plot purchases.
- AdamW (wd 0.01) + OneCycleLR, gradient clipping 1.0, bf16.

#### PPO loss

For each of the 31 decisions `k` at step `t` (20 units + 11 market positions),

$$
\rho\_{t,k} = \frac{\pi\_\theta(a\_{t,k} \mid s\_t)}{\pi\_{\mathrm{old}}(a\_{t,k} \mid s\_t)}, \qquad
\mathcal{L}\_{\mathrm{PPO}} = -\\,\mathbb{E}\_t\\!\left[\frac{1}{\sum\_k m\_{t,k}} \sum\_k m\_{t,k}\\,\min\\!\Big(\rho\_{t,k}\hat A\_t,\ \mathrm{clip}(\rho\_{t,k}, 0.8, 1.2)\\,\hat A\_t\Big)\right] + \beta\\,\mathrm{KL}\big(\pi\_\theta \\,\\|\\, \pi\_{\mathrm{best}}\big)
$$

- `m_{t,k}` marks the decisions that count (live units, and market positions up to STOP).
- The advantage `A_t` (with a hat in the formulas) comes from GAE. The reward `r_t` is `sign(own money - opponent money)` at the end of the game only, and 0 at every other step.

$$
\delta\_t = r\_t + \gamma V(s\_{t+1}) - V(s\_t), \qquad \hat A\_t = \sum\_{l \ge 0} (\gamma\lambda)^l\\, \delta\_{t+l}, \qquad \gamma = 1,\ \lambda = 0.95
$$

- The critic is a network separate from the policy: `V(o_t) = 0.5 * (v(o_t) - v(o'_t))` (`o'_t` is the opponent's observation, used only in training). It fits the target `A_t + V(o_t)` with smooth L1.
- The KL term is the distance to the best version that was last promoted. There is no entropy term.

#### BC notes
- We embed the teacher ID, add it to the global token, and learn all teachers in one network. For submissions and as the PPO starting point, we use a plain policy with a strong teacher's ID embedding added into the weights (baking in the teacher ID; output difference 2.2×10⁻⁶).
- Held-out loss is not a proxy for strength (§5.1). Fine-tuning from the baked-in weights was stronger than training from scratch on Team A's games (0.661 vs 0.523).
- Re-running BC on replays with a PPO-trained network drops it to 0.198 against the original weights (the PPO strength is lost). To nudge the policy, add a small auxiliary loss only on the targeted positions (0.02 for tomatoes).

### 6.2 PPO

- The reward is only the final win/loss, ±1 (draw 0). GAE γ=1, λ=0.95.
- We take the ratio and the clip (ε=0.2) per decision over the 31 decisions (20 units + 11 market positions), not on the joint probability of the step.
- An antisymmetric critic, separate from the policy (V = (v(own observation) − v(opponent observation)) / 2; the opponent's observation is used only in training). A new run inherits its parent's critic (building a new one cost about 0.04 in win rate).
- A KL penalty to the best version that was last promoted. No entropy term. Critic learning rate 2×10⁻⁵, minibatch 2,048, 1 epoch.
- League: our 8 most recent generations; strong policies from past submissions and other runs; and virtual opponents that are BC clones of rivals (Team A type = our weights trained with an extra 0.03 BC loss on Team A's seats; Team C and Team E types; and others). We checked win rates against the virtual opponents when judging new generations and in the unified ladder (the ladder required "vs Team A type ≥ current champion − 0.02"). Opponents we lose to more often are drawn more often (PFSP, w = 0.15 + (1 − p̂)²).
- The game mix per iteration, the gate, the learning rate, and β changed from run to run. The values for the main runs below come from the config lines in the training logs. Most runs used 192 games per iteration (48 self-play, 48 vs the best version, 72 league, 24 recorded) with a gate every 4 iterations (later runs used a stricter gate, §8.2). Only the last run, v4xy, used 96 games (32 self-play, 64 league) with a gate every 8 iterations.
- The final submission's run (gen70): about 360M steps (about 127k games), 70 generations. Strong past models were in the league, and a generation was promoted if it beat several models at a 60% or higher win rate. Plot-purchase timing was constrained by a rule, and the policy learned to win under it. Melon top-up purchases were added as a training-time intervention (§6.5).
- PPO from scratch, without imitation learning, collapsed. A game has 720 steps, and the path from early actions to a win is long. So we started from BC.

| Run | Period | Rank at the time | Start | Games per iteration (self / best / league / recorded) | Gate | LR | β (KL) | Updates | Positions trained | Generations | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| o9 | 09-14 | 5th | BC (initial) | 48 / 48 / 72 / 24 | 4 iters, 0.60 | 5e-05 | 0.1 | 99 | 17M | 5 | Pre-warming the critic |
| o19 | 09-15–16 | 2nd | BC (initial) | 48 / 48 / 72 / 24 | 4 iters, 0.60 | 5e-05 | 0.1 | 200 | 33M | 9 | First PPO submission, v66 |
| o37 | 09-17–18 | 2nd | Teacher-ID BC | 48 / 48 / 72 / 24 | 4 iters, 0.60 | 5e-05 | 0.1 | 337 | 57M | 15 |  |
| o37pace | 09-18–19 | 2nd | o37 | 48 / 48 / 72 / 24 | 4 iters, 0.70 | 5e-05 | 0.1 | 318 | 55M | 10→32 |  |
| p19anneal | 09-19–21 | 2nd → 1st | o37pace | 48 / 48 / 72 / 24 | 4 iters, 0.60 | 5e-05 | 0.1 | 709 | 122M | 20→44 |  |
| apo2 | 09-19–20 | 2nd | p19 lineage | 48 / 48 / 72 / 24 | 4 iters, 0.60 | 5e-05 | 0.1 | 501 | 1.21B | 28→80 | Asynchronous |
| apo5 | 09-19–20 | 2nd | p19 lineage | 48 / 48 / 72 / 24 | 4 iters, 0.60 | 0.0001 | 0.1 | 491 | 1.01B | 30→79 | Asynchronous; gen79 = v80 |
| land5 | 09-20–23 | 1st | apo5 lineage | 48 / 48 / 72 / 24 | 4 iters, 0.60 | 5e-05 | 0.03 | 60 | 46M | 137 | 4th plot during training only |
| g5g | 09-22–24 | 1st (briefly 12th) | land5 lineage | 48 / 48 / 72 / 24 | 4 iters, 0.60 | 2.5e-05 | 0.02 | 837 | 426M | 82 |  |
| g5g4 | 09-23–25 | 1st | g5g | 48 / 48 / 72 / 24 | 4 iters, 0.60 | 2.5e-05 | 0.01 | 596 | 546M | 47 |  |
| pn2p | 09-24–25 | 1st | Team A BC (pn2ft) | 48 / 48 / 72 / 24 | 4 iters, 0.60 | 2.5e-05 | 0.02 | 444 | 254M | 45 | v90 |
| pn2pnm | 09-25–27 | 1st–4th | pn2p | 48 / 48 / 72 / 24 | 4 iters, 0.60 | 2.5e-05 | 0.02 | 751 | 1.03B | 58 | New mask |
| pntom45 | 09-26–29 | 1st–4th | pn2pnm | 48 / 48 / 72 / 24 | 4 iters, 0.60 | 2.5e-05 | 0.02 | 548 | 564M | 34 | Tomato auxiliary loss 0.02 |
| v4x | 09-29–30 | 2nd–4th | Virtual Team A (vpfn4) | 48 / 48 / 72 / 24 | 4 iters, 0.60 | 2.5e-05 | 0.01 | 177 | 336M | 22 | 4 plots + tomatoes |
| v4xt | 09-29–30 | 2nd–4th | Teammate's gen23 | 32 / 0 / 64 / 0 | 4 iters, 0.60 | 2.5e-05 | 0.02 | 519 | 221M | 23 |  |
| v4xy | 09-30 onward | 4th → 3rd | Teammate's gen35 | 32 / 0 / 64 / 0 | 8 iters, 0.60 | 2.5e-05 | 0.005 | 91 | 193M | 2 | Melon intervention |

"Positions trained" covers only that run's own log span (not its parent's). For land5 it covers only part of the logs.

- When we put an opponent's new generations into the league right away, the league filled up with opponents we could not beat, and promotions stopped. So we swapped them in only after we caught up (≥ 0.5 against them).
- Caveat: BC-cloned virtual opponents are weaker than the real ones. Local win rates against them came out about 0.4 higher than in real games. A virtual opponent is a guide to "are we winning at all". Beating it does not mean we can beat the real team.

### 6.2.1 Training History

![Training History](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F23924550%2Fa5a3adf422c4433e6591c29eed0fcd9f%2Fhistory.png?generation=1792139303367703&alt=media)

### 6.3 Getting RL to work

![RL Flow](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F23924550%2Ff599437ce9a2f8303c1f81bf561e8b79%2Frlflow.png?generation=1792139398866263&alt=media)

Our first RL barely moved. Each row reads "what we tried → result → cause → so next", and the next row is the result of trying that next step. The 5 pieces that survived to the end, combined, let us submit PPO weights for the first time. The bottom row shows trials with different BC teachers (replays). Most of them did not help, and starting from a strong teacher's BC became a prerequisite.

**Glossary**

| Term | Meaning |
|---|---|
| Network | A neural network. In this solution, the Transformer that reads the board and outputs moves (§5) |
| Policy | The network that outputs, for each position, which moves to play and with what probability. This is what we submit |
| Critic | A network separate from the policy that predicts, from a position, "are we likely to win if things go on like this". PPO uses it as the yardstick for how good a move was. It is used only in training and is not part of the submission |
| Antisymmetric critic | The prediction from our own view minus the prediction from the opponent's view, halved. Swapping the two players flips the sign, which matches the nature of win/loss |
| Value head / trunk | The value head is the part of the network's output that gives the estimate. The trunk is the shared part before it |
| Decision | One individual choice within a step: 20 unit actions and 11 market order slots, 31 in total |
| Ratio | The probability ratio used in PPO. For a move actually played in a position: "the probability that the updated policy picks that move" ÷ "the probability that the policy that played that game picked it". Example: if the policy picked harvest with 0.30 and after the update picks it with 0.36, the ratio is 1.2. A ratio of 1 means no change |
| Clip | Cutting the ratio off at 0.8–1.2. For a good move (positive advantage), the objective stops growing once the ratio goes above 1.2. For a bad move (negative advantage), it stops growing once the ratio goes below 0.8. This keeps one update from moving a move's probability by more than 20% |
| Whole-step ratio vs per-decision ratio | One step consists of 31 decisions. The whole-step ratio is the product of the 31 ratios, so small changes in each decision quickly push the product outside 0.8–1.2. Most steps got clipped, and learning stopped. So we took the ratio and the clip per decision |
| γ, λ | γ sets how much future reward is discounted (1 means no discount). λ sets how many steps ahead the advantage looks |
| EV | Explained variance: how much of the variation in actual outcomes the critic's predictions explain. A positive value means the predictions are useful |
| Pre-warming the critic | Training only the critic before the policy starts to change |
| Gate / generation | After a fixed number of updates, the current policy plays the best version and others. If its win rate passes the threshold, it is promoted as a new generation |
| League | The pool of training opponents: our past generations, strong external policies, and virtual opponents that are BC clones of rivals' replays |
| Baking in | Adding the teacher ID's embedding into the network weights, so that the result is a plain policy that needs no ID input |

### 6.4 Compute and scale

- Actors and learners are connected only through files on shared storage (replay chunks in buf/, weights in pub/). If either side goes down, it can restart without the other side waiting.
- The cluster does not accept multi-node jobs on partial nodes, so we used torchrun to bundle separate 1-GPU jobs into one DDP group. When the queue was full, we piggybacked on our own running jobs with srun --overlap. Up to 23 A100s.
- Reusing the gradient-sync buffers cut one update from 104 s to 37 s (results unchanged). Throughput was about 6M positions/hour on 1 GPU and about 44M positions/hour on 23.

| Item | Value |
|---|---|
| PPO runs / updates | 395 / 44,733 |
| Positions / games trained (estimated) | 20.1B / about 21M |
| Promoted generations | 1,883 |
| Evaluation games | about 2.8M (league 1.92M + gate 0.71M + official engine 2,135) |
| Compute | about 17,400 A100 GPU-hours (sum over runs with surviving logs; the final run's ~360M steps are not included) |

### 6.5 Teaching the policy through interventions

![How the intervention works](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F23924550%2Fc05675b2aa4f20700f24529b5dbee4c5%2Fintervention.png?generation=1792139441717409&alt=media)

When a move worked as an inference-time rule, we also made the policy play it during training so that the policy would learn it. The key is to **record the rewritten move as the policy's own move**.

**Why we used interventions**

- Interventions can hurt generalization. They hand the policy a move from outside that it should have found by itself. Against opponents or boards the rule did not anticipate, the learned move can turn into a bad move.
- On the other hand, in this competition every team competes side by side for win rate on the same LB. What matters is how quickly you reach top strength and win rate within the competition period.
- The ideal is to become strong from pure from-scratch self-play, as in shogi. We considered this. But during the competition, new play styles and metas (4 plots, tomatoes, melons, and so on) kept appearing. We judged that if we waited for self-play to find them on its own, we could not keep up in time. In fact, RL from zero without BC collapsed (§6.3).
- So we used interventions to add moves that replay analysis showed to work, which made the policy stronger right away. We then left the rest, such as "when to grow, harvest, and sell", to PPO.

1. Right after sampling a move from the policy, and before passing it to the environment, the actor rewrites the move with a rule (for example, it adds melon seeds to the market order list).
2. The rewritten move is saved as-is to the training trajectory.
3. For the saved move, we recompute the behavior policy's probability `log pi_old`. This makes the PPO probability ratio correct for the move that was actually played.
4. If the game is won, the probability of that move goes up; if it is lost, the probability goes down. The policy then plays the move by itself, even after the rule is removed.

| Item | Melon (final run) | 4th plot (land5) |
|---|---|---|
| Rewritten move | Add BUY_SEED melon to the market orders | Add BUY_LAND |
| Timing | Morning of day 16–17 (differs by 1 day depending on the run trained) | When there are 3 plots and enough money |
| Condition | Few melon plants and seeds, and the policy has not bought them itself. 2 or more plots | — |
| Amount | Up to 3 seeds | 4th plot |
| Seats it applies to | The learner's seat only. Not applied to the league opponents' seats | Same |
| Rate | Probability 1 (not lowered) | Throughout training |
| Result | Generation 2 vs generation 1: +363 ± 79 (official engine, 195 games) | Against a strong 3-plot opponent (v80): 0.656 → 0.875 |

The forms that did not work (adding moves quietly on the environment side, forcing a cow opening, limiting spending, buying the 2nd plot earlier) are collected in §10. Only one form works: rewriting "moves the policy already gives some probability to". We also limited it to rules whose effect we had first measured as inference-time rules (the improvement loop in §3).

## 7. Inference-time post-processing

### 7.1 Teammates' post-processing (masspeaks; `_land`: shimishige)

Post-processing that closes out the endgame. On the last day, it sells everything left in the barn. Each day, it sells before the barn overflows (it sells when the crop in question is at or above its base price). As a counter to the top teams, it grows melons at the end of the game.

- `_pace`: when the inventory goes above a target for each time × item (the 75th percentile over 90 games of a strong team), it adds a sell for the excess. From step 710 on, it sells the inventory divided by the number of remaining steps.
- `_land` (shimishige): at steps 240–709, with fewer than 4 plots, if money + the expected sales of that step ≥ 4,000, it adds BUY_LAND.
- MELON16: at hours 0–5 on day 16 (steps 384–389), it buys melon seeds until seeds held + seeds planted today + seeds ordered reach 3 (keeping 1,000 money). On gen35, with vs without the rule: +434 ± 34 coins/game (768 games), and +285 ± 110 on the official engine.
- Melon replanting (sub126 only): on days 16–19, while melon seeds remain, it replaces the policy's PLANT WHEAT / CARROT with PLANT MELON. Melons are normally grown early (prices are high early), but the price recovers a little near the end. We simulated swapping crops and judged that growing melons once more at the end (double cropping) is better. On the official engine: +456 ± 137 vs sub125 (36 seeds; identical agents against each other give ±0). Against our team's policies in §9.1 it did not help (−1.67pp). Because the result depended on the situation, we made the two final submissions with it (sub126) and without it (sub125).

### 7.2 Fixing only moves that certainly have no effect

**Approach.** No training. It does not depend on the weights, so the same code works on any generation of the policy. We bundle the unit-action functions of the official `kaggriculture.py` (kaggle-environments 1.32.7) unchanged. We apply the policy's unit moves in order to a copy of the observation and check "does this move change the state?" and "what happens in the end-of-day processing?". If an exception occurs, it returns the policy's action unchanged. Added time per step: mean 0.19 ms (p99 0.42 ms, measured on 7,190 steps of real LB observations).

**Count first, then replace.** First, we counted, by type, the moves that cannot affect the final money (an arm that only detects them and does not change the action). Then we tried each replacement one at a time with the same seeds (640 games; the policy was the 9/28 submission (3-plot style); the opponents were 5 of our team's past submissions; both agent_index values).

| Rule | Target | Fix | Occurrences (per game) | Result (coin difference / game) |
|---|---|---|---:|---|
| Ineffective CARE | CARE whose first boosted production day falls after the game ends | Best other legal move | 8.8 | +85 (p = 0.0008) |
| Sell the barn overflow | At hour 23, the amount that would be discarded at the end-of-day intake because the barn (capacity 100) is full | Add a SELL of exactly that amount. Unit moves are not changed | 1.1 | +166 (p = 0.002) |
| Last-step sell | Items left in the barn at the last step (step 718) | Add a SELL | — | +231 together with the overflow sell (p = 9e-6) |
| Ineffective watering and feeding | WATER that cannot raise the yield; FEED and WATER on the last day | Best other legal move | 1.6 / 0.5 | Small positive, not significant |

The failures were just as clear. Rules that changed unit moves dozens of times per game hurt the policy badly (§10). What worked were narrow rules whose targets were limited to moves that certainly have no effect. In a later fix, we also made use of the empty-order `[]` slots that the model outputs. The first version treated those slots as filled.

### 7.3 Selling at the barn at hour 23

At hour 23 on days 0–28, for units at the barn's access tile, we replace a move, PASS, DROP, or PICKUP with DROP. In the same step, we sell any of STRAWBERRY, MILK, MELON, CARROT, TOMATO, and EGG whose price is at or above its base price (5.8 items per game on average, sold at 1.22× the base price). A version without the price condition lost money (coin difference −614 in a smoke test), so we dropped it.

### 7.4 Last-day collection plan

Units ended the game still holding about 1.1 items (about 34 coins) per game. A small planner (greedy insertion + local improvement) builds routes on the last day that carry those items to the barn and sell them.

To make it in time for the final sell-off, the plan has to balance work against hauling. After testing, we start the plan at hour 12 on the last day (step 708), and we discount an item's value the later it reaches the barn (value × (1 − α × steps from harvest to storage), α = 0.01).

We also tried a version without the discount (it sold everything in the last few steps, and the price dropped) and versions that start at hour 0 or hour 6 (they took up to 1.5–4 seconds per step and used too much of the overage budget).

## 8. Engines and evaluation

### 8.1 Fast engines

| Engine | Match with the official engine | Speed | Use |
|---|---|---|---|
| C++ (`kagsim`, pybind11; based on nikital7's public notebook [4000x environment speedup](https://www.kaggle.com/code/nikital7/4000x-environment-speedup-kaggriculture), Apache-2.0) | Exact match with the official traces over 719 steps | 256 games/s on its own (about 12,000× the official Python), about 5× more when batched | PPO games, `fasteval` |
| Rust | The full state matches at every transition over 1,000 seeds and 96,000 transitions | about 29,800 games/s with 8 threads and batch 256 | Team round-robin evaluation (`league.py`) |

- Two things made the match exact: a CPython-compatible MT19937 RNG, and preserving Python dict insertion order (which decides which items remain when the barn overflows).
- We kept the official engine as the ground truth and made it a rule to run the pre-submission tests on the official engine.

### 8.2 Evaluation rules

- Gate (promotion to a new generation): the criterion changed over time. Early runs used the 0.60 gate every 4 iterations in §6.2. Later, the candidate played 768 games against the current champion; if the win rate was ≥ 0.52, we extended to 1,536 games and required z > 2. The candidate must also score ≥ current champion −0.02 on yardsticks of other styles (such as the Team A-type BC) (the standard error over 768 games is about 0.018).
- We judged interventions and branches by head-to-head games against a control started from the same parent at the same time. We read the KL during training together with the gate results (KL alone cannot tell divergence from stagnation).
- Not used for decisions: the public score, a single 384-game run, money partway through the game, re-plays against opponents that do not react, and BC held-out loss.
- Pitfall: the league evaluator did not call the rules that run after `agent()` (we noticed because the tie rate between with-rule and without-rule was high, at 0.34–0.49). After that, we measured post-processing through the whole `agent()` chain: MELON16 and melon replanting on the official engine (§7.1), and the stage-by-stage A/B of §9.1 on the Rust engine (§8.1).
- Post-processing A/B: we fix the arms, opponents, seeds, and main metric before running. We compare against opponents that react to the board (our team's submissions and policies), using paired games (same seed, same agent_index). We re-test any hit on new seeds and do not decide from interim results (a difference that looked like +6.4pp partway through shrank once all games finished).

## 9. Results

### 9.1 Effect of post-processing (across policy generations)

The policy kept changing until the last day, so we re-measured the same post-processing on new generations. Below are a mid-run generation (gen41) and the final submission's policy (gen70). The games ran on the Rust engine (§8.1) with the whole post-processing chain. The opponents were 7 of our team's policies, which react to the board: 4 submissions (sub121 to sub124) and 3 generations (gen32, gen34, gen35) of a teammate's run, with the same 128 seeds and both agent_index values for every arm (1,792 games per arm).

| Policy | Post-processing | W/D/L | Difference |
|---|---|---|---|
| Mid-run generation (gen41) | Wasted-move fixes + sells + collection plan | 1233/0/559 → 1319/1/472 | +4.8pp [+2.8, +6.9], +151 / −65 |
| Final submission (gen70) | Wasted-move fixes + sells + collection plan | 1330/0/462 → 1419/1/372 | +4.99pp [+3.04, +6.95], +145 / −56 |

Brackets are 95% intervals at the seed level. +n / −n counts the games that flipped from loss to win / from win to loss. Selling at the barn at hour 23 added only +0.1pp [−0.8, +1.1] for gen41 and +0.47pp [−0.17, +1.17] for gen70, too small to measure.

For gen70 we also added the remaining stages of the final submissions one at a time:

| Stages on top of the policy | W/D/L | Difference from the row above |
|---|---|---|
| None | 1330/0/462 | — |
| Wasted-move fixes + sells + collection plan | 1419/1/372 | +4.99pp [+3.04, +6.95], +145 / −56 |
| + selling at the barn at hour 23 | 1428/0/364 | +0.47pp [−0.17, +1.17], +17 / −9 |
| + MELON16 (= sub125) | 1574/0/218 | +8.15pp [+5.36, +10.94], +241 / −95 |
| + melon replanting (= sub126) | 1544/0/248 | −1.67pp [−4.07, +0.73], +117 / −147 |

All the post-processing of sub125 together raised the win rate from 74.2% to 87.8%: +13.62pp [+10.88, +16.41], +321 / −77, and it was positive against each of the 7 opponents (+5.5 to +25.4pp). Melon replanting did not help in this setting (coin difference −117 [−205, −29] per game against sub125), although it did in the setting of §7.1. This is why we submitted both versions.

### 9.2 Re-playing real LB games

Our local opponents were only our own submissions, so we also re-played real LB games. We took 91 real LB games of the 9/28 submission (3-plot style) and re-played them in the official Python environment. The opponent returned its recorded action sequence as-is, and the seeds and agent_index values were set as recorded.

- Without post-processing, both players' final money matched the real LB exactly in all 91 games (a check that the re-play is faithful).
- With the overflow and last-step sells added: wins 84 → 85 (+1 / −0). The coin difference went up in 79 games, down in 8, and stayed the same in 4 (mean +448).
- Caveat: an opponent that only plays its recorded moves reacts neither to our moves nor to price changes. Part of the difference (the opponent's money fell by 171 on average) may be smaller against an opponent that reacts.

## 10. What we expected to work but did not

We list the things we tried with real expectations that did not work, grouped by area. The numbers use the same measurements as §6–§9 (win rate in games, or coin difference in paired games with the same seeds).

**Strategy and training foundation**

| What we expected and tried | Result | What we learned |
|---|---|---|
| From-scratch PPO (no BC). It should become strong from self-play alone, as in shogi | Training collapsed | A game has 720 steps, and the path from early moves to a win is long. With only the final win/loss as the reward, the signal does not reach them |
| Playing from scratch with a hand-written algorithm (price formula + optimization) | The version without a script: win rate 0.000 in a league of 29 agents | Our own state tracking drifted from the official engine. The market shifts with how the opponent sells, which breaks a fixed plan |
| PPO over macro actions (correcting only the market layer of a scripted player; choosing 12 daily strategy values) | Money went up, but the win rate was 0.000. The policy's decisions barely changed | The actions were coarse and tied to the script. We switched to directly outputting primitive actions for all units (§5.1) |

**BC**

| What we expected and tried | Result | What we learned |
|---|---|---|
| A larger network (27.8M). Its loss is lower, so it should be stronger | Same strength (+604 ± 1,400 coins) | Held-out loss is not a proxy for strength. Choose by games |
| BC of a different style (Team C) as the PPO starting point | Failed the gate (0.284) | Starting from a strong teacher's BC is a prerequisite |
| BC only on 4-plot demonstrations | Reproduces the style, but 0.005 against the 3-plot version | Copying the style does not bring the strength |
| Re-running BC on new replays with a PPO-trained network | 0.198 against the original weights | The PPO strength is lost. To nudge the policy, use a small auxiliary loss only on the targeted positions |
| Distillation into the new legal-move mask | 0.301 against the teacher | — |

**PPO settings**

| What we expected and tried | Result | What we learned |
|---|---|---|
| Standard PPO (clipping the whole-step ratio) | Barely learns | The product of the 31 decision ratios quickly leaves the range. Clip per decision (§6.3) |
| Putting the critic on the same trunk as the policy | The value loss broke the policy | Keep the critic as a separate network |
| γ = 0.999 | Win/loss information reaches only 89 of the 720 steps | γ = 1. Measure EV against win/loss |
| Turning off the KL penalty (later runs) | 0.396 (z −5.9) | Turning it off helped in early runs, but the penalty is needed once the policy is strong |
| 2 epochs / EMA / model soup | Zero promotions / 0.517 / 0.39–0.44 | Stay with 1 epoch and a single set of weights |
| Minibatch 4,096 | 0.496–0.520 (no difference from 2,048) | — |
| Putting an opponent's new generations into the league right away | The league fills with opponents we cannot beat, and promotions stop | Swap them in after catching up (≥ 0.5 against them) |
| Virtual opponents that are BC clones of rivals | Weaker than the real teams; local win rates come out about 0.4 higher than in real games | Useful as a guide, but beating a virtual opponent does not mean beating the real team |

**Reward and interventions**

| What we expected and tried | Result | What we learned |
|---|---|---|
| Adding reward on steps that buy a plot | The critic broke (EV −4.86) | Keep the reward to win/loss only |
| Making the policy buy its 2nd plot earlier | 0.106 (−2,448) over 113 control pairs on the same games | PPO was right to refuse it |
| Adding moves quietly on the environment side (recording the original move) | 0.495 over 3,072 games, no effect | It does not reach the gradient. Record the rewritten move as the policy's move (§6.5) |
| Forcing a cow opening during training | KL 0.50 → 1.30; diverged, at 0.27–0.36 against the best version | Forcing moves the policy gives no probability to breaks it |
| Limiting spending (restricting market wheat and hiring) | 0.31–0.34 against a same-time control | — |

**Inference-time post-processing**

| What we expected and tried | Result | What we learned |
|---|---|---|
| Replacing PASS and moves that do not change the state with the best state-changing work | Coin difference −1,938 to −2,144 / game (640 games) | Changing unit moves dozens of times per game hurts the policy badly |
| Feeding and watering animals earlier | Coin difference −2,093 to −2,259 / game | Same as above |
| Selling early on days 3–9 | +2.3pp [−0.6, +5.3], not significant. −1.5pp when combined with the hour-23 barn sell | — |
| At hour 23, also selling the existing barn stock / selling without the price condition | Coin difference 0 to −128 / game; −614 | Sell only at or above the base price |
| Keeping units from going where they cannot get back from on the last day / market-side rules (late buying, hiring, land) | Almost never fired (0.02 times / game; 0 times) | — |

**Evaluation**

| What we expected and tried | Result | What we learned |
|---|---|---|
| Deciding from the public score, a single 384-game run, or money partway through the game | We decided not to use them for decisions | Decide with 1,536 games and z > 2 (the standard error over 768 games is about 0.018; §8.2) |
| Judging an A/B from interim results | A difference that looked like +6.4pp partway through shrank over all games | Jobs finish in opponent order, so interim numbers are biased |

**Common lessons**

- Decide by games against opponents that react to the board, not by losses or local metrics.
- Forcing moves from outside that the policy gives no probability to breaks it. Only narrow interventions, recorded as the policy's own moves, worked.
- Narrow rules that fix only moves that certainly have no effect work better than broad rules.

## 11. Contributions

- **denden**: the inference-time post-processing in both final submissions (wasted-move fixes, barn-overflow and last-step sells, the hour-23 barn sell, the last-day collection plan). The Rust game engine that matches the official engine transition by transition. Evaluation tools (paired-game A/B against opponents that react, re-playing real LB games, 50 opponents shared with the team).
- **masspeaks**: the BC and asynchronous PPO system (actors, learners, DDP across jobs), the league and the gate, maintenance of the C++ engine and the evaluator, the unified ladder, replay analysis, training-time interventions, and the post-processing `_pace`, MELON16 and melon replanting.
- **shimishige**: training of the final submission's run (gen21–70), `_land`. Collection and train/validation splitting of 106 public games from Team A's submission 56640167, and execution of two additional BC runs from the same Sub112 training checkpoint, comparing standard and frequency-weighted market-token losses.

## 12. Code and reproduction

- Repository: https://github.com/seven320/kaggriculture-3rd-place-solution
- Contents: the code of the final submissions (sub125, sub126), the post-processing modules with their tests, the Rust engine, masspeaks' BC / PPO kit with the C++ engine, and the evaluation harness with the protocol of §9.1.
- Weights: the final policy (gen70) and the BC starting point (sub112) are distributed as a Kaggle Dataset, with sha256 in the repository.
- License: CC-BY 4.0 (rule 5). Parts derived from kaggle-environments (the bundled functions of the official `kaggriculture.py`, and the game rules ported to the Rust engine) and from nikital7's public notebook (the C++ engine) are under Apache-2.0, listed in NOTICE.