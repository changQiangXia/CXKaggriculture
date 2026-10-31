# V37 fertilizer threshold ablation (EXP-175)

Date: 2026-09-12  
Scope: one-variable local ablation of `public_v37_candidate.tar.gz`; no Kaggle submission.

## Change

The V37 source has the V219 labor/fertilizer gate:

```python
_V219_FERTILIZE and day in (24,27) and obs['market']['prices']['FERTILIZER'] <= 30
```

The candidate changes only the final threshold from `<= 30` to `<= 25`. The day set, labor allocation, sale logic, terminal planner, and all other code remain unchanged. The source package was copied into an isolated directory before editing; the submitted baseline archive was not modified.

Candidate archive: [candidate_v37_fert25.tar.gz](candidate_v37_fert25.tar.gz)  
Archive SHA-256: `14af99ab4a75c0a211bfd29249a3273fa35dd1c6b79c8209e035b0e2d5ca7796`  
Source SHA-256: `b3b5c73cc64f69d43948615aa8d4b5211410cc7980baf8cc15efbc83dcedb614`  
Archive contains only root `main.py`.

## Validation protocol

- Opponent: isolated `ready_flex_v7/main.py`.
- Seeds: `9001, 9002, 9003, 9004, 9005`.
- Both seat orders for every seed (10 games per candidate).
- Official local `kaggle_environments` engine, 720 episode steps, debug enabled.
- Baseline: extracted unmodified V37 source (`94c1c2c05ae7...`).
- Gate: `env.done`, 720 recorded steps, both terminal statuses `DONE`, no run exception.

## Results

| candidate | games | wins | losses | ties | mean margin | min margin | max margin | all DONE |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| V37 baseline | 10 | 10 | 0 | 0 | +4,831.0 | +1,785 | +12,661 | yes |
| V37 `price<=25` | 10 | 10 | 0 | 0 | +4,831.0 | +1,785 | +12,661 | yes |

Every paired game had exactly equal terminal rewards and margin:

```text
9001 seat0 +1785   seat1 +1785
9002 seat0 +2462   seat1 +2462
9003 seat0 +2314   seat1 +2314
9004 seat0 +6376   seat1 +3490
9005 seat0 +12661  seat1 +12661
```

The ablation therefore had no measurable effect on terminal outcome in this panel. This is consistent with the V219 gate not being active for these episodes (or with no resulting downstream action difference). It provides no measured improvement and should remain an experiment-only archive; do not submit on this evidence.

Validation output is preserved in `experiments/v37_fert25/results.json`, with the runner in `experiments/v37_fert25/run_panel.py`.
