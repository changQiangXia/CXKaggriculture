#!/usr/bin/env python3
"""Measure the exact day-end shed-overflow loss of an arm on the frozen panel.

The engine drops every unit-carried inventory into the shed at midnight and
DELETES whatever does not fit (kaggriculture.py ``_drop_inventories_to_shed``).
Order is inventories[0] (farmer) first, then each hand, dict-insertion order
inside.  The same cap applies to a DROP action during the day, a SELL can only
draw from the shed (never from a carried inventory), and an animal carried at
midnight is destroyed with the inventory (the animal refresh only walks farm
tiles).

Timing note: the observation handed to the agent at hour 23 is the PRE-step
state -- i.e. exactly what each unit is carrying when the day ends.  The
digest of that turn's actions is applied afterwards, so the discard is
computed two ways and the two must agree:

  A) predicted = max(0, pre_carry + pre_shed - capacity)
  B) realized  = pre_total - post_total   (both from observations)

Prices are the live price at that turn when available, else the base price.

Usage:
  diag_shed_overflow.py --arm pkg_comb_pp_race/main.py \
      --episodes /tmp/all108.json --workers 10 --out /tmp/ovf_comb.json
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

BASE_PRICE = {"WHEAT": 25.0, "CARROT": 35.0, "TOMATO": 60.0,
              "STRAWBERRY": 120.0, "MELON": 250.0, "EGG": 50.0,
              "MILK": 160.0, "WOOL": 200.0, "FERTILIZER": 100.0}
ASSET = {"CHICKEN": 100.0, "COW": 400.0, "SHEEP": 500.0, "GOOSE": 300.0}
CAP = 100

_CACHE = {}


def load_arm(path):
    pid = multiprocessing.current_process().pid
    key = (pid, path)
    if key in _CACHE:
        return _CACHE[key]
    spec = importlib.util.spec_from_file_location(
        f"ovf_{pid}_{abs(hash(path)) % 10**9}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fn = mod.__dict__.get("agent")
    if not callable(fn):
        fn = [v for v in mod.__dict__.values() if callable(v)][-1]
    _CACHE[key] = fn
    return fn


def tape_agent(actions):
    box = [0]

    def fn(obs, cfg=None):
        i = box[0]
        box[0] = i + 1
        return actions[i] if i < len(actions) else {
            "farmer": ["PASS"], "hands": [], "market": []}

    return fn


def carry_total(invs):
    tot = 0
    byitem = collections.Counter()
    for inv in invs or []:
        for k, v in (inv or {}).items():
            n = int(v or 0)
            if n > 0:
                tot += n
                byitem[k] += n
    return tot, byitem


def one(task):
    path, meta, arm_path = task
    try:
        with gzip.open(path, "rt") as fh:
            rep = json.load(fh)
        steps = rep.get("steps") or []
        want = float(meta.get("our_reward") or 0)
        r0 = float(steps[-1][0].get("reward") or 0)
        r1 = float(steps[-1][1].get("reward") or 0)
        our = 0 if abs(r0 - want) <= abs(r1 - want) else 1
        rec_opp = r1 if our == 0 else r0
        tape = T.replay_actions(rep, 1 - our)
        seed = int(T.replay_seed(rep))
        arm = load_arm(arm_path)
        rival = tape_agent(tape)
        sim = kagsim.Game(seed)
        lost_units = collections.Counter()
        lost_value = 0.0
        days_hit = 0
        animal_lost = collections.Counter()
        peak = 0
        pred_total = 0
        real_total = 0
        while not sim.done:
            o0 = sim.observe(0) or {}
            o1 = sim.observe(1) or {}
            o0["player"] = 0
            o1["player"] = 1
            pre = o0 if our == 0 else o1
            pre_step = int(pre.get("step", 0))
            a_mine = arm(pre)
            a_rival = rival(o1 if our == 0 else o0)
            pre_priv = pre.get("private") or {}
            pre_shed = pre_priv.get("shed") or {}
            pre_invs = pre_priv.get("inventories") or []
            # recorded before the step: at hour 23 this IS the midnight state
            h23 = pre_step % 24 == 23
            p_carry, p_by = (carry_total(pre_invs) if h23 else (0, None))
            p_shed = (sum(int(v or 0) for v in pre_shed.values() if v)
                      if h23 else 0)
            p_assets = collections.Counter()
            if h23:
                for inv in pre_invs:
                    for k, v in (inv or {}).items():
                        if k in ASSET and int(v or 0) > 0:
                            p_assets[k] += int(v)
            if our == 0:
                sim.step(a_mine, a_rival)
            else:
                sim.step(a_rival, a_mine)
            if not h23:
                continue
            obs = sim.observe(our) or {}
            post_priv = obs.get("private") or {}
            post_carry, _ = carry_total(post_priv.get("inventories") or [])
            post_shed = sum(int(v or 0) for v in
                            (post_priv.get("shed") or {}).values() if v)
            herd_pre = collections.Counter()
            herd_post = collections.Counter()
            post_farms = obs.get("farms") or []
            if our < len(post_farms):
                for row in post_farms[our].get("tiles") or []:
                    for tile in row or []:
                        if isinstance(tile, dict) and "animal" in tile:
                            herd_post[tile["animal"]] += 1
            pre_farms = pre.get("farms") or []
            if our < len(pre_farms) and p_assets:
                for row in pre_farms[our].get("tiles") or []:
                    for tile in row or []:
                        if isinstance(tile, dict) and "animal" in tile:
                            herd_pre[tile["animal"]] += 1
                for k, v in p_assets.items():
                    # v animals were carried at h23; did the herd grow by v?
                    grown = herd_post.get(k, 0) - herd_pre.get(k, 0)
                    if v - grown > 0:
                        animal_lost[k] += v - grown
            peak = max(peak, p_shed + p_carry)
            room = max(0, CAP - p_shed)
            if p_carry > room:
                prices = (pre.get("market") or {}).get("prices") or {}
                days_hit += 1
                pred = p_carry - room
                pred_total += pred
                real_total += (p_shed + p_carry) - (post_shed + post_carry)
                left = pred
                for inv in pre_invs:
                    for item, n in list((inv or {}).items()):
                        n = int(n or 0)
                        if n <= 0 or left <= 0:
                            continue
                        take = min(n, left)
                        lost_units[item] += take
                        px = float(prices.get(item) or 0) or BASE_PRICE.get(item, 0)
                        lost_value += take * px
                        left -= take
            for inv in pre_invs:
                for k, v in (inv or {}).items():
                    if k in ASSET and int(v or 0) > 0:
                        animal_lost[k] += int(v)
        f = (sim.observe(our) or {}).get("farms") or []
        real_mine, real_opp = ((float(f[our]["money"]), float(f[1 - our]["money"]))
                               if len(f) > 1 else (0.0, 0.0))
        fid = real_opp / rec_opp if rec_opp > 0 else 1.0
        return {
            "episode": int(meta["episode"]),
            "rating": meta.get("opp_initial"),
            "outcome": meta.get("outcome"),
            "margin": real_mine - real_opp,
            "fid": fid,
            "days_hit": days_hit,
            "lost_units": int(sum(lost_units.values())),
            "lost_value": round(lost_value, 1),
            "peak_sum": peak,
            "by_item": dict(lost_units),
            "assets_lost": dict(animal_lost),
            "pred_total": pred_total,
            "real_total": real_total,
        }
    except Exception as exc:  # noqa: BLE001
        return {"episode": int(meta.get("episode") or 0),
                "error": f"{type(exc).__name__}: {exc}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--episodes", required=True)
    ap.add_argument("--replays", default="/root/autodl-tmp/live_corpus/replays")
    ap.add_argument("--index", default="/root/autodl-tmp/live_corpus/index.json")
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    keep = {int(x) for x in json.load(open(args.episodes))}
    idx = json.load(open(args.index))["episodes"]
    tasks = []
    for ep in idx.values():
        if int(ep["episode"]) not in keep:
            continue
        p = os.path.join(args.replays, "episode-%s-replay.json.gz" % ep["episode"])
        if os.path.exists(p):
            tasks.append((p, ep, args.arm))
    print("panel %d games" % len(tasks), flush=True)
    with multiprocessing.Pool(args.workers) as pool:
        rows = pool.map(one, tasks, chunksize=1)
    errs = [r for r in rows if "error" in r]
    ok = [r for r in rows if "error" not in r]
    print("errors %d" % len(errs))
    if errs:
        print("first error:", errs[0])
    w = sum(1 for r in ok if r["margin"] > 0)
    l = sum(1 for r in ok if r["margin"] < 0)
    print("W/L %d/%d  mean margin %.0f" % (w, l, statistics.mean(r["margin"] for r in ok)))
    hits = [r for r in ok if r["lost_units"] > 0]
    print("games with discard: %d/%d  total lost units %d  total lost value %s" % (
        len(hits), len(ok), sum(r["lost_units"] for r in ok),
        format(sum(r["lost_value"] for r in ok), ",.0f")))
    print("cross-check: predicted %d vs realized %d (must be equal)" % (
        sum(r["pred_total"] for r in ok), sum(r["real_total"] for r in ok)))
    if hits:
        print("per-hit mean units %.2f  mean value %s  mean days_hit %.2f  mean peak %.1f" % (
            statistics.mean(r["lost_units"] for r in hits),
            format(statistics.mean(r["lost_value"] for r in hits), ",.0f"),
            statistics.mean(r["days_hit"] for r in hits),
            statistics.mean(r["peak_sum"] for r in hits)))
    agg = collections.Counter()
    for r in ok:
        agg.update(r["by_item"])
    print("by item:", dict(agg.most_common()))
    alost = collections.Counter()
    for r in ok:
        alost.update(r["assets_lost"])
    print("assets carried into midnight:", dict(alost.most_common()))
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(ok, fh)
        print("wrote", args.out)


if __name__ == "__main__":
    main()
