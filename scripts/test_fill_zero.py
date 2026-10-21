from test_clear128 import *
old=(ROOT/'build/clear128.rom').read_bytes();new=(ROOT/'build/fill_zero.rom').read_bytes()
fixtures=json.loads((ROOT/'tests/fixtures/index.json').read_text());rows=[];zero=nonzero=0
def measured(c):
 global zero,nonzero
 c.pc=0x9308;c.sp=0xfd;c.memory[0x1fe]=0xfe;c.memory[0x1ff]=0x3f
 start=c.processorCycles;steps=0
 while c.pc!=0x3fff:
  if c.pc==0x95f6:
   ptr=c.memory[0x80]+256*c.memory[0x81];value=c.memory[(ptr+c.y)&65535]
   if value==0:zero+=1
   else:nonzero+=1
  c.step();steps+=1;assert steps<1000000
 return c.processorCycles-start
def compare(a,b,label):
 assert a.memory[0x3a00]==255 and a.memory[0x3b00]==0
 ca=measured(a);cb=run(b,0x9308)
 assert all(a.memory[j]==b.memory[j] for j in range(0x8000) if not 0x100<=j<0x200),label
 assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp')),label
 assert b.memory.bank==2
 return ca,cb
for f in fixtures:
 data=(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes();a=machine(old,data);b=machine(new,data)
 run(a,0x87d3,f['regs']);run(b,0x87d3,f['regs'])
 a.x=b.x=int(f['regs']['X'][1:],16)+3
 ca,cb=compare(a,b,f['name']);rows.append({'scene':f['name'],'old':ca,'new':cb,'saved':ca-cb})
scene_counts={'zero':zero,'nonzero':nonzero}
template=bytes(a.memory);rng=random.Random(0x95f6);random_savings=[]
for i in range(256):
 a=machine(old,template);b=machine(new,template);offset=3+(48 if i%2 else 0)
 for col in range(42):
  first=rng.randrange(49)
  for row in range(49):
   value=0 if row<first else rng.randrange(256)
   a.memory[0x1010+96*row+offset+col]=b.memory[0x1010+96*row+offset+col]=value
  a.memory[0x1010+96*49+offset+col]=b.memory[0x1010+96*49+offset+col]=255
 a.x=b.x=offset;a.p=b.p=0x30+(i&1)
 ca,cb=compare(a,b,i);random_savings.append(ca-cb)
out={'result':'pass','scenes':rows,'scene_input_counts':scene_counts,'scene_cycles_old':sum(r['old'] for r in rows),'scene_cycles_new':sum(r['new'] for r in rows),'random_cases':256,'random_saved_min':min(random_savings),'random_saved_max':max(random_savings)}
(ROOT/'results/fill_zero/equivalence.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k!='scenes'})
