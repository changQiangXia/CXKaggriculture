# Cloning the best farmer on Colab

Thanks to Kaggle and the hosts for Kaggriculture. The game looks simple, but the shared market makes it hard. And thanks to the top teams, especially **DSM**, **M & M & P & Q** and **Victor @ Tufa Labs**. Their ladder games were our training data, so this solution is partly theirs.

**TL;DR.** For three weeks we built rule-based agents, planners and RL sale-timing policies, and they plateaued around 2,550-2,800. In the last four days we switched to **closed-loop behavioural cloning (BC)**: per-unit imitation of the top teams' ladder games, iterated on a single **RTX 5070 (12 GB)**. The CNN generations and the final fine-tunes ran on the 5070; the final ViT-style trunk was pre-trained on a Colab A100. The final agent is a hybrid ViT clone fine-tuned on DSM's tomato-always versions, with a small tomato top-up wrapper. Its final ladder score was **2807.4**.

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F22592122%2Fe662f30d27235e0019e96928533cf1ac%2F01_pipeline.png?generation=1792087864388614&alt=media)
---

## 1. Weeks 1-3: hand-built agents (subs 1-66)

Briefly, because most of it was beaten later:

- **Rules plus overlays.** We started from a public V37-lineage agent and layered on sale-timing, feed/fertilizer, opening guards and terminal planners.
- **An exact C++ port of our agent.** It passed two gates (zero action mismatches over 23 Python games) and runs **817 games/s** on 12 CPU threads, against about 0.01 games/s per core in Python. With it we trained a **REINFORCE sale-horizon table over 4.3M games**. That made sub 22/23, which reached 2801 on the mid-September ladder.
- **Route planners and VRP crews.** These included a closed-loop farm simulator with vehicle routing, route bandits and ridge-regression route tables.

What we learned from those weeks:

1. **The route (what you grow, and when you buy land and animals) is worth far more than the market layer.** We tested eleven market-layer levers, and every one was refuted.
2. **Replaying tapes is biased.** A recorded rival does not react to you, so a tape evaluation is only valid when the agent you substitute plays like the one the tape was recorded against.
3. **Mirror games are decided by who sells first.** Any fixed sale horizon loses once it is copied. A reactive lead detector, and then the RL table, beat every fixed horizon.
4. **We could not hand-build what the top teams did.** An exact cash audit showed DSM about **+$8.9k per game** ahead of us after controlling for shop luck. We tried tape executors, DSM-plan executors and a reactor on our planner, and none of them closed the gap.

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F22592122%2F5404fcd3d6eee1a3208c3c99d8b5f6a5%2F06_ladder_history.png?generation=1792087904910593&alt=media)
## 2. The switch: per-unit closed-loop BC

Earlier "clones" replayed open-loop tapes of recorded games, so execution kept breaking. We made the policy itself the clone: **every turn, every unit (farmer and each hand) picks an action from a network that sees the current state.**

### Data

- We pulled top-team ladder replays through the Kaggle API, each with its seed and both seats' actions.
- A **seat-game** is one player's side of one game, so a game has two. We trained only on the seats played by the teams we were cloning. The opponent's farm is part of the observed state, but its actions are never training targets.
- Every game is **re-simulated exactly** in our fastsim (Python, later the C++ bridge). A game is kept only if the replayed money matches the recorded money (1644/1644 seat-games for the first DSM set).
- The data grew from **1.6k DSM seat-games** (v1) to **10.3k seat-games from the top ~30 teams** (data6), which is about 4.5M turns in the "latest agents" subset.

### Model

