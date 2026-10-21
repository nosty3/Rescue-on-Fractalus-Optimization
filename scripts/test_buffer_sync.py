from opt14_cpu import *
OUT=ROOT/'results/buffer_race';old=(ROOT/'build/v7_clipping.rom').read_bytes();new=(ROOT/'build/buffer_sync.rom').read_bytes();mem=(ROOT/'tests/fixtures/center-0.bin').read_bytes();rng=random.Random(4242)
for x in range(256):
 data=bytearray(mem);data[0x42]=0;a=machine(old,data);b=machine(new,data);regs={'A':f'${rng.randrange(256):02x}','X':f'${x:02x}','Y':f'${rng.randrange(256):02x}','P':f'${rng.choice((0x30,0x31,0x70,0x71)):02x}'}
 run(a,0x9214,regs);run(b,0x9214,regs)
 assert all(a.memory[j]==b.memory[j] for j in range(0x8000) if not 0x100<=j<0x200),x
 assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp')),x
for flag in (1,2):
 for x in (3,51):
  c=machine(new,mem);c.pc=0x9214;c.sp=0xfd;c.a=0x73;c.x=x;c.y=0x42;c.p=0x71;c.memory[0x42]=flag;c.memory[0x4a]=2;before=list(c.memory)
  for _ in range(200):c.step()
  assert 0x84a0<=c.pc<0x84b1 and c.memory[0x42]==flag
  assert all(c.memory[j]==before[j] for j in range(0x8000) if not 0x100<=j<0x200)
  c.memory[0x42]=0
  for _ in range(20):
   if c.pc==0x982f:break
   c.step()
  assert (c.pc,c.a,c.x,c.y,c.p,c.sp)==(0x982f,0x73,x,0x42,0x71,0xfd)
# Presentation is not acknowledged outside flight; that path must not hang.
c=machine(new,mem);c.pc=0x9214;c.memory[0x42]=2;c.memory[0x4a]=0
for _ in range(20):
 if c.pc==0x982f:break
 c.step()
assert c.pc==0x982f
(OUT/'cpu-tests.json').write_text(json.dumps({'result':'pass','clear_inputs':256,'pending_flag_wait_cases':4,'nonflight_bypass':True,'registers_flags_and_ram_preserved':True},indent=2));print('Buffer sync CPU PASS')
