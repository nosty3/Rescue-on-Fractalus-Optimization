from cpu_test_support import *
from py65.disassembler import Disassembler
import subprocess
rom=(ROOT/'dist/Rescue on Fractalus! - PAL optimized v2.rom').read_bytes();template=(ROOT/'tests/fixtures/center-0.bin').read_bytes();c=cpu(rom,template);d=Disassembler(c)
lines=['; Audit prototype in test-only address space; no distributed ROM edit.',' opt h-',' org $c000']
def copy(lo,hi):
 pc=lo
 while pc<hi:
  n,t=d.instruction_at(pc)
  if t.endswith(' A'):t=t[:-1]+'@'
  lines.append(' '+t);pc+=n
def blend(idx,left,right,selector):
 lines.append(' lda #0')
 for bit in range(8):
  tag=f'b{idx}_{bit}'
  lines.extend([f' asl ${selector:04x}',f' bcs {tag}_one',f' lsr ${right:04x}',f' lsr ${left:04x}',f' adc ${left:04x}',f' jmp {tag}_done',tag+'_one',f' lsr ${left:04x}',f' lsr ${right:04x}',f' adc ${right:04x}',tag+'_done'])
copy(0x7eeb,0x7f37);blend(0,0x27f0,0x27f1,0x27fa)
lines+=[' sta $27f4',' stx $27fa'];blend(1,0x27f2,0x27f3,0x27fa)
lines+=[' sta $27f5',' lda $27ff',' sta $27fb'];blend(2,0x27f4,0x27f5,0x27fb)
copy(0x7faf,0x7fc2)
src=ROOT/'src/audit_interpolation.asm';src.write_text('\n'.join(lines)+'\n');binary=ROOT/'build/audit_interpolation.bin'
r=subprocess.run([str(ROOT/'tools/mads/bin/windows_x86_64/mads.exe'),str(src),'-o:'+str(binary)],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
code=binary.read_bytes();rng=random.Random(0x7eeb);total=[0,0];saved=[]
for i in range(1500):
 a=cpu(rom,template);b=cpu(rom,template);b.memory[0xc000:0xc000+len(code)]=code
 for addr in list(range(0x900,0xa00))+list(range(0x27fd,0x2801)):
  a.memory[addr]=b.memory[addr]=rng.randrange(256)
 regs={reg:f'${rng.randrange(256):02x}' for reg in ('A','X','Y')};regs['P']='$30'
 ca=run(a,0x7eeb,regs);cb=run(b,0xc000,regs);total[0]+=ca;total[1]+=cb;saved.append(ca-cb)
 assert all(a.memory[j]==b.memory[j] for j in range(0x8000) if not 0x100<=j<0x200),i
 assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp')),i
out={'cases':1500,'bytes':len(code),'original_bytes':0x7fc2-0x7eeb,'cycles':total,'mean_saved':sum(saved)/len(saved),'min_saved':min(saved),'max_saved':max(saved),'result':'pass'}
(ROOT/'analysis/lowlevel/interpolation-tests.json').write_text(json.dumps(out,indent=2));print(out)
