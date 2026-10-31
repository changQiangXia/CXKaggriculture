# V42 focused ablation (local, no submission)

Setup: Kaggle `kaggriculture` local engine, full 720 steps, V42 candidate against frozen `public_v37_pkg/main.py`, seeds 9101-9105, both seat orders (10 games per variant). Rewards are terminal scores; margin = V42 variant minus v37.

| Variant | Wins/Loss/Ties | Mean margin | Min margin | Complete |
|---|---:|---:|---:|---:|
| Full V42 | 10/0/0 | +34,763.9 | +25,597 | 10/10 |
| Disable R128 service/credit | 10/0/0 | +34,763.9 | +25,597 | 10/10 |
| Disable R127 grain/last-hour | 10/0/0 | +34,763.9 | +25,597 | 10/10 |
| Disable R124 opening safeguards | 10/0/0 | +34,763.9 | +25,597 | 10/10 |
| Disable shop-aware route selector (force old route map) | 10/0/0 | +32,614.3 | +19,605 | 10/10 |

Full-V42 vs no-selector margin deltas by seed (seat 0/1):

- 9101: -1,910 / -1,910
- 9102: 0 / 0
- 9103: -5,992 / -5,992
- 9104: -1,343 / -1,343
- 9105: -713 / -2,293

Thus route selection costs 0–5,992 margin when removed, mean loss ≈2,149.6 points over this small panel; the largest effect is seed 9103. Every variant still won all ten games, so this is a score-margin effect rather than a win-rate effect in this panel.

The three wrapper ablations were bit-for-bit identical in terminal rewards for these seeds. A one-game telemetry audit (seed 9103, V42 as seat 0) showed R128 service counters all zero; R127 priority-grain counters zero (its last-hour drop counter was 1); R124 seed-budget/atomic rescue counters zero (day-1 hires/cash bookkeeping still ran). Therefore these wrappers were not materially exercised in the selected market trajectories; this panel cannot estimate their latent value under other shop/market combinations.

Artifacts: `results.json` and `log.txt` under each variant directory. No Kaggle submission was performed.

## Online replay alignment audit

The submitted V42 validation replay `108955843` was downloaded and compared against fresh-process v37 and V42 calls on the same captured observations. Both online agents completed all 720 steps with empty stdout/stderr. The first route-state divergence occurs at step 144 for the observed pair `BAKERY, PET_CAFE`: v37 remains on route 0 while V42 selects route 106. V42 and v37 use different opening orders at step 0, so the first raw action difference is step 0; after the route switch there are 504 route-state-divergent steps and 281 raw action differences across the 720-step replay. Detailed per-step evidence is in `online_replay_diff.json`.

## Loss replay 108961159 (505 margin)

Detailed replay audit is in [loss_108961159_analysis.md](loss_108961159_analysis.md). Both agents completed all 720 steps with no errors; actions differ at only 29 turns and final sheds are empty. The 505 cash deficit is cumulative transaction sequencing, with the largest single jump (+123 for Bohann) at step 648: Bohann sells STRAWBERRY 18, WHEAT 10, MILK 1 while V42 sells WHEAT 5, MILK 1, STRAWBERRY 18, WHEAT 5. Since market orders execute one unit at a time in queue order and prices move after each unit, splitting/reordering same-item sales materially lowers revenue. Combining/grouping wheat sales and evaluating order permutations is a focused candidate; terminal planner and R124/R127/R128 did not cause this loss.

## Expanded four-opponent panel

To test whether the apparently inert layers mattered outside the first v37-only panel, three variants were run against frozen v37, Flex, Thomas and Dmitrii, with seeds 9001-9010 and 9101-9105, both seat orders (120 complete games per variant). Every game reached step 719/DONE; no action exceptions were observed.

| Variant | Opponent | Wins/Loss/Ties | Mean margin | Min margin |
|---|---|---:|---:|---:|
| No opening V42 orders (restore v37 BUY 13+30 / SELL 30) | v37 | 30/0/0 | +3,690.9 | +14 |
|  | Flex | 30/0/0 | +7,233.4 | +3,978 |
|  | Thomas | 29/1/0 | +10,627.6 | −590 |
|  | Dmitrii | 30/0/0 | +8,319.1 | +5,617 |
| No terminal planner (disable steps 712-718 rewrite) | v37 | 30/0/0 | +29,815.8 | +9,779 |
|  | Flex | 30/0/0 | +32,015.4 | +13,034 |
|  | Thomas | 30/0/0 | +8,752.6 | +1,408 |
|  | Dmitrii | 30/0/0 | +8,276.8 | +5,579 |
| No R85-R97 resource layer | v37 | 30/0/0 | +29,059.5 | +8,988 |
|  | Flex | 30/0/0 | +31,291.2 | +12,144 |
|  | Thomas | 30/0/0 | +7,595.8 | +841 |
|  | Dmitrii | 30/0/0 | +7,269.9 | +4,434 |

