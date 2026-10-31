# V42 loss replay 108989503

Submission 56234455 (the submitted V42) lost narrowly to opponent `cg`: 122461 versus 122689, a gap of 228. Both agents completed all 720 steps. The V42 log has 719 calls with mean duration 1.376 ms, median 0.720 ms, maximum 304.3 ms, and empty stdout/stderr.

The opponent used a materially different policy from the opening step. At step 1 V42 issued `BUY_PRODUCT WHEAT 5`, `BUY_PRODUCT WHEAT 10`, `SELL WHEAT 60`; `cg` issued `BUY_PRODUCT WHEAT 7` and two hires. The first action divergence is therefore step 1 and remains throughout the game. Around step 648 V42 sold fertilizer/wheat while `cg` had no market orders, and at steps 649-650 `cg` used a large wheat sale plus fertilizer purchases and an early milk sale. The terminal phase also differed: V42 used the terminal liquidation tape while `cg` sold only its remaining small inventory. This is a close adaptive-opponent loss, not an exception or timeout.

Because the local four-opponent panel does not contain `cg`, this replay is useful as an out-of-panel robustness sample but is insufficient to justify changing the opening or route policy. It should be used to design a future opponent-adaptive holdout, rather than tuning to this single game.
