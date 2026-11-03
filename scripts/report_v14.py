"""Regenerate current English FPS charts from retained observations."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
ref=json.loads((R/'results/v11/summary.json').read_text())
for video in ('pal','ntsc'):
 values=[]
 for mode in ('straight','steering'):
  suffix='_descent' if mode=='steering' else ''
  rows=json.loads((R/f'results/v14/full155_up74_{video}{suffix}.json').read_text());assert len(rows)==155
  values.append(sum(r['fps'] for r in rows)/155)
 values.append(sum(values)/2)
 fig,ax=plt.subplots(figsize=(9,5),layout='constrained');x=list(range(3))
 for offset,label,data,color in [(-.25,'Original',[ref[video]['table'][s]['original_fps'] for s in ('straight','steering','combined')],'#707b89'),(0,'v11',[ref[video]['table'][s]['candidate_fps'] for s in ('straight','steering','combined')],'#5b9bd5'),(.25,'v14 — Solo up74',values,'#16744a')]:
  bars=ax.bar([i+offset for i in x],data,.24,label=label,color=color);ax.bar_label(bars,fmt='%.2f',fontsize=9,padding=3)
 ax.set_xticks(x,['Straight flight','Descent pulses','50/50 mean']);ax.set_ylabel('Rendered images per second (FPS)');ax.set_title(f'Rescue on Fractalus! — {video.upper()}, 128 KB cartridge');ax.set_ylim(0,14);ax.legend(loc='upper left',ncol=3,fontsize=9);ax.spines[['top','right']].set_visible(False)
 ax.set_xlabel('155 cold-boot flights per scenario; v14 data by Solo, independently sampled for reproduction.',fontsize=8,labelpad=12)
 dest=R/f'docs/benchmarks/charts/V14_{video.upper()}.png';dest.parent.mkdir(parents=True,exist_ok=True);fig.savefig(dest,dpi=170);plt.close(fig)
