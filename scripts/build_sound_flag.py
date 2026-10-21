"""Build ablations with lazy event-flag clearing, without running tests."""
from session import *
import subprocess
out=ROOT/'build/lowlevel_sound_flag.bin'
subprocess.run([str(ROOT/'tools/mads/bin/windows_x86_64/mads.exe'),str(ROOT/'src/lowlevel_sound_flag.asm'),'-o:'+str(out)],check=True)
code=out.read_bytes();assert len(code)<=0xbb3e-0xbb1c
for source,dest in [('lowlevel_sound','lowlevel_sound_flag'),('lowlevel_full','lowlevel_flag')]:
 rom=bytearray((ROOT/f'build/{source}.rom').read_bytes())
 assert rom[0xf9a7:0xf9aa]==bytes.fromhex('20a4bc')
 assert rom[0xf9ad:0xf9b0]==bytes.fromhex('4c26b9')
 rom[0xfb1c:0xfb1c+len(code)]=code
 rom[0xf9a7:0xf9aa]=bytes.fromhex('201cbb');rom[0xf9ad:0xf9b0]=bytes.fromhex('4c2bb9')
 (ROOT/f'build/{dest}.rom').write_bytes(rom)
 print(dest)
