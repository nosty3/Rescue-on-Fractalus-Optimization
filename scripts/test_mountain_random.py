from test_mountain import *
import argparse
parser=argparse.ArgumentParser();parser.add_argument('variant',nargs='?',default='mountain_w3');parser.add_argument('--cases',type=int,default=5000);args=parser.parse_args()
base=(ROOT/'build/release.rom').read_bytes();new=(ROOT/f'build/{args.variant}.rom').read_bytes()
mem=(ROOT/'tests/fixtures/center-0.bin').read_bytes();rng=random.Random(9826502)
total=[0,0];fail=[]
for i in range(args.cases):
 a=bankcpu(base,mem);b=bankcpu(new,mem)
 left=rng.randrange(256);right=rng.randrange(256)
 if i%4==0:right=min(255,left+3)
 heights=[rng.randrange(256),rng.randrange(256)];phases=[rng.randrange(256),rng.randrange(256)]
 horizon=[rng.randrange(108,256) for _ in range(256)]
 for c in (a,b):
  c.memory[0x82]=left;c.memory[0x95]=right;c.memory[0x84]=heights[0];c.memory[0xea]=heights[1]
  c.memory[0x86]=phases[0];c.memory[0xf4]=phases[1];c.memory[0x260e:0x270e]=horizon
 regs={'A':f'${rng.randrange(256):02x}','X':f'${rng.randrange(16):02x}','Y':f'${rng.randrange(16):02x}','P':f'${(rng.randrange(256)&~8)|0x30:02x}'}
 total[0]+=run(a,0x982a,regs);total[1]+=run(b,0x982a,regs)
 diffs=[hex(j) for j in range(0x8000) if not 0x100<=j<0x200 and a.memory[j]!=b.memory[j]]
 rd=[k for k in ['a','x','y','p','sp'] if getattr(a,k)!=getattr(b,k)]
 if diffs or rd or b.memory.bank!=2:
  fail.append({'case':i,'left':left,'right':right,'heights':heights,'phases':phases,'diff':diffs[:20],'registers':rd});break
out={'cases_completed':i+1,'seed':9826502,'cycles':total,'failures':fail,'note':'Arbitrary byte endpoints/heights/phases and random horizon; includes reversed/offscreen intervals, 25% forced width3.'}
(ROOT/f'results/mountain/{args.variant}-random.json').write_text(json.dumps(out,indent=2));print(out)
assert not fail

