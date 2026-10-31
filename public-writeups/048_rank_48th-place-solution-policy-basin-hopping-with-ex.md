> **来源 / Source**：Kaggle Kaggriculture 公开 write-up，第 48 名，队伍 **JB Bryant**。
> **原文**：https://www.kaggle.com/competitions/kaggriculture/writeups/48th-place-solution-policy-basin-hopping-with-ex
> 本文为比赛归档的离线副本，仅作技术参考；**版权归原作者所有**。
> 如作者要求撤下，请联系仓库所有者。

## 1 Game Overview and Acknowledgments

Kaggriculture is a two-player farming game. Both players manage land, grow crops, raise animals, hire workers, and trade on a shared market over a fixed season. The player with more cash in the bank at the end wins.

Each farm has $10\times10$ tiles divided into four quadrants. Only one quadrant is available initially; the remaining land must be purchased. There are five crops and three animals, each with different costs, production cycles, maintenance requirements, and products. Each worker takes one action per turn, while the market accepts up to ten ordered transactions. The default season lasts 30 days, with 24 turns per day. In the environment used for this project, a complete game contains 719 decision steps.

Production, transport, and trading are tightly coupled. Buying a seed produces no immediate income: a worker must choose a tile, plant, water, wait for production, harvest, return the goods to the shed, and sell them. Animal production also requires buildings, transport, feeding, and care. Labor, land, cash, and inventory capacity constrain all these operations.

The market changes the value of production decisions. Selling the same product increases shared inventory and lowers subsequent sale prices. Shops consume inventory periodically, creating demand. A new shop opens randomly every three days, up to eight shops, with duplicates allowed. The same production mix can therefore earn very different amounts under different shop sequences and opposing production capacities. Higher production does not necessarily yield more cash. Selling earlier can both raise your revenue and depress your opponent’s sale price.

Kaggriculture attracted 10,148 teams, making it the largest Featured competition in Kaggle’s history by team count at the time of writing. I finished 48th as a solo competitor with a final team score of 5004.4, earning a silver medal.

My final solution uses an **entity transformer with approximately 0.86M parameters**, directly producing native worker actions and market orders. Training followed three stages:

1. Behavior cloning on selected expert replays to establish basic farm management.
2. PPO and self-play starting from the cloned policy.
3. Further behavior cloning on newer expert data to change and improve the policy.

The representation and architecture went through earlier exploration. The three-stage training and evaluation described here were concentrated in the final 48 hours of the competition, using RTX 3090 and RTX 5090 GPUs, with approximately $30 in GPU rental costs during that period.

The final training path was **BC → PPO → BC**. The first two scores and approximate ranks below were recorded before those submissions were replaced. The last row gives both final submission scores.

![Table 1. Leaderboard progression](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2Fbdc365a2e7815ea5724d4752cb0ab3c1%2Ftable-01.svg?generation=1792224471308767&alt=media)

Both final submissions use the same architecture, with weights from Final BC20 and BC23 respectively, and argmax decoding. The result was a solo silver medal. Data selection, full-game evaluation, and computational efficiency were as important to this process as the network itself.

Thanks to the organizers for this interesting environment, and to the community for sharing implementations and experience. Public writeups by @yijiey Yijie Yuan, @pressman1 Isaiah Pressman, @ferdinandlimburg flg, and others in previous agent competitions informed my work on representation, training, performance optimization, and writing this report. Special thanks to **M & M & P & Q( @morimo @qistripute @piiiiiiiii @msd0110 ), DECEM @zy1343930734 , and @majkel1337 Majkel** for their high-quality public replays. These replays supported the entire project: observing expert behavior, building training datasets, and checking what the model had actually learned.

I am also grateful to WalkingLab for the open-source book and accompanying project, [*Hands-On Modern RL*](https://github.com/walkinglabs/hands-on-modern-rl). I learned a great deal from it, both about reinforcement learning algorithms and about organizing experiments.

For readers learning reinforcement learning, I also recommend Stanford’s [CS234: Reinforcement Learning](https://web.stanford.edu/class/cs234/). Its step-by-step explanations and derivations helped me connect formulas, algorithms, and training procedures that I had previously understood only in pieces. That clarity is especially valuable for self-learners.

Finally, thanks to the competitors who shared unsuccessful experiments and training observations in the discussion forum. Those exchanges helped me understand and investigate my own training problems.

## 2 Model Representation and Architecture

An important lesson I took from PTCG was that representation design is a critical first step in an RL project. Including a feature in the state does not guarantee that the policy can use it effectively. A clear relationship between actions does not guarantee that a model will learn that relationship from limited data.

Markets, tiles, workers, and production resources depend on one another in Kaggriculture. With limited time and compute, I wanted to make these relationships easier for the model to access and improve sample and computational efficiency. Alongside the entity transformer, I therefore added explicit connections between product demand, production options, and action heads.

For newcomers to RL or simulation competitions, my main advice is to inspect what the model sees, how actions are represented, and how relevant information reaches a decision. These choices determine how much the model must discover for itself and affect the efficiency of subsequent training.

### 2.1 Why an Entity Transformer?

Decisions depend on relationships between entities that change with the game state. Harvesting a mature melon tile requires considering the worker’s position and carried items, the tile’s yield, the time needed to return to the shed, market inventory, and the opponent’s incoming supply. Different actions need to attend to different entities.

An entity transformer preserves these individual entities and uses attention to learn conditional relationships between them. Workers can use tile and resource information; products can use both players’ production capacity and shop demand; tiles can use the remaining season and production requirements. Entities of the same type share encoders and network parameters, allowing learned relationships to transfer between workers and tiles. Position, type, and ownership features preserve their differences.

The contextualized entity representations feed into the action heads, conditioning individual worker actions and market orders. This structure fits the relational nature of the game and accommodates the product-to-production-option connections described below.

Each turn, the model reads the public state of both farms and the market, together with its own private inventory, and outputs worker actions and up to ten ordered market transactions.

### 2.2 Input Entities and Features

The state is encoded from the acting player’s perspective, consistently ordering the players as self and opponent. Both farms are public. The opponent’s shed inventory and items carried by workers are hidden.

The final global encoder uses a fixed sequence of **308 tokens**:

![Table 2. Input entities and features](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F5a8444d69dd38ba70fd6ca491ca307ff%2Ftable-02.svg?generation=1792224483960269&alt=media)

There are 32 worker slots per player. Inactive slots are excluded by the attention mask. Tiles retain fixed positions, including empty and locked tiles, because these still affect expansion, movement, and deployment decisions.

**Tile features** describe both the occupant and its position in the production cycle: time until the next output, time until decay, watering or feeding status, remaining time before neglect causes loss, harvestable quantity, fertilizer duration, and accumulated animal care bonuses. Coordinates, quadrant, and distance to the shed are also explicit features.

**Resource features** distinguish shed inventory, worker cargo, and products still on tiles. These are all assets, but become available for sale or reinvestment at different times. The model also receives rule-based ranges for near-term production, distinguishing resources already being produced from those not yet purchased.

**Market features** include current prices, shared inventory, our stored and in-transit goods, and the revenue from liquidating inventory under current market conditions. These quantities are calculated from the current state. Future execution prices also depend on the opponent’s sales.

Shop information enters through two paths: shop-type tokens and product-level demand aggregated from those shops. The model can access both which shops are open and the demand for each product.

### 2.3 Shared Transformer Encoder

![Final model architecture](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F2cf254a558b6f759ec4dae5193c6ba0a%2Fmodel-architecture.svg?generation=1792227466502942&alt=media)

*Figure 1. Entity encoding, product–tile relations, and worker and market action heads. The dashed box on the right is the value head used in PPO.*

Each entity type has its own two-layer MLP for raw features:

$$
\text{raw features}
\rightarrow 2d
\rightarrow \operatorname{GELU}
\rightarrow d.
$$

Entity-type, player, and resource-category embeddings are then added to form the global token sequence.

The final backbone has **5 layers, width 96, and 4 attention heads**. Each head has dimension 24; the FFN hidden width is 192. Every block uses pre-LayerNorm and residual connections:

$$
x' = x+\operatorname{Attention}(\operatorname{LN}(x)),
$$

$$
x_{\text{next}}
=x'+W_2\operatorname{GELU}\!\left(W_1\operatorname{LN}(x')\right).
$$

