#!/usr/bin/env python3
"""Find games featuring the current leaderboard leaders in the public replay dump.

The public `georgy_dataset` parquet files store whole Kaggle replays, and each
replay's `info.TeamNames` identifies both seats.  Parsing the full JSON is far
too slow (170 GB of text), so we match the team-name bytes directly against the
raw payload -- no JSON decode at all.

Usage: scan_top_teams.py --out /tmp/top_games.json
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

import pyarrow.parquet as pq
import pyarrow.compute as pc

TOP = ["M & M & P & Q", "6x8 B200 Galaxy Run", "DSM", "CDE", "DECEM", "有辣条有权",
       "Anton Tikhonov", "Farmcore", "tetsuya & yuanzhe & guoqin", "KawattaTaido",
       "Azat Akhtyamov", "Yizhou", "Unknown Mother-Goose", "MarvinTMB", "Majkel1337"]

DEFAULT_DIR = "/root/autodl-tmp/public_intel/georgy_dataset"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=DEFAULT_DIR)
    ap.add_argument("--out", default="/tmp/top_games.json")
    ap.add_argument("--teams", nargs="*", default=TOP)
    args = ap.parse_args()
    hits = collections.Counter()
    eps = collections.defaultdict(list)
    files = [f for f in sorted(os.listdir(args.dir))
             if f.endswith(".parquet") and ".prev" not in f]
    for f in files:
        try:
            pf = pq.ParquetFile(os.path.join(args.dir, f))
        except Exception as exc:  # noqa: BLE001
            print("%s SKIP (%s)" % (f, type(exc).__name__), file=sys.stderr, flush=True)
            continue
        nrg = pf.num_row_groups
        for gi in range(nrg):
            try:
                rg = pf.read_row_group(gi)
            except Exception:
                continue
            # Match with pyarrow's native string kernel -- a Python-level
            # ``needle in payload`` scan over ~10 MB payloads is far too slow.
            mask = None
            per_name = {}
            for name in args.teams:
                m = pc.match_substring(rg.column("replay_json"), name)
                per_name[name] = m
                mask = m if mask is None else pc.or_(mask, m)
            if not pc.any(mask).as_py():
                continue
            ids = rg.column("episode_id")
            sel = ids.filter(mask).to_pylist()
            for name, m in per_name.items():
                hit_ids = ids.filter(m).to_pylist()
                if hit_ids:
                    hits[name] += len(hit_ids)
                    eps[name] += [[f, int(x)] for x in hit_ids]
        print("%s done  hits=%d  (rowgroups %d)" % (f, sum(hits.values()), nrg),
              file=sys.stderr, flush=True)
    print("=== hits ===")
    for k, v in hits.most_common():
        print("  %-30s %4d games" % (k, v))
    with open(args.out, "w") as fh:
        json.dump({"hits": dict(hits), "eps": dict(eps)}, fh)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
