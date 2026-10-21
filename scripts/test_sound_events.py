"""Stress simultaneous sound events and ordered POKEY writes against v2."""
from cpu_test_support import *
old=(ROOT/'build/mountain_cull.rom').read_bytes();new=(ROOT/'build/lowlevel_flag.rom').read_bytes()
class Traced(list):
 def __init__(self,items):super().__init__(items);self.writes=[]
 def __setitem__(self,key,value):
  if isinstance(key,int) and 0xd200<=key<=0xd20f:self.writes.append((key,value))
  super().__setitem__(key,value)
def pair(mem):
 a=cpu(old,mem);b=cpu(new,mem)
 a.memory=Traced(a.memory);b.memory=Traced(b.memory)
 return a,b
def compare(a,b,label):
 a.memory.writes=[];b.memory.writes=[]
 run(a,0xb91c);run(b,0xb91c)
 assert a.memory.writes==b.memory.writes,label
 assert all(a.memory[j]==b.memory[j] for j in range(0x8000) if not 0x100<=j<0x200),label
 assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp')),label
 return len(a.memory.writes)
template=(ROOT/'tests/fixtures/center-0.bin').read_bytes();rng=random.Random(718);writes=0
phase=next(i for i in range(1,44) if old[0xf895+i])
for case in range(400):
 mem=list(template);mem[0x65e:0x739]=[0]*(0x739-0x65e)
 mem[0x631]=0;mem[0x73]=mem[0x74]=31;mem[0x715]=1
 for y in range(1,15):
  active=True if case==0 else bool(rng.randrange(2))
  for delta,position,step,end,value in [(0x6db,0x6e9,0x6bf,0x6cd,0x679),(0x6a3,0x6b1,0x687,0x695,0x66b)]:
   mem[delta+y]=int(active);mem[position+y]=phase-1
   mem[step+y]=1;mem[end+y]=1;mem[value+y]=0
  mem[0x705+y]=0
 a,b=pair(mem);writes+=compare(a,b,case)
fixtures=json.loads((ROOT/'tests/fixtures/index.json').read_text())
for f in fixtures:
 a,b=pair((ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes())
 for frame in range(20):writes+=compare(a,b,(f['name'],frame))
out={'result':'pass','synthetic_cases':400,'fixture_calls':len(fixtures)*20,'pokey_writes_compared':writes,'includes_all_14_channels_dual_event':True,'note':'Register/value order compared; CPU write timestamps intentionally differ.'}
(ROOT/'results/lowlevel/sound-events.json').write_text(json.dumps(out,indent=2));print(out)
