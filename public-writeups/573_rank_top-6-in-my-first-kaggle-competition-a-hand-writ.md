> **来源 / Source**：Kaggle Kaggriculture 公开 write-up，第 573 名，队伍 **Tim McGarvey**。
> **原文**：https://www.kaggle.com/competitions/kaggriculture/writeups/top-6-in-my-first-kaggle-competition-a-hand-writ
> 本文为比赛归档的离线副本，仅作技术参考；**版权归原作者所有**。
> 如作者要求撤下，请联系仓库所有者。

# Top 6% in my first Kaggle competition: a hand-written planner with lookups 

**Final result: 573rd of 10,148 (top 5.6%), a bronze-range finish.** On the live ladder it ended 481st, inside silver; the final Bradley-Terry ranking over all two weeks of post-deadline games placed it 573rd. No trained model: the agent is a hand-written planner. I built it over eight weeks and it took five separate attempts to get there. This is the story of those attempts, how the final agent plays, and the things I'd do differently.

Thanks to the organizers for a wonderful game, and to everyone whose replays, notebooks and write-ups taught me something. Credits are at the end.

## Five attempts in eight weeks

I treated this as a learning project.  Along the way, I ran into brick walls and had to restart from scratch four times.  Each time, though, I solved new problems and for the most part the agent improved, in some areas if not in others.  By the final submission deadline I had an agent I was pretty happy with, although it wound up just shy of the silver medal I had been hoping for.  

| Attempt                                                               | Dates           | Best rating                     |
| --------------------------------------------------------------------- | --------------- | ------------------------------- |
| 1. A planner tuned by an evolution strategy using CMA-ES              | Aug 4 – Aug 21  | 879                             |
| 2. Attempting to remove the genome from the original code base        | Aug 21 – Sep 1  | 1,050                           |
| 3. Imitation Learning, an preliminary first attempt                   | Aug 27 – Aug 29 | 850                             |
| 4. A fresh start: rollout search over the season                      | Sep 1 – Sep 22  | 1,354                           |
| 5. Another fresh start: copy the best players boards with my executor | Sep 22 – Sep 30 | **2,109** (final ladder rating) |

Ratings from different weeks aren't really comparable, because the field kept getting stronger. Rank tells the story better: top 57% in mid-August, top 31% in mid-September, top 5.6% at the end.

All of my attempts separated the agent into a planner and an executor.  The planner made decisions, the executor ran the farm, hired workers, assigned them tasks, planned routes, and controlled sales.  

**Attempt 1** started with my idea of tuning a planner's weights by an evolution strategy.  Using a "genome" of about 30 elements, the idea was to tune that genome through CMA-ES. The executor improved quickly through ordinary design work. CMA-ES never helped: it tuned the wrong things, mutated the elements of the genome too slowly, and wasn't improving on the ladder. I tried to proceed by freezing the genome and working around it, but that was too limiting.  When I first attempted to remove the genome, the agent collapsed. The genome had been masking deep-seated issues in the executor.  The best rating during this period was 879.

**Attempt 2** was an trying to retain the existing code, remove the genome, and fix the underlying issues.  This worked for a while, but ultimately the design was not what I would build from scratch.  Final rating was 1,050.

For **Attempt 3** I trained a model to imitate the top of field's shared opening. It reached 99.5% accuracy on that opening, but the opening left the ladder within days, and its advice was neutral in live play.  I abandoned this attempt, perhaps too early, thinking I lacked the hardware to implement something like PPO on top of the imitation learning I was doing.  

**Attempt 4** started from scratch on 1 September. I built a new planner and a new executor.  This time the planner would use full rollout search over the rest of the season over a number of different simulated towns to see which candidate plans did best on average.  Each morning it ran its rollouts and recommended new actions.  The executor would take those plans and implement them.  It passed attempt 2 within four days, peaked around 1,370 a week later, and then stalled for a week. This approach had two significant limitations.  The first was compute: in python, the planner was slow.  It was trying to choose between 8 or so candidate plans by simulating full seasons and opponent reactions across multiple different towns.  It made better choices with more compute available, but at kaggle speeds with the 1s per turn / 60 s time bank, it was limited in how many plans and rollouts it could handle.  

