# v37 collect-fertilizer capacity brake (rejected)

Single intervention tested: during steps 600--695, replace only
`COLLECT_FERTILIZER` commands when visible shed plus carried inventory plus
current-turn collections exceeded 99 units. The branch never changed market
orders, SELL quantities, worker positions, or production commands otherwise.

The broad physical screen (Flex, seeds 9001--9005, seat 0) produced deltas
`-143, +324, +343, -108, +72` versus paired frozen-v37 margins, with two clear
negative games. Tightening the gate to steps 623 and 695 reduced the effect but
still produced a consistent `-1` delta on all five seeds. It is therefore
rejected: suppressing one fertilizer unit has an opportunity cost and does not
provide a robust capacity benefit. No further threshold tuning is warranted.

All games were 720 steps, `DONE`, with zero callback errors. No upload or
submission was attempted.
