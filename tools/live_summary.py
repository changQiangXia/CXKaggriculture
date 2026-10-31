#!/usr/bin/env python3
"""Summarise the episodes of our live submissions from downloaded replays.

Reads either plain-JSON or gzip replays (sniffed, not by extension), finds our
seat from info.TeamNames, and reports per-game results plus the terminal
economy of both seats when requested.

Usage: live_summary.py --dir /tmp/live_c2b [--opps] [--profile]
"""
from __future__ import annotations

import argparse
import collections
import gzip
import json
import os
import statistics

US = "CHEN Xiang"
ANIMALS = ("CHICKEN", "COW", "SHEEP", "GOOSE")


def read_rep(path):
    with open(path, "rb") as fh:
        magic = fh.read(2)
    if magic == b"\x1f\x8b":
        with gzip.open(path, "rt") as fh:
            return json.load(fh)
    with open(path) as fh:
        return json.load(fh)


def seat_of(rep):
    info = rep.get("info") or {}
    names = info.get("TeamNames") or [a.get("Name") for a in (info.get("Agents") or [])]
    for i, n in enumerate(names or []):
        if n == US:
            return i
    return 0


def terminal(rep, seat):
    st = rep.get("steps") or []
    o = (st[-1][seat] or {}).get("observation") or {}
    farms = o.get("farms") or []
    f = farms[seat] if seat < len(farms) else {}
    priv = o.get("private") or {}
    herd, crops = collections.Counter(), collections.Counter()
    for row in f.get("tiles") or []:
        for t in row or []:
            if not isinstance(t, dict):
                continue
            if "animal" in t:
                herd[t["animal"]] += 1
            elif t.get("kind") == "PLANT":
                crops[t.get("crop")] += 1
    return dict(money=float(f.get("money") or 0), quads=len(f.get("unlocked_quadrants") or []),
                herd=dict(herd), herd_tot=sum(herd.values()), crops=dict(crops),
                shed=sum(int(v or 0) for v in (priv.get("shed") or {}).values()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--profile", action="store_true")
    ap.add_argument("--top", type=int, default=8)
    args = ap.parse_args()
    rows = []
    for f in sorted(os.listdir(args.dir)):
        if not f.endswith(".json"):
            continue
        try:
            rep = read_rep(os.path.join(args.dir, f))
        except Exception:
            continue
        st = rep.get("steps") or []
        our = seat_of(rep)
        names = (rep.get("info") or {}).get("TeamNames") or ["?", "?"]
        r = [float((st[-1][i] or {}).get("reward") or 0) for i in (0, 1)]
        mine, opp = r[our], r[1 - our]
        rows.append(dict(ep=int(f.split("-")[1]), mine=mine, opp=opp,
                         margin=mine - opp, team=names[1 - our], seat=our,
                         rep=rep, our=our))
    if not rows:
        print("no usable replays in", args.dir)
        return
    w = sum(1 for r in rows if r["margin"] > 0)
    l = sum(1 for r in rows if r["margin"] < 0)
    t = len(rows) - w - l
    mg = [r["margin"] for r in rows]
    print("%s: n=%d  W/L/T %d/%d/%d  (win %.1f%%)" % (
        args.dir, len(rows), w, l, t, 100 * w / len(rows)))
    print("  margin mean %+.0f  median %+.0f  min %+.0f  max %+.0f  sd %.0f" % (
        statistics.mean(mg), statistics.median(mg), min(mg), max(mg),
        statistics.pstdev(mg)))
    q = sorted(mg)
    print("  p10 %+.0f  p25 %+.0f  p75 %+.0f  p90 %+.0f" % (
        q[int(.1 * len(q))], q[int(.25 * len(q))], q[int(.75 * len(q))], q[int(.9 * len(q))]))
    print("  输在 1k 内 %d 局, 3k 内 %d 局, 崩盘(<=-20k) %d 局" % (
        sum(1 for m in mg if -1000 <= m < 0), sum(1 for m in mg if -3000 <= m < 0),
        sum(1 for m in mg if m <= -20000)))
    print("\n  --- 最惨的 %d 局 ---" % args.top)
    for r in sorted(rows, key=lambda r: r["margin"])[:args.top]:
        print("   ep %-10d %+9.0f  vs %-22s" % (r["ep"], r["margin"], r["team"][:22]))
    print("\n  --- 最好的 %d 局 ---" % args.top)
    for r in sorted(rows, key=lambda r: -r["margin"])[:args.top]:
        print("   ep %-10d %+9.0f  vs %-22s" % (r["ep"], r["margin"], r["team"][:22]))
    if args.profile:
        us = collections.Counter()
        th = collections.Counter()
        for r in rows:
            a = terminal(r["rep"], r["our"])
            b = terminal(r["rep"], 1 - r["our"])
            us.update(a["herd"])
            th.update(b["herd"])
        n = len(rows)
        print("\n  终局牲畜均值:  我方 %s (总 %.1f)  对手 %s (总 %.1f)" % (
            {k: round(v / n, 1) for k, v in us.most_common()}, sum(us.values()) / n,
            {k: round(v / n, 1) for k, v in th.most_common()}, sum(th.values()) / n))
        uw = [terminal(r["rep"], r["our"]) for r in rows]
        tw = [terminal(r["rep"], 1 - r["our"]) for r in rows]
        print("  终局现金中位:  我方 %.0f   对手 %.0f" % (
            statistics.median(x["money"] for x in uw), statistics.median(x["money"] for x in tw)))
        print("  终局象限: 我方 %s  对手 %s" % (
            dict(collections.Counter(x["quads"] for x in uw)),
            dict(collections.Counter(x["quads"] for x in tw))))


if __name__ == "__main__":
    main()
