"""Full render/fill equivalence with actual bank-switching memory model."""
from cpu_test_support import *

class CartMemory(list):
 def __init__(self,rom,mem):
  super().__init__(mem);self.rom=rom;self.bank=2;self.switches=0
  super().__setitem__(slice(0x8000,0xa000),rom[0x4000:0x6000])
  super().__setitem__(slice(0xa000,0xc000),rom[0xe000:])
 def __setitem__(self,key,value):
  if isinstance(key,int) and 0xd500<=key<=0xd5ff:
   self.bank=value&7;self.switches+=1
   super().__setitem__(slice(0x8000,0xa000),self.rom[self.bank*8192:(self.bank+1)*8192])
  elif isinstance(key,int) and 0x8000<=key<0xc000:
   raise AssertionError(('ROM write',hex(key),value))
  else:super().__setitem__(key,value)

def bankcpu(rom,mem):return MPU(memory=CartMemory(rom,mem))

if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('variant',nargs='?',default='mountain');args=parser.parse_args()
 orig=(ROOT/'build/release.rom').read_bytes();rom=(ROOT/f'build/{args.variant}.rom').read_bytes()
 fixtures=json.loads((ROOT/'tests/fixtures/index.json').read_text());results=[]
 for f in fixtures:
  mem=(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes();a=bankcpu(orig,mem);b=bankcpu(rom,mem)
  ca=run(a,0x87d3,f['regs']);cb=run(b,0x87d3,f['regs'])
  a.x=b.x=int(f['regs']['X'][1:],16)+3
  ca+=run(a,0x9308);cb+=run(b,0x9308)
  diffs=[hex(i) for i in range(0x8000) if not 0x100<=i<0x200 and a.memory[i]!=b.memory[i]]
  regs=[k for k in ['a','x','y','p','sp'] if getattr(a,k)!=getattr(b,k)]
  results.append({'fixture':f['name'],'baseline_cycles':ca,'new_cycles':cb,'diff':diffs,'regs':regs,'bank':b.memory.bank,'switches':b.memory.switches})
 dest=ROOT/'results/mountain';dest.mkdir(exist_ok=True)
 (dest/f'{args.variant}-equivalence.json').write_text(json.dumps(results,indent=2))
 failures=[r for r in results if r['diff'] or r['regs'] or r['bank']!=2]
 print('failures',failures[:3]);print('cycles',sum(r['baseline_cycles'] for r in results),sum(r['new_cycles'] for r in results))
 assert not failures
