"""English figure for the original/v11/v13 50/50 comparison."""
from pathlib import Path
import os,json
R=Path(__file__).resolve().parents[1];os.environ['MPLCONFIGDIR']=str(R/'tools/matplotlib-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
s=json.loads((R/'results/v13/summary.json').read_text(encoding='utf-8'));v11=json.loads((R/'results/v11/summary.json').read_text(encoding='utf-8'));O=R/'docs/benchmarks/charts';O.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(12.5,5.6),dpi=170,sharey=True);keys=['original','v11','512','1024'];colors=['#5c718b','#cb8a42','#25867b','#7651a0']
for video,ax in zip(('pal','ntsc'),axes):
 q=s['video'][video];v=dict(q['versions']);base=v11[video]['table']['combined']['candidate_fps'];v['v11']={'fps':base,'ci95':[base,base]};ys=[v[k]['fps'] for k in keys];errs=np.array([([v[k]['fps']-v[k]['ci95'][0],v[k]['ci95'][1]-v[k]['fps']] if k!='v11' else [float('nan'),float('nan')]) for k in keys]).T
 bars=ax.bar(np.arange(4),ys,width=.7,color=colors,yerr=errs,capsize=4)
 for i,(bar,k) in enumerate(zip(bars,keys)):
  ax.text(i,v[k]['ci95'][1]+.15,f'{v[k]["fps"]:.4f}',ha='center',va='bottom',weight='bold',fontsize=10)
  if i:ax.text(i,v[k]['fps']/2,f'+{100*(v[k]["fps"]/v["original"]["fps"]-1):.2f}%',ha='center',weight='bold',color='white',fontsize=10)
 ax.set(title=video.upper(),xticks=np.arange(4),xticklabels=['Original','v11','v13\n512 KB','v13\n1 MB'],ylim=(0,11.2));ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
 if video=='pal':ax.set_ylabel('Mean rendered images per second (FPS)')
fig.suptitle('Rescue on Fractalus! · v13 · exact compiled terrain trees',fontsize=15,weight='bold')
fig.text(.5,.071,'50/50 straight and descent · each v13: 155 cold boots per system · original and v11: 155 + 155',ha='center',fontsize=9)
fig.text(.5,.031,'Nominal 60 s windows · natural early ends retained · 95% bootstrap error bars: original and v13; v11: mean only',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.12,1,.93])
for ext in ('png','svg'):fig.savefig(O/f'V13_COMPARISON.{ext}')
p=O/'V13_COMPARISON.svg';p.write_text('\n'.join(x.rstrip() for x in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
plt.close(fig);print('English v13 chart saved')
