#!/usr/bin/env python3
"""PPO + large-scale BC over routing, with dense per-decision rewards."""
import sys, json, math, gzip, argparse
sys.path.insert(0,"/tmp")
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import rl_router_env as E
from kaggsim import tape as T

DAY6=list(range(13))+list(range(100,129)); W=[104,112,120]
KS={'day6':41,'w1':3,'w2':3}; DIMS={'day6':20,'w1':10,'w2':10}
ORDER=('day6','w1','w2')
def N(k): return KS[k]*DIMS[k]

def softmax(z,T=1.0):
    z=np.asarray(z,dtype=np.float64)/max(T,1e-6); z=z-z.max(); e=np.exp(z); return e/e.sum()

class Pol:
    def __init__(self): self.W={k: np.zeros((KS[k],DIMS[k])) for k in ORDER}
    def vec(self): return np.concatenate([self.W[k].ravel() for k in ORDER])
    def setv(self,v):
        i=0
        for k in ORDER: self.W[k]=v[i:i+N(k)].reshape(KS[k],DIMS[k]); i+=N(k)

def lab_idx(tag,route):
    if route is None: return None
    if tag=='day6': return DAY6.index(route) if route in DAY6 else None
    return W.index(route) if route in W else None

def rollout(args):
    mode, vec, seed, opp, temp = args
    pol=Pol(); pol.setv(np.asarray(vec))
    rng=np.random.default_rng((seed*104729+7)%(2**31))
    def mk(k):
        def fn(f):
            p=softmax(pol.W[k]@f, temp)
            if mode=='label': return None, 0.0
            a=int(rng.choice(len(p),p=p)); return a, math.log(max(p[a],1e-12))
        return fn
    margin, samples, traj = E.run_game({'day6':mk('day6'),'w1':mk('w1'),'w2':mk('w2')}, seed, opp)
    rows=[]
    for tag,f,idx,lp,cur in samples: rows.append((tag,np.asarray(f),idx,lp,cur))
    return margin, rows, traj

