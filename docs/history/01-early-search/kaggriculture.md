

<!-- NOTEBOOK CELL 0 -->
### Hi everyone!) I’m trying to learn using publicly available notebooks and ideas from GitHub. In this notebook, I sort the publicly available notebooks by speed, and starting with the weakest ones and moving up to the leaders, I run them and study how they play so that, in the end, I can create something of my own based on your solutions.
### I’m learning with DEEPSEEK. I have 3 dialogues in it: in one I’m studying your work, in another I’m looking at ideas from GitHub, and in the third I’m reading the discussions!))

<!-- NOTEBOOK CELL 1 -->
# Kaggriculture Agent Evolution

## Development Path

| Version | Approach | Key Innovation | Source | Result |
|---------|----------|----------------|--------|--------|
| V17 | Modular Chassis + 13 Routes | 9 switchable reactive layers + shop-pair routing | — | 2409 peak |
| V18 | V39 copy | 20+ reactive overlays + Terminal Planner | [Ahmed Berat Özer V39](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v39-ready-before-the-rush/notebook?scriptVersionId=349373350) | 2680 (live) |
| **V19** | **V45 copy** | **First-turn wheat round trip (1 market change)** | **[Ahmed Berat Özer V45](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v45-first-turn-wheat-round-trip/notebook)** | **2760 (author)** |

---

## V17: Modular Chassis with 13 Routes

**Idea:** 13 complete action tapes from Shop Router 0909, selected by first two shops at step 144, shared ending at step 648.

**9 switchable reactive layers:**

| Layer | Purpose |
|-------|---------|
| `hand_align` | Pad hands to real count |
| `weed_repair` | DIG weeds blocking PLANT/BUILD |
| `sell_lead` | Sell next step's lots one turn early |
| `front_run` | Sell before opponent's SELL |
| `budget_guard` | Fund 72-step block purchases |
| `room_guard` | Prevent shed overflow at day end |
| `clamp_sells` | Trim unfillable SELLs |
| `dead_stock` | Sell stock the route never sells |
| `terminal_liquidation` | Final full shed sale |

**Result:** 2409 peak → 1900 in play. Taught us that a chassis without its reactive layers turned on is just an expensive tape.

---

## V18: V39 Copy — current live agent

**Source:** [Ahmed Berat Özer, Kaggriculture V39](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v39-ready-before-the-rush/notebook?scriptVersionId=349373350) — 2680 LB

**Idea:** The same 13-route chassis from V17, wrapped in 20+ reactive overlays accumulated over 12 days of evolution (V27 → V28 → … → V39).

**Key overlays:**

| Overlay | Purpose |
|---------|---------|
| Terminal Planner | Simulates last 7 turns, accepts only if it dominates baseline |
| V219 Tomato | Late tomato investment (day 18–29) with dedicated workers |
| V231 Cattle | Replaces sheep with cows when milk shops dominate |
| V233 Sheep | Six-sheep SE investment when 2+ YARN_STORE and WOOL ≥ 220 |
| R36 Two Coins | Reserves sales up to 4 turns ahead |
| R37 Nocturne | Sorts sales by impact using opponent's visible ripe yield |
| R44 Mirror Counter | Detects clones via cash-response probe |
| R51 Input Planner | Beam search for wheat/carrot fertilizer tours |
| R53 Labor | Exact spawn and route scheduling for tomato workers |
| R85 Feed | Economic feed-vs-production evaluation |
| R88 Care Value | Charges care bonus only when it can pay out |
| R95 Replenishment | Retains physical grain for two full days |
| R97 Supply Guard | Protects scheduled wheat pickups from being sold off |
| V224 Sales First | Reorders SELL orders before BUY orders |
| V234 Rescue | Emergency wheat purchase for starving sheep |

**Why it's strong:**

1. Same routes as V17 — but every reactive layer that was off in V17 is now on.
2. Terminal Planner — exact engine simulation, accepted only on strict dominance.
3. R37 Nocturne — reads opponent's visible ripe yield to decide sale order.
4. R44 Mirror Counter — probes opponent cash changes to detect clones.
5. Every overlay is bounded — checks physical state and abstains when uncertain.

**Result:** 2680 live (2152 after 3 days). Currently running as V18.

---

## V19: V45 Copy — First-Turn Wheat Round Trip

**Source:** [Ahmed Berat Özer, Kaggriculture V45](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v45-first-turn-wheat-round-trip/notebook) — 2760 LB

**Idea:** V45 keeps **the complete V44 policy** (all V43 production layers + clone-gated sale pre-emption) and changes **exactly one market turn**. On turn 0 the inherited opening bought 15 wheat as two orders and sold them as a third. V45 **buys 70 wheat as one order and sells them back as the next order in the same turn**.

**The mechanism:**

