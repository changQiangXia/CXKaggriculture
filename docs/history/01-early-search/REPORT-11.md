# V42 candidate report

Source: latest public Kaggle V42 notebook (`ahmedberatozer/kaggriculture-v42-production-that-fits-the-marke`), exported and isolated locally. This is a research candidate only; no submission was made.

## Evidence

- Paired against frozen v37: 20 screening games (10 seed × 2 seats), 20 wins, 0 losses, mean margin +27,389.6, minimum +9,849.
- Cross-opponent confirmation: 80 games (v37/Flex/Thomas/Dmitrii, 10 seed × 2 seats per opponent), 80 wins, 0 losses, minimum margin +1,416.
- Unseen holdout vs v37: 30 games (seed 9101–9115 × 2 seats), 30 wins, 0 losses, mean +30,686.3, minimum +18,382.
- Unseen holdout vs Flex/Thomas/Dmitrii: 90 games (15 seed × 2 seats × 3 opponents), 90 wins, 0 losses, minimum +385 (Thomas, seed 9113).
- All 200 games completed `DONE=True` with 720 steps; no engine errors were observed.

## Artifact audit

- `main.py` SHA-256: `728fdfb4405ba313f8b14ffb3e0f8eceaddcaa0de49e4835928d89aaf71467e9`
- `v42_pkg.tar.gz` SHA-256: `56a477595a04f3c48f6274aeef46c86aee4e1a7f368b88f94d0ea31d9a031f5c`
- Single `main.py` at archive root; Python syntax passes; imports are standard library only.

## Caveats

The holdout panel uses the locally available public opponents and is not a guarantee of live private leaderboard performance. V42 includes a larger, more complex wrapper stack than v37 and should receive a fresh-process timing check and public replay comparison before any submission. Submission requires explicit user authorization.

## Runtime audit

Independent fresh-process smoke games against `random`, `starter`, and `pass` used seeds 9101 and 9107 in both seats (12 games). All completed 720 steps with `DONE=True` and no exceptions. Wall-clock game time averaged 7.08 s and maxed at 7.35 s on the local engine; this is an end-to-end process measure, not an act-time limit measurement.

Per-call timing audit in a fresh process against `starter` (719 candidate calls, seed 9101): mean 0.933 ms, p99 7.279 ms, max 29.578 ms, zero exceptions. This leaves substantial margin below the platform's 1-second action timeout.
