# Carrot-route design (background track)

## Why the naive swaps failed

- Wheat out-earns carrot per tile/day (0.80 vs 0.75) in raw production.
- Late-window swaps starve the final-days animal feed (day-27 goose escapes).
- Mid-window swaps lose ~6.7K/game: the displaced wheat sales clamp down and
  the carrots are dumped by room_guard at weak mid-game prices.

## What a real carrot line must do

Carrot is a scarcity/hinge exploit, not a yield play. Requirements:

1. Plant carrots EARLY (day 3-8) in a dedicated 5x5 block, so the first wave
   lands while the field still under-supplies carrots.
2. Sell INTO the pet-cafe / farmers-market consumption ticks: pet cafe is a
   single-product shop (consumes 2x carrot) and carrot uses the hinge shape on
   the scarcity side, so demand spikes move the price sharply above base.
3. Keep the wheat-feed ledger intact: every removed wheat plant must come out
   of the SELL surplus, never the feed chain.
4. Own water/harvest/drop slots for the carrot block (the shared HARVEST is
   crop-agnostic, but planting day and sell steps must be designed).

## Planned build (incremental, each step gated)

1. Parse route 0 into a per-tile lifecycle (plant/water/harvest/drop steps).
2. Identify the wheat plant slots that feed animals vs sell (trace PICKUP WHEAT
   consumption by day).
3. Rewrite one SE/NE field block into an early carrot cycle:
   - replace the block's wheat PLANT slots with CARROT at days 3-8;
   - swap matching BUY_SEED WHEAT -> CARROT;
   - insert SELL CARROT lots at the town-tick steps of pet-cafe shops (day % 4);
4. Validate on 64 seeds: 720 steps, zero escapes, zero overflow, then h2h vs
   v48_a5 and the 10-family field panel.

Status: scaffolded, not yet implemented. This track resumes after the market
layer prototype is validated.
