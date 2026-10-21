"""Rebuild released v7 from MADS sources, without SDK or fixture files."""
import pathlib,subprocess,argparse,hashlib,json,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--mads',required=True);args=p.parse_args()
subprocess.run([sys.executable,str(ROOT/'scripts/rebuild_v6.py'),'--mads',args.mads],check=True)
rom=bytearray((ROOT/'build/opt14_interpolation.rom').read_bytes())
def asm(name):
 out=ROOT/f'build/{name}.bin';subprocess.run([args.mads,str(ROOT/f'src/{name}.asm'),'-o:'+str(out)],check=True);return out.read_bytes()
for bank in range(10,14):
 code=asm(f'v7_geometry_bank{bank}');assert len(code)==8192;rom[bank*8192:(bank+1)*8192]=code
assert rom[0x563d:0x5640]==bytes.fromhex('a58330');rom[0x563d:0x5640]=bytes.fromhex('4c8083')
code=asm('v7_clipping');rom[0x4380:0x4380+len(code)]=code
digest=hashlib.sha256(rom).hexdigest();assert digest=='104503c1be0ce8ab9fff7238122559dd2f537c101052ed0128e213b8ecc36da9'
stem='Rescue on Fractalus! - PAL optimized v7 128KB';assert rom==(ROOT/f'dist/{stem}.rom').read_bytes()
car=b'CART'+(14).to_bytes(4,'big')+(sum(rom)&0xffffffff).to_bytes(4,'big')+bytes(4)+rom;assert car==(ROOT/f'dist/{stem}.car').read_bytes()
(ROOT/'build/v7_clipping.rom').write_bytes(rom);(ROOT/'build/v7_clipping.car').write_bytes(car)
restored=bytearray((ROOT/'original/Rescue on Fractalus!.rom').read_bytes());ips=(ROOT/'dist/fractalus-pal-optimized-v7-128KB.ips').read_bytes();assert ips[:5]==b'PATCH';i=5
while ips[i:i+3]!=b'EOF':
 at=int.from_bytes(ips[i:i+3],'big');n=int.from_bytes(ips[i+3:i+5],'big');i+=5;assert n>0
 if at>len(restored):restored.extend(bytes(at-len(restored)))
 restored[at:at+n]=ips[i:i+n];i+=n
assert restored==rom
(ROOT/'build/reconstruction-v7.json').write_text(json.dumps({'result':'pass','sha256':digest,'rom_bytes':len(rom),'ips_verified':True,'fixtures_required':False},indent=2));print('v7',digest,'PASS')
