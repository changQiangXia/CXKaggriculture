> **来源 / Source**：Kaggle Kaggriculture 公开 write-up，第 28 名，队伍 **吃白饭的大肥鱼**。
> **原文**：https://www.kaggle.com/competitions/kaggriculture/writeups/28th-place-gold-solution-how-we-taught-a-farm-to
> 本文为比赛归档的离线副本，仅作技术参考；**版权归原作者所有**。
> 如作者要求撤下，请联系仓库所有者。

# 28th Place Gold Solution — How We Taught a Farm to Make Decisions

**28th place · Gold · Kaggriculture 2026**<br>
*A learned policy controls the first ten days; a planner then chooses what to grow, who does the work, and when to sell.*

<!-- paragraph -->

**Team 吃白饭的大肥鱼** — Gengsr · 醇久 (deepios) · TanPowasd · Tang Di24

[![Read from left to right: opening actions, the handover of recorded history, and continued planning. From day 10, daily plans coordinate future production, labor and purchases, while the hourly executor compares the next actions using new observations. The bottom strip marks the transition and main settings.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F130a3b62a9279f9fad630c9ab3b916c6%2F01_three_stage_system.png?generation=1792200935819421&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F130a3b62a9279f9fad630c9ab3b916c6%2F01_three_stage_system.png?generation=1792200935819421&alt=media)

**Illustration 01 · From the opening policy to the planner** *Read from left to right: opening actions, the handover of recorded history, and continued planning. From day 10, daily plans coordinate future production, labor and purchases, while the hourly executor compares the next actions using new observations. The bottom strip marks the transition and main settings.*

<!-- paragraph -->

A farm can look profitable and still run out of cash before its next harvest. Crops need care, animals need feed, and workers must deliver goods to the shed before they can be sold. Our Kaggriculture agent had to choose what to produce while keeping that whole sequence affordable and executable, hour by hour, until the season ended.

<!-- paragraph -->

Games involving Majkel1337, DSM, M & M & P & Q and DECEM showed several ways to manage these dependencies. A small cash balance could be enough when a delivery was about to fund the next purchase. A much larger balance could hide a farm with too little production capacity. We built the agent around the work and income still ahead: when each crop would mature, who could service it, when goods would reach the shed, and what both farms might earn from the shared market.

<!-- paragraph -->

We finished **28th of 10,148 teams**, with a **gold medal** and a final leaderboard score of **5111.2**. Our highest-scoring submission was **56720575**, the re-submitted **C2O7** agent. That leaderboard score is a competition rating, distinct from the cash earned inside an individual game. [Official final standings](https://www.kaggle.com/competitions/kaggriculture/leaderboard)

<!-- paragraph -->

Our agent used a learned policy for the first ten days, followed by a Rust planner for the rest of the game. The opening network coordinated setup actions. The planner chose production projects, assigned workers, built routes and scheduled sales within a limited computation budget. We also submitted a later experimental branch in our other final slot. We discuss its experiments separately from C2O7, because several late changes improved local measurements while the earlier agent produced our best final leaderboard result.

<!-- paragraph -->

This article follows the decisions the agent had to make: learn a coordinated opening, plan production and labor at dawn, then revise routes, purchases and sales as each hour unfolds. The experiments show where that design worked and where an apparently useful improvement failed to help the complete agent. During the final week, we used a Chinese-made PPU accelerator platform for learning alongside CPU simulation and game evaluation.

## 1. Turn production into cash before the season ends

Each player operates a separate 10×10 farm, starting with one unlocked quadrant and the option to buy more land. Crops and animals take inputs, work and time to produce goods. Workers move between tiles, carry items and perform jobs; the farm sells its output into shared product markets whose prices respond to inventory. The configured season lasts 30 days, and the final reward is the player's money. Assets therefore help only through income that the farm can earn and settle before termination. [Official game documentation](https://github.com/Kaggle/kaggle-environments/blob/28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c/kaggle_environments/envs/kaggriculture/README.md), [interpreter](https://github.com/Kaggle/kaggle-environments/blob/28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c/kaggle_environments/envs/kaggriculture/kaggriculture.py)

### The same cash balance can hide different farms

[![The schematic farms differ in crop ages, unfinished work and goods in transit. Dotted connections link current resources to possible future sales, showing which future receipts a farm valuation needs to consider.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F012c20ee2310fba9e83534b08a6223d9%2F02_equal_cash_different_farms.png?generation=1792201031229941&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F012c20ee2310fba9e83534b08a6223d9%2F02_equal_cash_different_farms.png?generation=1792201031229941&alt=media)

**Illustration 02 · Equal cash, different farms** *The schematic farms differ in crop ages, unfinished work and goods in transit. Dotted connections link current resources to possible future sales, showing which future receipts a farm valuation needs to consider.*

<!-- paragraph -->

One historical game showed how little a cash balance reveals about future production. At the beginning of day 16, our cash balance was **31,771** and DECEM's was **31,710**. Six days earlier, DECEM had sold a batch of melons and bought its fourth land quadrant in the same hour. We sold our melons too; by the following hour we had **7,712** in cash, but stayed at three quadrants. The almost equal cash balances on day 16 belonged to different farms: DECEM had more land, more tomatoes and more strawberries, with work still needed to turn those assets into money.

<!-- paragraph -->

We finished that game with **80,713 to DECEM's 99,340**. The cash gap narrowed by 2,344 on the last day, so most of it had accumulated before final liquidation. This was **CAND2 against DECEM**, episode **115509423**: CAND2 used the same native planner as C2O7 but an earlier opening checkpoint. The two farms reached almost equal cash balances with different production capacity and different work still ahead.

[![Daily cash and land ownership for CAND2 and DECEM in episode 115509423.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F13ec4980699c4c50aac9fb1d5b23d324%2FA_cash_and_capacity.png?generation=1792201097719483&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F13ec4980699c4c50aac9fb1d5b23d324%2FA_cash_and_capacity.png?generation=1792201097719483&alt=media)

*Data figure A. Cash at the start of each day and at termination in episode 115509423. The lower panel shows unlocked quadrants. At day 16, CAND2 and DECEM had almost equal cash balances and different land and production capacity.*

### Connect each production choice to the work and sale it requires

“Grow more tomatoes” therefore leaves most of the work undecided. The planner must find a tile that will be available in time, pay for seed without interrupting feed purchases, assign someone to plant and water it, and return for later care. It must check when the first harvest arrives and whether the remaining harvests can justify the setup before the season ends. It must also find workers who can collect the output and reach the shed before the intended sale. When several projects mature together, those projects compete for the same labor and storage.

<!-- paragraph -->

A forecast price alone cannot settle these choices. A crop may look profitable but consume a worker needed elsewhere. An affordable worker may have no useful task that can be reached in time. An expansion may promise a positive return but miss the hour when cash, inputs and labor are all available. We needed the planner to represent each part of the proposed sequence so that a failed plan could be traced to the missing money, work, delivery or sale.

[![Inputs and care produce goods; workers harvest, carry and deliver them; market orders turn the stock into cash. Following this sequence connects a production schedule to the next purchase it can finance.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F0f27398abbd1b5520d70b7b0b70fd84b%2F03_seed_to_cash.png?generation=1792201125033971&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F0f27398abbd1b5520d70b7b0b70fd84b%2F03_seed_to_cash.png?generation=1792201125033971&alt=media)

**Illustration 03 · The work behind a sale** *Inputs and care produce goods; workers harvest, carry and deliver them; market orders turn the stock into cash. Following this sequence connects a production schedule to the next purchase it can finance.*

<!-- paragraph -->

Majkel1337 showed why delivery belonged inside the investment calculation. In episode **110620339**, its farmer carried six units of wool at day 6, hour 3, while cash was only **303**. Dropping the wool put it in the shed, but the land order still failed. Selling those six units in the following hour raised cash to **1,588**. At hour 5, the farm bought its second quadrant and three units of wheat, leaving **495**. Majkel submission **56216119** was playing THIRD FARM CLUB **56326604**. The wool already had value in the farmer's bag, but it could pay for land only after delivery and sale.

<!-- paragraph -->

Both farms can produce the same good, so neither can value a harvest in isolation. A large batch may begin selling at a high price and end at a much lower one. Above the price floor, our own output changes market inventory as it is sold; the rival's output can reach the market while ours is still growing. The value of a crop therefore depends on the production and sales calendars of both farms.

<!-- paragraph -->

Data figure B shows this price response for six products, using the official rule when inventory is above its reference level. All panels use the same horizontal scale. Wheat and eggs decline slowly over the plotted range, while strawberry, milk and wool prices reach the floor with comparatively little surplus. Melon follows a different nonlinear curve. These differences make the timing and combination of production important: each product encounters a different price response as the farms sell their output.

[![Six official market price curves as inventory rises above its reference level.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F5a237c6cd806adcce07eca0b44e5d653%2FB_market_curves.png?generation=1792201154742054&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F5a237c6cd806adcce07eca0b44e5d653%2FB_market_curves.png?generation=1792201154742054&alt=media)

*Data figure B. Instantaneous price quotes from the official `MARKET_PARAMS` and `market_price` function, including integer rounding and the floor. Each panel has its own price scale; surplus inventory units share one horizontal scale. A batch settles unit by unit along the changing quotes. At the price floor, a sale credits cash while market inventory stays unchanged.*

<!-- paragraph -->

The market connects the players through prices. When we sell, the interpreter credits our account. Above the floor, that sale also increases market inventory and can lower the quotes available to later sellers, including the rival. Each player keeps a separate cash account; the competitive effect comes through subsequent sale prices. [Market settlement implementation](https://github.com/Kaggle/kaggle-environments/blob/28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c/kaggle_environments/envs/kaggriculture/kaggriculture.py#L652-L688)

## 2. Learn the opening, then plan the farm it leaves behind

Strong public games contained repeatable ways to organize the many dependent choices at the start. A learned opening could absorb those patterns without requiring us to write a rule for each one. As the game progressed, the farm became more specific to its own history: crops had different ages, inventories differed, animals needed maintenance, and market opportunities changed. We used explicit planning to compare possible continuations of that particular state.

<!-- paragraph -->

The opening's job was to leave a farm that the planner could continue successfully. Its value depended on the inherited crop ages, animal care, worker locations and upcoming receipts. For example, near-term deliveries could make a relatively cash-poor farm ready to expand. We evaluated the opening together with the controller that would service those assets and use those receipts.

<!-- paragraph -->

Learning from recorded actions also raises a familiar problem. Once the learner makes a different choice, it may reach states absent from the expert recordings. DAgger addresses this distribution shift by collecting expert actions on states visited by the learner. With offline replay training, complete-game evaluation provides the complementary test of how the opening and its later controller behave after the learner makes its own choices. [Ross, Gordon and Bagnell, 2011](https://proceedings.mlr.press/v15/ross11a.html)

<!-- paragraph -->

Our learning code included imitation-learning and reinforcement-learning components, including PPO. The deployed opening used the fixed **OV7 v90** checkpoint; the architecture and decoder below describe the policy that acted during the game. [PPO method background](https://arxiv.org/abs/1707.06347)

### Control changes at fixed steps, with a transition period

The deployed agent follows three phases. It uses the learned opening at steps **0–239**, covering days **0–9**. The compiled Rust planner takes over at step **240** and initially uses a transition configuration that disables several later mechanisms. At step **384**, the main configuration begins and remains in use for days **16–29**. These are explicit step-based switches in the deployed configuration.

<!-- paragraph -->

Once the planner is in control, it makes decisions at two time scales. At dawn it chooses what the farm should produce over the remaining days and derives today's jobs. During each following hour it revisits the remaining work, crew, purchases and sales from the state the farm has actually reached. A crop project can span several days even while the route used to service it changes from hour to hour.

<!-- paragraph -->

The transition configuration also checks land ownership. Owning the fourth quadrant enables stronger labor and budget treatment before day 16, bringing those two parts of the main configuration forward for the larger farm.

### The opening network reads the board and the market

The opening network receives **39 spatial planes on a 10×10 grid** and **142 global features**. Three categorical planes expand into one-hot channels, giving the convolutional stem **66 input channels**.

<!-- paragraph -->

The spatial planes describe both farms' tiles, including contents, age, available yield, watering or feeding status, fertilization, remaining lifetime and unit locations. Other planes describe our carried goods, shed access and distance, and quadrant identity. The global features add money, inventories, seeds, workforce, land ownership, prices, market inventory, shops, demand and recent market flow. Together, these inputs let the network consider the state of a crop alongside the economy into which its output will arrive.

<!-- paragraph -->

The stem combines local convolutional features with a projection of the global vector broadcast across the board. A **64-channel trunk with six residual blocks** processes that combined representation. Each block applies two spatial convolutions and a skip connection, so the network can revise the board features while retaining information from earlier layers.

<!-- paragraph -->

The trunk feeds two kinds of output. On the board, it produces operation and quantity logits at each tile: numerical scores for an action and its amount. It also averages the board features and combines them with the projected global vector to form a **128-dimensional context** for market decisions.

<!-- paragraph -->

Several workers can stand on the same tile but carry different goods, so the tile representation alone cannot tell each worker what to do. The deployed v3 policy gives each unit a token—a numerical vector representing that unit—that combines its current tile representation, index, inventory and previous action. The decoder selects actions sequentially. Each unit attends to the tokens and actions already chosen for earlier units in the current step, then adjusts the tile logits for its own decision. After those decisions, the market head receives a summary of the selected unit actions.

<!-- paragraph -->

The attention coordinates workers within the current step, while previous-action inputs and market-flow state supply short-term context. The deployed network uses these explicit inputs rather than a recurrent state spanning the whole game. Its checkpoint also contains movement-pointer parameters, with pointer decoding disabled in the header.

[![On the left, 39 board-feature planes expand to 66 channels, while global information enters the spatial trunk and the pooled branch. The trunk has 64 channels and six residual blocks. On the right, unit actions are chosen first and then supplied to the market branch.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F9ab41be5502846424f1387dccd93405c%2F04_deployed_opening_network.png?generation=1792201195895225&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F9ab41be5502846424f1387dccd93405c%2F04_deployed_opening_network.png?generation=1792201195895225&alt=media)

**Illustration 04 · How the opening network chooses actions** *On the left, 39 board-feature planes expand to 66 channels, while global information enters the spatial trunk and the pooled branch. The trunk has 64 channels and six residual blocks. On the right, unit actions are chosen first and then supplied to the market branch.*

### The decoder turns scores into legal actions without spending resources twice

The policy scores **44 unit-operation categories** as well as grouped market choices. Its action format can represent **32 units** and **10 market orders**. The market network itself has **21 groups**, each with **101 classes**, including a no-order class. These dimensions define the action representation's capacity; actual crew and order counts vary with the state.

<!-- paragraph -->

During decoding, legal masks remove invalid choices and a running resource account limits what later units can use. Several workers cannot all spend the same remaining seed. After one worker selects a pickup, the decoder reduces the stock available to the others. In the v3 model, it also suppresses repeated tile-work operations on a shared tile, while allowing repeated movement or pickup. Several workers may need to leave together, but repeating a watering operation on one plant does not service another plant.

<!-- paragraph -->

The decoder then builds market orders in a fixed group order. Each group must pass its threshold for issuing an order, and the requested quantity must fit the available cash, shed room and relevant stock. It credits provisional sale proceeds before forming later purchase orders. The game then settles the constructed list against market conditions and the rival's concurrent orders.

<!-- paragraph -->

During play, the compiled policy uses greedy decoding: at each choice it selects the highest-scored option that remains allowed. If weights are missing, input is malformed or output is non-finite, it reports an error. The wrapper then uses the fallback planner for that player for the rest of the game. This error path transfers control to a planner that can continue the game.

[![Blue arrows follow the order in which workers choose. Each selected action reserves its items in the resource ledger, and the next worker chooses from the remaining stock. The lower panel distinguishes duplicate work assignments from shared transit locations; the right panel shows the order budget.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F3954976fe966a40f70889489f04d13d7%2F05_legal_decoding.png?generation=1792201223170389&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F3954976fe966a40f70889489f04d13d7%2F05_legal_decoding.png?generation=1792201223170389&alt=media)

**Illustration 05 · Sharing stock across workers** *Blue arrows follow the order in which workers choose. Each selected action reserves its items in the resource ledger, and the next worker chooses from the remaining stock. The lower panel distinguishes duplicate work assignments from shared transit locations; the right panel shows the order budget.*

### At handover, replay the observed history through the planner's trackers

The day-10 observation gives the planner the current farm, but some of its information has to be accumulated over time. Rival-flow estimates, inventory beliefs, market adjustments and arrival histories depend on earlier observations. Initializing those trackers as empty at takeover would throw away what the opening had already observed.

<!-- paragraph -->

The wrapper therefore records every observation and chosen action during the learned opening. When SafeAgent first takes control, it checks that the final log entry is from the step immediately before handover, then feeds that history through the trackers. Those recorded observations and actions update the trackers in their original order. If warming fails, the wrapper clears the partially initialized state.

<!-- paragraph -->

The planner therefore takes over with both the current farm and trackers initialized from the preceding observations and actions. The decision maker changes, while the accumulated information remains available.

[![The lower strip holds opening observations and actions. The entrypoint checks the last record and then updates the trackers in sequence; the exception path clears tracker history and starts from fresh tracker state. Growing crops, carried goods and stored inventory remain in the continuing farm.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2Ffd6495fa6d725dbd28d7f8c75c5b5649%2F06_handover_history.png?generation=1792201238275478&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2Ffd6495fa6d725dbd28d7f8c75c5b5649%2F06_handover_history.png?generation=1792201238275478&alt=media)

**Illustration 06 · Passing the opening history to the planner** *The lower strip holds opening observations and actions. The entrypoint checks the last record and then updates the trackers in sequence; the exception path clears tracker history and starts from fresh tracker state. Growing crops, carried goods and stored inventory remain in the continuing farm.*

### At dawn, plan each tile's future work and production

At dawn, planning proceeds in three stages. First, generate possible futures for individual tiles. Second, choose a combination whose production and labor requirements work together across the farm. Third, construct today's worker routes and use their actual demands to revise the economic calculation.

<!-- paragraph -->

The planner represents a tile's future with a **Project**: dated rows listing operations, required inputs and expected outputs. A project may continue an existing crop, care for an animal, harvest its output or reuse the tile after the current activity ends. The portfolio selects one project per tile and combines their requirements, exposing work and production that overlap on future days.

<!-- paragraph -->

For a crop, one possible project plants and waters today, returns for later watering, fertilizes when useful, then harvests and either clears or continues the crop. The crop dynamic program generates alternatives by stepping through watering, fertilizing and harvesting choices. It carries forward dry days, age and yield along a directed acyclic graph whose dates always advance. To compare those paths, it uses the current labor prices and marginal product values: the estimated value of one extra unit produced on a particular day. The biological schedule is therefore evaluated under the economic conditions that the larger planner currently expects.

<!-- paragraph -->

The planner cannot choose the most profitable project for each tile independently. Those projects may all require workers on the same day or send the same product into an already crowded market. As the portfolio changes, it updates market marginal values and labor shadow prices, which estimate the additional cost of one more unit of work on a given day. It recomputes the objective before accepting a replacement project; the stored acceptance threshold requires an improvement greater than **1.0**.

<!-- paragraph -->

The core portfolio score is

$$
J(P)=B(F(P))-L(W(P))-C(P).
$$

Here, *P* is the selected set of tile projects. *F(P)* is the dated calendar of their product flows, and *B* values those flows through the market book. *W(P)* is the modeled work required on future days, *L* converts it to labor cost, and *C* subtracts seed and animal capital costs. This is the objective used to compare modeled continuations of the farm.

[![The two candidate schedules place care, inputs and harvests on future dates. The lower-right panel combines product supply, labor and purchases for a farm-wide comparison. The lower-left panel shows admission of new planting proposals, while established crops continue along their schedules.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2Ff798859a01a0ac5bdf18fe5e4d7c2dc3%2F07_dated_projects.png?generation=1792201267403847&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2Ff798859a01a0ac5bdf18fe5e4d7c2dc3%2F07_dated_projects.png?generation=1792201267403847&alt=media)

**Illustration 07 · Combining tile schedules into a farm plan** *The two candidate schedules place care, inputs and harvests on future dates. The lower-right panel combines product supply, labor and purchases for a farm-wide comparison. The lower-left panel shows admission of new planting proposals, while established crops continue along their schedules.*

### Check whether workers can actually complete the chosen jobs

Routing every possible portfolio would be expensive, so the first labor calculation uses a cheaper estimate. For each nonempty project row, the code charges **operation count + 1.4 + shed distance/8 + output units/8** work units. The added terms allow for visiting the tile and carrying output. A wage surrogate converts the combined work into the increasing cost of adding more hands.

<!-- paragraph -->

After selecting projects, the planner converts today's requirements into jobs and tests workforce sizes with a route solver. It accounts for each worker's starting location, pickup detours, operation order, travel between jobs, and required return or delivery. The validator checks job coverage, required resources and time. This second calculation asks whether the estimated work fits into actual routes, including cases where two otherwise attractive jobs are far apart.

<!-- paragraph -->

Crew selection weighs wages against the value of work left uncovered. It can drop optional work while keeping mandatory work represented. When the bounded route search finds a complete feasible schedule, the planner retains it as a witness, called a “certificate” in the code. That schedule specifies how the modeled jobs fit into the workers' routes and available time.

<!-- paragraph -->

The constructed routes can change the economic choice. If the required crew costs more than the portfolio expected, the planner can raise its labor multiplier and optimize the projects again. It keeps alternatives and compares them using today's selected wage and the cost of uncovered jobs. Route construction therefore helps determine which production plan is worth adopting.

[![Colored routes connect workers to jobs, with required and optional tasks distinguished at the upper right. The lower panels show input collection and time spent traveling, working and returning. Constructed crew costs and uncovered tasks then inform revisions to the production plan.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F84ae4aa888a8b8c3a18f3d594e2648a9%2F08_crew_and_routes.png?generation=1792201289057755&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F84ae4aa888a8b8c3a18f3d594e2648a9%2F08_crew_and_routes.png?generation=1792201289057755&alt=media)

**Illustration 08 · Can the workers finish these jobs?** *Colored routes connect workers to jobs, with required and optional tasks distinguished at the upper right. The lower panels show input collection and time spent traveling, working and returning. Constructed crew costs and uncovered tasks then inform revisions to the production plan.*

## 3. Choose work routes and sale times together

The rival's visible farm tells us which crops and animals exist now. It does not reveal exactly what the rival will plant, build or sell next. Our planner needs a forecast to compare future income, and different forecasts answer different parts of that question. Estimating when the rival will sell an approaching harvest is not the same as estimating what it will produce after clearing the tile.

<!-- paragraph -->

Imagine two opponents with identical mature wheat tiles. One harvests and replants wheat; the other replaces the wheat with a different crop. Their visible wheat production looks the same at the current step, but they create different supply later, when our own harvest may be ready. Expansion into another quadrant or a change in herd composition creates the same problem. Forecasting these later choices calls for a model of future production as well as near-term selling behavior.

### Each hour, compare the remaining routes with other ways to finish the work

The hourly planner starts from the latest observation and each worker's remaining task queue. It first evaluates continuing the installed plan. It then proposes alternatives: edit some routes, solve the routes again, hire workers together with the inputs they need, or act on a stock-management proposal. Eligibility checks avoid conflicts with pending capital purchases and time-sensitive sales, while the time budget limits how many alternatives can be examined.

<!-- paragraph -->

For an alternative that requires purchases, the planner simulates the purchase step and then constructs routes from the resulting state. The requested worker or input becomes available only when that transition supplies it, with the appropriate delay. Actions already committed for the first step are carried into the candidate as well.

<!-- paragraph -->

Candidate evaluation thus uses a simulated purchase transition to obtain the state from which future routes start. Within an actual game step, unit actions run before the market. A worker can therefore deliver goods that are sold later in the same step, and an earlier sale order can fund a later purchase order. New market purchases become inputs to subsequent unit actions.

<!-- paragraph -->

Each candidate then gets its own sales plan: different routes can deliver goods at different hours, changing both storage pressure and the prices available. All candidates face the **same sampled rival trajectories** during the comparison. Otherwise, an alternative could appear better simply because it was evaluated against a more favorable sample of the opponent's behavior.

<!-- paragraph -->

The evaluator combines the simulated cash changes with the value of remaining goods, seeds and future tile use. A candidate replaces the installed plan only when its estimated gain clears the threshold. The agent then issues the immediate work actions and first-step sales associated with that choice; the live market path caps sales at the quantity actually available. At the next observation, it evaluates the remaining continuation again. Future values still depend on the forecast, but the route, expected deliveries and immediate selling decision are evaluated together.

[![Each middle column is a simulated alternative with its own sales schedule. All candidates use the same rival samples shown above. Purchase-dependent candidates first simulate the resulting state, then construct subsequent routes. The selected immediate actions are submitted before the next observation is read.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F0b1fadd3a009ebf72cdedce7d0e35501%2F09_hourly_continuations.png?generation=1792201314346072&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F0b1fadd3a009ebf72cdedce7d0e35501%2F09_hourly_continuations.png?generation=1792201314346072&alt=media)

**Illustration 09 · Keep the current routes or choose another plan?** *Each middle column is a simulated alternative with its own sales schedule. All candidates use the same rival samples shown above. Purchase-dependent candidates first simulate the resulting state, then construct subsequent routes. The selected immediate actions are submitted before the next observation is read.*

<!-- paragraph -->

This loop resembles receding-horizon control: calculate a continuation from the current state, apply its immediate decision, observe the result, and calculate again. We implement that pattern with bounded route search and sampled market forecasts. [Mayne et al., 2000](<https://doi.org/10.1016/S0005-1098(99)00214-9>)

<!-- paragraph -->

M & M & P & Q's game against DSM makes the financing sequence concrete. In episode **111099760**, M&M submission **56371729** began day 8, hour 6, with **544** in cash. Workers delivered twelve units of milk. Market order 0 sold them for **2,425**; order 1 bought a sheep for **500**; order 2 bought the next quadrant for **2,000**, leaving **469**. The sheep entered storage and still had to be placed before it could produce. In the same game, DSM submission **56376434** tried to buy its third quadrant at day 9, hour 3, with **1,047** and failed. Wool sales at hours 4 and 5 brought cash to **1,932** and then **2,801**; the land purchase then succeeded, leaving **801**. These sequences show exactly which receipts funded each purchase.

### Schedule sales across time while sharing shed space

[![Both farms contribute to market inventory and prices above a shed shared by multiple products. The left panel shows stored goods competing with later deliveries for space, and the bottom schedules batches over time. At the price floor, the seller is paid while the sold unit adds no further market inventory.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F39b61af6b142010cd289692d7bf0392e%2F10_market_and_storage.png?generation=1792201338070578&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F39b61af6b142010cd289692d7bf0392e%2F10_market_and_storage.png?generation=1792201338070578&alt=media)

**Illustration 10 · When to sell and how much to hold** *Both farms contribute to market inventory and prices above a shed shared by multiple products. The left panel shows stored goods competing with later deliveries for space, and the bottom schedules batches over time. At the price floor, the seller is paid while the sold unit adds no further market inventory.*

<!-- paragraph -->

Selling now releases cash and storage; keeping goods may let the farm sell after later demand has raised the price. Our sales can also affect the price the rival receives. The market calculation therefore evaluates a competitive cash margin, including the effect on the opponent's receipts, rather than adding up only our own sales.

<!-- paragraph -->

DSM's game against Majkel1337 in episode **111253699** showed both sides of that choice. DSM submission **56376434** began day 7 with **96** in cash and financed feed through fertilizer collected, delivered and sold during the day. At day 8, hour 1, it started with **102**: six delivered units of milk sold for **1,091**, another worker cost **34**, and thirteen units of wheat cost **468**, leaving **691**. Later, the same agent kept milk and wool across days; Majkel submission **56216119** also carried substantial inventories. DSM used an immediate sale to pay for the next obligation while other goods could wait for a later market. The post-game replay reveals these private inventories; during play, our agent estimates the rival's stock from observable history.

[![The left column follows Majkel's wool from delivery through sale to a land purchase. The center contrasts M&M's milk-funded purchases with DSM's successive wool sales before buying land. The right column follows DSM's milk receipts into labor and feed. Arrows show the event order in the three games discussed in the text.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2Fafdd278a60301af86fc11249f6517861%2F11_rival_business_chains.png?generation=1792201347014826&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2Fafdd278a60301af86fc11249f6517861%2F11_rival_business_chains.png?generation=1792201347014826&alt=media)

**Illustration 11 · Sales and purchases across three games** *The left column follows Majkel's wool from delivery through sale to a land purchase. The center contrasts M&M's milk-funded purchases with DSM's successive wool sales before buying land. The right column follows DSM's milk receipts into labor and feed. Arrows show the event order in the three games discussed in the text.*

<!-- paragraph -->

For a single product, let *A_i* be the units available by decision time *i*, including initial shed stock and later arrivals, and *C_i* the cumulative number sold by then. A feasible schedule satisfies

$$
0\le C_{i-1}\le C_i\le A_i,
$$

and sells the available units by the end of its horizon. The solver samples a timeline of rival flows and town consumption. Our cumulative sales shift market inventory along that timeline. An integer price-prefix table expresses each scenario's score as a sum of terms that depend on *C_i*, allowing dynamic programming to search cumulative quantities instead of enumerating every possible sequence of orders.

<!-- paragraph -->

With scenarios fixed and away from the price floor, this dynamic program solves the single-product subproblem exactly. The floor needs special treatment: a sale at the floor earns money without adding that unit to market inventory, so cumulative sales no longer shift the inventory path in the simple additive way assumed by the formula. The implementation evaluates proposed schedules using exact unit settlement and applies bounded local search in this case.

<!-- paragraph -->

Products also share shed space: milk held for later competes with strawberries held for later. The solver uses Lagrangian relaxation, assigning a storage charge to each product and solving its schedule under that charge. Repair and local search then seek a feasible combined schedule. The calculation also leaves room for immediate purchases and accounts for cash commitments. The exact single-product result therefore sits inside a broader heuristic search over products, capacity and uncertain rival behavior.

<!-- paragraph -->

The rival forecast supplies the uncertain part of that calculation. In the main phase, the planner uses the learned model of rival sales for the next **72 hours**. Beyond that window, it projects production and assumes that a harvested tile is replanted with the same crop, also accounting for sales near the end of the game. This lets the market calculation combine learned near-term selling behavior with a longer view of what the rival's farm will produce.

<!-- paragraph -->

The code has a separate branch for explicit win-probability optimization. C2O7's main configuration sets that branch to activate on day **99**, leaving competitive margin as the objective throughout the season. Seeking a larger competitive margin and seeking a higher probability of ending above zero are related choices, but they can favor different actions.

### Save enough computation for later decisions

The farm has to budget computation as well as cash and labor. C2O7 reserves **20 seconds** of overage for later play and divides the remaining excess among the heavy steps still to come. The configured executor cap is **0.6 seconds** per local call, and dawn search has a **3.0-second** cap. These settings allocate the available search time across the remaining decisions.

<!-- paragraph -->

As the time pool shrinks, the planner first turns off expensive market searches for individual candidates, then eventually disables the executor. It checks deadlines between units of work and keeps the installed plan or the best result found so far. An in-progress work unit finishes before the next deadline check, so the check frequency determines how closely execution follows the allocated budget.

<!-- paragraph -->

If planning fails, a separate fallback sequence tries configured, neutral, cheap and fresh planner states before resorting to pass actions. Guarded calls retain the pre-call state, so a failed attempt does not leave a partially updated planner as the starting point for recovery.

[![The time reserve on the left determines the search budget. Deadline checks occur between units of work, with the current plan or a better result retained along the way. The lower path shows fallback attempts after planning errors.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2Ff07cd11cc0d4c56a37c3b6287f12af70%2F12_runtime_budget.png?generation=1792201359256336&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2Ff07cd11cc0d4c56a37c3b6287f12af70%2F12_runtime_budget.png?generation=1792201359256336&alt=media)

**Illustration 12 · Budgeting time for search and fallback** *The time reserve on the left determines the search budget. Deadline checks occur between units of work, with the current plan or a better result retained along the way. The lower path shows fallback attempts after planning errors.*

## 4. Test predictions, decisions and game results separately

More production, earlier sales and fewer idle worker-hours could all look useful while the farm finished with a smaller advantage. A better forecast could leave the planner choosing the same actions. A successful local test could also use an executable, time policy or opponent response different from the online setting. We encountered each of these problems often enough that we stopped treating one improved measurement as an answer to all of them.

### Each test answers a different question

We used five kinds of checks. Replay reconstruction asked whether extracted data matched the game that had actually happened. Held-out prediction compared a model with observations it had not trained on. Continuation screens compared candidate policies from controlled historical states. Reactive games let the opposing agent change its behavior in response. Official runtime checks asked whether the packaged executable completed through the required interface and within its timing constraints. Together, they covered data conversion, forecast quality, policy choices, opponent response and execution.

<!-- paragraph -->

The largest late-stage screen used **320 paired cells from 261 episodes and 19 opponent teams**, based on a leaderboard snapshot frozen on September 30. Each cell was one episode-and-seat combination, so two cells could belong to the same episode. We reconstructed the first 240 steps to warm the planner, then let it take control at day 10. The opponent's farm and private state followed the saved tape; its cash still changed with the shared market. We fixed the time bank and disabled ordinary time-based cutoffs to compare policy choices under the same conditions. Reactive play and live timing were tested separately.

<!-- paragraph -->

Score differences below are paired candidate-minus-baseline outcomes, averaged over the stated cells. A bar labelled SE spans **one standard error** of those paired differences on each side of the mean. We also calculate cluster standard errors when cells share an episode or seed. The screen compared multiple candidates; its selection rule required every planned pair to finish, sufficient positive margin, no negative win-rate change, and agreement across two principal opponent classes. A candidate meeting those conditions moved on to further game tests.

[![The upper-left test fixes the opponent's recorded trajectory so candidates face the same background. The upper-right test lets the opponent act on the evolving game state. The lower panels check replay transitions and the packaged agent's path from loading to completed execution.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F99b07ec32509f07deefcbe3bc677ef04%2F13_evaluation_protocols.png?generation=1792201378206758&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F99b07ec32509f07deefcbe3bc677ef04%2F13_evaluation_protocols.png?generation=1792201378206758&alt=media)

**Illustration 13 · How we evaluate the agent** *The upper-left test fixes the opponent's recorded trajectory so candidates face the same background. The upper-right test lets the opponent act on the evolving game state. The lower panels check replay transitions and the packaged agent's path from loading to completed execution.*

### A better sales forecast barely changed the measured policy result

The opponent model predicts what the rival will sell and in what quantities. Those sales affect the value of our own future output. Near the deadline, on the later experimental branch, we refreshed the model using 1,500 recorded games in experiment W17. We first checked that both final scores in every converted game matched the original record. Before training, we held out 225 complete episodes, with no seed overlap between training and test. Splitting complete games kept neighboring records from the same game out of opposite sides of the split.

<!-- paragraph -->

We kept the architecture unchanged: 53 inputs, two hidden layers of width 128, and 65 outputs per family. A family is an opponent group with a separate output head, either the V8 lineage or the top-opponent cohort. Each head predicts 0 through 63 units as individual sale-quantity classes and uses one final class for 64 or more. We trained for 12 epochs and replaced only the exported model resource. Training, internal validation and final holdout together contained about eight million rows. The main test used the top-opponent family: 174 held-out trajectories produced 1,125,954 one-step prediction rows and 9,396 windows for 24-step evaluation. The complete game is the grouping unit behind these repeated within-game prediction rows.

<!-- paragraph -->

The new model improved the primary metric declared before evaluation. Negative log-likelihood for the top-opponent family fell from **0.22603 to 0.20414**. Across nine products, mean 24-step MAE fell from **2.2623 to 2.2031**, and CRPS from **1.6990 to 1.6244**. Tomato's relative bias in expected sales moved from **−16.56% to +0.55%**. The aggregate improvement was uneven: milk, wool and fertilizer became worse on both reported rollout MAE and CRPS. All products improved on one-step likelihood, which measures a different error from the rollout metrics.

<!-- paragraph -->

After we inserted the refreshed model into the same late-game system, the 320-cell policy screen gave **+19.7 ±45.4 SE** in score margin over its immediate predecessor, **cx_bl**, with **zero observed change in win rate**. The prediction improvement had produced only a small measured change in policy performance relative to its standard error. A comparison against **c2ov225** gave **+614.4 ±149.6 SE**, but cx_bl already contained other changes relative to that baseline. The larger difference measures the accumulated changes in the package.

<!-- paragraph -->

The useful next question was which decisions a better forecast could change. A cash constraint, an unreachable job or an existing production commitment can make the selected action insensitive to small forecast improvements. We would focus further model work on states where different plausible forecasts lead to different feasible plans, then test whether the more accurate forecast selects the better continuation.

<!-- paragraph -->

The prediction metrics ask different questions. Negative log-likelihood measures the probability assigned to the sale outcome that occurred. MAE compares predicted means with observed 24-step sales totals. CRPS evaluates the distribution predicted over numerical quantities. We report CRPS as a loss, so lower is better; this has the opposite sign from the reward-oriented convention in Gneiting and Raftery. Together, these metrics describe the fit of the one-step probabilities, the error in expected cumulative sales, and the quality of the predicted distributions. [Gneiting and Raftery, 2007](https://doi.org/10.1198/016214506000001437)

[![The left panel compares predicted and observed sales; the middle uses forecasts to score candidate plans; the right compares policy outcomes before and after the predictor update. W17 belongs to the later research branch, with its forecast metrics and paired-test results reported in Data figure C.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2Fc47c3b3be4326a030869910c4d150384%2F14_forecast_vs_decision.png?generation=1792201388565376&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2Fc47c3b3be4326a030869910c4d150384%2F14_forecast_vs_decision.png?generation=1792201388565376&alt=media)

**Illustration 14 · What changes after a forecast improves?** *The left panel compares predicted and observed sales; the middle uses forecasts to score candidate plans; the right compares policy outcomes before and after the predictor update. W17 belongs to the later research branch, with its forecast metrics and paired-test results reported in Data figure C.*

[![W17 reduces held-out prediction errors, while its paired comparison against cx_bl has a small mean policy change relative to its standard error.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F1ce36269f289405a78898d1ccf294d82%2FC_prediction_and_policy.png?generation=1792201399048004&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F1ce36269f289405a78898d1ccf294d82%2FC_prediction_and_policy.png?generation=1792201399048004&alt=media)

*Data figure C. W17 improves held-out prediction, while its incremental policy result over cx_bl is +19.73 ±45.39 paired-cell SE on 320 cells. MAE and CRPS are in product units; NLL is dimensionless. Prediction bars show aggregate point estimates; the policy bar shows the mean ±1 SE. This experiment belongs to the later branch.*

### Fitting the market model on more games slightly worsened one forecast loss

Another refresh rebuilt the Blend forecaster's market priors and mixture weights. **Blend** mixes samples from a mechanistic supply model and the existing learned opponent sampler, with weights fitted separately for each product and forecast-horizon window. The first fit used **346 games**; the expanded fit used **1,500**, with the same **106 held-out episodes** in both tests. We evaluated both observer seats from the day-10 handover, kept sampling settings fixed, and checked the market-impact labels against exact settlement.

<!-- paragraph -->

CRPS fell from **7.2440** with the old resources to **7.0745** after the first refresh. With the larger fitting corpus it rose to **7.0964**, still better than the old resources but slightly worse than the smaller refresh. The paired difference by episode was **+0.02185**, with a normal-approximation 95% interval of **[+0.00376, +0.03993]**. MAE changed slightly in the opposite direction.

<!-- paragraph -->

The larger corpus changed which opponents, phases and market states the model saw. More games therefore changed the fitted distribution as well as the sample count. In this comparison, the larger fit improved one error measure while slightly worsening another; corpus size alone was a poor guide to the quality of the resulting forecast.

### Late-hour jobs improved the tape score but lost margin against Rall

Some hired hands had already been paid but spent useful late hours idle. We added proposals for work they could still do and let the existing execution system evaluate those proposals. Separate variants changed dawn hiring or combined the two changes. Small behavior checks showed fewer idle work-hours, so we took the proposals into complete policy comparisons.

<!-- paragraph -->

The late-hours candidate was the only treatment to meet the selection rule in the complete current-opponent tape screen. Relative to c2ov225, its mean paired score-margin change was **+426.0 ±79.5 SE**; the episode-cluster SE was **83.5**. The win-rate change was smaller, **+0.94 percentage points**. We froze the exact package as cx_tape1 before the next stage. That package combined the late-hour proposals with shared execution changes already present in its lineage.

<!-- paragraph -->

The reactive Rall test gave a different answer. It covered **48 seeds in both seats: 96 paired cells and 192 games**. The candidate won **96 of 96**, while the baseline won **94 of 96**. Yet the candidate's average score advantage over its opponent was **484.5 points smaller**, with a paired-cell SE of **304.6**. Our rule required no observed regression in mean margin, so the package failed that gate despite winning two more games.

<!-- paragraph -->

Both the wins and the smaller margin can be explained by the recorded scores. Our final score rose by **123.2** on average, while Rall's score in those separate games rose by **607.8**, giving a margin change of **−484.5**. Forty-five pairs improved and fifty-one worsened. The two baseline losses converted into wins contributed **+13,603** points of total margin change; the remaining 94 pairs contributed **−60,119**. A comfortable win that becomes a smaller win still counts as one win. All of these quantities use the game scores returned by the Rall evaluation.

<!-- paragraph -->

The tape screen and Rall test use different opponent populations and protocols, including whether the rival responds to our actions. We treated them as separate stages of evaluation. The proposal that had reduced idle hours in behavior checks went on to win more Rall games with a smaller average advantage. Final margin captured a change that the job and win counts missed.

[![The same frozen candidate package has a positive margin change in the tape screen and a negative margin change against reactive Rall, under different opponent populations and protocols.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2Fba145bf004f7f9406483eb9cfb6db59f%2FD_protocol_change.png?generation=1792201417272145&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2Fba145bf004f7f9406483eb9cfb6db59f%2FD_protocol_change.png?generation=1792201417272145&alt=media)

*Data figure D. The same frozen package produces +426.0 in 320 tape cells and −484.5 in 96 paired reactive Rall cells. Error bars show ±1 episode-cluster SE for the tape screen and ±1 seed-cluster SE for Rall. The two tests use separate opponent populations and timing protocols.*

### A better codebook changed nothing because the chosen branch did not read it

In another final-night experiment, we refitted a 1,024-entry trajectory codebook without changing its deployed hyperparameters. The codebook compresses similar historical situations and the distributions of net flows over the next four hours. Its held-out forecast tests improved, including the required short-horizon CRPS measures. But the package still selected `mk_flow=1`, which used Blend. Only the alternative `mk_flow=2/3` branches consumed the refreshed codebook.

<!-- paragraph -->

With that configuration unchanged, the new package and its predecessor had identical score margins and win outcomes in every one of the **320 cells**. The refreshed resource performed better when evaluated directly, but the active decision path never read it. This failure was a useful reminder to connect a model experiment to the configuration and code that actually consume its output.

### Choose an opening the later planner can continue

Opening selection brought the same issue into the first ten days. In a 97-cell comparison with the same later controller, openings from our own lineage produced positive mean changes, while two openings cloned from strong opponents produced negative ones. An older own-lineage checkpoint also retained more of the baseline's already-winning games than the newer checkpoint. A strong opening had to leave a farm our particular controller could use: crop ages, worker locations, upcoming deliveries and maintenance obligations all mattered alongside cash.

<!-- paragraph -->

One earlier handover experiment made that dependency especially clear. A cold-started planner cleared **eleven strawberry plots that were still producing**, replacing work the opening had already invested in. We added a short protection period for crops already productive at takeover. Moving the handover earlier also changed where it fell in the opening's cash cycle: the planner could inherit the costs before the corresponding harvest receipts arrived. These experiences made continuity part of the design. The incoming controller needed to preserve useful commitments, service the inherited farm and carry its financing sequence forward.

### Train models on PPU accelerators and test agents on CPU workers

We increased accelerator capacity gradually during the final week, reaching **four ZW810-family cards** later in the week. The PPU-ZW810E platform provided a **48-core CPU quota and 336 GiB of system memory**. Learning jobs produced model resources for the agent, while CPU Slurm workers handled simulation and game evaluation. These were different workloads even when they ran on infrastructure that also contained accelerators.

<!-- paragraph -->

The opponent-network training script used the `cuda:0` software interface and trained for 12 epochs. The underlying hardware was a Chinese-made PPU platform. Alibaba Cloud documents the PPU-ZW810 family, while T-Head's SAIL documentation names PPU-ZW810E / Zhenwu 810E. [PPU-SMI documentation](https://help.aliyun.com/en/document_detail/2971881.html), [T-Head documentation](https://github.com/t-head/vllm-sail/blob/cc1b67eaa1bee9a7f375baaef16dff4015650fd1/docs/user_guide/supported_features.md)

<!-- paragraph -->

A learning update still had to pass through the CPU agent before it could affect a game. We exported the model resource, combined it with the intended code and configuration, compiled the agent, and evaluated that executable. Build scripts staged an explicit source-file list, locked source snapshots and compiled in node-local temporary directories. Separate target directories and cached build products reduced repeated compilation. We recorded content hashes for the source and executable together with the configuration, toolchain, runner and evaluation protocol, so results stayed associated with the version that produced them.

<!-- paragraph -->

That separation also helped diagnose failures across machines. One data refresh encountered a Cargo cache collision in the tooling build and a Python ABI mismatch when importing evaluation code. Those failures called for repairs to the build or evaluation environment, rather than changes to the candidate policy. Keeping model fitting, packaging and game evaluation as separate stages let us rerun the failed stage with the intended inputs.

[![Learning jobs train and export models on PPUs, the build combines code, weights and configuration, and CPU workers run games. Version identifiers carry through these steps so each test result maps to the program that produced it.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2Fa760eead444a2b22b95dbb253c846078%2F15_compute_workflow.png?generation=1792201429261770&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2Fa760eead444a2b22b95dbb253c846078%2F15_compute_workflow.png?generation=1792201429261770&alt=media)

**Illustration 15 · From training a model to running games** *Learning jobs train and export models on PPUs, the build combines code, weights and configuration, and CPU workers run games. Version identifiers carry through these steps so each test result maps to the program that produced it.*

## 5. C2O7 was the submission selected by the final leaderboard

We kept two submissions for the final evaluation: C2O7 and a later experimental branch. C2O7 combined the established native planner with the OV7 v90 opening, while the other package carried further changes from the final development period.

<!-- paragraph -->

CAND2 and C2O7 used the same native planner and configuration. The change between them was the opening checkpoint, from OV2 v293 to OV7 v90. We first submitted C2O7 as **56687882**, then submitted it again as **56720575** in the final pair. The other slot, **56720565**, contained **cx_blr_o7_r20** with later changes. The final leaderboard identifies the re-submitted C2O7 as our highest-scoring agent.

[![The upper lane follows the re-submitted C2O7, whose result appears on the final leaderboard. The lower lane follows the later experimental agent into the other final slot. Code, opening weights and configuration together identify each agent.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2Fb39f79a84739ed778182d613361dd47b%2F16_version_and_evidence.png?generation=1792201443308704&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2Fb39f79a84739ed778182d613361dd47b%2F16_version_and_evidence.png?generation=1792201443308704&alt=media)

**Illustration 16 · The two final submissions** *The upper lane follows the re-submitted C2O7, whose result appears on the final leaderboard. The lower lane follows the later experimental agent into the other final slot. Code, opening weights and configuration together identify each agent.*

<!-- paragraph -->

The earlier agent that we retained produced our best final result. Several changes from the last night improved their target measurements without replacing it as the stronger submission. Those experiments were still informative: they showed how better prediction could stop short of different decisions, and how different decisions could stop short of a larger advantage. Keeping C2O7 in the final pair let both versions compete in the final evaluation.

## 6. Make the chosen investment survive through execution

Our clearest direction for improvement is to keep more of the proposed investment together throughout planning. Buying land has value only with a continuation: which tiles will be used, what must be bought, who will do the first useful work, and which later receipts will repay the expense. A promising continuation can lose that value if a later stage changes the work or sale schedule on which it depended.

<!-- paragraph -->

The fourth-quadrant purchase logic operates within a **day 10–12** window. Our CAND2 game against DECEM drew attention to what must happen within that window: once cash becomes available, the new land needs a useful production plan and workers who can carry it out.

<!-- paragraph -->

The land-purchase logic shows a concrete place to improve this consistency. It first creates a trial farm with the new quadrant and optimizes projects on the new tiles. For the purchase decision, it then creates **two additional copies**: one without the purchase and one with it. Both copies are reoptimized across **all tiles**, using the same post-purchase sweep budget. The estimated gain is the value of the reoptimized farm with land, minus the reoptimized farm without it, minus the purchase price. Thus both sides of the comparison can rearrange existing production.

<!-- paragraph -->

The comparison copies are used to make the purchase decision. When the dawn path adopts the purchase directly, it installs the earlier trial that initially optimized only the new tiles, then runs the usual subsequent optimization across the farm. The implementation therefore distinguishes the plan used to justify buying from the plan that starts the next optimization. Preserving a profitable continuation more directly through that transition is a useful development target, along with keeping its cash commitments and worker routes consistent.

<!-- paragraph -->

Land can also be bought during the day. A qualifying dawn verdict can enable an intraday capital proposal once cash is available. That proposal can generate new economic projects with the crop dynamic program, simulate the purchase and evaluate the work that follows. A separate purchase-only branch can acquire land for the next morning when the search finds no worthwhile plan for using it today. This gives the agent several ways to expand, with different timing and funding conditions. Keeping these paths consistent would let the agent compare the timing and financing of expansion more directly.

<!-- paragraph -->

Candidate generation is another place where a specific change may matter more than a better forecast. The main configuration filters out **new strawberry-planting candidates after day 15**, while leaving existing strawberries in place. A forecast cannot favor a planting that never reaches the evaluator. We would revisit such filters together with maturity dates, remaining harvests, labor and terminal sale opportunities, so the planner can compare complete late-season uses of a tile.

<!-- paragraph -->

The daily and hourly calculations should also agree more closely about how output becomes income. A daily production project can look attractive under one assumed sale schedule while its actual route requires another. More workers help only when they can reach useful jobs and deliver goods in time. Improving that connection means comparing project choices using the routes and sale opportunities the farm can actually execute, then retaining the chosen continuation as later decisions revise it.

<!-- paragraph -->

The experiments suggest different tests for each improvement. For a new opponent model, examine whether it changes the selected feasible plan and whether that change helps. For extra work or a different crew, measure the final margin as well as completed jobs and win count. For a refreshed resource, verify that the active decision path uses it. W17, the late-hours package and the unused codebook produced different outcomes at these stages, pointing to different changes in the system.

<!-- paragraph -->

The strongest opponents made these dependencies visible in ordinary actions. Majkel delivered and sold wool before expanding. M&M used an ordered sale and purchase sequence to turn milk into a sheep and land within one hour. DSM funded immediate obligations while holding other goods for later. Our agent combined learned opening decisions with explicit planning to manage the same kinds of commitments. Our next priority is to carry a valuable sequence of work, purchases and sales all the way from proposal to execution.

## Acknowledgments

We thank Kaggle and the environment authors for a game with rules we could study precisely. We also thank the participating teams whose public replays let us inspect complete decisions and their consequences. Their games provided alternative ways to run a farm, difficult opponents, and counterexamples that forced us to revise our own explanations.

## Appendix. End-of-game timing and additional results

### The last action occurs at day 29, hour 22

The default configuration records **720 frames** for the nominal 30-day season, beginning with initialization. The action at **step 718, day 29 hour 22**, produces **terminal frame 719**. Play ends there, before hour 23 and the usual nighttime deposit. Terminal reward is cash, so the final useful routes must deliver and sell their output by this boundary. [Interpreter termination](https://github.com/Kaggle/kaggle-environments/blob/28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c/kaggle_environments/envs/kaggriculture/kaggriculture.py#L935-L963)

### Fourteen complete comparisons from the late-stage screen

The plot below brings together **fourteen complete, nonduplicate candidate comparisons** from the late-stage screen, including negative results and the two largest positive means. Each arm contains all 320 paired cells, with error bars of ±1 episode-cluster standard error. This exploratory set compares several packages; our selection rule also used win-rate change and behavior across opponent classes. Some refreshed models used fitting data that overlapped the screen, so we used the screen for candidate selection before further game tests.

[![Fourteen complete exploratory arms from the late-night screen show positive and negative paired margin changes against c2ov225.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F394e388b29bbf709d021e4dbdc70ed19%2FE_full_screen.png?generation=1792201452469101&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F394e388b29bbf709d021e4dbdc70ed19%2FE_full_screen.png?generation=1792201452469101&alt=media)

*Data figure E. Fourteen complete exploratory arms against c2ov225, each with 320 paired cells from 261 episodes and 19 opponent teams. Bars show ±1 episode-cluster SE in game-score units. Control begins at step 240, with fixed rival tape and time bank and ordinary time cutoffs disabled. Model fitting and this candidate-selection screen share some data.*

### The farm boards behind the cash comparison

[![CAND2 and DECEM's public farm boards at day 16, with actual crop and animal categories and the locked southeast quadrant.](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F1cc6e251d13a2bcded1567c22ef9366f%2FF_farm_state.png?generation=1792201463523438&alt=media)](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F36551765%2F1cc6e251d13a2bcded1567c22ef9366f%2FF_farm_state.png?generation=1792201463523438&alt=media)

*Data figure F. The public farm boards at day 16, hour 0, in episode 115509423. Colors identify crop and animal categories, and the locked southeast quadrant is marked explicitly. These are the two farms behind the nearly equal cash balances in Data figure A.*

## References

1. Kaggle. (n.d.). *Kaggriculture: Environment documentation*. Kaggle Environments, revision `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`. [Official documentation](https://github.com/Kaggle/kaggle-environments/blob/28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c/kaggle_environments/envs/kaggriculture/README.md). Accessed October 16, 2026.

2. Kaggle. (n.d.). *Kaggriculture: Interpreter source*. Kaggle Environments, revision `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`. [Source code](https://github.com/Kaggle/kaggle-environments/blob/28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c/kaggle_environments/envs/kaggriculture/kaggriculture.py). Accessed October 16, 2026.

3. Kaggle. (2026). *Kaggriculture: Final leaderboard*. [Official standings](https://www.kaggle.com/competitions/kaggriculture/leaderboard). Accessed October 16, 2026.

4. Ross, S., Gordon, G. J., & Bagnell, J. A. (2011). A reduction of imitation learning and structured prediction to no-regret online learning. In *Proceedings of the Fourteenth International Conference on Artificial Intelligence and Statistics*, *Proceedings of Machine Learning Research*, 15, 627–635. [Proceedings paper](https://proceedings.mlr.press/v15/ross11a.html).

5. Schulman, J., Wolski, F., Dhariwal, P., Radford, A., & Klimov, O. (2017). *Proximal policy optimization algorithms*. arXiv:1707.06347. [doi:10.48550/arXiv.1707.06347](https://doi.org/10.48550/arXiv.1707.06347).

6. Mayne, D. Q., Rawlings, J. B., Rao, C. V., & Scokaert, P. O. M. (2000). Constrained model predictive control: Stability and optimality. *Automatica*, 36(6), 789–814. [doi:10.1016/S0005-1098(99)00214-9](<https://doi.org/10.1016/S0005-1098(99)00214-9>).

7. Gneiting, T., & Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, 102(477), 359–378. [doi:10.1198/016214506000001437](https://doi.org/10.1198/016214506000001437).

8. Alibaba Cloud. (n.d.). *PPU-SMI device management tool (v1.6)*. ZHENWU PPU Cloud Service documentation. [Official documentation](https://help.aliyun.com/en/document_detail/2971881.html). Accessed October 16, 2026.

9. T-Head. (n.d.). *vLLM SAIL: Supported features*. Revision `cc1b67eaa1bee9a7f375baaef16dff4015650fd1`. [Official documentation](https://github.com/t-head/vllm-sail/blob/cc1b67eaa1bee9a7f375baaef16dff4015650fd1/docs/user_guide/supported_features.md). Accessed October 16, 2026.