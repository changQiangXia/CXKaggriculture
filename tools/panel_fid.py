#!/usr/bin/env python3
"""Freeze-tape panel with TAPE-FIDELITY filtering.

Why: a recorded opponent cannot react.  If our candidate starves it (buys the
wheat it wanted, floods its sell book), the tape keeps playing its recorded
moves into nothing and the "win" is an artifact.  The public 2945-farm
write-up calls this out (evaluation lesson #2) and filters panels to games
where the frozen opponent keeps >= 95% of its recorded final bank.

This runner replays a candidate against recorded opponent tapes (same
semantics as trace_panel.py / pool_live_losses.py) and reports BOTH:

  * raw W/L,
  * fidelity-filtered W/L  (opponent realized >= --fid x recorded bank),

plus the fidelity distribution and the list of "suspect" games.

Usage:
  panel_fid.py --arm pkg_k_slh48/main.py \
      --episodes panel_runs/w6/live56629633_episodes.json \
      --replays /root/autodl-tmp/live_corpus/replays \
      --workers 10 --out panel_runs/w6/fid_slh48_live92.json
"""
import argparse
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

_CACHE = {}


def load_arm(path):
    pid = multiprocessing.current_process().pid
    key = (pid, path)
    if key in _CACHE:
        return _CACHE[key]
    spec = importlib.util.spec_from_file_location(f"pf_{pid}_{abs(hash(path)) % 10**9}", path)
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
        return actions[i] if i < len(actions) else {"farmer": ["PASS"], "hands": [], "market": []}

    return fn


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
        while not sim.done:
            o0 = sim.observe(0) or {}
            o1 = sim.observe(1) or {}
            o0["player"] = 0
            o1["player"] = 1
            a_mine = arm(o0 if our == 0 else o1)
            a_rival = rival(o1 if our == 0 else o0)
            sim.step(a_mine, a_rival) if our == 0 else sim.step(a_rival, a_mine)
        f = (sim.observe(our) or {}).get("farms") or []
        real_mine, real_opp = (float(f[our]["money"]), float(f[1 - our]["money"])) if len(f) > 1 else (0.0, 0.0)
        fid = real_opp / rec_opp if rec_opp > 0 else 1.0
        return {
            "episode": int(meta["episode"]),
            "rating": meta.get("opp_initial"),
            "outcome": meta.get("outcome"),
            "margin": real_mine - real_opp,
            "rec_mine": rec_mine,
            "rec_opp": rec_opp,
            "real_mine": real_mine,
            "real_opp": real_opp,
            "fid": fid,
        }
    except Exception as exc:  # noqa: BLE001
        return {"episode": int(meta.get("episode") or 0), "error": f"{type(exc).__name__}: {exc}"}


def band_of(rating):
    if rating is None:
        return "unknown"
    r = float(rating)
    if r < 1600:
        return "<1600"
    if r < 2000:
        return "1600-2000"
    if r < 2400:
        return "2000-2400"
    if r < 2600:
        return "2400-2600"
    return "2600+"


def agg(rows, fid_thr, key=None):
    g = [r for r in rows if key is None or band_of(r["rating"]) == key]
    n = len(g)
    if not n:
        return None
    raw_w = sum(1 for r in g if r["margin"] > 0)
    raw_l = sum(1 for r in g if r["margin"] < 0)
    fl = [r for r in g if r["fid"] >= fid_thr]
    fw = sum(1 for r in fl if r["margin"] > 0)
    fll = sum(1 for r in fl if r["margin"] < 0)
    return {
        "n": n,
        "raw": f"{raw_w}W/{raw_l}L",
        "raw_wr": raw_w / (raw_w + raw_l) * 100 if raw_w + raw_l else 0.0,
        "fid_n": len(fl),
        "filt": f"{fw}W/{fll}L",
        "filt_wr": fw / (fw + fll) * 100 if fw + fll else 0.0,
        "mean_fid": statistics.mean(r["fid"] for r in g),
        "share_low": sum(1 for r in g if r["fid"] < fid_thr) / n,
        "margin": statistics.mean(r["margin"] for r in g),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--episodes", required=True)
    ap.add_argument("--replays", default="/root/autodl-tmp/live_corpus/replays")
    ap.add_argument("--index", default="/root/autodl-tmp/live_corpus/index.json")
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--fid", type=float, default=0.95)
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
    print("episodes: %d (panel %d, index %d)" % (len(tasks), len(keep), len(idx)), flush=True)
    with multiprocessing.Pool(args.workers) as pool:
        res = pool.map(one, tasks, chunksize=1)
    ok = [r for r in res if r and "error" not in r]
    print("ok %d errors %d" % (len(ok), len(res) - len(ok)))

    print("\n%-12s %5s %14s %14s %9s %8s %9s" % ("band", "n", "raw", "filt", "mean_fid", "low<fid", "margin"))
    for key in (None, "<1600", "1600-2000", "2000-2400", "2400-2600", "2600+"):
        a = agg(ok, args.fid, key)
        if not a:
            continue
        print("%-12s %5d %14s %14s %9.3f %7.1f%% %+9.0f" % (
            key or "ALL", a["n"], a["raw"], a["filt"], a["mean_fid"], a["share_low"] * 100, a["margin"]))

    # fidelity histogram
    buckets = [0, 0.5, 0.7, 0.85, 0.95, 1.05, 1.2, 1.5, 10 ** 9]
    hist = [0] * (len(buckets) - 1)
    for r in ok:
        for i in range(len(buckets) - 1):
            if buckets[i] <= r["fid"] < buckets[i + 1]:
                hist[i] += 1
                break
    print("\nfidelity histogram:", ", ".join(
        f"[{buckets[i]:.2f},{buckets[i+1]:.2f}): {hist[i]}" for i in range(len(hist))))

    low = [r for r in ok if r["fid"] < args.fid]
    fake_wins = [r for r in low if r["margin"] > 0]
    print("suspect games (fid<%.2f): %d, of which raw wins: %d" % (args.fid, len(low), len(fake_wins)))
    if low:
        print("worst fidelity:", ", ".join(
            f"ep{r['episode']}({r['fid']:.2f},{r['margin']:+.0f})"
            for r in sorted(low, key=lambda r: r["fid"])[:8]))

    if args.out:
        json.dump({"arm": args.arm, "panel": args.episodes, "fid_thr": args.fid, "rows": res},
                  open(args.out, "w"))
        print("wrote", args.out)


if __name__ == "__main__":
    main()
