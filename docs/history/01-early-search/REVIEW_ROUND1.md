# Round 1 review

Round 1 draft (`round1/main.py`, SHA-256 `db1f4a5344c99a26e9e3bf08c4b3c8c7472a682f9099994fbb6ce70d62acdc22`) was reviewed against the official engine action order and a 240-turn smoke run (seed 9001, opponent `pass`). It completed without runtime errors but ended at $2,999 and had four unused melon seeds. The crop selector switched from MELON to WHEAT as soon as seeds were bought, so melons could never be planted. The task priority also harvested before watering, losing the final one-time-crop watering bonus.

Corrections for round 2: choose MELON while fewer than four melon plants exist (seeds already purchased do not switch the planting crop), and prioritize WATER before HARVEST on a tile. No opponent private state or fixed action tape is used.