- **v1-v4 (CNN):** a residual CNN over the 10×10 farm. Tile classes are embedded (ours and the opponent's), plus 12 numeric channels and a global vector: hour, day, cash, shed, seeds, prices, market inventory, shops, a team/style slot and carried goods.
  - **Unit head:** the trunk feature at the unit's tile, the pooled trunk, the globals, the unit index and its inventory → 47 action tokens.
  - **Market head:** 21 order keys × 18 count buckets. Each key (e.g. `SELL MILK`, `BUY_SEED WHEAT`, `HIRE`) is its own 18-way classification over order sizes, where bucket 0 means "no order". We use classification rather than regression because order sizes are bursty, and most turns place no order at all.
  - **Loss:** cross-entropy on the unit actions plus cross-entropy on the market buckets (averaged over the 21 keys), with label smoothing 0.02.
- **ViT trunk:** a transformer over the 100 tile tokens.
- **worker_hybrid (final trunk):** two local convolutions, then attention over tile tokens plus explicit **worker tokens** (position, identity, inventory). Width 256, 6 layers.

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F22592122%2F7a302f5fca4f307654f7deaf1588f5df%2F09_model_architecture.png?generation=1792087920890003&alt=media)
- **Decoding is parallel, not autoregressive.** The trunk runs once per turn, and each unit's head reads that shared trunk with its own position, index and inventory. All units decode independently in that one pass, so no unit sees what another unit chose this turn. Two units can therefore claim the same harvest or feed (see section 6 for why we left that alone).
- **Inference:** a plain numpy forward pass with fp16 weights base64-encoded into a single `main.py` (about 5.6 MB). Parity with PyTorch is about 1e-6. A turn takes 20 ms for the CNN and 73 ms for the ViT locally, against the 1 s actTimeout.

### The decoder mattered more than the network

The first trained build finished the season on **$0**. The network was fine; the wrapper around it was not:

1. **Calibrated market thresholds.** Argmax never fires rare orders such as `BUY_LAND` or `HIRE`. Each market key now fires when P(count > 0) exceeds a per-key threshold, calibrated so the clone's held-out firing rate matches the teacher's.
2. **A sell-what-arrives clamp.** DSM sells the same turn it delivers, so at observation time its shed shows 0. SELL counts must be clamped to shed stock **plus goods PLACEd or DROPped this turn**. Without this, the clone hoarded milk and wool.
3. **A legal-op mask, a PLANT cap at seeds in stock, and a last-day dump.** The mask runs at inference only. Before the argmax, every op that is illegal for that unit on its tile this turn has its logit set to −1e9. Training sees the teacher's actions unmasked.

With those fixes, the same weights went from $0.1k to $75.6k in DSM's recorded worlds after 2 epochs. A few epochs later the clone made **more money than DSM itself** in DSM's own hold-out worlds (v1 at epoch 9: $128k against DSM's $121k over 16 worlds):

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F22592122%2F42f5e2113345ae0634595d1f1e0ba082%2F08_decoder_fixes.png?generation=1792087936221207&alt=media)
That benchmark keeps the opponent's recorded actions fixed, so it is a fidelity check, not proof that the clone was stronger than DSM (section 4 covers this bias). The closed-loop results are what convinced us. The first upload (v2f) went 24/26 on the ladder with a +$31k mean margin. Locally it beat our best hand-built agent **24/24 at +$19.6k per game**.

## 3. Training: an RTX 5070, plus Colab for the big trunks

All the CNN generations and the final fine-tunes were trained on one consumer GPU in a Windows desktop. The ViT and worker_hybrid sweeps were too slow on a 12 GB card, so we pre-trained those trunks on a Colab A100 and then fine-tuned and evaluated them on the 5070. The times below come from the training logs:

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F22592122%2F6c8c839f83aedcea21b1a11f5cedffb6%2F02_training_curves_5070.png?generation=1792087953451713&alt=media)

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F22592122%2F0471eb07243676ecd2e528174c33ac80%2F03_train_time_5070.png?generation=1792087961104422&alt=media)
| model | data | epochs | wall-clock | where |
|---|---|---|---|---|
| v1 CNN 128×6 | 1.1M DSM turns | 16 | 36 min | RTX 5070 |
| v2 (+carried goods) | 1.2M turns | 16 | 40 min | RTX 5070 |
| v3 CNN 160×8 | 1.2M turns | 20 | 73 min | RTX 5070 |
| v4 top-20 teams | 3.5M turns | 12 | 117 min | RTX 5070 |
| v4d (DSM fine-tune) | 1.2M turns | 6 | 21 min | RTX 5070 |
| ViT / worker_hybrid sweeps | 7-10k seat-games | 12 | hours | Colab A100 |
| **dsmT (final fine-tune)** | 219 DSM seat-games | 3 (and 6) | **3.5 min** (3 epochs) | RTX 5070 |

