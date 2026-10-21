from opt14_cpu import *
OUT=ROOT/'results/opt14';old=(ROOT/'build/opt14_division.rom').read_bytes();new=(ROOT/'build/opt14_width45.rom').read_bytes();mem=(ROOT/'tests/fixtures/center-0.bin').read_bytes();rng=random.Random(45026502);total=[0,0]
for i in range(6000):
 a=machine(old,mem);b=machine(new,mem);left=rng.randrange(256);right=min(255,left+rng.choice([4,5,8,9,10,16,20,32,40,64,80])) if i%2==0 else rng.randrange(256)
 heights=[rng.randrange(256),rng.randrange(256)];phases=[rng.randrange(256),rng.randrange(256)];horizon=[rng.randrange(108,256) for _ in range(256)]
 for c in (a,b):
  c.memory[0x82]=left;c.memory[0x95]=right;c.memory[0x84]=heights[0];c.memory[0xea]=heights[1];c.memory[0x86]=phases[0];c.memory[0xf4]=phases[1];c.memory[0x260e:0x270e]=horizon
 regs={'A':'$00','X':f'${rng.randrange(16):02x}','Y':'$00','P':f'${rng.choice((0x30,0x31,0x70,0x71)):02x}'}
 total[0]+=run(a,0x982a,regs);total[1]+=run(b,0x982a,regs)
 diffs=[hex(j) for j in range(0x8000) if not 0x100<=j<0x200 and a.memory[j]!=b.memory[j]];rd=[k for k in ('a','x','y','p','sp') if getattr(a,k)!=getattr(b,k)]
 assert not diffs and not rd,(i,left,right,heights,phases,diffs[:15],rd,hex(a.p),hex(b.p))
(OUT/'width45-random.json').write_text(json.dumps({'result':'pass','cases':6000,'cycles':total},indent=2));print('Random width4/5 PASS',total)
