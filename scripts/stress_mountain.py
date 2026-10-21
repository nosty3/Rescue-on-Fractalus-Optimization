"""Cold boot, flight, higher levels, and START/restart with real PAL interrupts."""
from session import *
import hashlib
OUT=ROOT/'results/mountain';a=connect();a.bp_clear_all();a.config('history','off')
path=ROOT/'build/mountain_cull.rom';rows=[]

def advance(frames):
 start=a.clock()['tick'];a.frame(frames);end=a.clock()['tick']
 assert end-start>=35568*(frames-2),(frames,a.regs(),end-start)
 return end-start

def record(name,frames):
 ticks=advance(frames);row={'name':name,'frames':frames,'ticks':ticks,'mode':a.peek(0x4a,1)[0],'bank':a.cart_info()['bank'],'registers':a.regs()}
 rows.append(row);(OUT/f'stress-{name}.png').write_bytes(a.screenshot());print(name,row['mode'],row['bank'],'PASS',flush=True)

a.boot(str(path));record('cold-title',3000)
a.consol(start=True);advance(60);a.consol();record('cold-flight',2000)
assert a.peek(0x4a,1)[0]==2
for label,state in [('level10','level8'),('level26','level16')]:
 for direction in ['left','right','center']:
  a.state_load(str(ROOT/f'results/optimized/{state}.altstate2'))
  assert a.peek(0x4a,1)[0]==2,(label,'fixture must start in flight')
  a.joy(0,direction);record(label+'-'+direction,3000)
# Trigger the in-flight START path while foreground bank 5 is selected.
a.state_load(str(ROOT/'results/flying.altstate2'));a.bp_set(0x982f);a.frame(100)
assert a.cart_info()['bank']==5;a.bp_clear_all();a.consol(start=True);advance(60);a.consol();record('start-from-bank5',1000)
# A new power-on must recover title/flight after all previous transitions.
a.boot(str(path));advance(3000);a.consol(start=True);advance(60);a.consol();record('restart-flight',2000)
assert a.peek(0x4a,1)[0]==2
(OUT/'stress.json').write_text(json.dumps({'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'configuration':a.config(),'checks':rows,'result':'pass'},indent=2))
print('All stress checks PASS',flush=True)
