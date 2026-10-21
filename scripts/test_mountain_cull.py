"""Culling preserves live state; completed subdivision stack slots are dead."""
from test_mountain import *
from functools import lru_cache
@lru_cache(None)
def extra(w):return 0 if w<=2 else w//4+1+max(extra(w//2),extra((w+1)//2))
base=(ROOT/'build/release.rom').read_bytes();new=(ROOT/'build/mountain_cull.rom').read_bytes()
fixtures=json.loads((ROOT/'tests/fixtures/index.json').read_text());dead=set(range(0x96,0x9e))|set(range(0xeb,0xf4))|set(range(0xf5,0xfe))
scenes=[]
for f in fixtures:
 mem=(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes();a=bankcpu(base,mem);b=bankcpu(new,mem)
 ca=run(a,0x87d3,f['regs']);cb=run(b,0x87d3,f['regs'])
 a.x=b.x=int(f['regs']['X'][1:],16)+3;ca+=run(a,0x9308);cb+=run(b,0x9308)
 diff=[i for i in range(0x8000) if not 0x100<=i<0x200 and a.memory[i]!=b.memory[i]]
 assert set(diff)<=dead,(f['name'],diff)
 assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp'))
 # Poison every dead slot before another complete renderer invocation.
 # Its inputs are regenerated before use: output must be independent.
 poisoned=bytearray(mem)
 for addr in dead:poisoned[addr]^=255
 z=bankcpu(new,poisoned);run(z,0x87d3,f['regs']);z.x=int(f['regs']['X'][1:],16)+3;run(z,0x9308)
 assert all(z.memory[j]==b.memory[j] for j in range(0x8000) if j not in dead and not 0x100<=j<0x200),f['name']
 scenes.append({'fixture':f['name'],'baseline_cycles':ca,'new_cycles':cb,'dead_slot_differences':[hex(j) for j in diff]})
print('Scene and poisoned-stack tests PASS',len(scenes),flush=True)
mem=(ROOT/'tests/fixtures/center-0.bin').read_bytes();rng=random.Random(9826503)
scratch=dead|{0x60,0x80,0x81,0x82,0x84,0x86,0xb5}
for i in range(5000):
 a=bankcpu(base,mem);b=bankcpu(new,mem)
 l=rng.randrange(44,211);r=rng.randrange(l+1,212)
 heights=[rng.randrange(256),rng.randrange(256)];phases=[rng.randrange(256),rng.randrange(256)]
 bound=min(255,max(heights)+extra(r-l))
 horizon=[max(108,bound) if i%2==0 else rng.randrange(108,256) for _ in range(256)]
 for c in (a,b):
  c.memory[0x82]=l;c.memory[0x95]=r;c.memory[0x84]=heights[0];c.memory[0xea]=heights[1]
  c.memory[0x86]=phases[0];c.memory[0xf4]=phases[1];c.memory[0x260e:0x270e]=horizon
 regs={'A':'$00','X':'$03','Y':'$00','P':'$30'}
 run(a,0x982a,regs);run(b,0x982a,regs)
 diffs=[j for j in range(0x8000) if j not in scratch and not 0x100<=j<0x200 and a.memory[j]!=b.memory[j]]
 assert not diffs,(i,l,r,heights,phases,diffs[:20])
 assert b.x==a.x and b.sp==a.sp and b.memory.bank==2
 if (i+1)%1000==0:print('Random culling',i+1,'PASS',flush=True)
(ROOT/'results/mountain/cull-validation.json').write_text(json.dumps({'scenes':scenes,'random_cases':5000,'poisoned_stack_scenes':len(scenes),'dead_stack_addresses':[hex(j) for j in sorted(dead)],'result':'pass'},indent=2))
