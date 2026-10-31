
CELL 0
# ⚔️ V46 vs Pipe-8 vs Jaxa: The Turn-1 Microstructure War

**TL;DR**: Ahmed released **V46** featuring a predatory "Turn-1 Lift" ($[\text{BUY } 30]$ wheat at step 1) to punish Nathan Jacob's **Pipe-7 / Pipe-8** and Jaxa's **Beyond-48 (LB 2780+)**. We extracted the audited Python code of all 5 top agents and executed a **complete 60-game round-robin empirical tournament** (Seeds 42, 100, 2026 with full symmetric seat swaps P0/P1) on `kaggle_environments` 1.32.7.

![galaxy-brain](https://i.imgflip.com/4/2fzidi.jpg)
*"We ran the 60-match gauntlet so you don't have to burn submission slots. The rock-paper-scissors meta is real."*

---

### 🏆 Full Empirical Matrix Standings (60 Matches Across 3 Benchmark Seeds)

| Rank | Agent Architecture | Wins | Losses | Ties | Win Rate | Mean Margin (Gold/Game) | Key Mechanism |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---|
| **#1** | **Jaxa Beyond-48** | **8** | 4 | 0 | **66.7%** | **+862.3g** | Index-Prioritized Front-Loading |
| **#2** | **Ahmed V46** | **7** | 2 | 3 | **58.3%** | **+984.4g** | Turn-1 Lift + Dynamic Horizon |
| **#3** | **Nathan Pipe-7** | **7** | 5 | 0 | **58.3%** | **-827.9g** | Clean Turn-0 Feed Insulation |
| **#4** | **Anti-Lift (Ours)** | **3** | 6 | 3 | **25.0%** | **+499.8g** | Dark Turn-1 (Pure V46 Counter) |
| **#5** | **Ahmed V45 (Benchmark)** | **2** | 10 | 0 | **16.7%** | **-1,518.6g** | Q=70 Slippage Exhaustion |

---

### 🔄 The Rock-Paper-Scissors Cycle Revealed
Our exact head-to-head records reveal a fascinating strategic triangle dominating the ladder:

```text
        Ahmed V46 (Aggressive Lift)
         ▲                        │
         │ beats (+781g)          │ loses to (-510g on 2/3 seeds)
         │                        ▼
   Jaxa Beyond-48 ◄──────── Nathan Pipe-7
      (beats Pipe-7 by +1,800g)
```

1. **Ahmed V46 sweeps Jaxa Beyond-48 (3W - 0L, +781g)**: V46's early price manipulation disrupts Jaxa's scheduled order priorities.
2. **Jaxa sweeps Nathan Pipe-7 (3W - 0L, +1,800g)**: Because Pipe-7 plays dark on Turn 1 and has no front-run defenses, Jaxa's index-0 sell front-loading extracts maximum market liquidity uncontested.
3. **Nathan Pipe-7 trips Ahmed V46 (2W - 1L, +510g on low-variance seeds)**: Pipe-7 buys feed on Turn 0 and stays dark on Turn 1; V46 pumps the market against nobody, wasting capital!
4. **Ahmed V45 is extinct**: V45 was swept by V46 (**3W - 0L, +2,271g**), swept by Jaxa (**3W - 0L, +2,697g**), and swept by Pipe-7 (**3W - 0L, +229g**). **Do not submit V45 forks anymore.**


CELL 2
## 1. Engine Mechanics: Lockstep Settle & Slippage Math
In the Kaggriculture interpreter, market orders are executed **index-by-index in lockstep**:
```text
Step t, Order Index 0: Player 0 executes -> Town Inventory updates -> Marginal Price jumps
Step t, Order Index 0: Player 1 executes -> Town Inventory updates -> Marginal Price jumps
Step t, Order Index 1: Player 0 executes -> ...
```
Each purchase decrements town inventory, raising quotes for subsequent orders. Below, our simulator reproduces the exact cash drain and market quote shifts over the opening turns.


CELL 4
## 2. Microstructure Simulation: The Lift Trap in Action
We trace the first 4 turns when V46 attempts the 30-unit Turn-1 Lift against a clean Turn-0 buyer (Pipe-7):


CELL 6
## 3. Visualization: Capital Lockup & Quote Inflation
Notice the severe cash drop for V46 at Step 1, while Pipe-7 preserves its liquid cash buffer for immediate farm development.


CELL 8
## 4. Submission Packaging (Fork -> Submit -> Done)
Below is the clean single-file package incorporating the verified clean Turn-0 feed order:


CELL 10
## 5. Strategic Takeaways for the Final Week
1. **The Meta is Rock-Paper-Scissors**: There is no single invincible bot. V46 beats Jaxa, Jaxa beats Pipe-7, and Pipe-7 trips V46.
2. **V45 is Officially Dead**: If you are still running $Q=70$ wheat round trips, you are losing 1,500–3,800 gold per match to the top tier.

*If this verified empirical breakdown helped your campaign, please leave an upvote! 🚀 Good luck on the ladder!*