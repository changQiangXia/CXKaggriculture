# 70th place: Replay BC, teacher selection, and a tomato rule

Our team, **NSK_54**, finished **70th out of 10,148 teams**. This write-up focuses on the replay-BC agent that set our final score: **4883.6 private**, with a public rating of **2612.0**. The private and public ratings use different scales.

Our final agent combined a **6.54M-parameter recurrent entity Transformer**, behavior cloning from public replays, and a small deterministic overlay. The biggest improvements came from choosing **strong, current teachers with compatible strategies**.

## The final agent

We represented the observation as **277 entity tokens**: one global token, 12 item tokens, 200 farm tiles, 32 own-unit slots, and 32 opponent-unit slots. Only public opponent information was included.

The encoder used four Transformer blocks, width 256, eight attention heads, and FFN width 1024. A pooled representation updated a **256-dimensional GRU** once per turn. Two single-block autoregressive decoders generated:

- Worker commands, in engine order: farmer first, then farmhands.
- Up to ten market orders, attending to both the board and the decoded worker commands.

Each decision was factorized into **operation → item → quantity**, where applicable.

After every choice, we updated a **shadow state** tracking stock, seeds, changed tiles, cash, hires, and market supply. The next decision received legality masks and features from that updated state. This prevented reuse of stock already consumed by another worker and allowed a sale to fund a later purchase in the same turn.

The network chose routes, work allocation, investments, and sales. The shadow handled local validity and accounting; it could not prevent every strategic mistake, such as two workers walking toward the same distant tile.

Inference was greedy. In one paired test with identical weights, greedy decoding scored **0.836**, versus **0.094** with temperature-1 sampling. Small sampled errors accumulated into failed economies.

Throughout this post, local **score = (wins + 0.5 × draws) / games**.

## Replay preparation

Our initial clean top-30 dataset contained **4,290 player trajectories**, or **3,084,510 observation–action pairs**, from 18 teams. Each trajectory contained one player's 719 decisions.

We re-simulated recorded games to reconstruct observations, aligned each observation with the following replay action entry, and converted commands into **what the engine actually executed**. Every converted trajectory had to reproduce both players' next observations when its labels were decoded and replayed.

Market positions required special care. Strong teachers often submitted standing SELL orders for goods they did not hold. Approximately 10% of elite teachers' submitted SELL orders executed nothing in one audit.

We represented those orders as positional **SKIPs**. Removing them would shift subsequent orders: the engine processes both players' market lists by index, so position affects execution timing.

We also tracked exact team identities and submission versions, filtered invalid games and incompatible engine versions, deduplicated episodes, and excluded evaluation seeds. Both seats of an episode stayed in the same data split. Ordinary teacher losses were retained.

## Choosing compatible teachers

The first observation was **identical across seeds**. A greedy policy therefore made the same opening decision in every game. When we mixed teachers with incompatible openings, the student sometimes combined purchases from one strategy with labor allocation from another.

One failed opening spent **2,893 of the initial 3,000 coins**, then lost its animals by day three. Small changes near an opening logit tie could change every rollout at once.

We grouped teacher versions into families using their **turn-0/turn-1 order signatures**. An early mixed-family fine-tune lost all 32 games against our scripted reference, while a compatible-family fine-tune won **107/128**, scoring 0.836.

Compatibility alone was insufficient. A later comparison kept the architecture, initialization, budget, and learning-rate schedule fixed while changing teacher strength within the same opening family:

| Teachers | Wins against the wheat-dump reference |
| --- | ---: |
| Current top-30, compatible family | 0/32 |
| Current top-eight, compatible family | 60/64 |

The top-eight teachers differed in investment pace, market behavior, and later execution, despite similar openings.

Our successful training chain progressively narrowed the demonstrations:

| Stage | Data | Budget |
| --- | --- | --- |
| Broad pretraining | 4,290 clean top-30 trajectories | Selected checkpoint after 14 epochs |
| Compatible-family refinement | Strong and elite teacher tiers | 18k + 9k updates |
| Current top-eight refinement | 877 compatible trajectories | 6k updates |
| Final specialist fine-tune | Newest compatible DSM, DECEM, and yuto083 versions | 12k updates |

The final dataset contained **213 trajectories, 197 for training**. Those 197 trajectories were the last fine-tuning set, following broad pretraining and intermediate refinement.

Adding older compatible data diluted the result. Several highly ranked off-family teachers also damaged the policy. For our model and budget, teacher compatibility, strength, and exact version mattered more than dataset size alone.

### Training details

We used masked cross-entropy over worker and market operation/item/quantity factors, with teacher-forced prefixes. A nominal update contained **eight trajectories × 64 turns = 512 rows**. GRU state was carried between chunks and detached at their boundaries.

AdamW used weight decay 0.01. Peak pretraining learning rate was 3e-4; the final fine-tunes decayed from 3e-5 to 5e-6.

Two smaller details helped define the training recipe:

