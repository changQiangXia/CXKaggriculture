# Kaggriculture Simulation (kagg)

A fast, byte-identical simulator for the Kaggle **Kaggriculture**
competition, packaged for notebooks.

* `kagg` is a static x86-64 Linux binary: the Rust port of the official
  engine (`kaggle-environments==1.32.7`), plus tournaments, self-play data
  generation, batch rollouts and a step-by-step `serve` environment.
* `kaggsim/` is the standard-library-only Python toolkit around it.

Source code, full documentation and the fidelity test suite:
https://github.com/debmalyaroy/kaggriculture-simulation

## Use in a notebook

```python
import os, shutil, sys
DS = "/kaggle/input/kaggriculture-simulation"
shutil.copy(f"{DS}/kagg", "/kaggle/working/kagg")   # dataset files are read-only
os.chmod("/kaggle/working/kagg", 0o755)
os.environ["KAGG_BIN"] = "/kaggle/working/kagg"
os.environ["PYTHONPATH"] = DS          # lets kagg's Python agent host import kaggsim
sys.path.insert(0, DS)

from kaggsim.serve import run_match, load_agent
print(run_match(load_agent("/kaggle/working/main.py"),
                load_agent("/kaggle/working/main.py"), seed=3))
```

A tournament of your `main.py` against other agents, across worlds, in
parallel:

```python
from kaggsim.tournament import run_tournament
s = run_tournament({
    "name": "demo",
    "candidate": {"name": "mine", "type": "python", "path": "/kaggle/working/main.py"},
    "panel": [{"name": "rnd", "type": "builtin", "kind": "random", "seed": "per_game"}],
    "worlds": {"strategy": "stratified", "pool": [0, 2000], "per_world": 2, "key_depth": 2},
    "workers": 2,
    "output": {"dir": "/kaggle/working/tournaments", "resume": False}})
print(s["focus"]["overall"])
```

## Fidelity

Every step of every test episode is compared with the official engine
(full state: both banks as IEEE-754 bits, every tile, both private blocks,
the market and the town). The Kaggle notebook image may ship a different
`kaggle_environments` version; the toolkit's fidelity tools check the
engine's file hash and refuse anything but 1.32.7.

## License

Apache-2.0. The engine is a port of the Kaggriculture environment in
kaggle-environments (Copyright 2020 Kaggle Inc, Apache-2.0); see NOTICE.
Not affiliated with or endorsed by Kaggle.
