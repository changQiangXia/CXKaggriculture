# v37 latent pasture activation (screening result)

This branch tests one non-threshold mechanism copied from a public top-score
design: at step 313, duplicate one already planned animal purchase and add a
fourth hire only when a visible empty pasture, exact seven-hire spawn geometry,
cash reserve, shed room, and a one-animal/three-hire parent action all hold.
The new hand is then required to deliver the animal through the visible
314--316 position/inventory contract. Any mismatch cancels and returns the
parent action.

The entry point compiles and every tested game completed 720 steps with
`DONE` status and no policy exception. In the first ten-seed Flex panel
(9001--9010, seat 0), the activation predicate fired **0/10** times and the
candidate rewards were byte-for-byte the ordinary v37 rewards. The branch is
therefore unreachable under the v37 route on this screening distribution and
has no demonstrated improvement. It is archived as `rejected_unreachable`,
not a submission candidate. No further geometry loosening is justified without
a new replay showing the full certificate; loosening it would turn a
multi-day production intervention into an unverified investment change.

The source remains separate from the frozen v37 package and was never
uploaded.
