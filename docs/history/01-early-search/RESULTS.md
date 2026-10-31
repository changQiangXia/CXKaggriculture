# Thomas transfer probe results

Thomas's public state-router documents three layers (weed repair, clamp_sells, dead_stock) as +19/-0 over a 968-game bare-route panel. v37 already enables weed repair but has `clamp_sells` and `dead_stock` disabled in its final chassis settings. I generated isolated toggle builds from the frozen v37 source.

`dead_stock=True` versus v37 self-match, seeds 9001/9004, both seats:

| seed | seat | candidate margin | parent margin | delta |
|---|---:|---:|---:|---:|
|9001|0|-147|0|-147|
|9001|1|-147|0|-147|
|9004|0|1565|1581|-16|
|9004|1|-1597|-1581|-16|

All 8 game runs (candidate+parent) reached DONE at 720 steps, no stderr. This rejects dead_stock as a transferable layer.

`clamp_sells=True` initial six seed, seat0 deltas against v37 self-match: -10, +10, +10, +368, +86, +4; seat1 was symmetric. The effect is tiny and mixed. It is not stable evidence and requires no further sweep unless a new mechanism certificate is found.

`budget_guard=True` quick self-match (9001/9004, both seats): deltas -25,673 on 9001 and 0 on 9004; all DONE 720. Reject. The layer likely rewrites market buys incompatible with v37's route debt.
