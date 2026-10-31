# Loss replay 108996168

Submission 56209639 lost to the opponent 102358–110215 (−7857). The own agent log contains 719 calls, median 0.719 ms, mean 1.361 ms, max 313.8 ms, with no stdout/stderr output. The replay completed all 720 steps.

This is not a V42 loss: the own opening at step 1 is the v37 policy (`BUY_PRODUCT WHEAT 13`, `BUY_PRODUCT WHEAT 30`, `SELL WHEAT 30`). The major divergence is concentrated around step 648 and step 650. The opponent sells `STRAWBERRY 21, WHEAT 3, FERTILIZER 3, EGG 1` at step 648, while the own side issues extra fertilizer buys/hire and a different strawberry/wheat mix; by the final step the opponent has 8 EGG/4 WOOL/4 CARROT/2 WHEAT versus the own 4 EGG/4 WOOL/3 CARROT/2 WHEAT/1 FERTILIZER sale. This indicates that submission 56209639 is an older non-V42 policy with a production/resource mismatch, not evidence against the submitted V42 route selector. It is retained as a monitored historical loss sample only.
