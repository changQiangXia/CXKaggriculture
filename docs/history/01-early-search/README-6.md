# Thomas layer transfer probes

Source mechanism: Thomas Tschinkel public state-router's `clamp_sells` and `dead_stock` layers. v37 chassis contains both implementations but `_SETTINGS` disables them. We toggled them on as isolated probes without changing route tapes.

- `main_clamp.py`: `clamp_sells=True`, `dead_stock=False`
- `main_dead.py`: `clamp_sells=False`, `dead_stock=True`
- `main_clamp_dead.py`: both on

`dead_screen.jsonl` records 2 seed × 2 seat v37 self-match; all DONE 720, no errors. Dead-stock deltas are -147/-16 versus v37, so reject this layer. Clamp initial 9001–9006 seat0 screening was -10,+10,+10,+368,+86,+4 (symmetric seats), small and not evidence of stable gain; full screen was interrupted before cross-opponent confirmation. No candidate is submission-ready.
