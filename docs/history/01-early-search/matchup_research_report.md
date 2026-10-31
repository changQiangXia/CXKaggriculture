# Matchup research 2026-09-12

## Live evidence
- Kaggle team-submissions API currently shows submission 56176848 score/rating 975.1 and 56171485 score 2449.6.
- submission-limits: numToday=1, numTotal=4, numAllowedNow=4 (new UTC day; no submission done by this research).
- monitor state has 56176848 validation episode 108030576 plus 8 competitive episodes 108031686–108038599, all 8 competitive outcomes `win`, no loss/tie. Rewards: [22838,106503], [81414,157403], [83486,40377], [77565,140751], [111906,72355], [91465,48611], [141298,124173], [101816,111682].
- Current monitor process is PID 30161 (monitor.pid confirms), interval 600s; recent scans complete with collected_new=0. Earlier PID 28529 was stale.

## Public notebook intel
- Ahmed V36 (kaggriculture-v36-guarded-four-turn-sales): frozen source SHA256 7eb5ab6c...; four-turn sale reservation from step 288–695, with pickup/purchase/shop-boundary/terminal guards. Independent 512 strong recorded opponents: 272/240/0; reacting 1,856-game panel: 1784/72/0 (96.12%), +3.93pp vs V35, +446 margin; both seats ~96%. Caveat: recorded opponent field and not live rating.
- Ahmed V37 (more-yield-smarter-labor): SHA256 94c1c2...; finite crop fertilization, guarded warehouse sales, shared tomato-worker assignments. Reacting panel 1786/70/0 (96.23%) vs V36 1738/118/0, +48 improved/0 worse, +1180.8 margin; elite 136-panel 81/55 unchanged wins, so original elite gate failed. Treat as promising reacting improvement but uncertain elite robustness.
- Ahmed V35: 1,600 reacting games 1507/93/0 (94.19%) and strong recorded 178/206/0; setup + six-sheep expansion. V36/V37 are most recent evidence.
- New package prepared at /root/autodl-tmp/public_v37_candidate.tar.gz (only root main.py); main.py SHA256 94c1c2..., py_compile passes. This is a new research artifact, not submitted or modifying existing candidates.
- Public newer notebooks list includes V35 reactive sales/sheep (30 votes), V36 guarded four-turn (14 votes), V37 more-yield-smarter-labor (6 votes), Market Smart Farming (61 votes), flex route (65 votes), Thomas 95.5 route (57), Dmitrii herd-safe (60), Avioon Apex V7 (53), and recently updated route variants. V37 has strongest recent quantified reacting result, but low vote/elite caveat.
- Topic 740792 (`How are people making RL work in Kaggriculture?`) advice: identify opponent family around step 12; explicit future-sell cheating worth $224/game vs only ~$38 legitimate opponent identification; hold plans for hundreds steps; average both seats per seed and hold out seed block; weed RNG rerolls shops when replay agent changes; search-generated value targets preferable to naive imitation/PPO. CPU simulator ~670k steps/s; encoding observations bottleneck.
- Topic 740650 confirms environment version discrepancy: local 1.32.7 vs notebook 1.29.3 can alter fertilizer sale behavior. Use official local 1.32.7 environment consistently.
- Topic 740022 RL experiment author had no behavioral cloning and had only trained vs one static agent; planned league training, so not robust evidence.
- Topic 740282 convergence anecdotes vary 4h–4 days; rating noisy. Do not draw decisions from initial 600/975 rating.

## Local V37 checks vs existing agents (official local env, seed 0–2, each ordered pair)
V37 vs Flex: [65518,63441], [148247,147657], [97577,87545] (3/3 wins).
Flex vs V37: [62753,66206], [147657,148247], [87545,97577] (Flex loses all as seat0; seat-swapped rewards symmetric).
V37 vs Thomas: [66309,61551], [109162,101820], [94549,89043] (3/3).
Thomas vs V37: [63475,69010], [101820,109162], [89043,94549] (Thomas loses all as seat0; seat-swap symmetry).
V37 vs Dmitrii: [66735,62553], [149736,145952], [98486,87868] (3/3).
Dmitrii vs V37: [66114,70746], [145952,149736], [87868,98486] (Dmitrii loses all as seat0; seat-swap symmetry).
All local runs completed 720 steps and no exception. Note these are only 3 seeds and not a leaderboard estimate.

## V36 additional checks
V36 vs Flex rewards seeds 0–2: [64083,63781], [146925,146195], [97447,87553]. Flex vs V36: [63088,64776], [146195,146925], [87553,97447].
V36 vs Thomas: [64301,61843], [106900,101710], [94424,89051]. Thomas vs V36: [63594,67731], [101710,106900], [89051,94424].
V36 vs Dmitrii: [64996,63134], [148010,144818], [98353,87870]. Dmitrii vs V36: [66434,69216], [144818,148010], [87870,98353].
V36 was also local-compiled from public notebook, but compile took ~90s due huge tape; `/tmp/avioon/agent.so` had been created before cleanup. No archive was created or submitted.

## Recommendation
The public evidence supports trying V37 as a candidate before V36: its reacting-panel result is positive and local 3-seed checks beat current Python candidates. However, V37 elite-panel gate was inconclusive (81/55 unchanged), so do not claim silver/top-200 guarantee. Before any submission, run >=20 fixed seeds, both seats, package isolation and latency/error checks, then request explicit user authorization. Keep `public_v37_candidate.tar.gz` separate from ready_flex_v7 / ready_thomas_v6 / ready_dmitri_v6.


## Latest active log follow-up
See [latest_active_log_report.md](/root/autodl-tmp/latest_active_log_report.md): V37 11 competitive wins, Flex 25W/5L/3T; latest Flex losses are all small (<=1427) and correspond to opponent tomato/fertilizer/alternate route branches. No runtime errors.
