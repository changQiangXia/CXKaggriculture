# Technique extracts from public code round 2

## Bounded premium lead

Boatlee's public V16-RC5 uses `_future_quantity`, `_town_demand_now`, `_pickup_reserve`, `_existing_sell`, `_front_run`, and `_repay`. The mechanism moves only the amount the next tape turn would sell, subtracting current pickup and SELL reservations, skips items with immediate town demand, and records a due quantity for the next turn.

## Economic constraints

The public crop-economics notebook shows that premium inventory is price-sensitive and that the market resolves up to ten orders in sequence. A 100-unit lump sale can lose substantial revenue as inventory moves down the price curve. This supports order-aware local interventions but does not support copying a fixed quantity or fixed step globally.

## State contracts

Public frontier agents repeatedly keep substitutions bounded by pre-registered purchase/service nodes, visible demand and minimum pressure gaps. Their useful general pattern is `candidate action -> exact visible-state check -> parent fallback`.
