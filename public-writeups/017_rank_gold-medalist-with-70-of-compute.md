# Gold Medal Solution with Under $60 of Compute

I'm Yuan800, a high school junior, and this was my first time leading a team in a Kaggle competition. All the rented compute for our whole competition, GPU and CPU, came to **$59.78**. Each of our final models was trained from scratch on one rented RTX 5090, and the larger one took about 4.5 hours. Our final agents use no self-play and no RL, and every evaluation ran on CPU. This post explains how our plain behaviour-cloning (BC) agent got into the gold range, and what we learned on the way.

## 1. What we did

For most of the competition we built rule-based agents: hand-written schedulers, route splicing, opening counter-play, and planner + executor programs. They got us into the upper part of the board but stalled there. When we analysed our replays, the problem was always the same. We could copy *what* the top teams built, but our executors lost a large share of the throughput doing it.

In the last two days we went back to BC. We trained a Transformer on replays of top games and added a thin rule layer at inference time. Both of our final submissions, Final-192 and Final-256, come from this pipeline.

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F30586564%2F00ca6e73f059682f40aa23f1f279015f%2Ffig1-pipeline-16x9.png?generation=1792072673420990&alt=media)

*Figure 1. Our training and inference pipeline. Blue parts are learned, green parts are hand-written rules.*

## 2. Why BC worked this time

We had tried BC in August. Our model matched over 99% of common actions and still played badly. Three things had to change.

- **The action language had to survive the round trip.** In one early experiment, simply re-encoding quantities through our converter, without any training, turned an expert that won every game into one that lost every game. This time, before training anything, we checked that converting replays into labels and decoding the model's outputs back into game actions round-trips exactly.
- **Invalid requests are masked, not taught.** A raw request that the engine turns into PASS is removed from the loss. It is not used as a PASS label.
- **The whole team is decided together.** One decoder pass predicts every worker's action and an ordered list of market orders, so later orders can take into account the cash that earlier ones use.

## 3. Our model

A single Transformer reads the whole game state. In one pass it outputs an action for every unit and an ordered list of market orders. Final-192 and Final-256 differ mainly in width; they have 4.0M and 7.0M parameters. At inference, a shadow resolver commits orders one at a time against cash, seeds and shed space. An endgame routine then brings goods home and sells them.

## 4. Choosing the model by games, not by loss

Validation loss did not tell us which checkpoint was stronger. We played every candidate against our submitted Final-192 on the official engine, with both seat assignments. Most of the 256-wide run lost almost every game. The checkpoint with the lowest validation loss finished last in a round robin of four late 256 checkpoints plus Final-192 (32 fresh seeds, both seats for every pairing). Only the final checkpoint beat Final-192. We froze it and confirmed it on 64 seeds that had never been used for selection: **92 wins, 36 losses**.

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F30586564%2F0075229dd09102f220d6fcbd124e2c2b%2Fimage-1792071451616.png?generation=1792072683205931&alt=media)

*Figure 2. Win rate of our Final-256 checkpoints against Final-192. Each blue point is 64 games. The orange point is the frozen final model on fresh seeds, with a 95% bootstrap interval.*