The second limitation was related to compute: its vocabulary was limited.  It could not fully express all the different plans that might be possible, and so had to use generalizations.  It would leave a few tiles empty here or there because it had calculated, (e.g.) that 12 strawberry plants in the NE quadrant were a good idea, but didn't have the vocabulary to express that the remaining three tiles should be wheat.  Evaluating more candidate plans solved the limitation, but vastly exceeded the compute budget.  I tried to patch over these planning deficiencies with different heuristics in the executor (if a tile isn't specified by the planner, plant wheat, if no new decision is made, harvest and replant same crop, etc.) but this was eventually too cumbersome to work with.  So many different rules were injected into different pieces of the executor that were really planning rules, I decided to scrap it all and start over again.

**Attempt 5** started from scratch on 22 September with eight days left, and became the final agent.

## How the final agent plays

For the final attempt I wanted a fixed opening, and then instead of a rollout planner use the crop / animal choices from a top competitor, run through my own executor.  

**Days 0-6: someone else's opening.** Vadim Vasilenko played nearly the same opening in all 152 of his games I downloaded. I turned those games into a lookup table: in any situation Vadim reached, do what he did. That means a few melons, early cows and sheep, more animals over days 2-5, and spending down to almost nothing by day 6. If the game drifts somewhere Vadim never went, the planner takes over.

An early version replayed one of DSM's games move for move. It broke whenever my cash differed from his by even a few coins, which happened whenever the opponent bought wheat in the same turn. The table fixed that, because Vadim's own play already adapted to what he had.

**The melon race.** If the opponent planted ten or more melons on day 0, it fertilizes its own day-0 melons so they're ripe at dawn on day 10. Then it harvests and sells them before the opponent's melons crash the price.  If the opponent wasn't that heavy into melons, it could wait a few turns before getting its own to market.  

**Days 6-12: building the farm.** It buys a second quadrant on day 6 and a third on day 9, and never a fourth. Each quadrant is steered toward the farm Vadim had built by days 9 and 13 in towns with the same shops. The opening and those targets only worked together. Vadim's opening with someone else's build targets lost, and so did the reverse. Together they were worth about 5,900 coins a game in head-to-head tests, the largest single gain of the project.

**Days 13-28: the working farm.** Crop counts per quadrant follow what DSM grew in towns with similar shops. On top of that:
- Fertilized wheat is harvested at its best yield per day, not its maximum.
- Spent strawberries and tomatoes are dug up and replanted in the same visit.
- Six sheep are added for each yarn store that opens late.
- It hires 11 hands, and 12 from day 22. The twelfth hand costs about what it earns, but its output lowers the opponent's prices.
- From day 27 it feeds animals only when their remaining output pays for the feed.

**Every morning: routes.** It plans a route for every hand, sweeping jobs by direction around the shed and filling them in by value per turn. From day 13 it spends about a second shortening those routes. During the day, an idle hand takes over any job it can reach before the hand assigned to it.

**Day 29: planned exactly.** The last day has no future to worry about, so it's fully deterministic. The agent plans the whole crew's last day on the game's exact rules, with a search using about half its remaining time bank. It hires the last two hands only if the plan says they pay. A separate test showed every crop on a typical last-day board can be harvested and sold with about an hour to spare. My earlier agents were leaving 5-20 units in the field.

## Labor and routing: five attempts at the same problem

The hardest problem in this game isn't what to plant. It's getting a dozen workers through a few hundred jobs a day when each one does one action per turn, walks one tile per turn, and has to fetch feed and drop produce at a four-tile shed. Every attempt attacked it differently.

**Attempt 1: from auctions to owned days.** The first version re-scored every job every turn and gave each worker the best one, a fresh auction each turn. Workers abandoned errands halfway when something shinier appeared, and five different bugs turned out to be one disease: no decision could see what the others had already claimed. The fix was giving each worker its jobs for the whole day. Animal escapes went from about 2 a game to zero. A second rework sized the crew by costing the actual day plan, built routes by cheapest insertion, and executed them in deadline order. A hard-coded 15% "route slack" constant was quietly standing in for execution friction I hadn't yet measured, and the genome tuned around it.

**Attempt 2: every delivery as a chain with a deadline.** This design treated each product as a chain: produce, carry, return, drop, sell. A chain counts only if every step fits before its deadline. Animal care became atomic visit bundles; later, every published route task became a hard promise, with every planned task required to be executed. The approach was principled but heavy. Its last build inserted jobs into routes with a quadratic search, 97.6 million calls in one dawn, and ran out of Kaggle's time bank in 12 of 32 games. After that, every remaining step was a forced pass.

