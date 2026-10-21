"""Observe released v5 on existing renderer inputs; no code changes."""
from test_clear128 import *
from collections import Counter,defaultdict
from py65.disassembler import Disassembler
import re
OUT=ROOT/'results/research_v5';rom=(ROOT/'dist/Rescue on Fractalus! - PAL optimized v5 128KB.rom').read_bytes()
fixtures=json.loads((ROOT/'tests/fixtures/index.json').read_text());counts=Counter();pages=Counter();div=[];widths=Counter();firsts=Counter();masks=Counter();pixel=Counter();by_scene=[]
labels={}
for line in (ROOT/'build/mountain_cull.lst').read_text().splitlines():
 m=re.match(r'^\s*\d+\s+([0-9A-F]{4})\s+(d\w+_([0-9a-f]{4}))\s*$',line)
 if m:labels[int(m[1],16)]=(m[2],int(m[3],16))
for f in fixtures:
 c=machine(rom,(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes())
 for dst,src in [('a','A'),('x','X'),('y','Y'),('p','P')]:setattr(c,dst,int(f['regs'][src][1:],16))
 start=c.processorCycles;last_pixel=None;previous_div=None
 for entry in (0x87d3,0x9308):
  if entry==0x9308:
   c.x=int(f['regs']['X'][1:],16)+3
   for col in range(42):
    row=next((r for r in range(49) if c.memory[0x1010+96*r+c.x+col]),48);firsts[row]+=1
  c.pc=entry;c.sp=0xfd;c.memory[0x1fe]=0xfe;c.memory[0x1ff]=0x3f;steps=0
  while c.pc!=0x3fff:
   pc=c.pc;bank=c.memory.bank;op=c.memory[pc];mn,mode=c.disassemble[op];key=f'{bank}:{pc:04x}';counts[key]+=1
   if bank==2 and pc==0x8224:
    n=c.memory[0xb0]+256*c.memory[0xb1];d=c.memory[0xae]+256*c.memory[0xaf];sh=0;dd=d
    while not dd&0x4000 and sh<16:dd=(dd<<1)&65535;sh+=1
    div.append({'scene':f['name'],'n':n,'d':d,'shift':sh,'same_previous_divisor':previous_div==d});previous_div=d
   if bank==5 and pc in labels:
    name,orig=labels[pc]
    if orig==0x993b:widths[(c.memory[0x95+c.y]-c.x)&255]+=1
   if bank==5 and op==0x91 and c.memory[pc+1]==0x80:
    at=(c.memory[0x80]+256*c.memory[0x81]+c.y)&65535;pixel['writes']+=1
    if at==last_pixel:pixel['consecutive_same_address']+=1
    last_pixel=at
   if bank==9 and op in (0xb9,0xb1):
    if op==0xb9:addr=c.memory[pc+1]+256*c.memory[pc+2]
    else:addr=0
    # All actual body/first-loop loads are followed by TAX; scan loads are not.
    size=3 if op==0xb9 else 2
    if c.memory[pc+size]==0xaa:masks[c.memory[0x96]]+=1
   if mode in ('abx','aby','iny'):
    if mode=='iny':z=c.memory[pc+1];base=c.memory[z]+256*c.memory[(z+1)&255];idx=c.y
    else:base=c.memory[pc+1]+256*c.memory[pc+2];idx=c.x if mode=='abx' else c.y
    if ((base+idx)^base)&0xff00 and mn in ('LDA','LDX','LDY','ADC','SBC','CMP','AND','ORA','EOR'):pages[key]+=1
   next_pc=(pc+2)&65535;before=c.processorCycles;c.step();steps+=1
   if mode=='rel' and c.pc!=next_pc and ((c.pc^next_pc)&0xff00):pages[key]+=1
   assert steps<1000000
  by_scene.append({'scene':f['name'],'entry':hex(entry),'cycles':c.processorCycles-start});start=c.processorCycles
 print(f['name'],flush=True)
out={'scenes':len(fixtures),'counts':dict(counts),'page_penalties':dict(pages),'division_inputs':div,'widths':dict(widths),'fill_first_rows':dict(firsts),'fill_masks':dict(masks),'pixel':dict(pixel),'scene_cycles':by_scene}
(OUT/'renderer-trace.json').write_text(json.dumps(out,indent=2))
print('SUMMARY',json.dumps({k:v for k,v in out.items() if k not in ('counts','page_penalties','division_inputs','scene_cycles')}))
