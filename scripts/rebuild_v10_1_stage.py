"""Offline reconstruction from checked-in MADS sources; no emulator/fixtures."""
import argparse, pathlib, subprocess, hashlib, json
ROOT=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--mads',required=True,help='Path to MADS executable')
args=parser.parse_args()
BUILD=ROOT/'build';BUILD.mkdir(exist_ok=True)
sha=lambda data:hashlib.sha256(data).hexdigest()
EXPECTED={
 'original':'1eb18e2a1ff31f43871a5e4e21e73f61b7659177d33d2cdbb29f36530b9f4d68',
 'v1':'b2b7e2ad244eb4a127b31640f5e621efc9fc6502805e2f00c6d65871baf13d72',
 'v2':'fd374e06d8a5ef28a97069408e14d52e8ab9e188706751ec243600447f11a4d0',
 'v3':'0e34b5d240ae8613a8b8331d186474978e1ff6cead532688ab70cc8a872d5503'}
def assemble(name):
 out=BUILD/(name+'.bin')
 subprocess.run([args.mads,str(ROOT/'src'/(name+'.asm')),'-o:'+str(out)],check=True)
 return out.read_bytes()
def patch(rom,offset,data,expected=None):
 assert 0<=offset and offset+len(data)<=len(rom)
 if expected is not None:assert bytes(rom[offset:offset+len(expected)])==expected
 rom[offset:offset+len(data)]=data
def save(version,rom,name):
 assert len(rom)==65536 and sha(rom)==EXPECTED[version],(version,sha(rom))
 print('Verified intermediate stage',version,flush=True)
original=(ROOT/'original/Rescue on Fractalus!.rom').read_bytes()
assert sha(original)==EXPECTED['original']
rom=bytearray(original)
code=assemble('division_fast');assert len(code)<=0x8309-0x8224
patch(rom,0x4224,code)
patch(rom,0x5937,assemble('raster_order'),bytes.fromhex('8a8682'))
for at in (0x5a18,0x5a36,0x5a52):patch(rom,at,bytes.fromhex('4c3999'),bytes.fromhex('4c3399'))
code=assemble('fill_final');assert len(code)<=958
patch(rom,0x5c42,code,b'\xff'*len(code))
patch(rom,0x5308,bytes.fromhex('4c429c'),bytes.fromhex('8aa8a9'))
patch(rom,0x5623,bytes.fromhex('4c489c'),bytes.fromhex('4c0e93'))
save('v1',rom,'release');v1=bytes(rom)
code=assemble('mountain_cull');assert len(code)<=8192
patch(rom,0xa000,code,b'\xff'*len(code))
patch(rom,0xb907,v1[0x5907:0x6000])
patch(rom,0x582a,bytes.fromhex('a9058d00d5'))
patch(rom,0x5907,bytes.fromhex('682860'))
guard=assemble('mountain_vbi');assert len(guard)<=32
patch(rom,0xffda,guard,b'\xff'*len(guard))
patch(rom,0xf46c,bytes.fromhex('4cdabfea'),bytes.fromhex('a90085c7'))
for at in (0xf4ef,0xf737):patch(rom,at,bytes.fromhex('4ceabf'),bytes.fromhex('4c62e4'))
rom[0xbfff]=5
save('v2',rom,'mountain_cull')
address=0x9d3b
for entry,kind in [(0xbb19,'minimum'),(0xbb3e,'maximum')]:
 code=assemble('lowlevel_sound_'+kind);assert address+len(code)<=0x9fff
 patch(rom,0x4000+address-0x8000,code,b'\xff'*len(code))
 patch(rom,0xe000+entry-0xa000,bytes([0x4c,address&255,address>>8]))
 address+=len(code)
code=assemble('lowlevel_sound_flag');assert len(code)<=0xbb3e-0xbb1c
patch(rom,0xfb1c,code)
patch(rom,0xf9a7,bytes.fromhex('201cbb'),bytes.fromhex('20a4bc'))
patch(rom,0xf9ad,bytes.fromhex('4c2bb9'),bytes.fromhex('4c26b9'))
save('v3',rom,'lowlevel_sound_flag')

# Direct bitmap clearing and 128 KB layout
base=bytes(rom);rom=bytearray(base+b'\xff'*65536);rom[-8192:]=base[-8192:]
def assemble(name):
 out=ROOT/f'build/{name}.bin'
 subprocess.run([args.mads,str(ROOT/f'src/{name}.asm'),'-o:'+str(out)],check=True)
 return out.read_bytes()
wrapper=assemble('clear128_entry');rom[0x582f:0x582f+len(wrapper)]=wrapper
assert rom[0x5214:0x5217]==bytes.fromhex('8694a0')
rom[0x5214:0x5217]=bytes.fromhex('4c2f98');rom[0x58f7:0x58fa]=bytes.fromhex('682860')
for bank in (6,8):
 code=assemble(f'clear128_bank{bank}');assert len(code)==8192
 assert rom[bank*8192:(bank+1)*8192]==b'\xff'*8192
 rom[bank*8192:(bank+1)*8192]=code
assert rom[0x1ffea:0x1fff1]==bytes.fromhex('68c905f002a902')
rom[0x1ffeb:0x1ffef]=bytes.fromhex('c9099002')

