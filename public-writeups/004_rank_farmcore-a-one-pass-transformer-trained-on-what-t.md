# Farmcore: a one-pass transformer trained on what the engine executed

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21974454%2Fd4e98a544e2b1791f003ceeef73e38c3%2F01_intro.gif?generation=1792182652907558&alt=media)

Team Farmcore, 4th place of ~10 200 teams. Corresponding author: [Iaroslav Pudovkin](https://www.kaggle.com/betmyex). Code: [github.com/B3tMy3x/farmcore-kaggriculture](https://github.com/B3tMy3x/farmcore-kaggriculture). Trained agent: [Kaggle Models](https://www.kaggle.com/models/betmyex/farmcore-kaggriculture-agent).

Our final agent is pure behavioral cloning: no search at play time, no self-play data. The biggest gain came from fixing the labels, not the model: retrained on what the engine executed instead of what players ordered, plus one feeding rule, the same network went from 3 to 23 wins of 24 against our previous best. The three main choices:

1. **We imitate what the engine executed, not what the player ordered.** Strong players over-order and let the engine silently drop the rest. Cloning those orders teaches a policy to issue empty orders.
2. **The whole turn comes out of one forward pass.** A transformer drafts every unit's job and every market decision at once, then a six-layer corrector reads that soft draft once and lets all decisions adjust to each other.
3. **Pretrain broadly, fine-tune narrowly, then average.** Pretrain on 67 top submissions, fine-tune on a single team, and average the weights of two such fine-tunes.

PPO improved our policy too, but per GPU-hour, data and pretraining paid at least ten times more (section 6). After the deadline we found a market mechanic we never modeled: the engine pairs the players' orders by position in the market list, so whoever lists a good first sells it first (+$4 or −$10 per unit). In replays it is worth up to $0.4–0.6k per game against the top 3; we never tested a fix on the ladder (section 5).

| | |
|---|---|
| final model, end to end | ≈5.5 A100-hours |
| training data | 8 583 replays of 67 top submissions, then 563 and 766 replays of one team |
| self-play games in the final model | 0 (the winner: ~8.3M) |
| hardware | 1–2 × A100-80GB provided by our university, plus free cloud compute |
| cost to us | $0 |
| evaluation | ~19k paired-seed games, on CPU |

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21974454%2F90215c9537d46609700c72a04621ff17%2F02_timeline.png?generation=1792182680752537&alt=media)

**How to read the numbers.** A strong agent ends a game with about $100k. The engine is deterministic, so we compare two agents on the same seeds (usually 48): "+$X" is the mean per-game difference in final money, "44/48" means ahead on 44 of 48 seeds. *Margin* is our money minus the opponent's.

| | Common approach | Ours |
|---|---|---|
| Imitation target | Recorded player actions | State changes the engine actually applied |
| Turn generation | Independent per-unit outputs or autoregressive decoding | A draft of the whole turn, then a corrector over all decisions |
| After cloning | Large-scale PPO self-play | Broad pretraining, single-team fine-tuning, weight averaging |
| Checkpoint selection | Validation metrics or local win rate | Money on paired seeds |

## 1. What we imitate: executed trades, not orders

The engine executes a market order one unit at a time. When an order tries to sell from an empty shed or buy beyond the available money, it stops at the first unit that fails and silently drops the rest.

Many top players rely on this and over-order. Replaying the games of 15 top players showed how little of their orders executed:

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21974454%2F71ab0eaa8d44aa1477f187056cf4d77a%2F03_ordered_vs_executed.png?generation=1792182780608785&alt=media)

A policy trained on recorded actions learns these empty orders, while at play time our decoder clips them to the real shed and budget: it is trained in one world and plays in another. The fix works with any deterministic engine:

1. Replay every game, feeding both players' recorded actions.
2. Hook the engine's commit function and log what executed: units sold, bought, hired.
3. Check that replayed money matches recorded money at every step; drop games that do not reproduce.
4. Use the executed changes as labels, and cancel round trips (selling an item and buying it back in the same turn).
5. Compute all input features from the same replayed record, so training and play see the same quantities.

Against our previous best, the clone won 3/24 games on raw orders, 12/24 on executed labels and 23/24 with the feed guard below.

**Rules for states the teacher never visited.** A clone eventually reaches states absent from its teacher's games. Our teacher always fed its animals its own wheat, so its data never had a hungry herd and an empty shed; the clone stalled there, and animals unfed for two days run away. Three rules derived from the game mechanics closed such gaps:

