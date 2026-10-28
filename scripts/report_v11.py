"""Reproduce v11 README charts and tables from retained per-flight data."""
from pathlib import Path
import os,json,statistics
R=Path(__file__).resolve().parents[1];os.environ['MPLCONFIGDIR']=str(R/'build/mplconfig')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
O=R/'docs/benchmarks/charts';O.mkdir(exist_ok=True)
rows=[json.loads(s) for s in (R/'results/v11/flights.jsonl').read_text().splitlines()]
summary={}
for video in ('pal','ntsc'):
 historical=json.loads((R/f'results/{video}_isolated_main/benchmark.json').read_text())['rows']
 groups={('original','straight'):[r['measurement']['checkpoints']['60']['fps'] for r in historical if r['variant']=='original']}
 for version,mode in [('original','steering'),('candidate','straight'),('candidate','steering')]:groups[version,mode]=[r['measurement']['checkpoints']['60']['fps'] for r in rows if (r['video'],r['version'],r['mode'])==(video,version,mode)]
 assert all(len(v)==155 for v in groups.values())
 means={k:statistics.mean(v) for k,v in groups.items()};table={}
 for mode in ('straight','steering','combined'):
  a,b=[statistics.mean(means[v,m] for m in ('straight','steering')) if mode=='combined' else means[v,mode] for v in ('original','candidate')]
  table[mode]=dict(original_fps=a,candidate_fps=b,delta_fps=b-a,gain_percent=100*(b/a-1))
 expected=json.loads((R/'results/v11/summary.json').read_text())[video]['table']
 for mode in table:
  for k,v in table[mode].items():assert abs(v-expected[mode][k])<1e-10
 summary[video]=table
 fig,ax=plt.subplots(figsize=(10,5),dpi=160);x=np.arange(3);w=.34
 for version,label,color in [('original','Original','#587dad'),('candidate','v11','#df8b35')]:
  vals=[table[m][version+'_fps'] for m in table];bars=ax.bar(x+(-w/2 if version=='original' else w/2),vals,w,label=label,color=color);ax.bar_label(bars,fmt='%.4f',padding=4,fontsize=10)
 ax.set(xticks=x,xticklabels=['Straight flight','Descent pulses','50/50 combined'],ylabel='Mean rendered images per second (FPS)',ylim=(0,10.6),title=f'Rescue on Fractalus! · {video.upper()} · Original vs v11');ax.legend(loc='upper left');ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
 for i,q in enumerate(table.values()):ax.text(i,9.85,f'+{q["gain_percent"]:.2f}%',ha='center',weight='bold')
 fig.text(.5,.015,'155 cold boots per version and scenario · up to 60 s · cartridge results · early ends retained',ha='center',fontsize=9);fig.tight_layout(rect=[0,.045,1,1])
 for ext in ('png','svg'):fig.savefig(O/f'V11_COMPARISON_{video.upper()}.{ext}')
 plt.close(fig)
 fig,axs=plt.subplots(1,2,figsize=(11,4.5),dpi=160,sharex=True,sharey=True);vals=sum(list(groups.values()),[]);bins=np.linspace(min(vals)-.05,max(vals)+.05,25)
 for ax,mode,label in zip(axs,('straight','steering'),('Straight flight','Descent: 1 s up / 3 s neutral')):
  for version,name,color in [('original','Original','#587dad'),('candidate','v11','#df8b35')]:ax.hist(groups[version,mode],bins=bins,color=color,alpha=.55,label=name);ax.axvline(means[version,mode],color=color,ls='--')
  ax.set(title=label,xlabel='Per-flight FPS',ylabel='Flights');ax.legend();ax.grid(alpha=.2)
 fig.suptitle(f'{video.upper()} · FPS distributions · 155 flights per arm');fig.tight_layout()
 for ext in ('png','svg'):fig.savefig(O/f'V11_DISTRIBUTION_{video.upper()}.{ext}')
 plt.close(fig)
print(json.dumps(summary,indent=2))
