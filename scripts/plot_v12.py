"""English plots for the local v12 50/50 benchmark."""
from pathlib import Path
import os,json
R=Path(__file__).resolve().parents[1];O=R/'results/v12';D=R/'docs/benchmarks/charts';D.mkdir(exist_ok=True)
os.environ['MPLCONFIGDIR']=str(R/'tools/matplotlib-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
summary=json.loads((O/'summary.json').read_text());colors=['#5c718b','#cb8a42','#25867b']
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'font.size':11})
fig,axes=plt.subplots(1,2,figsize=(12,5.3),dpi=170,sharey=True)
for ax,video in zip(axes,('pal','ntsc')):
 q=summary['video'][video];c=q['combined'];values=[c['original_fps'],c['v11_full_fps'],c['v12_fps']]
 intervals=[c['original_fps_ci95'],c['v11_full_fps_ci95'],c['v12_fps_ci95']]
 errors=np.array([[v-a,b-v] for v,(a,b) in zip(values,intervals)]).T
 bars=ax.bar(range(3),values,color=colors,width=.64,yerr=errors,capsize=5,error_kw={'linewidth':1.2,'capthick':1.2})
 for i,(bar,value,bounds) in enumerate(zip(bars,values,intervals)):
  ax.text(bar.get_x()+bar.get_width()/2,bounds[1]+.13,f'{value:.4f}',ha='center',va='bottom',weight='bold',fontsize=12)
  if i:ax.text(i,value/2,f'+{100*(value/values[0]-1):.2f}%',ha='center',color='white',weight='bold',fontsize=12)
 ax.set(xticks=range(3),xticklabels=['Original','v11','v12'],ylim=(0,10.5),title=video.upper(),ylabel='Mean rendered images per second (FPS)' if video=='pal' else '')
 ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
 ax.text(.5,.96,f'v12 vs original: +{q["versus_original"]["gain_percent"]:.2f}%',ha='center',va='top',transform=ax.transAxes,color=colors[2],weight='bold')
fig.suptitle('Rescue on Fractalus! Â· v12 benchmark Â· 50/50 straight and descent',fontsize=15,weight='bold')
fig.text(.5,.055,'Original / v11: 155 + 155 flights per system Â· v12: 78 straight + 77 descent',ha='center',fontsize=9)
fig.text(.5,.022,'Cold boot per trial Â· up to 60 emulated seconds Â· natural early ends retained Â· 95% bootstrap intervals',ha='center',fontsize=9)
fig.tight_layout(rect=[0,.10,1,.93])
for ext in ('png','svg'):fig.savefig(D/f'V12_COMPARISON.{ext}')
plt.close(fig)
print('English overview saved:',D/'V12_COMPARISON.png')
