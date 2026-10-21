"""Real PAL interrupts, both new banks, cold boots and START paths."""
from session import *
import hashlib
OUT=ROOT/'results/clear128';a=connect();a.bp_clear_all();a.config('history','off')
path=ROOT/'build/clear128.car';rows=[]
def advance(frames):
 start=a.clock()['tick'];a.frame(frames);delta=a.clock()['tick']-start
 assert delta>=35568*(frames-2),(frames,a.regs(),delta)
 return delta
def record(name,frames):
 ticks=advance(frames);r={'name':name,'frames':frames,'ticks':ticks,'mode':a.peek(0x4a,1)[0],'bank':a.cart_info()['bank'],'registers':a.regs()}
 rows.append(r);(OUT/f'stress-{name}.png').write_bytes(a.screenshot());print(r,flush=True)
a.boot(str(path));record('cold-title',3000)
a.consol(start=True);advance(60);a.consol();record('cold-flight',2000)
assert a.peek(0x4a,1)[0]==2
for label,state in [('level10','level8'),('level26','level16')]:
 for direction in ['left','right','center']:
  a.state_load(str(ROOT/f'results/optimized/{state}.altstate2'));assert a.peek(0x4a,1)[0]==2
  a.joy(0,direction);record(label+'-'+direction,3000)
for bank,entry in [(5,0x982f),(6,0x9863),(8,0x9863)]:
 a.bp_clear_all();a.state_load(str(ROOT/'results/flying.altstate2'));a.joy(0,'center');a.bp_set(entry)
 for attempt in range(20):
  a.frame(100)
  if a.cart_info()['bank']==bank:break
 else:raise AssertionError(('bank not reached',bank))
 assert a.regs()['PC']==f'${entry:04x}'
 a.bp_clear_all();a.consol(start=True);advance(60);a.consol();record(f'start-from-bank{bank}',1000)
a.boot(str(path));advance(3000);a.consol(start=True);advance(60);a.consol();record('restart-flight',2000)
assert a.peek(0x4a,1)[0]==2
(OUT/'stress.json').write_text(json.dumps({'result':'pass','rom_sha256':hashlib.sha256(path.read_bytes()[16:]).hexdigest(),'configuration':a.config(),'checks':rows},indent=2))
print('All stress checks PASS',flush=True)
