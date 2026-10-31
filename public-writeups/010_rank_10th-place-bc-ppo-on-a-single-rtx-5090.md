> **来源 / Source**：Kaggle Kaggriculture 公开 write-up，第 10 名，队伍 **KawattaTaido**。
> **原文**：https://www.kaggle.com/competitions/kaggriculture/writeups/10th-place-bc-ppo-on-a-single-rtx-5090
> 本文为比赛归档的离线副本，仅作技术参考；**版权归原作者所有**。
> 如作者要求撤下，请联系仓库所有者。

# 10th place: BC + PPO on a Single RTX 5090

Code, weights and reproduction instructions: https://github.com/KawattaTaido/kaggriculture-release (CC BY 4.0).

Thank you to the organizers for hosting this competition.

## 1. Summary

The agent is **one policy network** (21.8M parameters, JAX/Flax), with no search and no
hand-written planner. It is trained in two steps:

1. **Behavior cloning (BC)** on the most recent leaderboard games: 2,380 episodes from
   the last four days before the final submission, using both seats.
2. **PPO** (≈370M environment steps, ≈19 h on one RTX 5090). In half of the games the
   agent plays itself. In the other half it plays one opponent from a small pool: two
   past generations of itself, or a **recording of a real LB agent** replayed move by move.

Three things mattered most:

- **The action representation follows the game.** Each worker unit *points at a target
  tile*, and the market head outputs *a quantity per item*.
- **The strength of the BC starting point, driven by fresh LB data.** A new day of LB
  games was released every morning, and rebuilding the BC teachers from the latest days
  made the model stronger almost every time. Imitating top agents was the cheapest large gain (Section 4).
- **Model size.** Making the network wider kept improving the results; the last two
  widenings took it to 11.96M and then 21.83M parameters. The gain does not show in BC;
  it shows only after PPO (Section 4).

At a glance:

- **Most important inputs**: the own-farm map with plant and animal states, market
  prices, stocks and price impact, the money and stock of both players, and estimates of
  the opponent's hidden barn and of when the opponent will deliver.
- **Tools**:
  - JAX / Flax / Optax for the network and PPO; a JAX port of the environment runs all
    PPO rollouts on the GPU.
  - Rust (PyO3) for the game rules, legal-action masks and observation features. The
    same compiled extension is used in training and in the submission.
  - `kaggle-environments` as the reference implementation.
- **Training time** (one RTX 5090): ≈23 h from the release of the last day of LB data to the
  final weights; ≈3.5 h for the data and BC, ≈19 h for PPO.
- **Inference**: ≈18 ms per turn locally, greedy (argmax) decoding. No ensemble.

---

## 2. Features selection / engineering

The input is not a feature table but the game state, encoded into three tensors
(specification v12). Every feature is computed in Rust; a JAX implementation is checked
against it bit by bit, and replays of LB games verify both.

| Input | Shape | Content |
|---|---|---|
| map | 65 × 10 × 10 | own farm: tile type, crop, plant state (water, fertilizer, turns to maturity, expected yield), animal state, unit occupancy, **number of harvests left in the season** |
| global | 312 | time and phase one-hots, money, seeds, barn and carried stock, market prices / stocks / price impact, town demand, labor, land, recent history, expected supply, **estimated opponent stock and delivery timing**, stock in hand + barn |
| units | 24 × 25 (+ mask) | per worker: position, carried items, distance to the barn, … |

Most important, judged by what changed results when added or removed:

1. **Market state and price impact.** Selling moves the price; both players share one
   market, and the town buys only a fixed amount (≈206k per game in total over all
   items).
2. **Opponent estimates.** The opponent's barn is not observable, so its stock is
   estimated from public information (purchases, harvests, sales), together with when it
   will deliver. An auxiliary head that predicts the opponent's sales 1 and 24 turns ahead
   (loss weight 0.05) trains the same representation.
3. **Plant state, including the harvests left in the season.** Continuing crops
   (strawberry, tomato) are worth more when several harvests remain.

Feature selection and transformations:

- Features were added one hypothesis at a time and kept only if BC *and* PPO improved,
  judged by paired comparisons on the same boards.
- A map of the opponent's farm was removed (no effect). Two later specifications were not
  adopted because they lost after PPO (Section 4).

