# 9th: From Reinforcement Learning to a Final BC Agent

First, I'd like to thank my teammates, **tetsuya** and **guoqin gu**. It was a pleasure taking part in this competition together. Thanks also to the hosts and everyone who shared strategies and experiences in the discussions.

# Overview

Our final agent is an **18.4M-parameter Transformer + CNN policy** trained by behavior cloning on strong game replays. It directly predicts worker commands and market orders, using EMA weights and single-model argmax decoding.

| Final agent | At a glance |
| --- | --- |
| Policy | 18.4M parameters · Transformer + farm CNN |
| Learning | Behavior cloning · EMA weights |
| Final replay mixture | 70% MMPQ · 30% other sources |
| Inference | Single model · FP32 · argmax · CPU AOT |

Development began with RL and later shifted toward BC as the replay pipeline and model improved. The sections below describe the training setup, the development timeline and the final agent.

# Training pipeline

The final submission uses behavior cloning with normalized replay targets, weighted source sampling and auxiliary objectives. A later PPO branch starts from a BC actor and continues training through interaction with opponents.

![Training and final submission](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F4578277%2Fa380982c9ad5e3395e77b874adafa616%2F01-training-pipeline.png?generation=1792304458543618&alt=media)

*Figure 1. The final BC submission pipeline and our later direct-action PPO branch. Our early RL exploration preceded this final setup.*

Three design choices were central to the final agent:

- **Requested actions and executed actions can differ.** We reconstructed execution effects before building BC targets.

- **Decisions within a turn depend on one another.** Workers and market orders are decoded in execution order, with later decisions seeing the resource changes caused by earlier ones.

- **A single observation does not describe the market process.** We added history statistics at multiple timescales, together with economic and forecasting objectives.

## Behavior cloning: replay data and action labels

Competition replays are converted into player-side trajectories containing observations, history and actions. The final fine-tuning corpus contains 4,996 trajectories from 38 submissions, or approximately 3.59 million action time steps.

**Replay requests can differ from executed actions.** A worker may request more items than remain available, a market order may receive no fill, or a command may have no effect. Cloning these requests directly can leave the action targets inconsistent with subsequent state changes.

Our preprocessing reconstructs execution: ineffective worker commands become PASS, quantities are corrected, unfilled market orders become NOOP, and sales can use SELL ALL. BC imitates this normalized command sequence.

## Mixing replay sources

BC starts with pretraining on high-scoring replays, followed by adjustments to replay sources and sampling weights. The final branch continues from an earlier BC checkpoint with a 70:30 mixture of MMPQ and other replays.

The corpus contains 1,165 MMPQ trajectories and 3,831 from other sources. The 70% sampling share deliberately emphasizes a relatively consistent group of strategies while retaining behavior from other sources.

## Training objectives

Action imitation is combined with economic and forecasting objectives. Economic targets cover labor, land, cash, cash margin, stock and field service. Forecast targets describe subsequent market and economic changes in the replay, giving the shared encoder supervision beyond the next action.

The total loss is:

```text
L = 2 * worker NLL + market NLL
    + economic loss + 0.05 * forecast loss
```

Future replay frames are used to construct targets only. During play, the policy consumes current legal observations and the history maintained so far.

Compressed trajectory pools and rotating sampling keep random reads and memory use manageable.

## Reinforcement learning: BC initialization and PPO

The later direct-action RL implementation initializes the actor from BC and uses PPO to continue learning against a mixture of opponents. This branch is distinct from the early RL experiments that motivated the initial approach.

A vectorized JAX simulator collects on-policy data, with 512 games per rollout wave across four GPUs. Early experiments mainly used self-play. The later opponent mixture has five approximately equal groups: self-play and four groups of frozen neural opponents.

The later reward emphasizes terminal win/loss and adds a cash-margin signal. With margin m and s(m)=tanh(m/100000):

```text
r = 0.25 * (s(m_next) - s(m_now))
    + terminal * (sign(m_next) + 0.25 * s(m_next))
```

