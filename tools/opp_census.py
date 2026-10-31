#!/usr/bin/env python3
"""Cross-sectional fingerprint of every recorded opponent in the local corpus.

For each episode we read the FINAL observation of both seats straight from the
replay (no simulation): that observation is the engine's post-day-29 state, so
it carries the whole terminal economy.  Per seat we record final bank, live
herd and structure inventory, the buy/sell order mix over the whole game from
the recorded actions, FEED effort, labour slack by hour band, and the terminal
shed.  Grouping by `opp_sub` then answers "what do the strong opponents have
that the weak ones do not".

Usage: opp_census.py --out /tmp/opp_census.json [--limit N] [--workers 12]
"""
from __future__ import annotations

import argparse
import collections
import gzip
import json
import multiprocessing
import os
import statistics
import sys

CORPUS = "/root/autodl-tmp/live_corpus"
ANIMALS = ("CHICKEN", "COW", "SHEEP", "GOOSE")
PRODUCTS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG",
            "MILK", "WOOL", "FERTILIZER")


def obs_of(entry):
    if entry is None:
        return None
    o = entry.get("observation")
    return o if isinstance(o, dict) else entry


def seat_stats(rep, seat):
    steps = rep.get("steps") or []
    final = obs_of(steps[-1][seat]) or {}
    farms = final.get("farms") or []
    farm = farms[seat] if seat < len(farms) else {}
    priv = final.get("private") or {}
    herd = collections.Counter()
    structures = collections.Counter()
    for row in farm.get("tiles") or []:
        for t in row or []:
            if isinstance(t, dict) and "animal" in t:
                herd[t["animal"]] += 1
            elif isinstance(t, dict):
                structures[t.get("kind")] += 1
    buys = collections.Counter()
    sells = collections.Counter()
    feeds = 0
    passes = collections.Counter()
    units = collections.Counter()
    for i, pair in enumerate(steps):
        if seat >= len(pair):
            continue
        a = (pair[seat] or {}).get("action")
        if not isinstance(a, dict):
            continue
        hour = i % 24
        for o in (a.get("market") or []):
            if not isinstance(o, (list, tuple)) or len(o) < 3:
                continue
            if o[0] == "BUY_ANIMAL" and o[1] in ANIMALS:
                buys[o[1]] += int(o[2])
            elif o[0] == "SELL":
                sells[o[1]] = sells.get(o[1], 0) + int(o[2])
        acts = [a.get("farmer")] + list(a.get("hands") or [])
        units[hour] += len(acts)
        for c in acts:
            if not isinstance(c, (list, tuple)) or not c:
                continue
            if c[0] == "FEED":
                feeds += 1
            elif c[0] == "PASS":
                passes[hour] += 1
    shed = {k: int(v) for k, v in (priv.get("shed") or {}).items() if int(v or 0)}
    return dict(
        money=float(farm.get("money") or 0),
        herd=dict(herd), herd_tot=sum(herd.values()),
        structures=dict(structures),
        buys=dict(buys), bought=sum(buys.values()),
        sells=dict(sells), sold=sum(sells.values()),
        feeds=feeds,
        late_pass=sum(passes[h] for h in range(18, 24)),
        late_units=sum(units[h] for h in range(18, 24)),
        all_pass=sum(passes.values()), all_units=sum(units.values()),
        shed=shed,
        unlocked=len(farm.get("unlocked_quadrants") or []),
    )


def one(path):
    try:
        with gzip.open(path, "rt") as fh:
            rep = json.load(fh)
        return path, rep
    except Exception as exc:  # noqa: BLE001
        return path, {"error": f"{type(exc).__name__}: {exc}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default=os.path.join(CORPUS, "index.json"))
    ap.add_argument("--replays", default=os.path.join(CORPUS, "replays"))
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default="/tmp/opp_census.json")
    args = ap.parse_args()
    idx = json.load(open(args.index))["episodes"]
    items = list(idx.values())
    if args.limit:
        items = items[:args.limit]
    tasks = []
    for e in items:
        p = os.path.join(args.replays, "episode-%s-replay.json.gz" % e["episode"])
        if os.path.exists(p):
            tasks.append((p, e))
    print("episodes %d (files %d)" % (len(items), len(tasks)), flush=True)
    rows = []
    with multiprocessing.Pool(args.workers) as pool:
        for (path, rep), (_, meta) in zip(pool.imap(one, [t[0] for t in tasks], chunksize=1), tasks):
            if not isinstance(rep, dict) or "error" in rep or not rep.get("steps"):
                continue
            steps = rep["steps"]
            want = float(meta.get("our_reward") or 0)
            try:
                r0 = float(steps[-1][0].get("reward") or 0)
                r1 = float(steps[-1][1].get("reward") or 0)
            except Exception:
                continue
            our = 0 if abs(r0 - want) <= abs(r1 - want) else 1
            mine = seat_stats(rep, our)
            opp = seat_stats(rep, 1 - our)
            rows.append(dict(episode=int(meta["episode"]), ref=meta.get("ref"),
                             opp_sub=meta.get("opp_sub"), opp_initial=meta.get("opp_initial"),
                             outcome=meta.get("outcome"),
                             mine=mine, opp=opp))
    print("usable %d" % len(rows))
    groups = collections.defaultdict(list)
    for r in rows:
        groups[r["opp_sub"]].append(r)
    summary = []
    for sub, g in groups.items():
        if len(g) < 5:
            continue
        summary.append(dict(
            sub=sub, games=len(g),
            opp_money=statistics.median(r["opp"]["money"] for r in g),
            mine_money=statistics.median(r["mine"]["money"] for r in g),
            our_winrate=statistics.mean(1.0 if r["mine"]["money"] > r["opp"]["money"] else 0.0 for r in g),
            opp_bought=statistics.median(r["opp"]["bought"] for r in g),
            opp_herd=statistics.median(r["opp"]["herd_tot"] for r in g),
            opp_feeds=statistics.median(r["opp"]["feeds"] for r in g),
            opp_sold=statistics.median(r["opp"]["sold"] for r in g),
            opp_late_units=statistics.median(r["opp"]["late_units"] for r in g),
            opp_unlocked=statistics.median(r["opp"]["unlocked"] for r in g),
        ))
    summary.sort(key=lambda s: -s["opp_money"])
    print("\n%-10s %5s %10s %10s %7s %7s %6s %7s %8s %6s" % (
        "opp_sub", "n", "opp$", "our$", "weW%", "bought", "herd", "feeds", "lateU", "quads"))
    for s in summary[:20]:
        print("%-10s %5d %10.0f %10.0f %6.1f%% %7.0f %6.0f %7.0f %8.0f %6.0f" % (
            s["sub"], s["games"], s["opp_money"], s["mine_money"], s["our_winrate"] * 100,
            s["opp_bought"], s["opp_herd"], s["opp_feeds"], s["opp_late_units"], s["opp_unlocked"]))
    print("\n--- weakest 10 ---")
    for s in summary[-10:]:
        print("%-10s %5d %10.0f %10.0f %6.1f%% %7.0f %6.0f %7.0f %8.0f %6.0f" % (
            s["sub"], s["games"], s["opp_money"], s["mine_money"], s["our_winrate"] * 100,
            s["opp_bought"], s["opp_herd"], s["opp_feeds"], s["opp_late_units"], s["opp_unlocked"]))
    with open(args.out, "w") as fh:
        json.dump(dict(rows=rows, summary=summary), fh)
    print("\nwrote", args.out)


if __name__ == "__main__":
    main()
