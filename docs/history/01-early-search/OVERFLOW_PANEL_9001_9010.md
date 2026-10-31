# Overflow candidate panel (public_v37, seeds 9001–9010, both seats)

Local `kaggriculture` engine, 720 steps, candidate versus frozen `public_v37_pkg/main.py`. No Kaggle submission was made. The run emitted the environment's unrelated optional-loader notices (`pokerkit`/`pydantic` missing); they did not affect Kaggriculture and every game completed normally.

| candidate | games | W/L/T | mean margin | min | max | all DONE | errors |
|---|---:|---:|---:|---:|---:|---|---:|
| h5sim96 baseline (9001–9005 reference) | 10 | 10/0/0 | +1815.1 | +740 | — | yes | 0 |
| overflow623 | 20 | 20/0/0 | +1773.15 | +368 | +4063 | yes | 0 |
| overflow695 | 20 | 20/0/0 | **+1842.45** | +466 | +4275 | yes | 0 |
| overflow623_695 | 20 | 20/0/0 | +1773.15 | +368 | +4063 | yes | 0 |
| overflow623 only (new) | 20 | 20/0/0 | **+2044.95** | +670 | +4334 | yes | 0 |

The files named `overflow623.py` and `overflow623_695.py` are byte-identical and both gate **steps 623 and 695** (the former name is historical; it is not a 623-only implementation). They are therefore the combined candidate, with mean +1773.15. The `overflow695.py` file gates step 695 only and is slightly above the h5sim96 reference (+27.35 margin points, within expected seed variance). The newly generated `overflow623_only.py` gates only step 623 and is +2044.95 mean on this panel, +229.85 above the h5sim96 reference and +202.50 above the combined variant. This favors isolating the day-6 fix; it still requires replay counterfactual validation before any submission decision. All 80 games reached 720 steps with both agents `DONE`; no candidate errors were observed. These local means do not establish an online rating gain.

Result JSON files:

- `h5sim96_overflow623_panel_9001_9010.json`
- `h5sim96_overflow695_panel_9001_9010.json`
- `h5sim96_overflow623_695_panel_9001_9010.json`
- `h5sim96_overflow623_only_panel_9001_9010.json`

Reference values from the existing `h5base_public_panel.json` (the first five seeds, both seats) are 10/10 wins, mean `+1815.1`, minimum `+740`. The 695-only candidate therefore improves the reference mean by `+27.35`; 623-only and combined are `-41.95` below it. This is a small local effect and should not be interpreted as an online rating prediction.

补充：只处理 step 695 的版本在 3 个公开高分对手的 9001–9003 双席小面板上也全部 6/6 胜：Flex 平均 +3607（最小 +3212）、Thomas 平均 +7201（最小 +5011）、Dmitrii 平均 +5373（最小 +4864）。该结果只是筛查，不能替代真实线上 replay 反事实。

补充修正：`h5sim96_overflow623.py` 旧文件实际包含 623+695 双时点逻辑。真正的 623-only 文件为 `h5sim96_overflow623_only.py`。其 public_v37 面板为 20/20 胜、平均 +2044.95、最小 +670；Flex 20/20、平均 +4954.85；Thomas 19/20、1 tie，平均 +6222.25，唯一负值为 seed 9004 seat1 的 -614；Dmitrii 20/20、平均 +6315.95。由于 Thomas 出现负值，623-only 尚未达到双候选提交门槛。
