## 8. Two traps that produced completely convincing wrong numbers

### Trap 1 — auditing against a wrapper file gives you a fake landslide

My candidates are built as wrappers: a small file that loads the V43 parent from a relative path and patches it. Convenient for sweeps. Then I ran the official-runner audit with a *wrapper* as the opponent and got:

```
candidate vs opponent:  16-0,  margin +167,366
```

which I very nearly believed for longer than I would like to admit.

`kaggle_environments` **exec's the agent source** rather than importing the file, so the wrapper's relative-path parent load fails. The opponent then PASSes every single turn and finishes the season on its 3,000 starting money. You are not beating it; you are watching it not play.

**Always audit against the packaged single-file `main.py` you would actually submit.** Re-run against the package: 16-0, **+1,328** — which matches the local harness (+1,333) and the 64 worlds (+1,334). Three independent numbers agreeing is the check; one spectacular number is a bug.

### Trap 2 — the evaluation dies exactly when it gets interesting

Long sweeps were being OOM-killed at 6 GB, always deep into a run. Each candidate module left ~40 MB in `sys.modules`, and wrappers load their parent under *the parent's* name, so deleting only my own `ag_*` entries was not enough:

```python
_BASE_MODULES = set(sys.modules)            # at import time

def fresh(path, tag):
    for k in [k for k in sys.modules if k not in _BASE_MODULES]:
        del sys.modules[k]                  # everything any earlier agent dragged in
    gc.collect()
    ...
```

Memory went flat at ~50 MB. Obvious afterwards; it cost a day of sweeps that died at game 200 of 256.
