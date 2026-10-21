from opt14_cpu import *
from collections import Counter
OUT=ROOT/'results/opt14';old=(ROOT/'build/opt14_base.rom').read_bytes();new=(ROOT/'build/opt14_division.rom').read_bytes()
class Monitor(Memory):
 def __init__(self,rom,mem):super().__init__(rom,mem);self.active=False;self.pc=0;self.hits=Counter()
 def __getitem__(self,key):
  if self.active and isinstance(key,int) and key in (0xae,0xaf,0xb0,0xb1):self.hits[f'{self.pc:04x}:{key:02x}']+=1
  return super().__getitem__(key)
rows=[]
for f in json.loads((ROOT/'tests/fixtures/index.json').read_text()):
 mem=(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes();m=Monitor(new,mem);c=MPU(memory=m)
 for tick in range(4):
  c.pc=0xbfda;c.sp=0xfd;m[5]=0;m[0xd40b]=0x80;m[0xd20a]=0;steps=0
  while c.pc!=0xe462:
   m.pc=c.pc;m.active=True;c.step();m.active=False;steps+=1
   assert steps<200000,(f['name'],hex(c.pc))
  assert not m.hits,(f['name'],m.hits)
 rows.append({'scene':f['name'],'vbi_passes':4,'divider_scratch_reads':dict(m.hits)})
(OUT/'division-vbi-tests.json').write_text(json.dumps({'result':'pass','checks':rows,'scope':'Full flight VBI paths on 58 fixtures x4; fixed hardware inputs for standalone CPU test.'},indent=2));print('VBI PASS',len(rows)*4)