The engine quotes each unit of both players' same-index orders **at the same inventory** and commits both. A large buy at index 0 followed by a large sell at index 1 leaves a rival's **index-1 purchase quoted at a scarcer, flat inventory**. Against the public route-tape family that dominates the top of the ladder, whose openings place a **second wheat purchase behind their first**, the shared per-unit market quoting makes that second purchase cost **about 60 more**, which their strictly funded first-day plan cannot absorb: **they plant one melon fewer**.

**Key properties:**

1. **Neutral against the market alone** — round trip nets zero.
2. **Neutral against itself** — same round trip means same quotes.
3. **Costs us the melon** against rivals whose opening sells wheat before buying again (the older Two Coins opening). That family is rare on the live ladder, and the trade-off is accepted and disclosed.
4. **No rival private information is used.**

**Evaluation (from author's notebook):**

| Cohort | W/L/T | Strict win rate | Mean cash margin |
|--------|-------|-----------------|------------------|
| Development V45 (24 fresh worlds, 10 rivals, both seats) | 470/10/0 | 97.92% | +4,966.87 |
| Independent V45 (32 untouched worlds) | 620/20/0 | 96.88% | +5,097.73 |
| Direct V45 vs V44, independent | 63/1/0 | 98.44% | +1,398.06 |

**Per-rival breakdown (64 games each):**

| Rival | V44 W/L/T | V45 W/L/T | Paired margin |
|-------|-----------|-----------|---------------|
| exact_v43 | 64/0/0 | 64/0/0 | +1231.5 |
| fastclone24 | 9/55/0 | 60/4/0 | +1304.2 |
| guru_dynamic | 62/2/0 | 62/2/0 | +993.6 |
| lynn_v5 | 62/2/0 | 61/3/0 | +1040.1 |
| **mirror_counter** | **64/0/0** | **62/2/0** | **-1153.0** |
| race8d_v44 | 3/3/58 | 63/1/0 | +1398.1 |
| seven_rescue | 64/0/0 | 62/2/0 | +725.1 |
| thomas955 | 64/0/0 | 64/0/0 | +501.0 |
| **v43_open78** | **33/31/0** | **62/2/0** | **+1945.0** |
| v49_bandit | 64/0/0 | 60/4/0 | +396.3 |

**Result:** 2760 (author). Running now as V19.

---

## V17 vs V18 vs V19 — Comparison

| Factor | V17 | V18 (V39) | V19 (V45) |
|--------|-----|-----------|-----------|
| Base routes | 13 (Shop 0909) | 13 (Shop 0909) | 13 (Shop 0909) |
| Reactive layers on | 3 of 9 | all 9 | all 9 |
| Terminal Planner | ❌ | ✅ | ✅ |
| Livestock overlays | ❌ | ✅ | ✅ |
| R36/R37/R44 market layers | ❌ | ✅ | ✅ |
| First-turn wheat round trip | ❌ | ❌ | ✅ |
| Opening sequence | BUY 5, BUY 10, SELL 60 | BUY 5, BUY 10, SELL 60 | **BUY 70, SELL 70** |
| Anti-clone pre-emption | ❌ | partial | ✅ |
| Peak result | 2409 | 2680 | **2760** |

**Key insight:** V45 is **one line of code** different from V44. The entire gain comes from **market microstructure** — the lockstep per-unit quoting of the engine. This is the highest leverage-to-code ratio we have seen.

---

## Future Plan

**Completed**
- V18 (V39 copy) launched and running — 2152 after 3 days
- V17 (our chassis) retired — 1639, outdated
- V19 (V45 copy) prepared — 2760 author score
- V45 mechanism fully understood: single market turn, lockstep quoting exploit

**Next Steps**
- Launch **V19** and compare against **V18** live on the ladder (wait 6h for both to converge)
- Test **V45 opening against V39** locally with the author's evaluation harness:
  - 24 fresh worlds, 10 rivals, both seats
  - Independent cohort of 32 untouched worlds
  - Per-rival breakdown with paired margin
  - Ledger audit (cash, products, feed shortfalls, animal escapes)
- Take from **V45** what is missing in **V39**:
  - **First-turn wheat round trip** — one market change
  - **Clone-gated sale pre-emption** (V44/V45 mechanism)
  - **Drop-turn race escalation** — if rival sells at our drop turn, escalate reservation horizon from 8 to 24
- Build a hybrid: **V39 overlays** + **V45 opening** + **V44 pre-emption**
- Target: **2800+** = confident silver territory

**Open questions**
- Does V45 opening hurt us against the mirror_counter family (-1153 in 64 games)?
- Is the melon trade-off acceptable given rarity of Two Coins opening on live ladder?
- Can we detect the Two Coins opening at turn 0 and use a different sequence against it?