* *Feed guard:* each turn, buy exactly enough wheat to feed the animals not yet fed today.
* *Night-shed sell:* at night units dump their loads into the shed and the overflow is destroyed, so on each day's last turn we sell what would be lost (+$0.5k on average over five opponents).
* *End sell:* sell the whole shed on the final turn.

Six other "common sense" rules (more coops, capped wheat purchases, spreading units out) were neutral or negative. Even blocking requests larger than the shed lost money: the engine turns such a request into a harmless no-op, while a blocked unit wastes its turn.

## 2. How a turn is built: one pass, then a corrector

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21974454%2F927a61687f62e67fe6308287c41eb4c7%2F04_architecture.png?generation=1792182794893881&alt=media)

A turn is a plan, and a plan is easiest to fix when all of it is visible. So the network drafts the whole turn in one pass, then a corrector lets the decisions see each other and revise:

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21974454%2Fec202737a41b42fe7a185a3b58b673ad%2F05_turn_in_one_pass.png?generation=1792182815693204&alt=media)

* **Input:** one token per own tile (100), per unit (up to 24), per product, crop and animal, plus a global token. The opponent's farm goes through its own encoder and a four-latent bottleneck.
* **Trunk:** nine transformer blocks. Each head has a learned 19×19 relative-position bias over the offset (dx, dy), shared across layers; removing it cost money.
* **Draft heads:** each unit gets a pointer to its target tile and an action. The market gets an open/closed gate and a quantity per item and order type, plus hiring and land. No head sees what the others decided: unit 3 doesn't know that unit 7 is heading for the same melon, and the sell head doesn't know what the units will drop into the shed this turn.
* **Movement:** a rule, not a prediction. Every teacher step we measured was a shortest-path move toward the unit's next job, so the network picks the tile and a rule takes the steps.
* **Corrector:** each unit gets its *intent*, the draft target distribution averaged over tile keys, and cross-attends to our tiles to see what lies on a contested target. Market tokens get the expected sells and buys and the shed as it will be at market time, after this turn's pickups and drop-offs; the global token gets the expected spend and revenue, computed explicitly. Six transformer layers run once over these 42 decision tokens (24 unit slots, 9 goods, 5 crops, 3 animals, 1 global), and the same heads give the final decisions.
* **Training:** end to end, with the loss only on final decisions, so the draft learns only through the corrector. The corrector reads the network's own soft draft, never the ground truth: a variant fed the true plan learned to trust it and lost in live play.

The policy has 21.5M parameters, about 16M at play time (the rest is a training-only value tower), and runs in FP32 PyTorch on two CPU threads, well within the 1 s limit. The case for this design is the error structure, not speed: the errors autoregression fixes (the right action given to the wrong unit) were only about a fifth of the clone's errors.

**What the corrector actually does.** It changes the target of 25% of units and the market orders in 74% of turns; without it, money drops from ~$100k to ~$14k and all 48 paired games are lost. But it does not do the job we designed it for: target collisions are as frequent after it as before (0.086 vs 0.088 per turn). Instead:

* in 17% of unit-turns the draft keeps the unit working its current tile and the corrector sends it elsewhere. The draft is a greedy "do the nearest job" policy, and the plan lives in the corrector;
* in the market it mostly closes gates: the draft opens 32% of sell gates, the final turn 14%;
* the draft is badly calibrated (expected calibration error 0.21 on sells). It is not a weaker policy but a feature map that the corrector reads.

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21974454%2Fd44eb9651cd97bf7b8b07a281a85b937%2F06_corrector_turn.png?generation=1792182828003287&alt=media)

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21974454%2F5b7bdae5adeb80510c97f8b02e15e64e%2F07_corrector_gates.png?generation=1792182847646179&alt=media)

**Where each decision is made.** With an early-exit form of the logit lens from LLM interpretability, we cut the trunk after k of 9 layers or the corrector after k of 6 and compare the turn with the full network's on 8 640 ladder states:

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21974454%2Fd19aab45cc004a1082696baf785d27be%2F08_layer_lens.png?generation=1792182859318899&alt=media)

At play time we also subtract the training class priors from the logits (logit adjustment, β = 1): +$3.2k and 44/48 against the same weights with raw logits.

## 3. How it was trained: pretrain, fine-tune, average

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21974454%2Fc245a9eebb96e06ab256241fce09b372%2F09_pipeline.png?generation=1792182868895746&alt=media)

