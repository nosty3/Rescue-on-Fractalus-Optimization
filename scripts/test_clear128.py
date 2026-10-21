from cpu_test_support import *
class Memory(list):
 def __init__(self,rom,mem):
  super().__init__(mem);self.rom=rom;self.bank=2
  super().__setitem__(slice(0x8000,0xa000),rom[0x4000:0x6000])
  super().__setitem__(slice(0xa000,0xc000),rom[-8192:])
 def __setitem__(self,key,value):
  if isinstance(key,int) and 0xd500<=key<=0xd5ff:
   self.bank=value&(len(self.rom)//8192-1)
   super().__setitem__(slice(0x8000,0xa000),self.rom[self.bank*8192:(self.bank+1)*8192])
  elif isinstance(key,int) and 0x8000<=key<0xc000:raise AssertionError(('ROM write',key))
  else:super().__setitem__(key,value)
def machine(rom,mem):return MPU(memory=Memory(rom,mem))
if __name__=='__main__':
 old=(ROOT/'build/clear_baseline64.rom').read_bytes();new=(ROOT/'build/clear128.rom').read_bytes()
 mem=bytearray((ROOT/'tests/fixtures/center-0.bin').read_bytes());rng=random.Random(9214);rows=[]
 for x in list(range(256))+[3,51]*100:
  mem[0x1000:0x2400]=bytes(rng.randrange(256) for _ in range(0x1400))
  regs={'A':f'${rng.randrange(256):02x}','X':f'${x:02x}','Y':f'${rng.randrange(256):02x}','P':f'${rng.choice([0x30,0x31,0x70,0x71]):02x}'}
  a=machine(old,mem);b=machine(new,mem);ca=run(a,0x9214,regs);cb=run(b,0x9214,regs)
  assert all(a.memory[j]==b.memory[j] for j in range(0x8000) if not 0x100<=j<0x200),x
  assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp')),x
  assert b.memory.bank==2
  rows.append({'x':x,'old':ca,'new':cb,'saved':ca-cb})
 for bank in (2,5,6,8):
  c=machine(new,mem);c.memory[0xd500]=bank;c.pc=0xbfda;c.sp=0xf0
  while c.pc!=0xb470:c.step()
  assert c.memory.bank==2;c.pc=0xbfea
  while c.pc!=0xe462:c.step()
  assert c.memory.bank==bank and c.sp==0xf0
 fixtures=json.loads((ROOT/'tests/fixtures/index.json').read_text())
 for f in fixtures:
  data=(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes();a=machine(old,data);b=machine(new,data)
  run(a,0x87d3,f['regs']);run(b,0x87d3,f['regs']);a.x=b.x=int(f['regs']['X'][1:],16)+3
  run(a,0x9308);run(b,0x9308)
  assert all(a.memory[j]==b.memory[j] for j in range(0x8000) if not 0x100<=j<0x200),f['name']
  assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp'))
 out={'result':'pass','clear_cases':len(rows),'renderer_scenes':len(fixtures),'banks':[2,5,6,8],'fast_paths':[r for r in rows[:256] if r['x'] in (3,51)],'fallback_saved_cycles':rows[0]['saved']}
 (ROOT/'results/clear128/equivalence.json').write_text(json.dumps(out,indent=2));print(out)
