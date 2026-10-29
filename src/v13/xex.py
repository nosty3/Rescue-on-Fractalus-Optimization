"""Relocate the 512 KB v13 cartridge into 62 extended 16 KB RAM pages."""
from pathlib import Path
import json,re,hashlib,subprocess,os
R=Path(__file__).resolve().parents[2];O=R/'build/v13';W=O/'xex-work';W.mkdir(parents=True,exist_ok=True)
MADS=Path(os.environ.get('FRACTALUS_MADS',str(R/'tools/mads/bin/windows_x86_64/mads.exe')))
BASE=R/'build/v12-reference.xex'
ROM=O/'Rescue on Fractalus! - optimized v13 512KB.rom'
OUT=O/'Rescue on Fractalus! - optimized v13 512KB - 1MB RAM.xex'
def M(a):return a^0xc000 if 0x4000<=a<0xc000 else a
def portb(n):
 assert 0<=n<64
 return (0x83|((n&3)<<2)|(((n>>2)&3)<<5))^((n>>4&1)<<1)^((n>>5&1)<<7)
def segments(data):
 rows=[];i=0
 while i<len(data):
  a=int.from_bytes(data[i:i+2],'little');i+=2
  if a==65535:continue
  end=int.from_bytes(data[i:i+2],'little');i+=2;n=end-a+1;assert n>0 and i+n<=len(data);rows.append((a,data[i:i+n]));i+=n
 assert i==len(data);return rows
def assemble(source,name,bank=False):
 p=W/(name+'.asm');out=p.with_suffix('.bin');p.write_text(source,encoding='utf-8');r=subprocess.run([str(MADS),str(p),'-o:'+str(out)],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 data=out.read_bytes()
 if bank:assert len(data)==8192
 return data
def relocate(source):
 source=re.sub(r'\$([0-9a-fA-F]{4})(?![0-9a-fA-F])',lambda m:f'${M(int(m[1],16)):04x}',source)
 source=re.sub(r'(?i)lda #(\d+)\n sta \$d500',lambda m:f'lda #${portb(int(m[1])):02x}\n sta $d301',source)
 return source
def main():
 raw=BASE.read_bytes();assert hashlib.sha256(raw).hexdigest()=='7e8fea0ffad7df5ecc3c6bc4fad33352f4903e184f7a5b969124f9e36b833bc8'
 rom=ROM.read_bytes();assert len(rom)==524288;meta=json.loads((O/'manifest-512.json').read_text());assert hashlib.sha256(rom).hexdigest()==meta['sha256']
 seg=segments(raw);inverse={portb(n):n for n in range(16)};pages={};order=[];selected=None
 for addr,data in seg:
  if addr==0x0500 and len(data)==1:selected=inverse.get(data[0])
  if addr==0x4000 and len(data)==16384:assert selected is not None;pages[selected]=bytearray(data);order.append(selected)
 fixed=bytearray(pages[0][8192:]);assert fixed[0x1feb:0x1fef]==bytes.fromhex('c980b002');fixed[0x1feb:0x1fef]=bytes.fromhex('c901b002')
 # A zero marker means bank 2; all 64 valid PORTB values are nonzero.
 for n in pages:
  if n!=7:pages[n][8192:]=fixed
 p=pages[2];p[0x1400:0x1500]=bytes(portb(n) if n else 0 for n in rom[0x5400:0x5500])
 selector=(O/'selector.asm').read_text(encoding='utf-8');selector=relocate(selector);selector=selector.replace(' lda #5\n jmp $5e50',f' lda #${portb(5):02x}\n jmp $5e50')
 code=assemble(selector,'selector');p[0x1c42:0x1c42+len(code)]=code;p[0x182a:0x182d]=bytes.fromhex('4c425c');p[0x1858:0x185b]=bytes.fromhex('8d01d3');p[0x1e50:0x1e53]=bytes.fromhex('8d01d3')
 assert pages[5][0x1e53:0x1e56]==b'\xff'*3;pages[5][0x1e53:0x1e56]=pages[5][0x182f:0x1832]
 checks=[]
 for n in range(16,16+meta['used_extra_banks']):
  paths=list((O/'workers').glob(f'*-b{n:03}.asm'));assert len(paths)==1,(n,paths)
  source=paths[0].read_text(encoding='utf-8');car=assemble(source,f'car-bank{n}',True);assert car==rom[n*8192:(n+1)*8192]
  source=relocate(source);source,k=re.subn(r' dta '+str(n)+r'\s*$',f' dta ${portb(n):02x}\n',source);assert k==1 and '$d500' not in source.lower()
  payload=assemble(source,f'bank{n}',True);assert payload[-1]==portb(n);pages[n]=bytearray(payload+fixed);order.append(n);checks.append(dict(bank=n,portb=portb(n),source_matches_car=True))
 # Same selector/check entry addresses as the existing loader; broader memory test.
 check=f''' opt h-
 org $0500
sel dta $ff
select lda sel
 sta $d301
 rts
check
 lda #$ff
 sta $d301
 ldx #63
write_bank
 lda table,x
 sta $d301
 txa
 sta $4000
 lda #$a5
 sta $4001
 dex
 bpl write_bank
 ldx #63
read_bank
 lda table,x
 sta $d301
 cpx $4000
 bne bad
 lda $4001
 cmp #$a5
 bne bad
 dex
 bpl read_bank
 lda #$ff
 sta $d301
 rts
bad
 lda #$ff
 sta $d301
 ldy #message_end-message-1
show_message
 lda message,y
 sta ($58),y
 dey
 bpl show_message
 jmp *
table
 dta {','.join(f'${portb(n):02x}' for n in range(64))}
message dta d'FRACTALUS V13 NEEDS 1MB RAM (1088K TOTAL)'
message_end
 ert * > $0600
'''
 chk=assemble(check,'loader-check');assert seg[1]==(0x02e2,bytes.fromhex('0805'))
 result=[(0x0500,chk),seg[1]]
 for n in order:result += [(0x0500,bytes([portb(n)])),(0x02e2,bytes.fromhex('0105')),(0x4000,bytes(pages[n]))]
 suffix=next(i for i,(a,d) in enumerate(seg) if a==0x8000 and len(d)==8192)-2;assert seg[suffix]==(0x0500,b'\xff');result+=seg[suffix:]
 out=bytearray(b'\xff\xff')
 for a,data in result:out+=a.to_bytes(2,'little')+(a+len(data)-1).to_bytes(2,'little')+data
 OUT.write_bytes(out)
 for n,data in pages.items():(W/f'ext-bank{n:02}.bin').write_bytes(data)
 report=dict(version='v13',rom_sha256=hashlib.sha256(rom).hexdigest(),xex_sha256=hashlib.sha256(out).hexdigest(),bytes=len(out),ram_pages=len(pages),ram_required_kb=1088,portb_bits=[1,2,3,5,6,7],os_rom_bit0_always_one=True,basic_and_selftest_disabled_before_banking=True,vbi_guard='Nonzero PORTB marker valid, zero marker falls back to bank2',base_loader_tail_unchanged=True,music_pointers_fixed=True,workers=checks)
 (O/'xex-build.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='workers'},indent=2))
if __name__=='__main__':main()
