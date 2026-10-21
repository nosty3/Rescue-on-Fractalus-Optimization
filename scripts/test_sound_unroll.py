from cpu_test_support import *
import subprocess
rom=(ROOT/'dist/Rescue on Fractalus! - PAL optimized v2.rom').read_bytes();template=(ROOT/'tests/fixtures/center-0.bin').read_bytes()
results=[]
for entry,kind in [(0xbb19,'minimum'),(0xbb3e,'maximum')]:
 lines=['; Standalone audit prototype, NOT patched into distributed game.',' opt h-',f' org ${entry:04x}']
 if kind=='minimum':lines+=[' lda #16',' sta $0716']
 else:lines+=[' ldx #0',' stx $0716']
 for i in range(1,13):
  if kind=='maximum':lines.append(f' ldx #{i}')
  lines += [f' lda ${0x705+i:04x}',f' beq check_{i}' if kind=='maximum' else f' beq next_{i}']
  if kind=='maximum':lines += [' cpx $0715',f' bne next_{i}',f'check_{i}']
  lines += [f' lda ${0x66b+i:04x}',' and #15',' cmp $0716',f" {'bcs' if kind=='minimum' else 'bcc'} next_{i}",' sta $0716']
  if kind=='minimum':lines+=[' sta $0714',f' ldx #{i}',' stx $0715']
  else:lines+=[' stx $0717']
  lines.append(f'next_{i}')
 if kind=='minimum':lines+=[' ldx #12']
 lines+=[' cpx #12',' rts']
 name='audit_sound_'+kind;src=ROOT/f'src/{name}.asm';src.write_text('\n'.join(lines)+'\n')
 binary=ROOT/f'build/{name}.bin'
 r=subprocess.run([str(ROOT/'tools/mads/bin/windows_x86_64/mads.exe'),str(src),'-o:'+str(binary)],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 code=binary.read_bytes();rng=random.Random(6502);oldcycles=newcycles=0;mins=9999;maxs=0
 for case in range(3000):
  a=cpu(rom,template);b=cpu(rom,template);b.memory[entry:entry+len(code)]=code
  for addr in list(range(0x66c,0x678))+list(range(0x706,0x712))+list(range(0x714,0x718)):
   value=rng.randrange(256) if addr<0x700 or addr>=0x714 else rng.choice([0,0,0,2,4,6,8])
   a.memory[addr]=b.memory[addr]=value
  a.memory[0x715]=b.memory[0x715]=rng.randrange(1,13)
  regs={r:f'${rng.randrange(256):02x}' for r in ('A','X','Y','P')};regs['P']='$30'
  ca=run(a,entry,regs);cb=run(b,entry,regs);oldcycles+=ca;newcycles+=cb;mins=min(mins,ca-cb);maxs=max(maxs,ca-cb)
  assert all(a.memory[j]==b.memory[j] for j in range(0x8000) if not 0x100<=j<0x200),(kind,case)
  assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp')),(kind,case)
 results.append({'entry':hex(entry),'kind':kind,'cases':3000,'bytes':len(code),'old_cycles':oldcycles,'new_cycles':newcycles,'saved_per_call_mean':(oldcycles-newcycles)/3000,'saved_per_call_min':mins,'saved_per_call_max':maxs})
 print(results[-1],flush=True)
(ROOT/'analysis/lowlevel/sound-tests.json').write_text(json.dumps(results,indent=2))
