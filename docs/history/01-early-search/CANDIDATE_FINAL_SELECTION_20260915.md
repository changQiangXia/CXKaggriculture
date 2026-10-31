# Final internal candidate selection (2026-09-15)

## Selected two

### 1. no-R128 V42 — primary

- Archive: `/root/autodl-tmp/no_r128_v42.tar.gz`
- Focused panel: 120/120 games complete, four opponents, both seats, multiple seeds.
- Mean margin: `+19,767.7`; minimum margin: `+1,416`.
- Dedicated paired holdout against complete V42: 40/40 rows had delta `0`.
- All recorded rows were 720 steps and `DONE`; no stderr was recorded.
- Reason for selection: strongest evidence and lowest observed regression risk. The online score difference is not treated as proof of a strategic gain, but this candidate is suitable as the first submission candidate after authorization.

### 2. no-R127 V42 — secondary

- Archive: `/root/autodl-tmp/incubated_candidates/v42_ablations/no_r127/candidate_C_no_r127_v42.tar.gz`
- Focused panel: 120/120 games complete, four opponents, both seats, multiple seeds.
- Mean margin: `+19,755.7`; minimum margin: `+1,416`.
- Per-opponent means/minima: v37 `+29,847.7/+9,849`; Flex `+32,035.5/+13,082`; Thomas `+8,858.7/+1,416`; Dmitrii `+8,281.1/+5,579`.
- All recorded rows were 720 steps and `DONE`; no stderr was recorded.
- Reason for selection: complete four-opponent panel and no observed negative margin; it is a clean second wrapper ablation with slightly better aggregate results than no-R124 and more complete evidence than merge648 or highscore-terminal.

## Not selected for the two-slot set

- `merge648 V42`: 30 rows (20 smoke + 10 Flex holdout), all delta `0`, but Dmitrii coverage and full paired tail audit are missing. The high-score tape study also found that elite tapes frequently use fragmented/interleaved SELL, so a merge should not be promoted without stronger evidence.
- `highscore-terminal V42`: only 4 v37 rows (two seeds, both seats); all delta `0`, but the wrapper did not activate in those ordinary games and there is no multi-opponent evidence. It remains an incubating hypothesis.

## Submission decision

These are the two most defensible candidates for a future authorized submission round. This document does not authorize upload or submission. Before any actual submit, rerun the required paired validation with common seeds, v37/Flex/Thomas/Dmitrii, both seats, 720 steps, DONE, zero stderr/timeout, latency and tail metrics, then obtain explicit user authorization.
