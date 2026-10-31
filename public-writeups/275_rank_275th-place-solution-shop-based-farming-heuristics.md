# 275th Place Solution | Shop-Based Farming Heuristics

I finished Kaggriculture in **202nd place**, with a final score of **2345.5**. My solution was a heuristic agent that selected production schedules from public replays according to the town's early shops.

## Core Strategy

I treated the game as a choice between coordinated farm plans, rather than a collection of independent purchases.

Increasing the herd is only useful when the farm can support it. Animal purchases, feed production, worker assignments, harvesting, deliveries, and sales all need to stay aligned. A more ambitious production plan can underperform if it runs short of feed, working capital, or labor.

To preserve those dependencies, I extracted complete turn-indexed action sequences from public replays. Candidate continuations were compared by score margin within early-shop categories, then checked on a separate replay set. The result was a small portfolio of general, milk-oriented, and wool-oriented schedules.

## Let the Town Guide Specialization

The first two shops become visible at steps **72 and 144**. These provided an early signal about which production chains the town would support.

The higher-scoring final variant used three branches:

- **Milk-oriented:** activate when both early shops consume milk, with Pizza, Ice Cream, and Smoothie qualifying. Requiring two qualifying shops made milk specialization depend on a stronger demand signal than a single shop.
- **Wool-oriented:** activate when a Yarn Store appears among the first two shops. This branch could begin after the first reveal, allowing an earlier shift toward wool production.
- **General mixed farm:** remain on the general schedule when neither condition applies, rather than forcing specialization without the corresponding early demand.

The important distinction was that a branch changed the production schedule, not just the number of animals purchased. More sheep, for example, also require a compatible feeding, collection, and selling plan.

Switching continued at the current turn index. However, the schedules came from different openings, and the agent did not fully reconcile its current farm with the new schedule's expected state. That remained a weakness of the approach.

## Protect the Next Production Cycle

Two targeted safeguards addressed the connection between immediate spending and future production.

**Keep enough cash for hiring.** Late on day one, I skipped affordable wheat-only orders for a single seed when paying would leave fewer than **4 coins**. Those four coins covered the next morning's first three hires.

The trade-off was not simply “buy fewer seeds.” It was preserving the workforce needed to execute the next production cycle. The safeguard left larger seed batches unchanged.

**Keep planting consistent with purchases.** Skipping a seed purchase also changes what the farm can plant next. Without a corresponding adjustment, the next turn could request more wheat plantings than the available seeds supported, causing the wheat planting batch to fail.

I therefore replaced excess wheat planting requests with `PASS`. The cash safeguard and planting adjustment needed to work together; changing only the purchase would introduce another failure.

## Comparing the Final Variants

The two final variants differed in how broadly they specialized:

- **Focused variant: 2345.5.** General and wool schedules, plus the milk branch.
- **Broader variant: 2325.3.** Adds a tomato branch and uses a wool continuation with more sheep purchases.

From step 144, the broader variant selected tomatoes when each of the first two shops was either Pizza or Farmers Market. The milk rule retained priority.

The focused version finished slightly higher. Both additions changed together and the agents faced different matches, so this comparison does not isolate either branch's value.