The opening policy is a real robustness mechanism: removing it produced the only loss in the expanded panel (Thomas, seed 9004, seat 1, −590) and nearly erased the v37 margin on some seeds. Disabling terminal planning or R85-R97 remained win-stable but reduced margins against several opponents; these layers are beneficial as score cushions even though they do not decide wins here. The route selector remains the only mechanism with an independently measured gain in the original paired ablation, and should remain the V42Pro foundation.

The expanded artifacts are `no_opening/focused.json`, `no_terminal/focused.json`, and `no_r85_97/focused.json` in this directory. No new submission was made.

## Runtime and divergence evidence

For loss episode 108961159, the V42 log contains 719 action calls (steps 0-718): mean 2.24 ms, median 1.06 ms, maximum 432.7 ms (one cold-start call), total recorded action time 1.61 s. Stdout and stderr were empty, and the replay confirms all 720 environment steps completed. On the captured validation replay 108955843, the first route-state divergence from v37 is step 144 (the shop-aware selector); there are 504 route-state-divergent steps and 281 raw action differences. These measurements satisfy the timing and first-divergence checks without introducing a new submission.

## Expanded focused ablations (120 games each)

The completed focused panels (seeds 9001-9010 and 9101-9105, both seats, opponents v37/Flex/Thomas/Dmitrii) all ran 720 steps with no runtime failures. Summary by opponent:

| variant | opponent | W/L/T | avg margin | min margin |
|---|---|---:|---:|---:|
| no opening override | v37 | 30/0/0 | +3,690.9 | +14 |
| no opening override | Flex | 30/0/0 | +7,233.4 | +3,978 |
| no opening override | Thomas | 29/1/0 | +10,627.6 | −590 |
| no opening override | Dmitrii | 30/0/0 | +8,319.1 | +5,617 |
| no terminal planner | v37 | 30/0/0 | +29,815.8 | +9,779 |
| no terminal planner | Flex | 30/0/0 | +32,015.4 | +13,034 |
| no terminal planner | Thomas | 30/0/0 | +8,752.6 | +1,408 |
| no terminal planner | Dmitrii | 30/0/0 | +8,276.8 | +5,579 |
| no R85-R97 resource layer | v37 | 30/0/0 | +29,059.5 | +8,988 |
| no R85-R97 resource layer | Flex | 30/0/0 | +31,291.2 | +12,144 |
| no R85-R97 resource layer | Thomas | 30/0/0 | +7,595.8 | +841 |
| no R85-R97 resource layer | Dmitrii | 30/0/0 | +7,269.9 | +4,434 |

The opening override is therefore the only expanded ablation that produced an actual loss (one Thomas game) and sharply reduced margins. Terminal and R85-R97 wrappers are not required for wins in this panel but removing them lowers margins, especially against Thomas/Dmitrii; retain them unless a larger holdout demonstrates harm.

## V42Pro gate decision

A targeted `merge648` prototype was prepared to merge duplicate WHEAT sells at step 648, the concrete mechanism implicated by loss 108961159. It was smoke-tested for two v37 seeds (both completed and won), but the full paired panel was intentionally not accepted as evidence because the run was interrupted before completion. Since order merging can change one-unit market interleaving, this prototype remains an experiment under `merge648/main.py`; it is not promoted to the sole V42Pro candidate. The current evidence-backed candidate remains the submitted V42 policy unchanged, with route selector and opening policy retained. A future V42Pro promotion requires a complete multi-opponent paired panel for the merge/order variants and a no-regression check against the full V42 trace.

## R124/R127/R128 expanded panels

The three service-layer ablations have now completed the same 120-game panel (four opponents, 15 seeds, both seats, 720 steps):

| Variant | v37 mean/min | Flex mean/min | Thomas mean/min | Dmitrii mean/min | W/L/T total |
|---|---:|---:|---:|---:|---:|
| No R124 | +29,847.7 / +9,849 | +32,035.5 / +13,082 | +8,758.9 / +1,416 | +8,281.1 / +5,579 | 120/0/0 |
| No R127 | +29,847.7 / +9,849 | +32,035.5 / +13,082 | +8,858.7 / +1,416 | +8,281.1 / +5,579 | 120/0/0 |
| No R128 | +29,927.5 / +9,849 | +32,103.4 / +13,082 | +8,758.9 / +1,416 | +8,281.1 / +5,579 | 120/0/0 |

The result is a stable no-regression gate for this panel, while the near-identical margins confirm that these wrappers are rarely exercised in the sampled market trajectories. They remain enabled in V42 for conservative protection, but are not credited as the primary source of the V42 uplift.

