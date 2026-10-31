# Candidate v48a5 — final validation report

## Artifact

- Archive: `candidate_v48a5.tar.gz`
- main.py SHA-256: `846ceacea81291dee4f30b1e922edbe83a1e5a188bbfa7d8dde1093f2612382a`
- archive SHA-256: `1b9540bd4d2d60912f7698a14fb9a12a68941324adceb8f570b729f4f3cf7caf`
- Base: Ahmed V48 (V47 + queue cleanup), single change `_OPEN_ATTACK` 30 -> 5.
- Runtime: 1438 callbacks, max 55.6 ms, 0 over the 1 s actTimeout; official loader verified; self-play exact tie.

## Evidence

- vs the live online candidate a05 (ref 56322157): **128 W / 0 L** over 64 worlds x both seats, mean margin +696, worst +58.
- Field panel (10 families, 64 worlds x 2 seats, 1280 games): **1276 W / 4 L (99.7%)**.
- vs V47 base (mirror pool): 126 W / 2 L (98.4%), mean +657.
- vs V48 base (mirror pool): 124 W / 4 L (96.9%).

## Explored and rejected this round

- pcond (price-conditional attack: 5 at price<=27, 22 at 28, 0 at >=29):
  field ties v48_a5 (1276/4); better vs V47 mirrors (128/0) but loses
  5 W / 123 L head-to-head against attack-5 variants. Not chosen.
- Attack-size matrix (9 sizes x 11 families x 64 games): all sizes win vs the
  field except the 12-18 trough; 5 and 22 tie on mirror W/L.
- Online loss replay diagnostic (13 games): pcond flips 3, improves 4, worsens 1.

## Online status at report time

- a05 (V47 + attack 5): 2717.2, climbing; a22 (V47 + attack 22): 2693.7.
- Historical account best: 2724 (V37 lineage, inactive).

## Not submitted

Per instruction, no submission was made; ~3 hours of online data collection is
in progress for a22/a05.
