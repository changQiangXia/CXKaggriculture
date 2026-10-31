## 3. Edge 2 — the two-turn sale advance

This one I did not design. I found it by re-simulating losses I could not explain.

I kept losing games where both agents produced **identical daily order sets**. Same crops, same volumes, same everything. Re-playing those episodes with the opponent's recorded actions showed the difference: they were selling the same lots **two turns earlier**. Selling earlier means selling before the town's consumption tick has been eaten into by the other player.

So: for pure cash products, look ahead in V43's own tape, and if a sale is planned within the next 2 turns and the goods are already in the shed, bring it forward.

`advance_declined_full` in the telemetry counts the times the look-ahead refused because the earlier sale would not have executed in full.
