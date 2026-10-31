# Q25 paired evaluation runner

This runner compares candidate and parent against each frozen opponent using the same initial seed and both seats. Both agents interact live; no replay tape substitutes for a rival.

```bash
/root/miniconda3/bin/python paired_eval.py candidate.py /root/autodl-tmp/candidate_v45_q25.py \
  --opponent v37=/root/autodl-tmp/public_v37_pkg/main.py \
  --opponent v45=/root/autodl-tmp/submission_competitive_v45.tar.gz \
  --seeds 9040,9041,9042 --workers 2 --out panel.json
```

Arguments accept `.py`, `.tar.gz`, `.tgz`, or `.tar`. An archive must contain a regular root `main.py` and cannot contain symlinks, hard links, path traversal, or duplicate root `main.py`. It is read in memory, never extracted. This evaluates standalone source; imported sibling files and archive assets are not packaged by this runner.

Use `--family-weight NAME=NUMBER` to set fixed weights; unspecified families have weight 1. Do not give multiple filename aliases of one strategy the weight of independent families. `--bootstrap` defaults to 4,000 resamples. Both seats are first averaged within a seed, and the same sampled seeds are used across every family in each bootstrap draw. This preserves common-environment correlation. It does not estimate uncertainty over unknown online opponent families.

`--checkpoint` defaults to `OUT.jsonl`. Each completed pair is appended and flushed. `--resume` requires an exact manifest match, including candidate/parent/opponent source and archive hashes, runner and engine hashes, seeds, weights, and episode/run timeout configuration. A fresh run refuses to append to an existing checkpoint. A changed runner intentionally requires a fresh checkpoint.

The official Kaggle `get_last_callable` export rule is used lazily during the first action, so source initialization is included in the official action allowance. The environment runs with `debug=False`, capturing exceptions and action-time logs. `--run-timeout` defaults to 120 seconds per game; an outer Linux alarm at timeout plus 5 seconds interrupts a callable that never returns. This local wrapper adds action digest and telemetry observation; it is not a claim that the full remote infrastructure has been reproduced.

Outputs contain actual candidate/parent `W`, `T`, `L`, `point_delta` with points 1/.5/0, outcome transitions, and cash-margin delta diagnostics. They also contain candidate and opponent raw/accepted action digests, final-callable telemetry, action durations, full health status, source/archive hashes, engine hashes and runner hash. A cash margin improvement is never counted as a win. Per-row `mine_*_action_duration_sec` and `opponent_*_action_duration_sec` fields are scoped to the tested artifact and its rival respectively, using the environment seat (`seat`); the older `max_action_duration_sec`/`sum_action_duration_sec` fields remain for compatibility and are explicitly marked `legacy_action_duration_scope: both_players`.

`summary.ok` is an inference eligibility flag, not a promotion decision: it requires a complete paired-seat panel, healthy rows, and at least two seed clusters. `point_delta_bootstrap` is the primary comparison. A positive point estimate alone, a cash CI above zero, or an eligible local panel cannot guarantee online improvement. Formal promotion must also use a prespecified held-out panel and family/tail constraints.

Non-DONE states, intermediate ERROR/INVALID/TIMEOUT, missing/nonfinite rewards, stderr, exceptions, or wrong episode length make rows unhealthy. Those rows remain in the output; the panel fails closed and any surviving estimates are labelled diagnostic only. One-seed loader smoke tests also produce diagnostic-only intervals and exit code 2 even when every game is healthy.

Validation: `python test_paired_eval.py` checks that losing less is not a win, both seats are one seed cluster, unhealthy panels fail, and `.py`/safe archive exports use the final callable. A small Q25 `.py` versus its `.tar.gz` null experiment (seed 9040, both seats, self opponent) completed healthily with identical outcome/cash/action results; it is a loader check, not strength evidence.
