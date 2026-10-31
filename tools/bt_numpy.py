#!/usr/bin/env python3
"""Vectorised Bradley-Terry MM fitter for sparse head-to-head graphs.

Same model as ``bt_fit.py`` but the update is expressed with numpy over a
precomputed adjacency array, so 10^5-10^6 iterations are cheap.  That matters
here because our graph has ~200 opponent nodes of degree <=3, and the raw MM
iteration converges only slowly on nodes like that.

    theta_i <- W_i / sum_j n_ij / (theta_i + theta_j)

with an optional ridge prior (``reg``) that pulls each node toward weight 1,
and the opponent set re-scaled to mean 1 so the candidates share one scale.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bt_fit import build_games, keep_bridging, load_rows, opp_name, short  # noqa: E402


def build_graph(games):
    names = sorted({g[0] for g in games} | {g[1] for g in games})
    idx = {n: i for i, n in enumerate(names)}
    n = len(names)
    W = np.zeros(n)
    pairs = collections.defaultdict(float)
    for w, l in games:
        i, j = idx[w], idx[l]
        W[i] += 1.0
        pairs[(min(i, j), max(i, j))] += 1.0
    # symmetric edge lists: for every (i,j) both directions appear
    src, dst, cnt = [], [], []
    for (i, j), c in pairs.items():
        if i == j:
            continue
        src += [i, j]
        dst += [j, i]
        cnt += [c, c]
    return names, idx, W, (np.array(src), np.array(dst), np.array(cnt))


def fit(names, W, adj, anchor_mask, iters=200000, tol=1e-12, reg=0.0, verbose=0):
    src, dst, cnt = adj
    n = len(names)
    theta = np.ones(n)
    for it in range(1, iters + 1):
        den = np.zeros(n)
        np.add.at(den, src, cnt / (theta[src] + theta[dst]))
        num = W + reg
        new = np.where(den > 0, num / (den + reg / np.maximum(theta, 1e-300)),
                       theta)
        m = new[anchor_mask].mean()
        if m > 0:
            new = new / m
        delta = float(np.max(np.abs(new - theta)))
        theta = new
        if delta < tol:
            return theta, it, delta
        if verbose and it % verbose == 0:
            print("    iter %6d  max|delta| %.3e" % (it, delta), flush=True)
    return theta, iters, delta


def to_elo(theta):
    return 400.0 / math.log(10.0) * np.log(np.maximum(theta, 1e-300))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="+", required=True)
    ap.add_argument("--min-partners", type=int, default=2)
    ap.add_argument("--reg", type=float, default=0.0)
    ap.add_argument("--iters", type=int, default=200000)
    ap.add_argument("--tol", type=float, default=1e-12)
    ap.add_argument("--verbose", type=int, default=0)
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    games_all, partners = build_games(args.inputs)
    games, keep = keep_bridging(games_all, partners, args.min_partners)
    if not games:
        print("no games after bridging filter")
        return 1
    names, idx, W, adj = build_graph(games)
    anchor_mask = np.array([nm.startswith("opp:") for nm in names])
    theta, iters, delta = fit(names, W, adj, anchor_mask,
                              iters=args.iters, tol=args.tol, reg=args.reg,
                              verbose=args.verbose)
    elo = to_elo(theta)
    cands = [nm for nm in names if not nm.startswith("opp:")]
    print("games=%d/%d  nodes=%d  bridging=%d  reg=%.3f  iters=%d  max|delta|=%.2e" % (
        len(games), len(games_all), len(names), len(keep), args.reg, iters, delta))
    print("\n=== 候选实力（Bradley-Terry，Elo 刻度，对手池均值=0）===")
    print("%-16s %10s %9s %7s" % ("candidate", "elo", "theta", "wins"))
    for nm in sorted(cands, key=lambda x: -elo[idx[x]]):
        print("%-16s %+10.1f %9.4f %7.0f" % (nm, elo[idx[nm]], theta[idx[nm]], W[idx[nm]]))
    print("\n=== 两两胜率（行击败列）===")
    order = sorted(cands, key=lambda x: -elo[idx[x]])
    print("%-16s%s" % ("", "".join("%-13s" % nm[:12] for nm in order)))
    for a in order:
        row = ""
        for b in order:
            if a == b:
                row += "%-13s" % "--"
            else:
                p = theta[idx[a]] / (theta[idx[a]] + theta[idx[b]])
                row += "%-13s" % ("%.1f%%" % (100 * p))
        print("%-16s%s" % (a, row))
    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"elo": {nm: float(elo[idx[nm]]) for nm in names},
                       "theta": {nm: float(theta[idx[nm]]) for nm in names},
                       "games": len(games), "iters": iters, "delta": delta,
                       "reg": args.reg}, fh)
        print("\nwrote", args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
