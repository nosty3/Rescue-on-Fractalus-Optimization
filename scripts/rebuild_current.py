"""Rebuild v14 from original through the v11 source stage and Solo up74."""
from pathlib import Path
import sys,os,subprocess,shutil,argparse,json,hashlib
R=Path(__file__).resolve().parents[1];B=R/'build';B.mkdir(exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('--mads',required=True);a=p.parse_args()
mads=str(Path(a.mads).resolve());env=os.environ.copy();env['FRACTALUS_MADS']=mads
subprocess.run([sys.executable,str(R/'scripts/rebuild_v11_stage.py'),'--mads',mads],cwd=R,env=env,check=True)
P=B/'up74';shutil.copytree(R/'src/up74',P,dirs_exist_ok=True)
W=B/'up74work';(W/'base').mkdir(parents=True,exist_ok=True)
shutil.copy2(B/'Rescue on Fractalus! - optimized 128KB.rom',W/'base/v11.rom')
env['FRACTALUS_WORK']=str(W)
subprocess.run([sys.executable,str(P/'tools/build.py'),'--name=v14','v11src','vbi2_mul','vbi2_sound','vbi2_interp','scene_grid','scene_pre','reorder','proj2','loop2'],cwd=R,env=env,check=True)
for ext in ('rom','car'):
 data=(W/f'build/v14.{ext}').read_bytes();assert data==(R/f'optimized version/Rescue on Fractalus! - optimized 128KB.{ext}').read_bytes()
rom=(W/'build/v14.rom').read_bytes();out=bytearray((R/'original/Rescue on Fractalus!.rom').read_bytes());patch=(R/'dist/fractalus-optimized-128KB.ips').read_bytes();i=5
assert patch[:5]==b'PATCH'
while patch[i:i+3]!=b'EOF':
 at=int.from_bytes(patch[i:i+3],'big');n=int.from_bytes(patch[i+3:i+5],'big');i+=5;assert n
 if len(out)<at+n:out.extend(bytes(at+n-len(out)))
 out[at:at+n]=patch[i:i+n];i+=n
assert out==rom
(B/'reconstruction.json').write_text(json.dumps(dict(version='v14',rom_car_equal=True,ips_verified=True,sha256=hashlib.sha256(rom).hexdigest()),indent=2))
print('v14 ROM/CAR and original-to-v14 IPS verified')
