# EXP-175 preliminary screening

The candidate changes only the V37 horizon assignment. All games below used
the local Kaggriculture engine, 720 steps, and completed with both agents in
`DONE` status. This quick runner did not persist per-callback stderr/latency,
so those fields remain part of the next confirmation audit.

Paired against frozen V37 with the same seed and seat:

| seed | seat | candidate margin over parent |
|---:|---:|---:|
| 9001 | 0 | +1853 |
| 9002 | 1 | +151 |
| 9002 | 0 | +151 |
| 9004 | 0 | +4075 |
| 9004 | 1 | +1008 |

The completed 12-game paired panel (seeds 9001--9006, both seats) was all
positive: mean delta **+1353.1**, minimum **+151**, 12/12 positive. Every game
ran 720 steps and both final statuses were `DONE`.

Against one public opponent seed (9004, candidate seat 0), margins were:

| opponent | candidate margin |
|---|---:|
| Flex | +6175 |
| Thomas | +11935 |
| Dmitrii | +3997 |

An additional interaction panel is running with Flex, Thomas and Dmitrii on
seeds 9001--9003, both seats, paired against V37. At the latest checkpoint,
Flex has 6/6 completed rows with candidate-minus-parent deltas
`[1480, 62, 1044]` duplicated across seats (mean `+862`, minimum `+62`), while
Thomas seed 9001 and seed 9002 have completed with zero delta in the rows
available so far. The process is resumable and writes each completed row to
`opponent_panel.jsonl`; Dmitrii and the remaining Thomas rows are still queued.

These are still screening results, not promotion evidence. The paired runner
did not persist callback-level stderr/latency, and the public-opponent panel is
only one seed per opponent. The candidate still needs unseen seeds, both seats
against each opponent, runtime/stderr capture, and loss-tape mechanism checks
before it can be considered stable or eligible for submission.
