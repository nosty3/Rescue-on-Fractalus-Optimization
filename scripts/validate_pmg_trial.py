from opt14_common import *
OUT=ROOT/'results/pmg_trial';a=connect();rows=[]
for scenario,state in [('cold',None),('flight','results/flying.altstate2'),('level10','results/optimized/level8.altstate2'),('level26','results/optimized/level16.altstate2')]:
 a.bp_clear_all();a.boot(str(ROOT/'build/pmg_trial.car'));a.frame(2)
 if state:a.state_load(str(ROOT/state));patch_state(a,'pmg_trial')
 else:
  a.frame(3000);a.consol(start=True);a.frame(60);a.consol();a.frame(2000)
 a.joy(0,'right');a.bp_set(0xa55c);checked=0;nonzero=0
 for i in range(80):
  a.frame(200)
  if a.regs()['PC']!='$a55c':break
  assert a.cart_info()['bank']==2
  prev=a.peek(0x2875,1)[0];pixels=a.peek(0xc97,57)
  if 0<prev<56:
   assert pixels==bytes(0 if j<=prev else 255 for j in range(57)),(scenario,i,prev,pixels.hex());nonzero+=1
  checked+=1
 assert checked>0,scenario
 rows.append({'scenario':scenario,'entries':checked,'coherent_nonzero_previous':nonzero,'mode':a.peek(0x4a,1)[0]});print(rows[-1],flush=True)
a.bp_clear_all();(OUT/'bar-invariant.json').write_text(json.dumps({'result':'pass','rom_sha256':hashlib.sha256((ROOT/'build/pmg_trial.rom').read_bytes()).hexdigest(),'checks':rows},indent=2))
