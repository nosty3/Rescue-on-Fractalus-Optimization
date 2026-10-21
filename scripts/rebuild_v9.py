"""Rebuild v9 from archived MADS sources, without emulator SDK or fixtures."""
import pathlib,subprocess,argparse,hashlib,json,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--mads',required=True);args=p.parse_args()
subprocess.run([sys.executable,str(ROOT/'scripts/rebuild_v8.py'),'--mads',args.mads],check=True)
rom=bytearray((ROOT/'build/buffer_sync.rom').read_bytes())
for name,offset,size in [('pmg_short_loops',0x43ca,167),('pmg_bar_delta',0x44b0,68)]:
 out=ROOT/f'build/{name}.bin';subprocess.run([args.mads,str(ROOT/f'src/{name}.asm'),'-o:'+str(out)],check=True)
 code=out.read_bytes();assert len(code)==size;rom[offset:offset+size]=code
for at,target in [(0xa54a,0x83ca),(0xa8ea,0x83e9),(0xa91e,0x8402),(0xa965,0x8431),(0xa975,0x8451),(0xa564,0x84b0)]:
 offset=len(rom)-8192+at-0xa000;rom[offset:offset+3]=bytes([0x4c,target&255,target>>8])
rom[len(rom)-8192+0xa547-0xa000]=7
digest=hashlib.sha256(rom).hexdigest();assert digest=='0c8226e1f58ad26b2a103cbf59c4b8b23fdb87caac0e22f2586a83513a859880'
stem='Rescue on Fractalus! - PAL optimized v9 128KB';assert rom==(ROOT/f'dist/{stem}.rom').read_bytes()
car=b'CART'+(14).to_bytes(4,'big')+(sum(rom)&0xffffffff).to_bytes(4,'big')+bytes(4)+rom;assert car==(ROOT/f'dist/{stem}.car').read_bytes()
(ROOT/'build/pmg_trial.rom').write_bytes(rom);(ROOT/'build/pmg_trial.car').write_bytes(car)
restored=bytearray((ROOT/'original/Rescue on Fractalus!.rom').read_bytes());ips=(ROOT/'dist/fractalus-pal-optimized-v9-128KB.ips').read_bytes();assert ips[:5]==b'PATCH';i=5
while ips[i:i+3]!=b'EOF':
 at=int.from_bytes(ips[i:i+3],'big');n=int.from_bytes(ips[i+3:i+5],'big');i+=5;assert n>0
 if at>len(restored):restored.extend(bytes(at-len(restored)))
 restored[at:at+n]=ips[i:i+n];i+=n
assert restored==rom
(ROOT/'build/reconstruction-v9.json').write_text(json.dumps({'result':'pass','sha256':digest,'rom_bytes':len(rom),'ips_verified':True,'fixtures_required':False},indent=2));print('v9',digest,'PASS')