All valid entities participate in global self-attention. The resulting tile, worker, and product representations contain context from other entities.

The global encoder runs once per player perspective per turn. Sequential worker and market decoding reuse these representations, with smaller local computations incorporating previously selected actions. The full transformer is not rerun for every action.

### 2.4 Connecting Product Demand to Farm Actions

Putting shops and prices into the encoder does not guarantee that the action heads can easily use them.

For example, the global state may contain an ice cream shop, while buying a cow, building a pasture, placing the cow, and harvesting milk remain separate actions. If all actions read only a global vector, the network must learn their relationships to milk demand itself.

I therefore added explicit product and production-option connections after the global encoder.

First, each product representation rereads the raw market features and incorporates demand from open shops. Demand features include consumption volume, time until the next consumption, and known demand over the next 1, 3, and 6 days and the remainder of the season. “Known” includes only shops that have already opened.

Next, I construct eight **production-option representations**, one for each of the five crops and three animals. Each combines:

- The corresponding output product representation.
- The relevant seed or animal resource representation.
- Rule-based costs, time to first output, production interval, and yield.
- Tile requirements and conditions such as wheat consumption or fertilizer use.

Animals map directly to their products: geese to eggs, cows to milk, and sheep to wool. Purchasing an animal and operating its production chain can therefore share product information.

The model then computes relations between our 100 tiles and the eight production options:

$$
R_{i,p}=f(T_i,E_p,G),
$$

where $T_i$ is a tile representation, $E_p$ is a production-option representation, and $G$ is the global context. The relation dimension is 16, giving a $100\times8\times16$ tensor computed after the global encoder, without adding global tokens.

This tensor is pooled in both directions: tile information is aggregated for each production option for market purchases, and production-option information is aggregated for each tile for worker decisions.

These relations condition the action heads, giving related actions access to the same supply, demand, and production information. The network chooses the purchases and tile operations.

### 2.5 Worker and Market Action Heads

#### Worker actions

The worker head retains the native action vocabulary: movement, planting, watering, harvesting, fertilizing, building, feeding, care, digging, pickup, placement, unloading at the shed, and PASS.

Workers are decoded in the official execution order. Later workers read earlier selected actions and use the resulting local state and legality updates. If an earlier worker consumes a seed or takes an item from the shed, later workers choose under the updated resource constraints.

Action candidates read representations of their relevant entities directly:

![Table 3. Worker actions and their entity inputs](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2Fa7aad936a1a44f5e65124fcff83dcccb%2Ftable-03.svg?generation=1792224494221642&alt=media)

Movement remains a single-step directional choice. Directional context combines candidate tile representations with changes in Manhattan distance before and after movement. Distance-related biases are learned as part of directional scoring.

#### Market orders

The market head generates up to ten ordered transactions. Each order first selects a category, then a quantity. Subsequent orders read the cash, inventory, and purchase prefix produced by earlier orders.

A strawberry-seed purchase candidate reads the strawberry product and production-option representations. Buying a cow reads milk-related representations. Selling reads the corresponding product and shed information. The market head also reads the worker actions already selected for this turn, allowing conditional relationships between harvesting, unloading, and trading.

The quantity head uses a **three-component discretized logistic mixture** to produce integer quantities, clipped by inventory, funds, and model-specific quantity limits. Training uses quantity log-likelihood; submission inference uses deterministic quantity decoding.

Legality masks exclude actions that cannot currently execute. The model also imposes some additional constraints, such as seed inventory caps linked to unlocked land area. It preserves native action types, with legality and quantity constraints narrowing the available choices.

These connections improve information flow between actions. Completing production after a purchase, or harvesting, returning, and liquidating before the season ends, still has to be learned. Those behaviors remained important issues in the experiments below.

### 2.6 Choosing the Model Size

