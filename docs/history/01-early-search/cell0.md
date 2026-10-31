# Beyond 48-0 · 128/128 Worlds with 95% CIs | Market Micro-Edges + the Traps That Faked Them

**TL;DR.** This is Ahmed Berat Özer's public **[V43 "Recovering Lost Harvests"](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v43-recovering-lost-harvests)** (Apache-2.0 — it does all the actual farming here) with **four added rules, none of which touch the farm plan**. Every one of them exploits the same single fact about the market, explained in section 1.

| tier | opponents | result |
|---|---|---|
| 24 seeds × both seats | V45 / aurax7 v6 | **48-0** (+2,384) |
| 24 seeds × both seats | V44 / V43 | 47-1 (+1,257) / **48-0** (+1,282) |
| stress clones (counters I built against myself) | open78 / fast24 / open70_h24 | 48-0 / 47-1 / 48-0 |
| **64 independent worlds × both seats** | V45 | **128-0**, +2,087, bootstrap 95% CI **[+1,950, +2,240]** |
| official `kaggle_environments` runner | V45 / V43 | 16-0 / 16-0, 0 errors, 0 slow turns |

The half I think is worth more than the agent is everything after section 5: **the full experiment log including what failed**, the acceptance suite that stopped me shipping three of those failures, and **two measurement traps that produced completely convincing wrong numbers**. One of them told me a candidate had won by +167,366.

Runs on the standard Kaggle image. No datasets, no GPU, no internet.

> If the acceptance suite or the traps save you a day, an upvote helps. Please also upvote [V43](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v43-recovering-lost-harvests) — this notebook is a thin shell around it.
