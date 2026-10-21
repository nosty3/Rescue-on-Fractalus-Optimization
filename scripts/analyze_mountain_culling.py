"""Bound-only experiment; never changes the rendered state or ROM."""
from cpu_test_support import *
from functools import lru_cache

@lru_cache(None)
def extra(w):
 if w<=2:return 0
 # Midpoint positive displacement <= floor(w/4)+1, including carry.
 # A conservative upper envelope, independent of phase and rounding.
 return w//4+1+max(extra(w//2),extra((w+1)//2))

rom=(ROOT/'build/release.rom').read_bytes();fixtures=json.loads((ROOT/'tests/fixtures/index.json').read_text());rows=[]
for f in fixtures:
 c=cpu(rom,(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes());c.pc=0x87d3;c.sp=0xfd;c.memory[0x1fe]=0xfe;c.memory[0x1ff]=0x3f
 for dst,src in [('a','A'),('x','X'),('y','Y'),('p','P')]:setattr(c,dst,int(f['regs'][src][1:],16))
 pending=None
 while c.pc!=0x3fff:
  if c.pc==0x982a:
   l,r=c.memory[0x82],c.memory[0x95]
   bound=min(255,max(c.memory[0x84],c.memory[0xea])+extra(max(0,r-l)))
   xs=list(range(max(44,l),min(212,r))) if r>l else []
   checked=0;reject=bool(xs)
   for x in xs:
    checked+=1
    if c.memory[0x260e+x]<bound:reject=False;break
   pending={'fixture':f['name'],'left':l,'right':r,'bound':bound,'checks':checked,'reject':reject,'start':c.processorCycles,'sp':c.sp}
  if pending and c.memory[c.pc]==0x60 and c.sp==pending['sp']:
   pending['cycles']=c.processorCycles-pending.pop('start')+6;pending.pop('sp');rows.append(pending);pending=None
  c.step()
summary={'calls':len(rows),'rejected_calls':sum(r['reject'] for r in rows),'saved_cycles_gross':sum(r['cycles'] for r in rows if r['reject']),
 'checked_columns':sum(r['checks'] for r in rows),'optimistic_test_cost':sum(20+10*r['checks'] for r in rows),
 'note':'Conservative height bound; cost model 20 cycles setup +10 per inspected column is optimistic. Skipping also needs a separate liveness proof for scratch state.'}
summary['net_optimistic']=summary['saved_cycles_gross']-summary['optimistic_test_cost']
(ROOT/'analysis/mountain/culling.json').write_text(json.dumps({'summary':summary,'calls':rows},indent=2));print(summary)