**External data**: none apart from the LB replays published through the Kaggle API (the
competition's own episodes).

## 3. Training methods

No ensembling; one network.

![Training pipeline](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F7165289%2F3ee28dc56624a1f1bdfd64dea415ddf9%2Ffig1_pipeline.png?generation=1792394221064026&alt=media)

*Figure 1. Training pipeline. LB replays feed both behavior cloning and the "tape" slot of
the PPO opponent pool. Every 210 PPO iterations the KL teacher is replaced by the current
weights, and the current weights join the opponent pool.*

### Network (Figure 2)

![Network](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F7165289%2F2ba5ce5f90a94b94620696dc53fdea9c%2Ffig2_network.png?generation=1792394204575262&alt=media)

*Figure 2. Network. The own-farm map is encoded by a ResNet and self-attention, the global
vector by an MLP, and the worker units attend to the board. Three heads produce unit
actions, market orders and value/auxiliary predictions. Every factor of every action is
masked by legal-action masks computed in Rust.*

| Part | Details |
|---|---|
| Map encoder | ResNet, 6 blocks, 96 channels, GroupNorm; FiLM conditioning on the global vector; 2 self-attention layers over the 100 tiles |
| Global encoder | MLP, hidden 512 → g (1024) |
| Unit encoder | 2 cross-attention layers from units to tiles, with a relative-position bias, then unit self-attention |
| **Unit head (pointer)** | per unit, autoregressive: operation, **target tile** (logit = query·tile key + learned function of distance / dx / dy / reservations of earlier units), argument, quantity. A unit on its target performs the operation; otherwise it moves one step along a fixed path. Targets are re-chosen every turn. A tile and operation already reserved by an earlier unit is masked, so units never duplicate work. |
| **Market head** | a turn's market action is a *quantity per item* (21 factors, 352 logits), decoded autoregressively in execution order by a 2-layer transformer over 14 item tokens. Budget and order-slot limits are tracked while decoding, so every sampled action is legal. The orders are then placed into the 10 order slots by a fixed rule: sells of items the opponent also holds come first, largest expected price drop first, because the environment processes the two players' slots alternately and earlier slots sell at higher prices. |
| Value / auxiliary | value head (final money difference), auxiliary heads (final money, win probability, opponent sales) |
| Size | 21.83M parameters; compute in bfloat16 |

**Legal-action masks** are computed in Rust and applied to every factor. Besides the
rules, they remove actions that are provably wasteful:

- market orders that are certainly loss-making or cannot fill;
- digging up a plant before harvest (continuing crops excepted);
- fertilizer that does not raise the yield;
- planting that cannot mature before the season ends;
- care on the last day;
- dropping items into a full barn.

Each mask was checked by replaying LB games, so it does not remove moves that top agents
actually play.

### Behavior cloning

- **Teachers**: 2,380 LB games of 2026-09-26..29 in which both players had a rating of at
  least 2,800, both seats (3.4M samples; 1,891 games for training, 489 held out).
- **Labels**: LB actions are projected onto the network's action representation (target
  tile for units, quantity per item for the market). A sell and a buy of the same item in
  the same turn are netted, and sells are budgeted against the barn *after* the unit
  actions of the turn.
- **Training**: 60k steps, batch 512, Adam with lr 3e-4 and a cosine schedule, gradient
  clip 1.0, auxiliary opponent-sales loss 0.05. Hold-out NLL 5.35 per sample (retrained model in the repository; the original BC checkpoint was lost).

### PPO

| Setting | Value |
|---|---|
| Environment | JAX port, 64 games in parallel, whole 720-turn game in `lax.scan` on the GPU |
| Reward | final money difference / 30,000, terminal only; γ = λ = 1 |
| Update | clip 0.2, 2 epochs, 16 minibatches, entropy 0.02, value 0.5, auxiliary 0.1, grad norm 0.5, early stop on KL (0.003) |
| Learning rate | stage 1: 5e-5 for 420 iterations; stage 2: **1e-5** for 3,570 iterations |
| Kickstarting | KL to a teacher policy, coefficient 1.0. The teacher starts as the BC model and is **replaced by the current weights every 210 iterations** ("segments"). |
| Opponents | 50% self-play; 50% one of a pool of 3: two past generations (pushed every 210 iterations) and one **LB tape** |
| TV guard | after each update, if the 90th percentile over games of the change in action probabilities (total variation) at any turn exceeds 0.5, the update is shrunk to ½ or ¼ |

**LB tape opponent.** One pool slot replays a recorded LB agent. The recordings come from
800 games: 657 LB games of 2026-09-25..28 (both ratings ≥ 2,800) and 143 LB games that our earlier submissions lost. A
recording is open-loop, so two things are aligned with the original game:

- **Randomness.** The tape seat's random events (weeds, the shop unlock order) follow the
  recording.
