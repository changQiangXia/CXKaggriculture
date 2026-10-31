# Reproducing the evaluation

The harness replays **recorded opponent action tapes** against a candidate on
a local engine and reports paired statistics.  Read the caution in the main
README before trusting any number that comes out of it.

## Requirements

* Python 3.11
* A local engine that reproduces the official rules.  The work in this archive
  used a Rust re-implementation of `kaggle-environments==1.32.7` exposed as the
  `kagsim` module (`kagsim.Game(seed)`), which is what every script imports.
  Any engine with the same API works.
* Replays: Kaggle replay JSON, gzip or plain (the readers sniff the gzip magic
  rather than trusting the extension, because the local corpus stores gzip
  payloads inside `.json` files).

## 1. Paired A/B against recorded opponents

```bash
python tools/h2h_w2120_live.py \
    --arms candidates_armA/main.py candidates_armB/main.py \
    --replays /path/to/replay_folder \
    --ids /path/to/episode_ids.txt \
    --workers $(nproc) \
    --out /tmp/paired.json
```

* `--ids` is one episode id per line; the script builds
  `episode-<id>-replay.json` under `--replays`.
* The opponent's exact action tape is replayed for the whole game, so both
  candidates face identical opponents.  The printed statistic is the
  **paired difference**, which is what you want.
* Rows also carry `fid` = opponent realised bank / recorded bank.  Filter to
  `fid >= 0.95` when the opponent might have been starved by your agent.

Typical runtime: ~6 games/second/worker, so wall time scales with the worker
count — but **size the count from the container's quota, not from habit**.

In a container the usual gauges report the *host*: `nproc`, `/proc/loadavg`
and `free` describe the machine, not your allocation. The enforced limits are
in cgroup files:

```bash
cat /sys/fs/cgroup/cpu.max       # format: "<quota> <period>"; 200000 100000 == 2 CPU
cat /sys/fs/cgroup/memory.max    # bytes, or "max"
cat /sys/fs/cgroup/cpu.stat      # nr_throttled / throttled_usec
```

Choose workers from that. A flag sized for a many-core machine can
oversubscribe a fractional-CPU container by more than an order of magnitude;
the symptoms are a load average far above the quota, sustained throttling, and
— on hosts that enforce a load ceiling — the instance being shut down mid-run.
Start conservative and raise the count only while throttling stays low.

The same applies to memory: a container limit can be a small fraction of what
`free` reports, so size memory-heavy work against `memory.max`.

## 2. Direct duel between two agents

```bash
python tools/duel.py --a armA.py --b armB.py --seeds 1-128 --workers $(nproc)
```

Each world is played twice with the seats swapped, so first-player advantage
cancels and the two games of a pair share a world.  Use `--seeds 1-128`
for 256 games; the per-world mean is the statistic to test.

## 3. Live submission profile

```bash
python tools/live_summary.py --dir <folder of replays> --profile
```

Prints W/L, margin quantiles, the worst and best games, and terminal-state
herd/cash/quadrant profiles for both seats.

## 4. Opponent strength buckets

```bash
python tools/today_analysis.py --lb <leaderboard csv> --games label=<replay dir>
```

Joins each game to the leaderboard by team name and reports win rate per
opponent-rank bucket.  Needs a leaderboard export containing
`rank, teamName, score` (the Kaggle CLI `leaderboard --show -v` output works).

## 5. Bradley-Terry refit

```bash
python tools/bt_numpy.py --inputs paired1.json paired2.json --json out.json
```

`--inputs` takes any number of files produced by `h2h_w2120_live.py`.

**Important limitation.**  The fitter uses each opponent as an anchor node.
If most opponents met only one candidate, the graph has no bridges and the
maximum-likelihood estimate is unbounded (all thetas collapse to zero).  Fit
**within one pool** — inside a single pool every opponent faces every
candidate, so the bridges exist.  The numpy version converges in seconds;
`bt_fit.py` is the readable reference implementation.

## 6. Diagnostic accounting tools

```bash
python tools/diag_shed_overflow.py --arm <main.py> --episodes <ids.json>
python tools/diag_escape_window.py --arm <main.py> --episodes <ids.json>
python tools/diag_animal_econ.py  --arm <main.py> --episodes <ids.json>
```

`diag_shed_overflow.py` notes a trap worth repeating: the engine observation
handed to an agent is the **pre-step** state, so a naive reader looks one tick
late and reports phantom losses.  The tool reconstructs the hour-23 carry from
the pre-step observation and cross-checks its prediction against the realised
inventory delta.

## Running these elsewhere

The scripts were written for the machine the competition ran on, so they carry
that machine's paths as **defaults**. Every one of them takes command-line
arguments, so nothing is hard-wired — but you will need to set:

| what | where it appears | what to change |
|---|---|---|
| the engine | `sys.path.insert(0, "/root/autodl-tmp/rust_sim")` at the top of most scripts | point at your local engine |
| replay corpus | `--replays`, `--index`, `--episodes` | defaults point at `/root/autodl-tmp/live_corpus` |
| working scratch | `/tmp/...` defaults inside the diagnostics tools | any writable directory |

Two of the tools are already fully argument-driven and need no edits:
`bt_numpy.py` (and its readable twin `bt_fit.py`) and `today_analysis.py`.

The RL sandbox under `tools/rl_sandbox/` is research code rather than a
finished tool — it contains the imitation-learning and PPO experiments
described in `../COMPLETE-STORY.md` §4.4, and it expects the corpus layout
above.

Files under `docs/history/` and `docs/experiment-log.md` are **verbatim working
notes**: their paths also refer to the original machine, and they are left
that way deliberately.

## Large downloads

Replay corpora run to gigabytes, and a transfer can be interrupted by a
timeout or by the process being reaped between tool calls. Download
resumably, detached, so that restarting the same command continues instead of
starting over:

```bash
setsid nohup wget -c -q <url> -O <path> > dl.log 2>&1 < /dev/null &
```

`-c` resumes a partial file, so the target must be kept between attempts.
Prefer one resumable transfer over many parallel ones on a constrained host,
and check free disk space first — a full disk surfaces later as an unrelated
failure.

## Pitfalls we hit (so you do not have to)

| symptom | cause |
|---|---|
| phantom shed overflow | read the observation one tick late |
| phantom tile-cap waste | counted capped turns, not *discarding production events* |
| phantom animal loss | compared inventories across different seats |
| absurd win rate on a "losses" pool | frozen opponent was starved |
| Bradley-Terry collapsed to zeros | opponent graph had no bridges |
| confident conclusion from a small effect | did not drop outliers before testing |
