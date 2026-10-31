# Development test record

All tests use the installed official Kaggriculture engine and only built-in `pass`/`starter` opponents.

```text
python smoke_r1.py                         # 240-turn exploratory round 1, seed 9001/pass
python smoke_r2.py                         # 720-turn final smoke, seeds 9001/pass and 9002/starter
python -m py_compile main.py
```

Observed final rewards from `smoke_r2.py`:

| seed | opponent | guts money/reward | opponent reward | status |
|---:|---|---:|---:|---|
| 9001 | pass | 17,878 | 3,000 | both DONE |
| 9002 | starter | 17,747 | 3,421 | both DONE |

SHA-256: round1 `db1f4a5344c99a26e9e3bf08c4b3c8c7472a682f9099994fbb6ce70d62acdc22`; round2/final `1af1b93c72c174c008375fa5ebd1f9a935d0ec815cd1972341921988dcf55a1e`.
