> **来源 / Source**：Kaggle Kaggriculture 公开 write-up，第 116 名，队伍 **Auto Fermers**。
> **原文**：https://www.kaggle.com/competitions/kaggriculture/writeups/116th-six-weeks-of-llm-coding-agents
> 本文为比赛归档的离线副本，仅作技术参考；**版权归原作者所有**。
> 如作者要求撤下，请联系仓库所有者。

# 116th: six weeks with LLM coding agents, and why replays mattered more than RL

**Silver, 116th of 10,148.** We worked with LLM coding agents throughout, and section 5 shares that experience. Over six weeks we tried forks of public bots, market-microstructure tricks, ML on replays, bandits, and behaviour cloning followed by PPO. What finally worked was the competition's most open resource: its recorded public games. Our final bot replays the recorded games of one strong bot (credited in section 3). It picks among them by the town's shop sequence, using a routing table tuned in simulation, and adds two execution layers of our own. Most published gold solutions were built on replays too; they trained models on them, while we replayed them directly.

## 1. What the competition looked like

Two farms play 720 turns and share a market where both players' orders are matched in lock-step. Every three days a random town shop unlocks: one of 8 types, and repeats are possible. The final ranking was a Bradley–Terry fit to about two weeks of post-deadline games, and only wins, losses and ties counted.

Three things shaped the field:
- **RL was hard.** The result arrives only at the end of a 720-turn game. Most RL attempts posted on the forum plateaued below the strong scripted and cloned bots. The best small-scale one we know of, a single-GPU agent that warm-started from cloning and then trained with PPO, finished 137th.
- **The ladder was full of copies.** Much of the field forked and patched the strongest public notebooks, which were themselves route-tape bots that follow pre-planned action sequences. One participant clustered a day's games and found that 78 % fell into groups with an identical day-6 state. Another found that in 25 of his last 26 games the opponent followed a tape rebuilt from public replays.
- **Replays were public.** Kaggle published the top episodes every day, so every strong bot's play could be studied and, as it turned out, reused.

![Our 181 submissions](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F34249579%2F9d1a5b30f16af0f9bc0599829eb4bc80%2Ffig1_submissions.png?generation=1792212630094314&alt=media)

*Each dot is a submission's live rating; for the final bot, the rating at the end of the ladder. Ratings from different weeks are not directly comparable, because the field kept getting stronger. One failed submission and four early test bots below 1,300 are not shown.*

## 2. What we tried (Aug 20 – Sep 30)

| Approach | What happened |
|---|---|
| Forks of strong public notebooks plus our own layers: sale timing, clone detection, lock-step order "sandwiches", repairs | The team's best live rating was 2896 in mid-September, from Artem's fork of Ahmed Berat Ozer's V43; byte-identical resubmissions settled near 2745. Then the field caught up: our route-tape chassis beat its clones by 0.2–3 % of money and lost by 3–30 % to bots with stronger production. |
| Adding production to that chassis (6 attempts) | Failed: no free tiles or hands, and extra wages ate the extra revenue. |
| ML on replays (gradient-boosted decision models) | Weaker than the bots it was meant to improve. |
| Opening bandit, route selectors, expert portfolio, sale bandit | A hindsight oracle promised +4–5 pp of wins; the selectors we could actually run gave −1.25 to 0 pp. |
| Behaviour cloning, then PPO, on a fast C++/JAX pipeline | Beat the starter bot 32/0 and a public RL bot 28/4, but lost 0/64 to strong public bots. |

In the final days we judged every candidate by wins on fresh, paired worlds against a diverse opponent pool, with forced shop sequences and stress settings. Earlier, the agents often optimised money margins (section 5). Wins over our own older versions turned out to say little about the ladder.

## 3. The final bot: public replays, our routing

On the last day we analysed 2,024 recorded games, screened about 150 single-game replay bots, and scanned recent games of the top 160 teams to measure how much each strong bot reacts to the game. Most react to money, prices and the opponent, so their own games diverge early, often before the first shop opens at step 72. One bot did not. ShunkiKyoya's bot played an identical farm layout until step 144, and after that its moves were almost a function of the shop sequence. Replaying one of his recorded games blindly already won 81–83 % on our 64 test worlds, against 67 % for our best chassis. Replay bots built the same way from four other top teams' games won 8–56 % on the same stand, against 95 % for his, because those bots react to the game.

