from opt14_common import *
from opt14_cpu import machine,run
OUT=ROOT/'results/pmg_trial';a=connect();a.bp_clear_all();a.boot(str(ROOT/'build/pmg_trial.car'));a.frame(3000)
a.bp_set(0xa55c);a.consol(start=True);a.frame(4000);a.consol()
old=(ROOT/'build/buffer_sync.rom').read_bytes();new=(ROOT/'build/pmg_trial.rom').read_bytes();rows=[]
for i in range(40):
 assert a.regs()['PC']=='$a55c';assert a.cart_info()['bank']==2
 mem=a.memdump(0,65536);regs=a.regs();c=machine(old,mem);d=machine(new,mem)
 run(c,0xa55c,regs);run(d,0xa55c,regs)
 assert all(c.memory[j]==d.memory[j] for j in range(0x8000) if not 0x100<=j<0x200)
 assert all(getattr(c,k)==getattr(d,k) for k in ('a','x','y','p','sp'))
 rows.append({'i':i,'previous':mem[0x2875],'new':mem[0x281a],'same_result':True})
 a.frame(200)
assert rows[0]['previous']==0
assert any(r['previous']==0 and r['new']!=0 for r in rows)
a.bp_clear_all();(OUT/'initialization.json').write_text(json.dumps({'result':'pass','rom_sha256':hashlib.sha256(new).hexdigest(),'first_updates_after_cold_start':rows},indent=2));print('Initialization PASS',rows[:5])
