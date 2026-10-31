> **来源 / Source**：Kaggle Kaggriculture 公开 write-up，第 12 名，队伍 **Unknown Mother-Goose**。
> **原文**：https://www.kaggle.com/competitions/kaggriculture/writeups/12th-place-bc-with-ppo
> 本文为比赛归档的离线副本，仅作技术参考；**版权归原作者所有**。
> 如作者要求撤下，请联系仓库所有者。

# 12th Place: BC with PPO

Project URL: https://github.com/LinkinPony/kaggriculture-rl-public

We finished **12th** in Kaggriculture with a two-policy portfolio trained by behavior cloning (BC) on
curated public replays and refined with proximal policy optimization (PPO) in a self-play league.
After two weeks of post-deadline evaluation, our two final submissions—specialized on the distinct
macro-economic styles of leaderboard contenders **M & M & P & Q (MMPQ)** and **DSM**—scored
**2917.8** (MMPQ branch) and **2859.9** (DSM branch).

Four empirical findings shaped our system:

- **Teach a complete economy before asking RL to improve it.** Pure self-play PPO from random
  weights never discovered the multi-day loop of buying land and seeds, planting, watering,
  harvesting, and selling—ending 720-turn games with the starting 3,000 coins and zero harvests.
  Full-game BC established a working production cycle that PPO could then scale.
- **Curate coherent teacher versions rather than mixing replays.** Filtering demonstrations to a
  single strategy version raised closed-loop win rates by **29.2 percentage points** (`48.4% → 77.6%`)
  when teacher-forced token accuracy changed by only `0.5–0.6%`. Removing older or competing styles
  stopped BC from averaging incompatible investment schedules at tight cash thresholds.
- **Treat league PPO after BC as short, anchored refinement.** In unanchored runs, the first
  100–200 updates fixed systematic BC mistakes, after which **~97.5% of each update was isotropic
  noise**. Parameters followed a √N random walk around the BC optimum, degrading teacher
  action likelihood linearly with update count while self-play masked the loss of external strength.
  Penalizing field-wise KL divergence to the frozen initial actor—and restarting from the peak
  checkpoint at a lower learning rate—kept improvements stable.
- **Select checkpoints by complete greedy games and diversify the final pair.** Across ~10,000
  conditional action fields per game, greedy decoding (`T=0`) beat sampling (`T=1`) by **18.85
  percentage points** (`82.91% vs. 64.06%`) on the same weights. Combining a 256-game-per-matchup
  local clone matrix with live leaderboard evidence led us to submit one policy from each branch.

