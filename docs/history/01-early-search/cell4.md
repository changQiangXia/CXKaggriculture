## 2. Edge 1 — market front-loading

Rewrite each turn's market list as:

```
[SELLs that are not wash trades] + [BUY_PRODUCT + the wash SELLs] + [everything else]
```

and keep the original list unless a per-unit simulation of **both** lists — cash, shed capacity, hire costs, land prices, once solo and once under lockstep pressure — says the reordered list still executes in full. It never adds, removes or resizes an order.

That last clause is the whole safety argument. A reorder that makes an order fail is worse than no reorder: V43's plan assumes every order lands.

Measured alone, on top of plain V43: **16-0 vs V43 (+476)**, 16-0 against every public bot I tested (V41, Farming Score V5, Shop Router Reactive V5, V40 Challenger). On the ladder it is a tie-breaker against the V43 family, which is most of the 2,500–2,700 band.