Our explanation is the usual problem with BC. The loss measures fit on the expert's states, but a full game makes the policy recover from states that *its own* actions create, for 719 decisions in a row. t fuku's team saw the same thing in [their writeup](https://www.kaggle.com/competitions/kaggriculture/discussion/745783). In their runs, several seeds of the same recipe reached the same validation loss, yet won anywhere from 3 to 23 of 40 games against their reference.

## 5. What did not work

**RL on top of BC.** We tried KL-constrained post-training. It improved the sampled policy and made our deployed argmax policy worse. In one case, a tiny shift flipped the farmer's choice at hour 44 from SOUTH to PASS. In every one of the 64 games, the first decision where the two policies differed was this one, and the candidate went 25–3–36 (wins–draws–losses) against its own base. When the deployed policy is greedy, a small average KL is not the same as a small change in behaviour.

![](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F30586564%2F36e0a68c8bb4b5f649ecc8be97833041%2Fimage-1792071478543.png?generation=1792072706971390&alt=media)

*Figure 3. Action probabilities at the first divergence. The axis starts at 48%.*

**Fine-tuned branches and weight averaging.** Both of our branches had lower validation loss than the base and were individually weaker than it. Their average was weaker too.

## 6. Why our Final-256 could not beat Final-192 on the ladder

Locally, Final-256 beat Final-192 92–36 on fresh seeds. On the ladder it consistently rated below Final-192, and Final-192 is the version holding our score. The overall win rate was not the problem. Over the whole evaluation period Final-256 won 543 of 993 games and Final-192 won 529 of 1,000. What hurt Final-256 was a handful of almost one-sided matchups against strong teams ranked close to us. Final-192 played the same teams nearly evenly:

| Opponent | Final-192 | Final-256 |
|---|---:|---:|
| Majkel1337 | 24–28 | 1–57 |
| Luca | 23–29 | 7–48 |
| Boey | 18–23 | 6–29 |
| KawattaTaido | 22–31 | 1–26 |

*Wins–losses over the whole evaluation period.*

In Bradley–Terry-style rating, losing that reliably to opponents with similar ratings costs more than extra wins against weaker teams bring back. Once we corrected for opponent strength, our own estimate put Final-192 slightly above Final-256. To find out why, we sampled 80 replays of both versions against the same Majkel and Luca submissions. The town matters a lot here, so we split games by whether the town had a wool shop. Against Majkel, in towns without a wool shop (16–18 sampled games per version), Final-256's median final cash was 102.5k against 103.4k for Final-192, while Majkel finished with 114.7k against Final-256 and 99.3k against Final-192. Final-256 was further ahead on day 12, and the gap opened from day 15 onwards. In those towns Final-256 was not a worse farmer; it was a weaker competitor in the shared market and left more money for the other side. In wool-shop towns (only 6–8 games each), Final-256 also earned less itself (106.7k against 122.8k), so this is a direction, not a settled result. Against Luca, in towns without a wool shop, Final-256 earned about 7k less and Luca about 2.6k more. We could not pin the effect on one product, because with different seeds, the shops in each town dominate the product mix.

Our local test had only one opponent identity, Final-192 itself, and the two models share most of their training data. So the 92–36 tells us how 256 does against 192's habits, not against other styles. Next time we would check each candidate's record against the teams around us, and against the opponents our current version struggles with, before choosing the final two. We would also track our own money and the opponent's money separately, not just the margin.

This cost us more than our own rating. Between 3 and 14 October, by the per-game score changes the ladder reported, Majkel gained about 202 points from games against our two versions, mostly against Final-256, while its total rise over that period was about 113 points.

## 7. Limitations

**Ablations.** We did not have the compute to measure how much each rule (masks, resolver, endgame) contributed. That is the main open question we leave.

## Team contributions

- @yuan800: led the project; built our pipeline, training and evaluation.
- @jacqueszhelinzhang: the theoretical groundwork for our behaviour-cloning architecture.

## Acknowledgements

We used Claude Code as an assistant for replay analysis, debugging and running evaluations. Most of our CPU evaluations ran on an 8-core cloud server provided by Grok Bot.

Thanks to the hosts for the [daily top-episodes datasets](https://www.kaggle.com/datasets/kaggle/kaggriculture-episodes-index), which were the main source of our training data, and to every team whose replays we learned from (especially M & M & P & Q, whose games we weighted most). Thanks also to [nikital7](https://www.kaggle.com/code/nikital7/4000x-environment-speedup-kaggriculture) for the public notebook "4000x environment speedup", and to [destbreso](https://www.kaggle.com/code/destbreso/kagsim-the-engine-at-2000-episodes-per-second) for packaging it as `kagsim`. A fast engine that matches the official one on well-formed actions let us screen our earlier rule-based agents on a small CPU budget. All model-selection games in this post ran on the official engine.

We're busy with Q1 benchmark exams right now, so our code will be cleaned up and released later. Sorry for the wait!