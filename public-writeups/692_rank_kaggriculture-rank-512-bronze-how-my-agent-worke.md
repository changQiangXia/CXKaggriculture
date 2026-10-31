# From 400 Score to Top 13: Kaggriculture Bronze Medal Solution

![Kaggriculture Rank 512 Bronze](https://raw.githubusercontent.com/sarthak-here/kaggriculture/master/docs/images/rank512-bronze-banner.svg)

I finished Kaggriculture at **rank 512 and earned a Bronze Medal**.

The final rank tells only part of the story. My earliest agents were near a rating of 400 and could barely operate a complete farm. After many iterations, replay investigations and local tournaments, one of my agents climbed into the **top 13** during the competition.

![Kaggriculture leaderboard showing rank 13](https://raw.githubusercontent.com/sarthak-here/kaggriculture/master/docs/images/top13-leaderboard.png)

*Figure 1. The agent reached rank 13 during the competition with a rating of 2810.0.*

I could not preserve that position until the final evaluation, but progressing from an almost non-functional farmer to competing near the top was the most rewarding part of the competition.

My final submitted policy, **Severe route current-rule cleanup**, received a final rating of **2089.3**.

## Understanding the game

Kaggriculture is a two-player farming simulation played over 30 days, with 24 turns per day. Each player must coordinate an entire production system: purchase seeds, animals and land; hire workers; plant and water crops; feed and care for animals; harvest products; transport everything back to the shed; and sell products before market demand disappears.

The player with the most money at the end wins. Produce left on the farm or inside the shed has no terminal value.

The most important complication is that both players use the same market. If both farms produce the same product, they compete for a limited amount of demand and push its price down. This meant that simply producing more was not enough. The agent had to produce the right items, deliver them on time and sell them before the opponent captured the available demand.

## Why I used a route-based policy

I initially explored learned policies, including behaviour cloning from strong public matches. The offline model reached high action-prediction accuracy, but it performed poorly in complete games. A few incorrect movement or economic decisions moved the farm into states that were not represented in the training data. The errors then accumulated over hundreds of turns.

I therefore focused on a deterministic route-based policy. A route provided a coordinated long-term schedule for:

- Farm expansion
- Crop placement
- Animal purchases
- Worker movement
- Watering and harvesting
- Feeding and animal care
- Product transportation
- Market activity

This approach was easier to inspect and evaluate. When a match was lost, I could trace the first important difference and determine whether the cause was financing, production, labour, transportation or selling.

## Learning from games

I downloaded competition replays and converted match information into structured data that could be compared across agents.

For every important loss, I examined:

- The sequence of unlocked shops
- Purchases made by both players
- Farm composition and worker count
- Planted and harvested crops
- Animal feed consumption
- Shed inventory and carried products
- Market orders and sale timing
- Money over time
- Unsold production at the end

The useful question was not simply, “Why did the opponent earn more?” I looked for the first decision that created the eventual gap. Lower revenue could come from producing too little, but it could also be caused by an early cash shortage, a missed worker hire, late harvesting, slow transportation or selling after the opponent.

![How the Kaggriculture agent worked](https://raw.githubusercontent.com/sarthak-here/kaggriculture/master/docs/images/agent-flow.svg)

*Figure 2. The final policy combined a planned farming route with reactive economic and execution controls.*

## Shop-conditioned strategies

The town’s unlocked shops determined which products would receive demand. Shops could also appear more than once, making every world economically different.

My agents therefore used different farming routes depending on the visible shop sequence.

| Visible condition | Strategic effect |
|---|---|
| YARN store | Increased the potential value of wool and sheep-heavy routes |
| Bakery-related shops | Changed the value of wheat, feed and animal products |
| Milk-supporting shops | Made cattle-heavy farms more attractive |
| Duplicate shops | Concentrated demand and changed the best product mix |
| Weak demand worlds | Favoured a leaner farm that protected cash |

This was a major improvement over using one fixed plan in every match. The agent selected a route early in the game and then used reactive controllers to handle market conditions, capital constraints and unexpected execution states.

## The final farming strategy

The final Severe route was reconstructed from one of the strongest farm structures found during loss analysis. Unlike a small market-order patch, it changed the complete production architecture.

Its typical terminal structure was:

- Three active quadrants
- Approximately eight cows
- Four geese
- Around ten workers
- No sheep retained in the final farm
- A fixed 54-carrot planting programme
- Approximately 173 carrots sold per game

This was a relatively lean farm compared with several labour-heavy opponents.

The goal was not to maximize every type of production. It was to create a farm whose land, workers, feed requirements and market supply remained balanced. Earlier agents often created larger mixed farms that looked productive but consumed too much feed and labour. The Severe route reduced that burden while preserving cattle, fertilizer and high-value crop production.

## Protecting operating capital

Several losses began with decisions that appeared small. Buying a few extra seeds could leave the farm without enough money to hire workers the next morning. Missing those workers then caused crops to go unwatered, animals to go unfed and harvests to arrive late.

The controller therefore protected money required for upcoming commitments:

- Worker hiring
- Seeds
- Animals
- Feed
- Land expansion
- Route-specific purchases

A purchase was not considered profitable merely because the crop or animal could eventually generate revenue. It also had to leave enough working capital for the rest of the farm to continue operating.

## Making the route executable

A long-term schedule works only if workers can execute it. The controller had to coordinate workers with different positions, inventories and deadlines.

The route handled planting, watering, feeding, caring, harvesting and carrying products back to the shed as one connected process. A profitable crop had no value if it was harvested too late, left in a worker’s inventory or never sold.

Late in the match, the policy stopped treating every possible farm action as useful. New investments, fertilizer, care and harvesting had to contribute to a sale before the final market window.

## Reactive market control

The market controller adjusted selling decisions using:

- Current inventory
- Available town demand
- Expected price impact
- Remaining production time
- Product priority
- Opponent behaviour
- The stage of the game

Orders were prioritized by their expected impact rather than only their nominal revenue. This mattered because both players submitted market orders during the same phase. Selling a product one turn earlier could capture demand before the opponent filled the market.

Against opponents with very similar behaviour, the agent could detect repeated action patterns and alter selected sale timing to avoid losing identical market races.

## YARN and bakery handling

YARN openings were among the most difficult match families. Some strong opponents used labour-heavy sheep farms with 11 or more sheep and as many as 13 workers. My Severe route generally remained closer to a lean cattle-and-geese structure with around ten workers.

I tested several possible repairs:

- Converting cows into sheep
- Changing wool-sale timing
- Increasing animal feed
- Adding terminal harvesting
- Replacing the complete route
- Detecting late YARN openings

Some changes improved the final cash margin but still failed to change the winner. This was an important distinction: explaining a loss did not mean that the proposed patch was better.

Bakery worlds required similar care. Wheat could be sold, used as animal feed or sacrificed for another crop. The agent used dedicated capital and route conditions to avoid expanding into a bakery strategy that it could not afford to execute.

## Execution safety

A strong strategy was useless if the submitted Python file failed during a match. The final agent included execution guards that:

- Removed empty market orders
- Removed invalid market PASS entries
- Rejected malformed quantities
- Removed non-positive orders
- Limited the market queue to ten entries
- Returned a safe fallback action if the main controller failed

The final artifact completed full 720-step validation under the current game rules with no hard action errors.

## Testing improvements

Every serious candidate was tested in both seat orders across fresh seeds. Seat pairing was necessary because the two players started in different positions. Even identical agents could behave differently depending on their seat.

I also tested against multiple opponent families. Beating one previous model was not enough because many strategies had highly favourable but narrow matchups.

The Severe route’s main validation result was:

| Evaluation | Result |
|---|---:|
| Ten strong opponent families | 136 wins, 64 losses |
| Overall win rate | 68% |
| Failed games | 0 |
| Diagnostic top-player replay panel | 27 wins, 3 losses |

The 27–3 replay result was useful for diagnosing coverage, but it was not treated as proof of a 90% live win rate because recorded opponents could not react to changes in the market.

In a separate six-agent current-rule round robin, Severe recorded **38 wins and 12 losses**. It defeated the historical pf_all agent in all ten games and beat the strongest broad internal agent 6–4 in their direct matchup.

These tests supported submission, but they did not guarantee leaderboard performance.

## What failed and what I learned

A large part of the project consisted of rejecting ideas that sounded reasonable.

Failed or inconsistent approaches included:

- Training a behaviour-cloning policy only from replay actions
- Buying additional land without a compatible worker schedule
- Increasing the number of workers globally
- Producing more crops without considering shared demand
- Generic weed-clearing overrides
- Unconditional feed top-ups
- Terminal harvesting changes that disrupted other work
- Selecting routes using replay reward alone
- Majority-voting actions from several strong routes
- Promoting a candidate because it improved one diagnostic metric
- Overfitting to a single opponent family

One particularly important lesson came from a lower-feed route. It appeared to fix the problem I had diagnosed, but direct testing showed that it lost badly to the route it was intended to replace.

After that, every replacement had to be tested directly against the incumbent. Fixing the suspected cause of a loss was not sufficient evidence.

Another lesson was that cash margin and match wins were not interchangeable. A candidate could earn a larger average margin while failing to improve the number of games won. I therefore promoted agents by paired-seat win rate, using margin only to understand the mechanism.

## From 400 to the top 13

The earliest agents were close to a 400 rating and often failed for basic reasons: broken submission entry points, invalid market actions, poor planting, missed hiring and incomplete harvesting.

The next stage produced functional farms but still lost because they followed one fixed plan in every world.

Route portfolios, shop-conditioned strategies and better market handling produced the largest improvement. One of these agents climbed into the top 13 during the competition.

However, the leaderboard continued to evolve. Some locally dominant agents had narrow matchup advantages, and several strong changes did not generalize to new opponent families.

I eventually finished at rank 512 with a Bronze Medal. Falling from a temporary top-13 position was disappointing, but it also made the final result more meaningful. The project was not a smooth climb. It was a long sequence of improvements, regressions, failed submissions, corrected evaluations and rebuilt agents.

## Final lessons

The most valuable lessons were not individual farming tricks. They were about experimental discipline:

- Test both seat orders.
- Use fresh seeds for confirmation.
- Evaluate against several independent opponent families.
- Treat replays as diagnostic evidence, not live-match proof.
- Measure wins and losses, not only cash margin.
- Verify that a mechanism actually activates.
- Test a replacement directly against the component it replaces.
- Keep exact source files and hashes for serious submissions.
- Never assume that more production creates more profit in a shared market.

Kaggriculture became much more than a leaderboard attempt. It was an exercise in simulation, economic modelling, adversarial decision-making, software reliability and learning from failure.

I started with an agent around 400 rating, briefly reached the top 13 and finished with a Bronze Medal at rank 512. It was a difficult competition, but I genuinely enjoyed the process.

## Code

The exact final main.py and the complete experiment history are available here:

- [Final Kaggriculture agent](https://www.kaggle.com/datasets/sarthaksharma14/kaggriculture-rank-512-bronze-agent)
- [GitHub repository](https://github.com/sarthak-here/kaggriculture)

**Final result: Rank 512 — Bronze Medal**