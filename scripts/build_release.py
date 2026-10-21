"""Reproducible MADS build of the selected, verified patches. Never edits input ROM."""
from session import *
import hashlib,subprocess
original=(ROOT/'Rescue on Fractalus!.rom').read_bytes()
expected='1eb18e2a1ff31f43871a5e4e21e73f61b7659177d33d2cdbb29f36530b9f4d68'
assert hashlib.sha256(original).hexdigest()==expected,'Unexpected input ROM'
rom=bytearray(original);records=[]
def patch(cpu,data,description):
 offset=0x4000+cpu-0x8000
 assert 0x4000<=offset and offset+len(data)<=0x6000
 before=bytes(rom[offset:offset+len(data)])
 rom[offset:offset+len(data)]=data
 records.append({'cpu_address':f'${cpu:04X}','rom_offset':f'${offset:04X}','bytes':len(data),'description':description,'before':before.hex(),'after':data.hex()})
def assemble(source):
 target=ROOT/f'build/{source}.bin'
 p=subprocess.run([str(ROOT/'tools/mads/bin/windows_x86_64/mads.exe'),str(ROOT/f'src/{source}.asm'),'-o:'+str(target),'-l:'+str(ROOT/f'build/{source}.lst')],capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return target.read_bytes()
code=assemble('division_fast');assert len(code)<=0x8309-0x8224
patch(0x8224,code,'Exact fractional division; high remainder in A')
assert original[0x5937:0x593a]==bytes.fromhex('8a8682')
patch(0x9937,assemble('raster_order'),'STX/TXA reorder; same state at common loop entry')
for pc in [0x9a18,0x9a36,0x9a52]:
 off=0x4000+pc-0x8000;assert original[off:off+3]==bytes.fromhex('4c3399')
 patch(pc,bytes.fromhex('4c3999'),'Subdivision: skip unchanged-X bound test and redundant STX')
scan=assemble('fill_final');assert len(scan)<=958
assert original[0x5c42:0x5c42+len(scan)]==b'\xff'*len(scan)
patch(0x9c42,scan,'First-row fast path and exact four-row scan in unused bank padding')
assert original[0x5308:0x530b]==bytes.fromhex('8aa8a9')
assert original[0x5623:0x5626]==bytes.fromhex('4c0e93')
patch(0x9308,bytes.fromhex('4c429c'),'Fill subroutine entry')
patch(0x9623,bytes.fromhex('4c489c'),'Next fill column')
previous=ROOT/'build/release.rom'
if previous.exists():assert previous.read_bytes()==rom,'Build differs from tested release'
previous.write_bytes(rom)
dist=ROOT/'dist';dist.mkdir(exist_ok=True)
name='Rescue on Fractalus! - PAL optimized.rom'
(dist/name).write_bytes(rom)
# Standard IPS patch: contiguous runs of changed bytes.
ips=bytearray(b'PATCH');pos=0
while pos<len(rom):
 if rom[pos]==original[pos]:pos+=1;continue
 start=pos
 while pos<len(rom) and rom[pos]!=original[pos] and pos-start<65535:pos+=1
 ips+=start.to_bytes(3,'big')+(pos-start).to_bytes(2,'big')+rom[start:pos]
ips+=b'EOF';(dist/'fractalus-pal-optimized.ips').write_bytes(ips)
# Independently apply the patch and compare against the built ROM.
check=bytearray(original);i=5
while ips[i:i+3]!=b'EOF':
 at=int.from_bytes(ips[i:i+3],'big');n=int.from_bytes(ips[i+3:i+5],'big');assert n>0;i+=5;check[at:at+n]=ips[i:i+n];i+=n
assert check==rom
manifest={'input_sha256':expected,'output_sha256':hashlib.sha256(rom).hexdigest(),'rom_bytes':len(rom),'changed_bytes':sum(a!=b for a,b in zip(original,rom)),'patches':records,'ips_verified':True}
(dist/'build-manifest.json').write_text(json.dumps(manifest,indent=2))
print('Release built and IPS verified:',name);print(manifest['output_sha256'],manifest['changed_bytes'],'changed bytes')