One pooled corpus of many top players was worse than cloning a single team. A clone matched its teacher on 88% of unit actions, while top teams agreed with each other on only 66–68%: a pooled model mixes neighbouring decisions of different players, and its plans stop fitting together. Cloning the top-ranked player also underperformed: reactive players clone cleanly, long-horizon planners do not.

Splitting training into stages worked:

1. **Pretrain** on the relabeled games of many top teams.
2. **Fine-tune** on a single strong team: +$9.2k and 89/96 against our previous model, and clearly better than training on that team from scratch.
3. **Average the weights** of two fine-tunes that start from the same pretrain but use different submissions of that team. Reliably about +$1k over a parent; our best soup gained +$3.3k (46/48), and re-running the recipe with other seeds gave +$0.9k and +$1.1k.

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21974454%2Ff28ed687335a805b52747ad6acb10ed8%2F10_soup_kinds.png?generation=1792182885121164&alt=media)

Mixing weights works like mixing data of one team, not like mixing teams. Because both parents start from the same point and agree on about 80% of unit actions, averaging their weights behaves much like ensembling their logits, at no inference cost.

**What the soup actually does.** We ran the pretrain, both parents and the soup on the same 5 760 ladder states:

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21974454%2F022ef186cfdbe5e0955787e816fb1727%2F11_soup_diff.png?generation=1792182918215684&alt=media)

**How we chose checkpoints.** Whole-turn validation accuracy correlated negatively with money (rank correlation −0.86 over eight versions), and our best validation ever came from a data leak. So we selected only by paired-seed money, in the final week against a panel of 5–7 opponents, since strength was not transitive: some versions gained +$8k against one baseline and lost to others. Our worst bugs were train/play mismatches that never showed in validation; only step-by-step comparison with the engine caught them.

## 4. What the network learned (interpretability)

Shuffling one input group at a time in live games shows what the policy relies on:

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21974454%2Ff00f228b78585f0d5ea27bee76b42d16%2F12_input_ablation.png?generation=1792182927788398&alt=media)

**What the product tokens encode.** A sparse autoencoder, the standard tool for reading LLM activations (TopK, 1 024 features, 315k product tokens from 35k ladder states, 4.5% variance unexplained), splits the network's view of each good into readable features:

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21974454%2Fb61952d7229b564979f2babb7bbf4c3a%2F13_sae_features.png?generation=1792187558858920&alt=media)

The feature directions are causally meaningful, though not strong levers. Pushing the milk token along a milk feature's direction, by twice the token's own norm, opens the milk sell gate on 58% of states instead of 3%; 20 random directions of the same size reach at most 8%. A fertilizer feature does the same, 18% → 51% (random: at most 22%). At shifts the size of the token itself the effect is small (milk 3% → 8%). Removing a single feature, though, rarely closes a gate: each decision is carried by several features at once. It is a cheap way to check what a cloned policy keys on before shipping it.

**It found the town's four-turn shop cycle on its own.** Strawberries, milk and wool are sold almost only on shop turns (sell probability 0.4–0.7, against under 0.1 on other turns), and sales rise with price and with stock in the shed:

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21974454%2F2088435038989740e68970587ee99763%2F14_sell_shop_cycle.png?generation=1792182950332104&alt=media)

**The opponent representation collapsed into one signal.** The four opponent latents have a cosine similarity of 0.993: the policy tracks the opponent mainly through the shared market, not through their board. The exception is livestock: buying cows and sheep takes finite, shared milk and wool demand away from the opponent. Disabling the corrector for livestock purchases cost $29k of margin, $26k of which went to the opponent.

## 5. Against the field

Margin per game of our final model against each top team, from two weeks of post-deadline ladder games:

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21974454%2F093a5121adcf43784813cd7e6a1ffe23%2F15_h2h_field.png?generation=1792182959958763&alt=media)

The margins are tiny: in 64% of games the gap is under $2k on ~$100k, and in 29% it is smaller than the effect of changing a single move (replacing one move with `PASS` shifts the final money by a median $0.7–0.85k, with a stable sign for only ~24 turns). Among the top teams, places are decided by many near-coin-flips, which is also why per-move credit in RL is so expensive (section 6).

### Where we lose to the top 3

We replayed our 295 ladder games against the top 3 through the engine, logging every executed market unit and its price (money reconciles to the dollar). Each side sells ~$135k of goods per game, and our selling looks almost identical to the 1st place's: same hours, same batch sizes, same number of sales. The gap is in high-value goods (strawberries, milk, wool), and against the 1st place about half of it is price, not volume: the same units sold $2–3 cheaper.

