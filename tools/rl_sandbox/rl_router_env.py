#!/usr/bin/env python3
"""Routing-policy sandbox: a policy overrides day-6 / W1 / W2 route choices; tape does the rest."""
import sys, os, importlib.util, numpy as np
sys.path.insert(0,"/root/autodl-tmp/rust_sim"); sys.path.insert(0,"/tmp")
import kagsim
from kaggsim import tape as T

BASE="/tmp/abl/comb_pp_race/main.py"
ROUTE_HOOK='''

# >>> routing hook for RL
_ROUTER_HOOK = {'f': None}
_ORIG_ROUTER = _router
def _router_rl(observation, step, state):
    r = _ORIG_ROUTER(observation, step, state)
    try:
        if _ROUTER_HOOK['f'] is not None:
            h = _ROUTER_HOOK['f'](observation, step, state, r)
            if h is not None: r = h
    except Exception:
        pass
    return r
_router = _router_rl
'''
HOOK_PATH="/tmp/rl/router_hooked.py"
os.makedirs("/tmp/rl", exist_ok=True)
src=open(BASE,encoding="utf-8",errors="replace").read()
# 必须在 make_agent 调用前替换 _router
assert src.count("_IMPL=make_agent(_ROUTES,router=_router,**_SETTINGS)")==1
src=src.replace("_IMPL=make_agent(_ROUTES,router=_router,**_SETTINGS)",
                ROUTE_HOOK+"\n_IMPL=make_agent(_ROUTES,router=_router,_ROUTES_RL,**{} )" if False else
                f"{ROUTE_HOOK}\n_IMPL=make_agent(_ROUTES,router=_router,**_SETTINGS)")
open(HOOK_PATH,"w").write(src)

def load():
    spec=importlib.util.spec_from_file_location("rh_"+str(np.random.randint(10**9)), HOOK_PATH)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

DAY6_ACTIONS=[0,1,2,3,4,5,6,7,8,9,10,11,12]
W_ACTIONS=[104,112,120]

def feat_day6(obs, state):
    shops=tuple((obs.get('town') or {}).get('unlocked_shops') or [])[:2]
    names=['BAKERY','BRUNCH_SPOT','FARMERS_MARKET','ICE_CREAM_SHOP','PET_CAFE','PIZZA_SHOP','SMOOTHIE_SHOP','YARN_STORE']
    f=np.zeros(8+8+4, dtype=np.float64)
    for i,s in enumerate(shops[:2]):
        if s in names: f[i*8+names.index(s)]=1.0
    try:
        me=obs['farms'][obs['player']]; rv=obs['farms'][1-obs['player']]
        f[16]=min(float(me['money']),60000)/60000.0
        f[17]=min(float(rv['money']),60000)/60000.0
        f[18]=min(int(obs['market']['inventory']['WHEAT']),12000)/12000.0
        f[19]=1.0 if 'YARN_STORE' in shops else 0.0
    except Exception: pass
    return f

def feat_window(obs, state, tag):
    f=np.zeros(10, dtype=np.float64)
    try:
        me=obs['farms'][obs['player']]; rv=obs['farms'][1-obs['player']]
        f[0]=min(float(me['money']),80000)/80000.0
        f[1]=min(float(rv['money']),80000)/80000.0
        pr=obs['market']['prices']; inv=obs['market']['inventory']
        f[2]=pr.get('MILK',0)/160.0; f[3]=pr.get('WOOL',0)/200.0; f[4]=pr.get('EGG',0)/50.0
        f[5]=inv.get('WHEAT',0)/12000.0
        f[6]=1.0 if tag=='w1' else 0.0
        f[7]=len(me.get('unlocked_quadrants') or [])/4.0
        f[8]=sum(1 for row in me.get('tiles') or [] for t in row if isinstance(t,dict) and t.get('animal'))/30.0
        f[9]=1.0 if any(s=='YARN_STORE' for s in (obs.get('town',{}).get('unlocked_shops') or [])) else 0.0
    except Exception: pass
    return f

def run_game(policy, seed, opp_tape, our_seat=0):
    """policy: dict with callables day6(feat)->(idx,logp), w1(feat)->..., w2(feat)->... ; returns (margin, samples)"""
    mod=load()
    samples=[]
    def hook(obs, step, state, current):
        try:
            if step==144:
                f=feat_day6(obs,state); idx,lp=policy['day6'](f)
                samples.append(('day6', f, idx, lp, current))
                return DAY6_ACTIONS[idx]
            if step==288:
                f=feat_window(obs,state,'w1'); idx,lp=policy['w1'](f)
                samples.append(('w1', f, idx, lp, current))
                return W_ACTIONS[idx]
            if step==480:
                f=feat_window(obs,state,'w2'); idx,lp=policy['w2'](f)
                samples.append(('w2', f, idx, lp, current))
                return W_ACTIONS[idx]
        except Exception:
            return None
        return None
    mod._ROUTER_HOOK['f']=hook
    ag=mod.agent
    box=[0]
    def rival(o,c=None):
        i=box[0]; box[0]=i+1
        if opp_tape is None: return {"farmer":["PASS"],"hands":[],"market":[]}
        return opp_tape[i] if i<len(opp_tape) else {"farmer":["PASS"],"hands":[],"market":[]}
    sim=kagsim.Game(int(seed)); g=0
    traj={}
    while not sim.done and g<800:
        g+=1
        o0=sim.observe(0) or {}; o1=sim.observe(1) or {}
        o0["player"]=0; o1["player"]=1
        a=ag(o0)
        try:
            st=int(o0.get('step',0))
            if st in (144,288,480,624,718):
                fm=o0['farms']; traj[st]=float(fm[0]['money'])-float(fm[1]['money'])
        except Exception: pass
        sim.step(a, rival(o1))
    f=sim.observe(0)["farms"]
    margin=float(f[0]["money"])-float(f[1]["money"])
    return margin, samples, traj
