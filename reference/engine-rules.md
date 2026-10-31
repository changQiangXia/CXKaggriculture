# Kaggriculture engine reference (partial; kaggle-environments 1.32.7)

Convenience excerpts from the engine version used during the competition.

> **Verification status:** these excerpts are not a replacement for the
> official engine source. The post-competition documentation audit could not
> independently retrieve public package version `1.32.7`, so the constants and
> docstrings below were not re-verified end-to-end. In particular, the
> `_daily_refresh_animals` docstring appears duplicated from the shed-drop
> helper and should be treated as an extraction artifact, not as an
> authoritative rule description. For execution-sensitive work, compare
> against the exact pinned engine source and replay traces.

Canonical evidence conventions are in
[`../docs/08-evidence-and-scope.md`](../docs/08-evidence-and-scope.md).


## FARMER_MOVES

```python
FARMER_MOVES = {
    "NORTH": (0, -1),
    "SOUTH": (0, 1),
    "EAST":  (1, 0),
    "WEST":  (-1, 0),
}
```


## CROPS

```python
CROPS = {
    "WHEAT":      {"seed": 10, "first_yield_day": 2, "max_yield_day": 4, "interval": 0, "max_yield": 6, "ongoing": False},
    "CARROT":     {"seed": 20, "first_yield_day": 2, "max_yield_day": 3, "interval": 0, "max_yield": 4, "ongoing": False},
    "TOMATO":     {"seed": 50, "first_yield_day": 8, "max_yield_day": 8, "interval": 1, "max_yield": 4, "ongoing": True},
    "STRAWBERRY": {"seed": 100, "first_yield_day": 10, "max_yield_day": 10, "interval": 2, "max_yield": 4, "ongoing": True},
    "MELON":      {"seed": 80, "first_yield_day": 10, "max_yield_day": 12, "interval": 0, "max_yield": 6, "ongoing": False},
}
```


## ANIMALS

```python
ANIMALS = {
    "GOOSE": {"cost": 300, "structure": "COOP",    "first_yield_day": 4, "interval": 1, "max_held": 4, "product": "EGG"},
    "COW":   {"cost": 400, "structure": "PASTURE", "first_yield_day": 8, "interval": 2, "max_held": 6, "product": "MILK"},
    "SHEEP": {"cost": 500, "structure": "PASTURE", "first_yield_day": 6, "interval": 3, "max_held": 6, "product": "WOOL"},
}
```


## PRODUCTS

```python
PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
```


## SHOPS

```python
SHOPS = {
    "BAKERY":         ["EGG", "WHEAT"],
    "PIZZA_SHOP":     ["MILK", "TOMATO", "WHEAT"],
    "BRUNCH_SPOT":    ["EGG", "WHEAT", "STRAWBERRY"],
    "YARN_STORE":     ["WOOL"],
    "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"],
    "PET_CAFE":       ["CARROT"],
    "SMOOTHIE_SHOP":  ["STRAWBERRY", "MILK"],
    "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}
```


## LAND_PRICES

```python
LAND_PRICES = [1000, 2000, 4000]
```


## LAND_ORDER

```python
LAND_ORDER = ["NE", "SW", "SE"]
```


## _drop_inventories_to_shed

```python
    """Drop every per-farmer inventory into the shed up to `capacity`; overflow is discarded.
    Seeds are tracked separately in private["seeds"] and don't pass through the shed."""
```


## _daily_refresh_animals

```python
    """Drop every per-farmer inventory into the shed up to `capacity`; overflow is discarded.
    Seeds are tracked separately in private["seeds"] and don't pass through the shed."""
```


## _end_of_day

```python
    """Carrot loop: buy seed, plant on the current tile, water, harvest at max_yield_day."""
```
