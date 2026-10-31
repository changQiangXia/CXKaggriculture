> **来源 / Source**：Kaggle Kaggriculture 公开 write-up，第 3726 名，队伍 **WOOSUNG YOON**。
> **原文**：https://www.kaggle.com/competitions/kaggriculture/writeups/gigpo-kaggriculture
> 本文为比赛归档的离线副本，仅作技术参考；**版权归原作者所有**。
> 如作者要求撤下，请联系仓库所有者。

# GiGPO: A Thought Experiment at Kaggriculture

I'm glad to have had the opportunity to learn about reinforcement learning through this competition.   

# A. Problem Definition: Reachable states within 720 turns

![a01](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F4808143%2Fc303fbeed59a848d010d7a49d8df5da0%2Fa01_world_micro.png?generation=1790815728962307&alt=media)

## (1) Motivation & World–Micro Architecture

Kaggriculture is an intractable **720-turn planning problem** (30 days × 24 hours). Inspired by Rubik's Cube stage-solving and Pattern Databases (PDBs).

We operationalize this framework via a two-tier hierarchy:

* **World (Macro Strategy)**: *"Which state to aim for?"*  
Compresses global farm states into strategic embeddings using patterns learned from user replays.
* **Micro (Atomic Execution)**: *"How to get there?"*  
Fuses World's strategic context with real-time turn observations to execute worker movements, field tasks, and market trades.

---

![a02](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F4808143%2F7b8cdc03d675d6c135429c57a1fae4e1%2Fa03_gigpo_implementation.png?generation=1790816403269720&alt=media)

## (2) Learning Without a Critic: GiGPO with Split-Credit
 
To evaluate complex 720-turn decisions with high precision, we adapt Group-in-Group Policy Optimization (GiGPO; Feng et al., 2025) through a vector-based **Split-Credit** formulation. By comparing parallel rollouts sampled from identical initial conditions, this methodology eliminates critic overhead and directly assesses macro strategy alongside micro execution.

### 1. Episode Credit: Macro Strategy

* **Key Insight**: Including retained land assets alongside liquid cash ensures early farm expansion is accurately credited as strategic capital growth.
* **Mechanism**: Evaluates full trajectory outcome **R** relative to parallel rollouts **R**:

$$A_E = \mathcal{N}_c(R; \mathbf{R})$$

### 2. Step Credit: Micro Continuation

* **Key Insight**: Isolates continuation efficiency—such as optimal harvesting and market delivery cycles—starting from identical intermediate board states.
* **Mechanism**: Measures localized economic progress **G** via rule-based asset valuation **Phi(s)** across rollouts sharing observation anchor **k**:

$$G = \Phi(s_{\text{end}}) - \Phi(s_{\text{now}})$$

$$A_S = \mathcal{N}_c(G; \mathbf{G}_k)$$

### 3. Combined Advantage & Policy Update

* **Key Insight**: Broadcasting a single advantage **A** across all active worker and market branches drives seamless team-wide coordination without additional per-agent critic overhead.
* **Mechanism**: Fuses macro strategic performance and micro continuation efficiency into a unified turn advantage **A**:

$$A = \operatorname{clip}(A_E + 0.8 A_S, \, -6, \, 6)$$

Policy parameters **theta** are updated across active action branches using the clipped PPO objective:

$$\rho_f = \exp\left(\ell_f - \ell_f^{\text{old}}\right)$$

$$L^{\text{CLIP}}(\theta) = \mathbb{E}_w \left[ \min\left(\rho_f A, \, \operatorname{clip}(\rho_f, 1-\epsilon, 1+\epsilon) A\right) \right]$$

---

# B. Architecture Overview: Spatial Bottleneck Transformer

![b02](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F4808143%2F30a90c133f6b1b80bc7e6eadbad17c09%2Fb02_katago_evolution.png?generation=1790814369259588&alt=media)

### Evolution of KataGo Architectures

