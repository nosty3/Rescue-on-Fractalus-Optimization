from opt14_common import *
OUT=ROOT/'results/research_v6';OUT.mkdir(exist_ok=True)
cart=ROOT/'dist/Rescue on Fractalus! - PAL optimized v6 128KB.car'
a=connect();a.bp_clear_all();a.config('history','off');manifest={'sha256':hashlib.sha256(cart.read_bytes()[16:]).hexdigest(),'runs':[]}
for scenario,direction,thrust in [('straight','center',False),('right','right',False),('left','left',False),('fast_right','right',True)]:
 for mode in ('callgraph','insns'):
  a.boot(str(cart));a.frame(2);a.state_load(str(ROOT/'results/flying.altstate2'));patch_state(a,'opt14_interpolation');a.joy(0,direction)
  if thrust:a.consol(option=True);a.frame(45);a.consol()
  a.frame(50);start=a.clock()['tick'];a.profile_start(mode=mode);a.frame(3000);a.profile_stop();end=a.clock()['tick'];assert end-start==3000*35568
  data=a.profile_dump_tree() if mode=='callgraph' else a.profile_dump(top=8192)
  (OUT/f'{scenario}-{mode}.json').write_text(json.dumps(data,indent=2))
  row={'scenario':scenario,'mode':mode,'ticks':end-start,'flight_mode':a.peek(0x4a,1)[0]};manifest['runs'].append(row);print(row,flush=True)
(OUT/'profile-manifest.json').write_text(json.dumps(manifest,indent=2));a.pause()
