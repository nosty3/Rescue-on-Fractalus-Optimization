"""Stratified analysis of the frozen v12 study and retained reference data."""
from pathlib import Path
import json,hashlib,statistics,csv
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'results/v12';B=R/'optimized version'
REPLICATES=20000;SEED=2026102912
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
fps=lambda r:r['measurement']['checkpoints']['60']['fps']
ci=lambda v:[float(x) for x in np.quantile(v,[.025,.975])]

def analysis_plan():
 plan=read(O/'analysis-plan.json');assert plan['bootstrap_replicates']==REPLICATES and plan['seed']==SEED;return plan

def basic(rows):
 vals=np.array([fps(r) for r in rows],dtype=float)
 return dict(n=len(rows),mean_fps=float(vals.mean()),sd_fps=float(vals.std(ddof=1)),median_fps=float(np.median(vals)),min_fps=float(vals.min()),max_fps=float(vals.max()),early_ends=sum(r['measurement'].get('termination') is not None for r in rows),duration_seconds_min=min(r['measurement']['checkpoints']['60']['seconds'] for r in rows),duration_seconds_max=max(r['measurement']['checkpoints']['60']['seconds'] for r in rows))

def main():
 plan=analysis_plan();integrity=read(O/'integrity.json');assert integrity['complete'] and integrity['flights']==310
 rows=[json.loads(s) for s in (O/'flights.jsonl').read_text().splitlines()]
 hist=[json.loads(s) for s in (R/'results/v11/flights.jsonl').read_text().splitlines()]
 expected=read(R/'results/v11/summary.json');rng=np.random.default_rng(SEED);out={};csvrows=[]
 for video in ('pal','ntsc'):
  new={r['trial']:r for r in rows if r['video']==video};assert len(new)==155
  original_s=[r for r in read(R/f'results/{video}_isolated_main/benchmark.json')['rows'] if r['variant']=='original']
  old={(v,m):{r['trial']:r for r in hist if (r['video'],r['version'],r['mode'])==(video,v,m)} for v,m in [('candidate','straight'),('candidate','steering'),('original','steering')]}
  assert len(original_s)==155 and all(len(d)==155 for d in old.values())
  assert all(set(d)==set(new) for d in old.values())
  for trial,n in new.items():
   for d in old.values():assert n['menu_frames']==d[trial]['menu_frames']
  ss=sorted(t for t,r in new.items() if r['mode']=='straight');dd=sorted(set(new)-set(ss));assert (len(ss),len(dd))==(78,77)
  ns=np.array([fps(new[t]) for t in ss]);nd=np.array([fps(new[t]) for t in dd]);orig_s=np.array([fps(r) for r in original_s])
  gather=lambda key,ids:np.array([fps(old[key][t]) for t in ids])
  os=gather(('original','steering'),ss);od=gather(('original','steering'),dd)
  vss=gather(('candidate','straight'),ss);vsd=gather(('candidate','straight'),dd)
  vds=gather(('candidate','steering'),ss);vdd=gather(('candidate','steering'),dd)
  newmean=.5*(ns.mean()+nd.mean());oldmean=.5*(np.r_[vss,vsd].mean()+np.r_[vds,vdd].mean());origmean=.5*(orig_s.mean()+np.r_[os,od].mean());matchedmean=.5*(vss.mean()+vdd.mean())
  assert abs(oldmean-expected[video]['table']['combined']['candidate_fps'])<1e-12 and abs(origmean-expected[video]['table']['combined']['original_fps'])<1e-12
  si=rng.integers(0,78,size=(REPLICATES,78));di=rng.integers(0,77,size=(REPLICATES,77))
  nb=.5*(ns[si].mean(1)+nd[di].mean(1))
  vb=.5*((vss[si].sum(1)+vsd[di].sum(1))/155+(vds[si].sum(1)+vdd[di].sum(1))/155)
  mb=.5*(vss[si].mean(1)+vdd[di].mean(1))
  ob=.5*(orig_s[rng.integers(0,155,size=(REPLICATES,155))].mean(1)+(os[si].sum(1)+od[di].sum(1))/155)
  comp=lambda base,bb:dict(baseline_fps=float(base),v12_fps=float(newmean),delta_fps=float(newmean-base),gain_percent=float(100*(newmean/base-1)),delta_ci95=ci(nb-bb),gain_ci95_percent=ci(100*(nb/bb-1)))
  arms={'v12_straight':basic([new[t] for t in ss]),'v12_steering':basic([new[t] for t in dd]),'v11_matched_straight':basic([old['candidate','straight'][t] for t in ss]),'v11_matched_steering':basic([old['candidate','steering'][t] for t in dd])}
  out[video]=dict(n=155,arms=arms,combined=dict(original_fps=float(origmean),v11_full_fps=float(oldmean),v11_matched_fps=float(matchedmean),v12_fps=float(newmean),v12_fps_ci95=ci(nb),original_fps_ci95=ci(ob),v11_full_fps_ci95=ci(vb)),versus_original=comp(origmean,ob),versus_v11_full=comp(oldmean,vb),versus_v11_matched=comp(matchedmean,mb),transport=dict(mean_flight_wall_seconds=statistics.mean(r['flight_wall_seconds'] for r in new.values()),mean_total_trial_wall_seconds=statistics.mean(r['wall_seconds'] for r in new.values()),total_measured_emulated_seconds=sum(r['measurement']['checkpoints']['60']['seconds'] for r in new.values())),bootstrap_scope=plan['method'])
  for t in sorted(new):
   r=new[t];c=r['measurement']['checkpoints']['60'];baseline=old['candidate',r['mode']][t]
   csvrows.append(dict(video=video,trial=t,execution_order=r['execution_order'],scenario=r['mode'],menu_frames=r['menu_frames'],intervals=c['intervals'],emulated_seconds=c['seconds'],v12_fps=c['fps'],v11_matched_fps=fps(baseline),natural_early_end=r['measurement']['termination'] is not None,flight_wall_seconds=r['flight_wall_seconds'],total_trial_wall_seconds=r['wall_seconds']))
 result=dict(version='v12',publication='branch v12',rom_sha256=hashlib.sha256((B/'Rescue on Fractalus! - optimized 128KB.rom').read_bytes()).hexdigest(),plan_sha256=integrity['plan_sha256'],analysis_plan_sha256=sha(O/'analysis-plan.json'),replicates=REPLICATES,run=read(O/'run.json'),video=out)
 (O/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 with (O/'flights.csv').open('w',newline='',encoding='utf-8') as f:
  writer=csv.DictWriter(f,fieldnames=list(csvrows[0]));writer.writeheader();writer.writerows(csvrows)
 print(json.dumps(result,indent=2))

if __name__=='__main__':main()
