"""Build candidate XEX using Solo's loader and source-level relocation of changed banks."""
import sys,os,dis,json,re,subprocess,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];P=R/'build/up38';O=R/'build/xex';O.mkdir(exist_ok=True)
(O/'xex').mkdir(exist_ok=True)
os.environ['FRACTALUS_WORK']=str(O);assert os.environ.get('FRACTALUS_MADS'), 'Run rebuild_current.py --mads PATH'
sys.path.insert(0,str(R/'tools/up38_audit_deps'));sys.path.insert(0,str(P/'tools'))
import reloc,mkxex
VAR='sentinel_depth_lazy_scan_fill';candidate=(R/'build/Rescue on Fractalus! - optimized 128KB.rom').read_bytes();baseline=(R/'build/up38work/build/final.rom').read_bytes()
assert hashlib.sha256(candidate).hexdigest()=='ec01982121b70baca35f04568617965c3164e716e0a5eb3c6ebcbb123566a868'
dec=json.loads((P/'xex/decisions.json').read_text());ins=reloc.extend(baseline,reloc.instructions(json.loads((P/'work/cov/all.json').read_text())))
# Two six-byte music descriptors begin with resident-code pointers.
# The original coverage-derived decisions omitted these data words.
assert baseline[0x17d3:0x17d5]==bytes.fromhex('fb57')
assert baseline[0x17d9:0x17db]==bytes.fromhex('df57')
dec['word']=dec.get('word',[])+[[0,0x57d3],[0,0x57d9]]
ext,log=reloc.build(baseline,ins,dec)
checks=[]
for bank,name in ((5,'raster5'),(6,'sky_b6'),(8,'sky_b8'),(9,'sky_b9')):
 for tag,src in [('baseline',P/'src'/f'{name}.asm'),('candidate',R/'src/v11'/f'{name}.asm')]:
  raw=src.read_bytes()
  try:s=raw.decode('utf-8')
  except UnicodeDecodeError:s=raw.decode('cp1250')
  s=s.replace('\r\n','\n')
  # All 16-bit constants in these generated banks are addresses or layout bounds.
  s=re.sub(r'\$([0-9a-fA-F]{4})(?![0-9a-fA-F])',lambda m:f'${reloc.M(int(m[1],16)):04x}',s)
  s,n=re.subn(r'(?i)lda #(\d+)\n sta \$d500',lambda m:f'lda #${reloc.portb(int(m[1])):02x}\n sta $d301',s)
  assert '$d500' not in s.lower()
  s,nmark=re.subn(r' dta '+str(bank)+r'\s*$',f' dta ${reloc.portb(bank):02x}\n',s);assert nmark==1
  data,labs=mkxex.mads(s,f'{tag}_{name}');assert len(data)==8192
  if tag=='baseline':
   diffs=[i for i,(a,b) in enumerate(zip(data,ext[bank][:8192])) if a!=b]
   assert all(data[i]==(ext[bank][i]^0xc0) and data[i-2:i]==bytes([0x4c,0]) and ext[bank][i]==0x99 and (bank,0x8000+i-2) not in ins for i in diffs),(bank,[(hex(i+0x8000),data[i],ext[bank][i]) for i in diffs[:30]])
   checks.append(dict(bank=bank,baseline_source_relocation_matches_solo_except_uncovered_jumps=True,additional_relocated_jump_operands=[hex(0x8000+i) for i in diffs]))
  else:ext[bank]=data+ext[bank][8192:]
# Remaining banks must be unchanged in the tested candidate.
for bank in set(range(16))-{5,6,8,9}:assert candidate[bank*8192:(bank+1)*8192]==baseline[bank*8192:(bank+1)*8192]
for bank,data in ext.items():(O/f'bank-{bank:02}.bin').write_bytes(data)
# Reuse the loader verbatim except its user-facing insufficient-memory message.
mkxex.CHECK=mkxex.CHECK.replace(mkxex.MSG,'FRACTALUS CAND NEEDS 320K RAMBO, 576K OR 1MB RAM')
assert len('FRACTALUS CAND NEEDS 320K RAMBO, 576K OR 1MB RAM')==len(mkxex.MSG)
mkxex.load_rom=lambda _:candidate
mkxex.instructions=lambda _:set()
mkxex.extend=lambda rom,ins:set()
mkxex.build=lambda rom,ins,dec:(ext,log)
(O/'cov').mkdir(exist_ok=True);(O/'cov/all.json').write_text('{}')
xex=O/'Rescue on Fractalus! - optimized 320KB-1MB.xex';mkxex.OUT=str(xex);mkxex.main()
(O/'build.json').write_text(json.dumps(dict(candidate_rom_sha256=hashlib.sha256(candidate).hexdigest(),xex_sha256=hashlib.sha256(xex.read_bytes()).hexdigest(),bytes=xex.stat().st_size,checks=checks,loader_source=str(P/'tools/mkxex.py')),indent=2))
print('BUILD VERIFIED',flush=True)
