"""Compare real-emulator geometry outputs against original CPU for same inputs."""
from opt14_common import *
from opt14_cpu import machine
a=connect();a.bp_clear_all();a.boot(str(ROOT/'build/opt14_geometry.car'));a.frame(2);a.state_load(str(ROOT/'results/flying.altstate2'));a.joy(0,'center')
old=(ROOT/'build/opt14_width45.rom').read_bytes();rows=[]
for i in range(30):
 a.bp_clear_all();a.bp_set(0x835e)
 for attempt in range(100):
  a.frame(100)
  if a.regs()['PC']=='$835e' and a.cart_info()['bank']==2:break
 else:raise AssertionError('entry bank2 not reached')
 regs=a.regs();mem=b''.join(a.peek(j,16384) for j in range(0,65536,16384));c=machine(old,mem);c.pc=0x835e
 for k,key in [('a','A'),('x','X'),('y','Y'),('p','P'),('sp','S')]:setattr(c,k,int(regs[key][1:],16))
 steps=0
 while c.pc!=0x84fd:c.step();steps+=1;assert steps<20000
 a.bp_clear_all();a.bp_set(0x84fd)
 for attempt in range(100):
  a.frame(100)
  if a.regs()['PC']=='$84fd' and a.cart_info()['bank']==2:break
 else:raise AssertionError('exit bank2 not reached')
 after=a.peek(0x2200,0x300);rr=a.regs()
 diff=[hex(j) for j in range(0x22a3,0x24e1) if c.memory[j]!=after[j-0x2200]]
 rd={k:[getattr(c,k),int(rr[key][1:],16)] for k,key in [('a','A'),('x','X'),('y','Y'),('p','P'),('sp','S')] if getattr(c,k)!=int(rr[key][1:],16)}
 row={'i':i,'memory_diff':diff,'register_diff':rd,'table':hex(mem[0x80]+256*mem[0x81])};rows.append(row);print(row,flush=True)
 if diff:break
a.bp_clear_all();(OUT/'geometry-live-probe.json').write_text(json.dumps(rows,indent=2))
assert len(rows)==30 and all(not r['memory_diff'] and not r['register_diff'] for r in rows)
