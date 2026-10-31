#!/usr/bin/env python3
"""REINFORCE for the local MILK-sell policy (linear Gaussian, shaped reward=realized revenue)."""
import sys, math, random, json
sys.path.insert(0,"/tmp")
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import rl_env

D=8
SIGMA=0.25

def feats(step, obs, avail):
    day=step//24; hour=step%24
    pr=obs['market']['prices']; inv=obs['market']['inventory']
    return np.array([1.0, day/30.0, hour/24.0,
                     (pr.get('MILK',0) or 0)/160.0,
                     (inv.get('MILK',0) or 0)/10000.0,
                     min(avail,40)/40.0,
                     1.0 if hour>=20 else 0.0,
                     (step-432)/288.0], dtype=np.float64)

def rollout(args):
    w, sigma, seed = args
    tr=[]
    def pol(step, obs, avail):
        f=feats(step,obs,avail)
        mu=float(np.clip(w@f, 0.0, 1.0))
        a=float(np.clip(mu+sigma*np.random.randn(), 0.0, 1.0))
        tr.append((f, mu, a))
        return a
    r=rl_env.run_episode(pol, seed, trace=True)
    # realized revenue from hook trace: min(q, avail)*price  (q already <= avail)
    rev=sum(min(q,av)*p for (_,av,fr,q,p) in r["trace"])
    return rev, r["final"], tr, r["trace"]

def main(iters=60, pop=48, seeds=None, lr=0.05, out="/tmp/rl/curve.jsonl"):
    rng=np.random.default_rng(0)
    w=np.zeros(D)
    if seeds is None:
        seeds=list(range(1500,1532))
    hist=[]
    base=0.0
    with ProcessPoolExecutor(max_workers=12) as ex:
        for it in range(iters):
            tasks=[(w, SIGMA, int(s)) for s in rng.choice(seeds, size=pop, replace=True)]
            res=list(ex.map(rollout, tasks, chunksize=1))
            R=np.array([r[0] for r in res], dtype=np.float64)
            b=float(np.mean(R))
            g=np.zeros(D)
            for rev,_,tr,_ in res:
                adv=rev-b
                for f,mu,a in tr:
                    g += adv * ((a-mu)/(SIGMA**2)) * f
            g /= max(1,len(res))
            w = w + lr*g
            hist.append((it, float(np.mean(R)), float(b), float(np.std(R))))
            print(f"iter {it:3d}: mean_rev {np.mean(R):9.1f} adv_base {b:9.1f} std {np.std(R):8.1f} |w| {np.linalg.norm(w):.3f}", flush=True)
            json.dump(hist, open(out,"w"))
    np.save("/tmp/rl/W.npy", w)
    print("learned w:", np.round(w,3))

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("--iters",type=int,default=60); ap.add_argument("--pop",type=int,default=48)
    a=ap.parse_args(); main(iters=a.iters, pop=a.pop)
