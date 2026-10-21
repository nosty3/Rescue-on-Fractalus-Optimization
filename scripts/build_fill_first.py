"""Specialize first fill iteration and simplify pointer-carry loop layout."""
from session import *
import hashlib,subprocess
base=(ROOT/'dist/Rescue on Fractalus! - PAL optimized v4 128KB.rom').read_bytes();rom=bytearray(base)
assert hashlib.sha256(base).hexdigest()=='268a401d9bb0cfdffa627adec73ef79b901c7d08813cefa4426eba24ce8713f2'
source='''; Bank 2 free raster space. Exact live RAM/register behavior.
 opt h-
 org $9863
 lda $073d,x
 sta $80
 lda $0793,x
 sta $81
 lda #0
 sta $95
 lda #$55
 sta $96
; First iteration: ($byte & 0) | $55 | table3B[$byte].
 lda ($80),y
 tax
 lda $3b00,x
 ora #$55
 sta ($80),y
 lda $3a00,x
 and #$55
 beq column_end
update_mask
 sta $96
 tax
 lda $3a00,x
 sta $95
 clc
 lda $80
 adc #$60
 sta $80
 bcc loop
 inc $81
; Carry path falls through, replacing the original BCS.
loop
 lda ($80),y
 tax
 and $95
 ora $96
 ora $3b00,x
 sta ($80),y
 lda $3a00,x
 and $96
 bne update_mask
column_end
 iny
 dec $9f
 beq done
 jmp $9c48
done
 rts
 ert * > $98f0
'''
src=ROOT/'src/fill_first.asm';src.write_text(source);out=ROOT/'build/fill_first.bin'
subprocess.run([str(ROOT/'tools/mads/bin/windows_x86_64/mads.exe'),str(src),'-o:'+str(out)],check=True)
code=out.read_bytes();rom[0x5863:0x5863+len(code)]=code
# Both old entry points remain valid, including the fallthrough from sky fill.
assert base[0x55e1:0x55e7]==bytes.fromhex('eaeaeabd3d07')
rom[0x55e1:0x55e7]=bytes.fromhex('4c63984c6398')
(ROOT/'build/fill_first.rom').write_bytes(rom)
(ROOT/'build/fill_first.car').write_bytes(b'CART'+(14).to_bytes(4,'big')+(sum(rom)&0xffffffff).to_bytes(4,'big')+bytes(4)+rom)
dest=ROOT/'results/fill_first';dest.mkdir(exist_ok=True)
(dest/'build.json').write_text(json.dumps({'sha256':hashlib.sha256(rom).hexdigest(),'helper_bytes':len(code),'address':0x9863,'bank':2},indent=2));print('Built',len(code),hashlib.sha256(rom).hexdigest())
