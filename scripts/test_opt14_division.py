from opt14_cpu import *
from collections import Counter
OUT=ROOT/'results/opt14';old=(ROOT/'build/opt14_base.rom').read_bytes();new=(ROOT/'build/opt14_division.rom').read_bytes();ram=(ROOT/'tests/fixtures/center-0.bin').read_bytes();rng=random.Random(822414)
a=machine(old,ram);b=machine(new,ram);cases=[(d,n) for d in (1,2,3,127,128,255,256,257,8191,16383,16384,32767) for n in sorted({0,d//2,d-1})]+[(d:=rng.randrange(1,32768),rng.randrange(d)) for _ in range(20000)];savings=[]
for d,n in cases:
 x=rng.randrange(256);initial=rng.randrange(256);p=rng.choice((0x30,0x31,0x70,0x71))
 for c in (a,b):c.memory[0xae:0xb3]=[d&255,d>>8,n&255,n>>8,initial];c.a=77;c.x=x;c.y=49;c.p=p
 ca=run(a,0x8224);cb=run(b,0x8224);savings.append(ca-cb)
 assert a.memory[0xb2]==b.memory[0xb2]==256*n//d
 assert b.x==x and b.a==a.a and b.sp==a.sp and b.p&1==a.p&1
rows=[]
for f in json.loads((ROOT/'tests/fixtures/index.json').read_text()):
 mem=(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes();a=machine(old,mem);b=machine(new,mem)
 ca=run(a,0x87d3,f['regs']);cb=run(b,0x87d3,f['regs']);a.x=b.x=int(f['regs']['X'][1:],16)+3;ca+=run(a,0x9308);cb+=run(b,0x9308)
 diffs=[i for i in range(0x8000) if not 0x100<=i<0x200 and a.memory[i]!=b.memory[i]]
 assert set(diffs)<=set((0xae,0xaf,0xb0,0xb1)),(f['name'],[hex(i) for i in diffs])
 assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp')),f['name']
 # Continue the following main-loop calls, including next geometry/render iteration.
 for entry in (0x8e51,0xa444,0x8309):
  run(a,entry);run(b,entry)
  assert all(a.memory[i]==b.memory[i] for i in range(0x8000) if not 0x100<=i<0x200 and i not in (0xae,0xaf,0xb0,0xb1)),(f['name'],hex(entry))
 rows.append({'scene':f['name'],'old_cycles':ca,'new_cycles':cb,'saved':ca-cb})
out={'result':'pass','division_cases':len(cases),'scenes':rows,'scratch_exceptions':['AE','AF','B0','B1'],'following_calls':['8E51','A444','8309'],'division_saved_min':min(savings),'division_saved_max':max(savings)}
(OUT/'division-tests.json').write_text(json.dumps(out,indent=2));print('PASS',len(cases),len(rows),'renderer saved',sum(r['saved'] for r in rows),flush=True)
