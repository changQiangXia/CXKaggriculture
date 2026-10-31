# Origin and permitted sources

`guts` was written from scratch during the 2026-09-15 development run. The only material read was:

- `/root/autodl-tmp/kaggriculture/README.md`
- `/root/autodl-tmp/kaggriculture/AGENTS.md`
- Official installed engine implementation `/root/miniconda3/lib/python3.10/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py` (and its specification JSON only as loaded by that engine).

No other agent source, public notebook, historical candidate, replay, or research report was read. The policy is observation-driven and contains no precomputed action tape or opponent private-state access.