PPO uses gamma 0.995, GAE lambda 0.95, ratio clipping to [0.8, 1.2] and normalized advantages. The actor learning rate is 1e-6; the independent critic uses 3e-4. Policy sampling and PPO likelihood evaluation both use temperature 0.5.

Two parts received particular attention. The first was **critic initialization**: after changing the reward, we held the actor fixed and fitted returns from complete games, holding out whole games for validation. The second was **controlling policy movement**: after each proposed update, we checked KL on both the update minibatch and a fixed reference minibatch from that rollout, reverting proposals that exceeded the limits.

# Training history

![Competition timeline](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F4578277%2Fb12e5348574f11e23200e55425afde2f%2F04-competition-timeline.png?generation=1792304533221100&alt=media)

*Figure 2. Four milestones in our competition. The final BC model came from a continuation run in the last two or three hours.*

## RL exploration and scaling

Early experiments established that RL was viable in this environment. Once the training pipeline was working, further development focused on improving the policy and scaling training.

![Exploring reinforcement learning on the farm](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F4578277%2F9279f19009846c68ae559c1f421a1185%2F05-cartoon-rl-exploration.png?generation=1792304553142539&alt=media)

*Learning through trial and error. A conceptual illustration of our early RL exploration.*

Scaling produced substantial improvements, but issues in the JAX implementation and model design slowed iteration. Limited experience with these parts of the system contributed to longer debugging cycles and made scaling less effective than expected.

## Shift toward BC

Strong BC agents from other teams prompted a renewed focus on imitation learning during the final week. The last three days of development concentrated on correcting weaknesses in the BC training pipeline, followed by changes to the policy model.

In local testing, the revised BC models substantially outperformed the RL models available at that stage. Further RL training was also tested, but improvements arrived more slowly, so the remaining development focused on BC.

A further BC continuation ran during the final two or three hours before the deadline. Local testing identified its step197129 EMA checkpoint as the strongest candidate available at that point, and it was selected for submission.

![One final late-night behavior-cloning run](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F4578277%2F9625ee0eac04047b37530bde1396dae9%2F06-cartoon-final-bc.png?generation=1792304567545760&alt=media)

*Learning from replays, with one last experiment near the deadline. A conceptual illustration of the final BC run.*

# Architecture and inference

![Policy architecture](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F4578277%2F058cc7db907b61fa16651a37e6a44cce%2F02-policy-architecture.png?generation=1792304502912275&alt=media)

*Figure 3. Main policy pathways. History and spatial features condition the entity representation; the resource ledger connects worker and market decoding.*

## Entity Transformer and farm CNN

The state is represented as entity tokens: a global state, workers, tiles, shops, commodities and project features. Attention connects these entities, including relationships between workers and tiles, production and inventory, and the player's farm and the shared market.

The backbone has two interaction rounds. Each round processes worker and field tokens in separate branches before shared attention exchanges information. A residual 5×5 CNN additionally processes our own 10×10 farm. The opponent's public farm participates through entity features.

| Component | Final configuration |
| --- | --- |
| Parameters | 18,425,190 |
| Transformer width | 288 |
| Feed-forward width | 224 |
| Attention heads | 4 |
| Entity-branch and shared-attention rounds | 2 |
| Own-farm CNN | Two 5×5 convolutions, 63→224→960 channels, projected to width 288 |

History is represented by rolling means and lagged differences, with windows of 6, 24, 72, 168, 360 and 719 turns. These statistics can be updated incrementally during play and cached during preprocessing, allowing BC to sample random time steps without unrolling an entire game.

## Sequential action decoding

Worker actions are factorized into direction, local operation, argument and quantity. During autonomous play, commands are generated in worker execution order, updating the resource ledger after each one. Items taken by an earlier worker therefore change the inventory context available to the next worker.

