# Public code/discussion intelligence, rounds 1–2 (2026-09-15)

## Round 1: live public code index

Using the configured Kaggle CLI against competition `kaggriculture`, the public kernel list was fetched with `--sort-by voteCount --page-size 100`. Raw index: [public_code_intel_20260915_round1.json](/root/autodl-tmp/public_code_intel_20260915_round1.json).

High-signal public entries include:

| votes | public code theme |
|---:|---|
| 313 | premium market lead with 8 COW / 4 SHEEP route |
| 201 | strict-future day 25/27 meta reset |
| 188 | findings from zero to top meta |
| 142 | adaptive farming strategy |
| 137 | rank-your-agent / route evaluation |
| 131 | six-day public-state fieldbook |
| 128 | shop router 0909 |
| 105 | more yield, smarter labor |
| 103 | frontier / soil remembers rain |
| 99 | public state router |
| 98 | crop economics and visualization |
| 93 | multi-route farming agent |
| 92 | reactive shop router |

This is public scouting information only. No public code was copied into the current submission.

## Round 2: downloaded and inspected public notebooks

The following public notebooks were downloaded into `public_code_round2/` and converted to text for inspection:

- Boatlee premium market lead;
- Kaito strict-future v27;
- Rayk findings from zero to top meta;
- Yusuke six-day public-state fieldbook;
- Pilkwang structured economic policy;
- Prvsiyan soil-remembers-rain frontier;
- Georgy crop economics visualization.

The most actionable technique is Boatlee's bounded one-turn premium-market lead. It does not sell everything early. It looks at the next tape's SELL quantity, visible town demand, current shed inventory and pickup reserve; if the next turn will sell a premium item, it may sell a limited quantity one turn early, then repays the moved quantity on the next turn. It preserves order slots and skips front-running when town demand is due. The relevant public pattern is:

```text
future SELL suffix + visible shed - pickup reserve - existing SELL
→ bounded one-turn front-run
→ next-turn repayment / quantity accounting
```

This is materially different from global SELL merging. It treats order timing as a market-flow decision and preserves the parent's route and physical actions.

The crop-economics notebook provides useful engine facts: premium products such as MELON are highly sensitive to oversupply; town shops consume every four turns, town center consumes one unit per day; shop draws are with replacement and are coupled to the engine's random stream; care compounds animal production; fertilizer is essential for max WHEAT. These facts reinforce the need for state-conditioned sales and caution against copying fixed tapes.

The soil-remembers-rain and structured-policy notebooks emphasize conservative state contracts, route/production commitments, and explicit guardrails around feed, care, fertilizer and projected inventory.

## Discussion-area result

The first probe used the global `forums` command and guessed web endpoints, which do not identify competition topics. A second probe of the installed CLI help revealed the supported command `kaggle competitions topics list/show`; using it against `kaggriculture` returned competition-specific topics and comments. Raw responses are preserved as `topic_740022.json`, `topic_739273.json`, `topic_740823.json`, and `topic_741414.json`. The extracted claims below are attributed to individual commenters and treated as hypotheses until local validation.

## Local experiment implications

1. Do not import the Boatlee route wholesale: it is tied to a different opening, route and replay family.
2. A safe experiment should wrap V42 with a bounded one-turn front-run only for premium items, using visible town demand, current shed, pickup reserve, existing SELL and order-slot barriers.
3. The wrapper must repay on the next turn, abstain when the parent has BUY/HIRE or no free order slot, and fall back to V42 on any state mismatch.
4. Validate against common seeds, four strong opponents, both seats, and track negative margins, 5% margin quantile, seat variance, max callback duration and front-run activation count.

### Round 2b: competition discussion topics fetched via CLI

The competition-specific topic endpoint is available as `kaggle competitions topics`. I fetched topic metadata and comments for IDs 740022, 739273, 740823, and 741414 (raw JSON: `topic_*.json`). Actionable observations:

| topic | evidence | implication for our agent |
|---|---|---|
| My experimentation with RL (740022, 31 votes, 25 comments) | Authors report static-opponent RL can reach ~70K, but commenters stress that recent static replays differ materially; proposed next step is a league of diverse tapes or replay fragments. | If we train or tune, use a multi-opponent/fragment league. A single tape opponent creates representation bias and will not explain our online tail losses. |
| Replay-measurement pipeline (739273, 34 votes, 18 comments) | Nathan Jacob reports 3/4 of v40 losses came from two cows dying on day 1 due to a missed FEED; each death cost roughly $12–32K. He retained only 4 of 16 tested fixes after deterministic local arena checks. Other comments describe tape + state-dependent mechanism as the current public frontier and warn of diminishing returns from copied tapes. | Add an explicit day-1 feed invariant and reject any candidate with a feed omission. Keep the local common-seed arena as the gate; most intuitive patches should be expected to regress until measured. |
| City shops (740823, 0 votes, 1 comment) | Shops consume from the common market periodically; useful state is `town.unlocked_shops`, market inventory/prices, future production and rival supply. Shops are drainage, not direct buyers; premium oversupply can still collapse price. | Use shop unlocks as an absorption feature in bounded sale timing. Do not route or dump product solely because a shop is unlocked. |
| Final-week replay analyzer (741414, 1 vote, 2 comments) | A public browser dashboard reads replay JSON locally and visualizes P&L/cost leaks; no data leaves the machine. | Our existing JSON reports can be cross-checked with the same P&L-by-phase view; no need to upload private logs. |

The RL and replay-measurement comments are anecdotal public claims, so they are hypotheses rather than leaderboard facts. We preserve provenance (topic IDs, dates, votes) and will validate any change in the real 720-step engine before considering a candidate.

另一个已抓取主题 `does copying opponent help?`（740588，14 comments）提供了可测试但未经证实的市场时序假设：评论者认为只能把对手上一回合的 BUY/SELL 当作供给压力信号，不能逐动作镜像；一种说法是对已知的下一回合销售做单步前移，但必须处理草、土地、现金和同回合不可反应等约束。我们只把它纳入 `premium_front_run` 的待验证假设，不把对手复制逻辑写入候选。