What we learned about the hardware:

- **One GPU job at a time.** Running two GPU-batched harnesses together left half the games with an agent that never acted (bank stuck at $3,000), including the control.
- **The 12 GB card pages at ViT batch 1024** once anything else holds memory, which made training about 25× slower. We used a smaller batch or Colab.
- **Under Windows WDDM, each model call costs about 18 ms regardless of batch size**, so on this machine batching across games matters more than model size.
- **Pin BLAS to one thread** in evaluation workers. OpenBLAS threading made our small conv matmuls 2.5× slower.

### Architecture sweep

On the same data, features, heads and 12 epochs, **spatial attention beat temporal context by a wide margin.** Nearly all the gain from history comes from the previous action alone.

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F22592122%2F5771b74c4b96b8cb46a47a71ee3fdb84%2F04_arch_sweep.png?generation=1792087980847389&alt=media)
The held-out loss did not always predict closed-loop strength. A DSM-only fine-tune of the ViT had *lower* loss (0.194) but lost about $4k per game. **We judged every model by games, not by loss.**

## 4. Evaluation: fast, paired and on the right worlds

The bottleneck was always evaluation, not training.

- **GPU-batched gauntlet.** Worker processes play games as threads, and one GPU forward per build serves every waiting game (full fp32, TF32 off, because TF32 broke parity). **48 games take 101 s instead of 13 minutes**, and 45/48 games match the numpy path's money exactly.
- **Pinned ladder worlds.** A replay's `info.seed` reproduces the game exactly, so we replay *our real ladder losses* with the rival's recorded actions pinned and swap in a candidate. This is how we found the tomato gap below.
- **Why pinned worlds are still usable, despite the tape bias from section 1.** The pinned rival is open-loop. Once our candidate changes the shared market, the rival keeps selling into prices it never saw. That makes absolute pinned scores unreliable. We only used pinned worlds to compare two candidates, both close to the agent the tapes were recorded against. Because both sides of that comparison inherit the same bias, the paired difference stays meaningful while the market changes only a little. We also watched for open-loop artifacts. One MMPQ fine-tune scored +$24k per game pinned, but 54 of its pinned rival tapes crashed once the market diverged, so we threw it out. Pinned worlds were a screen, and closed-loop head-to-head games were the gate.
- **Teacher hold-out worlds.** These are the teacher's own post-training ladder games. Both pinned and head-to-head wins can be artifacts (that MMPQ fine-tune also won 75% head-to-head, yet was not a faithful clone), so the teacher's own held-out worlds were our fidelity check.
- **Count seeds, not games.** Every head-to-head seed is played twice with the seats swapped. Shop unlocks and weed spawns come from the seed, and the game treats the two seats the same. So when both agents play the same way in both games, the seat-swapped game mirrors the first and each agent's money comes out identical. That happened in about 70% of seeds between our near-identical clones. With 24 games you have about 12 independent worlds, not 24.
- **Gate rule.** Before any upload, the candidate must win the incumbent's ladder losses and post a clear head-to-head win rate against the incumbent.

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F22592122%2F04307676ea01127ba9036474ede9183c%2F05_incumbent_chain.png?generation=1792087993290831&alt=media)
## 5. The last gap: tomatoes

We audited 86 ladder games against the ~2800 tier. Our clone matched or beat them on every product except one:

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F22592122%2F5495d6e4d3ca699681cd9b385b3b36e8%2F07_tomato_gap.png?generation=1792088006393681&alt=media)
The top teams started tomatoes late (median opponent tomato plants: 0 by day 14, 8 by day 17, 11.5 by day 20) and sold them at about $113. Our clone came from DSM versions that did not grow tomato, so it never started.

