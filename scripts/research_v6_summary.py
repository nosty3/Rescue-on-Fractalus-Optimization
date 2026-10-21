from session import *
from collections import defaultdict
OUT=ROOT/'results/research_v6';agg=defaultdict(lambda:[0,0,0])
for scenario in ('straight','right','left','fast_right'):
 for r in json.loads((OUT/f'{scenario}-callgraph.json').read_text()):
  g=int(r['gaddr'][1:],16);key=f'{(g>>16)&255}:{0x8000+(g&8191):04x}' if g>>28==8 else f'ram:{g&65535:04x}'
  for i,k in enumerate(('calls','excl_cycles','incl_cycles')):agg[key][i]+=r[k]/4
rows=[{'entry':k,'calls':v[0],'own':v[1],'inclusive':v[2],'percent':v[1]/1067040} for k,v in agg.items() if v[1]];rows.sort(key=lambda r:-r['own'])
(OUT/'summary.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows[:24],indent=2))
