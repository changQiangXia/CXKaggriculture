import gzip, json, sys, collections, importlib.util
sys.path.insert(0,'/root/autodl-tmp/rust_sim')
import kagsim
from kaggsim import tape as T
AN={'COW':400.,'SHEEP':500.,'GOOSE':300.,'CHICKEN':100.}
idx=json.load(open('/root/autodl-tmp/live_corpus/index.json'))['episodes']
panel=[int(x) for x in json.load(open('/tmp/all108.json'))]
def one(want):
    ep=[e for e in idx.values() if int(e['episode'])==want][0]
    rep=json.load(gzip.open('/root/autodl-tmp/live_corpus/replays/episode-%s-replay.json.gz'%want,'rt'))
    steps=rep['steps']; r0=float(steps[-1][0].get('reward') or 0); r1=float(steps[-1][1].get('reward') or 0)
    our=0 if abs(r0-float(ep.get('our_reward') or 0))<=abs(r1-float(ep.get('our_reward') or 0)) else 1
    tape=T.replay_actions(rep,1-our); seed=int(T.replay_seed(rep)); box=[0]
    def rival(o,c=None):
        i=box[0]; box[0]=i+1
        return tape[i] if i<len(tape) else {"farmer":["PASS"],"hands":[],"market":[]}
    spec=importlib.util.spec_from_file_location('arm','/root/autodl-tmp/farm2945_dev/pkg_comb_pp_race/main.py')
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); arm=m.agent
    sim=kagsim.Game(seed)
    bought=collections.Counter(); bought_cost=0.; esc=collections.Counter(); noWheatBuy=0
    def amap(pre):
        out=set()
        for row in pre['farms'][our]['tiles']:
            for t in row:
                if isinstance(t,dict) and 'animal' in t: out.add(t['animal'])
        return out
    while not sim.done:
        o0=sim.observe(0) or {}; o1=sim.observe(1) or {}
        o0['player']=0; o1['player']=1
        pre=o0 if our==0 else o1
        am=arm(pre); ar=rival(o1 if our==0 else o0)
        for o in (am.get('market') or []):
            if isinstance(o,list) and o and o[0]=='BUY_ANIMAL' and len(o)>=3:
                bought[o[1]]+=int(o[2]); bought_cost+=int(o[2])*AN.get(o[1],0)
        if our==0: sim.step(am,ar)
        else: sim.step(ar,am)
    post=sim.observe(our)
    herd=collections.Counter()
    for row in post['farms'][our]['tiles']:
        for t in row:
            if isinstance(t,dict) and 'animal' in t: herd[t['animal']]+=1
    shed=collections.Counter({k:int(v) for k,v in post['private']['shed'].items() if k in AN and v})
    carry=collections.Counter()
    for inv in post['private']['inventories'] or []:
        for k,v in inv.items():
            if k in AN: carry[k]+=int(v)
    return dict(episode=want,bought=dict(bought),bought_cost=bought_cost,herd=dict(herd),shed=dict(shed),carry=dict(carry))
import multiprocessing
with multiprocessing.Pool(12) as p: rows=p.map(one,panel,chunksize=1)
B=collections.Counter(); H=collections.Counter(); S=collections.Counter(); C=collections.Counter(); cost=0.
for r in rows:
    B.update(r['bought']); H.update(r['herd']); S.update(r['shed']); C.update(r['carry']); cost+=r['bought_cost']
print('bought',dict(B),'cost',cost)
print('final herd',dict(H),'shed animals',dict(S),'carry animals',dict(C))
resid={k:B[k]-H.get(k,0)-S.get(k,0)-C.get(k,0) for k in B}
print('residual (bought - final herd - shed - carry) = escapes?',resid, 'total',sum(resid.values()))
print('net capital leak if all residual escaped:',sum(resid[k]*AN.get(k,0) for k in resid))
