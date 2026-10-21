"""Compile four constant command streams into banked straight-line code."""
from opt14_common import *
from opt14_cpu import machine
from py65.disassembler import Disassembler
import argparse
p=argparse.ArgumentParser();p.add_argument('--base',default='opt14_width45');args=p.parse_args();rom=bytearray((ROOT/f'build/{args.base}.rom').read_bytes());original=bytes(rom)
c=machine(original,[0]*65536);dis=Disassembler(c)
dispatch=assemble('opt14_geometry_entry','''; Reuse the obsolete bank-2 raster body; preserve clear fallback.
 opt h-
 org $9863
 lda $80
 cmp #$55
 beq bank10
 cmp #$82
 beq bank11
 cmp #$af
 beq bank12
 lda #13
 jmp switch
bank10
 lda #10
 jmp switch
bank11
 lda #11
 jmp switch
bank12
 lda #12
 jmp switch
 ert * > $9890
 :($9890-*) dta $ff
switch
 sta $d500
''')
assert original[0x435e:0x4361]==bytes.fromhex('a000b1');rom[0x435e:0x4361]=bytes.fromhex('4c6398');rom[0x5863:0x5863+len(dispatch)]=dispatch
rom[0x58e7:0x58ec]=bytes.fromhex('68284cfd84')
stats=[]
for index,table in enumerate((0x9a55,0x9a82,0x9aaf,0x9adc)):
 bank=10+index;assert original[bank*8192:(bank+1)*8192]==b'\xff'*8192
 lines=['; Generated constant command stream; only original command selection is removed.',' opt h-',' org $8000','entry',' ldy #0'];prefix_bytes=0
 for y in range(45):
  # Discover the path controlled only by this immutable command byte.
  sim=machine(original,[0]*65536);sim.pc=0x8360;sim.y=y;sim.memory[0x80]=table&255;sim.memory[0x81]=table>>8;visited=[]
  while sim.pc!=0x8467:
   at=sim.pc;visited.append(at);sim.step();assert len(visited)<100
  lines.append(f'point_{y}')
  for at in visited:
   n,text=dis.instruction_at(at);op,mode=c.disassemble[c.memory[at]]
   if at in (0x8360,0x8362) or mode=='rel' or op=='JMP' or (op=='ROL' and c.memory[at+1]==0xb5):continue
   if mode=='aby':addr=c.memory[at+1]+256*c.memory[at+2]+y;text=f'{op} ${addr:04x}'
   if mode=='acc':text=op+' @'
   lines.append(' '+text)
  lines+=[' jsr point_tail',' iny']
 lines+=[' cpy #45',' jmp $98e0',' ert * > $9300',' :($9300-*) dta $ff','point_tail']
 pc=0x8467
 while pc<0x84f5:
  n,text=dis.instruction_at(pc);op,mode=c.disassemble[c.memory[pc]];lines.append(f't_{pc:04x}')
  if mode=='rel' or op=='JMP':text=f'{op} t_{int(text.split("$")[1],16):04x}'
  if mode=='acc':text=op+' @'
  lines.append(' '+text);pc+=n
 lines+=[' rts',' ert * > $9893',' :($9893-*) dta $ff',' jmp entry',' :($98e0-*) dta $ff',' php',' pha',' lda #2',' sta $d500',' ert * <> $98e7',' :($9fff-*) dta $ff',f' dta {bank}']
 code=assemble(f'opt14_geometry_bank{bank}','\n'.join(lines)+'\n');assert len(code)==8192;rom[bank*8192:(bank+1)*8192]=code
 stats.append({'bank':bank,'command_table':hex(table)})
assert rom[0x1ffeb:0x1ffef]==bytes.fromhex('c90a9002');rom[0x1ffec]=15
save('opt14_geometry',rom,base=args.base,banks=stats,bank_entry=0x9893)
