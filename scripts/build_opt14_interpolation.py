"""Exact nibble-contribution interpolation; ROM bank14 plus private SMC RAM."""
from opt14_common import *
from opt14_cpu import machine
from py65.disassembler import Disassembler
import re
rom=bytearray((ROOT/'build/opt14_geometry.rom').read_bytes());template=(ROOT/'tests/fixtures/center-0.bin').read_bytes()
assert rom[0x3eeb:0x3fc2]==template[0x7eeb:0x7fc2]
ram_source='''; Private interpolation helper; called inside VBI. Updated operands are
; fully initialized before each use. DLI does not call this helper.
 opt h-
 org $7eeb
 lda #14
 sta $d500
 jsr $9000
 php
 pha
 lda #2
 sta $d500
 pla
 plp
 rts
 :($7f20-*) dta $ea
mix
 stx value1+1
 tax
high0
 lda $8000,x
 sta sum1+1
 lda $9e00,x
 tax
low0
 lda $8000,x
 clc
sum1
 adc #0
 sta sum2+1
value1
 ldx #0
high1
 lda $8000,x
sum2
 adc #0
 sta sum3+1
 lda $9e00,x
 tax
low1
 lda $8000,x
sum3
 adc #0
 rts
 ert * > $7fc2
 :($7fc2-*) dta $ea
'''
ram_code=assemble('opt14_interpolation_ram',ram_source);assert len(ram_code)==0xd7
labels={}
for line in (ROOT/'build/opt14_interpolation_ram.lst').read_text().splitlines():
 m=re.match(r'^\s*\d+\s+([0-9A-F]{4})\s+(high0|low0|high1|low1|sum1|sum2|sum3|value1)\s*$',line)
 if m:labels[m[2]]=int(m[1],16)
assert len(labels)==8,labels
def contribution(v,f):
 total=0
 for bit in (3,2,1,0):
  if f>>bit&1:total+=(v+1)//2
  v>>=1
 return total
lines=['; Exact four-bit contribution table, 16 aligned pages.',' opt h-',' org $8000']
for f in range(16):
 for lo in range(0,256,16):lines.append(' dta '+','.join(str(contribution(v,f)) for v in range(lo,lo+16)))
lines+=[' ert * <> $9000','entry']
c=machine(bytes(rom),template);dis=Disassembler(c);pc=0x7eeb
while pc<0x7f31:
 n,text=dis.instruction_at(pc);op,mode=c.disassemble[c.memory[pc]]
 if mode=='acc':text=op+' @'
 lines.append(' '+text);pc+=n
lines+=[' ldx $27fd',' jsr configure',' lda $27f0',' ldx $27f1',' jsr $7f20',' sta $27f4',' lda $27f2',' ldx $27f3',' jsr $7f20',' sta $27f5',' ldx $27ff',' jsr configure',' lda $27f4',' ldx $27f5',' jsr $7f20',' sta $62',' ldx $27fd',' lda #0']
for at in (0x27f0,0x27f1,0x27f2,0x27f3,0x27f4,0x27f5,0x27fa,0x27fb):lines.append(f' sta ${at:04x}')
lines+=[' lda $62']
pc=0x7fb1
while pc<0x7fc2:
 n,text=dis.instruction_at(pc);op,mode=c.disassemble[c.memory[pc]]
 if mode=='acc':text=op+' @'
 lines.append(' '+text);pc+=n
lines+=['configure',' txa',' lsr @',' lsr @',' lsr @',' lsr @',' ora #$80',f' sta ${labels["high1"]+2:04x}',' eor #$0f',f' sta ${labels["high0"]+2:04x}',' txa',' and #$0f',' ora #$80',f' sta ${labels["low1"]+2:04x}',' eor #$0f',f' sta ${labels["low0"]+2:04x}',' rts',' ert * > $9e00',' :($9e00-*) dta $ff']
for lo in range(0,256,16):lines.append(' dta '+','.join(str(v>>4) for v in range(lo,lo+16)))
lines+=[' :($9fff-*) dta $ff',' dta 14'];code=assemble('opt14_interpolation_bank14','\n'.join(lines)+'\n');assert len(code)==8192
assert rom[14*8192:15*8192]==b'\xff'*8192;rom[14*8192:15*8192]=code;rom[0x3eeb:0x3fc2]=ram_code
save('opt14_interpolation',rom,base='opt14_geometry',ram_patches=[{'address':0x7eeb,'hex':ram_code.hex()}],smc_labels=labels,bank_entry=0x9000)
