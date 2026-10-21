from session import *
a=connect();a.bp_clear_all();a.config('history','off');out=ROOT/'analysis/lowlevel'
for mode in ['callgraph','insns']:
 a.boot(str(ROOT/'dist/Rescue on Fractalus! - PAL optimized v2.car'));a.frame(2)
 a.state_load(str(ROOT/'results/flying.altstate2'));a.joy(0,'center')
 start=a.clock()['tick'];a.profile_start(mode=mode);a.frame(3000);a.profile_stop();end=a.clock()['tick']
 assert end-start==3000*35568
 p=a.profile_dump_tree() if mode=='callgraph' else a.profile_dump(top=4096)
 (out/f'v2-{mode}.json').write_text(json.dumps(p,indent=2))
 print(mode,'elapsed',end-start,'records',len(p) if isinstance(p,list) else p['count'],flush=True)
a.quit()
