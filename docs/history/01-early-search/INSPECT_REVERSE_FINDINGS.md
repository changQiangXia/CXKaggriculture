# Reverse/replay candidate inspection

The phrase “reverse” most plausibly refers to the **replay** route candidate (likely a typo): `ready_thomas_v6.tar.gz` / `thomas_candidate_v5.tar.gz`. Both archives unpack to a single `main.py`; their payloads are byte-identical (SHA256 `10f4982e85c0596055e740cb45f4f663fae64d003b5ee7cd163314714619a4d6`). Archive SHA differ only due tar metadata (`ready_thomas_v6`: `8da95498...`; `thomas_candidate_v5`: `79c815c1...`).

Evidence from `READY_CANDIDATES.md`: Thomas replay router uses public replay routing, shop-aware schedule selection, state recovery and terminal handling. Isolated seed-0 starter runs finish `DONE` at `183962/3504` and `3633/151868` (candidate seat 0/1); seed-0 self-play `66496/67254`. Public notebook reports ~95.5% holdout win rate across 689 replays, 32 seeds, both seats (not a guarantee).

Other “ready” candidates are unrelated to replay wording: `ready_dmitri_v6.tar.gz` (herd-safe sale window; seed-0 starter `180394/3510`, self-play `69506/69506`) and `ready_flex_v7.tar.gz` (sheep overlay disabled; local Thomas 3/3, Dmitrii 2/3 on seeds 0–2). `public_v37_candidate_replay.tar.gz` is simply an exact byte copy of submitted V37 (`public_v37_candidate.tar.gz`, SHA `4babc9e9...`), not a distinct reverse strategy.

No submission was made during this inspection. User phrase should be clarified as referring to `ready_thomas_v6` if they mean replay router; retain existing no-resubmit constraint.
