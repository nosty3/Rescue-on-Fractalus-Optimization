"""Reconstruct v1-v6 from archived source with MADS, without SDK or states."""
import pathlib,subprocess,argparse,hashlib,json,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--mads',required=True);args=p.parse_args()
subprocess.run([sys.executable,str(ROOT/'scripts/rebuild_v5.py'),'--mads',args.mads],check=True)
rom=bytearray((ROOT/'build/fill_rows.rom').read_bytes())
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
digest=hashlib.sha256(rom).hexdigest();assert digest=='cc2a6a1001d4471431bd03b37a496cfd3b1088baf457ed5403b79b0d58767f21'
stem='Rescue on Fractalus! - PAL optimized v6 128KB'
assert rom==(ROOT/f'dist/{stem}.rom').read_bytes()
car=b'CART'+(14).to_bytes(4,'big')+(sum(rom)&0xffffffff).to_bytes(4,'big')+bytes(4)+rom
assert car==(ROOT/f'dist/{stem}.car').read_bytes()
(ROOT/'build/opt14_interpolation.rom').write_bytes(rom);(ROOT/'build/opt14_interpolation.car').write_bytes(car)
restored=bytearray((ROOT/'original/Rescue on Fractalus!.rom').read_bytes());ips=(ROOT/'dist/fractalus-pal-optimized-v6-128KB.ips').read_bytes();assert ips[:5]==b'PATCH';i=5
while ips[i:i+3]!=b'EOF':
 at=int.from_bytes(ips[i:i+3],'big');n=int.from_bytes(ips[i+3:i+5],'big');i+=5;assert n>0
 if at>len(restored):restored.extend(bytes(at-len(restored)))
 restored[at:at+n]=ips[i:i+n];i+=n
assert restored==rom
(ROOT/'build/reconstruction-v6.json').write_text(json.dumps({'result':'pass','sha256':digest,'rom_bytes':len(rom),'ips_verified':True,'fixtures_required':False},indent=2))
print('v6',digest,'PASS')