A fresh-process timing smoke was also run for every ablation variant (four representative opponent/seed/seat combinations per variant). All 28 smoke games reached 720 steps with zero captured exceptions. Across variants, mean per-call latency was 0.87–1.15 ms; the largest observed single call was 265.7 ms. Full-panel JSONs provide the complete win/loss/margin/720-step records; `timing_smoke.json` provides the corresponding timing and anomaly schema for each mechanism.

## Route-selector expanded panel completion

The no-route-selector variant has now completed the full 120-game panel. It remained win-stable (30/30 against each of v37, Flex, Thomas and Dmitrii), but reduced mean margins relative to the complete V42 baseline: +28,297 (v37), +31,347 (Flex), +8,141 (Thomas), and +7,494 (Dmitrii). Its minimum margins were +9,849, +13,082, +1,416 and +4,951 respectively. The route selector is therefore retained as the central V42 mechanism.

`mechanism_results.json` is the machine-readable per-mechanism summary and `ablation_manifest.json` maps every variant to its raw JSON. `timing_smoke.json` contains fresh-process timing, error and completion records for four representative games per variant; the 120-game result JSONs contain the full outcome/score/step panel. Because the historical panel runner did not persist per-call timing and first-divergence traces for every one of those 120 games, those two fields are not retroactively claimed as complete per-game evidence. The manifest marks this as a representative timing status, and no candidate is promoted or submitted on that basis.

## Final gate status

No modified candidate has produced a stable score improvement over complete V42 on a complete four-opponent, double-seat holdout panel. The `merge648` sale-order idea remains smoke-only (20 games) because its full panel was interrupted. Under the conservative gate, the only evidence-backed candidate remains the already submitted V42; there is no safe V42Pro to submit at this point.

## Trace-run boundary

A shadow-trace implementation was attempted to record per-call timing and first divergence for every full-panel game while invoking complete V42 on each identical observation. The method is correct in principle, but the local Kaggriculture struct conversion made it prohibitively slow (several minutes per 720-step game) and it was stopped before producing a checkpoint. No partial trace file was treated as evidence. The authoritative timing evidence remains `timing_smoke.json` (four fresh-process representative games per variant), while the authoritative complete-panel evidence remains the seven 120-row outcome JSONs. This limitation is explicitly recorded in `ablation_manifest.json`; it does not affect the no-submission decision.

## Evidence status (machine-readable)

The exact scope and remaining evidence limits are recorded in `evidence_status.json`. All seven primary ablation JSONs have complete 120-game outcome panels. Timing/error evidence is fresh-process and representative (28 games, four per variant), not retroactively attached to every historical panel row. First-divergence evidence is complete for one online V42-v37 replay (route switch at step 144), not for every ablation row. These limitations are deliberate and prevent overclaiming completion.

`full_v42_panel.json` is now a deduplicated 200-row control index assembled from the original cross-opponent and holdout files. It provides the complete V42 reference for pairing against every primary ablation row by `(opponent, seed, seat)`.

## Latest monitor loss

The post-restart monitor collected episode 108996168 for submission 56209639 (102358 vs 110215, margin −7857). Its 719 calls had mean 1.361 ms, median 0.719 ms, maximum 313.8 ms, and no stdout/stderr output. Replay inspection shows the agent used the old v37 opening orders and diverged around the day-27 production/sale sequence; it is not the submitted V42 (56234455), so it is not evidence of V42 degradation. Details are in `loss_108996168_analysis.md`.

## New submitted-V42 loss (episode 108989503)

The monitor collected a new V42 loss against opponent `cg`: 122461 versus 122689 (−228). Both agents completed 720 steps; V42 had 719 calls with mean 1.376 ms, median 0.720 ms, maximum 304.3 ms, and no stdout/stderr output. The first action divergence was step 1 because `cg` used a different opening (BUY WHEAT 7 plus two hires) while V42 used its tested 5+10/SELL 60 opening. Later differences included a large opponent wheat sale and early fertilizer/milk transactions. Since `cg` is outside the four public opponents used in the paired panel and the loss is only 228 points, this is recorded as an adaptive-opponent robustness sample, not a basis for changing V42. Full analysis: `loss_108989503_analysis.md`.

## Online V42 non-win inventory

`v42_online_nonwins.json` now inventories every competitive non-win currently observed for submission 56234455. There are two losses and no ties among 43 competitive episodes; both losses have 719 logged calls and empty stdout/stderr. This file is regenerated from monitor state and collected logs, so it separates true V42 failures from the older submission 56209639 losses.

## New V42 near-tie (episode 108998279)

