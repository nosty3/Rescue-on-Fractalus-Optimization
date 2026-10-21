from cpu_test_support import *
orig=(ROOT/'original/Rescue on Fractalus!.rom').read_bytes();rom=(ROOT/'build/release.rom').read_bytes()
mem=(ROOT/'tests/fixtures/center-0.bin').read_bytes();base=cpu(orig,mem)
f=json.loads((ROOT/'tests/fixtures/index.json').read_text())[0];run(base,0x87d3,f['regs']);template=bytes(base.memory)
rng=random.Random(982)
passes=0
for i in range(256):
 a=cpu(orig,template);b=cpu(rom,template);offset=3+(48 if i%2 else 0)
 for col in range(42):
  first=rng.randrange(49)
  for row in range(49):
   value=0 if row<first else rng.randrange(256)
   a.memory[0x1010+96*row+offset+col]=b.memory[0x1010+96*row+offset+col]=value
  a.memory[0x1010+96*49+offset+col]=b.memory[0x1010+96*49+offset+col]=255
 a.x=b.x=offset;a.p=b.p=0x30+(i&1);run(a,0x9308);run(b,0x9308)
 assert all(a.memory[j]==b.memory[j] for j in range(0x8000) if not 0x100<=j<0x200),i
 assert all(getattr(a,k)==getattr(b,k) for k in ['a','x','y','p','sp']),i
 passes+=1
(ROOT/'results/optimized/release_random_tests.json').write_text(json.dumps({'cases':passes,'byte_columns':passes*42,'result':'pass'},indent=2));print('PASS',passes,'fill cases',passes*42,'byte columns')