![Replay bot](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F34249579%2F7078e58c6b8b3d319b82c0405912cdad%2Ffig2_replay_trie.png?generation=1792212663543350&alt=media)

- **Trie (a prefix tree over the recorded games, or "tapes").** Of its 429 tapes, the bot keeps those consistent with its own moves and the visible shops, and follows the best-ranked one. It loads in under 0.7 s, moves in under 1 ms and is deterministic.
- **Routing by simulation.** With 8 shop types there are 512 three-shop prefixes but only 429 tapes, so after step 216 the bot usually follows a tape recorded in a slightly different world. We patched the engine to force a world's first shops and played every tape with each possible third shop. Then we replayed the best tapes against several opponent families: 73.7k games on two 112-core nodes. The resulting table picks the tape for each (shop 1, shop 2, shop 3).
- **Order priority.** The market matches both players' order lists index by index, so earlier orders get better prices. This layer moves our sell and product-buy orders to the front, but only when that provably cannot change which of our orders execute.
- **Weed guard.** It digs out a weed on a tile the plan is about to build on.
- **Release.** About 6,000 test games ran with no exceptions, and the server's validation game matched our local re-simulation in all 1,438 actions.

**Result.** The bot finished 116th, four places and 3 rating points above ShunkiKyoya's own bot (120th). That margin alone is within noise, but our additions measurably improved the plain replay:
- On 160 fresh worlds against seven opponents, the final build won 1044 of 1120 games, against 974.5 for the plain replay trie (392 tapes, no routing table or layers). It did better against all seven opponents.
- Against copies of the original plan it won 32/32 and 28/32, against about 19/32 without the order layer.

The farming plan itself is ShunkiKyoya's.

## 4. The leaders confirm it: replays were the key resource