In PTCG, I had underestimated the capacity of a small transformer. Isaiah’s [*Scaling Reinforcement Learning to the Stars*](https://www.kaggle.com/competitions/orbit-wars/writeups/1st-place-solution-scaling-reinforcement-learnin) showed the art of scaling up models and training while accounting for deployment constraints. These experiences motivated a practical comparison of model capacity, learning speed, and computational cost.

Before choosing the final size, I compared three models with the same entity and action design. All were randomly initialized and trained for one complete epoch on the same **1,404 Majkel replays**, using one **RTX 5090 32GB**, BF16, batch size 64, and no entropy regularization.

![Table 4. Model sizes and training time](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F686aaca841c864e5fade09e1ae507f4e%2Ftable-04.svg?generation=1792224516579359&alt=media)

The action-fitting results were:

![Table 5. Action fitting after one epoch](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F788d99fcc3fd721bc3b6d66d7a3ba4ba%2Ftable-05.svg?generation=1792227176070892&alt=media)

Deep was substantially underfit. Mid had slightly better fitting metrics than Small, but that ordering did not carry over to head-to-head strength. The following games used deterministic decoding and fixed seats, without seat swapping. Throughout this report, **cash margin** means our terminal bank cash minus the opponent’s.

![Table 6. Head-to-head model comparison](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2Fc0a95137a5c17ffff3c7ec76c2aca74c%2Ftable-06.svg?generation=1792227188334229&alt=media)

The 512-game panel extends the original panel and includes the previous 200 seeds. This comparison covers one initialization and one epoch. Deep increases both width and depth, so the results do not establish a general model-scaling relationship.

For the available budget, Small was an attractive choice: faster training, accuracy close to Mid, and stronger head-to-head results. I used **d96, 5 layers, and 308 tokens** for subsequent training.

I also tried reducing the global sequence to 134 tokens. Tile summaries replaced the 200 individual tiles in global attention, with cross-attention updating the detailed tile representations afterward. Training throughput improved by approximately 7.7% after one epoch, but its win rate against the 308-token model was only **40.82%** over 512 games. I retained full tile participation in global attention to preserve detailed representation.

These experiments shaped the remaining compute allocation. The small model could already express useful farm management, so I put more computation into data, training iterations, and full-game evaluation.

## 3 First BC Stage: Pretraining and Data Selection

After choosing d96, I randomly initialized a fresh network and trained on selected expert replays. This stage focused on completing production chains, expanding farm area, and converting output into cash. The model-size experiment used Majkel data; this pretraining stage used DSM, DECEM, and M & M & P & Q.

### 3.1 Data Sources and Teacher Perspectives

From the official daily bundles, I selected DSM and DECEM games from September 24–25 and M & M & P & Q games from September 28. I retained perspectives from those teams that had unlocked all four quadrants by the end of the game. Both winning and losing perspectives were eligible.

![Table 7. Pretraining data sources](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2Fc43c4e9a6c23b6569debcf769a5f7780%2Ftable-07.svg?generation=1792227198455261&alt=media)

These perspectives came from **611 complete games**. A game can provide two eligible perspectives, so game counts and teacher-perspective counts are recorded separately. With 719 decision steps per game, the dataset contained 439,309 environment states and 481,730 valid perspective-level state–action samples.

All data was used for training. Training-set action accuracy tracked fitting progress; full-game win rate, cash, and cash margin guided checkpoint selection.

### 3.2 Converting Replays into Training Samples

Each sample contains the state before action execution, a public-information ledger, and that turn’s worker actions and market orders. Replay actions are converted into the categories and quantities described in Chapter 2, then normalized using worker and order prefixes to handle invalid operations and quantity boundaries.

Both player perspectives are stored, with an `actor_mask` identifying the teachers used for training. Only selected perspectives contribute to the loss. Inputs respect the acting player’s visibility, with opponent private inventory estimated from public information.

Training uses teacher forcing: decoding a later worker or market order uses the expert’s preceding actions. This supplies supervision for a specific conditional decision. For example, the second purchase sees the first order’s effect on funds and inventory; later workers see local changes caused by earlier operations.

Games are stored as compressed shards, loaded in batches, with every state visited during a complete epoch. I also tracked the fraction of targets rejected by legality processing. It was 0 in this training run.

### 3.3 Fast Simulation and Parity Validation

Full-game evaluation and PPO require many state transitions. With GPT’s assistance, I ported the official Python environment’s core rules to C++ and built a batched simulator for the standard competition configuration. Simulation runs on the CPU; batched policy inference and training run on the GPU.

Farm state, tiles, worker positions and cargo, shed inventory, and market state are stored in contiguous fixed-size arrays. Python submits both players’ actions through a shared-library batch interface. OpenMP advances environments in parallel. Product prices are precomputed from the rules into lookup tables. Worker actions, market transactions, crop and animal updates, and end-of-day events retain the official processing order.

Rule parity was essential. Weed draws and shop openings are explicit inputs, allowing both implementations to execute the same actions under the same exogenous events. Replay validation starts from the official state and executes both players’ complete action sequences. Every step compares all encoded farm and market fields, including cash, tiles, worker positions, carried items and their ordering, shed inventory, seeds, purchased land, and shop counts. Terminal cash and termination status are checked as well.

An early validation run recorded:

![Table 8. C++ simulator parity validation](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F9d191e9edc3da6ee003da6356020e184%2Ftable-08.svg?generation=1792227210571344&alt=media)

This timing came from stepping individual games through the C++ interface. It includes Python calls and state copying, and excludes policy inference and validation comparisons. End-to-end batched rollout speed also depends on model inference, feature processing, data transfer, and backward updates.

Explicit random-event inputs also enabled later grouped resampling: shop sequences and exogenous weed draws could be held fixed while policy actions changed. The validation aligns actual events and transitions. Using the same integer seed alone does not ensure identical random sequences in Python and C++.

Accelerating the heuristic opponent was separate work. I also ported community heuristic path execution and related farm-management logic to C++. Fast v104 and full v109 differ in implementation and management logic; evaluations below identify the version used. Environment-rule parity and heuristic-action parity were checked separately.

### 3.4 Objective and Training Configuration

The loss combines worker actions, market categories, and their quantity likelihoods:

$$
L_{\mathrm{BC}}
=L_{\mathrm{worker\ action}}
+L_{\mathrm{worker\ quantity}}
+L_{\mathrm{market\ intent}}
+L_{\mathrm{market\ quantity}}.
$$

Each term is normalized over its valid targets. Action categories use cross-entropy with hard expert labels; operations requiring a quantity use the quantity distribution’s negative log-likelihood. PASS and market STOP retain ordinary weights, and the quantity-loss coefficient is 1. Only the actor is trained; critic and auxiliary-prediction loss coefficients are 0.

![Table 9. First BC stage: training configuration](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F33656e92ba6a6ba570ee01c5695cc245%2Ftable-09.svg?generation=1792227219238537&alt=media)

A warmed-up epoch processes approximately 439,309 environment states on two GPUs. At epoch 37, logged throughput was 2,338 states/s, or approximately 3.1 minutes per epoch, followed by separate match evaluation.

### 3.5 Progress and Checkpoint Selection

After each epoch, I evaluated deterministic decoding against fast v104, a community heuristic accelerated through a GPT-assisted C++ port. Evaluations initially used 50 games and increased to 512 from epoch 24. Our policy always occupied seat 0, using a panel with the same starting seed.

![First BC stage: win rate and cash](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F9b88ac0865dcf255a91a6b648658ad3c%2Fbc-pretraining.svg?generation=1792227448433178&alt=media)

*Figure 2. Win rate, both players’ mean terminal cash, and mean cash margin against fixed v104. The dashed vertical line marks the increase from 50 to 512 evaluation games; the dotted line marks the selected BC37.*

Early policies were weak: neither epoch 1 nor epoch 10 won any of the 50 evaluation games. At epoch 30, the 512-game win rate reached 45.90%, with a mean cash margin of −1,335. Epoch 37 reached 85.35% and +9,164.

I also measured land use because reliably using the fourth quadrant was a training goal. In BC37’s 512 games against v104, it unlocked the fourth quadrant in every game, with a median unlock day of 11. That quadrant contributed approximately 302 crop tile-days and 19.5 animal tile-days per game. Expansion had become productive activity.

By epoch 45, training loss and action accuracy improved, but match results did not improve alongside them:

![Table 10. BC37 and BC45: fitting and match strength](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F4f4a528c6fc7e0bfc947c924d72ecd59%2Ftable-10.svg?generation=1792227230199586&alt=media)

The gap became clearer against the submitted full v109 heuristic. Both evaluations used the same 512 seeds, fixed seats, and deterministic decoding:

![Table 11. BC37 and BC45 against v109](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F32a6768c501e86135cfc3afd731774f2%2Ftable-11.svg?generation=1792228073155105&alt=media)

BC45 also won only 42.97% of its direct games against BC37. I chose BC37 for PPO.

Action fitting can improve while complete-game strength fluctuates. Performance against one heuristic can also differ substantially from performance against another. I therefore saved every epoch and considered fixed-panel evaluations, other opponents, and direct checkpoint matches together.

BC37 established usable expansion and production behavior. Its submission score was 1269.6, at approximately rank 3k/10k before replacement. Subsequent training started from this policy and optimized game returns.

## 4 PPO: From Imitation to Game Returns

BC37 could already expand and maintain production. I hoped PPO would improve purchasing, production choices, transport, and sales in response to the shared market, opposing capacity, and final returns. The model and native action space remained unchanged. Starting from BC37’s actor, I first trained a value head and then updated actor and critic jointly.

### 4.1 Critic Warm-Up

BC trained only the actor. Before PPO, I attached a value head to its 96-dimensional public-state context: $96\to96\to1$, with GELU between the layers and 9,409 parameters. It shares the entity transformer’s encoding and predicts the expected terminal return under the current policy.

During warm-up, the actor was frozen. Each round sampled 2,048 fresh complete games: 1,024 softmax games against fixed BC37 argmax and 1,024 games of dual-softmax self-play, all at temperature 1. Every state was supervised with its perspective’s realized terminal reward. The fixed opponent’s perspective was excluded. Both self-play perspectives received half weight, giving the two game groups equal total loss weight.

I ran 3 rounds, sampling 6,144 complete games in total. Each round used an 80/20 game-level training/validation split, holding out 205 games from each group, or 410 total. The value head was fitted for 20 epochs using Adam, learning rate $3\times10^{-4}$, and batch size 8,192. Each new round inherited the previous value head and sampled fresh games. The actor stayed fixed throughout.

![Table 12. Critic warm-up](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F86e9ec90ba7dd8424c91d52933c0a302%2Ftable-12.svg?generation=1792227240658978&alt=media)

Each round had a new validation set. Breaking down the third round’s dual-softmax validation games by game stage showed better discrimination later in the season:

![Table 13. Critic validation by game stage](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F668870c2f7ae81805f367fc286ace3fe%2Ftable-13.svg?generation=1792227251242915&alt=media)

The fixed-BC37 group required attention to class balance. Its late-game return-sign accuracy after round 3 was 84.55%, while always predicting a loss would achieve 86.83%. I therefore also checked correlation and error relative to a constant predictor. Late-game self-play MSE was 0.962, compared with 1.106 for the constant baseline. Early-game predictions remained weak. Warm-up established an initial value estimate; finer distinctions between states still needed to be learned during training.

### 4.2 Opponents and Terminal Reward

PPO used 4 RTX 3090 24GB GPUs with 2,048 parallel environments, or 512 per GPU. The opponent mix continued the warm-up configuration:

- 50%: current-policy softmax against fixed BC37 argmax.
- 50%: dual-softmax self-play with the current policy.

Fixed BC37 supplied a stable reference, while self-play supplied an evolving opponent. The two groups had equal total loss weight. Sampling used temperature 1, and shop sequences were generated normally by the environment.

Rewards were terminal only. For terminal bank cash $M_i$ and $M_j$, I used:

$$
r_i=\operatorname{sign}(M_i-M_j)
 +0.1\tanh\left(\frac{M_i-M_j}{20000}\right).
$$

A win, draw, or loss contributes $+1,0,-1$. The cash-margin term has magnitude below 0.1, distinguishing returns within wins or losses while keeping the game outcome dominant. Rewards are zero-sum, and intermediate environment rewards are 0.

### 4.3 Rollouts, GAE, and Updates

A complete game contains 719 decision steps. I split the season into $240+240+239$ rollout segments, carrying environment state across segments and updating PPO after each segment. Ordinary truncations bootstrap from the next state’s value; true terminal states use zero continuation value.

GAE used $\gamma=1$ and $\lambda=0.97$:

$$
\delta_t=r_t+\gamma(1-d_t)V(s_{t+1})-V(s_t),
\qquad
\hat A_t=\delta_t+\gamma\lambda(1-d_t)\hat A_{t+1},
$$

where $d_t$ indicates environment termination. The value target is $\hat A_t+V_{\mathrm{old}}(s_t)$. Setting $\gamma=1$ retains the full terminal return, while $\lambda$ controls the weighting of value estimates and longer return paths in the multistep advantage. Advantages were normalized across the entire rollout batch, weighted by the learning perspectives.

![Table 14. PPO training configuration](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F7c2ab63924533a29c932d204a35dfecb%2Ftable-14.svg?generation=1792227271452495&alt=media)

A 240-turn window contains $2048\times240=491,520$ environment transitions, divided into 16 logical minibatches and 16 optimizer steps. Each step accumulates gradients over 60 global microbatches before updating parameters. One optimization epoch traverses that rollout batch once. Self-play transitions include both learning perspectives; fixed-opponent games use only our perspective.

The final 239-turn window contains 489,472 transitions. After shuffling, the implementation drops 6,144 so the data divides into 16 logical minibatches with global microbatch size 512. During PPO, the actor, shared encoder, and value head are updated jointly. The policy uses the clipped surrogate objective, and the value loss uses clipped MSE.

### 4.4 Win Rate and Cash against BC37

After every three updates, corresponding to one batch of complete seasons, the current checkpoint’s argmax policy played fixed BC37 argmax. Each evaluation used 512 independent seeds, with our policy in seat 0 and starting seed 2026092901. The same panel was reused throughout this stage to compare updates.

![PPO against BC37: win rate and cash](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F58ab808658e0835cd08ce66d4116d695%2Fppo-bc37.svg?generation=1792227483572263&alt=media)

*Figure 3. Win rate, both players’ mean terminal cash, and mean cash margin against fixed BC37. Each point represents the same 512-game panel. Lines connect raw evaluations without smoothing. The vertical dotted line marks PPO15.*

![Table 15. PPO against fixed BC37](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2Fb1545e30820bd13b18f746e212542470%2Ftable-15.svg?generation=1792227280678955&alt=media)

Win rate and mean cash margin generally moved together. PPO15 achieved both the highest win rate and the largest mean margin. Median cash was 102,564 for our policy and 97,941.5 for the opponent, indicating that the improvement extended across a substantial part of this panel.

Because the market is shared, the fixed opponent’s cash also changes with our policy. PPO15’s advantage combined higher revenue for us with lower revenue for the opponent. Both cash curves matter: our cash alone misses the effect of supply and sale timing on opposing revenue.

I saved every update and selected PPO15. Its 79.69% win rate comes from the fixed panel used for selection. After fixing a submission startup issue, PPO15’s leaderboard score was 2177.2, compared with BC37’s 1269.6. Before replacement, PPO15 had stabilized in the silver-medal range and won 21 of its latest 30 ladder games, or 70%. Those ladder games had different opponents and environments from the fixed BC37 evaluation.

### 4.5 Repeated Regressions and Policy Basins

PPO produced a real improvement, but continued training was unstable. The win rate against BC37 rose to 67.97% at update 6, fell to 47.66% at update 12, reached 79.69% at update 15, then dropped to 55.47% at update 18. Updates 21 and 33 approached the peak again, while update 39 returned to 50.98%. Mean cash margin fell from its peak of +5,249 to −103. Joint declines in win rate and margin on the same panel showed that some updates damaged previously acquired match strength.

Across several PPO runs, I repeatedly encountered this pattern of policy collapse: short-term gains followed by regression, prompting a rollback to an earlier checkpoint. Here, collapse describes a substantial loss of match performance. The logs did not establish convergence to a single-action distribution.

Exploration was another difficulty. BC had already established a fairly consistent way of running the farm, with low probabilities for some purchases and production combinations. Individual actions remained stochastic, yet complete production mixes often changed little. Purchasing, building, placing, maintaining, harvesting, and selling depend on one another. Exploring a new route requires several stages to work together. A newly sampled purchase may be followed by familiar execution behavior, leaving no competitive output.

This is the policy-basin behavior I was concerned with: training adjusts familiar management patterns while struggling to discover substantially different, effective ones. [Other competitors reported](https://www.kaggle.com/competitions/kaggriculture/discussion/736917) regressions from PPO or additional imitation data after BC reached a certain level, along with accumulated errors in atomic-action imitation. These observations resembled the instability I encountered.

#### Sale-timing controls: local cash improvements and advantage estimates

Repeated PPO regressions led me to ask whether local cash improvements verifiable from the rules were consistently reflected in value and advantage estimates. I constructed controlled sale-timing comparisons using PPO15.

Starting from real states with existing inventory, I changed only sale timing, held other operations fixed, and compared outcomes after three turns. All 56 pairs were checked for identical window-end engine states except for the two players’ cash. Earlier sales produced a larger cash advantage, yet the critic assigned the resulting state a lower value in 10 pairs.

I then calculated local GAE over the three-turn window. With $\gamma=1,\lambda=0.97$, the earlier-sale branch had lower local GAE in 25 of 56 pairs. Raising $\lambda$ to 0.995 reduced that count to 14. With $\lambda=1$, it was 10, matching the number of pairs with lower window-end value estimates.

![Table 16. Sale-timing controls: local GAE rankings](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F25f70f2ef452fedff8b3292eb3654864%2Ftable-16.svg?generation=1792227295754008&alt=media)

In one milk-sale pair, selling earlier increased our cash by 208 and reduced the opponent’s by 283, improving the margin by 491 within three turns. All other window-end engine state was identical. The critic valued the earlier-sale endpoint more highly, but intermediate value changes gave it lower local GAE at $\lambda=0.995$. For a three-step window with no intermediate environment reward and $\gamma=1$, the advantage expands to:

$$
\hat A_t=-V_t+(1-\lambda)V_{t+1}
 +\lambda(1-\lambda)V_{t+2}+\lambda^2V_{t+3}.
$$

Intermediate values therefore contribute to the local advantage. At $\lambda=1$, those terms cancel. Since both branches start from the same state, their local GAE difference then depends only on the endpoint value difference. Increasing $\lambda$ reduces intermediate-value effects in this comparison, while the final ranking still depends on the endpoint prediction.

Even with otherwise identical window-end engine states, a clear local cash improvement did not always receive a higher critic value or local GAE. Changing λ affected the ranking, showing the practical role of intermediate estimates in advantage construction. This motivated closer examination of whether verifiable economic improvements could consistently produce useful learning signals.

This experiment checks alignment between three-turn cash changes and estimated signals. Expected terminal returns under the policy’s subsequent actions, and the actual update effects in the original training windows, require further investigation.

#### The gap between action exploration and effective updates

I also suspected a gap between per-action entropy rewards and useful exploration of farm management. Producing a new commodity requires coordinated purchasing, land use, worker actions, and sales. Starting without cows, milk production requires at least the following:

1. Buy a cow into the shed, then have a worker pick it up and carry it to the chosen tile.
2. Build a pasture and place the cow. Different workers can build and transport, but the structure must exist before placement.
3. Prepare wheat for feed. Wheat can be bought or grown, harvested, and returned to the shed. A feeding worker must carry it to the occupied pasture and execute FEED.
4. Continue feeding and wait for milk production. CARE can increase later output, while consuming worker actions.
5. Harvest the milk, bring it back, and sell it through a market order to realize cash.

These stages have different dependencies. Buying needs funds, building needs an empty tile, feeding needs carried wheat, production takes time, and income depends on transport and sale timing. A higher cow-purchase probability can simply add costs if workers fail to pick up, build, or place the animal. We observed purchased animals carried by workers for long periods without deployment. We also observed workers building and then digging up structures after pasture-building propensity was increased. Individual actions changed without completing the production objective.

Strawberries have a shorter chain, with similar problems. Seeds enter a separate inventory and can be planted directly on a chosen empty tile. Production still requires watering, waiting, harvesting, and transport; fertilizer changes ongoing yield. A policy accustomed to wheat may retain its tile and planting choices after buying more strawberry seeds. The seeds then remain unused, or establish only a small, unreliable amount of production.

An early attempt to cross a policy basin illustrated this problem. A checkpoint performed poorly against the heuristic under some high-strawberry-demand shop sequences. We added logit bias to strawberry-related purchases, increasing their sampling probability, but did not reliably establish strawberry production. Changing purchase propensity still required coordinated follow-up actions to create useful new trajectories. This experiment used an earlier checkpoint and configuration.

Per-action entropy rewards face the same issue. They preserve randomness within conditional action distributions without requiring those changes to form a complete production chain. After BC, some distributions are already concentrated, and execution may not adapt to changed purchases. More randomness can also disrupt reliable watering, feeding, and transport. Sampling may produce more new actions and more execution failures while yielding few complete, effective new production combinations. With terminal rewards, incomplete attempts often leave only their costs and little signal encouraging the new route.

Training also combines softmax against fixed argmax with dual-softmax self-play, while evaluation uses argmax on both sides. State and opponent distributions differ, and self-play opponents change during training. Better training loss or rollout performance must still translate into stronger deployed play. PPO clipping constrains probability ratios on sampled actions without guaranteeing monotonic fixed-panel win rates.

These investigations left two phenomena worth studying further: local cash improvements do not always align with value and advantage rankings, and individual-action exploration struggles to produce complete new production combinations. Both may affect learning efficiency and stability. Their actual contributions to PPO regression still need to be separated experimentally.

### 4.6 Parameter Changes and a Return to Expert Data

Before returning to BC, I continued trying to stabilize PPO. PPO15 provided a stronger starting point. I varied update windows, exploration strength, parallelism, and learning rate, while examining the critic’s local advantage signals. With the competition in its final day, time and compute were limited, making repeated short-lived gains especially costly.

The following attempts all evaluated against fixed PPO15 argmax:

![Table 17. PPO tuning attempts](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F370f4abdd8088953d822be83efcdf818%2Ftable-17.svg?generation=1792227304750477&alt=media)

Some attempts improved briefly without establishing stable progress. They may have received too few updates, although some earlier, longer runs had also regressed. In the final hours, I retained PPO15 and continued BC on 451 newly downloaded MMPQ games, supplying more complete, effective management trajectories.

These were the 451 M & M & P & Q (MMPQ) replays from September 29–30 collected by that point. I kept every MMPQ perspective, including losses, and added opposing perspectives that defeated MMPQ. This exposed the model to both the strong team’s play and successful responses to it. The second BC stage inherited PPO15’s actor, used action cross-entropy, saved every epoch, and evaluated 512 games against fixed PPO15 argmax.

This change came after repeated tuning and audits had failed to produce stable progress, with little competition time remaining. Recent expert replays provided completed purchasing, production, transport, and sale sequences. The next question was whether learning from them could change established management patterns and improve win rate and cash margin. That became the next experiment.

## 5 Second BC Stage: Policy Basin Hopping

The second BC stage started from PPO15 and continued training on newer expert replays. Architecture, state features, and native actions stayed the same. Supervision came from more recent MMPQ games, followed by additional DECEM games.

Earlier PPO training largely adjusted familiar management patterns and struggled to sample new effective production combinations. The new expert trajectories supplied directions for crossing policy basins: purchases, production choices, transport, and sales could change together under new demonstrations.

The process involved substantial strength fluctuations. A game contains 719 decision steps, each involving multiple workers and market orders. BC learns local actions on expert states, while actual play requires the model to sustain an entire season. A changed purchase, planting decision, or return route alters later cash, inventory, positions, and capacity, creating different decision conditions. State-distribution shift and error accumulation in imitation learning are also discussed in [DAgger](https://proceedings.mlr.press/v15/ross11a.html).

Different stages of a new production route may be learned at different times. Cow purchases might increase before pasture construction, transport, placement, and feeding adapt, raising costs while reducing output. The route becomes profitable only when these stages work together. Routine and critical actions also affect outcomes differently: better fitting of frequent movement and maintenance actions can coexist with worse purchasing, crop replacement, or endgame return decisions.

Argmax decoding adds another source of sensitivity. When two close action probabilities exchange rank, a small parameter change can switch a critical choice and redirect the entire trajectory. Per-epoch cross-entropy and action accuracy therefore only partially describe complete-game strength.

I observed something similar when training LLMs to solve mathematics problems: among problems near the model’s current policy capability boundary, success rates on those requiring long completions often fluctuated more during training than on those requiring short completions. This is an observation from my own training experience. It offers an analogy here: longer solutions and management trajectories need more local decisions to combine into a successful result, and better local fitting need not immediately improve complete-task success. Together with the match curves, I considered error accumulation, asynchronous adaptation across production stages, and argmax switches in critical actions as possible sources of BC strength fluctuations.

In Kaggriculture, the observed policy basin consisted of a fairly consistent management pattern: the market favored certain seeds or animals, workers deployed and maintained familiar production, and similar product mixes emerged. Exploring alternatives required several conditional actions to change together. Milk production, for example, needs cow and feed purchases, pasture allocation, animal transport and placement, feeding, harvesting, and sales. Partial changes often increase costs or interrupt production before generating useful returns, leaving little encouragement from game rewards.

Expert trajectories supervise these dependent stages and move the policy between different management patterns. As parameters change, shifts in key action rankings can produce jumps in the purchasing, production, and selling combinations executed by argmax. Policy basin hopping also comes with repeated strength fluctuations, making per-epoch evaluation important for retaining stronger policies.

### 5.1 Expert Data and Perspective Selection

The initial dataset contained 451 MMPQ games from September 29–30 collected by that point. Every MMPQ perspective was retained, regardless of outcome. If an opponent defeated MMPQ, the winning opponent’s perspective was retained as well. MMPQ mirror matches contributed both perspectives.

This captures how a strong team operates under different market and opponent conditions, together with successful ways to beat it. Losing expert perspectives still contain many useful production and execution decisions. Perspective selection determines which actions enter the BC loss; inputs retain the full public state and the acting player’s private state.

Data preparation reused the native-action conversion. It checked complete season length, environment configuration, team identities, terminal completion, and source-file checksums before saving compressed state and label shards. Each game contained 719 decision states, with separate supervision masks for both players. The shared game state was stored once.

The dataset expanded twice during training:

![Table 18. Second BC stage: dataset expansion](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F5a8efb3c473a5c64cfe28a8d83adbb8d%2Ftable-18.svg?generation=1792227313230691&alt=media)

The final addition’s conversion manifest contained 115 games, including 2 duplicates of the previous 556, producing 669 unique games. Both MMPQ and DECEM followed the rule of all target-team perspectives plus opponents that beat them. Games, perspectives, and states are counted separately.

### 5.2 Training and Evaluation

Training used categorical cross-entropy and quantity negative log-likelihood with hard expert labels and target confidence 1. Both worker and market heads used teacher forcing. Every complete epoch traversed the current dataset across days 1–30. All selected data was used for training.

![Table 19. Second BC stage: training configuration](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F920a22b455b9912abd70e31964f0fa0c%2Ftable-19.svg?generation=1792227321640315&alt=media)

Only the actor was optimized, with no extra entropy regularization. The first stage loaded PPO15’s model parameters and initialized a fresh BC optimizer. Continuation after BC22 inherited training state. The final addition of DECEM data again initialized a new training run from BC87’s parameters, restarting epoch numbering at 1. I call the latter checkpoints **Final BC20 / BC23** to distinguish them from earlier epochs with the same numbers.

Fixed-panel evaluations used argmax on both sides, always placing our policy in seat 0 without swapping. The first three stages used starting seed 2026092901 and 512 games per evaluation. The final stage used 2026105001. Additional cross-opponent evaluations used fresh seeds and were recorded separately.

### 5.3 Updating the Fixed Evaluation Opponent

Once win rate against an old benchmark became high, that opponent offered less discrimination: further gains had little room to appear in win rate. I progressively froze stronger checkpoints as new evaluation references, keeping the benchmark challenging while checking whether later policies could reliably beat the preceding stage.

![Table 20. Successive evaluation references](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F7b3565e4daa6fc89c8b68d178eb188a0%2Ftable-20.svg?generation=1792227333943309&alt=media)

Stage A initially ran through BC25. After reviewing the results, I rolled back to BC22, made it the fixed opponent for stage B, and resumed from epoch 23. After selecting BC50 in stage B, continuation actually started from the already saved BC51. The first complete evaluation against the new reference was at epoch 52. After BC61, I added 105 replays while keeping BC50 as the opponent.

Stage C continued through BC91, after which BC87 became the starting point and fixed opponent for the next stage. Other training attempts took place in between; the final expert-BC branch restarted from the retained BC87. Those branches are discussed in Chapter 6. Final BC20 and BC23 became submission candidates and were not used as subsequent training benchmarks.

The second BC stage therefore had four evaluation references—PPO15, BC22, BC50, and BC87—with three changes. Win rates against these different opponents represent progress within their respective stages.

### 5.4 Win Rate, Mean Cash, and Cash Margin

![Second BC stage: win rate and cash against successive references](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F1507451cedfde957388e1763f4586362%2Fsecond-bc.svg?generation=1792227493813112&alt=media)

*Figure 4. Win rate, both players’ mean terminal cash, and mean cash margin are plotted separately for the four fixed-opponent stages. Each point is 512 games; lines connect raw values without smoothing. Green vertical lines mark selected checkpoints. The gray dashed line in stage C marks the data expansion after BC61. Stage D restarts epoch numbering and uses a new seed panel.*

**Stage A: moving from PPO15 toward new expert trajectories.** After the first BC epoch, win rate against PPO15 was only 6.45%, with mean margin −16,537. The new supervision initially damaged the original policy’s match strength. Epoch 5 improved to 20.31% and −7,270; epoch 10 reached 55.66% and +597; epoch 22 reached 91.80% and +7,612. Our mean cash rose from 91,630 to 104,346 while the opponent’s fell from 108,166 to 96,735. Continued training still fluctuated sharply: epoch 24 dropped to 1.76% and −23,950, then epoch 25 recovered to 78.12% and +5,257. Saving every epoch and selecting through matches remained necessary under the same supervision.

**Stage B: continuing on the same data.** Resuming from BC22, epoch 23 won 26.37% against frozen BC22, with mean margin −4,299. Training continued to fluctuate: epoch 30 won only 25.39%, epoch 40 reached 61.52%, and epoch 50 reached 82.62% with +4,564. Further training on the same 451 games still produced policies that beat earlier checkpoints.

**Stage C: adding recent replays and challenging BC50.** Epoch 52 reached 30.08% and −2,727; epoch 61 reached 46.88% and −576. After adding 105 games, epoch 62 fell to 32.81%, and epoch 70 to 20.12%. Performance later recovered: epoch 80 reached 64.26%, and epoch 87 reached 77.73% with +3,099. The data expansion again brought short-term regression that required continued training to assess.

**Stage D: adding DECEM data.** Restarting from BC87, the first epoch won 20.12% against BC87 with mean margin −3,589. Epoch 10 approached parity at 47.27% and −367. Final BC20 reached 57.81% and +565; Final BC23 reached 55.27% and +742. Improvements over this stronger starting point were now measured in hundreds of cash on average.

![Table 21. Selected checkpoints against their fixed references](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2Fe18b945a1f66adc5e693d6cc8a59bcf8%2Ftable-21.svg?generation=1792227343120639&alt=media)

None of these evaluations had draws. Win rate and margin usually moved together within each stage, but measure different things: Final BC20 had the higher win rate against BC87, while Final BC23 had the larger mean margin. Absolute cash also depends on opponent behavior, the shared market, and shop sequences. Both players’ cash and their difference should be considered together.

**Production mixes of adjacent checkpoints.** To examine behavioral changes behind strength fluctuations, I evaluated five consecutive stage-B checkpoints, BC46–50. Each played 256 complete games against fixed BC22, with argmax on both sides and our policy in seat 0. All five shared the same fresh seeds, with explicit shop sequences and exogenous random draws held fixed. Shop sequences matched exactly. The instrumented engine passed state-parity checks against the original engine for all 719 steps of every game.

The table gives our **mean production / mean sales per game**. Wheat is also used as feed, contributing to the gap between production and sales. Fertilizer production was not recorded, so only sales are shown. Win rates and margins refer to this 256-game panel.

![Table 22. Adjacent checkpoints: production and sales](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2Fd01f495e6e7d184c4e61dc45b0b8fd06%2Ftable-22.svg?generation=1792227353789835&alt=media)

![Sales across adjacent BC checkpoints under matched conditions](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F81d6b02568a40485bcec4c197841f9f3%2Fbc-production-mix.svg?generation=1792227458591451&alt=media)

*Figure 5. Mean sales per game for eight agricultural products in BC46–50 against fixed BC22. Each point represents 256 games with the same shop sequences and exogenous random draws. Panels have independent y-axes. “Range” is the difference between the highest and lowest mean sales across the five checkpoints. Lines connect raw statistics without smoothing.*

Strawberry and egg sales alternated particularly clearly. From BC46 to BC47, mean strawberry sales fell by 19.8 while eggs rose by 32.0. From BC47 to BC48, strawberries rose by 27.3 while eggs fell by 25.1. The next two epochs reversed direction again. Under identical environmental conditions, adjacent checkpoints produced different production and sales mixes alongside fluctuating strength. This gives direct behavioral evidence for the policy basin hopping discussed above: continued BC moved the policy between different management patterns, with changes visible in complete-game output and sales.

### 5.5 Fresh Seeds and Cross-Opponent Checks

BC22 won 89.36% against PPO15 on fresh seeds but only 61.23% against v109. PPO15 had previously won 60.94% against v109 on another fresh panel, a similar result. A large advantage over the preceding policy translated into little win-rate difference against another opponent. Production mix, shared supply, and sale timing may produce stylistic matchups in which one policy is especially effective against a particular opponent.

To investigate this dependence and evaluate strength more broadly, I cross-tested stronger policies against earlier checkpoints and the heuristic on fresh seeds. Each row below consists of independent complete games, with our policy in seat 0 and argmax on both sides. PPO15’s 256-game v109 evaluation and BC22’s 1,024-game evaluation used different fresh seed panels.

![Table 23. Cross-opponent evaluation on fresh seeds](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F3426962f34bdda67ffdebf727c9418bc%2Ftable-23.svg?generation=1792227362594225&alt=media)

BC50 and BC87 reached 99.61% and 99.80% against v109 on fresh seeds and retained clear advantages over older checkpoints. Final BC20 won 55.47% against BC87 with mean margin +594; Final BC23 won 99.90% against PPO15 with +15,788. Later progress increasingly involved smaller gains against stronger references.

Final BC20 and BC23 also played 1,024 direct games, with BC20 in seat 0: 468 wins, 1 draw, and 555 losses, with mean margin −255. Together with their different strengths on the BC87 panel, this led me to retain both submissions.

The final submissions used BC20 and BC23, with agent scores of 2662.5 and 2669.5 respectively. The final team score was **5004.4**, placing **48th out of 10,148** and earning a solo silver medal.

### 5.6 What This Stage Showed

With the same model and action space, continued training on newer expert data repeatedly produced checkpoints that beat earlier policies. I am grateful to the experts whose public replays became the most valuable training resource in the final stage.

“Garbage in, garbage out” applies to policy learning too. BC learns conditional decisions from its data. That data determines which management patterns the model encounters and how purchasing, production, transport, and sales fit together. High-quality expert trajectories contain production chains completed in actual games and show tradeoffs under different demand and opposing supply. They directly supervise effective behaviors that were difficult to obtain through our own sampling.

Error accumulation over long decision chains and temporary incompatibility between old and new behaviors can still cause substantial strength fluctuations. Amid those fluctuations, expert data brought observable gains: BC22, BC50, and BC87 each surpassed their fixed reference, and the final models retained clear advantages over older policies. This experience reinforced the importance of data quality. The decision trajectories supplied to a model matter as much as how it is optimized.

## 6 Unsuccessful Attempts and Difficulties

Repeated PPO regressions raised the possibility that local critic errors were affecting advantage estimates. A natural direction was to remove the critic, sample multiple trajectories under the same game conditions, and construct relative advantages from realized returns. GRPO or related within-group comparisons could reduce dependence on potentially inaccurate value estimates.

Since expert BC had already improved the policy, I first tried a simpler approach: retain better winning trajectories from resampling and learn them through BC.

### 6.1 Resampling Wins under Fixed Game Conditions

Starting from BC87, I ran 1,024 argmax self-play games. For the 678 games with a winner, the original loser was resampled with temperature-1 softmax while the original winner continued using BC87 argmax. The opponent made fresh decisions on the states actually reached in each branch.

Branches within a group shared shop sequences and exogenous weed draws. Weed draws were fixed by turn, original seat, and tile index; actual weed spawning still depended on whether the tile was empty. Shops were revealed to the policy only when they opened. This held exogenous conditions fixed while comparing different management behavior.

Eight samples per group produced 5,424 branches, with 0 shop-sequence mismatches:

![Table 24. Resampling under fixed game conditions](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F86a6fc2b52f09812b82237487eeb55e7%2Ftable-24.svg?generation=1792227370600141&alt=media)

The original loser’s baseline mean margin was −1,261. Across all softmax branches it was −5,920, while selecting the best of eight per group gave +2,190. Average softmax play was worse, but repeated sampling could find wins in many originally losing games. The earlier difficulty of sampling almost no alternative effective strategies had eased at this checkpoint.

To reduce sampling costs, I lowered the group size to 4. Using only the first four samples from the existing data reduced loss-to-win coverage to 45.87%. I then expanded collection through more independent baseline games.

### 6.2 BC on Selected Wins

The main collection included losses and draws. For losses, the original loser was resampled. For draws, one side was randomly selected for softmax while the other remained argmax. Each group used 4 samples at temperature 1, retaining only the winning branch with the largest cash margin. Groups without a win were skipped.

Six collection batches retained 2,761 winning trajectories, or 1,985,159 environment decision states. Training started from BC87 and supervised only the selected winner’s actions, with batch size 1,024, learning rate $3\times10^{-4}$, hard-label cross-entropy, and quantity negative log-likelihood. All training data came from these resampled wins.

This was win-filtered BC. Within-group comparisons selected data; supervised losses performed the update. After each epoch, the argmax policy played 512 games against fixed BC87:

![Table 25. Win-filtered BC against BC87](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F21719742%2F91b9c6be9b5ca720f01263e304a1782d%2Ftable-25.svg?generation=1792227383617572&alt=media)

All four epochs were substantially weaker than the frozen starting policy. Sampling found wins, but supervised training on those wins caused regression. With approximately two hours remaining, I stopped this branch, returned to BC87, and continued training on new MMPQ and DECEM expert data.

### 6.3 Data Quality and Action-Level Credit

This attempt made me reconsider which winning trajectories are useful training data.

The first issue is coverage and data mix. Collection focused on scenarios where the original policy lost or drew and limited resampling could find a win. Games the policy already handled well and the original expert trajectories were excluded. Adapting to the resampled data may have damaged existing capabilities. One possible improvement is to mix trajectories where the original policy reliably wins as anchors, alongside resampled wins and expert data, while expanding coverage over independent games.

The second issue is credit assignment. I focused on finding wins and underestimated the gap between trajectory-level labels and action-level supervision. A temperature-1 winning trajectory can contain critical good decisions, inefficient operations, and choices that happened to work out. BC raises the probability of every supervised action, including poor ones. Selecting only the highest-margin win in each group may also favor behavior combinations whose advantage is difficult to reproduce reliably.

Execution quality may differ between expert trajectories and self-sampled wins. Expert play often sustains purchasing, deployment, maintenance, and sales throughout the game. An occasional win by the current policy can still contain many inefficient actions. Winning is a useful filter, but it does not identify which individual behaviors deserve reinforcement.

Dataset size, coverage, data mix, and action-level credit are all possible contributors to the regression. The second expert-BC stage also showed declines followed by recovery, so four epochs were insufficient to establish this branch’s longer-term trajectory. Before the deadline, I prioritized the expert-data route that had already produced improvements. Mixing anchors, scaling sampling, and directly updating with within-group relative advantages remain directions for future work.

## 7 Discussion and Limitations

### 7.1 Game Structure and Credit Assignment

This competition brought me face to face with a classic RL difficulty in a real training problem: **credit assignment**.

A complete Kaggriculture game contains 719 environment transitions. At each step, both players submit a set of worker commands and market orders. The number of native actions issued by one player over a game is:

$$
N_{\mathrm{actions}}
=\sum_{t=0}^{718}(W_t+O_t),
$$

where $W_t$ includes the main farmer and active hired workers, and $O_t$ is the number of market orders. In two locally inspected, successfully completed submission replays, a player issued approximately 8,654 commands per game on average, including PASS and movement.

These actions have specific dependencies before they generate income. Buying an animal requires later building, transport, placement, and feeding to produce anything. Harvested goods must return to the shed and be sold in time. An early return may secure a better sale price while sacrificing extra yield from another tile along the route. Multiple workers further couple these choices through shared time and resources.

Even when a trajectory achieves a better result, identifying the actions responsible remains difficult. PPO constructs per-step signals through the critic and GAE. The win filtering in Chapter 6 selects data using whole-game outcomes, then supervises the actions within it. Both face the problem of assigning management outcomes to individual choices.

The sale-timing controls made this concrete: when all other window-end engine state was identical, earlier sales produced verifiable cash improvements without consistently higher critic values or local GAE. This motivated inspecting value and advantage estimates while distinguishing local economic gains, expected terminal returns under the current policy, and the effect of actual gradient updates.

### 7.2 Exploring Complete Management Strategies

Effective production requires several prerequisite actions to work together.

Exploring milk production involves buying a cow, preparing a pasture, transporting and placing the animal, carrying feed, feeding, waiting for output, harvesting, and selling. If several required stages have low conditional probability under the current policy, the complete route is unlikely to appear in sampling. Increasing one purchase probability may do little for the probability of completing the entire route.

In early experiments, workers sometimes retained their familiar behavior after purchases changed, leaving animals undeployed for long periods or digging up newly built structures. These attempts added costs without corresponding income, giving little training encouragement to the new route.

From an optimization perspective, learned purchases, production, and execution form an internally coordinated behavior pattern. Changing one component often reduces returns initially; a useful alternative requires several conditional actions to change together. Training can consequently remain close to familiar management patterns. This was the main phenomenon behind our discussion of policy basins.

New expert data demonstrated these dependent stages together. The additional experiment in Chapter 5 showed different production and sales mixes in adjacent BC checkpoints under matched shop sequences, exogenous draws, and opponents. Expert supervision could change management patterns, with strength fluctuating during those changes.

### 7.3 Reconsidering Training Regressions

PPO improved the policy. PPO15 clearly surpassed BC37, with higher submission scores and rank. Continued training nevertheless produced repeated declines in win rate and margin. Under the available time and compute, I frequently rolled back checkpoints, changed configurations, or switched training routes.

Kaggriculture depends on coordination across purchasing, planting, maintenance, transport, and sales. A local behavioral change can alter an entire downstream production chain. Returning one turn later may miss an early sale. Replacing one crop may change cash and labor allocation over the following days. These effects accumulate and can cause a substantial win-rate drop. Small parameter updates can also change argmax rankings at critical decisions and produce different trajectories.

This led me to reconsider earlier judgments of PPO policy collapse. In this game, short-term regression may reflect dependent behaviors temporarily losing coordination during updates. The later BC runs, which declined before recovering and exceeding their starting points, support that possibility. Some PPO attempts may have needed more iterations to reveal their longer-term direction.

The principal cause of PPO instability remains unresolved. Value estimation, advantage construction, exploration, update magnitude, and the changing self-play distribution may all contribute. Determining more reliably whether a training route deserves further investment is an important question this competition left me with.

### 7.4 Scope and Future Directions

Time and compute limited further ablations. The final result combines representation design, expert selection, BC, PPO, and checkpoint selection. More explicit controls would help separate their contributions.

One important question concerns the intermediate PPO stage. Could BC37 reach similar strength by continuing BC directly on the same new expert data? Comparing that route with BC37 → PPO15 → BC under matched data, training budgets, and evaluation conditions would help establish whether PPO improved the starting point for later learning. PPO itself also needs comparisons of GAE, rollout lengths, and update configurations under a fixed sampling budget, repeated across independent training seeds.

The final solution depends on high-quality expert data. During the competition, I did not complete an RL route from random initialization to comparable strength. Learning basic execution, complete production chains, and management choices together makes effective exploration harder. Curriculum learning, reward shaping around verifiable management outcomes, and high-quality, diverse heuristic-generated demonstrations are promising directions.

For self-generated training data, I would still like to explore within-group comparisons under identical game conditions: use the current argmax policy as a return baseline, explore alternative management strategies through softmax, and study how to turn improvements into relative advantages while preserving existing capabilities. Chapter 6 shows that finding winning trajectories leaves substantial work in data construction and action-level credit before those wins become policy improvement.