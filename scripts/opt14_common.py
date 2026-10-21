from session import *
import subprocess,hashlib
OUT=ROOT/'results/opt14';OUT.mkdir(exist_ok=True)
MADS=ROOT/'tools/mads/bin/windows_x86_64/mads.exe'
def assemble(name,source):
 p=ROOT/f'src/{name}.asm';p.write_text(source,encoding='utf-8');b=ROOT/f'build/{name}.bin'
 r=subprocess.run([str(MADS),str(p),'-o:'+str(b),'-l:'+str(ROOT/f'build/{name}.lst')],capture_output=True,text=True)
 assert r.returncode==0,r.stdout+r.stderr
 return b.read_bytes()
def save(name,rom,**meta):
 rom=bytes(rom);(ROOT/f'build/{name}.rom').write_bytes(rom)
 (ROOT/f'build/{name}.car').write_bytes(b'CART'+(14).to_bytes(4,'big')+(sum(rom)&0xffffffff).to_bytes(4,'big')+bytes(4)+rom)
 data={'variant':name,'sha256':hashlib.sha256(rom).hexdigest(),**meta};(OUT/f'{name}-build.json').write_text(json.dumps(data,indent=2));print(data,flush=True)
def patch_state(a,name):
 p=OUT/f'{name}-build.json'
 if p.exists():
  for r in json.loads(p.read_text()).get('ram_patches',[]):
   code=bytes.fromhex(r['hex']);a.memload(r['address'],code);assert a.peek(r['address'],len(code))==code
