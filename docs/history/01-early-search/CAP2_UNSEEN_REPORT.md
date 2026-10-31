# h5sim96_cap2 unseen-seed validation

- Candidate: `h5sim96_cap2.py`
- Opponent: frozen `public_v37_pkg/main.py`
- Seeds: 12001-12010 and 13001-13005 (30 games, both seats)
- Environment: Kaggriculture, 720 steps, kaggle-environments 1.25.9

## Results

`30/30` wins, `0` losses, `0` ties. Mean margin `+1873.7`, median `+1586`, min `+889`, max `+3687`. All games terminated at 720 steps with both agents `DONE`; no runtime errors or stderr observed. Most games are seat-symmetric; two seeds (12003, 12007) show small seat-dependent variation, consistent with shared order tie-breaking.

Per-seed margins (seat 0, seat 1):

```
12001 +925, +925
12002 +2456, +2456
12003 +3687, +3441
12004 +1954, +1954
12005 +1943, +1943
12006 +1467, +1467
12007 +1147, +889
12008 +2187, +2187
12009 +2534, +2534
12010 +1352, +1352
13001 +1586, +1586
13002 +1153, +1153
13003 +1503, +1503
13004 +1231, +1231
13005 +3233, +3233
```

This extends the earlier 16/16 wins on the 8-seed V37 panel with an independent 15-seed block. It supports cap2 as a robust local candidate against V37, but does not establish improved online Bradley–Terry rating or performance against adaptive high-rated opponents. No submission was made.