# Specialized bitmap filling
out=ROOT/'build/fill_rows.bin'
subprocess.run([args.mads,str(ROOT/'src/fill_rows.asm'),'-o:'+str(out)],check=True)
code=out.read_bytes();assert len(code)==8192 and rom[9*8192:10*8192]==b'\xff'*8192
rom[9*8192:10*8192]=code
assert rom[0x5308:0x530b]==bytes.fromhex('4c429c')
rom[0x5308:0x530d]=bytes.fromhex('a9098d00d5')
assert rom[0x5ff7:0x5ffa]==b'\xff'*3
rom[0x5ff7:0x5ffa]=bytes.fromhex('682860')
assert rom[0x1ffeb:0x1ffef]==bytes.fromhex('c9099002')
rom[0x1ffec]=10

# Division, terrain widths, geometry and RAM interpolation
def asm(name):
 out=ROOT/f'build/{name}.bin'
 subprocess.run([args.mads,str(ROOT/f'src/{name}.asm'),'-o:'+str(out)],check=True)
 return out.read_bytes()
assert rom[0x4224:0x4229]==bytes.fromhex('8a484c3182')
code=asm('opt14_division');assert len(code)==5;rom[0x4224:0x4229]=code
code=asm('opt14_width45');assert len(code)==8192;rom[5*8192:6*8192]=code
assert rom[0x435e:0x4361]==bytes.fromhex('a000b1');rom[0x435e:0x4361]=bytes.fromhex('4c6398')
code=asm('opt14_geometry_entry');rom[0x5863:0x5863+len(code)]=code;rom[0x58e7:0x58ec]=bytes.fromhex('68284cfd84')
for bank in range(10,15):
 name=f'opt14_geometry_bank{bank}' if bank<14 else 'opt14_interpolation_bank14'
 assert rom[bank*8192:(bank+1)*8192]==b'\xff'*8192
 code=asm(name);assert len(code)==8192;rom[bank*8192:(bank+1)*8192]=code
assert rom[0x1ffeb:0x1ffef]==bytes.fromhex('c90a9002');rom[0x1ffec]=15
code=asm('opt14_interpolation_ram');assert len(code)==215;rom[0x3eeb:0x3fc2]=code

# Geometry tail and clipping
def asm(name):
 out=ROOT/f'build/{name}.bin';subprocess.run([args.mads,str(ROOT/f'src/{name}.asm'),'-o:'+str(out)],check=True);return out.read_bytes()
for bank in range(10,14):
 code=asm(f'v7_geometry_bank{bank}');assert len(code)==8192;rom[bank*8192:(bank+1)*8192]=code
assert rom[0x563d:0x5640]==bytes.fromhex('a58330');rom[0x563d:0x5640]=bytes.fromhex('4c8083')
code=asm('v7_clipping');rom[0x4380:0x4380+len(code)]=code

# Buffer ownership synchronization
out = ROOT/'build/buffer_sync.bin'
subprocess.run([args.mads, str(ROOT/'src/buffer_sync.asm'), '-o:'+str(out)], check=True)
code = out.read_bytes(); assert len(code) == 15
assert rom[0x5214:0x5217] == bytes.fromhex('4c2f98')
rom[0x5214:0x5217] = bytes.fromhex('4ca084'); rom[0x44a0:0x44a0+len(code)] = code

# PMG updates
for name,offset,size in [('pmg_short_loops',0x43ca,167),('pmg_bar_delta',0x44b0,68)]:
 out=ROOT/f'build/{name}.bin';subprocess.run([args.mads,str(ROOT/f'src/{name}.asm'),'-o:'+str(out)],check=True)
 code=out.read_bytes();assert len(code)==size;rom[offset:offset+size]=code
for at,target in [(0xa54a,0x83ca),(0xa8ea,0x83e9),(0xa91e,0x8402),(0xa965,0x8431),(0xa975,0x8451),(0xa564,0x84b0)]:
 offset=len(rom)-8192+at-0xa000;rom[offset:offset+3]=bytes([0x4c,target&255,target>>8])
rom[len(rom)-8192+0xa547-0xa000]=7

digest=sha(rom)
assert digest=='0c8226e1f58ad26b2a103cbf59c4b8b23fdb87caac0e22f2586a83513a859880',digest
# Preserve a reproducible historical control in ignored build/.
reference=bytes(rom)
(BUILD/'reference-v9.car').write_bytes(b'CART'+(14).to_bytes(4,'big')+(sum(reference)&0xffffffff).to_bytes(4,'big')+bytes(4)+reference)
code=asm('v10_plotter');assert len(code)==8192;rom[5*8192:6*8192]=code
digest=sha(rom)
assert digest=='fde2166f28d768514a933a76654c9c3f9a583d4cdac182ed08aa14d15761bc37'
# Keep the exact measured v10 available only as an ignored research artifact.
(BUILD/'reference-v10.car').write_bytes(b'CART'+(14).to_bytes(4,'big')+(sum(rom)&0xffffffff).to_bytes(4,'big')+bytes(4)+rom)
code=asm('pause_resume_stack');assert code==bytes.fromhex('a009')
assert rom[0x1eb1d:0x1eb1f]==bytes.fromhex('a008')
rom[0x1eb1d:0x1eb1f]=code
digest=sha(rom)
assert digest=='afa04d6802a03333516936b4912f8f7abf23a1837362ac2b0ceaa83b6b6414da'
(BUILD/'reference-v10.1.rom').write_bytes(rom)
print('Verified v10.1 intermediate stage',digest)
