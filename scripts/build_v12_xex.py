"""Port the six changed source banks onto the verified v11 XEX loader/layout."""
from pathlib import Path
import re,json,hashlib,subprocess,os
R=Path(__file__).resolve().parents[1];O=R/'src/v12'
W=R/'build/v12_xex';W.mkdir(parents=True,exist_ok=True)
MADS=Path(os.environ.get('FRACTALUS_MADS',str(R/'tools/mads/bin/windows_x86_64/mads.exe')))
ROM=R/'build/Rescue on Fractalus! - optimized 128KB.rom'
V11=R/'build'
BASE_XEX=R/'build/xex/Rescue on Fractalus! - optimized 320KB-1MB.xex'
OUT=R/'build/Rescue on Fractalus! - optimized 320KB-1MB.xex'
SOURCES={5:'candidate.asm',9:'sky_b9.asm',**{b:f'geometry_bank{b}.asm' for b in range(10,14)}}

def M(a):return a^0xc000 if 0x4000<=a<0xc000 else a
def portb(n):return 0x83|((n&3)<<2)|((n>>2&3)<<5)

def segments(data):
 i=0
 while i<len(data):
  start=int.from_bytes(data[i:i+2],'little');i+=2
  if start==0xffff:continue
  end=int.from_bytes(data[i:i+2],'little');i+=2
  assert end>=start and i+end-start+1<=len(data)
  yield start,i,end-start+1
  i+=end-start+1
 assert i==len(data)

def assemble(source,stem):
 path=W/(stem+'.asm');path.write_text(source,encoding='utf-8');output=path.with_suffix('.bin')
 p=subprocess.run([str(MADS),str(path),'-o:'+str(output),'-t:'+str(path.with_suffix('.lab'))],capture_output=True,text=True)
 assert p.returncode==0,p.stdout+p.stderr
 data=output.read_bytes();assert len(data)==8192
 return data

def main():
 rom=ROM.read_bytes();assert hashlib.sha256(rom).hexdigest()=='4959a82ab36528a0448a40e6178fdb72d321e5d1e23c258036f5e22e51cfa20e'
 original=(V11/'v11-reference.rom').read_bytes()
 changed=[b for b in range(16) if rom[b*8192:(b+1)*8192]!=original[b*8192:(b+1)*8192]]
 assert changed==list(SOURCES),changed
 raw=BASE_XEX.read_bytes();assert hashlib.sha256(raw).hexdigest()=='ac0c217074d52a4db6163ad94339031e4610e9a99a5c7d02f629c6b34ce9a20b'
 banks={};checks=[]
 for bank,name in SOURCES.items():
  source=(O/name).read_text(encoding='utf-8')
  assert assemble(source,f'car_bank{bank}')==rom[bank*8192:(bank+1)*8192]
  # Four-digit literals in these six sources are addresses or layout bounds.
  source=re.sub(r'\$([0-9a-fA-F]{4})(?![0-9a-fA-F])',lambda m:f'${M(int(m[1],16)):04x}',source)
  source,switches=re.subn(r'(?i)lda #(\d+)\n sta \$d500',lambda m:f'lda #${portb(int(m[1])):02x}\n sta $d301',source)
  assert switches>0 and '$d500' not in source.lower(),bank
  source,nmark=re.subn(r'(?i) dta '+str(bank)+r'\s*$',f' dta ${portb(bank):02x}\n',source);assert nmark==1
  data=assemble(source,f'bank{bank}');assert data[-1]==portb(bank)
  banks[bank]=data
  checks.append(dict(bank=bank,car_source_exact=True,portb_switches=switches,marker=hex(portb(bank)),relocated_sha256=hashlib.sha256(data).hexdigest()))
 result=bytearray(raw);inverse={portb(n):n for n in range(16)};selected=None;patched=[];payloads={}
 for start,offset,size in segments(raw):
  if start==0x0500 and size==1:selected=inverse.get(raw[offset])
  if start==0x4000 and size==16384:
   assert selected is not None
   payloads[selected]=offset
   if selected in banks:result[offset:offset+8192]=banks[selected];patched.append(selected)
 assert sorted(patched)==list(SOURCES)
 # Keep both corrected music descriptors and every loader/fixed-bank byte intact.
 zero=payloads[0]
 assert result[zero+0x17d3:zero+0x17d5]==bytes.fromhex('fb97')
 assert result[zero+0x17d9:zero+0x17db]==bytes.fromhex('df97')
 allowed=set()
 for b in patched:allowed.update(range(payloads[b],payloads[b]+8192))
 assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(raw,result))) and len(raw)==len(result)
 for b,offset in payloads.items():(W/f'ext-bank{b:02}.bin').write_bytes(result[offset:offset+16384])
 OUT.write_bytes(result)
 report=dict(candidate_rom_sha256=hashlib.sha256(rom).hexdigest(),xex_sha256=hashlib.sha256(result).hexdigest(),bytes=len(result),base_v11_xex_sha256=hashlib.sha256(raw).hexdigest(),patched_banks=patched,checks=checks,loader_and_fixed_code_unchanged=True,both_music_descriptors_fixed=True,memory='320 KB Rambo, 576 KB or 1088 KB; BASIC off',relocation='Banked 8000-9FFF -> 4000-5FFF, resident 4000-7FFF -> 8000-BFFF, fixed A000-BFFF -> 6000-7FFF; PORTB banking.')
 (W/'xex-build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

if __name__=='__main__':main()
