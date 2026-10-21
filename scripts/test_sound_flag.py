"""Exercise the entire sound update with lazy reset of its event flag."""
from cpu_test_support import *
import subprocess
base=(ROOT/'build/lowlevel_full.rom').read_bytes();rom=bytearray(base)
source='''; Reset event flag only after consumption, preserve last-channel value.
 opt h-
 org $bb1c
 jsr $bca4
 cpy #1
 beq done
 lda #0
 sta $0718
done
 rts
'''
src=ROOT/'src/lowlevel_sound_flag.asm';src.write_text(source);binary=ROOT/'build/lowlevel_sound_flag.bin'
subprocess.run([str(ROOT/'tools/mads/bin/windows_x86_64/mads.exe'),str(src),'-o:'+str(binary)],check=True)
code=binary.read_bytes();assert len(code)<=0xbb3e-0xbb1c
rom[0xfb1c:0xfb1c+len(code)]=code
assert rom[0xf9a7:0xf9aa]==bytes.fromhex('20a4bc')
assert rom[0xf9ad:0xf9b0]==bytes.fromhex('4c26b9')
rom[0xf9a7:0xf9aa]=bytes.fromhex('201cbb')
rom[0xf9ad:0xf9b0]=bytes.fromhex('4c2bb9')
counts={'events':0,'last_channel_events':0};savings=[]
def measured(c):
 c.pc=0xb91c;c.sp=0xfd;c.memory[0x1fe]=0xfe;c.memory[0x1ff]=0x3f
 start=c.processorCycles;steps=0
 while c.pc!=0x3fff:
  if c.pc==0xbb1c:
   counts['events']+=1
   if c.y==1:counts['last_channel_events']+=1
  c.step();steps+=1
  assert steps<100000
 return c.processorCycles-start
fixtures=json.loads((ROOT/'tests/fixtures/index.json').read_text())
for fixture in fixtures:
 mem=(ROOT/f"tests/fixtures/{fixture['name']}.bin").read_bytes()
 a=cpu(base,mem);b=cpu(rom,mem)
 for frame in range(100):
  ca=run(a,0xb91c);cb=measured(b);savings.append(ca-cb)
  assert all(a.memory[j]==b.memory[j] for j in range(65536) if not 0x100<=j<0x200 and not 0x8000<=j<0xc000),(fixture['name'],frame)
  assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp')),(fixture['name'],frame)
out={'result':'pass','calls':len(savings),'saved_mean':sum(savings)/len(savings),'saved_min':min(savings),'saved_max':max(savings),'coverage':counts}
(ROOT/'results/lowlevel/flag-equivalence.json').write_text(json.dumps(out,indent=2));print(out)
(ROOT/'build/lowlevel_flag.rom').write_bytes(rom)
