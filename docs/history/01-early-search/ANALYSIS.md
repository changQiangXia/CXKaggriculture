# EXP-175 premium gate: evidence review

## Scope

EXP-175 changes one line in the frozen V37 policy. Between steps 288 and 695 it
uses a five-turn reservation horizon only when public farm similarity is at
least 0.96 and one visible quote is high (`WOOL >= 80`, `STRAWBERRY >= 150`, or
`MILK >= 100`). In every other state it retains V37's four-turn horizon. The
candidate also carries the no-op H-DSS safety hook; that hook did not change an
action in the runs reviewed here. No Kaggle submission was made.

## Paired local results

The completed opponent panel contains six Flex pairs (seeds 9001--9003, both
seat orders), six Thomas pairs (seeds 9001--9003, both seats), and four Dmitrii
pairs (seeds 9001--9002, both seats). For each pair the
candidate and frozen V37 were run with the same seed, seat and opponent:

| opponent | pairs | mean candidate-minus-parent margin | median | minimum | negative pairs |
|---|---:|---:|---:|---:|---:|
| Flex | 6 | +862 | +1,044 | +62 | 0 |
| Thomas | 6 | 0 | 0 | 0 | 0 |
| Dmitrii | 4 | -284 | -284 | -521 | 4 |

Flex deltas by seed were +1,480 (9001), +62 (9002), and +1,044 (9003), with
identical deltas in both seat orders. Thomas seed 9001 was a no-op tie in the
candidate policy (zero delta in both seats). The first Dmitrii pair is already
a paired regression: seed 9001 is -521 in both seat orders (candidate margin
5,874 versus parent 6,395), and seed 9002 is -47 in both seats (candidate
margin 5,248 versus parent 5,295).
The completed games had 720 steps, `DONE` terminal statuses and no callback
stderr. The Dmitrii regression is sufficient to reject the claim that EXP-175
is stable across opponents; remaining queued rows are useful diagnosis only.

The earlier V37 paired screening file (`screen.jsonl`) has 12/12 positive
candidate-minus-parent margins over seeds 9001--9006, both seats (mean +1,353,
minimum +151). Those games used the same engine and completed cleanly, but they
also do not identify which part of the gate produced the gain.

## Is the hot-price gate causal?

The gate is behaviorally reachable. An independent branch-coverage audit of the
parent V37 path found a qualifying episode (seed 9001) where the V219 path was
active and the price condition was true for all 48 callbacks on days 24 and 27;
it produced two concrete `BUY_PRODUCT FERTILIZER 10` additions. A
non-qualifying episode (seed 9005) never entered that path, so changing a price
threshold there was inert. This confirms that public price conditions can alter
actions, but it concerns V219 fertilizer requests rather than EXP-175's
reservation horizon and is not a performance attribution for this candidate.

For the currently collected online loss logs, the replay observations are from
other submitted policies, so they cannot be used as candidate-vs-parent causal
labels. As a stress check, applying the EXP-175 predicate to two recent losses
from submission 56185929 found one loss with 278 qualifying callbacks and one
with none; both were losses (margins -942 and -1,234). The six most recent
losses from submissions 56190357 and 56209639 had no states satisfying the
predicate. This shows that a hot quote does not guarantee a win and that the
gate is absent from many losses; it does not show that the gate caused either
outcome. The replayed policies are not identified as EXP-175, so these numbers
are diagnostic context only.

The strongest current causal statement is therefore: **the candidate's only
known action-level change is the horizon assignment; the hot-price predicate
is reachable, and gains are observed in the small paired panel, but attribution
to the price gate is unproven.** A proper attribution run must log, for every
candidate/parent pair, gate-active intervals, action diffs, reservation/debt
states and block-level deposits under the same engine trajectory.

One focused trace makes the attribution less ambiguous. In a fresh interactive
run against `ready_dmitri_v6` (seed 9001, candidate in seat 0), the candidate
and parent each completed 719 callbacks. The EXP-175 predicate was true on 402
candidate callbacks. Comparing the two traces at matching callback steps found
63 differing actions, all 63 during predicate-active callbacks; farmer and hand
commands stayed equal, while the candidate moved existing MILK/WOOL/STRAWBERRY
and other SELL orders across adjacent market turns. Thus the hot-price branch is
causally responsible for the observed action mutation in this trace. The paired
terminal result for the same opponent/seed was -521 coins versus V37 (both seat
orders), so the mutation can be harmful under Dmitrii's market timing. This is
an attribution trace, not an independent reward estimate: the two runs have
separate trajectories and the panel remains the authoritative paired result.

## Promotion and kill criteria

Do not promote or submit EXP-175 on this evidence. The paired Dmitrii losses
(-521 in seed 9001 and -47 in seed 9002, both seats) already fail the
zero-negative promotion gate; archive the branch unless a pre-registered
analysis specifically explains and repairs them without introducing another
V37 regression. Continue only with an explicit confirmation
panel of at least 15 previously unseen seeds, both seats, and Flex, Thomas and
Dmitrii, paired against frozen V37. Persist per-game stderr, runtime,
720-step/DONE checks and block-level telemetry. Require no negative paired
margin, no seat-specific regression, and a positive lower-tail margin after
excluding no-op games. If either of two independent confirmation blocks
contains a negative pair, if the candidate's action changes do not coincide
with a complete reservation/debt certificate, or if the fixed-tape direction
disagrees with interactive opponents, archive EXP-175 and stop the branch. A
separate ablation (five-turn horizon under the same similarity condition but
without `premium_hot`) is needed before claiming that the quote threshold itself
is causal.
