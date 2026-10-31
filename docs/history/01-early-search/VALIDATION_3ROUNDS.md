# Nathan candidate validation — 2026-09-16

## Scope

Validated `nathan_cautious_3rounds_candidate.tar.gz` without submitting. Three rounds were performed: archive and true loader inspection; paired engine smoke; and replay/action parity on two historical losses. A corrected local package was then made after finding a composition bug in the Round 2 wrapper.

## Round 1 — archive and Kaggle loader

- Archive: `nathan_cautious_3rounds_20260916/nathan_cautious_3rounds_candidate.tar.gz`
- Archive SHA-256: `a599e856ddc30072868324ffe0ee33c02035b83f85e117e1cc2b35fbbede3a15`
- Extracted root contains `main.py` and `README.md`; extracted `main.py` SHA-256 is `98614045e1616e5b8b9711bd925f427991ceb92f312c94ebf2923ff738acf02d`.
- `py_compile` passes.
- `kaggle_environments.agent.get_last_callable()` selects a callable named `agent`, and `selected.__globals__['agent'] is selected` is true. Thus the uploaded candidate's final wrapper is actually selected by the Kaggle file loader.
- It completes 720-step local runs with status `DONE/DONE` in the paired panel.

The parent file `nathan_cautious_final/main.py` does not pass this identity check: its selected callable is the internal parent rather than the final cautious wrapper. This is why a candidate-vs-parent comparison must be described as candidate versus the parent's actual deployed callable, not candidate versus the intended named wrapper.

## Round 2 — paired engine smoke

Representative panel: opponents `public_v37` and `ready_flex_v7`, unseen seeds `9011` and `9014`, both seats. Eight candidate/parent paired games (16 engine runs) were completed. Every run reached 720 steps and `DONE/DONE`.

The original candidate had zero final-margin delta in all eight pairs. This is only a smoke result; it does not prove generalization. The original long panel was stopped after two pairs because the controller takes roughly 10–11 seconds per 720-step run.

## Round 3 — historical replay/action parity

Replayed the own-seat observations from Nathan loss episodes `109437616` (kobayasi) and `109392182` (forever young), 719 callbacks each, against both the original candidate and the selected parent callable.

The original candidate had one action difference per episode, both at step 121:

```text
candidate: market = [["HIRE"]]
parent/recorded: market = [["HIRE"], []]
```

The difference is caused by the composition of the wrappers: the final Round 2 wrapper sets `_NC2_PARENT=agent`, where `agent` is already the Round 1 malformed-order filter. Therefore Round 2 cannot restore zero/empty market slots removed by Round 1. The candidate still changes order-list indices in exactly the situation the round was intended to protect.

This is a real slot-preservation failure, even though the two small engine panels happened to have identical final margins. Original candidate recommendation: **do not submit**.

## Corrected local candidate

A local corrected source was made by changing only:

```python
_NC2_PARENT=agent
```

to:

```python
_NC2_PARENT=_NC_PARENT
```

This makes the final wrapper call the pre-filter R148 parent directly, so zero/empty order slots are retained. The corrected source passes `py_compile` and true-loader identity. Its historical replay parity on both loss episodes is exact: 719/719 callbacks, zero candidate-parent differences, zero candidate-recorded differences, zero errors; maximum callback latency about 0.052 s and p99 about 0.007 s per episode.

Corrected archive:

- [nathan_cautious_corrected_candidate.tar.gz](./nathan_cautious_corrected_candidate.tar.gz)
- SHA-256: `c7d8ed1f5da2f047eeb3d9ae96eb3774a178647374d7cd16fb07425d7e3893f1`
- Source: [corrected/main.py](./corrected/main.py)

The corrected paired panel also completed: 8/8 pairs (v37/flex × seeds 9011/9014 × both seats), all 720-step DONE/DONE, with zero final-margin delta in every pair. This only establishes no regression on this small panel; it is not evidence of a positive score gain.

## Decision

The original `nathan_cautious_3rounds_candidate.tar.gz` is **rejected for submission** because its claimed slot-preservation round is not effective after wrapper composition. The corrected package is only a local candidate pending its paired panel; no package has been submitted to Kaggle.
