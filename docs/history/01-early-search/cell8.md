## 6. The experiment log — including everything that failed

Published notebooks show what worked. The negatives cost the same GPU-hours and are more useful, so here they all are.

| # | idea | result | kept? |
|---|---|---|---|
| K0002 | market front-loading | 16-0 vs V43 (+476) | **yes** |
| K0003 | two-turn sale advance **alone** | no ladder win gain | no — only pays combined with front-loading |
| K0004 | + sale-reservation horizon 8 | 2,695 on the ladder | superseded |
| K0005 | + step-0 round trip at 70 | 2,597 | superseded |
| K0006 | round trip re-sized to 50, horizon 24 | 2,663 and climbing at the time of writing | **yes** |
| — | animal SHEEP↔COW substitution | −6 wins | no |
| — | feed sweeper | negative | no |
| — | route re-selection | negative | no |
| — | seed recovery | negative | no |
| — | pipe-4 C9 opening | +$1/game — noise | no |
| — | horizons 36 / 48 | lose mirror games to plain V43 | no |

### The one worth writing up: the season-long funding attack

If the step-0 round trip works *because* wheat is market-priced and the rival's plan is exactly funded, then repeating it on **every** turn whose tape buys wheat for feed should raise their feed cost all season and eventually starve an animal. It is the obvious generalisation. I built it (26–28 attacks per game) and it lost:

| attack size | result vs the unattacked build |
|---|---|
| 30 | **0-16** (−594) |
| 50 | **2-14** (−1,091) |

It also weakened the agent against V45 (+1,311 instead of +2,384).

**Why it fails:** the day-0 attack works because on day 0 the rival's purchase is *tightly funded*. By mid-season both farms hold enough cash that the same price bump changes nothing — so you pay the spread ~27 times and buy nothing. The edge was never "make wheat expensive"; it was "break a purchase that has no slack". Dropped.
