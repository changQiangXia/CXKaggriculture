#!/usr/bin/env python3
"""Direct head-to-head between two agents on identical worlds.

This is the cleanest possible test of relative strength: no opponent pool, no
selection bias and no ladder path.  Each world is played TWICE with the seat
assignment swapped, so any first-player advantage cancels and the two games of
a pair share the same world.

Usage:
  duel.py --a agent_a.py --b agent_b.py --seeds 1-64 --workers 12
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import multiprocessing
import os
import statistics
import sys

sys.path.insert(0, "/root/autodl-tmp/rust_sim")
import kagsim  # noqa: E402

_CACHE = {}


def load_arm(path):
    pid = multiprocessing.current_process().pid
    if (pid, path) in _CACHE:
        return _CACHE[(pid, path)]
    spec = importlib.util.spec_from_file_location(
        f"duel_{pid}_{abs(hash(path)) % 10**9}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fn = mod.__dict__.get("agent")
    if not callable(fn):
        fn = [v for v in mod.__dict__.values() if callable(v)][-1]
    _CACHE[(pid, path)] = fn
    return fn


def one(task):
    seed, a_path, b_path, a_seat = task
    try:
        A = load_arm(a_path)
        B = load_arm(b_path)
        sim = kagsim.Game(seed)
        while not sim.done:
            o0 = sim.observe(0) or {}
            o1 = sim.observe(1) or {}
            o0["player"] = 0
            o1["player"] = 1
            a_obs = o0 if a_seat == 0 else o1
            b_obs = o1 if a_seat == 0 else o0
            act_a = A(a_obs)
            act_b = B(b_obs)
            if a_seat == 0:
                sim.step(act_a, act_b)
            else:
                sim.step(act_b, act_a)
        farms = (sim.observe(0) or {}).get("farms") or []
        banks = [float(f["money"]) for f in farms]
        return dict(seed=seed, a_seat=a_seat, a_bank=banks[a_seat],
                    b_bank=banks[1 - a_seat], margin=banks[a_seat] - banks[1 - a_seat])
    except Exception as exc:  # noqa: BLE001
        return dict(seed=seed, a_seat=a_seat, error=f"{type(exc).__name__}: {exc}")


def parse_seeds(spec):
    out = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-")
            out += list(range(int(lo), int(hi) + 1))
        else:
            out.append(int(part))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--seeds", default="1-32")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    seeds = parse_seeds(args.seeds)
    tasks = [(s, args.a, args.b, seat) for s in seeds for seat in (0, 1)]
    print("worlds %d  games %d (each world played both seats)" % (len(seeds), len(tasks)),
          flush=True)
    done = [0]

    def tick(_r):
        done[0] += 1
        if done[0] % 50 == 0 or done[0] == len(tasks):
            print("  %d/%d" % (done[0], len(tasks)), flush=True)
        return False

    with multiprocessing.Pool(args.workers) as pool:
        rows = [r for r in pool.imap(one, tasks, chunksize=1) if not tick(r)]
    errs = [r for r in rows if "error" in r]
    ok = [r for r in rows if "error" not in r]
    if errs:
        print("errors %d, first: %s" % (len(errs), errs[0]["error"]))
    a_name = os.path.basename(os.path.dirname(args.a)) or "A"
    b_name = os.path.basename(os.path.dirname(args.b)) or "B"
    aw = sum(1 for r in ok if r["margin"] > 0)
    bw = sum(1 for r in ok if r["margin"] < 0)
    print("\n%s %dW / %s %dW   (ties %d, of %d games)" % (
        a_name, aw, b_name, bw, len(ok) - aw - bw, len(ok)))
    mg = [r["margin"] for r in ok]
    print("margin (A-B): mean %+.0f  median %+.0f  sd %.0f" % (
        statistics.mean(mg), statistics.median(mg), statistics.pstdev(mg)))
    # paired per-world: average the two seats, then test across worlds
    byseed = {}
    for r in ok:
        byseed.setdefault(r["seed"], []).append(r)
    pairs = [statistics.mean(x["margin"] for x in v) for v in byseed.values() if len(v) == 2]
    if pairs:
        sd = statistics.pstdev(pairs)
        n = len(pairs)
        t = statistics.mean(pairs) / (sd / (n ** 0.5)) if sd else 0.0
        print("per-world mean %+.0f  sd %.0f  n=%d  t=%+.2f" % (
            statistics.mean(pairs), sd, n, t))
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(ok, fh)
        print("wrote", args.out)


if __name__ == "__main__":
    main()
