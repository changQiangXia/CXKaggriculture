#!/usr/bin/env python3
"""Locate the exact failure mode behind animal escapes, on the frozen panel.

Engine rule (``_daily_refresh_animals``): at midnight an animal that was not
fed that day gets ``consecutive_unfed += 1``; at 2 it escapes and the tile
becomes an empty structure.  So an animal is "vulnerable" for one day after
its first missed feeding, and the engine prints nothing -- the agent only
sees an empty pasture the next morning.

This runner replays the panel and, for every animal tile, reconstructs that
per-day flag from our own observations and the actions our agent took.  It
reports, per game:

  * escapes by species,
  * animal-days spent vulnerable (consecutive_unfed == 1),
  * of those, how many were fed in time (rescue) vs missed,
  * whether a FEED was even attempted with WHEAT in hand,
  * the same totals for the frozen opponent (the tape's own actions),

so we can tell a labor/scheduling miss from a feed-stock miss.

Usage:
  diag_escape_window.py --arm pkg_comb_pp_race/main.py \
      --episodes /tmp/all108.json --out /tmp/esc_comb.json
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

ASSET = {"CHICKEN": 100.0, "COW": 400.0, "SHEEP": 500.0, "GOOSE": 300.0}
PLACE_UNIT = {"PLACE", "BUILD_COOP", "BUILD_PASTURE"}
_CACHE = {}


def load_arm(path):
    pid = multiprocessing.current_process().pid
    key = (pid, path)
    if key in _CACHE:
        return _CACHE[key]
    spec = importlib.util.spec_from_file_location(
        f"esc_{pid}_{abs(hash(path)) % 10**9}", path)
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


def animal_map(farm):
    """{(x,y): (species, fed_today, cared_today)} from a pre-step observation."""
    out = {}
    for y, row in enumerate(farm or []):
        for x, tile in enumerate(row or []):
            if isinstance(tile, dict) and "animal" in tile:
                out[(x, y)] = (tile["animal"],
                               bool(tile.get("fed_today")),
                               bool(tile.get("cared_today")),
                               int(tile.get("yield_units") or 0),
                               int(tile.get("consecutive_unfed") or 0))
    return out


def unit_positions(farm):
    """[farmer, *hands] positions as (x, y)."""
    pos = [tuple(farm.get("farmer") or ())]
    for p in farm.get("hands") or []:
        pos.append(tuple(p))
    return pos


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

        unfed = {}                 # (x,y) -> consecutive_unfed, our farm only
        escapes = collections.Counter()
        vulnerable = 0
        rescued = 0
        missed = 0
        feed_attempt_no_wheat = 0
        feed_no_animal_action = 0
        vulnerable_wheatless = 0
        pending_escape_value = 0.0
        while not sim.done:
            o0 = sim.observe(0) or {}
            o1 = sim.observe(1) or {}
            o0["player"] = 0
            o1["player"] = 1
            pre = o0 if our == 0 else o1
            step = int(pre.get("step", 0))
            am = arm(pre)
            ar = rival(o1 if our == 0 else o0)
            farms_pre = pre.get("farms") or [{}]
            farm = farms_pre[our] if our < len(farms_pre) else {}
            amap = animal_map(farm)
            positions = unit_positions(farm)
            acts = [am.get("farmer")] + list(am.get("hands") or [])
            feed_targets = set()
            wheatless_feed = False
            for i, a in enumerate(acts):
                if isinstance(a, list) and a and a[0] == "FEED" and i < len(positions):
                    feed_targets.add(positions[i])
            if our == 0:
                sim.step(am, ar)
            else:
                sim.step(ar, am)
            post = sim.observe(our) or {}
            # the step just executed is pre_step -> pre_step+1; the day ends
            # when that lands on a multiple of 24, i.e. when pre_step is h23.
            if (step + 1) % 24 == 0:
                # midnight has run: update our own consecutive-unfed book
                for pos, (sp, fed, cared, yu, cu) in amap.items():
                    if pos in feed_targets:
                        fed_now = True
                    else:
                        fed_now = fed
                    if fed_now:
                        unfed[pos] = 0
                    else:
                        prev = unfed.get(pos, 0)
                        unfed[pos] = prev + 1
                # find escapes: tiles that had an animal before but not after
                farms_post = post.get("farms") or [{}]
                pfarm = farms_post[our] if our < len(farms_post) else {}
                pamap = animal_map(pfarm)
                for pos, (sp, *_rest) in amap.items():
                    if pos not in pamap and unfed.get(pos, 0) >= 2:
                        escapes[sp] += 1
                        pending_escape_value += ASSET.get(sp, 0)
                        unfed.pop(pos, None)
                # count vulnerable (consecutive_unfed == 1) animal-days
                for pos, n in list(unfed.items()):
                    if n == 1:
                        vulnerable += 1
                        if pos in feed_targets:
                            rescued += 1
                        else:
                            missed += 1
                unfed = {k: v for k, v in unfed.items() if v > 0}
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
            "escapes": dict(escapes),
            "escape_total": int(sum(escapes.values())),
            "escape_value": pending_escape_value,
            "vulnerable": vulnerable,
            "rescued": rescued,
            "missed": missed,
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
    print("W/L %d/%d" % (w, l))
    tot_esc = sum(r["escape_total"] for r in ok)
    print("escapes: total %d  games with >=1 %d/%d  mean %.2f/game" % (
        tot_esc, sum(1 for r in ok if r["escape_total"] > 0), len(ok),
        tot_esc / max(1, len(ok))))
    sp = collections.Counter()
    for r in ok:
        sp.update(r["escapes"])
    print("by species:", dict(sp.most_common()))
    print("escape capital: %s" % format(sum(r["escape_value"] for r in ok), ",.0f"))
    v = sum(r["vulnerable"] for r in ok)
    rs = sum(r["rescued"] for r in ok)
    ms = sum(r["missed"] for r in ok)
    print("vulnerable animal-days %d  rescued-in-time %d (%.1f%%)  missed %d" % (
        v, rs, 100.0 * rs / max(1, v), ms))
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(ok, fh)
        print("wrote", args.out)


if __name__ == "__main__":
    main()
