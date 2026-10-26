"""Verify completed v10 series, compare historical controls and draw English charts."""
from pathlib import Path
import json,sys,hashlib,math,argparse,os
parser=argparse.ArgumentParser();parser.add_argument('--published-data',action='store_true');args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/stats_packages'))
os.environ['MPLCONFIGDIR']=str(ROOT/'tools/matplotlib-cache')
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=ROOT/'results/v10';rng=np.random.default_rng(2026102605);result={}
for video,freq in [('pal',1773447.5),('ntsc',1789772.5)]:
 folder=OUT/video;plan=json.loads((folder/'plan.json').read_text());data=json.loads((folder/'benchmark.json').read_text());new=data['rows']
 assert len(new)==155 and data['metadata']==plan['metadata']
 assert len({r['menu_frames'] for r in new})==155 and len({r['trial'] for r in new})==155
 for t,r in zip(plan['schedule'],new):
  assert all(t[k]==r[k] for k in ('variant','trial','block','menu_frames'))
  assert r['entry']['config']['video']==video
  events=None
  if not args.published_data:
   events=json.loads((folder/f"{r['name']}-events.json").read_text())
   assert hashlib.sha256(json.dumps(events).encode()).hexdigest()==r['measurement']['events_sha256']
   assert events[0]==0 and all(b>a for a,b in zip(events,events[1:]))
  for sec,c in r['measurement']['checkpoints'].items():
   if events is not None:assert c['ticks']==events[c['intervals']]
   assert abs(c['fps']-c['intervals']*freq/c['ticks'])<1e-12
   assert abs(c['seconds']-c['ticks']/freq)<1e-12
  if not args.published_data:
   for suffix in ('entry','after-warmup','end'):assert (folder/f"{r['name']}-{suffix}.bin").stat().st_size==32768
   assert hashlib.sha256((folder/f"{r['name']}-entry.bin").read_bytes()).hexdigest()==r['entry']['ram_sha256']
 old=json.loads((ROOT/f'results/{video}_isolated_main/benchmark.json').read_text())['rows']
 rows=old+new;summary={'windows':{}}
 for sec in ('15','30','60'):
  g={};boot={}
  for v in ('original','v9','v10'):
   rr=[r for r in rows if r['variant']==v];x=np.array([r['measurement']['checkpoints'][sec]['fps'] for r in rr]);assert len(x)==155
   half=stats.t.ppf(.975,154)*x.std(ddof=1)/math.sqrt(155)
   g[v]=dict(mean=float(x.mean()),sd=float(x.std(ddof=1)),median=float(np.median(x)),mean_ci95=[float(x.mean()-half),float(x.mean()+half)],shortened=sum(not r['measurement']['checkpoints'][sec].get('complete_window',True) for r in rr),pooled_fps=sum(r['measurement']['checkpoints'][sec]['intervals'] for r in rr)/sum(r['measurement']['checkpoints'][sec]['seconds'] for r in rr))
   total=np.zeros(50000)
   for block in range(1,32):
    xx=np.array([r['measurement']['checkpoints'][sec]['fps'] for r in rr if r['block']==block]);assert len(xx)==5
    total+=rng.choice(xx,(50000,5),replace=True).sum(axis=1)
   boot[v]=total/155
  for ref in ('original','v9'):
   g['v10_vs_'+ref]=dict(delta_fps=g['v10']['mean']-g[ref]['mean'],gain_percent=100*(g['v10']['mean']/g[ref]['mean']-1),gain_bootstrap_ci95=list(map(float,np.quantile(100*(boot['v10']/boot[ref]-1),[.025,.975]))))
  # v9/v10 reuse the same randomized START schedule: preserve this pairing.
  pairs=[(next(r for r in old if r['variant']=='v9' and r['trial']==n['trial']),n) for n in new]
  assert all(a['menu_frames']==b['menu_frames'] for a,b in pairs)
  delta=np.array([b['measurement']['checkpoints'][sec]['fps']-a['measurement']['checkpoints'][sec]['fps'] for a,b in pairs])
  half=stats.t.ppf(.975,154)*delta.std(ddof=1)/math.sqrt(155)
  g['v10_vs_v9']['paired_delta_ci95']=[float(delta.mean()-half),float(delta.mean()+half)]
  g['v10_vs_v9']['identical_entry_ram_pairs']=sum(a['entry']['ram_sha256']==b['entry']['ram_sha256'] for a,b in pairs)
  summary['windows'][sec]=g
 summary['integrity']='published-aggregate-pass' if args.published_data else 'pass';summary['n_per_version']=155
 (folder/'summary.json').write_text(json.dumps(summary,indent=2));result[video]=summary
 colors={'original':'#2563a6','v10':'#17865b'};labels={'original':'Original','v9':'v9','v10':'v10'}
 fig,axes=plt.subplots(1,2,figsize=(13,5),dpi=160)
 bins=np.linspace(min(r['measurement']['checkpoints']['60']['fps'] for r in rows)-.05,max(r['measurement']['checkpoints']['60']['fps'] for r in rows)+.05,25)
 for v in colors:
  x=np.array([r['measurement']['checkpoints']['60']['fps'] for r in rows if r['variant']==v]);label=f'{labels[v]} · mean {x.mean():.4f} FPS'
  axes[0].hist(x,bins=bins,alpha=.45,color=colors[v],label=label)
  axes[1].step(np.sort(x),np.arange(1,156)/155,where='post',color=colors[v],label=label)
 for ax in axes:ax.set_xlabel('FPS');ax.grid(alpha=.2);ax.legend(fontsize=8)
 axes[0].set_ylabel('Flights');axes[1].set_ylabel('Cumulative fraction of flights')
 fig.suptitle(f'{video.upper()} · 155 cold-start flights per version · 60-second limit')
 fig.text(.5,.015,'Original: historical reference series. v10: new series; natural early endings retained.',ha='center',fontsize=8)
 fig.tight_layout(rect=(0,.04,1,.94))
 for ext in ('png','svg'):fig.savefig(folder/f'FPS_DISTRIBUTION_{video.upper()}_EN.{ext}')
 plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(13,5),dpi=160,sharey=True)
 for ax,v in zip(axes,colors):
  xx=np.array([[r['measurement']['checkpoints'][s]['fps'] for s in ('15','30','60')] for r in rows if r['variant']==v])
  for line in xx:ax.plot([15,30,60],line,color=colors[v],alpha=.13,lw=.7)
  ax.plot([15,30,60],xx.mean(axis=0),color=colors[v],lw=3,marker='o',label='Mean');ax.set_title(labels[v]);ax.set_xticks([15,30,60]);ax.set_xlabel('Measurement time limit [s]');ax.grid(alpha=.2);ax.legend()
 axes[0].set_ylabel('Mean FPS since measurement start');fig.suptitle(f'{video.upper()} · Measurement duration · 155 flights per version')
 fig.text(.5,.015,'Nested windows of the same flight; early-ending flights retain their final result. Original uses historical data.',ha='center',fontsize=8);fig.tight_layout(rect=(0,.04,1,.94))
 for ext in ('png','svg'):fig.savefig(folder/f'FLIGHT_DURATION_{video.upper()}_EN.{ext}')
 plt.close(fig)
(OUT/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({v:s['windows']['60'] for v,s in result.items()},indent=2))
