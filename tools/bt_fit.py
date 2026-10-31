#!/usr/bin/env python3
"""Fit a Bradley-Terry model over paired replay results.

The competition's final leaderboard is a Bradley-Terry rerun, which uses ONLY
win/loss -- not margins.  This tool re-scores our candidates under that exact
criterion, locally.

How the graph is built
----------------------
Every recorded opponent becomes a node, so each game is an edge

    candidate  --beat-->  opponent

and the four candidates are connected through the opponents they share, which
is what makes them comparable on one scale.  The opponent field is the anchor:
we normalise the opponents' mean ability to 0, so a candidate's rating reads
as "how far above the average opponent in this pool it is".

    sigma  = 1 / sqrt(scale)   (K=400 scale, BT logit convention)
    theta_i <- W_i / sum_j n_ij / (theta_i + theta_j)      (MM update)

Usage
-----
  bt_fit.py --inputs /tmp/live131c.json /tmp/w2n_34_compare.json ...
  bt_fit.py --inputs A.json B.json --regularize 0.01 --json out.json

Each input is a dict {arm_path: [row, ...]} as written by h2h_w2120_live.py;
rows need `episode`, `margin` and `team`/`seat` (or `profile` for the name).
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import os
import sys


def load_rows(path):
    with open(path) as fh:
        d = json.load(fh)
    out = {}
    for arm, rows in d.items():
        if not isinstance(rows, list):
            continue
        good = [r for r in rows if "error" not in r and "margin" in r]
        if good:
            out[arm] = good
    return out


def opp_name(row):
    team = row.get("team") or []
    seat = int(row.get("seat", 0))
    if len(team) > 1:
        return str(team[1 - seat])
    prof = row.get("profile") or {}
    return str(prof.get("name") or "unknown")


def short(arm):
    base = os.path.basename(os.path.dirname(arm)) or os.path.basename(arm)
    return base.replace("main.py", "").strip("/") or base


def build_games(inputs):
    """-> list of (winner, loser); opponent nodes are prefixed with 'opp:'.

    Opponents are also reported with the set of candidates they faced, so that
    the caller can keep only the ones that actually bridge two or more
    candidates -- a one-game opponent contributes no comparison information
    but does add a severely under-determined node that stops MM from settling.
    """
    games = []
    partners = collections.defaultdict(set)
    for path in inputs:
        for arm, rows in load_rows(path).items():
            cand = short(arm)
            for r in rows:
                o = opp_name(r)
                if not o or o == "unknown":
                    continue
                partners[o].add(cand)
                if r["margin"] > 0:
                    games.append((cand, "opp:" + o))
                elif r["margin"] < 0:
                    games.append(("opp:" + o, cand))
    return games, partners


def keep_bridging(games, partners, min_partners=2):
    """Drop opponents seen by fewer than ``min_partners`` distinct candidates."""
    keep = {o for o, c in partners.items() if len(c) >= min_partners}
    filtered = [g for g in games if g[0].replace("opp:", "") in keep
                or g[1].replace("opp:", "") in keep]
    return filtered, keep


def fit(games, iters=4000, tol=1e-10, regularize=0.0, anchor_prefix="opp:"):
    names = sorted({g[0] for g in games} | {g[1] for g in games})
    idx = {n: i for i, n in enumerate(names)}
    n = len(names)
    W = [0.0] * n
    nij = collections.defaultdict(float)
    for w, l in games:
        i, j = idx[w], idx[l]
        W[i] += 1.0
        nij[(i, j)] += 1.0
        nij[(j, i)] += 1.0
    theta = [1.0] * n
    # opponents used as the scale anchor
    anchors = [i for i, nm in enumerate(names) if nm.startswith(anchor_prefix)]
    for it in range(iters):
        new = [0.0] * n
        for i in range(n):
            den = 0.0
            for (a, b), c in nij.items():
                if a != i:
                    continue
                den += c / (theta[i] + theta[b])
            if den <= 0:
                new[i] = theta[i]
                continue
            num = W[i] + regularize * 1.0
            new[i] = num / (den + (regularize / max(theta[i], 1e-12)))
        # normalise on the anchor set so the scale is stable
        if anchors:
            m = sum(new[i] for i in anchors) / len(anchors)
        else:
            m = sum(new) / n
        if m > 0:
            new = [v / m for v in new]
        delta = max(abs(new[i] - theta[i]) for i in range(n))
        theta = new
        if delta < tol:
            break
    return names, idx, theta, it


def to_elo(theta):
    """Log-odds -> a 400-point Elo-like scale."""
    return [400.0 / math.log(10.0) * math.log(max(t, 1e-12)) for t in theta]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="+", required=True)
    ap.add_argument("--regularize", type=float, default=0.0,
                    help="L2 pull of each win count toward 1 (Bayesian prior)")
    ap.add_argument("--json", default="")
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--show-opponents", action="store_true")
    ap.add_argument("--min-partners", type=int, default=2,
                    help="keep only opponents faced by >= N distinct candidates")
    args = ap.parse_args()

    games_all, partners = build_games(args.inputs)
    games, keep = keep_bridging(games_all, partners, args.min_partners)
    if not games:
        print("no games parsed (after bridging filter: %d opponents kept)" % len(keep))
        return 1
    names, idx, theta, iters = fit(games, regularize=args.regularize)
    elo = to_elo(theta)
    cands = [(nm, elo[i], theta[i]) for i, nm in enumerate(names)
             if not nm.startswith("opp:")]
    opps = [(nm, elo[i]) for i, nm in enumerate(names) if nm.startswith("opp:")]
    wl = collections.Counter()
    for w, l in games:
        wl[w] += 1
    print("games=%d / %d  bridging-opponents=%d (>=%d candidates)  nodes=%d  iters=%d  reg=%.4f" % (
        len(games), len(games_all), len(keep), args.min_partners, len(names),
        iters, args.regularize))
    print("\n=== 候选（相对对手池均值的 Elo 刻度）===")
    print("%-22s %9s %9s %7s" % ("candidate", "elo", "theta", "wins"))
    for nm, e, t in sorted(cands, key=lambda x: -x[1]):
        print("%-22s %+9.1f %9.4f %7d" % (nm, e, t, wl[nm]))
    print("\n=== 两两胜率矩阵（行击败列的概率）===")
    order = [nm for nm, _, _ in sorted(cands, key=lambda x: -x[1])]
    hdr = "".join("%-14s" % nm[:13] for nm in order)
    print("%-22s%s" % ("", hdr))
    for a in order:
        row = ""
        for b in order:
            if a == b:
                row += "%-14s" % "--"
                continue
            p = theta[idx[a]] / (theta[idx[a]] + theta[idx[b]])
            row += "%-14s" % ("%.1f%%" % (100 * p))
        print("%-22s%s" % (a, row))
    if args.show_opponents:
        print("\n=== 对手（前 %d，锚定均值=0）===" % args.top)
        for nm, e in sorted(opps, key=lambda x: -x[1])[:args.top]:
            print("  %-34s %+8.1f" % (nm[4:], e))
    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"elo": {nm: elo[i] for i, nm in enumerate(names)},
                       "theta": {nm: theta[i] for i, nm in enumerate(names)},
                       "games": len(games), "iters": iters}, fh)
        print("\nwrote", args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
