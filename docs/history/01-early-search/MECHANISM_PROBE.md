# H-DSS mechanism probe (2026-09-14)

The only admissible minimal intervention tested was **filling an existing
zero-quantity SELL reservation** from the current visible shed ledger.  The
probe deep-copies the whole action block, never appends or reorders market
orders, and returns the parent block on malformed input or replay errors.

`mechanism_probe.py` provides this diagnostic and a synthetic fixture.  The
fixture confirms the causal direction: with a nearly full shed, selling an
already reserved WHEAT slot before a DROP reduced simulated overflow from 3 to
0 and increased local money by 2,172.  This is a unit-mechanism check only;
the fixture is not a game policy and carries a shared-market parity warning.

On captured replay `episode-107904739-replay.json`, blocks 576–647 and 648–719
for both seats replayed without engine errors and reported zero overflow.  No
existing zero SELL reservation produced a non-negative money improvement in
the tested day-24 block; one-unit fills were neutral for WOOL and negative for
STRAWBERRY/MILK.  Therefore no real replay certificate exists for enabling the
intervention.

The block simulator still cannot reproduce exact online money/tiles parity
because opponent private state is synthetic.  Results are consequently
limited to own-side physical diagnostics and cannot justify a submission.
