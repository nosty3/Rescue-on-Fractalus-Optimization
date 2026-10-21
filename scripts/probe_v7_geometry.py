"""Actual emulator, four explicitly selected command streams, same-input CPU oracle."""
from opt14_common import *
from opt14_cpu import machine
a=connect();a.bp_clear_all();a.boot(str(ROOT/'build/v7_geometry.car'));a.frame(2);a.state_load(str(ROOT/'results/flying.altstate2'));patch_state(a,'v7_geometry');a.joy(0,'center')
old=(ROOT/'build/opt14_interpolation.rom').read_bytes();rows=[]
def reach(pc):
 a.bp_clear_all();a.bp_set(pc)
 for _ in range(200):
  a.frame(100)
  if a.regs()['PC']==f'${pc:04x}' and a.cart_info()['bank']==2:return
 raise AssertionError(hex(pc))
for i in range(40):
 reach(0x835e);table=(0x9a55,0x9a82,0x9aaf,0x9adc)[i%4];a.memload(0x80,bytes([table&255,table>>8]));regs=a.regs();mem=b''.join(a.peek(j,16384) for j in range(0,65536,16384));c=machine(old,mem);c.pc=0x835e
 for k,key in [('a','A'),('x','X'),('y','Y'),('p','P'),('sp','S')]:setattr(c,k,int(regs[key][1:],16))
 steps=0
 while c.pc!=0x84fd or c.memory.bank!=2:c.step();steps+=1;assert steps<20000
 reach(0x84fd);after=a.peek(0x2200,0x300);rr=a.regs()
 diff=[hex(j) for j in range(0x2276,0x24e1) if c.memory[j]!=after[j-0x2200]]
 rd={k:[getattr(c,k),int(rr[key][1:],16)] for k,key in [('a','A'),('x','X'),('y','Y'),('p','P'),('sp','S')] if getattr(c,k)!=int(rr[key][1:],16)}
 assert not diff and not rd and a.peek(0x9f,1)[0]==mem[0x9f],(i,diff,rd)
 rows.append({'i':i,'table':hex(table),'result':'pass'})
a.bp_clear_all();(ROOT/'results/research_v6/geometry-live-probe.json').write_text(json.dumps({'result':'pass','stream_selection':'explicit test input, all four tables','cases':rows},indent=2));print('Emulator geometry PASS',len(rows))
