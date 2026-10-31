# Submission receipt — candidate v48-a05

- Time: 2026-09-18 (UTC), authorized by the user ("交一次").
- File: `v48_candidate/candidate_v48_a05.tar.gz`
- archive SHA-256: `d931c3639529fb9346419863017e0aedc195e2374212d922cc0c13b81375a965`
- main.py SHA-256: `432d36822e1200016a49226a398be744c8d56e801b05106980867fe11ff0cf16`
- Kaggle result: `Successfully submitted to Kaggriculture`; 3 submissions remaining today.
- Diff vs the live a22: `_OPEN_ATTACK` 22 -> 5 only.

Local evidence (engine 1.32.7):
- vs V47 base: 248 W / 8 L over 128 games (96.9%) — identical to a22.
- Field panel: 1265 W / 15 L over 1280 games (98.8%) vs a22's 1258/22 (98.3%).
- No family regressed; seyit 117/11 (vs 115/13), pipe7 128/0 (vs 126/2),
  reactive7 127/1 (vs 125/3), v45 128/0 (vs 127/1).
- Runtime: max callback 50.1 ms, 0 over the 1 s actTimeout; self-play exact tie.

Active-window effect once processed: [a22 (56320959) + a05 (new ref)], v3 retired.
