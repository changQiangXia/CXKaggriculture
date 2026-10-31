#!/usr/bin/env python3
"""Local RL sandbox: a policy controls MILK selling in a window; tape drives everything else."""
import importlib.util, sys, json, gzip, random, collections
import numpy as np
sys.path.insert(0,"/root/autodl-tmp/rust_sim")
import kagsim
from kaggsim import tape as T
ROOT="/root/autodl-tmp"
BASE="/tmp/abl/comb_pp_race/main.py"
HOOK = '''

# >>> RL hook: policy controls MILK sells in [LO,HI)
_RL = {'policy': None, 'lo': 432, 'hi': 719, 'mode':'tape', 'trace': None}
_RL_PARENT = {'f': agent}
def _rl_agent(observation, configuration=None):
    a = _RL_PARENT['f'](observation, configuration)
    try:
        step=int(observation.get('step',0))
        if _RL['lo']<=step<_RL['hi'] and _RL['policy'] is not None:
            prices=observation['market']['prices']; priv=observation['private']
            # available milk: shed + carried
            shed=int(priv.get('shed',{}).get('MILK',0) or 0)
            carried=sum(int((inv or {}).get('MILK',0)) for inv in (priv.get('inventories') or []))
            avail=shed+carried
            frac=_RL['policy'](step, observation, avail)
            mkt=[list(o) for o in (a.get('market') or []) if not (o and len(o)>1 and o[0]=='SELL' and o[1]=='MILK')]
            q=int(round(max(0.0,min(1.0,frac))*avail))
            if q>0 and len(mkt)<10: mkt.append(['SELL','MILK',q])
            if _RL['trace'] is not None:
                _RL['trace'].append((step, avail, float(frac), q, int(prices.get('MILK',0) or 0)))
            a=dict(a); a['market']=mkt
    except Exception:
        pass
    return a
agent=_rl_agent
'''
hooked_path="/tmp/rl/hooked.py"
import os; os.makedirs("/tmp/rl", exist_ok=True)
open(hooked_path,"w").write(open(BASE,encoding="utf-8",errors="replace").read()+HOOK)

def load(path):
    spec=importlib.util.spec_from_file_location("rl_"+str(abs(hash(path))%10**9), path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def _rl_features(step, obs, avail):
    day=step//24; hour=step%24
    pr=obs['market']['prices']; inv=obs['market']['inventory']
    return np.array([1.0, day/30.0, hour/24.0,
                     (pr.get('MILK',0) or 0)/160.0,
                     (inv.get('MILK',0) or 0)/10000.0,
                     min(avail,40)/40.0,
                     1.0 if hour>=20 else 0.0,
                     (step-432)/288.0], dtype=np.float64)

def run_episode(policy, seed, opp_tape=None, lo=432, hi=700, trace=False, replay=None, our_seat=0):
    mod=load(hooked_path)
    mod._RL['policy']=policy; mod._RL['lo']=lo; mod._RL['hi']=hi
    mod._RL['trace']=[] if trace else None
    ag=mod.agent
    if opp_tape is None:
        def rival(o,c=None): return {"farmer":["PASS"],"hands":[],"market":[]}
    else:
        box=[0]
        def rival(o,c=None):
            i=box[0]; box[0]=i+1
            return opp_tape[i] if i<len(opp_tape) else {"farmer":["PASS"],"hands":[],"market":[]}
    sim=kagsim.Game(int(seed)); g=0
    revenue=0.0; milk_sold=0
    while not sim.done and g<800:
        g+=1
        o0=sim.observe(0) or {}; o1=sim.observe(1) or {}
        o0["player"]=0; o1["player"]=1
        step=int(o0.get('step',0))
        a_mine=ag(o0)
        if lo<=step<hi:
            pre=int(o0['market']['prices'].get('MILK',0) or 0)
            q=0
            for m in (a_mine.get('market') or []):
                if m and len(m)>2 and m[0]=='SELL' and m[1]=='MILK': q+=int(m[2])
            revenue += q*pre; milk_sold += q
        sim.step(a_mine, rival(o1))
    f=sim.observe(0)["farms"][0]
    return dict(final=float(f["money"]), revenue=revenue, sold=milk_sold,
                trace=(mod._RL['trace'] or []))
