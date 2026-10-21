"""Explicit preliminary budgets, not measured modified-game FPS."""
from session import *
OUT=ROOT/'results/research_v5';p=json.loads((OUT/'summary.json').read_text());t=json.loads((OUT/'renderer-trace.json').read_text());a=json.loads((OUT/'arithmetic-models.json').read_text())
F=7.367256208389218;T=106704000;render=p['summary']['2:87d3']['mean_calls'];fill=p['summary']['2:9308']['mean_calls'];geom=p['summary']['2:8309']['mean_calls'];n=58
def model(name,lo,hi,assumption):
 return {'name':name,'saved_cpu_cycles_3000_frames':[lo,hi],'fps_delta_sensitivity':[F/(1-lo/T)-F,F/(1-1.5*hi/T)-F],'assumption':assumption}
div=p['summary']['2:8224']['mean_calls']*a['division']['cycles_saved_mean']
w45=t['widths']['4']+t['widths']['5'];tests=sum(v for k,v in t['widths'].items() if int(k)>3)
rows=[model('division_no_normalization',div,div,'Observed quotient/cycle model; assumes normalized scratch and V dead, no new guard/glue.'),
 model('width4_width5',(w45*35-tests*5)*render/n,(w45*55-tests*5)*render/n,'Budget: 35..55 cycles gross per target; 5-cycle dispatch per width>3. Requires code in same bank/RAM, no per-leaf switching.'),
 model('geometry_commands',geom*(45*20-40),geom*(45*45-40),'Budget: save 20..45 cycles for each of 45 points, subtract 40 per invocation for banking.'),
 model('interpolation_lookup',2250*200,2250*350,'Budget: net 200..350 cycles saved per call including lookup setup/banking; arithmetic verified, assembly cost unverified.'),
 model('fill_late_rows',501*15*fill/n,501*35*fill/n,'Budget: 15..35 cycles net for 501/2436 columns starting after row32; no extra per-column banking.'),
 model('layout_pages',sum(t['page_penalties'].values())*0.25*render/n,sum(t['page_penalties'].values())*0.65*render/n,'Assume 25..65% observed page penalties removable, no other path regression; all penalties would be an upper bound.'),
 model('multiply_lookup',4500*20,4500*45,'Budget: 20..45 cycles net; reuse interpolation table, exact residue/flags still unresolved.'),
 model('sound_dispatch',42000*2,42000*5,'Budget: remove 2..5 cycles from 14-channel scan per VBI; preserve event order and hardware writes.')]
out={'baseline_fps':F,'machine_ticks':T,'method':'Fnew=F/(1-alpha*delta_CPU/T); alpha=1 low, 1.5 high are sensitivity assumptions, not a confidence interval. No patch or new FPS measured. Budgets may fail; do not add overlapping rows.','rows':rows}
(OUT/'estimates.json').write_text(json.dumps(out,indent=2))
for r in rows:print(r['name'],r['fps_delta_sensitivity'])
