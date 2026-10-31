# Log-derived modification: rule-aware generalization constraints

Official README semantics imply a log-derived change must be tested as a state-conditioned intervention. A replay exposes one realized RNG path, one seat, one opening, and one opponent; it does not reveal hidden opponent shed/inventory or future actions. Therefore:

- discovery from loss/high-score logs only;
- development on multiple strategy families and seeds;
- holdout on unseen public agents/seeds/seats;
- stress perturb market inventory, shops, order queues, and visible opponent farm;
- enforce parent-action equivalence whenever contract fails;
- evaluate 72-step downstream cash/shed/carried/capacity/sale-debt effects, not only local margin;
- report activation, rejection reasons, valid orders, DONE/720, stderr, timeout, 5% quantile, CVaR, min margin, seat/opponent strata.

Do not use hidden opponent state or future tape in submitted agents. Market orders are ordered, one-unit concurrent, max 10/player/turn; silent no-ops and shed overflow make action-level validation mandatory. Reward counts bank coins only at season end, so unsold inventory cannot be credited.
