# cap2 latest loss review (2026-09-14)

The monitor collected two new cap2 losses (`56209639`): episodes `108600815` and `108599773`. Both completed normally; no runtime errors or stderr.

## Observed state

- `108600815`: our reward `86419`, opponent `87615` (`-1196`). At step 623 the shed was full (100): WHEAT 46, STRAWBERRY 21, FERTILIZER 14, MILK 9, EGG 6. MILK price fell from 198 at step 360 to 32 at step 623 and 1 at step 695.
- `108599773`: our reward `97697`, opponent `103651` (`-5954`). At step 623 the shed was full (100): WHEAT 51, STRAWBERRY 20, FERTILIZER 13, MILK 6, EGG 5. MILK remained high (214 at step 623, 229 at step 695), while WOOL collapsed to 1.

Both losses had no carried inventory at steps 623 or 695, so a simple carried-capacity guard cannot explain or guarantee a fix. The first loss has a severe MILK price collapse; the second has high MILK but a WOOL collapse, indicating shared-market ordering and product-specific demand, rather than one universal MILK threshold.

For `108600815`, MILK SELL turns in the ordinary window begin at 308, 318, 320, 338–340, 361, 371; opponent begins at 309, 318, 320, 338–340, 361, 371. For `108599773`, ours begins at 308 while opponent begins at 311, then schedules largely coincide. Therefore “always sell MILK earlier” is not supported: the second loss already sells earlier and still loses.

## Candidate implication

The next useful experiment must condition on the *joint* visible market state (MILK/WOOL/STRAWBERRY prices and inventory) and current route obligations. A single-product unconditional lead is rejected. No new candidate is authorized or submitted from this review.
