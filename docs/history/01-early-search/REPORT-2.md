# v37 demand pasture activation (rejected)

This branch tested a single non-threshold intervention: on an existing
BUY_ANIMAL turn during steps 120--300, add one same-type animal and one HIRE
when public shop demand, an empty matching structure, cash reserve, and shed
room all pass. A new hand then attempted an observation-driven pickup and
placement sequence with cancellation on state mismatch.

The branch compiled and all games completed 720 steps/DONE. It failed the
first interactive screen: against Flex seed 9004, seat 0, the candidate margin
was 5704 versus frozen v37 margin 6376 (delta **-672**). Telemetry showed one
activation, five delivery overrides, and zero successful placements: the extra
purchase was consumed without establishing a new producing animal. This is a
causal implementation failure, not evidence that the public pasture idea is
profitable on v37. The branch is archived as `rejected_delivery_contract`.

No geometry loosening or further tuning is allowed in this branch. A future
animal-investment experiment would need an engine-verified multi-step delivery
certificate, including exact spawned-hand index, inventory transitions, target
occupancy and barrier preservation before any market mutation is enabled.
No upload or submission was made.
