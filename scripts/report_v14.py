"""Regenerate English and Polish current-vs-original FPS charts."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
# Historical summary supplies the original observations used as baseline.
ref=json.loads((R/'results/v11/summary.json').read_text())
for video in ('pal','ntsc'):
 values=[]
 for mode in ('straight','steering'):
  suffix='_descent' if mode=='steering' else ''
  rows=json.loads((R/f'results/v14/full155_v14_{video}{suffix}.json').read_text());assert len(rows)==155
  values.append(sum(r['fps'] for r in rows)/155)
 values.append(sum(values)/2)
 for pl in (False,True):
  fig,ax=plt.subplots(figsize=(9,5),layout='constrained');x=list(range(3))
  for offset,label,data,color in [(-.18,'Oryginał' if pl else 'Original',[ref[video]['table'][s]['original_fps'] for s in ('straight','steering','combined')],'#707b89'),(.18,'v14',values,'#16744a')]:
   bars=ax.bar([i+offset for i in x],data,.34,label=label,color=color);ax.bar_label(bars,fmt='%.2f',fontsize=9,padding=3)
  ax.set_xticks(x,['Lot prosto','Nurkowanie','Średnia 50/50'] if pl else ['Straight flight','Descent pulses','50/50 mean'])
  ax.set_ylabel('Renderowane obrazy na sekundę (FPS)' if pl else 'Rendered images per second (FPS)')
  ax.set_title(f'Rescue on Fractalus! — {video.upper()}, 128 KB')
  ax.set_ylim(0,14);ax.legend(loc='upper left',ncol=2,fontsize=9);ax.spines[['top','right']].set_visible(False)
  ax.set_xlabel('v14: 155 lotów na scenariusz i system; dane Solo. Oryginał: wcześniejsze pomiary.' if pl else 'v14: 155 flights per scenario and system; Solo’s data. Original: earlier measurements.',fontsize=8,labelpad=12)
  suffix='_PL' if pl else ''
  dest=R/f'docs/benchmarks/charts/V14_{video.upper()}{suffix}.png';dest.parent.mkdir(parents=True,exist_ok=True);fig.savefig(dest,dpi=170);plt.close(fig)