Nine gold teams have published so far (1st only as a preview). Eight of them start from top players' replays:
- Five clone them with a policy that reacts to the game: [4th](https://www.kaggle.com/competitions/kaggriculture/discussion/750068), [5th](https://www.kaggle.com/competitions/kaggriculture/discussion/750159), [7th](https://www.kaggle.com/competitions/kaggriculture/discussion/745367), [17th](https://www.kaggle.com/competitions/kaggriculture/discussion/749586), [24th](https://www.kaggle.com/competitions/kaggriculture/discussion/749669).
- One clones daily macro decisions and compiles them into actions ([26th](https://www.kaggle.com/competitions/kaggriculture/discussion/749775)).
- Two add self-play PPO on top ([1st](https://www.kaggle.com/competitions/kaggriculture/discussion/745073), [13th](https://www.kaggle.com/competitions/kaggriculture/discussion/745258)).

The ninth pairs a learned opening with a planner and credits public replays for its analysis ([28th](https://www.kaggle.com/competitions/kaggriculture/discussion/750151)). The 17th- and 24th-place teams switched to cloning only in their last 2–4 days, and reached gold after fixing labels and decoding. What separated the leaders was the modelling on top of the replays: executed-trade labels, team and recency conditioning, winner-only training and calibrated decoding.

Six of the nine are transformers or attention models trained on replays, and small ones: 4–55 M parameters, mostly trained on a few GPUs. The recipe looks like LLM training: pretrain on many top players' games, fine-tune on the best team, and at the very top add RL. Imitation accuracy was not strength: the 4th-place team found validation accuracy negatively correlated with money, and selected checkpoints by paired games only.

Our own public-based line shows the ceiling of the other path. The route-tape chassis with ~30 of our layers reached 2,300–2,400 on the live ladder and was among the strongest late public forks we know of. Yet on its own it would have finished about 570th, in the bronze zone; the other late forks we know of ended between 473rd and ~1,400th.

| What we believed at the deadline | What the writeups show |
|---|---|
| RL can't catch strong bots in days | **Mostly.** RL carried a gold solution only at fleet scale (1st, ~8.3 M self-play games) or in a long-engineered one-GPU league (13th). Teams that added a short RL stage to cloning gained at most ~$1.4k per game and left it out of their finals. |
| A replay plateaus at its donor's level | **Yes** (116 vs 120). Cloning with a reacting policy is how the leaders went further. |
| Order position in the market is a small effect | **Partly.** It decides mirror games (ours above; the 26th-place team won 39/40) but is probably worth under 1 % against different bots. |

## 5. Working with LLM agents

We used LLM coding agents heavily throughout the competition, so we want to share that experience too. For five weeks Dmitrii worked through Codex chats (GPT-5.6 Sol, then GPT-6 Astra and GPT-6 Sol). In the final week Claude Opus 5.5 coordinated up to six sandboxed Astra workers that ran their jobs on a compute cluster, and a model from another family reviewed each release. The numbers below cover Dmitrii's side (133 of our 181 submissions); Artem and arsgorynich used their own setups.

![Model output per week](https://www.googleapis.com/download/storage/v1/b/kaggle-user-content/o/inbox%2F34249579%2F64a72f7a75e853fd4b071529ace35ac7%2Ffig4_tokens.png?generation=1792212704699852&alt=media)

*"Other": GPT-5.6 Luna, GPT-5.5 and Codex Spark.*

**In short:** about 64k model calls, 37 M output tokens and roughly 500 agent-hours.

**Models.** Dmitrii's subjective ranking of how convenient each model was here: *Sol 6 < Sol 5.6 < Astra ≈ Fable ≪ Opus 5.5.* His next message had to correct 8–22 % of GPT-5.6 Sol's answers, 14 % of GPT-6 Sol's and Claude Opus 5.5's, and 18–64 % of GPT-6 Astra's in chat. Astra was strong as a bounded worker, and Claude Fable 5.1 served as a reviewer. This is not a controlled comparison: roles and phases differed.

**What helped and what hurt.** Review by a model from a different family caught real defects before release, among them a wrong staged build. The most common failure was the objective: agents optimised coins instead of wins, and took local gains for leaderboard gains. A large monolithic code base could be patched but not restructured.

**Our takeaway.** An LLM agent behaves like a literal genie: it grants exactly the wish you make, quickly and well, but rarely questions the wish. When we asked for RL, the agents built RL; when we asked for a warm start, they cloned a public bot. A transformer that imitates the top teams' replays was never on our list, so the agents never built one: they work within the framing you give them. You still need to know where to look, see the whole picture and design the architecture yourself, and that comes with experience. LLMs are a very powerful tool, not a wish-granting genie.

## 6. Conclusions

The solution itself is not unusual; many teams converged on replays. We publish this mainly as a record of how the work was organised with LLM agents in autumn 2026: what they could and could not do, what we tried, and which conditions of the competition pushed everyone toward replays.

- **The problem is hard, and RL was rarely cost-effective.** Most RL attempts we know of, ours included, plateaued. RL carried a gold solution only with fleet-scale self-play or a long-engineered fast league.
- **Open replays were the key shared resource.** We replayed one bot's games directly and reached the top 1.1 % without training any model. Most gold teams instead trained small transformers to imitate the top players' replays, and that generalised better.
- **Our main lesson.** We should have trained a transformer to imitate the top teams' replays from the first weeks. We tried imitation only once, late: on games of a public bot, as a warm start for RL. When it did not match that bot, we dropped it.
- **Agents amplify what you already know.** They let us test far more ideas in six weeks, but choosing the approach is still up to the people using them (section 5).

## Acknowledgements

- **ShunkiKyoya:** our final bot replays his recorded games.
- **Public notebook authors** our forks and chassis built on (Apache-2.0): Ahmed Berat Ozer ([V56](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v56-smarter-seeds-and-fertilizer), V43), [Thomas Tschinkel](https://www.kaggle.com/code/thomastschinkel/kaggriculture-93-8-win-rate-public-state-router), [Yusuke Hayashi](https://www.kaggle.com/code/yhay81/shop-router-0913), [shiiin9](https://www.kaggle.com/code/shiiin9/your-market-list-is-an-order-book), [tetsutani](https://www.kaggle.com/code/tetsutani/demand-preserving-turn-sale-timing), [aurax7](https://www.kaggle.com/code/aurax7/kaggriculture-shop-router-reactive-v5), Kaito Fukami and others.
- **The teams who published solutions,** which made section 4 possible.
- **The Kaggle team,** for the competition, its open simulator and the public replays.
- **Team Auto Fermers:** Dmitrii Gluzdov, Artem Boltaev, arsgorynich.