Throughout this writeup, match scores count a draw as half a win:
`score = (wins + 0.5 × draws) / games`. Run and submission IDs are
mapped in the [Appendix](#appendix-repository-run-and-submission-glossary).

---

## 1. From Pure RL to a Two-Branch Imitation–Refinement Pipeline

### 1.1 Why full-game imitation came first

A profitable harvest requires a multi-day chain of dependent actions: unlocking land, buying seeds
or livestock, routing workers to plant and water before daily deadlines, hauling produce to the
central shed, and timing sales against town consumption. Missing a single day of water turns planted
seeds into weeds overnight; missing two days of feed causes livestock to escape permanently.

Random exploration never completes this loop. After three weeks of experimenting with planners,
opening-only BC, and RL over scripted abstractions, a September 7 benchmark isolated the bottleneck
(**Figure 1A**): across 720-turn self-play games on two seeds, pure RL from random weights never
harvested a single crop (`$3,000` final cash), whereas full-game BC on 1,337 public games (`1.92M`
decisions) immediately established a `$25.8k` economy (`194` harvests) and scaled to `$66.2k` (`758`
harvests, `70%–77%` win rate against a fixed reference) after 128 PPO updates. Demonstrations
supplied the macro-economic skeleton; RL scaled its throughput.

![Full-game BC bootstrap and two-branch Relay BC and PPO lineage.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F15429833%2Fd506601b74a4d9051752e907de0e164f%2F01-lineage.png?generation=1792940245966454&alt=media)

### 1.2 Relay BC and the final two-branch lineage

Retraining BC from random weights whenever stronger public replays appeared discarded days of RL
representation learning. In the final ten days, we switched to **Relay BC**: carrying the trained
actor, critic, and prioritized opponent pool forward across successive replay refreshes.

Both final submissions descend from a **Shared BC Base** (September 28), trained on 882 games
strength-selected from the two dominant three-quadrant contenders on the late-season leaderboard:
**DSM** (which focused on a tight wheat–goose–egg and dairy compounding loop) and **MMPQ** (which
paired deterministic cash-threshold expansion with tomato cultivation and ~10.2 hired hands/day).
Rather than averaging these two styles into one policy, we specialized two branches (**Figure 1B**):

1. **DSM Branch (Slot 2, Final LB 2859.9):** After 1,061 unanchored league PPO updates from the
   Shared BC Base, we ran a Relay BC refresh on **598 games** from DSM's six latest submissions over
   the preceding two days, then refined that actor (with the inherited critic) for **756 KL-anchored
   PPO updates** at 128 games/update on two H200 GPUs.
2. **MMPQ Branch (Slot 1, Final LB 2917.8):** Branching directly from the Shared BC Base, we cloned
   **714 games** restricted to six submissions of MMPQ's current strategy. Pairing that actor with
   the DSM branch's trained critic, we ran **200 KL-anchored PPO updates** at 64 games/update on one
   H200 GPU (Stage 1), then restarted from the 200-update peak as the new reference anchor at a
   lower constant actor learning rate (`4e-6`) for **250 additional updates** (Stage 2).

---

## 2. Architecture: Entities, Memory, and Structured Actions

### 2.1 Entity representation and spatial–global backbone

At each turn, our C++ encoder maps the visible state into **286 entity tokens** of width 384
(**Figure 2A**): 200 farm tiles (2×10×10 boards), 64 worker slots (the permanent
farmer plus up to 31 hired hands per player), 9 market products, 8 town shop slots, 4 public
history-delta tokens (`1, 4, 12, 24` turns), and 1 global state token. Across all 286 tokens, the
encoder extracts **27,915 scalar features**—roughly 100 features per tile and worker—allowing
attention layers to connect worker coordinates directly to tile maintenance deadlines or upcoming
harvests to shop demand. Hidden opponent shed and carried inventories are zeroed with a
`private_known = 0` flag, and absent workers or unopened shops are masked from attention.

The highest-leverage domain features translate raw rules into **time horizons and marginal returns**:

- **Multi-horizon supply, demand, and price scenarios:** For all 9 products across six windows
  `H ∈ {1, 2, 4, 8, 12 days, remaining season}`, we compute exact town consumption
  and both farms' projected output under basic maintenance and yield-boosting (`CARE` / `FERTILIZE`)
  templates. Longer windows capture the 8+ day payback of cows and tomatoes and 3-day shop unlocks.
- **Non-linear liquidation and feed reservation:** Market prices follow nonlinear curves where
  oversupply drives premium goods toward the `$1` floor and scarcity triggers quadratic price spikes
  on carrots, tomatoes, and eggs. We compute exact unit-by-unit liquidation values, reserve two days
  of wheat feed for existing livestock to prevent starvation escapes, and simulate the full-season
  cash delta of placing one additional crop or animal.
- **Execution slack and contention:** Tile and worker tokens encode travel-plus-service slack before
  dehydration/starvation deadlines, plus seed shortfalls when multiple planters compete for stock.
- **Zero-initialized residual surgery (`+5,912 features`):** When expanding our feature schema from
  `22,003` to `27,915` scalars on September 25, we injected the new feature blocks before the first
  transformer layer via zero-initialized linear projections (`h_new = h_old + A_type · z_e`, with
  `A_type = 0` at initialization). This added only 59,904 actor parameters, preserved bit-exact
  logits and values at step 0, and let Relay BC and PPO absorb the new signals without disturbing
  the learned representation.

On the 200 tile tokens, a residual 3×3 depthwise-separable ConvNeXt block mixes local board
geometry before a **16-block, 8-head pre-norm Transformer** relates all 286 entities (**Figure 2B**).
The deployed actor totals **25.2M parameters**; during PPO, an independent **6-block, width-320
critic** estimates per-field value baselines.

![Entity encoder, spatial-global backbone, and prefix-conditioned actor-critic.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F15429833%2Fe364e3bb5366e9a9c149b6d132b0525a%2F02-architecture.png?generation=1792940430554988&alt=media)

### 2.2 Compress history on a side branch, retain current spatial detail

Pooling 286 entities into a single recurrent vector would bottleneck spatial precision for 32
workers. Instead, we compress history **only on a side branch** while keeping an unpooled bypass for
all 286 current tokens (**Figure 3A**). At each turn, four learned queries attend over valid entities
to form **four 256-d summaries**. A two-layer gated temporal transformer (GTrXL) attends causally
across the current summaries and up to **384 past turns** (`1,536` cached K/V slots per layer, or 16
game days). All 286 current entities then query these contextualized summaries via cross-attention
and merge the result through a gated residual connection.

![Side-branch GTrXL memory architecture and same-weight cache ablation.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F15429833%2F745fb523c2dff701948f8cb9c5e98ff0%2F03-memory.png?generation=1792940449458935&alt=media)

To verify that the policy relied on this 16-day cache rather than only its four explicit
history-delta tokens, we ran a same-weight ablation across 128 mirror games (**Figure 3B**): keeping
the 384-turn K/V cache won **104 of 128 games (`81.25%`)** and gained **`+$3,629`** mean cash over the
identical weights with the cache cleared before each turn.

### 2.3 Decode workers in parallel and market orders in sequence

Each turn combines up to 32 worker actions with up to 10 ordered market requests (**Figure 4**):

1. **Parallel worker chains (`T_u → O_u → q_u`):** All active workers decode in
   parallel across three conditional heads: a pointer head over tiles selects **Target (`T_u`)**
   (`PASS` and orthogonal moves `N/E/S/W` terminate immediately); selecting the current tile
   activates a rule-masked 44-class **Operation (`O_u`)** head (`PLANT`, `WATER`, `HARVEST`, `FEED`,
   `CARE`, `PICKUP`, `DROP`, `PLACE`, `BUILD_*`, `DIG`); amount-taking operations (`PICKUP`, shed
   `PLACE`) activate a 100-class **Quantity (`q_u`)** head (`1–100`).
2. **Sequential market decoder:** Committed worker choices are embedded and pooled with the global
   token to initialize up to 10 sequential market slots (`BUY_SEED`, `BUY_ANIMAL`, `BUY_PRODUCT`,
   `SELL`, `HIRE`, `BUY_LAND`, or `STOP`, followed by quantity `1–100`). After each order, an
   internal **quote ledger** updates remaining cash and shed stock from current prices and earlier
   same-turn requests so subsequent slots never overspend.

![Parallel worker chains and sequential market decoder with running quote ledger.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F15429833%2F73d36fb6ef19267bb2cc6daf3ae42fe7%2F04-decoding.png?generation=1792940522936677&alt=media)

We also tested an **autoregressive joint worker decoder** where workers decoded sequentially from
farmer to last hired hand while attending to earlier workers' choices. Even under teacher forcing,
target error rates still rose with worker index (`5.8%` on the farmer to `8.8%` on the seventh hand)
due to mid-season board complexity rather than coordination failures, and closed-loop play did not
improve (`77.2%` vs. `77.6%`), so we kept parallel worker decoding.

---

## 3. Behavior Cloning: Curating Coherent Demonstrations

### 3.1 Strategy coherence beats dataset volume

Adding more public replays frequently weakened the cloned policy. Top teams revised their opening
schedules and crop/livestock mixes across versions; imitating a mixture forced a unimodal policy to
average incompatible plans:

- **Cross-team schedule conflicts and loss skew:** In mid-week multi-team mixtures, one top teacher
  (`Boey`) bought ~2 geese in days 1–3 and tapered later, whereas `DSM` bought zero geese in days
  1–3 and surged to ~4.7 geese in days 6–8. Because `Boey` also placed high-frequency market orders
  (`~6,616` valid market fields/game vs. `1,600–2,000` for others), that 20% slice of trajectories
  absorbed **44.6%–57.3%** of the market loss while rare capital decisions like buying geese made up
  just **0.06%** of all action fields—leaving the mixed clone short on mid-game livestock.
- **Within-team version aliasing at tight cash thresholds:** In the final week, `MMPQ` shifted from
  an older three-quadrant style to a deterministic new opening (`v4`, including an unbeaten `123–0`
  submission) that added tomatoes, unlocked its third quadrant on day 10, and hired ~10.2 hands/day.
  Training the exact same BC recipe on mixed `MMPQ` versions (`v3`) versus only the six current-style
  versions (`v4`, 714 games) raised teacher-forced token accuracy by just **0.5–0.6 percentage
  points**, yet greedy closed-loop win rate jumped by **29.2 percentage points** (`48.4% → 77.6%`,
  and `82.8%` head-to-head; **Figure 5B**). Because `MMPQ`'s opening branches on tight cash
  thresholds (such as turn-4 melon-seed purchases where `604` vs. `614` coins separates two build
  orders), mixing versions caused the ~6% residual error to systematically average incompatible
  plans at critical branching turns.

Because raw leaderboard ratings deflated over time as opponents strengthened, we selected teachers
for our September 28 Shared BC Base by fitting a Bayesian Bradley–Terry model to all **4,339
decisive public games** across **1,790 submissions** (`P(i beats j) = σ(β_i − β_j)`, `β_i ~ N(0, 4)`) and keeping recent versions within `0.5 logit` of the
leader (7 `DSM` and 2 `MMPQ` submissions). Across ten Relay BC generations (**Figure 5A**),
single-team and Bradley–Terry curated refreshes consistently opened ahead of their predecessor
(`53%–65%`), whereas four- to six-team mixtures regressed (`23%–52%`).

### 3.2 Canonicalize labels, balance field frequencies, and evaluate in closed loop

Using our native engine's settlement traces, we stripped zero-fill requests and merged adjacent
identical market orders from replay labels while always encoding observations from unmodified
official replay states. To prevent rare `unit_qty` fields (emitted only on shed pickup/place) from
receiving ~30× inflated gradients under per-head averaging, we trained with a single **field-mean
cross-entropy loss** across all valid fields:

$$
\mathcal{L}\_{\mathrm{BC}}(\theta) =
\frac{\sum\_{d} w\_d \sum\_{i \in F\_d} -\log \pi\_\theta(y\_i \mid h\_i, y\_{\lt i})}
{\sum\_{d} w\_d |F\_d|},
\qquad w\_{\text{unit}} = 1.0,\quad w\_{\text{market}} = 3.5.
$$

![Relay BC opening strength, MMPQ version coherence, and validation NLL vs. closed-loop play.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F15429833%2F8bf1679fc77d7b72c901f101170cdca1%2F05-curation.png?generation=1792940573167693&alt=media)

Even with balanced loss weights, **validation NLL failed to rank closed-loop playing strength**
(**Figure 5C**): across four `MMPQ v4` BC variants, doubling the learning rate with joint decoding
(`J-hi`) achieved the lowest validation NLL (`0.2036`) and highest token accuracy (`93.7%`), but
dropped **12.2 percentage points** in full games (`65.4%` vs. `76.6%–77.6%`). Every final BC
checkpoint was therefore chosen by full 720-turn greedy evaluation matches.

---

## 4. League PPO: Prefix Credit, Opponent Prioritization, and Anchoring

### 4.1 Prefix-conditioned critic and PFSP league curation

We optimize pure terminal win/draw/loss reward (`R ∈ {+1, 0, −1}`, `γ = 1`). Because a turn
commits up to 32 worker chains before up to 10 sequential market orders, a single turn-start value
`V(h_t)` is a poor baseline for late fields. Our **prefix critic** encodes the 286-entity scene once
per turn and applies normalized cumulative embeddings of committed preceding fields `a_{t,<k}` to
output per-field baselines `V_φ(h_t, a_{t,<k})` in a single tensor pass:

$$
A_{t,k} = R - V_\phi(h_t, a_{t,<k}), \qquad
\rho_{t,k}(\theta) = \frac{\pi_\theta(a_{t,k} \mid h_t, a_{t,<k})}{\pi_{\mathrm{old}}(a_{t,k} \mid h_t, a_{t,<k})}.
$$

Each PPO update splits rollouts **50% self-play** and **50% prioritized fictitious self-play (PFSP)**
against a unified archive of historical snapshots and **seven ahead-of-time compiled C++ public
scripts** (`ahmed_v45`, `ahmed_v53`, `metacounter_r1`, `shop_router_0913`, `rayk_v38_low_pressure`,
`farming_v4_0914`, `thomas_metav4`). Pool opponents are weighted by `w_j = (1 − s_j)^2`, where
`s_j = (W_j + 4) / (G_j + 8)` tracks exponentially decayed points and games
(128-update half-life). As the archive grew past 500 policies, two rules kept league budget focused
on contested matchups (**Figure 6C**):

- **Mastered-opponent review cap (`≥64 games & ≥95% score → 5% cap`):** Mastered opponents share a
  combined **5%** of PFSP probability for regression checks, cutting sampling wasted on 304 mastered
  policies from **54.8% to 5.0%**.
- **Discounted predecessor inheritance (`discount = 0.5`):** New Relay BC or clone runs initialize
  unseen opponents' `(W_j, G_j)` from the nearest predecessor's ledger scaled by
  `0.5^k`, cutting cold-start re-probing overhead from **75.3% to 1.6%**.

### 4.2 Diagnose parameter random walk and anchor PPO to the reference policy

Beating our own historical checkpoints in league play did not guarantee progress against top external
teams. In a September 28 diagnostic, an unanchored PPO run beat its BC start **111–17 (`86.7%`)** in
direct play, yet on held-out teacher states its goose-purchase matching fell from `79.6%` to `57.3%`
while tomato-seed turns more than tripled (`110 → 386`)—contributing to a `1–37` record against
live Top-5 teams where a `+$1,846` tomato gain was outweighed by deficits in eggs (`−$2,098`), milk
(`−$1,520`), and wheat (`−$2,328`).

Analyzing the parameter trajectory across a 1,061-update unanchored run explained why longer RL
runs consistently peaked around 150–250 updates and then drifted (**Figure 6A**):

1. **Signal-to-noise collapse and √N random walk:** The cosine similarity between
   consecutive 64-update parameter displacement vectors `Δθ` was `0.098` between updates
   64 and 128 (fixing systematic BC mistakes), but fell to **`0.017–0.030` after update 128**—meaning
   **~97.5% of each subsequent update was isotropic noise**. With constant step norms (`~0.38`),
   cumulative parameter displacement followed a √N random walk (`0.445 × √6 ≈ 1.03`
   predicted vs. `1.041` measured at update 616), causing teacher action NLL to degrade **linearly
   with update count** (`0.172 → 0.244 → 0.517`).
2. **Why step-wise clipping and self-play failed to stop drift:** Per-update KL remained tiny
   (`0.0008–0.0035`), never triggering the `0.05` step cap. Meanwhile, `γ = 1` terminal returns
   carried high variance across 719 turns, and playing mostly against self-play and recent own
   snapshots kept expected win rate near 50% even as both sides drifted away from strong external
   play.

![Unanchored PPO drift diagnosis, KL anchoring, and PFSP opponent prioritization.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F15429833%2F30df52145672cb1a36b9ac1d6f30ae73%2F06-anchoring.png?generation=1792940601660626&alt=media)

We therefore froze the initial actor `π_ref` at the start of each RL run and added a
**field-wise KL anchor** across all active action fields:

$$
\mathcal{L}\_{\mathrm{actor}}(\theta) = \mathcal{L}\_{\mathrm{PPO}}(\theta) + 0.3 \mathbb{E}\_{h,a\sim\pi\_{\mathrm{old}}}\left[\sum\_k D\_{\mathrm{KL}}\left(\pi\_\theta(\cdot\mid h,a\_{\lt k}) \Vert \pi\_{\mathrm{ref}}(\cdot\mid h,a\_{\lt k})\right)\right] - 10^{-4}\mathcal{H}(\pi\_\theta).
$$

The reference anchor bounded cumulative divergence near `KL ≈ 0.030` (**Figure 6B**). On the MMPQ
branch, when the initial warmup schedule (`5e-6 → 7.5e-6`) peaked at update 200 (`72.5%` panel
score), we restarted from update 200 as the new frozen KL anchor at a constant `4e-6` learning rate;
after 250 additional updates, Stage 2 beat Stage 1 **56.0%** across 1,280 direct mirror games.

---

## 5. Systems Engineering: Native Engine, Async Rollouts, and Deployment

Full-season RL over 720-turn episodes relied on a unified C++/CUDA pipeline (**Figure 7**):

- **Bit-exact C++20 batch simulator (`_revue_native`):** One C++20 engine implements game rules,
  market settlement, `27,915`-feature extraction, and legality masks across replay curation, BC, GPU
  rollouts, and live play—matching the official Python interpreter across all 92,160 observations in
  64 audit games while running compiled C++ script opponents with the GIL released.
- **Ping-pong CPU/GPU rollouts:** Two environment groups alternate on each GPU (**Figure 7B**):
  while Group A steps C++ environments on CPU into double-buffered pinned memory, Group B replays
  captured **BF16 CUDA Graphs** on GPU and updates its rolling 384-turn K/V cache. One H200 GPU
  collects 64 complete 720-turn games (up to 92,160 steps) and completes a prefix-critic +
  KL-anchored PPO update in **~43 seconds**.
- **93.7 MB CPU bundle:** Each submission packages the FP32 TorchScript actor and C++ extension for
  single-threaded CPU inference (`T=0`, rolling 384-turn K/V cache), finishing 720-turn matches with
  **>59.35s** of the 60s extra-time bank remaining.

![Native C++20 batch simulator, alternating CPU/GPU rollout schedule, and CPU submission bundle.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F15429833%2F361db6a93f3b657477b0f590bacf5a37%2F07-pipeline.png?generation=1792940619945572&alt=media)

---

## 6. Evaluation and Final Portfolio Selection

### 6.1 Greedy decoding (`T=0`) vs. sampling (`T=1`)

Although training samples actions at `T=1` to explore, evaluating frozen checkpoints in complete
games showed that **greedy decoding (`T=0`, conditional argmax over legal actions) was vastly
stronger** (**Figure 8A**): across 1,024-game paired panels on two DSM-branch checkpoints, `T=0`
improved scores from `64.06% → 82.91%` (**+18.85pp**) and `66.31% → 78.61%` (**+12.30pp**), winning
`72.7%` and `63.3%` head-to-head. Across ~10,000 conditional decisions per game, `T=1` sampling
inevitably draws occasional tail errors—like skipping a watering turn or mistiming a land purchase—that
compound over the remaining season.

### 6.2 Complementary strengths across local clones and live matches

Open-loop replay of recorded opponent actions is invalid in Kaggriculture: at the end of each day,
the environment draws weed spawns on empty tiles before drawing town shops from the same RNG stream,
so changing either player's land usage alters the RNG offset and changes which shops unlock. We
therefore trained closed-loop **BC proxy clones** of the top five external teams (`MMPQ`, `DSM`,
`Tufa Labs`, `DECEM`, `Vadim`) and evaluated six finalist candidates across a 256-game-per-cell
matrix (1,792 mirror games per candidate at `T=0`; **Figure 8B**).

![Greedy T=0 temperature ablation and finalist evaluation matrix.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F15429833%2F4734963265d6e9e921d74e03d4e417f4%2F08-finalists.png?generation=1792940641988149&alt=media)

Combining the local clone matrix with pre-deadline live matches resolved our final two-slot portfolio:

- **Slot 1 — MMPQ Branch (`restart +250`, Final LB 2917.8):** Achieved the highest five-clone
  average (**71.3%**), beat both internal RL anchors (`55.1%` and `63.7%`), and scored **78.5%**
  against the DSM clone. In pre-deadline live matches, the MMPQ branch went **74–4** against teams
  ranked 6th or lower (`20–4` against ranks 6–20; `54–0` below rank 20).
- **Slot 2 — DSM Branch (`756 updates`, Final LB 2859.9):** Against the live Top 5 before the
  deadline, an earlier MMPQ checkpoint went `0–9`, whereas the DSM branch went **15–37**—including
  **8–5 against DECEM** and **6–10 against Tufa Labs**—matching Figure 8B, where the DSM branch led
  all candidates against the **Tufa (`80.9%`)**, **DECEM (`83.6%`)**, and **Vadim (`76.6%`)** clones.

| Final submission attribute | Slot 1: MMPQ Branch | Slot 2: DSM Branch |
| --- | --- | --- |
| Lineage | Shared BC Base → MMPQ v4 BC → Stage 1 PPO (200 upd) → Stage 2 PPO (+250 upd) | Shared BC Base → League PPO (1,061 upd) → DSM Relay BC → Anchored PPO (756 upd) |
| Teacher dataset | 714 games (6 current-style MMPQ versions) | 598 games (6 recent DSM versions over 2 days) |
| PPO budget / hardware | 200 + 250 updates (64 games/upd, 1×H200) | 756 updates (128 games/upd, 2×H200) |
| Actor LR / KL anchor (`λ = 0.3`) | `7.5e-6` anchored to BC, then `4e-6` re-anchored to Stage 1 peak | `7.5e-6` anchored to DSM Relay BC |
| Inference / endgame rule | FP32, `T=0` greedy, 384-turn K/V, step-718 liquidation | FP32, `T=0` greedy, 384-turn K/V, step-718 liquidation |
| **Final Kaggle rating** | **2917.8** | **2859.9** |

Both bundles also apply a deterministic **step-718 liquidation rule** on the final actionable turn:
workers on the four central shed tiles carrying produce execute `DROP`, and the market queue is
replaced by `SELL` orders for all shed stock sorted by descending holding value (`stock × price`),
gaining **+208 coins** on average in paired games with zero regressions.

---

## 7. How the Approach Evolved and Key Takeaways

![Four development phases with historical submission scores and PPO budgets by generation.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F15429833%2F51b0a85b70552a230586347a7ea3799b%2F09-journey.png?generation=1792940660829075&alt=media)

Our six-week effort progressed through four phases (**Figure 9**):

1. **Aug 18 – Sep 6 — Action-abstraction search (peak `2,166`):** Three weeks of LP planners, route
   scripts, opening-only BC, and RL over scripted forks peaked at `2,166` and collapsed whenever the
   script prior was removed.
2. **Sep 7 – Sep 20 — Full-game BC from scratch + long RL (peak `3,185`):** Full-game BC plus the
   16-block entity transformer jumped from `1,485` to `3,035` in two days and reached our
   season-high public rating of **3,185** on September 16 (6,105 PPO updates), but resetting to
   random weights on each BC refresh required thousands of RL updates to rebuild strength.
3. **Sep 21 – Sep 28 — Relay BC and persistent league state:** Carrying the actor, critic, 384-turn
   GTrXL memory, zero-init feature expansions, and PFSP mastery/inheritance state forward cut RL
   budgets by an order of magnitude.
4. **Sep 29 – Sep 30 — Style-specific clones, KL anchoring, and greedy play (`2917.8` / `2859.9`):**
   Diagnosing unanchored PPO drift led to the frozen-reference KL anchor (`λ = 0.3`),
   single-style `DSM` and `MMPQ` branches, and `T=0` greedy inference.

### Key Takeaways

- **Bootstrap the full horizon before optimizing locally.** Full-trajectory imitation provides the
  multi-day economic invariants that local policy gradients fail to discover from scratch.
- **Data coherence beats dataset size and teacher-forced loss.** Removing version aliasing inside a
  single team's replays yielded a `+29.2pp` closed-loop jump from a `+0.5%` token-accuracy change,
  whereas lower validation NLL did not translate to stronger play.
- **Anchor post-BC reinforcement learning against noisy drift.** When terminal-reward variance is
  high and self-play dominates sampling, unanchored PPO random-walks away from strong teachers after
  fixing early mistakes; a frozen-reference KL penalty and low-LR continuations keep improvements
  stable.
- **Compound state across generations.** Treating the actor, prefix critic, zero-init feature
  additions, and decayed PFSP ledger as persistent assets turned multi-day rebuilds into 3-hour
  refinements.

---

## Acknowledgements

Thanks to the Kaggriculture organizers and `kaggle-environments` contributors for a deep competitive
economy, to M & M & P & Q, DSM, Tufa Labs, DECEM, Vadim, and Boey whose public replays enabled our
curation studies, and to the authors of the public notebooks that formed our compiled C++ script
baseline:
[Ahmed V45](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v45-first-turn-wheat-round-trip) &
[Ahmed V53](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v53-opening-signature) (`ahmedberatozer`),
[MetaCounter R1](https://www.kaggle.com/code/alperen5252525/kaggriculture-metacounter-r1-scored-agent) (`alperen5252525`),
[Shop Router 0913](https://www.kaggle.com/code/yhay81/shop-router-0913) (`yhay81`),
[Rayk V38 Low Pressure](https://www.kaggle.com/code/raykkretzschmar/kaggriculture-rank-your-agent) (`raykkretzschmar`),
[Farming V4](https://www.kaggle.com/code/lynnsakurai/farming-score-v4-a-better-shop) (`lynnsakurai`), and
[Thomas Metav4](https://www.kaggle.com/code/thomastschinkel/the-metav4-farm-submission-v13) (`thomastschinkel`).

---

## Appendix: Repository Run and Submission Glossary

| Writeup & figure name | Repository run IDs & Kaggle submission IDs |
| --- | --- |
| **Slot 1: MMPQ Branch (`2917.8`)** | MMPQ v4 BC `s101001` (epoch 9) → Stage 1 anchored PPO `s101102 U200` (`56709373` / `56720178`) → Stage 2 low-LR continuation `s101701 U250` (**final submission `56721459`**) |
| **Slot 2: DSM Branch (`2859.9`)** | DSM 2-day Relay BC `s100801` (epoch 11) → anchored PPO `s100901 U756` (**final submission `56721201`**; `U480` submitted earlier as `56689315`) |
| **Shared BC Base & unanchored drift probe** | Sep 28 Bradley–Terry BC `s98001` (epoch 11) → unanchored PPO `s99001` (`U200` submitted as `56658433`, `U588` as `56644629`, analyzed up to `U1061`; PFSP inheritance benchmark) |
| **Sep 7 full-game BC bootstrap benchmark** | Mirror self-play seeds `s47001`, `s47002` |
| **Sep 8 Entity Transformer debut** | `s62001` (16-block, width-384 entity encoder) |
| **Sep 13 scratch BC + long RL (`3,185` peak)** | `s68001` (6,105 PPO updates; reached season-high public rating `3,185` on Sep 16) |
| **Sep 23–25 DSM Relay BC series** | `s79001 → s80001` (grouped BC); `s81001 → s82001` (all DSM games); `s85001 → s86001` (`v5b` +5,912 zero-init residual features) |
| **Sep 25–28 multi-team mixtures & ablations** | 4-team `s88001 → s89001`; 6-team `s90001 → s91001` and `s94001 → s95001` (PFSP mastery review at `U890`); Boey+4 `s96001 → s97001` (384-turn memory ablation at `U116`, goose/tomato drift probe at `U472`) |
| **Sep 30 MMPQ BC ablation suite** | `s101001` (`v4 P-cosine`), `s101002` (`v4 J-joint`), `s101003` (`v4 J-hi`), `s101004` (`v4 P-const`), `s101005–s101008` (`v5` & second seeds); MMPQ Stage 1 seed 2 `s101101` / `s101702`; temperature benchmark `s100201 U200` |
| **Tracked MMPQ teacher versions** | Earlier style (`v3` mix): `56594027`, `56607039`; current style (`v4` corpus): `56612150`, `56624842`, `56640167`, `56658903`, `56679033` (`123–0`), `56680759` |