- **R4 wrapper.** If the opponent has at least 4 tomato plants between days 13 and 20, swap the clone's `PLANT WHEAT` to `PLANT TOMATO`, with a cap of 10 and a $1,500 cash guard. On 40 real tomato-opponent ladder worlds it scored **+$2.2k per game paired, with 7 losses flipped to wins and 0 wins flipped to losses.** Early tomato (from day 8) starved cash on days 8-10 and *lost* $6-9k per game.
- **Wrapper tuning hit a local optimum.** Other caps and triggers all landed within ±$230 of R4.
- **dsmT, the final model.** DSM's newest versions grow tomato in 100% of games, so we fine-tuned worker_hybrid on only those **219 seat-games** (lr/4, 3 epochs, **3.5 min on the 5070**). Validation unit loss went from 0.217 to 0.141. On its own, dsmT beat the wrapper agent (worker_hybrid + R4) by **+$2.4k per game** on 212 pinned ladder worlds, almost all of it in tomato worlds.
- **`_R4a`, the additive top-up.** R4 rewrites the network's choices: it turns `PLANT WHEAT` into `PLANT TOMATO` and limits tomato seed stock. That would fight a model that already wants tomato. `_R4a` uses the same trigger (opponent has 4 or more tomato plants on days 13-20), but it never edits or limits the network's own tomato buys and plants. It only adds tomato when the network's own plan is still under the cap. We kept it as a safety net because dsmT sometimes starts too late. In one head-to-head game it planted its first tomato on day 18, with only 4-6 plants. dsmT with `_R4a` beat R4 61% head-to-head and flipped 6 of R4's 12 losses on R4's own ladder worlds.
- **dsmT6e_R4a, the best final sub.** It is the same recipe at 6 epochs. Its validation loss is *worse* (0.150), but it went 70% head-to-head against R4 and 24/40 in DSM's held-out seat (R4 21/40). It ended at **2807.4**.

The lesson is that **a crop strategy has to come from the plan (the teacher), not from a wrapper.** As the main mechanism, the wrapper only patched the symptom: R4 alone hit a local optimum within ±$230. Switching the teacher was worth +$2.4k on top of that. In the final agent the wrapper is demoted to a small safety net on top of a policy that already grows tomato.

## 6. What did not work

| idea | result |
|---|---|
| Unit-coordination masks (dedupe units claiming the same fertilizer, harvest or feed) | −$42k to −$89k per game. The clone learned DSM's own collisions, and "fixing" them pushes it off-distribution. |
| Relabelling engine no-ops as PASS in training | 62% fewer no-ops, no score change |
| Single-team fine-tunes (MMPQ, Victor) / playing in a non-DSM style slot | −$3k to −$4k per game, despite better loss on that team's games |
| Mixing all top-20 teams with a style slot (v4) | no better than DSM-only |
| Weight soup (0.5·base + 0.5·fine-tune) | loss in between, but 25-38% head-to-head |
| Logit ensemble of 3 fine-tunes | +$0.4-0.7k per game, but no extra wins, and 3× slower (321 ms per turn) |
| Head-only PPO on the BC policy (frozen trunk, exact legal-set log-probs) | tied the base (+$36 ± $596) |
| Sale horizon by rival class, land-buying wrapper, sheep/goose annexes, melon races | all flat or negative |

## 7. Takeaways

1. **If move-level data from a stronger agent exists, clone it per unit and in closed loop first.** We spent weeks hand-building executors for plans that a 40-minute BC run on a consumer GPU learned better.
2. **Audit the decoder before you judge the model.** Threshold calibration and a same-turn sell clamp were the difference between $0 and beating the teacher.
3. **Lower validation loss did not reliably mean a stronger agent.** Gate on games: paired, seed-counted and in the right worlds (your real losses and the teacher's hold-outs).
4. **On one GPU, spend compute on evaluation throughput.** Batching the network across games gave an 8× faster gauntlet, which was worth more than a bigger model.
5. **Look at the losses one product at a time.** One crop explained most of the gap to the 2800 tier.
6. **Don't "fix" the teacher's mistakes at play time.** Units in our clone sometimes collide on the same task, as DSM's do. Masking those collisions cost $42k-$89k per game, because the clone was pushed into states it had never seen. If a behaviour has to change, change it in training.

Thanks for reading. Happy to answer questions in the comments.