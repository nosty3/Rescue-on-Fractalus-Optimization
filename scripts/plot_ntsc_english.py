"""English editions of the final NTSC charts, using unchanged measurement data."""
from pathlib import Path
import json, argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--video',choices=['ntsc','pal'],default='ntsc');args=p.parse_args()
video=args.video.upper()
DATA = ROOT / f'results/{args.video}_isolated_main'
OUT = ROOT / 'docs/benchmarks/charts'
OUT.mkdir(parents=True, exist_ok=True)
data = json.loads((DATA / 'benchmark.json').read_text())
rows = data['rows']
n = data['metadata']['count_per_version']

fig, axes = plt.subplots(1, 2, figsize=(13, 6), dpi=160)
fig.patch.set_facecolor('#f8fafc')
for ax, variant, title, color in zip(axes, ('original', 'v9'), ('Original', 'v9'), ('#2563a6', '#e78125')):
    values = np.array([[r['measurement']['checkpoints'][sec]['fps'] for sec in ('15', '30', '60')]
                       for r in rows if r['variant'] == variant])
    for yy in values:
        ax.plot([15, 30, 60], yy, color=color, alpha=.18, lw=.8)
    ax.plot([15, 30, 60], values.mean(axis=0), color=color, lw=3, marker='o', label='Mean')
    ax.set_title(title)
    ax.set_xticks([15, 30, 60])
    ax.set_xlabel('Measurement time limit [s]')
    ax.set_ylabel('Mean FPS since the start of measurement')
    ax.grid(alpha=.2)
    ax.legend()
    ax.spines[['top', 'right']].set_visible(False)
fig.suptitle(f'{video} · Main study · {n} flights per version', fontsize=18, fontweight='bold')
fig.text(.08, .03, 'Thin line: one flight; windows are dependent. Flights ending early retain their result up to the end of flight.', fontsize=9)
fig.subplots_adjust(top=.86, bottom=.17, wspace=.23)
fig.savefig(OUT / f'FLIGHT_DURATION_{video}_EN.png', facecolor=fig.get_facecolor())
fig.savefig(OUT / f'FLIGHT_DURATION_{video}_EN.svg', facecolor=fig.get_facecolor())
plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=160)
colors = {'original': '#2563a6', 'v9': '#e78125'}
allfps = [r['measurement']['checkpoints']['60']['fps'] for r in rows]
bins = np.linspace(min(allfps) - .05, max(allfps) + .05, 24)
for variant, label in (('original', 'Original'), ('v9', 'v9')):
    x = np.array([r['measurement']['checkpoints']['60']['fps'] for r in rows if r['variant'] == variant])
    axes[0].hist(x, bins=bins, alpha=.55, color=colors[variant], label=label)
    axes[0].axvline(x.mean(), color=colors[variant], ls='--', lw=2)
    axes[1].step(np.sort(x), np.arange(1, len(x) + 1) / len(x), where='post', color=colors[variant], lw=2, label=label)
axes[0].set(title='Distribution of per-flight FPS', xlabel='FPS', ylabel='Number of flights')
axes[1].set(title='Empirical cumulative distribution', xlabel='FPS', ylabel='Proportion of flights with FPS at or below x')
for ax in axes:
    ax.legend()
    ax.grid(alpha=.2)
    ax.spines[['top', 'right']].set_visible(False)
fig.suptitle(f'{video} · {n} native starts per version · 60 s limit', fontsize=15)
fig.text(.08, .02, 'No extreme results excluded. Dashed lines: means. Each flight has equal weight.', fontsize=9)
fig.tight_layout(rect=(0, .05, 1, .93))
fig.savefig(OUT / f'FPS_DISTRIBUTION_{video}_EN.png')
fig.savefig(OUT / f'FPS_DISTRIBUTION_{video}_EN.svg')
plt.close(fig)
print('English PNG and SVG charts saved to', OUT)
