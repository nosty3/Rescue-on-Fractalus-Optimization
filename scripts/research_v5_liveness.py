"""Read-after-return observation of divider scratch; no program mutation."""
from test_clear128 import *
from collections import Counter
OUT=ROOT/'results/research_v5';rom=(ROOT/'dist/Rescue on Fractalus! - PAL optimized v5 128KB.rom').read_bytes()
class Observe(Memory):
 def __init__(self,rom,mem):super().__init__(rom,mem);self.watch=set();self.active=False;self.pc=0;self.hits=Counter();self.killed=Counter()
 def __getitem__(self,key):
  if self.active and isinstance(key,int) and key in self.watch:self.hits[f'{self.pc:04x}:{key:02x}']+=1;self.watch.remove(key)
  return super().__getitem__(key)
 def __setitem__(self,key,value):
  if getattr(self,'active',False) and isinstance(key,int) and key in self.watch:self.killed[f'{self.pc:04x}:{key:02x}']+=1;self.watch.remove(key)
  super().__setitem__(key,value)
hits=Counter();killed=Counter();remaining=Counter();calls=0
for f in json.loads((ROOT/'tests/fixtures/index.json').read_text()):
 m=Observe(rom,(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes());c=MPU(memory=m)
 for dst,src in [('a','A'),('x','X'),('y','Y'),('p','P')]:setattr(c,dst,int(f['regs'][src][1:],16))
 c.pc=0x87d3;c.sp=0xfd;m[0x1fe]=0xfe;m[0x1ff]=0x3f
 while c.pc!=0x3fff:
  end_div=c.pc==0x8303 and m.bank==2;m.pc=c.pc;m.active=True;c.step();m.active=False
  if end_div:m.watch={0xae,0xaf,0xb0,0xb1};calls+=1
 hits.update(m.hits);killed.update(m.killed);remaining.update(hex(x) for x in m.watch)
out={'calls':calls,'read_before_overwrite':dict(hits),'first_overwrites':dict(killed),'still_unresolved_at_renderer_return':dict(remaining),'scope':'58 renderer invocations only; no interrupts and no subsequent main-loop/VBI liveness proof.'}
(OUT/'divider-liveness.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
