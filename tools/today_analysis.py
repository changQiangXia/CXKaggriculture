#!/usr/bin/env python3
"""Join today's ladder games with the leaderboard to measure opponent strength.

For every game we read our result from the replay and look up the OPPONENT's
current leaderboard rank/score by team name, then bucket our win rate by that
opponent strength.  Also reports the raw W/L, margin distribution, and which
opponents beat us.

Usage:
  today_analysis.py --lb /tmp/lb_full.csv \
      --games comb2b=/tmp/today_c2b w2_120=/tmp/today_w2n
"""
from __future__ import annotations

import argparse
import csv
import collections
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live_summary import read_rep, seat_of  # noqa: E402

US = "CHEN Xiang"


def load_lb(path):
    by_name = {}
    by_id = {}
    with open(path, newline="") as fh:
        for r in csv.DictReader(fh):
            try:
                rank = int(r["rank"]); score = float(r["score"])
            except (KeyError, ValueError, TypeError):
                continue
            nm = (r.get("teamName") or "").strip()
            if nm:
                by_name.setdefault(nm, (rank, score))
            if r.get("teamId"):
                by_id[str(r["teamId"])] = (rank, score)
    return by_name, by_id


def games(dirpath):
    out = []
    for f in sorted(os.listdir(dirpath)):
        if not f.endswith(".json"):
            continue
        p = os.path.join(dirpath, f)
        if os.path.getsize(p) == 0:
            continue
        try:
            rep = read_rep(p)
        except Exception:
            continue
        st = rep.get("steps") or []
        our = seat_of(rep)
        names = (rep.get("info") or {}).get("TeamNames") or []
        if len(names) < 2:
            continue
        r = [float((st[-1][i] or {}).get("reward") or 0) for i in (0, 1)]
        out.append(dict(ep=int(f.split("-")[1]), margin=r[our] - r[1 - our],
                        mine=r[our], opp=r[1 - our],
                        opp_name=names[1 - our], our_seat=our))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lb", required=True)
    ap.add_argument("--games", nargs="+", required=True,
                    help="label=dir")
    args = ap.parse_args()
    by_name, _ = load_lb(args.lb)
    print("leaderboard teams: %d" % len(by_name))
    for spec in args.games:
        label, _, d = spec.partition("=")
        g = games(d)
        if not g:
            continue
        w = sum(1 for x in g if x["margin"] > 0)
        l = sum(1 for x in g if x["margin"] < 0)
        mg = [x["margin"] for x in g]
        print("\n" + "=" * 78)
        print("%s : %d 局   %dW / %dL  (胜率 %.1f%%)" % (label, len(g), w, l, 100 * w / len(g)))
        print("  margin 中位 %+.0f  均值 %+.0f  sd %.0f   p10 %+.0f  p90 %+.0f" % (
            statistics.median(mg), statistics.mean(mg), statistics.pstdev(mg),
            sorted(mg)[int(.1 * len(mg))], sorted(mg)[int(.9 * len(mg))]))
        # opponent strength buckets by leaderboard rank
        buckets = [("前 50", 1, 51), ("51-200", 51, 201), ("201-500", 201, 501),
                   ("501-1000", 501, 1001), ("1001-3000", 1001, 3001), ("3000+", 3001, 10 ** 9),
                   ("未上榜", None, None)]
        agg = collections.OrderedDict((b[0], [0, 0, []]) for b in buckets)
        unknown = []
        for x in g:
            hit = by_name.get(x["opp_name"])
            if hit is None:
                agg["未上榜"][0] += 1
                agg["未上榜"][1] += 1 if x["margin"] > 0 else 0
                unknown.append(x["opp_name"])
                continue
            rank, score = hit
            for name, lo, hi in buckets:
                if lo is None:
                    continue
                if lo <= rank <= hi:
                    agg[name][0] += 1
                    agg[name][1] += 1 if x["margin"] > 0 else 0
                    agg[name][2].append(x["margin"])
                    break
        print("\n  %-12s %5s %5s %8s %12s" % ("对手排名", "局数", "胜", "胜率", "平均margin"))
        for name, (n, ww, mm) in agg.items():
            if not n:
                continue
            rate = "%.0f%%" % (100 * ww / n) if n else "-"
            mean = "%+.0f" % statistics.mean(mm) if mm else "-"
            print("  %-12s %5d %5d %8s %12s" % (name, n, ww, rate, mean))
        # strongest opponents we faced / that beat us
        scored = []
        for x in g:
            hit = by_name.get(x["opp_name"])
            if hit:
                scored.append((hit[0], hit[1], x))
        scored.sort(key=lambda t: t[0])
        print("\n  对手最强（对方排名最高的 5 局）:")
        for rank, score, x in scored[:5]:
            print("     #%-6d %-22s 分 %7.1f   我们 %s  by %+8.0f" % (
                rank, x["opp_name"][:22], score, "胜" if x["margin"] > 0 else "负", x["margin"]))
        losses = [t for t in scored if t[2]["margin"] < 0]
        losses.sort(key=lambda t: t[0])
        print("  击败我们的最强对手（前 5）:")
        for rank, score, x in losses[:5]:
            print("     #%-6d %-22s 分 %7.1f   差 %+8.0f" % (
                rank, x["opp_name"][:22], score, x["margin"]))


if __name__ == "__main__":
    main()
