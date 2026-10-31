#!/usr/bin/env python3
"""Compare the animal economy of our comb seat against the recorded opponent,
split by win/loss, on the frozen 108-game panel.

For each side we replay the WHOLE farm (not just our seat) and record:
  * BUY_ANIMAL orders (units per species)  -> purchases
  * FEED actions, and FEED actions landing on an animal that was hungry in
    the danger window (the tape's own rescue effort)
  * PASS actions per hour band (labour slack)
  * final live herd per species
  * escapes = purchased - final - carried/shed  (identity-checked)

Usage: diag_animal_econ.py --episodes /tmp/all108.json --out /tmp/econ.json
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

ANIMALS = ("CHICKEN", "COW", "SHEEP", "GOOSE")
_CACHE = {}


def load_arm(path):
    pid = multiprocessing.current_process().pid
    if (pid, path) in _CACHE:
        return _CACHE[(pid, path)]
    spec = importlib.util.spec_from_file_location(
        f"ae_{pid}_{abs(hash(path)) % 10**9}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fn = mod.__dict__.get("agent")
    if not callable(fn):
        fn = [v for v in mod.__dict__.values() if callable(v)][-1]
    _CACHE[(pid, path)] = fn
    return fn


def tape_agent(actions):
    box = [0]

    def fn(obs, cfg=None):
        i = box[0]
        box[0] = i + 1
        return actions[i] if i < len(actions) else {
            "farmer": ["PASS"], "hands": [], "market": []}

    return fn


def side_snapshot(obs, seat):
    farm = (obs.get("farms") or [{}])[seat] if seat < len(obs.get("farms") or []) else {}
    live = collections.Counter()
    fed = set()
    for y, row in enumerate(farm.get("tiles") or []):
        for x, t in enumerate(row or []):
            if isinstance(t, dict) and "animal" in t:
                live[t["animal"]] += 1
                if t.get("fed_today"):
                    fed.add((x, y))
    positions = [tuple(farm.get("farmer") or ())]
    for p in farm.get("hands") or []:
        positions.append(tuple(p))
    return live, fed, positions, farm


def audit_side(obs, action, seat):
    """Stats for one seat's own action in one turn."""
    live, fed, positions, farm = side_snapshot(obs, seat)
    invs = ((obs.get("private") or {}).get("inventories") or []) if seat == int(obs.get("player", -1)) else []
    acts = [action.get("farmer")] + list(action.get("hands") or [])
    out = dict(buys=collections.Counter(), feeds=0, feed_danger=0, passes=0, units=len(positions))
    for o in (action.get("market") or []):
        if isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] == "BUY_ANIMAL" and o[1] in ANIMALS:
            out["buys"][o[1]] += int(o[2])
    for i, a in enumerate(acts):
        if not isinstance(a, (list, tuple)) or not a:
            continue
        if a[0] == "FEED":
            out["feeds"] += 1
            if i < len(positions) and positions[i] in fed:
                out["feed_danger"] += 1
        elif a[0] == "PASS":
            out["passes"] += 1
    return out


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
        rec_mine = r0 if our == 0 else r1
        tape = T.replay_actions(rep, 1 - our)
        seed = int(T.replay_seed(rep))
        arm = load_arm(arm_path)
        rival = tape_agent(tape)
        sim = kagsim.Game(seed)
        acc = {0: dict(buys=collections.Counter(), feeds=0, feed_danger=0, passes=0,
                       pass_h=collections.Counter(), unit_h=collections.Counter(),
                       animal_turns=0, danger_turns=0),
               1: dict(buys=collections.Counter(), feeds=0, feed_danger=0, passes=0,
                       pass_h=collections.Counter(), unit_h=collections.Counter(),
                       animal_turns=0, danger_turns=0)}
        while not sim.done:
            o0 = sim.observe(0) or {}
            o1 = sim.observe(1) or {}
            o0["player"] = 0
            o1["player"] = 1
            # our action must be the FIRST call on this observation
            our_obs = o0 if our == 0 else o1
            am = arm(our_obs)
            ar = rival(o1 if our == 0 else o0)
            a_by_seat = {0: am, 1: ar} if our == 0 else {0: ar, 1: am}
            hour = int(our_obs.get("step", 0)) % 24
            for seat in (0, 1):
                obs = o0 if seat == 0 else o1
                st = audit_side(obs, a_by_seat[seat], seat)
                a = acc[seat]
                a["buys"].update(st["buys"])
                a["feeds"] += st["feeds"]
                a["feed_danger"] += st["feed_danger"]
                a["passes"] += st["passes"]
                a["pass_h"][hour] += st["passes"]
                a["unit_h"][hour] += st["units"]
                live = side_snapshot(obs, seat)[0]
                a["animal_turns"] += sum(live.values())
            if our == 0:
                sim.step(am, ar)
            else:
                sim.step(ar, am)
        final = sim.observe(0) or {}
        farms = final.get("farms") or []
        rows = {}
        for seat in (0, 1):
            key = "mine" if seat == our else "opp"
            herd = collections.Counter()
            if seat < len(farms):
                for row in farms[seat].get("tiles") or []:
                    for t in row or []:
                        if isinstance(t, dict) and "animal" in t:
                            herd[t["animal"]] += 1
            a = acc[seat]
            bought = sum(a["buys"].values())
            live_tot = sum(herd.values())
            rows[key] = dict(
                buys=dict(a["buys"]), bought=bought, herd=dict(herd), live=live_tot,
                escape=bought - live_tot, feeds=a["feeds"], feed_danger=a["feed_danger"],
                passes=a["passes"], animal_turns=a["animal_turns"],
                late_pass=sum(a["pass_h"][h] for h in range(18, 24)),
                late_units=sum(a["unit_h"][h] for h in range(18, 24)),
                money=float(farms[seat]["money"]) if seat < len(farms) else 0.0)
        return dict(episode=int(meta["episode"]), margin=rows["mine"]["money"] - rows["opp"]["money"],
                    our=our, mine=rows["mine"], opp=rows["opp"])
    except Exception as exc:  # noqa: BLE001
        return {"episode": int(meta.get("episode") or 0),
                "error": f"{type(exc).__name__}: {exc}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="/root/autodl-tmp/farm2945_dev/pkg_comb_pp_race/main.py")
    ap.add_argument("--episodes", default="/tmp/all108.json")
    ap.add_argument("--replays", default="/root/autodl-tmp/live_corpus/replays")
    ap.add_argument("--index", default="/root/autodl-tmp/live_corpus/index.json")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", default="/tmp/econ_comb.json")
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
        print(errs[0])
    for grp, sel in (("ALL", lambda r: True),
                     ("WINS", lambda r: r["margin"] > 0),
                     ("LOSSES", lambda r: r["margin"] < 0)):
        g = [r for r in ok if sel(r)]
        if not g:
            continue
        print("\n== %s (n=%d)" % (grp, len(g)))
        for side in ("mine", "opp"):
            bt = collections.Counter()
            herd = collections.Counter()
            for r in g:
                bt.update(r[side]["buys"])
                herd.update(r[side]["herd"])
            print("  %-4s bought %s (tot %d) | final herd %s (tot %d) | escapes %d | FEED %d (danger %d) | latePASS %.0f/%.0f" % (
                side, dict(bt), sum(bt.values()), dict(herd), sum(herd.values()),
                sum(bt.values()) - sum(herd.values()),
                sum(r[side]["feeds"] for r in g), sum(r[side]["feed_danger"] for r in g),
                statistics.mean(r[side]["late_pass"] for r in g),
                statistics.mean(r[side]["late_units"] for r in g)))
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(ok, fh)
        print("\nwrote", args.out)


if __name__ == "__main__":
    main()
