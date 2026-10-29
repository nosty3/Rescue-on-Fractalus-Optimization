"""Rebuild v13 cartridges and the 512 KB XEX from source."""
from pathlib import Path
import argparse,subprocess,sys,os,json,hashlib
from release_metadata import ips_make
R=Path(__file__).resolve().parents[1];B=R/'build';B.mkdir(exist_ok=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--mads',required=True);args=p.parse_args();mads=str(Path(args.mads).resolve())
 env=os.environ.copy();env.update(PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',FRACTALUS_MADS=mads)
 call=lambda cmd:subprocess.run(cmd,cwd=R,env=env,check=True)
 call([sys.executable,str(R/'scripts/rebuild_v12_stage.py'),'--mads',mads])
 call([sys.executable,str(R/'src/v13/trees.py'),'build'])
 call([sys.executable,str(R/'src/v13/xex.py')])
 expected=json.loads((R/'src/v13/expected.json').read_text(encoding='utf-8'));checks=[]
 for kb in (512,1024):
  stem=f'Rescue on Fractalus! - optimized {kb}KB';data=(B/f'v13/Rescue on Fractalus! - optimized v13 {kb}KB.rom').read_bytes();assert hashlib.sha256(data).hexdigest()==expected[str(kb)]
  for ext in ('rom','car'):
   built=B/f'v13/Rescue on Fractalus! - optimized v13 {kb}KB.{ext}';assert built.read_bytes()==(R/f'optimized version/{stem}.{ext}').read_bytes()
  patch=ips_make((R/'original/Rescue on Fractalus!.rom').read_bytes(),data);assert patch==(R/f'dist/fractalus-optimized-{kb}KB.ips').read_bytes();checks.append(dict(kb=kb,rom_sha256=expected[str(kb)],rom_car_and_ips_equal=True))
 built=B/'v13/Rescue on Fractalus! - optimized v13 512KB - 1MB RAM.xex';xex=built.read_bytes();assert hashlib.sha256(xex).hexdigest()==expected['xex'];assert xex==(R/'optimized version/Rescue on Fractalus! - optimized 512KB - 1MB RAM.xex').read_bytes()
 (B/'reconstruction.json').write_text(json.dumps(dict(version='v13',result='pass',checks=checks,xex_sha256=expected['xex'],xex_equal=True),indent=2),encoding='utf-8')
 print('v13 ROM/CAR/XEX/IPS rebuilt and verified byte-for-byte')
if __name__=='__main__':main()
