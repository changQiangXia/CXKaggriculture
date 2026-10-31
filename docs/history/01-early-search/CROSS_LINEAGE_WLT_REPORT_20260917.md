# Q20/Q25 cross-lineage W/L/T audit (2026-09-17)

The strict paired harness was run with Kaggriculture local engine, 720 steps,
seeds 9022 and 9023, both seats, comparing each candidate against the V45
parent under the same opponent and seed. All rows completed 720 steps with no
stderr.

## Outcome conversion

For both `candidate_v45_q20.py` and `candidate_v45_q25.py`, all 16 rows across
`public_v37_pkg/main.py`, `ready_flex_v7/main.py`, `v44_extracted.py`, and
`nathan_cautious_final/main.py` were `W -> W`: the V45 parent won and the
candidate also won. There were no `W -> L`, `W -> T`, `L -> W`, or `T` rows.
Nathan is byte-for-byte behaviorally unchanged because these candidates only
alter the opening wrapper.

Cash deltas are therefore diagnostic only. Q20 deltas by family were V37
`[-2270,-2270,+164,+164]`, flex `[-3686,-3686,-1379,-1379]`, V44
`[-1178,-1178,-1166,-1166]`, and Nathan `0`; Q25 has the same values except
V44 `[-1072,-1072,-1073,-1073]`. The V44 candidate margins remain positive
(Q20 `122/134`, Q25 `228/227`), so these negative deltas do not change the
result class.

An additional Q25 opening-wrapper panel (`opp_single5.py`, `opp_q19.py`, seeds
9024/9025) likewise had no outcome conversion: single5 stayed at 2W/2L,
q19 had L->L twice and W->W twice. Q25 improved cash margin in every q19 row.

The Q20 V37 fresh panel (seeds 9020--9023) had 8/8 `W -> W`; deltas were
`-3156,+684,-2270,+164` by seed (seat duplicates).

These panels cover known lineages and synthetic opening wrappers; they do not
prove leaderboard improvement against unseen strategies. Since Q20/Q25 only
change the opening quantity, evaluation against lineages that do not trigger
the opening wrapper is expected to be behaviorally identical or nearly so.
