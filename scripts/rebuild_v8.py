"""Rebuild v8 buffer synchronization fix using only archived sources and MADS."""
import pathlib, subprocess, argparse, hashlib, json, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(); p.add_argument('--mads', required=True); args = p.parse_args()
subprocess.run([sys.executable, str(ROOT/'scripts/rebuild_v7.py'), '--mads', args.mads], check=True)
rom = bytearray((ROOT/'build/v7_clipping.rom').read_bytes())
out = ROOT/'build/buffer_sync.bin'
subprocess.run([args.mads, str(ROOT/'src/buffer_sync.asm'), '-o:'+str(out)], check=True)
code = out.read_bytes(); assert len(code) == 15
assert rom[0x5214:0x5217] == bytes.fromhex('4c2f98')
rom[0x5214:0x5217] = bytes.fromhex('4ca084'); rom[0x44a0:0x44a0+len(code)] = code
digest = hashlib.sha256(rom).hexdigest()
assert digest == '02da0221c95fc8896720a7ca17181bbb1c3c7502dadf62d933d1ba0c341347bd'
stem = 'Rescue on Fractalus! - PAL optimized v8 128KB'
assert rom == (ROOT/f'dist/{stem}.rom').read_bytes()
car = b'CART'+(14).to_bytes(4,'big')+(sum(rom)&0xffffffff).to_bytes(4,'big')+bytes(4)+rom
assert car == (ROOT/f'dist/{stem}.car').read_bytes()
(ROOT/'build/buffer_sync.rom').write_bytes(rom); (ROOT/'build/buffer_sync.car').write_bytes(car)
restored = bytearray((ROOT/'original/Rescue on Fractalus!.rom').read_bytes())
ips = (ROOT/'dist/fractalus-pal-optimized-v8-128KB.ips').read_bytes(); assert ips[:5] == b'PATCH'; i=5
while ips[i:i+3] != b'EOF':
    at=int.from_bytes(ips[i:i+3],'big'); n=int.from_bytes(ips[i+3:i+5],'big'); i+=5; assert n>0
    if at>len(restored): restored.extend(bytes(at-len(restored)))
    restored[at:at+n]=ips[i:i+n]; i+=n
assert restored == rom
(ROOT/'build/reconstruction-v8.json').write_text(json.dumps({'result':'pass','sha256':digest,'rom_bytes':len(rom),'ips_verified':True,'fixtures_required':False},indent=2))
print('v8', digest, 'PASS')
