"""Analyze a completed pilot/main sample without accessing the emulator."""
from pathlib import Path
import json,sys,math,argparse
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/stats_packages'))
import numpy as np
from scipy import stats

p=argparse.ArgumentParser();p.add_argument('stage',choices=['pilot','main']);p.add_argument('--video',choices=['ntsc','pal'],default='ntsc');args=p.parse_args()
OUT=ROOT/f'results/{args.video}_isolated_{args.stage}'
d=json.loads((OUT/'benchmark.json').read_text());rows=d['rows'];n=d['metadata']['count_per_version']
assert len(rows)==2*n
summary={'stage':args.stage,'count_per_version':n,'windows':{},'blocks':{},'planning':{}}
rng=np.random.default_rng(2026102302)
for sec in ('15','30','60'):
    g={}; arrays={}
    for v in ('original','v9'):
        rr=[r for r in rows if r['variant']==v]
        x=np.array([r['measurement']['checkpoints'][sec]['fps'] for r in rr]); arrays[v]=x
        sd=x.std(ddof=1); half=stats.t.ppf(.975,n-1)*sd/math.sqrt(n)
        g[v]=dict(n=n,mean=float(x.mean()),median=float(np.median(x)),sd=float(sd),cv=float(sd/x.mean()),
            pooled_fps=sum(r['measurement']['checkpoints'][sec]['intervals'] for r in rr)/sum(r['measurement']['checkpoints'][sec]['seconds'] for r in rr),
            quantiles_05_25_75_95=list(map(float,np.quantile(x,[.05,.25,.75,.95]))),
            skewness=float(stats.skew(x,bias=False)),
            mean_ci95=[float(x.mean()-half),float(x.mean()+half)],min=float(x.min()),max=float(x.max()),
            shortened_flights=sum(not r['measurement']['checkpoints'][sec].get('complete_window',True) for r in rr),
            measured_seconds_range=[min(r['measurement']['checkpoints'][sec]['seconds'] for r in rr),max(r['measurement']['checkpoints'][sec]['seconds'] for r in rr)],
            unique_maps=len({r['entry']['terrain_sha256'] for r in rr}))
    ratio=g['v9']['mean']/g['original']['mean']
    se=ratio*math.sqrt(sum(g[v]['cv']**2/n for v in ('original','v9')))
    g['gain_percent']=100*(ratio-1)
    g['pooled_gain_percent']=100*(g['v9']['pooled_fps']/g['original']['pooled_fps']-1)
    g['gain_delta_normal_ci95']=[100*(ratio-1-1.96*se),100*(ratio-1+1.96*se)]
    # Stratified resampling: preserve the five runs/version in each fixed block.
    means={}
    for v in ('original','v9'):
        total=np.zeros(50000)
        for b in sorted({r['block'] for r in rows}):
            x=np.array([r['measurement']['checkpoints'][sec]['fps'] for r in rows if r['block']==b and r['variant']==v])
            total+=rng.choice(x,(50000,len(x)),replace=True).sum(axis=1)
        means[v]=total/n
    gain=100*(means['v9']/means['original']-1)
    g['gain_stratified_bootstrap_ci95']=list(map(float,np.quantile(gain,[.025,.975])))
    summary['windows'][sec]=g
for block in sorted({r['block'] for r in rows}):
    g={v:float(np.mean([r['measurement']['checkpoints']['60']['fps'] for r in rows if r['block']==block and r['variant']==v])) for v in ('original','v9')}
    g['gain_percent']=100*(g['v9']/g['original']-1);summary['blocks'][str(block)]=g
for v in ('original','v9'):
    summary.setdefault('stability',{})[v]={}
    ordered=[r for r in rows if r['variant']==v]
    x=np.array([r['measurement']['checkpoints']['60']['fps'] for r in ordered])
    rho,pval=stats.spearmanr(np.arange(n),x)
    summary['stability'][v]['order_spearman']=dict(rho=float(rho),p=float(pval))
    groups=[np.array([r['measurement']['checkpoints']['60']['fps'] for r in rows if r['variant']==v and r['block']==b]) for b in sorted({r['block'] for r in rows})]
    summary['stability'][v]['kruskal_blocks_p']=float(stats.kruskal(*groups).pvalue)
    summary['stability'][v]['sd_ratio_60_to_15']=summary['windows']['60'][v]['sd']/summary['windows']['15'][v]['sd']
g=summary['windows']['60']; ratio=g['v9']['mean']/g['original']['mean']
n0=(1.96*ratio/.01)**2*sum(g[v]['cv']**2 for v in ('original','v9'))
summary['planning']=dict(target_gain_halfwidth_percentage_points=1,normal_approx_n_per_version=math.ceil(n0),
    proposed_fixed_n_per_version=5*math.ceil(1.2*n0/5),margin_factor=1.2,
    caveat='Conditional estimate from the 60-second pilot variance; no guarantee. No finite-population correction. Main size must be frozen before running; no optional stopping.')
if args.stage=='main':
    summary['planning']=dict(target_gain_halfwidth_percentage_points=1,frozen_n_per_version=n,
        basis='Separate pilot: 127 estimated, 20% margin, rounded to 155 before the main experiment.',
        achieved_normal_halfwidth_percentage_points=(g['gain_delta_normal_ci95'][1]-g['gain_delta_normal_ci95'][0])/2,
        caveat='Main sample size was fixed in advance. No new sample size is proposed from the main results.')
    if args.video=='pal':summary['planning']['basis']='155 per version fixed to repeat the NTSC protocol, without a new PAL pilot.'
(OUT/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
