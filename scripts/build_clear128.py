"""Exact absolute-store bitmap clearing in two XEGS 128 KiB extension banks."""
from session import *
import subprocess,hashlib
OUT=ROOT/'results/clear128';OUT.mkdir(exist_ok=True)
base=(ROOT/'dist/Rescue on Fractalus! - PAL optimized v3.rom').read_bytes()
assert hashlib.sha256(base).hexdigest()=='0e34b5d240ae8613a8b8331d186474978e1ff6cead532688ab70cc8a872d5503'
rom=bytearray(base+b'\xff'*65536);rom[-8192:]=base[-8192:]
def save(name,data,carttype):
 (ROOT/f'build/{name}.rom').write_bytes(data)
 (ROOT/f'build/{name}.car').write_bytes(b'CART'+carttype.to_bytes(4,'big')+(sum(data)&0xffffffff).to_bytes(4,'big')+bytes(4)+data)
save('clear_baseline64',base,13);save('clear_baseline128',rom,14)
def assemble(name,lines):
 src=ROOT/f'src/{name}.asm';src.write_text('\n'.join(lines)+'\n')
 out=ROOT/f'build/{name}.bin'
 subprocess.run([str(ROOT/'tools/mads/bin/windows_x86_64/mads.exe'),str(src),'-o:'+str(out)],check=True)
 return out.read_bytes()
wrapper=assemble('clear128_entry',['; Bank 2 trampoline; preserve incoming carry/overflow.',' opt h-',' org $982f',' php',' cpx #3',' beq first',' cpx #51',' beq second',' plp',' stx $94',' ldy #42',' lda #0',' jmp $921a','first',' lda #6',' jmp switch','second',' lda #8',' jmp switch',' :($9860-*) dta $ff','switch',' sta $d500',' ert * <> $9863'])
assert base[0x5214:0x5217]==bytes.fromhex('8694a0')
rom[0x5214:0x5217]=bytes.fromhex('4c2f98')
rom[0x582f:0x582f+len(wrapper)]=wrapper
rom[0x58f7:0x58fa]=bytes.fromhex('682860')
tail=[]
for at in range(0x52a7,0x5307,3):
 assert base[at]==0x9d
 tail.append(base[at+1]+256*base[at+2])
sizes=[]
for bank,x in [(6,3),(8,51)]:
 lines=['; Exact stores for one hidden bitmap buffer.',' opt h-',' org $8000',' stx $94',' ldy #0',' lda #0']
 for column in range(42):
  for row in range(44):lines.append(f' sta ${0x1010+row*96+x+column:04x}')
 lines += [f' sta ${addr+x:04x}' for addr in tail]
 lines += [' ldx $94',' jmp $98f0','code_end',' ert * > $9863',' :($9863-*) dta $ff',' plp',' jmp $8000',' :($98f0-*) dta $ff',' php',' pha',' lda #2',' sta $d500',' ert * <> $98f7',' :($9fff-*) dta $ff',f' dta {bank}']
 code=assemble(f'clear128_bank{bank}',lines);assert len(code)==8192
 assert rom[bank*8192:(bank+1)*8192]==b'\xff'*8192
 rom[bank*8192:(bank+1)*8192]=code;sizes.append({'bank':bank,'buffer_x':x,'stores':42*44+len(tail)})
# Existing VBI always selects bank 2, then restores foreground from marker.
# FF means bank 2; active extension markers are 5, 6, 8.
assert rom[0x1ffea:0x1fff1]==bytes.fromhex('68c905f002a902')
rom[0x1ffeb:0x1ffef]=bytes.fromhex('c9099002')
save('clear128',rom,14)
(OUT/'build.json').write_text(json.dumps({'sha256':hashlib.sha256(rom).hexdigest(),'rom_bytes':len(rom),'cart_type':14,'variants':sizes},indent=2))
print('Built clear128',hashlib.sha256(rom).hexdigest())
