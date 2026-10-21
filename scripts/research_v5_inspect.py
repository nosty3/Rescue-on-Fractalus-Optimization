from cpu_test_support import *
from py65.disassembler import Disassembler
from collections import Counter,defaultdict
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'results/research_v5'
rom=(ROOT/'dist/Rescue on Fractalus! - PAL optimized v5 128KB.rom').read_bytes()
ram=(OUT/'ram-local.bin').read_bytes()
def setup(bank):
 m=list(ram);m[0x8000:0xa000]=rom[bank*8192:(bank+1)*8192];m[0xa000:0xc000]=rom[-8192:];return MPU(memory=m)
lines=[]
for bank,lo,hi in [(2,0x814c,0x8224),(2,0x8309,0x8360),(2,0x85d4,0x88c0),(2,0x9627,0x982a),(2,0x7cd6,0x8000),(2,0x7310,0x74a0)]:
 c=setup(bank);d=Disassembler(c);pc=lo;lines.append(f'BANK {bank} ${lo:04X}-${hi:04X}')
 while pc<hi:
  n,t=d.instruction_at(pc);lines.append(f'{pc:04X}: {t}');pc+=n
(OUT/'inspected-code.txt').write_text('\n'.join(lines))
p=json.loads((OUT/'straight-insns.json').read_text());lines=[]
for r in p['hot'][:150]:
 g=int(r['gaddr'][1:],16);bank=(g>>16)&255 if g>>28==8 else 2;pc=0x8000+(g&8191) if g>>28==8 else g&65535
 c=setup(bank);d=Disassembler(c);n,t=d.instruction_at(pc)
 lines.append(f'{bank if g>>28==8 else "RAM/fixed"}:{pc:04X} {r["insns"]:8} {r["cycles"]:9} {t}')
(OUT/'hot-instructions.txt').write_text('\n'.join(lines));print('\n'.join(lines[:65]))
