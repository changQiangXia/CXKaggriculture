# Q20/Q25 confidence audit (independent panel, 2026-09-17)

## Scope

This audit asks whether either frozen opening candidate can be called a high-confidence improvement over the V45 parent. It does not authorize or perform a Kaggle submission. The candidates differ from V45 only in the standard wheat round-trip opening (`_OPEN_UNITS=20` or `25`).

## Independent fresh panel

`strict_paired_eval.py` was rerun for Q20 against `opening_q70.py`, `opening_q85.py`, and `public_v37_pkg/main.py` on previously unused seeds `9040, 9041, 9042`, both seats. Candidate and parent use the same world and opponent for each pair. All 36 games completed 720 steps with `DONE` status and empty stderr.

| family | rows | mean cash delta | p10 | worst | positive rows | negative rows | outcome regressions |
|---|---:|---:|---:|---:|---:|---:|---|
| q70 | 6 | +1340.0 | +1340.0 | +1340.0 | 6 | 0 | none; parent ties become candidate wins |
| q85 | 6 | +58.67 | +58.0 | +58.0 | 6 | 0 | none; parent and candidate remain wins |
| v37 | 6 | -4084.33 | -8137.0 | -8137.0 | 0 | 6 | seed 9040: parent W (+6014) becomes candidate L (-2123), both seats |

The v37 rows are not just harmless cash variation. On seed 9040, the candidate changes a parent win into a loss. Seeds 9041 and 9042 remain wins but with lower margins. Equal weighting by family gives mean delta `-895.22`; pooled p10 is `-4398.30`. The machine and runner were healthy, so this is a strategy interaction rather than a runtime artifact.

Raw paired rows and hashes are in [q20_confidence_9040_9042.json](q20_confidence_9040_9042.json).

## Confidence decision rule

For a candidate to be labelled **high confidence** for a new submission, require all of the following:

1. At least three fresh seeds per opponent family, both seats, and at least four independent families (including one older non-V45 lineage).
2. No `W -> L` or `W -> T` conversion in the complete paired panel.
3. Equal-family mean delta positive and a family-balanced lower bootstrap bound above zero, or a clearly positive W/L/T conversion rate with no negative family tail.
4. Every run healthy (`DONE`, 720 steps, empty stderr).
5. Evidence from at least one engine/version or online replay cohort beyond the synthetic opening family, with the local/online engine difference disclosed.

Q20 fails criteria 2 and 3 in this independent panel despite strong q70/q85 behavior. Existing Q25 evidence has the same known V37/flex sensitivity and therefore cannot be promoted to high-confidence status without a fresh panel that clears these gates. A high online score by itself is not enough because the rating is dynamic and current public games are not a paired comparison.

As a direct check rather than an inference from the older report, Q25 was rerun against V37 on the same fresh seeds and seats (`q25_confidence_v37_9040_9042.json`). It produced exactly the same six deltas (`-8137, -8137, -2796, -2796, -1320, -1320`), including the same seed-9040 `W -> L` conversion. Thus the negative tail is shared by both quantity variants on this lineage.

## Recommendation

Keep Q20 and Q25 as exploratory/high-upside archives, but describe them as directional candidates only. Do not claim that either is likely to exceed the historical V37 score `2724.0` with high confidence. Continue searching for a mechanism that retains the q70 upside while eliminating the v37 negative tail; if no such candidate clears the gate, preserve the strongest existing submission rather than replacing it.