- **Repeated-history weighting:** identical history prefixes received row weight `min(1, 25/m)`, where `m` was their multiplicity. This reduced repeated-opening dominance while preserving later unique behavior.
- **Fixed loss denominators:** normalizing each chunk separately had given the short 15-turn tail chunk about 4.3 times the per-row influence of a full chunk. We switched to fixed denominators.

These changes entered alongside the teacher-tier pipeline, so we did not isolate their individual contributions.

## The wheat dump: more targeted data made things worse

Eight of one BC version's first nine Kaggle losses came against opponents selling at least 20 wheat on turn zero. We reproduced the failure with a scripted opponent that submitted a large opening wheat sale.

The sale depressed wheat prices and squeezed our opening liquidity. Our policy reached zero cash, bought small amounts of feed, and fed animals that were not yet at risk. A cow unfed since day zero died at turn 48.

Our first hypothesis was missing coverage. We devoted **30% of a fine-tuning mixture** to teacher wins against these openings. It regressed:

| Attempt | Result |
| --- | --- |
| Targeted teacher wins against dump openers | Paired score change **−0.286**, 95% CI **[−0.531, −0.040]** |
| Current top-eight compatible teachers, including newer openings | **64/64 wins** on fresh seeds, mean margin about **+20.1k coins** |

The targeted model's own bank actually rose, but its market behavior helped the opponent even more. In a shared market, higher own income is an incomplete metric.

In this experiment, extra teacher examples did not teach reliable recovery from the student's mistakes. Stronger current teachers, including a more robust opening, were more effective.

## Detours: macro executors and RL

A macro-task policy produced our first major improvement. Instead of predicting individual movement steps, it predicted a task and destination, while a persistent executor handled routing and reservations. Wasted movement fell from **35.1% to 14.0%**, and the agent beat our handwritten baseline **50–0**.

Later, a higher-level planner became a bottleneck. Even when fed teachers' reconstructed investment schedules on 21 held-out games, it banked only about **55k**, against the teachers' **106k**. This diagnosed limitations of that executor's placement, labor, timing, and selling. We moved execution back into the network while retaining shadow-state accounting.

We also tried extensive PPO and self-play. A scratch run on the final-sized architecture reached **47M environment steps over 91 hours** without learning useful farming. One BC-initialized PPO branch improved its public rating from 1738.5 to 2322.0, but the local gain was insignificant and the ladder comparison included possible field drift.

The later BC chain overtook that branch. **No RL updates were applied to the final agent described here.**

## The tomato overlay

Our stronger BC agents still lost close games late. Across 94 losses from two versions, **62% were not behind at day 20**. On day 22, they averaged **0.9 tomato plants**, versus opponents' **7.9**.

A parallel LLM-selector experiment helped explore crop-timing changes. We distilled its useful tomato decision into deterministic code, matching **140/140 tested LLM decisions**.

The final rule replaced planned carrot-seed purchases with tomato seed on **engine days 16–19**, provided:

- Tomato price was at least 1.25 times base price and an unlocked shop bought tomatoes.
- Plants plus held seeds stayed within eight per tomato-buying shop.
- At least 300 coins remained after purchase.

Tomatoes produce four times before decaying, making planting time important for the late-season shortage.

The overlay also directed carried goods toward the shed during the final 20 steps and added final-step sales. Against the plain base on **96 fresh seeds, both seats**, with five rotating opponents, the complete overlay gained:

| Metric | Paired improvement, 95% CI |
| --- | ---: |
| Panel score | **+0.130 [0.072, 0.189]** |
| Final bank | **+1,456 [688, 2,224]** |

Its standalone leaderboard contribution remained unresolved: the plain control was retired before the private tournament. The evidence for this improvement is the paired local test.

## Evaluation and deployment

We selected checkpoints through **full greedy games**, using matched seeds, seats, and opponents, separate development and confirmation bands, and confidence intervals over seeds. External opponents and same-recipe retrains helped expose overfitting and training noise.

Offline accuracy could improve while play remained poor. One stage raised turn-exact accuracy from **0.085 to 0.248** without winning a game against the reference.

Deployment used a **NumPy policy in one file**, approximately 24.5 MB zipped. Export checks reproduced **2,876/2,876 action turns** between PyTorch and NumPy. Quiet-host p99 inference latency was approximately **0.28–0.29 seconds**.

We trained on an RTX 3090 Ti and a machine with four GTX 1080 Ti cards. Broad pretraining took about 12 hours; later 6,000-update fine-tunes took about 50 minutes on the four-card machine.

The experiments we would prioritize earlier next time are teacher-version audits, executor tests with true teacher targets, and full-game comparisons of proposed failure fixes. Those diagnostics repeatedly changed where we spent our effort.

## Acknowledgements

Thanks to the hosts and all teams sharing public replays, especially DSM, DECEM, and yuto083 for the final specialist demonstrations. Earlier stages also benefited from other public leaders. Our separate scripted-baseline line used Ahmed Berat Ozer's V43 agent, shared through sdy623's notebook under Apache-2.0.