def per_decision_rewards(traj):
    def g(s, default=0.0): return float(traj.get(s, default))
    return {'day6': g(480)-g(144), 'w1': g(624)-g(288), 'w2': g(718)-g(480)}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--bc-games",type=int,default=400)
    ap.add_argument("--iters",type=int,default=40)
    ap.add_argument("--batch",type=int,default=48)
    ap.add_argument("--lr",type=float,default=0.02)
    ap.add_argument("--clip",type=float,default=0.2)
    ap.add_argument("--ent",type=float,default=0.005)
    ap.add_argument("--temp",type=float,default=0.5)
    ap.add_argument("--out",default="/tmp/rl/ppo2.jsonl")
    a=ap.parse_args()
    idx=json.load(open("/root/autodl-tmp/live_corpus/index.json"))["episodes"]
    games=[]
    for e in json.load(open("/tmp/all108.json")):
        try:
            rep=json.load(gzip.open(f"/root/autodl-tmp/live_corpus/replays/episode-{e}-replay.json.gz"))
            steps=rep["steps"]; meta=idx[str(e)]
            want=float(meta["our_reward"]); r0=float(steps[-1][0].get("reward") or 0); r1=float(steps[-1][1].get("reward") or 0)
            our=0 if abs(r0-want)<=abs(r1-want) else 1
            games.append((int(T.replay_seed(rep)), T.replay_actions(rep,1-our)))
        except Exception: pass
    print("opponent tapes:", len(games), flush=True)
    zero=np.zeros(sum(N(k) for k in ORDER))
    # ---- BC labels: passthrough (current router) on many random worlds ----
    bc_tasks=[('label', zero, int(s), None, a.temp) for s in range(6000, 6000+a.bc_games)]
    data={k: [] for k in ORDER}
    with ProcessPoolExecutor(max_workers=12) as ex:
        for margin, rows, traj in ex.map(rollout, bc_tasks, chunksize=2):
            for tag,f,i,lp,cur in rows:
                li=lab_idx(tag,cur)
                if li is not None: data[tag].append((f,li))
    print("BC labels:", {k: len(v) for k,v in data.items()}, flush=True)
    pol=Pol()
    for ep in range(400):
        for k in ORDER:
            if not data[k]: continue
            g=np.zeros_like(pol.W[k])
            for f,li in data[k]:
                p=softmax(pol.W[k]@f); oh=np.zeros_like(p); oh[li]=1
                g+=np.outer(oh-p,f)
            pol.W[k]+= 0.05*g/len(data[k])
    # freeze exploration temp; scale logits for near-deterministic start
    for k in ORDER: pol.W[k]*=3.0
    # ---- evaluation helper (deterministic argmax) ----
    def eval_policy(vec, hold, temp=0.05):
        tasks=[('policy', vec, g[0], g[1], temp) for g in hold]
        with ProcessPoolExecutor(max_workers=12) as ex:
            res=list(ex.map(rollout, tasks, chunksize=1))
        return res
    hold=games[-24:]
    # baseline: true passthrough
    bt=[('label', zero, g[0], g[1], 1.0) for g in hold]
    with ProcessPoolExecutor(max_workers=12) as ex:
        base=list(ex.map(rollout, bt, chunksize=1))
    bm=np.mean([b[0] for b in base]); bw=sum(1 for b in base if b[0]>0)
    cand=eval_policy(pol.vec(), hold)
    cm=np.mean([c[0] for c in cand]); cw=sum(1 for c in cand if c[0]>0)
    print(f"BC policy vs true router (24 holdout): BC margin {cm:+.0f} wins {cw} | passthrough margin {bm:+.0f} wins {bw}", flush=True)
    json.dump([{"phase":"bc-eval","bc_margin":float(cm),"bc_wins":int(cw),"base_margin":float(bm),"base_wins":int(bw)}], open(a.out,"w"))
    # ---- PPO ----
    rng=np.random.default_rng(3)
    run_mean={k: 0.0 for k in ORDER}
    with ProcessPoolExecutor(max_workers=12) as ex:
        for it in range(a.iters):
            batch=[games[i] for i in rng.choice(len(games), size=a.batch, replace=True)]
            res=list(ex.map(rollout, [('policy',pol.vec(),g[0],g[1],a.temp) for g in batch], chunksize=1))
            advs=[]; samples=[]
            for margin,rows,traj in res:
                r=per_decision_rewards(traj)
                for tag,f,i,lp,cur in rows:
                    A=r[tag]-run_mean[tag]
                    samples.append((tag,f,i,lp,A,None))
                for k in ORDER: run_mean[k]=0.9*run_mean[k]+0.1*r[k]
            A_all=np.array([s[4] for s in samples]); scale=A_all.std()+1e-9
            for ep in range(3):
                gW={k: np.zeros_like(pol.W[k]) for k in ORDER}
                for tag,f,i,lp,A,oldp in samples:
                    p=softmax(pol.W[tag]@f,a.temp)
                    A=a.clip*A/scale
                    oh=np.zeros_like(p); oh[i]=1
                    dlog=np.outer(oh-p,f)/a.temp
                    gW[tag]+=A*dlog
                    H=-(p*np.log(p+1e-12)).sum()
                    gW[tag]+=a.ent*(-np.outer(p*(np.log(p+1e-12)+H),f))/a.temp
                for k in ORDER: pol.W[k]+=a.lr*gW[k]/max(1,len(res))
            if it%5==0 or it==a.iters-1:
                cand=eval_policy(pol.vec(), hold)
                cm=np.mean([c[0] for c in cand]); cw=sum(1 for c in cand if c[0]>0)
                print(f"ppo {it:3d}: train mean(margin) {np.mean([r[0] for r in res]):+9.0f} | holdout margin {cm:+.0f} wins {cw}/24 (base {bm:+.0f}/{bw})", flush=True)
                with open(a.out,"a") as fh: fh.write(json.dumps({"phase":"ppo","it":it,"hold_margin":float(cm),"hold_wins":int(cw)})+"\n")
    np.savez("/tmp/rl/ppo2_W.npz", **{k: pol.W[k] for k in ORDER})
    print("done")
