from session import *
from altirra_bridge._analyzer_tables import OPCODES
import subprocess
rom=(ROOT/'Rescue on Fractalus!.rom').read_bytes()
def decode(mem,pc):
 op=mem[pc]; mn,mode,n=OPCODES.get(op,('???','imp',1));v=mem[pc+1] if n>1 else 0;w=v+(mem[pc+2]<<8) if n==3 else v
 forms={'imp':'','acc':'@','imm':f'#${v:02X}','zp':f'${v:02X}','zpx':f'${v:02X},x','zpy':f'${v:02X},y','abs':f'${w:04X}','abx':f'${w:04X},x','aby':f'${w:04X},y','ind':f'(${w:04X})','izx':f'(${v:02X},x)','izy':f'(${v:02X}),y','rel':f'${(pc+2+(v if v<128 else v-256))&65535:04X}'}
 return mn.lower()+' '+forms[mode],n
mem=bytearray(65536);mem[0xa000:0xc000]=rom[-8192:];mem[0x8000:0xa000]=rom[16384:24576]
comments={0xa32e:'First half: update flight/scene, build image for display list $3210.',0xa333:'Renderer preparation, buffer selector X=$33.',0xa338:'Terrain pipeline stage, buffer selector X=$30.',0xa33d:'Raster/output stage, buffer selector X=$33.',0xa34a:'Publish ready buffer 2 via zero-page $42.',0xa36c:'Second half: same pipeline for display list $316B.',0xa371:'Same renderer, selector X=$03.',0xa376:'Same terrain stage, selector X=$00.',0xa37b:'Same output stage, selector X=$03.',0xa3af:'Publish ready buffer 1 via zero-page $42.',0xa3cd:'Repeat both halves.',0xb4f4:'VBI: skip presentation when flight mode ($4A) is zero.',0xb4f8:'Read ready buffer flag; zero means renderer has not published.',0xb500:'Ready=1: display list $316B.',0xb50c:'Ready=2: display list $3210.',0xb516:'Measurement breakpoint: exactly one hit per buffer presentation.',0xb518:'Acknowledge presentation; clear ready flag.'}
for name,start,end in [('flight_loop',0xa32e,0xa3d0),('present_buffer',0xb4f4,0xb51a)]:
 lines=['; Extracted from supplied 64 KiB ROM; addresses are original CPU addresses.','; Reassemble with MADS; output verified byte-for-byte against fixed ROM bank.',' opt h-',f' org ${start:04X}'];pc=start
 while pc<end:
  if pc in comments:lines.append('; '+comments[pc])
  s,n=decode(mem,pc);lines.append(f' {s:22} ; ${pc:04X}');pc+=n
 (ROOT/f'analysis/{name}.asm').write_text('\n'.join(lines)+'\n')
 p=subprocess.run([str(ROOT/'tools/mads/bin/windows_x86_64/mads.exe'),str(ROOT/f'analysis/{name}.asm'),'-o:'+str(ROOT/f'analysis/{name}.bin')],capture_output=True,text=True)
 print(p.stdout,p.stderr);actual=(ROOT/f'analysis/{name}.bin').read_bytes();assert actual==mem[start:end],(name,len(actual));print(name,'BYTE EXACT',len(actual))
# A raw sequential listing is exploratory: only entry-aligned portions are code evidence.
for name,start,end in [('terrain_bank2',0x8000,0xa000),('fixed_bank7',0xa000,0xc000)]:
 lines=['; Exploratory linear disassembly: includes data; not a complete code/data classification.'];pc=start
 while pc<end-2:
  s,n=decode(mem,pc);lines.append(f'{pc:04X} {mem[pc:pc+n].hex():8} {s}');pc+=n
 (ROOT/f'analysis/{name}.txt').write_text('\n'.join(lines))