**Attempt 4: an exact executor inside every simulation.** Here the executor compiled the day's commitments into routes and dry-ran them under the engine's exact rules. Anything that wouldn't complete was dropped by value until every route finished, and crew size was found by binary search. Routing was crew-aware Clarke-Wright savings plus 2-opt. It was genuinely efficient: 0.82-0.94 moves per useful action, about what the top agents managed. But the planner scored candidate plans by simulating the rest of the season, and every simulation ran this executor. Compiling routes was about 77% of a simulation's cost. Any change that made the farm do more work per day made the simulations slower, so fewer fit in Kaggle's budget. This executor ran well when the planner was leaving empty tiles dotted around the farm, but patching that defect exposed the weakness of the labor routing.  It could handle 60ish occupied tiles well, but a full 75 and it broke down and important jobs started getting missed.  

**Attempt 5: one dawn plan, then cheap repairs.** The final agent plans once a day and keeps the planning out of any simulation:
- **Petal routes.** At hour 1, when the hired hands arrive, it sweeps the day's must-do tiles by angle around the shed and cuts the sweep into one "petal" per worker, sized to that worker's turns. It tries 12 starting angles and keeps the best, then orders each petal by nearest neighbour and 2-opt.
- **Prize-collecting.** Every visit and every drop carries a value in coins. Optional jobs go into a route only if they earn enough per extra turn.
- **Exact supplies.** Feed wheat is allocated route by route, so a worker never arrives at an animal without it. Fertilizer is collected from the animals on the way instead of fetched from the shed, which cut shed trips from 18 a day to 15 and was worth about 1,400 coins a game.
- **Repairs during the day.** A worker with nothing left takes over a job it can reach before the worker assigned to it.

The efficiency metrics I used throughout came from observing and measuring DSM's farm from replays. Late in the game his hands made about 148 productive actions a day to my 134-137. Most of the gap was shed trips: he made about 6 a day, I made about 13. His animals sat beside his wheat, so his hands fed what they just harvested. I closed part of that by copying his layout, never all of it.
## Spending the time bank: what got us into the top 6%

Kaggle gives each agent 1 second per turn plus a 60-second bank for the whole game. The early attempts learned to fear the bank: Attempt 2 lost a build to running it dry, and Attempt 4's season simulations never fit. By the last week my agent was using almost none of it: mostly under 0.1 seconds a turn, plus about 4 seconds to load its data tables. Two late changes spent it, and both landed in the final pair.

**1. The last day, planned exactly ** I asked a simple question while watching replays: is it even possible to harvest and sell everything on the last day? I wrote a solver, separate from the agent, that searches the whole crew's last-day plans on the engine's exact rules. Its moves are insertion, relocation, 2-opt, swaps, toggling water-before-harvest, and inserting drops. It runs simulated annealing with restarts. The answer: yes, with about an hour to spare, and 9-11 workers are enough on most boards. My agent's heuristic last day was leaving 5-20 units in the field.

On the last day nothing can surprise you. No weeds appear during the day, crops decay by a fixed rule, and the opponent can't touch your farm. So the plan can be computed and then executed action by action. The agent does exactly that:
- At hour 0 it hires 10 workers and searches with **half the remaining bank**.
- At hour 1 it decides whether the 11th and 12th workers pay for themselves, and searches again with **half of what's left**.
- Every later turn it warm-starts the search from the current plan for 0.25 seconds, so any drift gets repaired.
- Each turn's drops must fit the 100-unit shed, because overflow is destroyed.

On Kaggle that is about 25 seconds at hour 0 and 13 at hour 1. Gains measured over 57 recorded last days, against the old heuristic:

| search time (desktop)              | coins gained on the last day |
| ---------------------------------- | ---------------------------- |
| 0.25 s                             | +275                         |
| 1 s                                | +307                         |
| 2 s                                | +381                         |
| 5 s                                | +434                         |
| 12.7 s (≈ half the bank on Kaggle) | +482                         |

Two-thirds of the gain arrives in the first second or two. One coherent plan for the whole crew is worth more than search time. In one replayed game, last-day harvest went from 103 units to 121. Combined with harvesting melons the day they reach full size, this build beat its predecessor by about 1,250 coins a game.

**2. A shorter route every morning (the last change)** With the last day budgeted, there was still bank to spare from day 13 on. The last build spends about 1.3 seconds on Kaggle each morning improving the dawn plan by large-neighborhood search. It removes a cluster of 2-6 nearby jobs from the routes and reinserts them, plus any dropped jobs nearby, at their cheapest positions. It keeps the change only if the routes come out better: more value covered, or the same value in fewer turns.

