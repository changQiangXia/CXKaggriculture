# Kaggriculture engine parity audit

Date: 2026-09-12. Online replay metadata reports `module_version=1.32.7`; installed local `kaggle-environments` is `1.25.9`. I fed both recorded agents' actions from each replay into the installed simulator, using `replay.info.seed` as the configuration seed and comparing every semantic observation after each transition. Replay index 0 is reset state; action at index `i` is applied from state `i-1` (the replay records post-interpreter state at index `i`). Runtime-only `remainingOverageTime`, action/info fields, and framework's absent shared `step` field were normalized away.

Results:

| replay | seed | states | first divergence | local rewards | online rewards |
|---|---:|---:|---|---|---|
| 108204611 | 438383292 | 720 | none | 94949, 96714 | 94949, 96714 |
| 108205627 | 324176619 | 720 | none | 75995, 73869 | 75995, 73869 |
| 108206966 | 1022152157 | 720 | none | 90323, 90323 | 90323, 90323 |
| 108208668 | 672671802 | 720 | none | 59264, 59138 | 59264, 59138 |

The complete machine-readable output is [installed_multi.json](installed_multi.json), and the reusable harness is [reproduce_recorded_actions.py](reproduce_recorded_actions.py). A single replay audit is also in [installed_parity.json](installed_parity.json).

Conclusion: despite the package metadata difference, the installed Kaggriculture interpreter is behaviorally identical on four independently seeded online replays, including all market/farm/private state transitions and final rewards. The lower h5 score is therefore not explained by local-vs-online simulator drift for these trajectories; local panel outcomes remain meaningful for action-policy comparisons. This does not prove byte identity or rule identity for every possible state, but it rules out a general engine mismatch as the cause of the approximately 200-point gap.
