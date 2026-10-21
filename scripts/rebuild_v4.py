"""Reconstruct v1-v4 without emulator states, SDK or py65."""
import pathlib,subprocess,argparse,hashlib,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--mads',required=True);args=p.parse_args()
import sys
subprocess.run([sys.executable,str(ROOT/'scripts/rebuild_releases.py'),'--mads',args.mads],check=True)
base=(ROOT/'build/lowlevel_sound_flag.rom').read_bytes();rom=bytearray(base+b'\xff'*65536);rom[-8192:]=base[-8192:]
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
digest=hashlib.sha256(rom).hexdigest()
assert digest=='268a401d9bb0cfdffa627adec73ef79b901c7d08813cefa4426eba24ce8713f2'
assert rom==(ROOT/'dist/Rescue on Fractalus! - PAL optimized v4 128KB.rom').read_bytes()
(ROOT/'build/clear128.rom').write_bytes(rom)
(ROOT/'build/clear128.car').write_bytes(b'CART'+(14).to_bytes(4,'big')+(sum(rom)&0xffffffff).to_bytes(4,'big')+bytes(4)+rom)
original=(ROOT/'original/Rescue on Fractalus!.rom').read_bytes();restored=bytearray(original)
ips=(ROOT/'dist/fractalus-pal-optimized-v4-128KB.ips').read_bytes();assert ips[:5]==b'PATCH';i=5
while ips[i:i+3]!=b'EOF':
 at=int.from_bytes(ips[i:i+3],'big');n=int.from_bytes(ips[i+3:i+5],'big');i+=5;assert n>0
 if at>len(restored):restored.extend(bytes(at-len(restored)))
 restored[at:at+n]=ips[i:i+n];i+=n
assert restored==rom
(ROOT/'build/reconstruction-v4.json').write_text(json.dumps({'result':'pass','sha256':digest,'rom_bytes':len(rom),'ips_verified':True,'fixtures_required':False},indent=2))
print('v4',digest,'PASS')
