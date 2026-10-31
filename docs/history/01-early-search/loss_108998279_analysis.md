# V42 loss replay 108998279

V42 (seat 1) narrowly lost to `whm8016` (89768 versus 89773, −5). Both agents completed 720 steps. The V42 log contains 719 calls, mean 2.265 ms, median 1.020 ms, maximum 430.0 ms, and no stdout/stderr output.

Only three action steps differ: 302, 528 and 677. At step 302 the opponent used `PLANT WHEAT` while V42 used `DIG`; at step 528 the opponent prefixed a one-unit WHEAT sale before `SELL MILK 9`; at step 677 the opponent used `BUILD_COOP` while V42 used `DIG`. All market prices and the later terminal sales are otherwise aligned. The five-point gap is therefore a tiny tie-break caused by a different tactical field action and one-unit sale ordering, not a route-selector, opening, resource-layer, or runtime failure. This is an out-of-panel adaptive-opponent sample and does not justify changing V42.
