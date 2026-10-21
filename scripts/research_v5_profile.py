"""Read-only profiling of released v5; never patches game code."""
from session import *
import hashlib
OUT=ROOT/'results/research_v5';OUT.mkdir(exist_ok=True)
cart=ROOT/'dist/Rescue on Fractalus! - PAL optimized v5 128KB.car'
manifest={'sha256':hashlib.sha256(cart.read_bytes()[16:]).hexdigest(),'frames_per_run':3000,'runs':[]}
a=connect();a.bp_clear_all();a.config('history','off')
for scenario,direction,thrust in [('straight','center',False),('right','right',False),('left','left',False),('fast_right','right',True)]:
 for mode in ('callgraph','insns'):
  a.boot(str(cart));a.frame(2);a.state_load(str(ROOT/'results/flying.altstate2'));a.joy(0,direction)
  assert a.peek(0x8000,8192)==cart.read_bytes()[16+0x4000:16+0x6000]
  if thrust:a.consol(option=True);a.frame(45);a.consol()
  a.frame(50)
  if scenario=='straight' and mode=='callgraph':
   (OUT/'memory-map.json').write_text(json.dumps(a.memmap(),indent=2))
   (OUT/'config.json').write_text(json.dumps(a.config(),indent=2))
   (OUT/'ram-local.bin').write_bytes(b''.join(a.peek(at,16384) for at in range(0,65536,16384)))
  start=a.clock()['tick'];a.profile_start(mode=mode);a.frame(3000);a.profile_stop();end=a.clock()['tick']
  assert end-start==3000*35568
  data=a.profile_dump_tree() if mode=='callgraph' else a.profile_dump(top=4096)
  (OUT/f'{scenario}-{mode}.json').write_text(json.dumps(data,indent=2))
  row={'scenario':scenario,'mode':mode,'ticks':end-start,'flight_mode':a.peek(0x4a,1)[0]}
  manifest['runs'].append(row);(OUT/'profile-manifest.json').write_text(json.dumps(manifest,indent=2))
  print(row,flush=True)
a.pause()
