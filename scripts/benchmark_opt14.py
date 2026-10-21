from opt14_common import *
import argparse
p=argparse.ArgumentParser();p.add_argument('variants',nargs='+');args=p.parse_args();FREQ=3546895/2
a=connect();a.bp_clear_all();a.config('history','off');saved=OUT/'benchmark.json'
results=[r for r in json.loads(saved.read_text()) if r['variant'] not in args.variants] if saved.exists() else []
for variant in args.variants:
 path=ROOT/f'build/{variant}.car';a.boot(str(path));a.frame(2)
 for scenario,direction,thrust in [('straight','center',False),('right','right',False),('left','left',False),('fast_right','right',True)]:
  a.bp_clear_all();a.state_load(str(ROOT/'results/flying.altstate2'));a.joy(0,direction);patch_state(a,variant)
  assert a.peek(0x8000,8192)==path.read_bytes()[16+0x4000:16+0x6000]
  if thrust:a.consol(option=True);a.frame(45);a.consol()
  a.frame(50);a.bp_set(0xb516);a.frame(100);assert a.regs()['PC']=='$b516';start=a.clock()['tick'];count=0;end=start;events=[start]
  while end-start<3000*35568:
   a.frame(100);assert a.regs()['PC']=='$b516';end=a.clock()['tick'];count+=1;events.append(end)
  a.bp_clear_all();row={'variant':variant,'scenario':scenario,'intervals':count,'ticks':end-start,'fps':count*FREQ/(end-start),'mode':a.peek(0x4a,1)[0]}
  assert row['mode']==2;results.append(row);print(row,flush=True)
  (OUT/f'{variant}-{scenario}.png').write_bytes(a.screenshot());(OUT/f'{variant}-{scenario}-ticks.json').write_text(json.dumps(events));saved.write_text(json.dumps(results,indent=2))
print('DONE',flush=True)
