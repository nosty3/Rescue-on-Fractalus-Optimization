"""Arithmetic/cycle models only: does not assemble or patch game code."""
from test_clear128 import *
from collections import Counter
OUT=ROOT/'results/research_v5';rom=(ROOT/'dist/Rescue on Fractalus! - PAL optimized v5 128KB.rom').read_bytes();ram=(OUT/'ram-local.bin').read_bytes()
trace=json.loads((OUT/'renderer-trace.json').read_text())
def divide_model(n,d,normalize):
 shifts=0
 if normalize:
  while not d&0x4000:n<<=1;d<<=1;shifts+=1
 cycles=31+26*shifts if normalize else 23;q=0
 for i in range(8):
  n<<=1;q<<=1
  if n>>8 < d>>8:cycles+=18
  elif n>=d:cycles+=38;n-=d;q|=1
  else:cycles+=39
 return q,cycles
rows=[]
for item in trace['division_inputs']:
 n,d=item['n'],item['d'];assert 0<=n<d<32768
 qo,co=divide_model(n,d,True);qn,cn=divide_model(n,d,False);assert qo==qn==256*n//d
 rows.append(co-cn)
for item in trace['division_inputs'][::17]:
 c=machine(rom,ram);n,d=item['n'],item['d'];c.memory[0xb0]=n&255;c.memory[0xb1]=n>>8;c.memory[0xae]=d&255;c.memory[0xaf]=d>>8;c.p=0x30
 cyc=run(c,0x8224);q,model=divide_model(n,d,True);assert cyc==model,(cyc,model);assert c.memory[0xb2]==q
def contribution(v,f,bits):
 total=0
 for b in range(bits-1,-1,-1):
  if f>>b&1:total+=(v+1)//2
  v>>=1
 return total
table=[[contribution(v,f,4) for v in range(256)] for f in range(16)]
for v in range(256):
 for f in range(256):assert contribution(v,f,8)==table[f>>4][v]+table[f&15][v>>4]
def mix(a,b,f):return (table[(f>>4)^15][a]+table[(f&15)^15][a>>4]+table[f>>4][b]+table[f&15][b>>4])&255
rng=random.Random(82247);cpu_cases=1000
for i in range(cpu_cases):
 c=machine(rom,ram);data=[rng.randrange(256) for _ in range(256)];c.memory[0x900:0xa00]=data
 for at in (0x2800,0x27fe,0x27fd,0x27ff):c.memory[at]=rng.randrange(256)
 row=(c.memory[0x2800]<<4)&255;col=c.memory[0x27fe]&15;row2=(row+16)&255;col2=(col+1)&15;fx=c.memory[0x27fd];fy=c.memory[0x27ff]
 u=mix(data[row|col],data[row|col2],fx);v=mix(data[row2|col],data[row2|col2],fx);z=mix(u,v,fy);t=z>>4;expected=(z+t+((t+1)//2))&255
 c.p=0x30;run(c,0x7eeb);assert c.memory[0x62]==expected
out={'division':{'input_count':len(rows),'model_verified_on_original_calls':len(trace['division_inputs'][::17]),'quotients_match':True,'divisor_min':min(x['d'] for x in trace['division_inputs']),'divisor_max':max(x['d'] for x in trace['division_inputs']),'cycles_saved_min':min(rows),'cycles_saved_max':max(rows),'cycles_saved_mean':sum(rows)/len(rows),'slower_cases':sum(x<0 for x in rows),'caveat':'Only quotient/cycles modeled. Changed normalized scratch state requires liveness proof; no patched code or ROM.'},'nibble_table':{'bytes':4096,'contribution_identities_checked':65536,'full_interpolation_cases_against_original_6502':cpu_cases,'result':'pass','caveat':'Arithmetic output only; integration, all registers, flags, scratch and interrupts not validated.'}}
(OUT/'arithmetic-models.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
