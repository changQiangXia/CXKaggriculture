# 47th place: teaching a farming agent from replays

Code: [github.com/spoutop/kaggriculture-replay-cloning](https://github.com/spoutop/kaggriculture-replay-cloning) · Final agents: [Kaggle dataset](https://www.kaggle.com/datasets/spoutop/kaggriculture-smackaveli-final-agents)

![Cover illustration of a farm beneath a neural network](https://raw.githubusercontent.com/spoutop/kaggriculture-replay-cloning/main/assets/hero.png)

**In numbers**

- Five policy networks per submission at 11.79M parameters each. A smaller six-member ensemble sits beside them for one opening pattern.
- Behaviour cloning on about 21k recorded game-seats. Pretraining on many teams then two fine-tuning stages on one.
- NumPy float32 inference on Kaggle's CPU workers from int8 and float16 weight storage. PyTorch for training only.
- Public rank 10 on September 25. Final rank 47 of 10,148 after the post-deadline rating phase.

We finished 47th of 10,148 teams with an agent that learned to farm from other players' public replays. A decoder turns its predictions into legal orders. A handful of stock rules handle overflow and the last two days. We also spent a large part of the month on PPO. None of those runs produced a checkpoint that beat our best clone.

Our clones reached 92% on held-out unit commands within a week. Turning that into complete games that win took the rest of the month.

---

## 1. The example turn

![Five steps from public replay files to a submitted policy](https://raw.githubusercontent.com/spoutop/kaggriculture-replay-cloning/main/assets/f1_pipeline.png)

The example comes from one of the final agent's ladder games. It is day 10 at hour 1 with ten units on the farm and $1,069 in hand. The network predicts a command for every unit and an order for every market slot. The decoder turns that into the action the game executes.

![The actual farm at step 241 beside six feature planes and the unit and global inputs](https://raw.githubusercontent.com/spoutop/kaggriculture-replay-cloning/main/assets/g1_turn.png)

The farm becomes 28 feature planes over the 10 x 10 board. Each plane holds one fact per tile. One plane marks wheat. Another holds plant age. Others record watering and yield and how many units stand on the tile. The opponent's visible farm gets its own 28. Each farm hand is a row of 17 numbers that give its position and its cargo. One entry is its index. A 64-number global vector holds the clock and both players' money. Seed and shed stock sit there too. So do the current prices and the market stock and the town's shops.

---

## 2. The network

![Policy architecture with the farm trunk and global conditioning feeding shared unit and market heads](https://raw.githubusercontent.com/spoutop/kaggriculture-replay-cloning/main/assets/g2_architecture.png)

Every worker uses the same action head. Its input is the trunk features at the worker's own tile together with the worker's inventory and a pooled summary of the game. At the example turn that one head sends hand 2 to harvest. It sends hands 3 and 4 to pick up four wheat each. The rest get a single move.

The trunk is a 3 x 3 stem followed by eight residual blocks at 256 channels. FiLM conditioning lets the 64 global numbers scale and shift the features inside every block. The same crop pattern can produce a different decision at a different time or price. The opponent's farm passes through a smaller branch before pooling. Each of the ten market slots predicts an order kind on its own. A second head then predicts the quantity for that kind. The slots never see each other's choices. The deployed decoder therefore carries a rule that appends likely kinds no slot picked.

![Score distributions for hand 3 and market slot 1 at the example turn](https://raw.githubusercontent.com/spoutop/kaggriculture-replay-cloning/main/assets/g3_decode.png)

Hand 3 picks up four wheat. The first market slot hires a worker. Run from the start of this episode the deployed agent reproduces the recorded action at this turn exactly: three hires and two wheat purchases alongside the unit commands.

---

## 3. Training

![A supervised minibatch update with separate losses for unit commands and market kinds and quantities](https://raw.githubusercontent.com/spoutop/kaggriculture-replay-cloning/main/assets/g4_update.png)

A replay simulator rebuilds the state before each recorded action. We encode that state. The recorded action supplies three classification targets: the unit command and the market kind and the market quantity. Each cross-entropy runs over legal choices only. The quantity head sees the recorded kind in training and the predicted kind at play. There is no reward signal and no online rollout in training. The inherited value head stays unused.

![The three training stages and the member chains in the two final submissions](https://raw.githubusercontent.com/spoutop/kaggriculture-replay-cloning/main/assets/g5_lineage.png)

Each stage starts from the previous checkpoint. Stage 1 learns from many teams (18,667 game-seats). Stage 2 narrows to one strong reference style (1,150 seats from selected versions of that team with newer games weighted up). Stage 3 refreshes on that team's recent games with extra weight on games against opponents rated 2,800 and above. The two submissions share two members from an earlier chain and differ in the other three.

![Saved validation losses and accuracies for one final member across all three stages](https://raw.githubusercontent.com/spoutop/kaggriculture-replay-cloning/main/assets/g6_curves.png)

Seed 311's saved logs. Each column uses that stage's own validation seats. In stage 2 the losses rise for most of the run while the accuracies stay flat. Ten validation seats are too few for the loss to guide anything there. We chose export epochs by full games against cloned opponents.

---

## 4. The deployed turn

![One turn on Kaggle in code order from the time guard to the returned action](https://raw.githubusercontent.com/spoutop/kaggriculture-replay-cloning/main/assets/g7_deployed.png)

The active members average their log-probabilities. The decoder adds a score offset per order kind and game phase before the argmax under legality masks. Those offsets came from game-level evolution strategies on paired games against cloned opponents.

Three rules run after the decoder. The missing-order rule appends a likely order kind that none of the ten slots selected. It never merges duplicates. The overflow rule sells before the shed fills. The last turns liquidate stock. Two mechanisms can override the base action. An opening-signature check at step 2 can hand the rest of the game to the smaller six-member ensemble. An opening book can replace the base action when the encoded state exactly matches a recorded opening. A time guard drops members rather than let a slow worker time out.

![The shipped score offsets with market-order rows separated from unit-command rows](https://raw.githubusercontent.com/spoutop/kaggriculture-replay-cloning/main/assets/f6_correction.png)

The offsets favour seed orders for wheat and tomato and carrot from day 15. They discourage late wheat sales and early land purchases. They change scores rather than forcing or forbidding actions.

---

## 5. Results

![Public rank over the last week with the September 25 top-ten screenshot](https://raw.githubusercontent.com/spoutop/kaggriculture-replay-cloning/main/assets/g10_ladder.png)

The first cloned ensembles went up on September 23. Two days later we sat at rank 10. The last week was spent in the 30s as other teams kept improving and as we replaced submissions. Every replacement restarts a submission's rating from 600. The final pair went up four hours before the lock.

![Every upload by date with the public score each held on October 4](https://raw.githubusercontent.com/spoutop/kaggriculture-replay-cloning/main/assets/g8_results.png)

| Approach | Result |
|---|---|
| Hand-written strategies (first week) | Public scores from about 400 to 2,710 |
| Public-notebook rebase with our own layers | About 2,700. The layers added little on the live ladder |
| Single cloned networks | Played complete games but lost close ones in some towns |
| Cloned ensembles | First entries above 2,850 and a best of 2,916 in the snapshot |
| Decode-time offsets and opening mechanisms | Kept after paired games against cloned opponents |
| PPO fine-tuning of the clone | Best checkpoint 0.70 against our live agent where its starting clone read 0.77 |

There was no clean ablation. The table is the development history in order.

---

## 6. Lessons

**92% action accuracy still lost games.** Our clones matched about 92% of recorded unit commands on held-out seats (PASS excluded) and about 83% of non-trivial market kinds. In full games some checkpoints with a worse imitation loss won more. One early mistake such as a missed hire or a seed bought a day late could put the agent in states the teacher never visited. So checkpoint selection used full games against cloned opponents as well as the curves.

**A team's replays are not one agent.** Teams upload new agents daily. A team's latest agent can differ from the one that produced its older games. We indexed every replay by submission id and chose which versions to pool on purpose.

**PPO never got a fair run.** We tried it four times. The first run started from a clone baked at a low temperature with a money-shaped reward and a league of scripted opponents. Its best checkpoint read 0.70 against our live agent where the clone read 0.77. A later run unlearned the clone's price suppression and fell from 0.54 to 0.30 against the league before we stopped it. The longest run started from random weights with an imitation leash and reached 0.66B steps in about 20 hours. It stalled near 0.5 against its panel and at the same network size 40 minutes of supervised cloning beat it. Every run was judged after hours on a noisy read and none passed a billion steps. Next time the PPO lineage gets a fixed budget up front and is judged by full games at the end of each stage.

**Market slots never see each other.** Each slot decodes alone and the missing-order rule patches the coordination by hand. A future experiment is an autoregressive market decoder that conditions each order on the ones before it.

---

## 7. Next time

![The choices to repeat and the choices to skip](https://raw.githubusercontent.com/spoutop/kaggriculture-replay-cloning/main/assets/g9_takeaways.png)

Thanks to the hosts and to the players whose public replays we used.