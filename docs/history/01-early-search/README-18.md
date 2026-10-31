# guts agent

`main.py` is a standalone Kaggriculture agent. It opens with four MELON plots for their high one-time return, then fills available NW tiles with WHEAT cycles. Every turn it reads the own farm and private shed/seeds, sells stored products, buys required seeds, and assigns the farmer and any daily hired hands to nearest outstanding WATER, HARVEST, or PLANT tasks. Up to three hands are hired at the start of each day when cash permits. Movement is coordinate driven and locked quadrants are traversable while tile operations are only attempted on owned tiles.

The agent uses Python standard-library features only and has no opponent-state dependency. `agent(obs, configuration=None)` returns `farmer`, `hands`, and bounded `market` actions and can be packaged as a single file.

Round artifacts are in `round1/` and `round2/`; review notes and smoke records are in `REVIEW_ROUND1.md` and `REVIEW_ROUND2.md`.