Part of the reason is a mechanic we never modeled. The engine executes order *i* of one player together with order *i* of the other, unit by unit, and every unit sold moves the price down. So when both players sell the same good in the same turn (a collision), whoever put it earlier in their market list sells first:

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21974454%2F5b916fc96dbb4d6d1261a2a5800ae3ee%2F16_market_order.png?generation=1792182973881715&alt=media)

Summed over these collisions, that is up to −$0.4–0.6k per game against each of the top 3. This is a replay estimate, not a causal effect: who lists a good first depends on the state of the game, and the opponent would also play differently against a different order. All three top teams sort their sells by price every turn (rank correlation of list position with price −0.58 to −0.62). Our decoder lists sells in a fixed order that starts with wheat, the cheapest good (−0.09), so the network could not compete for the slot. The only causal test we ran: sorting our sells by price gains +$216 ± 189 per game (69% of 48 paired seeds) against our older package, which sells in our order. Against teams that sort by price the gain could differ either way; we found this after the deadline and never tested it on the ladder.

## 6. RL worked; scaling the data worked far better

PPO on top of our imitation checkpoints, with the change in farm net worth as the reward, gained +$1.3k per game over its starting checkpoint (64/96 paired seeds, p = 1e-5), and an RL checkpoint was one of our ladder submissions. Our teammate's self-play runs of ~100k games each gave similar gains.

We dropped it because of compute. Per GPU-hour, data and pretraining paid at least ten times more than our best PPO run:

| | compute | gain |
|---|---|---|
| best PPO run (23 updates of 128 games) | ~2.8 A100-hours | +$1.3k |
| longest PPO run (260 updates) | ~30 A100-hours (estimated) | −$14k against the relabeled clone below |
| relabeling the corpus with executed trades | an afternoon of CPU | 3/24 → 23/24 against our previous best |
| fine-tuning the pretrained model on one team | 1.2 A100-hours | +$9.2k (89/96) |
| the whole final model | ≈5.5 A100-hours | 4th place |

Both final submissions are pure imitation; the RL loop is in the repository as a working tool. Rule of thumb for similar competitions: if the engine is deterministic and strong replays are public, relabel and clone first; PPO on top pays only with far more compute than we had.

Why PPO is so expensive here: at our batch size the per-move signal is mostly noise. Split one rollout of 128 games in two and compute the policy gradient on each half, and the cosine between the halves is 0.06 (−0.01 with shuffled advantages, 0.93 for a control target the policy itself determines). That matches the chaos probe in section 5: a move's true effect is worth $30–400 and visible for ~24 turns, while the final result moves by ±$1–2k for unrelated reasons. A net-worth reward also cannot see market sells: selling turns stock into cash of about the same value. PPO needs far larger batches, which is what teams with GPU fleets ran.

Compute reported by other top teams:

| | training hardware | notes |
|---|---|---|
| [1st place](https://www.kaggle.com/competitions/kaggriculture/discussion/745073) | final 10M model: up to 17 A100 + 29 A30 (~7 + 20 on average); a parallel 20M model: up to 26 A100 more | ~8.29M self-play games |
| [pure BC, top 10](https://www.kaggle.com/competitions/kaggriculture/discussion/745367) | one RTX 5090 | pretrain ≈50 min |
| [autoregressive SFT, top 10](https://www.kaggle.com/competitions/kaggriculture/discussion/745036) | two RTX 4090 and an RTX 3090, a DGX Spark, rented Colab GPUs | final model trained from scratch on one Colab G4 |
| us | 1–2 university A100 + free cloud compute, $0 in total | final model ≈5.5 A100-hours, 0 self-play games |

Every pure-imitation team in the top 10 trained its final model on one to three cards. The GPU fleets bought the self-play scale that PPO needs.

## 7. What did not work

* Mixed multi-teacher corpora with teacher-style embeddings: weaker than one consistent teacher. Other teams gained from conditioning on team, version and outcome; we tried only a team embedding.
* Routing between expert models per decision head: gains against one opponent, losses against others.
* Feeding each unit its previous action: the clone learned to copy itself (−$25k for one teacher).
* All board tiles as corrector tokens: attention spread away from the units.
* Sampling actions instead of argmax: money within noise, fewer wins.
* Iterative multi-pass draft refinement: no gain over a single corrector step.

Thanks to the organizers for a genuinely interesting game, and to the teams at the top of the ladder: every one of our models learned by watching your games. This gold also made all of us Kaggle Competitions Masters. Thank you!