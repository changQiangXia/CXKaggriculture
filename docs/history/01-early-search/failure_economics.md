# Current V43 failure economics (2026-09-16)

Source: `replays/episode-*-replay.json` and `episodes_latest.json`; only episodes whose own agent is `CHEN Xiang` are counted. Rewards and money are the engine observations, not inferred scores.

The 66 available V43 (submission `56260878`) replays contain 52 wins, 2 ties, and 12 losses (mean margin +16,813; worst −7,801). All inspected episodes run 720 steps and end `DONE`; the losses are economic/gameplay outcomes rather than runner failures.

| episode | opponent | margin | money margin at checkpoints | terminal behavior |
|---|---|---:|---|---|
| 109430701 | Sadettin Şamil Verdil | −7,801 | 0 (t0), −1,599 (t288), +5,006 (t576), −5,170 (t696), −7,801 (t719) | own ~86k SELL quantity requested versus opponent ~2k; many 1000-unit terminal SELL orders; no terminal recovery |
| 109438141 | LH-and-FPGA | −4,466 | +1,113 (t288), −4,324 (t576), −7,955 (t708), −4,466 (t719) | own ~118k SELL requested versus opponent ~1.6k; divergence predates terminal patch |
| 109477519 | FunLegendGaming | −2,221 | 0 through t144, −703 (t576), −2,219 (t672) | streams nearly identical to opponent; no terminal recovery |
| 109482442 | FunLegendGaming | −1,593 | 0 through t144, −896 (t576), −1,594 (t696) | streams nearly identical; no terminal recovery |
| 109519380 | WeAreFarmers | −1,349 | −1,125 (t432), −1,447 (t648), −1,689 (t696) | fertilizer salvage improves to −1,351 at t718 and −1,349 final (~+340), still loses |

The dominant pattern is opponent-dependent market/order economics. The Ahmed-derived policy routinely submits hundreds of SELL orders with quantities up to 1000 (requested quantities are not executed quantities). Against opponents with sparse or differently ordered market lists, list-index matching and price curves make those orders produce very different cash flows. In the mirrored FunLegend episodes, action counts and market quantities are effectively the same while final money differs by 1.6–2.2k, so the current gap cannot be attributed to a simple missing production action.

The step-717/718 fertilizer salvage is a narrow terminal intervention. It activates in some games, but observed benefit is at most a few hundred coins (clear example 109519380); losses generally begin hundreds of steps earlier. In 109430701 and 109438141 there is no meaningful terminal recovery. Therefore ten rounds of terminal-focused changes could not address the main failure surface: midgame sale/order pairing and opponent-sensitive cash divergence.

These observations are descriptive. Requested market quantities are not receipts, and replay logs alone cannot claim a causal counterfactual for changing the policy. A valid next experiment would replay identical seeds/opponent actions with the exact file loader and compare raw V43 against one market-policy change while recording executed quantities and cash by day.

## Nathan submission comparison

For submission `56257428` (Nathan package), 127 competitive episodes currently have 74 wins, 7 ties, and 46 losses. The deployed callable is the raw Nathan parent (the `_NC_PARENT` wrapper was bypassed by the Kaggle last-callable loader), so the purported five-round guard is not present online.

The largest available loss, episode 109437616 against `kobayasi`, ends −6,564. Cash is +726 at t288, −786 at t432, −5,285 at t576, and −6,823 at t672. At t432 Nathan submits `SELL EGG 4` while the opponent submits `SELL CARROT 3` and `SELL EGG 4`; at t576 Nathan submits two wheat sells while the opponent submits no market order. The terminal 1000-unit sell lists leave the gap essentially unchanged.

Other Nathan losses show the same timing: episode 109518675 reaches −1,849 by t576 and −2,964 by t672 (final −2,971); 109502811 reaches −1,512 at t648 and −2,235 at t672 (final −2,665); 109516516 reaches −1,514 at t648 and −2,281 at t672 (final −2,296). In these games later market lists are nearly identical, so the loss is already locked in by earlier order pairing and production/sales timing. This also explains why terminal-only modifications did not improve the online rating.
