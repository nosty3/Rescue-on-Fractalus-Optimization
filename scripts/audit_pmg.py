"""Read-only PMG audit: static candidates and CPU instruction/write counts."""
from opt14_cpu import *
import hashlib
from py65.disassembler import Disassembler
OUT=ROOT/'results/pmg_audit'; OUT.mkdir(exist_ok=True)
rom=(ROOT/'build/buffer_sync.rom').read_bytes()
mem=(ROOT/'analysis/flying-ram.bin').read_bytes()
c=machine(rom,mem); dis=Disassembler(c)
lines=[]
for start,end in ((0x4000,0x8000),(0xa000,0xc000)):
    pc=start
    while pc<end:
        n,s=dis.instruction_at(pc); lines.append(f'{pc:04X} {s}'); pc+=n
(OUT/'linear-listing.txt').write_text('\n'.join(lines))
class Writes(Memory):
    def __init__(self,rom,mem): super().__init__(rom,mem); self.writes=[]; self.at=0
    def __setitem__(self,key,value):
        if isinstance(key,int) and 0x0b00<=key<0x1000: self.writes.append({'pc':self.at,'address':key,'old':self[key],'new':value})
        super().__setitem__(key,value)
def trial(label,entry,setup,x=0):
    data=bytearray(mem)
    for at,val in setup.items(): data[at]=val
    m=Writes(rom,data); cpu=MPU(memory=m); cpu.pc=entry; cpu.x=x; cpu.sp=0xfd; m[0x1fe]=0xfe; m[0x1ff]=0x3f
    steps=0
    while cpu.pc!=0x3fff:
        m.at=cpu.pc; cpu.step(); steps+=1
        assert steps<10000,(label,hex(cpu.pc))
    return {'label':label,'entry':f'{entry:04X}','cycles_cpu_no_dma':cpu.processorCycles,'instructions':steps,'writes':len(m.writes),'changed_writes':sum(w['old']!=w['new'] for w in m.writes),'addresses':[f"{w['address']:04X}" for w in m.writes]}
rows=[]
for old,new in ((20,20),(20,21),(21,20),(0,55),(55,0)):
    setup={0x281a:new,0x2875:old,0x281b:20,0x2876:20}
    setup.update({0xc97+y:0 if y<=old else 255 for y in range(57)})
    rows.append(trial(f'bar {old}->{new}',0xa55c,setup))
rows.append(trial('21-row unchanged',0xa527,{0x291c:0,0x2872:0,0x291d:0,0x2874:0}))
rows.append(trial('21-row changed',0xa527,{0x291c:1,0x2872:0,0x291d:0,0x2874:0}))
rows.append(trial('missile 3-row unchanged',0xa94d,{0xb9:20,0x28da:8}))
rows.append(trial('missile 3-row moved',0xa94d,{0xb9:19,0x28da:8}))
rows.append(trial('init 3x8 rows',0xaa65,{}))
rows.append(trial('5-row shape moved',0xa8de,{0x2846:20,0x2845:21,0x2839:0,0x283a:0}))
rows.append(trial('RAM scaled object, old length 10, scale index 10',0x710d,{0x2865:20,0x2866:10,0x36:4,0x38:64,0x39:10,0x283c:0},x=10))
rows.append(trial('ROM object, masked source',0xa71e,{0x2835:10,0x286f:20,0x2826:255,0x2821:20}))
rows.append(trial('RAM scroll four planes 89 rows',0x4fc2,{}))
(OUT/'cpu-observations.json').write_text(json.dumps({'rom_sha256':hashlib.sha256(rom).hexdigest(),'note':'Synthetic valid inputs, original routines only; CPU cycles exclude DMA and interrupts; no FPS estimate. Initial pixel contents come from historical flight snapshot.','cases':rows},indent=2))
print(json.dumps(rows,indent=2))
