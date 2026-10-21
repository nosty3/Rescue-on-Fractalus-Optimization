"""Add bank-6 interpolation; RAM wrapper preserves return flags/registers."""
from session import *
import subprocess,hashlib
rom=bytearray((ROOT/'build/lowlevel_sound.rom').read_bytes())
template=(ROOT/'tests/fixtures/center-0.bin').read_bytes()
assert rom[0x3eeb:0x3fc2]==template[0x7eeb:0x7fc2]
assert rom[0xc000:0xe000]==b'\xff'*8192
def assemble(name,source):
 src=ROOT/f'src/{name}.asm';src.write_text(source)
 out=ROOT/f'build/{name}.bin'
 subprocess.run([str(ROOT/'tools/mads/bin/windows_x86_64/mads.exe'),str(src),'-o:'+str(out)],check=True)
 return out.read_bytes()
code=assemble('lowlevel_interpolation',(ROOT/'src/audit_interpolation.asm').read_text().replace('org $c000','org $8000').replace('; Audit prototype in test-only address space; no distributed ROM edit.','; Bank 6 exact interpolation.'))
rom[0xc000:0xc000+len(code)]=code;rom[0xdfff]=6
wrapper=assemble('lowlevel_interpolation_entry','''; Called from flight logic while bank 2 is selected.
 opt h-
 org $7eeb
 lda #6
 sta $d500
 jsr $8000
 php
 pha
 lda #2
 sta $d500
 pla
 plp
 rts
''')
rom[0x3eeb:0x3eeb+len(wrapper)]=wrapper
# Flight VBI must restore both extension banks (5 and 6); bank 2 marker is FF.
assert rom[0xffea:0xfff1]==bytes.fromhex('68c905f002a902')
rom[0xffeb:0xffef]=bytes.fromhex('c9079002')
path=ROOT/'build/lowlevel_full.rom';path.write_bytes(rom)
(ROOT/'results/lowlevel/full-build.json').write_text(json.dumps({'sha256':hashlib.sha256(rom).hexdigest(),'ram_patch_address':0x7eeb,'ram_patch_hex':wrapper.hex(),'interpolation_bytes':len(code)},indent=2))
print(path)
