import gzip, json, sys, collections, importlib.util, multiprocessing
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
    atrisk=set(); atrisk_days=collections.Counter(); esc=collections.Counter()
    feed_ops_target=0; feed_ops_other=0; feed_ops_total=0
    slack_by_hour=collections.Counter(); units_by_hour=collections.Counter()
    wheat_in_inv_h22=0; atrisk_with_wheat_nearby_h22=0; atrisk_h22=0
    danger_feed=0; waste_feed=0
    prev=None
    while not sim.done:
        o0=sim.observe(0) or {}; o1=sim.observe(1) or {}
        o0['player']=0; o1['player']=1
        pre=o0 if our==0 else o1; st=int(pre['step']); hour=st%24
        f=pre['farms'][our]
        amap={}; fedset=set()
        for y,row in enumerate(f['tiles']):
            for x,t in enumerate(row):
                if isinstance(t,dict) and 'animal' in t:
                    amap[(x,y)]=t['animal']
                    if t.get('fed_today'): fedset.add((x,y))
        invtot=collections.Counter()
        for i,inv in enumerate(pre['private']['inventories'] or []):
            for k,v in (inv or {}).items(): invtot[k]+=int(v or 0)
        # at midnight step (hour 0) we know which animals were unfed on the previous day
        if hour==0 and prev is not None:
            p_amap,p_fed,p_inv,p_positions=prev
            for pos,sp in amap.items():
                if pos not in p_fed: atrisk.add(pos)
            for pos in list(atrisk):
                if pos not in amap: continue
        am=arm(pre); ar=rival(o1 if our==0 else o0)
        positions=[tuple(f['farmer'])]+[tuple(p) for p in f['hands']]
        acts=[am.get('farmer')]+list(am.get('hands') or [])
        for i,a in enumerate(acts):
            if isinstance(a,list) and a and a[0]=='FEED':
                feed_ops_total+=1
                if i<len(positions) and positions[i] in atrisk: feed_ops_target+=1
                else: feed_ops_other+=1
        units_by_hour[hour]+=len(positions)
        for i,a in enumerate(acts):
            if isinstance(a,list) and a and a[0]=='PASS': slack_by_hour[hour]+=1
        if hour>=22:
            atrisk_h22+=len(atrisk)
            for i,a in enumerate(acts):
                if i<len(positions) and positions[i] in atrisk and isinstance(a,list) and a and a[0]=='FEED':
                    danger_feed+=1
        if our==0: sim.step(am,ar)
        else: sim.step(ar,am)
        if (st+1)%24==0:
            post=sim.observe(our)
            newmap=set()
            for row in post['farms'][our]['tiles']:
                for t in row:
                    if isinstance(t,dict) and 'animal' in t: newmap.add('x')
            # escapes = atrisk positions that vanished at this midnight
            cur=set()
            for y,row in enumerate(post['farms'][our]['tiles']):
                for x,t in enumerate(row):
                    if isinstance(t,dict) and 'animal' in t: cur.add((x,y))
            for pos in list(atrisk):
                if pos not in cur: esc[prev[0].get(pos,'?')]+=1; atrisk.discard(pos)
        prev=(amap,fedset,invtot,None)
    return dict(episode=want,escapes=dict(esc),feed_total=feed_ops_total,feed_target=feed_ops_target,feed_other=feed_ops_other,
                slack=dict(slack_by_hour),units=dict(units_by_hour),atrisk_h22=atrisk_h22,danger_feed=danger_feed)
with multiprocessing.Pool(12) as p: rows=p.map(one,panel,chunksize=1)
esc=collections.Counter(); ft=0; ftg=0; fo=0; slack=collections.Counter(); units=collections.Counter(); ar22=0; df=0
for r in rows:
    esc.update(r['escapes']); ft+=r['feed_total']; ftg+=r['feed_target']; fo+=r['feed_other']; ar22+=r['atrisk_h22']; df+=r['danger_feed']
    for k,v in r['slack'].items(): slack[int(k)]+=v
    for k,v in r['units'].items(): units[int(k)]+=v
print('escapes',dict(esc),'total',sum(esc.values()))
print('FEED ops total',ft,'targeting an at-risk animal',ftg,'other',fo)
print('at-risk animals seen at h22-23 (animal-observations)',ar22,'FEED issued to at-risk in h22-23',df)
print('slack PASSes by hour:',{h:slack[h] for h in sorted(slack)})
print('unit-observations by hour:',{h:units[h] for h in sorted(units)})
print('slack share by hour:',{h:round(slack[h]/max(1,units[h]),3) for h in sorted(slack)})
