#!/usr/bin/env python3
"""Replay the recorded opponents of w2_120's first submission against our arms.

The Kaggle replay files from ``kaggle competitions replay`` are plain JSON.
Each replay pins the opponent's exact action tape, so any number of our arms
can be scored on the identical 131 games and compared pairwise.  Our seat is
identified from ``info.TeamNames`` ("CHEN Xiang").

Usage:
  h2h_w2120_live.py --arms A.py B.py --workers 12 --out /tmp/live131.json
"""
from __future__ import annotations

import argparse
import collections
import gzip
import importlib.util
import json
import multiprocessing
import os
import statistics
import sys

sys.path.insert(0, "/root/autodl-tmp/farm2945_dev")
sys.path.insert(0, "/root/autodl-tmp/rust_sim")
import kagsim  # noqa: E402
from kaggsim import tape as T  # noqa: E402

LIVE = "/tmp/w2120_replays"
IDS = "/tmp/w2120_ids.txt"
US = "CHEN Xiang"
ANIMALS = ("CHICKEN", "COW", "SHEEP", "GOOSE")
_CACHE = {}


def load_arm(path):
    pid = multiprocessing.current_process().pid
    if (pid, path) in _CACHE:
        return _CACHE[(pid, path)]
    spec = importlib.util.spec_from_file_location(
        f"h2h_{pid}_{abs(hash(path)) % 10**9}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fn = mod.__dict__.get("agent")
    if not callable(fn):
        fn = [v for v in mod.__dict__.values() if callable(v)][-1]
    _CACHE[(pid, path)] = fn
    return fn


def read_rep(path):
    """Read a replay regardless of extension: sniff the gzip magic instead.

    The corpus under ``live_corpus/replays`` uses ``.json.gz`` while the
    per-ref trees under ``live_corpus/refs`` keep gzip payloads in ``.json``
    files, and the Kaggle API returns plain JSON.  Sniffing the first two
    bytes handles all three.
    """
    with open(path, "rb") as fh:
        magic = fh.read(2)
    if magic == b"\x1f\x8b":
        with gzip.open(path, "rt") as fh:
            return json.load(fh)
    with open(path) as fh:
        return json.load(fh)


def tape_agent(actions):
    box = [0]

    def fn(obs, cfg=None):
        i = box[0]
        box[0] = i + 1
        return actions[i] if i < len(actions) else {
            "farmer": ["PASS"], "hands": [], "market": []}

    return fn


def our_seat(rep):
    info = rep.get("info") or {}
    names = info.get("TeamNames") or [a.get("Name") for a in (info.get("Agents") or [])]
    for i, n in enumerate(names or []):
        if n == US:
            return i
    return 0


def opp_profile(rep, seat):
    """Everything we can read about the recorded opponent without simulating."""
    steps = rep.get("steps") or []
    final = (steps[-1][seat] or {}).get("observation") or {}
    farms = final.get("farms") or []
    farm = farms[seat] if seat < len(farms) else {}
    priv = final.get("private") or {}
    herd, crops, struct = collections.Counter(), collections.Counter(), collections.Counter()
    for row in farm.get("tiles") or []:
        for t in row or []:
            if not isinstance(t, dict):
                continue
            if "animal" in t:
                herd[t["animal"]] += 1
            elif t.get("kind") == "PLANT":
                crops[t.get("crop")] += 1
            else:
                struct[t.get("kind")] += 1
    buys = collections.Counter()
    feeds = 0
    passes = collections.Counter()
    sells = collections.Counter()
    for i, pair in enumerate(steps):
        a = (pair[seat] or {}).get("action") if seat < len(pair) else None
        if not isinstance(a, dict):
            continue
        for o in (a.get("market") or []):
            if isinstance(o, (list, tuple)) and len(o) >= 3:
                if o[0] == "BUY_ANIMAL" and o[1] in ANIMALS:
                    buys[o[1]] += int(o[2])
                elif o[0] == "SELL":
                    sells[o[1]] = sells.get(o[1], 0) + int(o[2])
        acts = [a.get("farmer")] + list(a.get("hands") or [])
        if i % 24 >= 18:
            for c in acts:
                if isinstance(c, (list, tuple)) and c and c[0] == "PASS":
                    passes[i % 24] += 1
        for c in acts:
            if isinstance(c, (list, tuple)) and c and c[0] == "FEED":
                feeds += 1
    return dict(
        money=float(farm.get("money") or 0),
        herd=dict(herd), herd_tot=sum(herd.values()),
        crops=dict(crops), struct=dict(struct),
        bought=dict(buys), bought_tot=sum(buys.values()),
        sold=dict(sells), sold_tot=sum(sells.values()),
        feeds=feeds, late_pass=sum(passes.values()),
        shed={k: int(v) for k, v in (priv.get("shed") or {}).items() if int(v or 0)},
        quads=len(farm.get("unlocked_quadrants") or []),
    )


def play(rep, our, arm):
    tape = T.replay_actions(rep, 1 - our)
    seed = int(T.replay_seed(rep))
    rival = tape_agent(tape)
    sim = kagsim.Game(seed)
    while not sim.done:
        o0 = sim.observe(0) or {}
        o1 = sim.observe(1) or {}
        o0["player"] = 0
        o1["player"] = 1
        mine = arm(o0 if our == 0 else o1)
        theirs = rival(o1 if our == 0 else o0)
        if our == 0:
            sim.step(mine, theirs)
        else:
            sim.step(theirs, mine)
    farms = (sim.observe(our) or {}).get("farms") or []
    mine_money = float(farms[our]["money"]) if our < len(farms) else 0.0
    opp_money = float(farms[1 - our]["money"]) if 1 - our < len(farms) else 0.0
    return mine_money - opp_money, mine_money, opp_money


def one(task):
    path, arm_path = task
    try:
        rep = read_rep(path)
        our = our_seat(rep)
        arm = load_arm(arm_path)
        margin, mine, opp = play(rep, our, arm)
        steps = rep.get("steps") or []
        rec_mine = float((steps[-1][our] or {}).get("reward") or 0)
        rec_opp = float((steps[-1][1 - our] or {}).get("reward") or 0)
        return dict(episode=int(os.path.basename(path).split("-")[1]),
                    arm=arm_path, seat=our, margin=margin, mine=mine, opp=opp,
                    rec_mine=rec_mine, rec_opp=rec_opp,
                    fid=(opp / rec_opp if rec_opp else 1.0),
                    profile=opp_profile(rep, 1 - our),
                    team=(rep.get("info") or {}).get("TeamNames"))
    except Exception as exc:  # noqa: BLE001
        return dict(path=path, arm=arm_path,
                    error=f"{type(exc).__name__}: {exc}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", nargs="+", required=True)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", default="")
    ap.add_argument("--replays", default=LIVE)
    ap.add_argument("--ids", default=IDS)
    args = ap.parse_args()
    ids = [int(x) for x in open(args.ids).read().split()]
    files = [os.path.join(args.replays, f"episode-{i}-replay.json") for i in ids]
    files = [p for p in files if os.path.exists(p)]
    print("episodes %d" % len(files), flush=True)
    res = {}
    total_arms = len(args.arms)
    for ai, arm_path in enumerate(args.arms, 1):
        done = [0]
        t0 = __import__("time").time()

        def _tick(_r, _done=done, _t0=t0, _ai=ai, _n=len(files)):
            _done[0] += 1
            if _done[0] % 100 == 0 or _done[0] == _n:
                el = __import__("time").time() - _t0
                rate = _done[0] / el if el else 0
                print("  arm %d/%d: %d/%d  (%.1f 局/秒, 已 %.1f 分钟, 剩 %.1f 分钟)" % (
                    _ai, total_arms, _done[0], _n, rate, el / 60,
                    ((_n - _done[0]) / rate / 60) if rate else -1), flush=True)

        with multiprocessing.Pool(args.workers) as pool:
            rows = [r for r in pool.imap(one, [(p, arm_path) for p in files], chunksize=1)
                    if not _tick(r)]
        errs = [r for r in rows if "error" in r]
        ok = [r for r in rows if "error" not in r]
        res[arm_path] = ok
        w = sum(1 for r in ok if r["margin"] > 0)
        l = sum(1 for r in ok if r["margin"] < 0)
        print("%-28s n=%d err=%d  W/L %d/%d  mean margin %+.0f  total %+.0f" % (
            arm_path.split("/")[-2], len(ok), len(errs), w, l,
            statistics.mean(r["margin"] for r in ok), sum(r["margin"] for r in ok)), flush=True)
        if errs:
            print("  first err:", errs[0]["error"])
    base = args.arms[0]
    bmap = {r["episode"]: r for r in res[base]}
    for arm_path in args.arms[1:]:
        amap = {r["episode"]: r for r in res[arm_path]}
        common = sorted(set(bmap) & set(amap))
        d = [amap[e]["margin"] - bmap[e]["margin"] for e in common]
        flips_up = sum(1 for e in common
                       if bmap[e]["margin"] <= 0 < amap[e]["margin"])
        flips_dn = sum(1 for e in common
                       if amap[e]["margin"] <= 0 < bmap[e]["margin"])
        wins_a = sum(1 for e in common if amap[e]["margin"] > 0)
        wins_b = sum(1 for e in common if bmap[e]["margin"] > 0)
        sd = statistics.pstdev(d) if len(d) > 1 else 0.0
        t = (statistics.mean(d) / (sd / (len(d) ** 0.5))) if sd else 0.0
        print("\nPAIRED %s vs %s  n=%d" % (
            arm_path.split("/")[-2], base.split("/")[-2], len(common)))
        print("  wins %d -> %d   flipped L->W %d   W->L %d" % (wins_b, wins_a, flips_up, flips_dn))
        print("  mean delta %+.0f  total %+.0f  sd %.0f  t %+.2f" % (
            statistics.mean(d), sum(d), sd, t))
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(res, fh)
        print("\nwrote", args.out)


if __name__ == "__main__":
    main()
