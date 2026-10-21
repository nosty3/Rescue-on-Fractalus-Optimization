from cpu_test_support import *
from py65.disassembler import Disassembler
rom=(ROOT/'Rescue on Fractalus!.rom').read_bytes();mem=(ROOT/'tests/fixtures/center-0.bin').read_bytes();p=json.loads((ROOT/'analysis/optimization/insns.json').read_text())
out=[]
for r in p['hot']:
 g=int(r['gaddr'][1:],16)
 if g>>28==8:
  bank=(g>>16)&255
  if bank!=2:continue
  pc=0x8000+(g&8191);c=cpu(rom,mem);location='bank2'
 elif g>>24==0:
  pc=g&65535;c=cpu(rom,mem);location='fixed' if pc>=0xa000 else 'RAM'
 else:continue
 if pc>=0xc000:continue
 d=Disassembler(c);n,t=d.instruction_at(pc);op,mode=c.disassemble[c.memory[pc]]
 reason=None
 if op=='JSR' and c.memory[pc+3]==0x60:reason='tail call: JSR/RTS -> JMP, nominal 9 cycles'
 if op in ('LDA','LDX','LDY','AND','ORA','EOR','TAX','TAY','TXA','TYA') and c.memory[pc+n:pc+n+2] in ([0xc9,0],[0xe0,0],[0xc0,0]):reason='compare zero: check register match and carry liveness'
 if op in ('LDA','LDX','LDY') and mode in ('abs','abx','aby'):
  operand=c.memory[pc+1]+256*c.memory[pc+2]
  if operand<256:reason='absolute access to zero page: check legal indexed mode'
 if reason:
  lines=[];q=pc
  for _ in range(7):
   z,s=d.instruction_at(q);lines.append(f'{q:04X} {s}');q+=z
  out.append({'where':location,'pc':f'{pc:04X}','count_old_profile':r['insns'],'reason':reason,'code':lines})
dest=ROOT/'analysis/lowlevel';dest.mkdir(exist_ok=True)
(dest/'candidates.json').write_text(json.dumps(out,indent=2))
for x in out:
 if not (x['where']=='bank2' and int(x['pc'],16)>=0x982a):print(x)
