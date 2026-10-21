"""Inline geometry tails, specialize destinations and hoist frame-invariant shift."""
from opt14_common import *
from opt14_cpu import machine
from py65.disassembler import Disassembler
import re
rom=bytearray((ROOT/'dist/Rescue on Fractalus! - PAL optimized v6 128KB.rom').read_bytes())
original=(ROOT/'build/opt14_width45.rom').read_bytes();c=machine(original,[0]*65536);dis=Disassembler(c)
for bank in range(10,14):
 old=(ROOT/f'src/opt14_geometry_bank{bank}.asm').read_text();prefix=old[old.index('point_0'):old.index(' cpy #45')];chunks=re.split(r'point_(\d+)\n',prefix)[1:]
 lines=['; v7 candidate: full tail specialization, exact arithmetic, 9F saved/restored.',' opt h-',' org $8000','entry',' lda $9f',' pha',' sec',' lda #0',' sbc $8b',' lsr @',' lsr @',' lsr @',' sta $9f',' ldy #0']
 for k in range(0,len(chunks),2):
  y=int(chunks[k]);body=chunks[k+1].split(' jsr point_tail')[0]
  # Reserve bank-switch landing pads; a whole point stays on one side.
  lines+=[' ift * > $97b0 .and * < $9900',' jmp $9900',' :($9893-*) dta $ff',' jmp entry',' :($98e0-*) dta $ff',' php',' pha',' lda #2',' sta $d500',' :($9900-*) dta $ff',' eif',f'point_{y}',body]
  lines+=[' sec',' lda #0',' sbc $8b',' txa',' and #15',' ora $b6',' tax',f' stx ${0x2276+y:04x}',' lda $0900,x',f' sta ${0x23b5+y:04x}',' sbc $8c',' tax',f' bcs positive_{y}',' lda high_table,x',' ora #$f0',f' bne high_done_{y}',f'positive_{y}',' lda high_table,x',f'high_done_{y}',f' sta ${0x2388+y:04x}',' lda $9f',' lsr @',' ora low_table,x',' sta $b5',f' sta ${0x235b+y:04x}',f' ldx ${0x2276+y:04x}']
  if y>=33:
   lines += [f' ldy #{y}',' jsr classify']
   continue
  pc=0x84a7
  while pc<0x84f5:
   n,text=dis.instruction_at(pc);op,mode=c.disassemble[c.memory[pc]];lines.append(f'p{y}_{pc:04x}')
   if mode=='rel' or op=='JMP':text=f'{op} p{y}_{int(text.split("$")[1],16):04x}'
   elif mode=='aby':text=f'{op} ${c.memory[pc+1]+256*c.memory[pc+2]+y:04x}'
   lines.append(' '+text);pc+=n
 # Preserve final A/X and flags: original finishes with Y=45, CPY #45.
 lines+=[' tay',' pla',' sta $9f',' tya',' ldy #45',' cpy #45',' jmp $98e0','classify']
 pc=0x84a7
 while pc<0x84f5:
  n,text=dis.instruction_at(pc);op,mode=c.disassemble[c.memory[pc]];lines.append(f'c_{pc:04x}')
  if mode=='rel' or op=='JMP':text=f'{op} c_{int(text.split("$")[1],16):04x}'
  lines.append(' '+text);pc+=n
 lines+=[' rts','code_end',' ert * > $9d00',' :($9d00-*) dta $ff','high_table']
 for lo in range(0,256,16):lines.append(' dta '+','.join(str(v>>4) for v in range(lo,lo+16)))
 lines+=['low_table']
 for lo in range(0,256,16):lines.append(' dta '+','.join(str((v<<4)&255) for v in range(lo,lo+16)))
 lines+=[' :($9fff-*) dta $ff',f' dta {bank}']
 code=assemble(f'v7_geometry_bank{bank}','\n'.join(lines)+'\n');assert len(code)==8192
 assert code[0x1893:0x1896]==bytes.fromhex('4c0080') and code[0x18e0:0x18e7]==bytes.fromhex('0848a9028d00d5')
 rom[bank*8192:(bank+1)*8192]=code
meta=json.loads((ROOT/'results/opt14/opt14_interpolation-build.json').read_text())
save('v7_geometry',rom,base='v6',ram_patches=meta['ram_patches'])
