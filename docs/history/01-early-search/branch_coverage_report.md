# V219/V37 fertilizer branch coverage (EXP-176)

Date: 2026-09-12  
Scope: read-only branch audit of `public_v37_pkg/main.py`; no candidate or monitor changes and no Kaggle submission.

## Call-path audit

The price-gated branch is at [public_v37_pkg/main.py](/root/autodl-tmp/public_v37_pkg/main.py:1289):

```python
fertilizer = bool(
    _V219_FERTILIZE and day in (24, 27)
    and obs['market']['prices']['FERTILIZER'] <= 30
)
```

The request function is called at line 1414 (`action = _v219_request(...)`) in the current 2355-line package. `_V219_PARENT` is captured at line 1219, before the V219 wrapper is installed. Subsequent wrappers preserve this call through the global `_v219_request` lookup: the final exported agent is wrapped at lines 1709, 1916, 2100, 2247, 2312, and 2355; the R53 labor wrapper invokes its parent at line 2350. A source search finds only the definition of `_v219_request` and its call (plus the temporary diagnostic wrapper used for this experiment); the production source does not replace it later. Thus the V219 gate is reachable through the final V37 callable when qualification succeeds.

The V219 entry also has an earlier qualification gate at line 1391 (`state['eligible']` is set from `_v219_qualifies` at line 1390 and checked at line 1391 and the function returns before day 18 when false). This explains why a price threshold edit can be behaviorally inert on seeds that never qualify.

## Instrumented runs

I loaded an instrumented copy of V37 and an isolated `ready_flex_v7` opponent, then ran 720-step episodes in both seat orders for seeds 9001 and 9005. Instrumentation only counted calls and copied returned actions; it did not alter any action or state. All four games completed with `env.done=True`, 720 steps, both statuses `DONE`.

| seed | seat | V219 qualification at step 432 | `_v219_request` calls | gate condition true | returned action changed | added FERTILIZER buy orders | FERTILIZE commands observed in returns | R51 control calls / changed | terminal rewards (V37, Flex) |
|---:|---:|:---:|---:|---:|---:|---:|---:|---|
| 9001 | 0 | true | 287 | 48 (24 on day 24, 24 on day 27) | 12 | 2 orders (+10 units each) | 41 | 719 / 57 | 109922, 108137 |
| 9001 | 1 | true | 287 | 48 (24 + 24) | 12 | 2 orders (+10 units each) | 41 | 719 / 57 | 109922, 108137 |
| 9005 | 0 | false | 0 | 0 | 0 | 0 | 0 | 719 / 0 | 117284, 104623 |
| 9005 | 1 | false | 0 | 0 | 0 | 0 | 0 | 719 / 0 | 117284, 104623 |

For the qualifying 9001 run, the two actual price-triggered request changes were:

- step 577 (day 24, hour 1, fertilizer price 11): existing market queue gained `BUY_PRODUCT FERTILIZER 10` and two `HIRE` orders;
- step 650 (day 27, hour 2, fertilizer price 2): existing queue gained `BUY_PRODUCT FERTILIZER 10` and three `HIRE` orders.

The other ten changed returns are ordinary V219 day request/commitment changes (days 18–23, 25–26, and 28–29), not fertilizer-price additions. The 41 `FERTILIZE` command observations are downstream worker action returns after the branch has committed; they are not 41 independent purchases.

At qualification time, seed 9001 had `NW, NE, SW` unlocked and passed the V219 structural checks. Seed 9005 had `NW, NE, SW, SE`; `_v219_qualifies` returned false, so its V219 request path was never entered. Its initial fertilizer price was 34, while 9001's was 38; these initial prices are diagnostic only because the relevant gate is evaluated on days 24 and 27.

## Interpretation

The branch is real and reachable, but only after the strict V219 qualification gate. In the instrumented callback, the downstream R53 labor selector was called 14 times on 9001 (fertilizer argument true 4 times, non-null assignment 3 times, no assignment 1 time); the corresponding counts were zero on non-qualifying 9005. The R51 input controller still ran 719 callbacks on each episode, changing 57 actions on 9001 and none on 9005, but this controller is a separate post-V219 layer and does not replace the price gate. On a qualifying episode, the price condition was true on all 48 request callbacks for days 24 and 27, yet it caused only one market mutation per day because the per-day request guard and worker commitment state suppress repeats. The threshold `<=30` therefore controls two concrete +10-unit purchase decisions in seed 9001. On the non-qualifying seed 9005, changing that threshold cannot affect behavior.

This coverage does not establish a win-rate improvement and is not a submission recommendation. The original EXP-175 terminal-reward JSON was copied unchanged to [local_evals/exp175_results.json](/root/autodl-tmp/local_evals/exp175_results.json) (SHA-256 `d34b314018baed89b2ed3d9bed0c300a4febb6a1098668ef0cd6d32a3139d121`). Raw branch details are in [local_evals/branch_coverage_detail.json](/root/autodl-tmp/local_evals/branch_coverage_detail.json), qualification probes in [local_evals/qualification_detail.json](/root/autodl-tmp/local_evals/qualification_detail.json), and the diagnostic runner is `/tmp/run_branch_detail.py`.

## Concurrent monitor check

The existing monitor was not modified. At this audit it remained alive as PID 30161 with `--interval 600`; its log had collected new V37 tie episode `108071579` and continued watching both active submission IDs. A direct API check at this time returned active IDs `56178383` and `56176848` (public scores `2567.0` and `2571.1`; scores are recorded only as state, not used as the candidate gate).