| Period | Architecture | Structural Innovation | Core Impact |
| --- | --- | --- | --- |
| **2019** | Residual CNN | Global Pooling + Auxiliary Heads | Combined local grid patterns with board-wide context. |
| **2023** | Bottleneck CNN | Channel Compression | Reduced compute costs via low-dimensional channels. |
| **2026** | Bottleneck Transformer | Attention + 2D RoPE + SwiGLU | Enabled direct, long-range global spatial reasoning. |

### Key Design Motivation

To model multi-agent dynamics on a **10×10 grid** under strict CPU limits, we adapted **KataGo’s (2026) Nested Bottleneck Transformer**. Each block processes spatial features through four stages:

1. **1×1 Conv (Compress)**: Reduces feature channels to lower spatial compute overhead.
2. **2D RoPE Spatial Attention**: Captures board-wide interactions while encoding relative 2D coordinates.
3. **Pre-Normalized FFN**: Transforms features using RMSNorm and SwiGLU activations.
4. **1×1 Conv (Expand) + Residual**: Restores feature channels and adds them to the main residual stream.

Self-attention connects distant grid entities (workers, crops, warehouse) in a single layer without deep CNN stacking. Combining **2D RoPE** for geometric awareness with a compressed **1×1 bottleneck** achieves global spatial reasoning well within real-time CPU execution limits.

---

# C. Day 30: Terminal Vehicle Routing Optimization

![c01](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F4808143%2F8fe839fc6acd7f6a604e525f11f52db2%2Fc01_terminal_vrp.png?generation=1790813355731575&alt=media)

### Core Objective

At hour **h**, the heuristic algorithm selects an optimal plan **P** that maximizes net cash return:

$$\max_{P} \Delta \hat{M}(P) = R_{\text{sale}}(P) - C_{\text{hire}}(P) - C_{\text{opp}}(P)$$

* **R_sale(P)**: Projected revenue from delivered harvests.
* **C_hire(P)**: Total labor cost for additional workers.
* **C_opp(P)**: Opportunity cost of consumed resources.

### Key Operational Drivers

* **Value-Dense Selection**: Ranks candidate tasks by cash yield relative to time cost:

$$\text{Priority Score} = \frac{\text{Value}}{\Delta t}$$

* **Cost-Efficient Insertion**: Assigns tasks to worker routes based on minimal travel overhead, dynamically expanding workforce size only when marginal gains exceed hiring costs (**C_hire**).
* **Parallel Execution**: Coordinates concurrent worker routes to ensure complete pipeline execution (**Harvest → Drop → Sell**) before deadline expiration.

### Limitation: Scaling to General Days (Days 1–29)

Unlike Day 30 where terminal value is zero (**V_31 = 0**), earlier days require solving a recursive multi-stage value function where today's action plan **P_t** dynamically reshapes tomorrow's state **S_{t+1}**:

$$V_t(s) = \max_{P_t} \left( \Delta M_t(P_t) + \mathbb{E}\left[V_{t+1}(S_{t+1})\right] \right)$$

* **Nested Combinatorial Explosion**: Evaluating a single candidate plan **P_t** requires recursively solving a full route optimization problem for every generated downstream state **S_{t+1}**.
* **Systemic Solution**: The **Neural Network** handles Days 1–29 by directly approximating future continuation value **V_{t+1}**, reserving the heuristic exclusively for single-period terminal liquidation (**V_31 = 0**).

---

# D. Conclusion & Future Directions

Training with GiGPO under an unconstrained opening strategy enabled rich exploration, but exposed a core long-horizon challenge: **state detachment** (akin to Go-Explore). High-value late-game strategies rely on specific early farm configurations. As the opening policy evolved, these favorable intermediate states became rare, preventing the policy from repeatedly reaching and refining effective late-game continuations.

To address this, future work points toward a **Reverse Curriculum Learning** framework:

1. **Intermediate State Freezing**: Fix selected openings or preserve promising intermediate farm states during training, allowing late-game policies (production, liquidation) to stabilize under consistent conditions.
2. **Progressive Opening Expansion**: Gradually re-introduce diverse opening layouts only after late-game continuations demonstrate reliable competence.

Structuring training to reliably return to valuable discovered states—rather than continually shifting the opening distribution—offers a clear path toward more compute-efficient long-horizon planning.