- **Market fills.** For every order of the recorded player, the number of units that
  filled on the LB is precomputed. The replay stops at that number, and missing money is
  lent and subtracted at the end.

Without this alignment, a difference of a few coins on day 0 makes the tape's first
purchases fail, and in about 30% of games the opponent collapses. Opponents are sampled
per team, and teams that are harder to beat are drawn more often.

![Learning curves](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F7165289%2F5596bdf5d645902108cbc45081892351%2Ffig3_curves.png?generation=1792394254023811&alt=media)

*Figure 3. During PPO training, the win rate against the recorded LB agents (the tape
slot of the pool) rose from 0.53 to ≈0.88.*

## 4. Interesting findings

**What mattered most**

1. **Fresh BC teachers.** A new day of LB games was released every morning, and rebuilding
   the BC teachers from the latest four days made the model stronger almost every time.
   This was the cheapest large gain. On one model
   generation it raised the win rate against a strong public rule-based agent from 0.835
   to 0.993.
2. **An action representation that matches the game**: pointing at tiles instead of
   choosing move directions, quantities per item instead of a fixed list of order slots,
   and sell budgets counted on the real barn.
3. **Model size, which shows up in PPO, not in BC.** Every widening of the network improved
   the final result. Wider fully connected layers barely changed the BC hold-out NLL
   (−0.04) and lost BC-vs-BC games. At the same PPO step count, however, they raised the
   win rate against tapes from 0.454 to 0.589.
4. **Realistic recorded opponents.** Self-play alone never meets some LB behaviors, such
   as selling in the same turn as a delivery or replanting late. The tapes only helped
   once randomness and fills were aligned (Section 3).
5. **A low learning rate for long PPO runs.** At 5e-5 the run stopped improving after
   about 40M steps. Restarting at 1e-5:
   - lowered the clipped fraction from 0.26 to 0.09;
   - gained +355 money against held-out LB tapes in two seeds;
   - won head-to-head (0.56 and 0.69);
   - kept improving for the remaining 3,500 iterations (Figure 3).
6. **Guarding against "opening flips".** A single ordinary-sized update sometimes flipped
   the near-deterministic opening purchases (for example buying 3 geese on turn 1). Each
   flip sent the policy into another strategy. A KL measured on sampled actions cannot
   see this (≈3e-5 on average). The per-turn TV guard removed all such spikes in a
   verification run, at a cost of +9% time per iteration.

**Relationships in the game**

- **Fixed demand.** The town buys a fixed amount per game (≈206k in total), and the two
  players' sales nearly saturate it, so taking the opponent's share is the shortest way
  to win.
- **Shared market.** When our money rose by 1,000, the opponent's rose by 690–790, through
  the shared market. Maximizing our own money and maximizing the win rate are therefore
  different objectives. The PPO reward is the money *difference*.
- **One loss-making action.** A single legal but certainly loss-making action (for
  example an animal that cannot pay back before the end) is enough to make PPO suppress
  all spending, including planting. Masking provable losses was a prerequisite for
  learning.

**Tried and not adopted** (each lost in paired evaluation):

- day-level planners and solvers for the workforce (timed out on Kaggle or lost
  head-to-head);
- local search over the policy's actions;
- a calendar one-hot plus "next land" features, and opponent-unit cross-attention (both
  better in BC, both worse after PPO);
- a weaker kickstart (0.3);

## 5. Simple features and methods

- **Simplest useful model**: the BC model alone, with the same network and inputs and
  no PPO. It already plays a complete, sensible economy because it imitates recent top
  LB agents, and it needs no long training (≈3.5 h on an RTX 5090, data preparation included).
- **Most important step**: PPO starting from BC. Figure 3 shows the gain against recorded
  LB agents during training. Most of the improvement comes in the first ≈2,000
  iterations (≈10 h on an RTX 5090).
- **Smaller input subsets** were not evaluated systematically. The input is the encoded
  game state rather than a hand-made feature table, so it does not reduce to a short list
  of features.

## 6. Model execution time

| | Time |
|---|---|
| LB data download, BC dataset and BC training (60k steps) | ≈3.5 h |
| PPO stage 1 (420 iterations) | ≈2.2 h |
| PPO stage 2 (3,570 iterations) | ≈17 h |
| Total | ≈23 h on one RTX 5090 (≈17 s per PPO iteration) |
| Prediction | ≈18 ms per turn locally; about 35 ms per turn and ≈35 s for the first turn (JIT compilation) on Kaggle's runtime, measured on an earlier submission. A game has 720 turns. |
| Simplified model (BC only) | training ≈3.5 h; prediction as above |