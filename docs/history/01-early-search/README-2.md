# v37_hdss (EXP-174)

Minimal H-DSS day block scheduler scaffold. The executable agent delegates to
`public_v37_pkg/main.py` behaviour and keeps the `native` profile until a caller
provides a complete certificate (`overflow_units == 0`, unchanged barriers, and
at least 50 coins conservative gain). `hdss.py` contains the profile contract
and telemetry helpers; it does not model hidden opponent state or submit code.
`engine_block_sim.py` is a separate diagnostic tool that replays at most 72
actions through the installed Kaggriculture engine primitives. It clones only
the acting player's private observation, uses synthetic opponent private state
and PASS by default, and labels any supplied opponent action tape as offline
public input. Run `python test_engine_block_sim.py` for deterministic semantic
and information-flow checks.
