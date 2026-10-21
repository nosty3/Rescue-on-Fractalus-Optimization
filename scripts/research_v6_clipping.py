from opt14_cpu import *
from collections import Counter
OUT=ROOT/'results/research_v6';rom=(ROOT/'build/opt14_interpolation.rom').read_bytes();counts=Counter();samples=[]
for f in json.loads((ROOT/'tests/fixtures/index.json').read_text()):
 c=machine(rom,(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes());c.pc=0x87d3;c.sp=0xfd;c.memory[0x1fe]=0xfe;c.memory[0x1ff]=0x3f
 for dst,src in [('a','A'),('x','X'),('y','Y'),('p','P')]:setattr(c,dst,int(f['regs'][src][1:],16))
 while c.pc!=0x3fff:
  if c.memory.bank==2 and c.pc==0x9627:
   m=c.memory;counts['total']+=1
   if c.x==0 and all(m[a]==0 for a in (0x83,0x85,0x25d2,0x24e2)):
    counts['all_high_zero']+=1
    if m[0x82]<m[0x25b4] and m[0x82]<216:
     counts['ordered_inside']+=1
     if m[0x84]>=108 and m[0x25f0]>=108:counts['direct_draw']+=1
     elif m[0x84]<108 and m[0x25f0]<108:counts['direct_skip']+=1
     else:counts['mixed']+=1
   samples.append({'x':c.x,'x0':m[0x82]+256*m[0x83],'x1':m[0x25b4]+256*m[0x25d2],'y0':m[0x84]+256*m[0x85],'y1':m[0x25f0]+256*m[0x24e2]})
  c.step()
(OUT/'clipping-census.json').write_text(json.dumps({'counts':dict(counts),'samples':samples},indent=2));print(dict(counts))
