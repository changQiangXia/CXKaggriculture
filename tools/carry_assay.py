import gzip, json, sys, importlib.util, collections
sys.path.insert(0,'/root/autodl-tmp/rust_sim')
import kagsim
from kaggsim import tape as T
IDX=json.load(open('/root/autodl-tmp/live_corpus/index.json'))['episodes']
ovf=json.load(open('/tmp/ovf_comb.json'))
margins={r['episode']:r['margin'] for r in ovf}
worst=sorted(margins.items(), key=lambda kv: kv[1])[:2]
BASE={'WHEAT':25.,'CARROT':35.,'TOMATO':60.,'STRAWBERRY':120.,'MELON':250.,'EGG':50.,'MILK':160.,'WOOL':200.,'FERTILIZER':100.,'COW':400.,'SHEEP':500.,'GOOSE':300.,'CHICKEN':100.}
def run(want, mode):
    ep=[e for e in IDX.values() if int(e['episode'])==want][0]
    rep=json.load(gzip.open('/root/autodl-tmp/live_corpus/replays/episode-%s-replay.json.gz'%want,'rt'))
    steps=rep['steps']; r0=float(steps[-1][0].get('reward') or 0); r1=float(steps[-1][1].get('reward') or 0)
    our=0 if abs(r0-float(ep.get('our_reward') or 0))<=abs(r1-float(ep.get('our_reward') or 0)) else 1
    tape=T.replay_actions(rep,1-our); seed=int(T.replay_seed(rep)); box=[0]
    def rival(o,c=None):
        i=box[0]; box[0]=i+1
        return tape[i] if i<len(tape) else {"farmer":["PASS"],"hands":[],"market":[]}
    spec=importlib.util.spec_from_file_location('arm','/root/autodl-tmp/farm2945_dev/pkg_comb_pp_race/main.py')
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); arm=mod.agent
    sim=kagsim.Game(seed); final_carry=None; final_shed=None; final_money=None
    while not sim.done:
        o0=sim.observe(0) or {}; o1=sim.observe(1) or {}
        o0['player']=0; o1['player']=1
        pre=o0 if our==0 else o1; st=int(pre.get('step',0))
        am=arm(pre); ar=rival(o1 if our==0 else o0)
        if mode=='lastday_pass' and st>=696:
            am={'farmer':['PASS'],'hands':[['PASS']]*len(am.get('hands') or []),'market':[]}
        if our==0: sim.step(am,ar)
        else: sim.step(ar,am)
        post=sim.observe(our) or {}
        if st==719:
            pv=post.get('private') or {}
            final_carry=pv.get('inventories'); final_shed=dict(pv.get('shed') or {})
    f=(sim.observe(our) or {}).get('farms') or []
    money=float(f[our]['money']); opp=float(f[1-our]['money'])
    val=sum(BASE.get(k,0)*max(0,int(v or 0)) for inv in (final_carry or []) for k,v in (inv or {}).items())
    return money,opp,money-opp,final_carry,final_shed,val
for want,_ in worst:
    a=run(want,'normal'); b=run(want,'lastday_pass')
    print('ep',want)
    print('  normal margin %+.0f  terminal carry %s value %.0f  shed %s' % (a[2],a[3],a[5],a[4]))
    print('  lastdayPASS margin %+.0f carry %s value %.0f shed %s' % (b[2],b[3],b[5],b[4]))
