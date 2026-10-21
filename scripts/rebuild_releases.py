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
 (BUILD/(name+'.rom')).write_bytes(rom)
 car=b'CART'+(13).to_bytes(4,'big')+(sum(rom)&0xffffffff).to_bytes(4,'big')+bytes(4)+rom
 (BUILD/(name+'.car')).write_bytes(car)
 print(version,sha(rom),'PASS',flush=True)
original=(ROOT/'Rescue on Fractalus!.rom').read_bytes()
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
(BUILD/'lowlevel_sound.rom').write_bytes(rom)
code=assemble('lowlevel_sound_flag');assert len(code)<=0xbb3e-0xbb1c
patch(rom,0xfb1c,code)
patch(rom,0xf9a7,bytes.fromhex('201cbb'),bytes.fromhex('20a4bc'))
patch(rom,0xf9ad,bytes.fromhex('4c2bb9'),bytes.fromhex('4c26b9'))
save('v3',rom,'lowlevel_sound_flag')
report={v:EXPECTED[v] for v in ('v1','v2','v3')}
for version,suffix in [('v1',''),('v2',' v2'),('v3',' v3')]:
 distributed=(ROOT/'dist'/('Rescue on Fractalus! - PAL optimized'+suffix+'.rom')).read_bytes()
 assert sha(distributed)==EXPECTED[version]
 patchname='fractalus-pal-optimized'+('' if version=='v1' else '-'+version)+'.ips'
 ips=(ROOT/'dist'/patchname).read_bytes();assert ips.startswith(b'PATCH')
 restored=bytearray(original);i=5
 while ips[i:i+3]!=b'EOF':
  at=int.from_bytes(ips[i:i+3],'big');n=int.from_bytes(ips[i+3:i+5],'big');i+=5
  assert n>0
  restored[at:at+n]=ips[i:i+n];i+=n
 assert restored==distributed
report.update(result='pass',ips_verified=True,fixtures_required=False,emulator_required=False)
(BUILD/'reconstruction.json').write_text(json.dumps(report,indent=2))
print('All released ROM hashes and IPS patches verified.')
