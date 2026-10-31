# V42 candidate set (local validation, 2026-09-15)

## Candidate A: no-R128 V42

Artifact: `no_r128/main.py`; archive: `/root/autodl-tmp/no_r128_v42.tar.gz`.

This keeps the complete V42 route selector, opening policy and terminal planner, while disabling only the outer R128 wrapper. The 120-game focused panel covers v37/Flex/Thomas/Dmitrii, 30 rows per opponent, both seats and multiple seeds. All rows completed 720 steps with DONE; candidate margins have mean 19,767.7 and minimum 1,416. The dedicated 40-game holdout against full V42 (5 unseen seeds × 4 opponents × 2 seats) had delta 0 in every row. No submission is authorized by this report.

## Candidate B: merge648 V42

Artifact: `merge648/main.py`; archive: `merge648/merge648_v42.tar.gz`.

This changes one identifiable mechanism: at step 648, duplicate WHEAT SELL orders are merged while preserving the rest of V42. Existing 20-game smoke (v37/Thomas, both seats, seeds 9001–9005) was all DONE/720 and had delta 0 against the corresponding V42 control. A further 10-game Flex holdout (seeds 9001–9005, both seats) was all DONE/720, stderr empty, max callback duration 1.199 s; observed final margins were all positive. The full four-opponent paired panel is incomplete, so this is an incubating candidate and is not eligible for submission yet.

## Decision

Keep both artifacts available for the next authorized validation round. Candidate A is the safer observational probe because its evidence is complete and shows parity with V42; Candidate B is the mechanism probe with limited additional coverage. Do not submit either artifact without explicit user authorization and a completed multi-opponent tail-risk audit.

## Candidate C: no-R127 V42

Artifact: `no_r127/main.py`; archive: `no_r127/candidate_C_no_r127_v42.tar.gz`.

This disables only the R127 priority wrapper while retaining the rest of V42. Its existing 120-game focused panel covers v37/Flex/Thomas/Dmitrii, both seats and multiple seeds; all games reached 720 steps and DONE. Mean margin is 19,755.7 and minimum margin is +1,416. This is an observational low-risk variant, not yet evidence of an improvement over V42.

## Side-by-side local evidence

| candidate | rows | opponents | all DONE/720 | stderr | mean margin | minimum margin | paired delta evidence |
|---|---:|---|---|---:|---:|---:|---|
| no-R128 | 120 focused + 40 V42 holdout | v37/Flex/Thomas/Dmitrii | yes | 0 | 19,767.7 | +1,416 | 40/40 delta 0 vs full V42 |
| no-R127 | 120 focused | v37/Flex/Thomas/Dmitrii | yes | 0 | 19,755.7 | +1,416 | focused panel; wrapper-only ablation |
| merge648 | 20 smoke + 10 Flex holdout | v37/Thomas/Flex | yes | 0 | see reports | +1,416 (smoke), +13,082 (Flex holdout) | 30/30 delta 0 vs full V42 |
