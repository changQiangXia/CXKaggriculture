# cap2 replay findings (2026-09-13)

Analyzed latest loss/tie replays for active submissions 56185929 (h5sim96) and 56190357 (h5room623), focusing on steps 210-234 where V231 cattle substitution may trigger. To account for replay indexing, candidate is called on replay steps[i].observation with explicit shared step; recorded action generated from that observation is replay step i+1 action (the old direct action comparison was offset and falsely showed 719 diffs).

Using h5sim96_cap2 logic, among recent losses:
- cap2 cattle controller triggered requested=1, confirmed=1, picked=1, placed=1 in episodes 108276056, 108284087, 108320556, 108351343, 108376666.
- In all triggers requested quantity was exactly 1, so cap=2 and original cap=4 produce identical behavior. No recent loss had >2 substitutions; cap2 therefore does not change decisions in these games.
- Most losses had no cattle trigger at all; losses remain driven by market/sales timing and hidden inventory/order effects.

At step 623/695 in triggered episode 108276056, cap2 harvested extra milk and appended to existing SELL MILK orders (telemetry extra_milk_harvested=15 at step623, extra_milk_sale_requests=6; total by step695 21 harvested, 15 appended). This is inherited h5sim96 behavior, not cap2-specific.

Implication: cap2 is a low-risk diversity variant but replay evidence does not show it fixing h5sim96's losses; its only difference from cap4 appears when >2 cow substitutions requested, which has not occurred in inspected recent losses.
