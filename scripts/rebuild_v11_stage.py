"""Rebuild v11 ROM/CAR/XEX from original ROM and checked-in assembly sources."""
from pathlib import Path
import argparse,sys,os,subprocess,shutil,hashlib,json
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];B=R/'build';B.mkdir(exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('--mads',required=True);args=p.parse_args();mads=str(Path(args.mads).resolve())
env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',FRACTALUS_MADS=mads,FRACTALUS_WORK=str(B/'up38work'))
def call(cmd):subprocess.run(cmd,check=True,cwd=R,env=env)
call([sys.executable,str(R/'scripts/rebuild_v10_1_stage.py'),'--mads',mads])
# Generators write sources; run them in ignored build/, keeping the archive untouched.
P=B/'up38';shutil.copytree(R/'arc/up38',P,dirs_exist_ok=True)
runner=B/'build_up38_stage.py';runner.write_text("import sys\nfrom pathlib import Path\nR=Path(__file__).resolve().parents[1]\nsys.path.insert(0,str(R/'build/up38/tools'))\nimport build as b\nb.BASE=str(R/'build/reference-v10.1.rom')\nb.build([b.PATCHES[n] for n in ('wait_beam','sky','vbi_sound_idle','vbi_gauge','proj_loop')],'final')\n")
call([sys.executable,str(runner)])
base=(B/'up38work/build/final.rom').read_bytes();assert hashlib.sha256(base).hexdigest()=='6087e9b314368b95e7885f5634c88a506bbc61d7a4c988db345e7373377253da'
rom=bytearray(base)
for bank,name in ((5,'raster5'),(6,'sky_b6'),(8,'sky_b8'),(9,'sky_b9')):
 out=B/f'v11_{name}.bin';call([mads,str(R/f'src/v11/{name}.asm'),'-o:'+str(out)]);code=out.read_bytes();assert len(code)==8192;rom[bank*8192:(bank+1)*8192]=code
assert hashlib.sha256(rom).hexdigest()=='ec01982121b70baca35f04568617965c3164e716e0a5eb3c6ebcbb123566a868'
stem='Rescue on Fractalus! - optimized 128KB'
for ext,data in [('rom',rom),('car',b'CART'+(14).to_bytes(4,'big')+(sum(rom)&0xffffffff).to_bytes(4,'big')+bytes(4)+rom)]:
 (B/f'{stem}.{ext}').write_bytes(data)
(B/'v11-reference.rom').write_bytes(rom)
call([sys.executable,str(R/'scripts/build_v11_xex.py')])
print('Verified v11 intermediate ROM and fixed XEX')
