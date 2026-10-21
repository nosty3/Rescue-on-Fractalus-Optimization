"""Reconstruct v1-v5 without emulator states, SDK or py65."""
import pathlib,subprocess,argparse,hashlib,json,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--mads',required=True);args=p.parse_args()
subprocess.run([sys.executable,str(ROOT/'scripts/rebuild_v4.py'),'--mads',args.mads],check=True)
rom=bytearray((ROOT/'build/clear128.rom').read_bytes())
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
digest=hashlib.sha256(rom).hexdigest()
assert digest=='9a6445651455d011008238ab5038e4186badc9e4b7a84a2881b6ab2e02d0d5ef'
assert rom==(ROOT/'dist/Rescue on Fractalus! - PAL optimized v5 128KB.rom').read_bytes()
car=b'CART'+(14).to_bytes(4,'big')+(sum(rom)&0xffffffff).to_bytes(4,'big')+bytes(4)+rom
assert car==(ROOT/'dist/Rescue on Fractalus! - PAL optimized v5 128KB.car').read_bytes()
(ROOT/'build/fill_rows.rom').write_bytes(rom);(ROOT/'build/fill_rows.car').write_bytes(car)
restored=bytearray((ROOT/'original/Rescue on Fractalus!.rom').read_bytes())
ips=(ROOT/'dist/fractalus-pal-optimized-v5-128KB.ips').read_bytes();assert ips[:5]==b'PATCH';i=5
while ips[i:i+3]!=b'EOF':
 at=int.from_bytes(ips[i:i+3],'big');n=int.from_bytes(ips[i+3:i+5],'big');i+=5;assert n>0
 if at>len(restored):restored.extend(bytes(at-len(restored)))
 restored[at:at+n]=ips[i:i+n];i+=n
assert restored==rom
(ROOT/'build/reconstruction-v5.json').write_text(json.dumps({'result':'pass','sha256':digest,'rom_bytes':len(rom),'ips_verified':True,'fixtures_required':False},indent=2))
print('v5',digest,'PASS')
