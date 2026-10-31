# Macro BC + Day Compiler

[Github](https://github.com/PavelSavchenkov/kaggriculture/tree/main/final_handoff)

![summary](https://www.googleapis.com/download/storage/v1/b/kaggle-forum-message-attachments/o/inbox%2F3790528%2F1e2bc44d92271b367b36e6576eb8acd1%2Fsummary.png?generation=1791113611314562&alt=media)

## TL;DR

- Once per day, at dawn, a behaviour-cloned network outputs a **DayIntent**: only the macro decisions. What to plant and buy, whether to buy land, and for each group of identical crops or animals how many to water, fertilize, harvest, clear, feed, care for and collect.
- A deterministic C++ **day compiler** does everything else: tiles, workers, routes, hires, purchases, when to bring goods back to the shed, funding checks, and an hourly selling plan against a learned forecast of the opponent's sales.
- We built this in the last ~5 days of the competition with Claude Opus 5.5.

---

## 1. The idea: separate long-term decisions from day planning

We did our best to separate two kinds of decisions:

- **Long-term decisions**: what the farm grows, how big the herd is, when to buy land, which crops to keep. A **network** makes them once per day, at dawn. It learns them from top players' games.
- **Day planning**: where to put new crops and animals, who walks where, how many workers to hire, order slots, when to sell the harvest. A deterministic C++ **day compiler** does this with exact search and dynamic programming.

The test for where a choice goes: does it pay off today or on later days? A new cow gives its first milk at age 8 and a strawberry its first fruit at age 10, so how many of them to add is the network's call. A route, a tile or a sale pays off today, so the compiler works it out exactly.

---

## 2. The network: one DayIntent per dawn

### 2.1 The output interface

The goal of the interface was to pull out **every decision that shapes the macro strategy** and leave every mechanical choice to the compiler. Macro decisions include what to grow, how many animals of each kind, land, which crops to keep or clear, and how much service each group gets.

Crops and animals that are identical except for their tile form a **group**. The network outputs counts per group, not per tile. The compiler chooses which members get which action. Groups are rebuilt from each dawn observation.

![dayintent](https://www.googleapis.com/download/storage/v1/b/kaggle-forum-message-attachments/o/inbox%2F3790528%2F1c73f77d24643fbf00ca47cdb10f2c8c%2Fdayintent.png?generation=1791113565105976&alt=media)

Three things made this interface work:

- **Outcomes, not actions.** `new_cow = 2` means "two cows placed and alive tonight". Buying, carrying, placing and feeding them is the compiler's job. `retain / clear / abandon` says what the ongoing crop group should look like tonight, not how to get there.
- **Fixed values.** When an action is impossible or worthless, its field is fixed to 0 from the dawn state alone. Examples: harvesting an unripe crop, care whose bonus cannot be used before the game ends, anything new on day 29. The same mask is used in label building, training (no loss), decoding (never chosen) and compiling.
- **Exact labels, no fallback.** Each day of a top player is replayed in our exact engine and converted to its DayIntent by definition. The converter never guesses or clamps. A day it cannot represent stops dataset generation until the interface is fixed. On 1.45M expert days: 0 failures. Only two cases are skipped: two land quadrants bought in one day, or an animal thrown away.

### 2.2 Training: the non-trivial parts

- **Data.** Games of strong Kaggle submissions (final rating ≥ 2,700) plus earlier top-20 games: 29k episodes, 1.45M player-days. Later networks were fine-tuned on fresh top games up to Sep 28.
- **Condition, don't filter.** Every training row carries three conditioning inputs:
  - *Strength* = the submission's final rating minus a ladder reference for that date (90th percentile of top-episode ratings). Raw ratings drift by ~300 points over weeks; this makes old and new games comparable.
  - *Recency* = the date of the game.
  - *Style* = a one-hot of 9 top teams (M&M, Majkel, DECEM, DSM, …).
  - Each input is dropped to "unknown" 10% of the time. At play time we ask for strength +150 and a recent date.
  - Filtering the data to the strongest players instead lost $11.3k per game. 13× more data with conditioning raised our local-LB win rate from 79% to 88%.
- **Opening style.** Days 0–5 are decoded in DSM's style, later days with no style (all teams pooled). This won 82–38 against a Vadim-style opening, which in turn beat no style.
- **Select by games, not by validation loss.** Seeds of one recipe with the same loss won between 3 and 23 of 40 games against the reference network. We trained several seeds, played them, and kept the best.
- **Final networks.** Main network v17 (width 512, fine-tuned on fresh games) plus 4 older networks. On days 6+, their logits are averaged with the main network's, which is worth ~$1.8k per game. The main network alone decides days 0–5.

---

## 3. The day compiler

The compiler is deterministic C++ (~4,000 lines for its core). It runs at dawn, about 1–2 s and at worst 3.5 s on Kaggle's CPU, and outputs an hourly plan for every worker plus purchases and hires. The same input always gives the same game on any machine, so every game we play can be replayed exactly.

What it decides:

| Area | What the compiler does |
|---|---|
| **Binding** | Which members of each group get each action. Members are interchangeable, so the router may swap them. |
| **Placement** | Tiles for new crops and animals are chosen inside the route search: a free tile, or one freed today by a harvest or a clear. Tiles near the shed are kept for animals, and each new entity pays a long-term cost for its distance to the shed. |
| **Routes** | The farmer plus up to 13 hires. Work is a set of stops (actions on one tile). Shed stops pick up feed wheat, fertilizer and animals, and drop off products. Routes are built by construction plus local search (swaps, tail exchanges). |
| **Crew size** | Hire-count search: from a lower bound up to the first complete crew, then down again, dissolving the least-loaded route. Cost = wages (1, 1, 2, 3, 5, …) + route time − deposit value + value of dropped work. |
| **Watering** | The network says how many crops in each group to water (alone or with fertilizer / harvest). The compiler picks which crops, which worker and what hour. It always waters new crops. |
| **Return-to-shed schedule** | Each unit that reaches the shed at hour h gets a value from the sale DP: when it can be sold and at what price. The router trades walking time against these values, so it searches over when each worker comes back. The values are averaged over scenarios of the opponent's sale timing. |
| **Purchases and funding** | Seeds, animals, wheat and fertilizer are bought just in time. The whole plan is played hour by hour in an engine copy with the real seller, under an expected and a stress forecast (the opponent sells all its visible goods at hour 2). Morning sales may fund same-day purchases. |
| **When money is short** | Unaffordable purchases move later. Then new crops and animals are trimmed one unit at a time. Then the fallback ladder: drop land → new entities → collection → survival. A cash floor keeps animals fed. |
| **Night** | The shed holds 100 items: cargo that cannot be stored tonight is planned away. |
| **Plan menu** | A few alternative plans (with earlier deliveries) are each played against the forecast. The best end-of-day value wins: our money + stock − the opponent's money. |
| **Market orders** | Sales are listed by revenue at stake: both players' orders fill slot by slot, so an earlier slot gets the better quote. Hires use the same 10 order slots, so a dawn sale takes a hire's slot when the crew still fits. |
| **Selling** | Every hour, see 3.1. |
| **Executor** | Follows the plan hour by hour and repairs it when an action fails or cash differs. |

### 3.1 The hourly seller

Per product, a dynamic program over the remaining hours of the day. It includes:

- the price impact of our own units;
- town and shop drains;
- the opponent's forecast sales, hour by hour;
- same-turn quotes exactly as the engine computes them (both players' i-th units get the same quote);
- the objective: our revenue minus the opponent's revenue, because a unit we sell first takes price from the opponent;
- the value of units kept overnight: 0.95 × the expected price tomorrow morning;
- 16 opponent sale paths sampled from the forecast. This hour's lot is chosen by its mean value over them;
- on a tie between selling now and later: sell now.

### 3.2 The opponent sales forecast

This was our largest single component. In a 20-game head-to-head, our agent without the learned forecaster lost all 20 games to the same agent with it, by $4.2k per game on average. Removing only the intra-day head cost $2.3k per game.

- **The opponent's sales are not visible, so we infer them** every hour: market inventory change + known town and shop drains − our actual fills. Using our requested quantities instead of actual fills turns our own failed orders into fake opponent sales.
- **Model.** For each game and opponent, a sequence of days. Per day and product, the inputs are:
  - the opponent's recent sales and yesterday's 24 hourly sales;
  - its inferred shed stock and its visible output (ripe crops, products waiting on animals);
  - its herd and money.

  A causal transformer over days predicts the opponent's sales for each of the next 24 hours.
- **Intra-day head**: given what the opponent has sold so far today, re-forecast the remaining hours.
- **Next-morning head**: tomorrow's first 12 hours, used to value the stock we keep overnight.
- 3 seeds averaged at runtime.
- **Timing matters more than totals.** An oracle of the opponent's timing was worth +$8.3k per game, an oracle of its totals +$4.5k.
- Chosen by games, not by held-out loss. In our second final pick, the forecaster is trained only on other teams' games.

---

## 4. Validation

Every comparison is paired: same world, same seed, same seat, both arms. We report:

- the margin (our money − the opponent's) and its standard error;
- our money and the opponent's money separately;
- the win rate.

### Test beds

1. **Our live Kaggle games.** Every Kaggle replay reproduces exactly in our C++ engine, so we can study any game turn by turn.
2. **Take-over continuations.** Load a recorded live game at the dawn of day d and let the candidate take over our seat, while the opponent replays its recorded moves. Play 1 day, 5 days, or to the end. Before using it, the unchanged agent must reproduce the recorded game exactly (700 of 700 days did).
3. **Frozen leaderboard games.** Put our agent into one seat of a recorded top-team game.
4. **Teacher days.** Start from a top player's recorded dawn and give the compiler that player's own DayIntent. Then compare the compiled day with what the player did. This separates compiler problems from network problems.
5. **Exact local-leaderboard judge.** Our team's local leaderboard, run with its own code. It reproduces the leaderboard's official games to the dollar.

### Gates

- Win rate plus the paired margin with its SE.
- Sequential reading at 24 / 48 / 96 / 192 games. Reject when mean + 1.28 SE < 0. Promote when mean − 2 SE > 0.
- One 40-game mirror set can produce a false winner, so we adopted a change only after ≥ 4 seed sets.
- Beds with real opponent behaviour (live games, continuations, frozen top-team games) come first. Our own agents sell later than real teams, so beds made only of our own agents overrate early-selling changes.

### Iterations came from concrete failures in games

We did not tune against offline metrics. We traced lost games, found the exact cause, and fixed the compiler's model of the game:

| What we saw in games | Cause | Fix | Effect |
|---|---|---|---|
| The 3rd sheep was lost in every game | The day-0 budget trim dropped animals first | On day 0, trim crops before animals | +$6.6k per game |
| A short day lost all its new crops and animals | The trim was all-or-nothing | Trim one unit at a time | 14 → 42 wins of 64 |
| Animals escaped; one game lost by $186k | An unfunded day left no cash for feed wheat | Survival cash floor | that world: −$186k → −$7.9k |
| Day-0 cash left unspent, game lost by $15–20k | The opening plan silently dropped work | Keep trimming until a complete plan is funded | removed the cliff |
| The opponent got the better price in the same hour | Both players' orders fill slot by slot | List sales by revenue at stake | 39 of 40 mirror games, +$11.6k |
| Dawn sales never happened on big hiring days | Hires used all 10 order slots | Reserve slots for dawn sales | +$0.36k on real games |
| The seller's expected prices were wrong | Our units were priced before the opponent's in the same turn | Price same-turn sales the way the engine does | +$1.6k to +$4.6k |
| Investments (e.g. the day-3 cow) came late | Goods were held for the evening, so there was no morning cash | Sell the morning's goods to fund same-day purchases | +$1.5k on real games |
| Products were lost at night with 4 land quadrants | Shed overflow | Plan night cargo against shed room | +$0.75k on real games |

Many of our gains were **denial**. Our fresh-data network, for example, won mostly because the opponent earned $4.6k less, while our own money changed little. So we always read our money and the opponent's money separately.

## Kaggriculture LocalLB: From Pull Request to Leaderboard

LocalLB is a self-hosted leaderboard for comparing Kaggriculture agents. Submit an agent through a GitHub pull request, and a Docker worker handles validation, evaluation, and ranking updates automatically.

![locallb](https://www.googleapis.com/download/storage/v1/b/kaggle-forum-message-attachments/o/inbox%2F3790528%2F5504a3fc7d0a4dae9f2fd3a389df792d%2Fimagettt.png?generation=1791113715427755&alt=media)

1. **Submit:** Open a non-draft PR targeting `main`, adding exactly one new agent under `agents/<agent_id>/`.
2. **Validate:** The worker checks submission rules and runs a smoke test. Passing submissions are automatically merged; ranking matches start **after merge**.
3. **Evaluate:** The challenger plays the current top 10 agents using **15 seeds in both seat positions**, giving **30 games per opponent**.
4. **Update:** Recorded results determine Elo ratings and the retained top 10. Published ratings are recomputed using only matches among those ten agents, giving each **270 games**.
5. **Publish:** The worker commits and pushes match records, rankings, and the README leaderboard to `main`.

The separate 30-agent leaderboard requires a manual round robin and is not triggered by PR submissions.