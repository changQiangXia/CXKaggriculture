> **来源 / Source**：Kaggle Kaggriculture 公开 write-up，第 51 名，队伍 **Driz Lo**。
> **原文**：https://www.kaggle.com/competitions/kaggriculture/writeups/51st-place-solution-replay-bc
> 本文为比赛归档的离线副本，仅作技术参考；**版权归原作者所有**。
> 如作者要求撤下，请联系仓库所有者。

# 51st Place Solution: Replay BC

A good farm layout is only the beginning of a Kaggriculture strategy. Animals need feed, harvests need transport, workers need to arrive at the right time, and products need to reach the market. A policy can make a sensible choice at every individual station and still fail to run the farm as a whole.

Our approach is to learn that complete policy from replays. A single **22.4-million-parameter network** predicts the farmer's command, the hired workers' commands, and an ordered list of market instructions. The released agent uses supervised behavior cloning, with a small final-turn liquidation rule. It does not choose among hand-written farming plans.

The central design separates three kinds of coordination: **memory across turns, attention between workers, and sequential decoding between market orders**. This article explains why those mechanisms are useful, how to construct their training problem, and how to turn the trained network into an agent. The [companion repository](https://github.com/zhuzhirui2005/Kaggriculture-Replay-Agent) includes the pretrained checkpoint and the data, training, and inference code.

## A policy that remembers and coordinates

Imagine a worker arriving at storage. Is it finishing a harvest delivery, starting a feeding trip, or collecting an animal for a new pasture? Position alone cannot answer that question. Inventory and the previous command help, but a multi-turn job may need more context.

Now imagine two workers standing on different empty tiles, both ready to plant wheat. Each action looks reasonable in isolation. If the farm has only one wheat seed, the pair cannot both succeed.

These are different problems. The first calls for a representation of the recent trajectory; the second calls for communication and shared-resource accounting. Treating them separately makes the architecture easier to reason about.

![Visible state passes through an encoder, daily recurrent memory and same-turn worker attention, then branches into worker commands and sequential market orders.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F35931910%2F36cba2f640dcd008ed4cfafb856cdef1%2Fpolicy-coordination.png?generation=1792395561188004&alt=media)
*Figure 1. Three kinds of coordination. GRUs carry information across turns; attention exchanges information within the current turn; a separate GRU generates market orders in sequence. The farming illustrations are schematic.*

### Encode both the local job and the whole economy

The input has a spatial part and an economic part. A **52 × 10 × 10** tensor represents both publicly visible farms in own-player-first order, including tile states, crops, animals, worker occupancy, and coordinates. A **114-dimensional** feature vector describes time, finances, expansion, shop availability, market prices and stocks, observed market changes, and our private inventory. Large counts use scaled inverse-hyperbolic-sine transforms so that small quantities remain distinguishable.

A residual CNN encodes the board. One path summarizes it into a farm-wide context; another gathers the encoded cell beneath each worker. Worker features then add inventory, a within-day slot embedding, and the previous command and quantity. Previous market instructions also contribute to the shared context through pooled embeddings.

This representation exposes the opponent's public production without exposing their private storage. Future shop unlocks and hidden world information are not inputs.

### Remember a day's work, then coordinate the current turn

A shared GRU carries farm-wide history, while a shared-parameter GRU maintains a separate state for each worker. Both use 256-dimensional hidden states and reset at day boundaries, matching the replacement of hired workers. This gives the model capacity to learn task continuity without requiring an explicit task queue.

Two attention layers then operate on the current context token and worker tokens. They let a worker's representation incorporate what other workers are positioned to do. Absent workers are masked. This is **same-turn attention**, not attention over future replay frames.

| Component                         | Released configuration                                       |
| --------------------------------- | ------------------------------------------------------------ |
| Board encoder                     | 192 channels, three residual convolutional blocks            |
| Shared and worker representations | 768 dimensions; up to 32 actors including the farmer         |
| Daily recurrent memory            | Shared and per-worker GRUs, each with 256 hidden units       |
| Worker attention                  | Two layers, four heads, 1,536-dimensional feedforward layers |
| Market decoder                    | 768-dimensional GRU; at most ten orders                      |

### Give different demonstrations a consistent policy mode

Replays contain different, sometimes incompatible ways to play. One demonstrator may commit labor to animals where another would expand crop production. Asking an unconditional model to imitate both can leave the decision ambiguous.

A learned **style embedding** provides a condition on our own policy. The same network shares spatial, economic, and execution knowledge across styles, while the embedding distinguishes their behavior. At inference, one style is fixed for the entire game; the published default is named `default`. It is not an opponent classifier, and the agent does not switch styles in response to a guessed opponent identity.

## Turn predictions into a structured action

Rather than flattening an entire turn into one enormous category, the model decomposes it into commands, quantities, and an ordered market sequence.

Workers have **44 command tokens**. Crop or item identity is part of the relevant command token, and a command-conditioned head predicts quantities from 0 to 100 where applicable. This avoids asking an independent quantity head to choose a number before knowing what operation it belongs to.

Local masks remove obviously infeasible choices, but must respect the environment's execution order. For example, an earlier worker may build a pasture before a later worker places an animal there. Rejecting placement solely because there was no pasture at the start of the turn would remove a valid collaboration.

Shared seeds need an additional mechanism. Worker scores are computed together, but planting choices are resolved in execution order. Selecting a planting command consumes that crop's quota; later workers can no longer select it once the quota is exhausted. This is a limited, explicit resource constraint—not a fully autoregressive worker policy or a general joint-action planner.

![Two workers compete for one wheat seed; separately, a recurrent market decoder produces a sale, a purchase and an end token.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F35931910%2F5f869e7d08cbe989bf4932bd1b1082ea%2Fone-turn-decoding.png?generation=1792395649212967&alt=media)
*Figure 2. Two independent examples. A shared seed quota prevents duplicate consumption; an ordered market decoder represents dependencies between instructions. The examples illustrate decoding, not a recorded game.*

Market instructions form a different sequence. A **23-token vocabulary** covers supported purchases, sales, hiring, expansion, and an end marker. Starting from the shared context after attention, a GRU generates each order and its quantity, then conditions the next order on that choice. A sale followed by a purchase is therefore distinguishable from an unordered pair of intentions.

Training uses the demonstrated market prefix; deployment feeds back the model's own chosen prefix and uses greedy decoding. The worker and market branches share representations, but the market decoder does not explicitly receive the worker commands just selected for that turn.

## Make replays into the right learning problem

The most important preprocessing detail is easy to miss: **the action stored in replay record `t + 1` belongs with observation `t`**. It is the command that led out of the current observation, not an instruction chosen after seeing the next state. An off-by-one error can still produce a falling loss while teaching the wrong mapping.

For each selected player, the processor merges the public observation with that player's private observation and constructs the action target. The targets imitate submitted commands rather than reconstructing every action the engine ultimately executed. Known infeasible labels are excluded. In particular, when a demonstrated turn requests more planting of a crop than the available seeds allow, its planting labels for that crop are excluded rather than teaching the conflict.

Whole episodes are assigned to train, validation, or test **before** sampling sequences. Both seats stay in the same partition: the two perspectives of one game are not independent examples. The implementation uses a stable episode-ID hash for an approximately 80/10/10 split.

![Whole-game data splits and two separate lanes distinguish decision-time observations from action, intent and return supervision.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F35931910%2F27182921f793e7caed1192d1982a4655%2Freplay-supervision.png?generation=1792395835557790&alt=media)
*Figure 3. Future replay information can provide training targets without becoming a policy input. Record alignment and episode-level splitting are part of the learning problem, not just file handling.*

Training samples 24-frame days, initializes recurrent memory to zero, and backpropagates through the day's sequence. The final short day is padded, with padded action and intent labels ignored. Compressed per-seat arrays provide a portable intermediate format; read-only memory-mapped caches avoid repeatedly decompressing trajectories during training.

### Teach what a route is for

An action label such as `EAST` says little about the job behind the movement. Consider a route that goes east, east, north, then feeds an animal. In addition to predicting the immediate command, auxiliary heads learn the destination cell and the work command the route is leading toward.

The target is the nearest non-movement, non-pass action within the current-to-next-twelve-turn window, without crossing a day boundary. These intent labels come from replay supervision. At inference, they are not fed into a separate path planner.

A scalar auxiliary head predicts the remaining change in cash margin, scaled by 10,000, plus twice the sign of the final margin. It supplies another training signal about the trajectory's outcome; deployment does not use it for action search.

The combined objective is:

```text
L = L_worker + 0.5 L_worker_quantity
  + L_market + 0.5 L_market_quantity
  + 0.2 L_goal_cell + 0.2 L_goal_command
  + 0.1 L_return
```

Action and intent terms use cross-entropy; the return term uses Smooth L1. Worker `PASS` receives weight 0.5, while planting, building, placement, pickup, and digging receive weight 2. Other worker commands receive weight 1. Missing actors, inapplicable quantities, and excluded labels do not contribute to their respective losses.

### Avoid depending on perfect demonstration history

During training, the preceding commands usually come from a demonstrator. During play, they come from the model itself. That difference matters as soon as the learner makes a mistake.

We randomly erase 15% of previous worker command/quantity pairs. Previous market histories are erased as whole prefixes with the same probability. The current observation and target action remain unchanged. The intended effect is to make action history useful without making a clean teacher prefix indispensable.

This does not solve the full distribution-shift problem: erasing history does not create the new board states caused by the learner's errors. Full-game testing remains necessary.

## A practical training recipe

The training code supports both learning from scratch and continuing from the released checkpoint. Continuation can mix new demonstrations with older rehearsal data, with a default 70/30 ratio when both are present. New styles are sampled uniformly before choosing a trajectory and a day, so a prolific source does not dominate simply by supplying more replay files.

| Setting                 | Reference recipe                             |
| ----------------------- | -------------------------------------------- |
| Optimizer               | AdamW, weight decay `1e-4`                   |
| Learning rate           | `1e-4` from scratch; `1e-5` for continuation |
| Sequence unit           | One 24-frame day                             |
| Gradient norm clipping  | 1                                            |
| CUDA precision          | bfloat16 forward computation                 |
| History erasure         | 15%                                          |
| New / rehearsal mixture | 70% / 30%, when both groups are available    |

These are reproducible starting settings, not a claim that each is independently optimal.

The implementation batches board encoding across frames, advances recurrent states chronologically, then batches same-turn attention and action heads. Read-only memory mapping lets training processes share prepared data without loading separate copies into RAM.

For multi-GPU training, each process receives a slice of the global day batch. Loss normalization uses globally summed target weights: class weights for worker commands, and valid-label counts for unweighted heads. Because worker counts and applicable quantities vary, averaging each GPU's local mean would give sparse and dense batches the wrong relative influence.

The short reproduction path is:

1. Prepare complete replays with stable episode IDs, selected seats, and consistent style labels using `tools.data prepare`.
2. Build memory-mapped arrays with `tools.data cache`.
3. Train with `tools.train`, optionally warm-starting from `weights/model.pt`; use `torchrun` for distributed training.
4. Test frozen checkpoints in complete games, then build the runtime archive with `tools.package`.

The repository README gives the commands and manifest format.

## Deploy the policy you actually evaluate

The runtime loads one checkpoint, fixes one style, carries daily memory, and decodes greedily on CPU. Its history records the actions actually returned to the environment. Repeated calls on the same observation do not advance recurrent memory twice. Training utilities and replay data are not part of the submission package.

One narrow economic rule remains outside the network: **final-turn liquidation**. On the last actionable turn, it projects the immediate effects of our worker commands, then adds or extends sales of products available in storage. Already requested sales and the market-order limit are respected. The original worker commands are unchanged.

This addresses a finite-horizon mismatch: inventory useful for tomorrow has no production value when there is no tomorrow. The rule does not intervene in ordinary production, sell goods that remain in a worker's hands, or replace earlier plans. With scarce order slots, it uses current price times quantity to prioritize remaining products, rather than searching for an optimal final transaction sequence.

The model and this rule must be evaluated together. Adding a postprocessor after measuring a checkpoint means deploying a different policy.

## What to take away

Replay prediction and competitive strength answer different questions. Held-out loss can reveal alignment errors, missing features, or difficult action classes. Complete games reveal whether individually plausible decisions form a working farm. Use fresh worlds and both seats, prioritize win rate, keep ties visible, and inspect repeated failure patterns rather than choosing a model on a few extreme score margins.

Behavior cloning also has a ceiling: it approximates observed decisions, encounters states absent from its demonstrations, and can compound its own errors. The explanations above motivate the architecture; they are not controlled ablations assigning a win-rate gain to each component.

The transferable idea is to make the **structure of the execution problem** visible to learning. Local spatial features describe the job, daily memory supplies continuity, attention connects workers, and structured decoding handles commands and shared resources. This turns replay imitation from isolated action prediction into a practical way to learn how to run the whole farm.