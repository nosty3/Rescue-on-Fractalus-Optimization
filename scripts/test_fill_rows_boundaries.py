from test_clear128 import *
old=(ROOT/'build/clear128.rom').read_bytes();new=(ROOT/'build/fill_rows.rom').read_bytes()
template=(ROOT/'tests/fixtures/center-0.bin').read_bytes();count=0
for first in (0,1,31,32,33,47,48):
 for offset in (3,51):
  for flags in (0x30,0x31,0x70,0x71):
   a=machine(old,template);b=machine(new,template)
   for col in range(42):
    for row in range(70):
     value=1 if row==first else 255 if row>=69 else 0
     a.memory[0x1010+96*row+offset+col]=b.memory[0x1010+96*row+offset+col]=value
   a.x=b.x=offset;a.p=b.p=flags
   run(a,0x9308);run(b,0x9308)
   assert all(a.memory[j]==b.memory[j] for j in range(0x8000) if not 0x100<=j<0x200),(first,offset,flags)
   assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp')),(first,offset,flags)
   assert b.memory.bank==2;count+=1
fixtures=json.loads((ROOT/'tests/fixtures/index.json').read_text())
for f in fixtures:
 mem=(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes()
 for r in range(49):assert mem[0x73d+r]+256*mem[0x793+r]==0x1010+96*r,(f['name'],r)
c=machine(new,template);c.memory[0xd500]=9;c.pc=0xbfda;c.sp=0xf0
while c.pc!=0xb470:c.step()
assert c.memory.bank==2;c.pc=0xbfea
while c.pc!=0xe462:c.step()
assert c.memory.bank==9 and c.sp==0xf0
out={'result':'pass','long_tail_cases':count,'last_row':69,'tested_first_rows':[0,1,31,32,33,47,48],'row_table_fixtures':len(fixtures),'vbi_bank9_restored':True,'decimal_flag':0}
(ROOT/'results/fill_rows/boundaries.json').write_text(json.dumps(out,indent=2));print(out)
