# Candidate v48_adv20_h10 — beats adv20

## Artifact

- Archive: `candidate_v48_adv20_h10.tar.gz`
- archive SHA-256: `f0d541ce1d65ec5fdc314c3555604e899c9febca12fa53da18cdac0b3784637d`
- main.py SHA-256: `dd1c2b1fef2893403e67d22e0d43fa68deffdd6e4109474e9061051a5e581c7f`
- Recipe: V48 chassis + attack 5 + `_ADV_LOOK=20` + R37 sale-reservation horizon 10
  (`if 288 <= step < 696: _R37_HORIZONS[player] = 10`).
- Runtime: 1438 callbacks, max 48.3 ms, 0 over the 1 s actTimeout; official loader verified; self-play exact tie.

## Evidence vs adv20 (the submitted baseline)

| Gate | adv20_h10 | adv20 |
|---|---:|---:|
| 120-game loss-biased online pool | 96W/24L (80.0%) | 95W/25L (79.2%) |
| 207-game full online corpus | 182W/24L/1T (88.2%), mean +1548 | 180W/26L/1T (87.2%), mean +1526 |
| fresh 16-game corpus | 12W/4L | 12W/4L |
| h2h vs adv20 (64 seeds) | 5W/5L/118T (neutral) | - |
| 10-family field panel | 1272W/8L | 1272W/8L |

The horizon 5..12 range is a plateau at 96W/24L on the 120-game pool, all above
adv20's 95W/25L; 10 was selected (best mean on the full corpus).

## Search context

Knobs swept this round on the online snapshot oracle: LOOK {3..32}, attack
{0,3,5}, wool caps {8,16}, tetsutani demand conditionals, _ADV_BOOK /
_ADV_SUBTRACT_DEBTS / _ADV_PROTECT, _ADV_FROM {96,144,240}, R37 horizon
{4,5,6,7,8,10,12}, strawberry->carrot and cow-heavy structural edits. The R37
horizon was the only one that improved the real pool without a regression.

## Not submitted

Per instruction, no submission was made.
