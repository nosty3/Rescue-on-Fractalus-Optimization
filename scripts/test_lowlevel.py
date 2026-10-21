"""Test actual relocated ROM entry points including JMP overhead."""
from cpu_test_support import *
original=(ROOT/'build/mountain_cull.rom').read_bytes()
patched=(ROOT/'build/lowlevel_sound.rom').read_bytes()
template=(ROOT/'tests/fixtures/center-0.bin').read_bytes()
rows=[]
for entry in (0xbb19,0xbb3e):
 rng=random.Random(entry);saved=[]
 for case in range(3000):
  a=cpu(original,template);b=cpu(patched,template)
  for addr in list(range(0x66c,0x678))+list(range(0x706,0x712))+list(range(0x714,0x718)):
   value=rng.randrange(256) if addr<0x700 or addr>=0x714 else rng.choice([0,0,0,2,4,6,8])
   a.memory[addr]=b.memory[addr]=value
  a.memory[0x715]=b.memory[0x715]=rng.randrange(1,13)
  regs={r:f'${rng.randrange(256):02x}' for r in ('A','X','Y')};regs['P']='$30'
  ca=run(a,entry,regs);cb=run(b,entry,regs);saved.append(ca-cb)
  assert all(a.memory[j]==b.memory[j] for j in range(0x8000) if not 0x100<=j<0x200),(entry,case)
  assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp')),(entry,case)
 row={'entry':hex(entry),'cases':3000,'saved_min':min(saved),'saved_max':max(saved),'saved_mean':sum(saved)/len(saved)}
 rows.append(row);print(row,flush=True)
(ROOT/'results/lowlevel/equivalence.json').write_text(json.dumps({'result':'pass','tests':rows},indent=2))
