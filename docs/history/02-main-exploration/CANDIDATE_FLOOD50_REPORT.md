# Candidate flood50 - farm2945 + mirror-flood layer

## Artifact

- Archive: `farm2945_dev/candidate_flood50.tar.gz`
- archive SHA-256: `8a221e2c1a83ff4211a5bb118ff237d72dba6ed42e21dd7800dada71f854c178`
- main.py SHA-256: `07b5dbb4ace9ed7c079d32e3a8f0d82c001926aac1d440e3abf06f886a8d4e8d`
- Base: Thomas "The 2945 Farm" (V39 chassis + RACE / RACEGATE / RACEPX / carrot /
  herd / overflow layers), unmodified except two constants turned into a
  per-step policy described below.
- Runtime: 1438 callbacks/game, max 68 ms vs 1000 ms actTimeout. Healthy on the
  local kaggle-environments 1.32.7 engine.

## The change (mirror-flood)

farm2945 refuses to pull sales forward once an item's quote is at or below its
base price (`V9_RACEGATE_MARGIN = 0`, `V9_RACEPX_MARGIN = 0`). In an exact
self-mirror this makes both copies hold identical lots and the game collapses
to a tie (plus tiny seat-order noise). flood50 lowers both margins to **-100**:
it keeps reserving/lead-selling while the book is up to $100 below base, so our
lot clears before the mirror's identical lot, at a pre-glut price.

Guard rail: items quoted below **50% of base** are still left to the tape
schedule (absolute price floor). This stops $1-9 dump cascades without costing
the mirror edge. Nothing else changes; the opening stays farm2945's
round-trip-proof `[BUY 13, BUY 30, SELL 30]`.

## Evidence

### vs farm2945 itself (exact mirror)

| Seeds | Result | Mean margin |
|---|---:|---:|
| 24 worlds (screen) | 38W/10L/0T, 79.2% | +544 |
| 64 fresh worlds (confirm) | 98W/30L/0T, 76.6% (bootstrap 75.0-78.1%) | +380 |

The few big negative margins are world-intrinsic seat knife-edges: base-vs-base
already swings +-5k/10k on those same seeds; they are not caused by the flood.

### vs the Ahmed lineage mirrors (32 fresh worlds)

| Rival | Result |
|---|---:|
| v47base | 62W/2L/0T, 96.9%, mean +3378 |
| v48base | 62W/2L/0T, 96.9%, mean +3288 |
| v49base | 62W/2L/0T, 96.9%, mean +3357 |

Base farm2945 scores 92.2% against these three (118W/10L on 64 worlds), so the
flood improves the Ahmed-mirror matchups too, not just the self-mirror.

### 293-game real online-opponent corpus (fixed-tape replay)

| Agent | W/L | Pts | Mean margin |
|---|---:|---:|---:|
| flood50 | 247W/46L | 84.3% | +3598 |
| farm2945 base | 236W/57L | 80.5% | +3434 |
| v49_noguard | 233W/60L | 79.5% | +1138 |
| adv20 (online best) | 222W/70L/1T | 75.9% | +791 |

Flip matrix vs base: 15 base-losses turned into wins, 4 base-wins turned into
small losses (-88..-411). Net +11 wins.

### Head-to-head vs current submissions (32 fresh worlds)

- vs adv20: 60W/4L (93.8%), mean +3679
- vs v49_noguard: 60W/4L (93.8%), mean +3596

### 10-family public field (64 worlds x 2 seats per family)

q25 128W/0L, v45 128W/0L, v46 120W/8L, v37 128W/0L, seyit 128W/0L,
pipe7 128W/0L, pipe8 128W/0L, martsmart 120W/8L, reactive7 128W/0L,
beyond 124W/4L. Total 1260W/20L.

The v46/martsmart/beyond losses are inherited from the farm2945 base, not
caused by the flood: on the same worlds base-vs-v46 is 3L/1W and
base-vs-beyond is 3L/3W with the same losing seeds. adv20's lineage is
stronger on this old public field (1272W/8L) but far weaker on the 293-game
recent online pool (75.9% vs flood50 84.3%), which is the better predictor of
current ladder opponents.

## Known tail

One pool opponent (episode-110581821) punishes any early-flood variant with a
~-21k cascade because perturbed prices flip farm2945's herd choice (SHEEP ->
GOOSE) in that world. Base loses the same game at -1.7k, flood50 at -21.7k, so
the rating outcome is unchanged (still 1 loss); the floor does not prevent this
particular cascade because it starts before prices fall below the floor. It is
1 of 293 games.

## Status

NOT submitted. Awaiting user authorization per instruction.