The monitor collected a V42 near-tie against `whm8016`: 89768 versus 89773 (−5). Both agents completed 720 steps with no output errors. V42 timing was 719 calls, mean 2.265 ms, median 1.020 ms, maximum 430.0 ms. Only steps 302, 528 and 677 differed; the opponent planted Wheat where V42 dug, prefixed a one-unit Wheat sale before Milk, and built a coop where V42 dug. This five-point adaptive-opponent tie-break is recorded in `loss_108998279_analysis.md` and does not provide evidence for changing the validated V42 mechanisms.

## Offline full-step trace representatives

An offline trace runner now completes each representative game's candidate trajectory for all 719 action calls, then replays the saved observations through a fresh V42 control process. This avoids running two agents inside the Kaggriculture environment and makes first-divergence measurement reproducible. Four representative games per mechanism (one v37, one Flex, one Thomas, one Dmitrii; mixed seats/seeds) are stored under `traces/*.json`, with aggregate checks in `trace_summary.json`.

All 28 representative traces have 719 calls, 720 environment steps, zero exceptions, and per-call timing fields. Observed first-divergence patterns are mechanism-consistent: opening at step 0, route selector around step 166, R85-R97 around steps 252/340, R127 at step 383, terminal planner at step 712, and no divergence for R124/R128 in these representatives. These traces strengthen the timing/divergence evidence but do not replace per-game fields for the remaining 120-row historical outcome panels.

## Authorized no-R128 Kaggle comparison submission

Per explicit user authorization, `no_r128_v42.tar.gz` was submitted once for direct online comparison with V42. Upload used the resilient Kaggle client with the resumable upload host handling requested for `storage.googleapis.com`. Kaggle returned submission ref `56238321` with status `PENDING`; no retry or second submission was made. The active monitor will begin collecting its episodes once Kaggle exposes the pending submission in `team-submissions`.

## Online V42 versus no-R128 score divergence (2026-09-15)

The monitor now sees both authorized active submissions. The latest team-submissions response reports public scores of 2080.5 for V42 (`56234455`) and 2765.3 for no-R128 (`56238321`); these values are dynamic and have changed slightly during evaluation. The replay sample is not consistent with interpreting that 684.8-point gap as a direct policy-quality gap:

| submission | competitive episodes | wins | losses | ties | own mean reward | opponent mean reward | mean margin |
|---|---:|---:|---:|---:|---:|---:|---:|
| V42 | 113 | 107 | 5 | 1 | 108,236 | 92,734 | +15,502 |
| no-R128 | 107 | 63 | 27 | 17 | 101,471 | 95,656 | +5,815 |

The sequence is also revealing. V42 remains win-heavy in every 20-game block (19/20, 19/20, 19/20, 20/20, 19/20, then 11/13 in the newest partial block). no-R128 starts 20/20, then moves to 13/20, 8/20, 11/20, 8/20, and 3/7 in the newest block, with most non-wins being near ties. This is the expected shape when a submission's rating or matchmaking pool is updated after an unusually strong opening streak: early wins raise the estimated strength, later games are against stronger opponents, and the public score can remain high while raw win rate and reward margin fall.

The opponent-reward signal points in the same direction. no-R128 has faced opponents averaging about 95,656 terminal reward, versus about 92,734 for V42, despite producing a lower own reward. Earlier name matching against the current leaderboard also found a much stronger identifiable opponent pool for no-R128. These are observational indicators rather than a reconstruction of Kaggle's exact rating formula, but they make a pure causal claim that removing R128 created the public-score jump untenable.

The fresh paired holdout is decisive for the mechanism question: no-R128 and full V42 completed all 40 games (seeds 9111-9115, v37/Flex/Thomas/Dmitrii, both seats), with `delta = 0` in every row. R128 did not alter a single action or final margin in this holdout. Together with the earlier 120-row panel (116 equal, 4 positive, 0 negative), this means R128 is effectively dormant on ordinary trajectories. It cannot explain the online score divergence through a broad strategic improvement. At most, it remains an untested tail-risk layer that could activate on rare market states.

The research implication is to separate two questions. First, estimate absolute policy quality with frozen-opponent paired replays and matched seeds; by that test no-R128 is behaviorally equivalent to V42 so far. Second, study online rating dynamics and opponent selection as a separate process; public score should be treated as a noisy, path-dependent measurement until both candidates have comparable opponent exposure. We should therefore keep collecting the queue and avoid another submission or a broad code change based on the 2700+ score alone.

The next useful experiments are low-risk and falsifiable: (1) continue the monitor until each submission has a substantially larger post-streak sample; (2) stratify online margins by opponent identity, episode order, and identifiable opponent score; (3) instrument V42's R128 counters on local stress scenarios to find whether it can ever change an action; and (4) finish a complete paired panel for the step-648 sale-order/merge prototype before considering any V42Pro promotion. The validated V42 route selector and opening policy remain the baseline; no-R128 is an observational comparison candidate, not yet an evidence-backed replacement.
