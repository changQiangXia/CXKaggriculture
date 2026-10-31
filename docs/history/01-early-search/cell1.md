## 1. The one fact the market gives you

The interpreter settles market orders **in lockstep by list index**:

```
order[0] of player 0 → order[0] of player 1 → order[1] of player 0 → order[1] of player 1 → …
```

Two consequences, and everything below is one of them:

**(a) Every executed unit moves the shared inventory.** So the *first* SELL of a product in a turn is quoted before the glut it creates, and the *first* BUY_PRODUCT is quoted before the squeeze it creates. If your sells sit at index 5 and your opponent's sit at index 0, you are selling into a market they already pushed down — a few dollars per unit, every day, for 30 days.

**(b) Same-index orders of both players are quoted at the same inventory.** This is what makes the step-0 attack in section 5 work: your `BUY_PRODUCT WHEAT n` at index 0 does not make *your own* index-0 order dearer — it makes the opponent's **index-1** order dearer.

V43's own tapes routinely list `HIRE`, `BUY_SEED`, `BUY_LAND` before the day's sells. Against a rival running the same tape, whoever's sells sit earlier wins the day. That is the entire thesis.

Nothing here changes what is planted, watered, harvested or hired. The farm plan is V43's. Only the **order of the market list**, the **timing** of sales, and **one step-0 order** are different.
