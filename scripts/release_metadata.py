"""Write and independently apply an IPS patch; never modify the original ROM."""
from pathlib import Path
import hashlib,json
def sha(data):return hashlib.sha256(data).hexdigest()
def ips_make(original,rom):
 padded=original+bytes(max(0,len(rom)-len(original)));out=bytearray(b'PATCH');i=0
 while i<len(rom):
  if padded[i]==rom[i]:i+=1;continue
  start=i
  while i<len(rom) and padded[i]!=rom[i] and i-start<65535:i+=1
  out+=start.to_bytes(3,'big')+(i-start).to_bytes(2,'big')+rom[start:i]
 out+=b'EOF';restored=bytearray(original);i=5
 while out[i:i+3]!=b'EOF':
  at=int.from_bytes(out[i:i+3],'big');n=int.from_bytes(out[i+3:i+5],'big');i+=5;assert n
  if at+n>len(restored):restored.extend(bytes(at+n-len(restored)))
  restored[at:at+n]=out[i:i+n];i+=n
 assert restored==rom
 return bytes(out)
def distribution(root,version,stem,manifest_name='build-manifest.json',patch_name='fractalus-optimized-128KB.ips'):
 root=Path(root);folder=root/'optimized version';rom=(folder/(stem+'.rom')).read_bytes();car=(folder/(stem+'.car')).read_bytes();assert car[16:]==rom
 original=(root/'original/Rescue on Fractalus!.rom').read_bytes();patch=ips_make(original,rom);(root/'dist'/patch_name).write_bytes(patch)
 data=dict(version=version,original_sha256=sha(original),rom_sha256=sha(rom),car_sha256=sha(car),rom_bytes=len(rom),cartridge_type=int.from_bytes(car[4:8],'big'),ips_verified=True,ips_sha256=sha(patch))
 (root/'dist'/manifest_name).write_text(json.dumps(data,indent=2),encoding='utf-8');return data
