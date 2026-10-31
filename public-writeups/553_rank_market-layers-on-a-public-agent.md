> **来源 / Source**：Kaggle Kaggriculture 公开 write-up，第 553 名，队伍 **42**。
> **原文**：https://www.kaggle.com/competitions/kaggriculture/writeups/market-layers-on-a-public-agent
> 本文为比赛归档的离线副本，仅作技术参考；**版权归原作者所有**。
> 如作者要求撤下，请联系仓库所有者。

# Market layers on a public agent, and where they stop

**Final result: #553 of 10,148, a bronze medal, 15.3 points (46 places) below silver.** We are team 42 ([Kefei Yan](https://www.kaggle.com/kefeiyan), [Frank Yang](https://www.kaggle.com/ffy208), [yirenw11](https://www.kaggle.com/yirenw11)). Our final agent is a public route-replay agent with a stack of our own market layers on top. It reached live #128 on Sep 26 and then slid as the strong final versions arrived. This post covers what we tried, how the agent works, how we measured, and why market play was not enough.

Thanks to Kaggle and the hosts for a great game. Everything is in our repository, [github.com/cliff003/Kaggriculture](https://github.com/cliff003/Kaggriculture): all 34 packages we built, the tools, and the documentation behind every number below.

## TL;DR

- **We built on a public base, chosen by measurement.** Our own planner stalled at a live rating of 1014.5. The public cha22 agent with our first layer beat the 21 distinct codes among the top 30 public notebooks 826 games to 14.
- **Order position is worth money.** The engine clears market orders slot by slot, so the earlier sell gets the better price. Moving our sells first won 97 of 100 local games against the unmodified base.
- **The town eats after the market.** Buying wheat in the last slot of that step and selling it on the next (TICK) took us to live #128 and was worth 616 per game to our final agent.
- **Whatever you show gets traded against.** Within half a day other teams were trading against TICK. A guard that checks our cash against our own orders turned two losses of about 17k each into wins on replay.
- **Market layers have a ceiling.** Our last change gained 10 wins on 1,572 replays. The games we still lost, we lost on production.

## 1. What we tried, in order

| Phase | Dates | What | Result |
|---|---|---|---|
| Our own planner | Sep 16 to 21 | a planner with economics, rival tracking, scheduling and trading modules; 19 uploads | stalled at 1014.5; locally it lost all 2,240 games against seven public-level agents |
| Public bases | Sep 22 to 24 | five public agents uploaded verbatim, one of them twice | 1992 to 2534; cha22 was the strongest in the same window |
| cha22 plus selling layers | Sep 24 to 25 | v4 to v7c: sell first, sell shallow goods on arrival, fixes to the base | 2590.8 (v7b) |
| TICK | Sep 26 | v8: wheat traded around the town's meals | peaked at 2679; live #128 |
| Defences and production patches | Sep 26 to 30 | v9 to v12_19: trap guard, FADE, gated tomato and fertilizer patches | final #553 with V12_AventadorSVJ and v12_19 |

Two lessons came out of the first two phases. First, measure the public bases against each other before building on one: with our first layer, cha22 won 826 of 840 local games against the other public codes, and uploaded verbatim on Sep 24 it reached 2333 in 7 hours, against 2100 in 10.8 hours for rescue, another public base uploaded the same day. Second, compare live ratings only within the same window. The same public code scored 2534 when we uploaded it on Sep 22 and 2100 when we uploaded it again on Sep 24, because the field had got stronger in between.

## 2. Two engine facts we built on

**Orders clear slot by slot.** Each player sends up to 10 market orders a step. The engine fills them slot by slot, and within a slot both players fill one unit at a time at the same price. Every unit sold lowers the price, so the earlier sell gets the better prices: 20 milk sold first from the neutral stock earn 2,802; sold second, 1,962; in the same slot, 2,402 each. The high-value markets are shallow: 76 extra milk take the price from 160 to 1, and 62 strawberries or 59 wool do the same to theirs.

**The town eats after the market.** On every fourth step (`s % 4 == 0`) each shop eats one of each of its goods, and once a day the town centre eats one of everything. This happens after the orders have cleared.

![Figure 02: order matching](https://raw.githubusercontent.com/cliff003/Kaggriculture/main/docs/img/02_order_matching_light.png)

*Figure 02. One engine step, why the slot matters, and a real turn of our agent: sells in slots 0 and 1, the TICK buy in slot 9.*

## 3. How the agent works

The base is [cha22](https://www.kaggle.com/code/abhinav0370/cha22-agent) by Abhinav0370. It follows 41 recorded routes (action tapes from strong past games): one opening for days 0 to 5, a mid-game route chosen on day 6 by the first two shops, and an endgame tape from day 27, with dozens of public reactive layers on top. We left its logic in place. Every addition is either a wrapper, which receives the observation and the action of the layer inside it and edits that action, or a patch inside the base source that is off unless its condition holds.

![Figure 01: the agent](https://raw.githubusercontent.com/cliff003/Kaggriculture/main/docs/img/01_agent_light.png)

*Figure 01. The public base and our wrappers, inner to outer, each with the evidence that kept it in.*

- **Sell first** (v4). From day 12 we move sells ahead of hires and seed, animal and land purchases: 97 W / 3 L locally against the unmodified base. Doing it from step 0 broke the opening (0 W / 36 L).
- **Eager sell** (v6). The base sells in small lots on its tape schedule, so in an oversupplied market it sells late and cheap. We sell milk, strawberries and wool as they arrive if the quote is at least 0.3× the base price. On replay this flipped 9 of the previous version's 19 live losses.
- **Room guard.** At hour 23 the warehouse destroys everything above 100 items. We predict the overflow with the engine's rules and sell it first (local panel: 140 → 154 wins of 210).
- **Fixes to the base** (v7c). A dedicated six-sheep worker could stall for a whole day when the warehouse had no wheat, which cost about 5,000 per wool game. The base also sold most of its animal fertilizer for 10 to 20 late in the game; putting it on crops wherever it was worth more than its quote took local wins from 844 to 873 of 980.
- **Production patches.** Four narrowly gated changes to the base's tomato and fertilizer modules, for example 18 tomatoes instead of 10 when four or more of the first six shops are pizza shops or farmers' markets. Each is off unless its condition holds.

## 4. TICK: trading on the town's meal

We found the idea in Otter Vibe's public replays. On a step with `s % 4 == 0` we buy up to 95 wheat in the last slot, after the rival's orders in slots 0 to 8, and sell the lot on the next step. In between, the town eats c units of wheat at the price our buy pushed up, so the round trip earns about

`gain ≈ c × (P(gap + N) - P(gap))`

where gap = 10,000 - wheat stock, P(gap) = 25 + √gap (rounded) and N is our lot.

A single round earns little: in the first example of Figure 03 the town ate 3 units, the price had moved from 40 to 43, and TICK made 9. But there are six such steps a day. On 576 replayed live games v8, the first version with TICK, won 538 against 497 for v7b (the difference includes the v7c fixes), and it beat v7b 60 W / 0 L head to head. Two hours after upload v8 stood at 2594, while v7c and v7b had stood at 2280 and 2172 at the same age. That morning it took us to live #128. Switching TICK off in our final agent cost 616 per game on 1,504 replays: 112 games flipped to losses and 3 the other way.

## 5. Whatever you show gets traded against

Within half a day of v8 going live, other teams were trading against TICK.

- **Same-direction arbitrage.** Rivals running the same wheat trade from slot 0 always filled first and left us buying high and selling low (-3k to -11k per game). Stock changes reveal the rival's wheat flow exactly, so a peer guard stops TICK once a rival makes the same round trip twice in eight rounds.
- **Sandwiches.** At the tick a rival bought 80 to 90 wheat in slot 0 to lift the price and sold the same amount in slot 9, straight into our last-slot buy, then reversed on the next step. Its net flow per step was zero, so the peer guard could not see it, and v8 lost its games against two such traders by about 17k each.
- **Trap guard** (v9). Money only moves in the market, so each step we work out with the engine's rules what our own orders should have cost and compare that with the actual cash on the next step. In the sandwiched round of Figure 03 our 95 units should have cost 3,900 and cost 3,990. Repeated mismatches stop TICK, and the guard trades back: it sells into the lift in a middle slot and buys back in the last slot on the next step. On replay the two sandwich games went from -16,743 to +13,919 and from -17,114 to +10,419, and none of v8's last 94 live games flipped to a loss.
- **FADE** (v12). Once the guard has identified an arbitrageur, we take the other side: right after its buy lifts the price we sell up to 90 wheat, and after its sell drops the price we buy them back, both in the last slot. FADE was our first change whose payoff grows with the rival's volume. On the 49 replayed games against arbitrageurs, wins went from 41 to 47.

![Figure 03: the wheat cycle](https://raw.githubusercontent.com/cliff003/Kaggriculture/main/docs/img/03_wheat_cycle_light.png)

*Figure 03. Four wheat rounds from real games, unit by unit: TICK alone (+9), TICK sandwiched (-117), the trap guard's counter (+241) and FADE (+206).*

Because of this, we held our strongest version back until about two days before the deadline. That protected it, but left less time to validate it.

## 6. How we measured

- **Live-replay counterfactuals.** We re-ran our own live games with the rival's recorded actions, the real seed and the real shop order, replacing only our side with the candidate. The engine reproduces server games exactly; by Sep 30 we had 1,572 deduplicated games. The rival cannot react, so every market change was also tested on a reactive panel of 7, later 13 local opponents, including our emulations of the sellers, arbitrageurs and sandwich traders we met on the ladder.
- **Force the shop order.** Weed draws on empty tiles share the random stream with the shop draw, so a change that alters the number of empty tiles also changes which shops open. Every local A/B forces the shop order.
- **Count flips, not money.** The ranking only counts wins. A change had to win at least as many games as it lost on replay and leave no panel opponent worse. Several changes that added money were dropped for one or two flipped losses.
- **Sample worlds, not seeds.** After swapping seats, 78% to 91% of worlds gave exactly the same money gap.
- **Do not trust self-play.** Route tables (switching the mid-game route by the first two shops) went 80 W / 16 L against our own champion and fell from 263 to 148 wins of 280 against the reacting cha22 family.

## 7. Where it stopped

![Figure 05: the standing](https://raw.githubusercontent.com/cliff003/Kaggriculture/main/docs/img/05_standing_light.png)

*Figure 05. Live rank from Sep 26 to Oct 16, and the final board.*

**Production.** By Sep 30 our last change, v12_19, gained 10 wins on 1,572 replays. The games we still lost were lost on the farm: against a production-heavy team (final #54) our final agent won 9 of 75 replayed games, and that team earned 6.2k more per game in eggs, 3.6k in strawberries and 3.2k in carrots. We could not close the gap ourselves. The best of about 60 schedulers we wrote from scratch was 11.5k per game behind cha22. Cloning the then-leading team reached 0.88 action accuracy and won 0 games. Our production agent p6 was 7.9k per game behind our own Sep 25 agent without TICK, and given a strong team's own plan from its own seat, it lost 19.1k per game in the same games where that team had been 7.3k ahead. Choosing the plan was not our problem; executing it was.

**The final board.** On Sep 28 and 29 we were 144 to 226 live points above the silver line and thought silver was safe. We finished 15.3 points below it, for three reasons:

1. **Only games between final submissions count.** The final board fits only games in which both sides were still active at the end, so about 85% of our counted games were played after the deadline. Of our final agent's 333 games before the deadline, only 102 counted.
2. **The strong finals arrived late.** On Sep 29, 72 of our 95 games were against submissions uploaded after our final agent went live. We won 20 of them and lost 52, mostly to production-heavy farms.
3. **Our two finals were one agent.** The second final was an improved version of the first, not a hedge. After the deadline they lost the same worlds; on Oct 6 their 51 games had exactly the same outcomes.

After the deadline we won 233 of 705 games (33%) against the silver zone (#31 to #507) and 572 of 917 (62%) against the bronze zone (#508 to #1014). A logistic fit gives us a 46% chance against a team at the silver line: silver was within reach, but above the line we won about one game in three.

## 8. What did not work

The main dead ends; all 68 are in [docs/experiments.md](https://github.com/cliff003/Kaggriculture/blob/main/docs/experiments.md).

| Idea | Result |
|---|---|
| Holding milk for the evening | -868 per game on 636 replays (88 flips lost, 1 won) |
| TICK's sell forced into slot 0, ahead of our milk | -717 per game, 116 flips lost |
| Tomatoes instead of strawberries on the recorded routes | 413 replays: wins 394 → 229, -3,193 per game |
| A top team's recorded actions replayed on our base | -29.8k per game |
| Knowing the rival's same-step orders in advance (an upper bound for order placement) | +46 per game: not worth chasing |

## 9. What we would do differently

1. **Benchmark every public base in the same time window before building on one.**
2. **Read lost games.** Each layer in section 3 and section 5 came from one.
3. **Count flipped games on held-out worlds against the real field,** with the shop order forced.
4. **Size production to the shops from day one,** and if hand-written production stalls, start learning it from replays early instead of patching a replay base late.
5. **Test against the final field, and make the second final a different agent.** Only games between final submissions count, and two versions of one base are no insurance.

## Credits

- [cha22](https://www.kaggle.com/code/abhinav0370/cha22-agent) by Abhinav0370 and the public route-replay lineage it builds on: thomastschinkel, yhay81, destbreso, aurax7, tetsutani, prvsiyan, Dmitrii Gluzdov, Ahmed Berat Ozer and others.
- Otter Vibe, whose public replays showed us the tick trade, and everyone who shared public analyses (listed in the repository).
- Our code and text are under the Apache License 2.0; every package keeps its upstream license text and attribution notices.