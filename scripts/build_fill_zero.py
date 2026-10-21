"""Skip redundant mask computations for zero input bytes in the fill loop."""
from session import *
import subprocess,hashlib
rom=bytearray((ROOT/'dist/Rescue on Fractalus! - PAL optimized v4 128KB.rom').read_bytes())
assert hashlib.sha256(rom).hexdigest()=='268a401d9bb0cfdffa627adec73ef79b901c7d08813cefa4426eba24ce8713f2'
source='''; Bank 2 free old-raster area, after the v4 clear bank-switch instruction.
; Invariant: $96 != 0 and $95 = table3A[$96]. table3A[0]=FF, table3B[0]=0.
; Zero data writes $96, keeps both masks and must continue to the next row.
; X is dead until the next nonzero byte loads it, including the terminating row.
 opt h-
 org $9863
 lda ($80),y
 bne nonzero
 lda $96
 sta ($80),y
 jmp $9611
nonzero
 tax
 jmp $95f9
 ert * > $98f0
'''
src=ROOT/'src/fill_zero.asm';src.write_text(source)
out=ROOT/'build/fill_zero.bin'
subprocess.run([str(ROOT/'tools/mads/bin/windows_x86_64/mads.exe'),str(src),'-o:'+str(out)],check=True)
code=out.read_bytes();rom[0x5863:0x5863+len(code)]=code
assert rom[0x55f6:0x55f9]==bytes.fromhex('b180aa')
rom[0x55f6:0x55f9]=bytes.fromhex('4c6398')
(ROOT/'build/fill_zero.rom').write_bytes(rom)
(ROOT/'build/fill_zero.car').write_bytes(b'CART'+(14).to_bytes(4,'big')+(sum(rom)&0xffffffff).to_bytes(4,'big')+bytes(4)+rom)
dest=ROOT/'results/fill_zero';dest.mkdir(exist_ok=True)
(dest/'build.json').write_text(json.dumps({'sha256':hashlib.sha256(rom).hexdigest(),'helper_bytes':len(code),'bank':2,'address':0x9863},indent=2))
print('Built',hashlib.sha256(rom).hexdigest(),len(code))
