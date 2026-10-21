from opt14_cpu import *
OUT=ROOT/'results/opt14'
old=(ROOT/'build/opt14_width45.rom').read_bytes();new=(ROOT/'build/opt14_interpolation.rom').read_bytes()
meta=json.loads((OUT/'opt14_interpolation-build.json').read_text());patch=bytes.fromhex(meta['ram_patches'][0]['hex'])
mem=(ROOT/'tests/fixtures/center-0.bin').read_bytes()
for x in range(256):
 a=machine(old,mem);b=machine(new,mem)
 regs={'A':'$00','X':f'${x:02x}','Y':'$00','P':'$30'}
 run(a,0x9214,regs);run(b,0x9214,regs)
 assert all(a.memory[j]==b.memory[j] for j in range(0x8000) if not 0x100<=j<0x200),x
 assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp')),x
banks=(2,5,6,8,9,10,11,12,13,14)
for bank in banks:
 c=machine(new,mem);c.memory[0xd500]=bank;c.pc=0xbfda;c.sp=0xf0
 while c.pc!=0xb470:c.step()
 assert c.memory.bank==2;c.pc=0xbfea
 while c.pc!=0xe462:c.step()
 assert c.memory.bank==bank and c.sp==0xf0
checks=0
for f in json.loads((ROOT/'tests/fixtures/index.json').read_text()):
 data=(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes();a=machine(old,data);b=machine(new,data);b.memory[0x7eeb:0x7fc2]=patch
 for tick in range(4):
  for c in (a,b):
   c.pc=0xbfda;c.sp=0xfd;c.memory[5]=0;c.memory[0xd40b]=0x80;c.memory[0xd20a]=0;steps=0
   while c.pc!=0xe462:
    c.step();steps+=1;assert steps<200000
  diffs=[hex(j) for j in range(0x8000) if not 0x100<=j<0x200 and not 0x7eeb<=j<0x7fc2 and a.memory[j]!=b.memory[j]]
  assert not diffs,(f['name'],tick,diffs[:20])
  assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp')),(f['name'],tick)
  assert a.memory.bank==b.memory.bank==2
  checks+=1
(OUT/'integration-tests.json').write_text(json.dumps({'result':'pass','clear_all_x':256,'vbi_bank_restore':banks,'full_vbi_equivalence':checks,'excluded_ram':['dead hardware stack','replaced code 7EEB..7FC1'],'hardware_inputs':'D40B=80 D20A=00'},indent=2))
print('Integration PASS',checks,flush=True)
