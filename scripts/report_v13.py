"""Paired 50/50 analysis of v13, with original and v12 reference data."""
from pathlib import Path
import json,hashlib,csv,statistics
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'results/v13';O.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
load=lambda p:[json.loads(s) for s in p.read_text(encoding='utf-8').splitlines()]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
fps=lambda r:r['measurement']['checkpoints']['60']['fps']
ci=lambda x:[float(t) for t in np.quantile(x,[.025,.975])]
SEED=2026102913;N=20000
def freeze_analysis():
 d=dict(seed=SEED,replicates=N,confidence=.95,estimator='Half of straight mean plus half of descent mean; preserve all natural early ends.',bootstrap='Paired start-plan resampling within the preassigned 78/77 groups for v12 and both v13 variants; preserve original-descent dependence, independently resample original straight flights.',comparisons=['Each v13 variant vs original','Each v13 variant vs v12','v13 1024 KB vs v13 512 KB'],reference_sha256={n:sha(R/n) for n in ('results/v12/flights.jsonl','results/v11/flights.jsonl','results/pal_isolated_main/benchmark.json','results/ntsc_isolated_main/benchmark.json')})
 p=O/'analysis-plan.json'
 if p.exists():assert read(p)==d
 else:p.write_text(json.dumps(d,indent=2),encoding='utf-8')
 return d
def main():
 freeze_analysis();new={}
 for kb in (512,1024):
  folder=O/f'{kb}KB';integrity=read(folder/'integrity.json');assert integrity['complete'] and integrity['flights']==310
  new[str(kb)]=load(folder/'flights.jsonl');assert len(new[str(kb)])==310
 old=load(R/'results/v12/flights.jsonl');history=load(R/'results/v11/flights.jsonl');rng=np.random.default_rng(SEED);result={};flat=[]
 for video in ('pal','ntsc'):
  groups={name:{r['trial']:r for r in rows if r['video']==video} for name,rows in {'v12':old,**new}.items()}
  base=groups['v12'];assert all(set(v)==set(base) and len(v)==155 for v in groups.values())
  for name,rows in groups.items():
   for t,r in rows.items():assert (r['mode'],r['menu_frames'],r['terrain_sha256'])==(base[t]['mode'],base[t]['menu_frames'],base[t]['terrain_sha256'])
  ids={m:sorted(t for t,r in base.items() if r['mode']==m) for m in ('straight','steering')};ss=ids['straight'];dd=ids['steering'];assert len(ss)==78 and len(dd)==77
  si=rng.integers(0,78,(N,78));di=rng.integers(0,77,(N,77));means={};bs={};details={}
  for name,rows in groups.items():
   a=np.array([fps(rows[t]) for t in ss]);b=np.array([fps(rows[t]) for t in dd]);means[name]=float(.5*(a.mean()+b.mean()));bs[name]=.5*(a[si].mean(1)+b[di].mean(1))
   details[name]=dict(fps=means[name],ci95=ci(bs[name]),n=155,straight_n=78,descent_n=77,early_ends=sum(r['measurement']['termination'] is not None for r in rows.values()),straight_mean_fps=float(a.mean()),descent_mean_fps=float(b.mean()),mean_trial_wall_seconds=statistics.mean(r['wall_seconds'] for r in rows.values()))
   for t,r in rows.items():flat.append(dict(video=video,version=name,trial=t,scenario=r['mode'],menu_frames=r['menu_frames'],fps=fps(r),seconds=r['measurement']['checkpoints']['60']['seconds'],early_end=r['measurement']['termination'] is not None))
  os=np.array([fps(r) for r in read(R/f'results/{video}_isolated_main/benchmark.json')['rows'] if r['variant']=='original']);assert len(os)==155
  od={r['trial']:r for r in history if (r['video'],r['version'],r['mode'])==(video,'original','steering')};assert set(od)==set(base)
  for t,r in od.items():assert r['menu_frames']==base[t]['menu_frames']
  ods=np.array([fps(od[t]) for t in ss]);odd=np.array([fps(od[t]) for t in dd]);means['original']=float(.5*(os.mean()+np.r_[ods,odd].mean()));bs['original']=.5*(os[rng.integers(0,155,(N,155))].mean(1)+(ods[si].sum(1)+odd[di].sum(1))/155)
  details['original']=dict(fps=means['original'],ci95=ci(bs['original']),n=310,straight_n=155,descent_n=155)
  previous=read(R/'results/v12/summary.json')['video'][video]['combined'];assert abs(previous['v12_fps']-means['v12'])<1e-12 and abs(previous['original_fps']-means['original'])<1e-12
  comps={}
  for candidate,reference in [('512','original'),('1024','original'),('512','v12'),('1024','v12'),('1024','512')]:
   comps[candidate+'_vs_'+reference]=dict(delta_fps=means[candidate]-means[reference],gain_percent=100*(means[candidate]/means[reference]-1),gain_ci95_percent=ci(100*(bs[candidate]/bs[reference]-1)),delta_ci95=ci(bs[candidate]-bs[reference]))
  result[video]=dict(versions=details,comparisons=comps,all_155_start_maps_match=True)
 out=dict(version='v13',variants=['512KB','1024KB'],video=result,analysis_plan_sha256=sha(O/'analysis-plan.json'),replicates=N,runs={str(k):read(O/f'{k}KB/run.json') for k in (512,1024)})
 (O/'summary.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 with (O/'flights.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
