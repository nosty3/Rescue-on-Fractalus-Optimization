"""Cold boot, flight, higher levels, and START/restart with real PAL interrupts."""
from session import *
from lowlevel_state import patch_loaded_state
import argparse
parser=argparse.ArgumentParser();parser.add_argument('variant',nargs='?',default='lowlevel_sound');args=parser.parse_args()
import hashlib
OUT=ROOT/'results/lowlevel';a=connect();a.bp_clear_all();a.config('history','off')
path=ROOT/f'build/{args.variant}.rom';rows=[]

def advance(frames):
 start=a.clock()['tick'];a.frame(frames);end=a.clock()['tick']
 assert end-start>=35568*(frames-2),(frames,a.regs(),end-start)
 return end-start

def record(name,frames):
 ticks=advance(frames);row={'name':name,'frames':frames,'ticks':ticks,'mode':a.peek(0x4a,1)[0],'bank':a.cart_info()['bank'],'registers':a.regs()}
 rows.append(row);(OUT/f'stress-{name}.png').write_bytes(a.screenshot());print(name,row['mode'],row['bank'],'PASS',flush=True)

a.boot(str(path));record('cold-title',3000)
if args.variant in ('lowlevel_full','lowlevel_flag'):
 code=bytes.fromhex(json.loads((OUT/'full-build.json').read_text())['ram_patch_hex'])
 assert a.peek(0x7eeb,len(code))==code,'Cold boot must load modified RAM code'
a.consol(start=True);advance(60);a.consol();record('cold-flight',2000)
assert a.peek(0x4a,1)[0]==2
for label,state in [('level10','level8'),('level26','level16')]:
 for direction in ['left','right','center']:
  a.state_load(str(ROOT/f'results/optimized/{state}.altstate2'))
  if args.variant in ('lowlevel_full','lowlevel_flag'):patch_loaded_state(a)
  assert a.peek(0x4a,1)[0]==2,(label,'fixture must start in flight')
  a.joy(0,direction);record(label+'-'+direction,3000)
# Trigger the in-flight START path while foreground bank 5 is selected.
a.state_load(str(ROOT/'results/flying.altstate2'))
if args.variant in ('lowlevel_full','lowlevel_flag'):patch_loaded_state(a)
a.bp_set(0x982f);a.frame(100)
assert a.cart_info()['bank']==5;a.bp_clear_all();a.consol(start=True);advance(60);a.consol();record('start-from-bank5',1000)
# A new power-on must recover title/flight after all previous transitions.
a.boot(str(path));advance(3000);a.consol(start=True);advance(60);a.consol();record('restart-flight',2000)
assert a.peek(0x4a,1)[0]==2
(OUT/f'{args.variant}-stress.json').write_text(json.dumps({'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'configuration':a.config(),'checks':rows,'result':'pass'},indent=2))
print('All stress checks PASS',flush=True)

