# Q20/Q25 review (2026-09-17)

The latest paired panels were reviewed with the competition's W/L/T scoring in mind. The local engine reports cash margin, but leaderboard rating only observes the final win, loss, or tie.

## Evidence affecting selection

- `broad_q20_9016_9019.json`: against q50, Q20 changes six parent losses to wins and leaves one parent win unchanged; against q85 it leaves all outcomes unchanged (7 wins, 1 loss); against V37 it has one win-to-loss conversion in eight rows; against flex and Nathan it has no outcome conversion.
- `broad_q25_9016_9019.json`: Q25 has the same W/L/T conversions as Q20 on q50, V37, flex, and Nathan. Its q85 cash delta is weaker (mean -330.5, two negative rows), although no q85 outcome changes in this panel.
- `q20_actual_openings_9018_9021.json`: against the V44/custom opening lineage and single-buy-5, Q20 leaves every parent outcome unchanged (7 wins/1 loss against V44; 6 wins/2 losses against single-buy-5), despite a lower cash margin against V44.
- Direct Q20-vs-Q25 paired runs on seeds 9022-9023 (q50/q70/q85/V37) are ties in all 16 rows. Q20's cash is lower by 17-18 on q70 and 196-211 on q85; q50/V37 are identical. This means the two packages are strategically very close, with Q25 providing little independent outcome diversity.

## Decision implication

Q20 is the safer primary package: it converts the observed q50 losses and q70 ties in synthetic opening tests while preserving tested q85 outcomes, and its q85 margin is consistently positive. Q25 is acceptable as a second high-upside package, but its only distinction is a slightly larger opening quantity and a negative q85 cash tail; it should not be described as a proven universal improvement. The q20 seat-mix hedge has lower upside and is better kept as a fallback.

Both archives were healthy (720 steps, no stderr) and remain frozen. Submission command and URL rewrite are documented in `submit_kaggle_resilient.py`; use the kaggle-cli Python environment and submit only after the conditional two-candidate decision is accepted.
