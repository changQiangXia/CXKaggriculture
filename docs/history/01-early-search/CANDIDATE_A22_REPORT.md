# Candidate v48-a22 (anti-mirror) — validation report

## What changed vs V47

Single change: the step-1 opening attack quantity `_OPEN_ATTACK` 30 -> 22.
Everything else is byte-identical to Ahmed's public V47.

## Artifact

- Archive: `candidate_v48_a22.tar.gz`
- main.py SHA-256: `3ad8b871a35c09158551b62846d9d12b09d301630233bd5ff9ce902e801e9ff2`
- archive SHA-256: `68152256d9c9a4a44ecfff94918b679ccd330dbd664558853ba8340ac29b8b1b`
- Runtime: 1438 callbacks, max 54.6 ms, 0 over the 1 s `actTimeout`; official loader verified.

## Anti-mirror head-to-head vs V47 base

| Seeds | W/L/T | Mean margin | Worst |
|---|---:|---:|---:|
| 302001-302064 | 124/4/0 | +121.5 | -566 |
| 303001-303064 | 124/4/0 | +73.6 | -12255 |
| Total 128 | 248/8/0 (96.9%) | +97.6 | -12255 |

Attack-size sweep vs base (64 seeds each): 5..8 and 22..25 are safe zones;
10..20 is a bad zone (6 losses, -4695 tails); >=40 self-harms catastrophically.
22 was chosen for the highest combined mean with the same W/L as the other safe-zone sizes.

## Field regression (10 families, seeds 302001-302064, both seats, 128 games each)

| Family | v48-a22 W/L/T | win% | mean | worst |
|---|---:|---:|---:|---:|
| q25_active | 128/0/0 | 100.0 | +2225.9 | +313 |
| v45 | 127/1/0 | 99.2 | +2342.9 | -134 |
| v46 | 128/0/0 | 100.0 | +1941.1 | +679 |
| v37 | 126/2/0 | 98.4 | +4498.0 | -1446 |
| seyit2820 | 115/13/0 | 89.8 | +609.3 | -1970 |
| pipe7 | 126/2/0 | 98.4 | +2178.3 | -1443 |
| pipe8 | 128/0/0 | 100.0 | +2016.3 | +577 |
| martsmart | 128/0/0 | 100.0 | +1777.4 | +502 |
| reactive7 | 125/3/0 | 97.7 | +1719.5 | -1399 |
| beyond | 127/1/0 | 99.2 | +1822.9 | -106 |

Total: 1258 W / 22 L over 1280 games (98.3%).

Same panel for the verbatim V47 base: 1251 W / 29 L (97.7%).
v48-a22 gains +7 wins and -7 losses on the field while also beating the base
head-to-head 96.9% of the time (248/8). Only seyit2820 is slightly worse
(115 vs 117 wins), the donor of several of V47's layers.

## Interpretation

- vs the current active best (Q25, 2578.6): 128/128 wins, worst +313.
- vs the historical best (V37, 2724): 126/128 wins, mean +4498.
- vs V47 mirrors: converts ~97% of mirror ties into wins; the remaining tail is
  world-dependent and bounded.
- Local evidence cannot guarantee an online rating, but this is the strongest,
  most-differentiated candidate the workspace has produced.
