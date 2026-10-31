# Round 2 review

Round 2 (`round2/main.py`, SHA-256 `1af1b93c72c174c008375fa5ebd1f9a935d0ec815cd1972341921988dcf55a1e`) was checked against the installed official `kaggriculture.py` engine. The agent emits the required `agent(obs, configuration=None)` dictionary, limits market orders to ten, uses only visible own private state plus public farm/market state, and keeps movement legal on locked tiles. It hires up to three hands daily, routes units to nearest WATER/HARVEST/PLANT work, sells shed stock, and waits for one-time crops to reach their max-yield day, reserves cash for seeds/land, and stops new planting on the final few days so harvested goods can be sold before season termination.

Development smoke tests (real engine, only allowed built-ins):

- seed 9001, 720 turns, opponent `pass`: player money 17,878; opponent 3,000; both DONE.
- seed 9002, 720 turns, opponent `starter`: player money 17,747; opponent 3,421; both DONE.

No replay, notebook, candidate agent, or opponent private state was inspected.