I had tried exactly this three days earlier and rejected it: shorter routes, no more coins. What changed was everything around it. By the 30th, idle workers took over jobs they could reach first, so the turns the search freed became real work instead of idle time. It was also kept out of the building phase (days 6-12), where it had cost money. Result: about +700 coins a game against o-v18 in head-to-head play, and +800 on replays against recorded field opponents.

**Which one mattered?** Both agents played the whole post-deadline tournament side by side, and they share the exact last day. The only difference is the morning route search.

|                                          | final rating | vs 1,700-1,900 opponents | vs 2,100+ opponents |
| ---------------------------------------- | ------------ | ------------------------ | ------------------- |
| Exact last day                           | 1,844        | 53%, +672 a game         | never met one       |
| Exact last day plus morning route search | **2,104**    | 56%, +1,555 a game       | 44% over 158 games  |

Both played about 900 games across the full 14 days, side by side against the same field, so this isn't the early-tournament noise that can separate identical uploads. And against the same band of opponents,  average margin was more than double with morning route search turned on. My read is that the exact last day made the agent solid, and the morning route search made it good enough to hold its own against the 2,000+ field. Both came from noticing that the time bank was sitting unused.

## What I learned about measuring

Most of my time went into this, and it's where I'd start next time.

- **Self-play flatters you.** One build beat its predecessor by 1,300-1,800 coins a game in head-to-head play and was level on the ladder. Both versions farmed the same way, so the test couldn't see what the field would do to it.
- **Replay real games instead.** The test I came to trust restores a recorded ladder game, lets my agent take one seat, and replays the real opponent's moves. Only builds that won both head-to-head (on two separate sets of seeds) and on those replays shipped.
- **Hold the town fixed.** The engine draws one random number per empty tile each night before picking the next shop. So two agents that play differently on the same seed get different towns. My replay test drew new towns for days before I caught it; fixing it cut the noise about five-fold.
- **Judge on margin, not your own coins.** You sell into the same market as your opponent. Several changes raised my coins and lost games, like releasing animals once milk got cheap: the opponent's milk then sold higher. Others cost me coins and won, like the twelfth hand.
- **Watching replays found most of my late gains.** Empty pastures nobody replanted, crops stranded on the last day, a yarn store that opened after the farm was built, and melons left until evening while the opponent sold at hour 7. Each was a concrete defect with a measurable fix.

## What I missed

- **The public notebooks.** I never even clicked on the Code tab until after the deadline. Public agents that finished rated above 2,500 had been up since mid-September, along with careful lab notebooks like Rayk Kretzschmar's. I wouldn't have wanted to fork one: a recorded-script agent built from about 280 numbered patches isn't the kind of building I enjoyed, and I wouldn't have learned the things I did from this competition. But studying them would have shown me where the bar was, and given me strong opponents to test against instead of my own old builds.
- **The fourth quadrant.** On 26 September I watched DSM's best agent run four quadrants, then saw his next two submissions go back to three. I concluded it wasn't worth it. The top agents used it in the end, in the games where it paid: early, for late tomatoes and wool. On a ladder where only your two newest submissions play, a rival's visible behaviour is a signal they control.
- **The opening trick that was being used on me.** On turn 0, buying wheat and selling it straight back raises the price of the opponent's first wheat purchase. Against an opening funded to the coin, that costs a seed. My first opening book kept breaking for "just a few coins" on day 0, and I treated it as bad luck.
- **Trained imitation.** My attempt 3 imitated only the opening, and the opening went stale. The top teams cloned the whole policy from replays of the best players and kept retargeting the newest versions, and at least two reached the top 10 training on a single desktop GPU. I spent many, many hours on labor routing and efficiency in particular, and some of the top teams completely sidestepped that issue with a trained model that learned to be more efficient than my agent was without needing to understand why.

## Credits

- **Vadim Vasilenko** and **DSM**, whose replays my opening, build targets, layout and late-game crop counts were taken from. I extracted all of it from public replays, not from their code.
- **HowardLeeTW**, whose opening I studied and tested early on.
- The posts and notebooks that taught me the most after the fact: Rayk Kretzschmar's "Findings from Zero to Top Meta", Pilkwang Kim's "Structured Economic Policy", Yujin Cha's "Six things I wish I'd known before trusting my local win rates", Kirderf's leaderboard tracker, dzjiann's RL write-up, sdy623's "Beyond 48-0", and Chris Deotte's write-up and the comments under it.

Happy to answer questions about any of it.