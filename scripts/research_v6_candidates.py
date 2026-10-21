from pathlib import Path
from collections import Counter
import json,re
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/research_v6';F=7.69100049687045;T=106704000
profile=json.loads((OUT/'summary.json').read_text());calls={r['entry']:r['calls'] for r in profile}
def delta(c,alpha=1):return F/(1-alpha*c/T)-F
geometry=json.loads((ROOT/'results/opt14/v7-geometry-tests.json').read_text());clipping=json.loads((OUT/'clipping-tests.json').read_text())
rows=[]
for name,data in [('geometry_inline',geometry),('clipping_fast',clipping)]:
 mean=sum(r['saved'] for r in data['scenes'])/len(data['scenes']);saved=mean*calls['2:8309' if name=='geometry_inline' else '2:87d3']
 rows.append({'name':name,'measured_cpu_saved_per_fixture_mean':mean,'projected_cpu_saved_per_3000_pal_frames':saved,'fps_delta_sensitivity_alpha_1_125_15':[delta(saved,a) for a in (1,1.25,1.5)],'status':'implemented_and_benchmarked'})
diag={}
for bank in range(10,14):
 text=(ROOT/f'src/opt14_geometry_bank{bank}.asm').read_text().split(' cpy #45')[0];chunks=re.split(r'point_\d+\n',text)[1:];extra=0
 for chunk in chunks:
  c=Counter(re.findall(r'STA \$(2[23][0-9a-f]{2})',chunk.split(' jsr point_tail')[0]));extra+=sum(n-1 for n in c.values())
 diag[str(bank)]={'redundant_intermediate_coordinate_stores':extra,'gross_budget_cycles':extra*12}
# Isolated CPU-only upper budget ignores setup; no implementation if even the
# representative gain is below threshold. DMA multiplier is sensitivity only.
max_saved=max(r['gross_budget_cycles'] for r in diag.values())*calls['2:8309']
div=json.loads((ROOT/'results/research_v5/renderer-trace.json').read_text())['division_inputs'];small=sum(r['d']<256 for r in div);small_saved=small/len(div)*calls['2:8224']*250
out={'baseline_fps':F,'threshold':0.05,'method':'CPU savings scaled from fixtures by fresh v6 call counts. alpha=1/1.25/1.5 are sensitivity assumptions, not confidence bounds. Geometry central estimate just exceeds threshold; measured FPS decides retention.','implemented':rows,'screened':{'fused_diagonal_steps':{'bank_counts':diag,'gross_fps_budget_alpha_1_125_15':[delta(max_saved,a) for a in (1,1.25,1.5)],'setup_cost_excluded':True},'small_divisor':{'historical_observations':len(div),'small_count':small,'optimistic_saving_per_target':250,'gross_fps_delta':delta(small_saved,1.5),'dispatch_cost_excluded':True,'status':'below threshold; not implemented'},'pixel_smc':{'analysis':'Replacing the existing zero-page pointer with two self-modified absolute operands adds 2 cycles of stores, while absolute indexed load/store saves about 2; no credible >=0.05 FPS budget for this substitution.','status':'not implemented'},'cross_frame_reuse':{'analysis':'Camera, map access and recursive fractal state can change. No demonstrated invariant with a defensible >=0.05 FPS budget; no cache or approximation introduced.','status':'unproven; not implemented'}},'deferred_original_options':[5,6,7,8]}
(OUT/'candidate-estimates.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
