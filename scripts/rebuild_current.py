"""Rebuild v12 from the original ROM and checked-in MADS sources."""
from pathlib import Path
import argparse,subprocess,sys,os,hashlib,json
from release_metadata import ips_make
R=Path(__file__).resolve().parents[1];B=R/'build';B.mkdir(exist_ok=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--mads',required=True);args=p.parse_args();mads=str(Path(args.mads).resolve())
 env=os.environ.copy();env.update(PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',FRACTALUS_MADS=mads)
 call=lambda cmd:subprocess.run(cmd,cwd=R,env=env,check=True)
 call([sys.executable,str(R/'scripts/rebuild_v11_stage.py'),'--mads',mads])
 rom=bytearray((B/'v11-reference.rom').read_bytes())
 for bank,name in {5:'candidate',9:'sky_b9',**{b:f'geometry_bank{b}' for b in range(10,14)}}.items():
  out=B/f'v12_{name}.bin';call([mads,str(R/f'src/v12/{name}.asm'),'-o:'+str(out)]);data=out.read_bytes();assert len(data)==8192;rom[bank*8192:(bank+1)*8192]=data
 assert hashlib.sha256(rom).hexdigest()=='4959a82ab36528a0448a40e6178fdb72d321e5d1e23c258036f5e22e51cfa20e'
 stem='Rescue on Fractalus! - optimized 128KB';car=b'CART'+(14).to_bytes(4,'big')+(sum(rom)&0xffffffff).to_bytes(4,'big')+bytes(4)+rom
 for ext,data in [('rom',rom),('car',car)]:
  (B/f'{stem}.{ext}').write_bytes(data);assert data==(R/f'optimized version/{stem}.{ext}').read_bytes()
 call([sys.executable,str(R/'scripts/build_v12_xex.py')])
 xex=(B/'Rescue on Fractalus! - optimized 320KB-1MB.xex').read_bytes();assert hashlib.sha256(xex).hexdigest()=='7e8fea0ffad7df5ecc3c6bc4fad33352f4903e184f7a5b969124f9e36b833bc8'
 assert xex==(R/'optimized version/Rescue on Fractalus! - optimized 320KB-1MB.xex').read_bytes()
 patch=ips_make((R/'original/Rescue on Fractalus!.rom').read_bytes(),rom);assert patch==(R/'dist/fractalus-optimized-128KB.ips').read_bytes()
 (B/'reconstruction.json').write_text(json.dumps(dict(version='v12',result='pass',rom_sha256=hashlib.sha256(rom).hexdigest(),xex_sha256=hashlib.sha256(xex).hexdigest(),ips_verified=True),indent=2),encoding='utf-8')
 print('v12 ROM/CAR/XEX/IPS rebuilt and verified byte-for-byte')
if __name__=='__main__':main()
