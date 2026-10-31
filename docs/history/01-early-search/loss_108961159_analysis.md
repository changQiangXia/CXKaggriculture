# Loss replay 108961159 (V42 vs Bohann Wang)

The replay is a complete 720-step episode with no timeout or runtime error.  Bohann (seat 0) finished at **144,000** and our V42 (seat 1) at **143,495**, a 505-money loss.  Actions differ on only 29 of 720 turns; after the opening, both farms follow almost identical production and terminal schedules.  At step 719 both sheds and all worker inventories are empty, so the margin is cash earned during the episode rather than an unliquidated asset or terminal-planner failure.

The cash gap is created in several small phases:

* Opening wheat tape: step 1 leaves V42 at 3,001 versus Bohann at 2,866; step 2 reverses this by 198.  By steps 21–22 the remaining gap is 43, with V42's opening tape having a different wheat/seed balance.
* At days 7–9 V42 buys two extra wheat units (steps 171 and 195), adding 66 and 68 to the opponent's lead.  The production route later recovers much of this; the gap is about 270 by day 14 and then grows through small sale-order effects.
* The largest single divergence is step 648 (day 27 hour 0).  Bohann submits `STRAWBERRY 18, WHEAT 10, MILK 1`; V42 submits `WHEAT 5, MILK 1, STRAWBERRY 18, WHEAT 5`.  Bohann gains 4,556 while V42 gains 4,433 (+123 for Bohann).  Market orders are processed one unit at a time and in queue order, with prices changing after each unit; splitting/reordering wheat around premium-resource sales therefore changes revenue even when total quantities match.
* Final liquidation (step 717) contributes only one additional money unit.

The step-648 pattern is a concrete, replay-supported candidate for a safe improvement: retain V42's route and production actions but canonicalize sale orders by combining same-item orders (WHEAT 10) and searching a small set of order permutations.  The opening and extra-feed purchases should be evaluated separately because they account for the earlier 200–270 money difference.  This replay does not implicate R124/R127/R128 or terminal actions.

See `kaggriculture/README.md` §Market Mechanics (ordered, concurrent one-unit sales; lines 188–202) for the pricing behavior behind this effect.