![Workers share a changing inventory](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F4578277%2F042d22630cbdc94601d124f301d994f1%2F07-cartoon-sequential-actions.png?generation=1792304581111238&alt=media)

*Earlier actions change what remains available. A conceptual illustration of the resource ledger used in sequential decoding.*

During BC training, causal prefixes are precomputed from demonstrated actions. Worker losses can then be evaluated in parallel while preserving within-turn dependencies.

The market decoder similarly generates up to ten ordered slots, conditioning each one on the prefix updated by earlier orders. Quantities support numeric values and SELL ALL. The final policy emits commands directly, without an additional state-dependent legality mask.

## CPU deployment

Inference uses one model, FP32 weights and conditional-head argmax. To fit the competition's CPU runtime, we compiled the initial forward pass, subsequent forward pass and history update ahead of time for Broadwell CPUs.

We also fixed persistent inventory insertion order in the deployment adapter. This affects which items survive DROP when shed capacity is insufficient, and therefore changes later states. We maintain the order from consecutive observations so deployment follows the execution semantics used in training. The final package passed a complete-season raw-source execution check.

# Evaluation and checkpoint selection

Local evaluation uses fixed historical BC agents as opponents. Each comparison contains 512 seeds, with both seats played on every seed, for 1,024 games per pairing. Deterministic argmax matches submission-time decoding.

The final step197129 EMA achieved the following results. Draws are not counted as wins, and cash margin is our terminal cash minus the opponent's.

![Offline evaluation](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F4578277%2Fe36aedac60433fda91e2427739017d1a%2F03-offline-evaluation.png?generation=1792304518599267&alt=media)

*Figure 4. Strict win rates and mean terminal cash margins against five historical BC opponents. Each pairing contains 1,024 games with both seats on every seed.*

| Opponent | W / L / D | Win rate | Mean cash margin |
| --- | ---: | ---: | ---: |
| Earlier BC 0.40 | 944 / 80 / 0 | 92.19% | +4,935 |
| Split2 BC 0.45 | 900 / 124 / 0 | 87.89% | +3,770 |
| Double BC 0.25 | 876 / 148 / 0 | 85.55% | +3,623 |
| Stage14 BC 0.25 | 861 / 163 / 0 | 84.08% | +3,338 |
| 37.3M BC step41000 | 781 / 243 / 0 | 76.27% | +2,301 |

These results are from our local JAX simulator against the fixed historical panel used for checkpoint comparison.

## Final checkpoint selection

Our final checkpoint is the stage 3 EMA at step197129, saved when the mean of the last twenty raw-model total training losses reached approximately 0.50. Training later continued to step202752, but the later checkpoint did not improve every matchup. Across four common opponents, the two checkpoints won 3,581 and 3,579 games respectively, with different strengths by opponent.

Checkpoint selection considered complete-game performance alongside BC loss. The loss measures fit to demonstrations; local matches test behavior over a full season. These comparisons do not isolate the effects of model size, training data or optimization.

Submission remained uncertain: a comparable model had not yet been tested on the leaderboard, and an earlier submission had failed to generalize due to overfitting. This checkpoint was submitted once and became the team's highest-scoring submission.

# Discussion and future work

**Iteration speed.** Scaling improved the models, but implementation and architecture issues limited experiment throughput. Faster validation and more reliable training code would have made successive changes easier to assess.

**Data quality starts with execution semantics.** In a sequential environment, action names and requested quantities do not fully describe a sample. Within-turn resource changes, partial fills and ineffective commands all belong in the data pipeline.

**Replay distribution and the BC-to-RL transition.** Further work would compare teacher consistency, behavioral diversity and sampling weights, then examine critic pretraining, opponent selection and policy-update stability under matched training and evaluation conditions.

# Acknowledgements

Thanks again to **tetsuya** and **guoqin gu** for sharing this competition journey. Thanks to the hosts for the environment and replay access, and to the competitors who shared strategies, code and discussions. Strong replays provided the foundation for our final BC agent, and the community's work helped us throughout the competition.