## 5. Edge 4 — the step-0 wheat round trip, and why 70 is the wrong size

The mechanism is Ahmed's, from his public V45 notebook: at step 0, replace V43's opening market list with a single round trip, `[BUY_PRODUCT WHEAT n, SELL WHEAT n]`. Your index-0 buy lifts the wheat price; because same-index orders quote at the same inventory, **your own sell at index 1 is unharmed but the rival's index-1 wheat buy is ~60 dearer** — which, for a V43-family rival whose day-0 plan is exactly funded, costs them one melon seed. On day 0. For the rest of the season.

V45 ships `n = 70`. I swept it against my own 70-unit build (paired margin, 8 seeds × 2 seats):

| n | 0 | 10 | 16 | 20 | 25 | 30 | 40 | 45 | 50 | 70 | 85 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| margin | −1,300 | +1,286 | +1,324 | +1,340 | +1,358 | +1,367 | +1,359 | +1,348 | **+1,328** | base | −1,318 | −1,345 |

Three regions, and the shape is the interesting part:

- **below ~10** — a cliff. The round trip is too small to break the rival's day-0 funding, so you pay the spread for nothing.
- **25–50** — a plateau. **The damage saturates**: once their funding is broken, breaking it harder buys nothing.
- **85 and above** — self-harm. You are now paying real spread on a large round trip for damage you already caused at 30.

I picked **50**, inside the plateau but with margin above the lower cliff rather than at its optimum, because the cliff is the dangerous side: the opponent pool changes, and a plateau edge that slips below 10 is worth −1,300.

This is the sort of thing that makes a published number worth re-measuring. 70 is not wrong — it is on the far shoulder of a plateau, and the shoulder is where an opponent shift hurts.
