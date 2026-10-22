from ntsc_v9_common import *
a=connect();rows=[]
for scenario,direction,thrust in [('straight','center',False),('right','right',False),('left','left',False),('fast_right','right',True)]:
 load(a);a.joy(0,direction)
 if thrust:a.consol(option=True);a.frame(45);a.consol()
 advance(a,50);a.bp_set(0xb516);a.frame(200);assert a.regs()['PC']=='$b516';start=a.clock()['tick'];events=[start];modes=set()
 while events[-1]-start<3600*FRAME_TICKS:
  a.frame(200);assert a.regs()['PC']=='$b516',a.regs();events.append(a.clock()['tick']);modes.add(a.peek(0x4a,1)[0])
 a.bp_clear_all();verify(a);signature(a);assert modes=={2},(scenario,modes)
 ticks=events[-1]-start;count=len(events)-1;row={'scenario':scenario,'intervals':count,'ticks':ticks,'seconds':ticks/FREQ,'fps':count*FREQ/ticks,'mode_throughout':2,'configuration':a.config()};rows.append(row)
 (OUT/f'{scenario}-ticks.json').write_text(json.dumps(events));(OUT/f'{scenario}-end.png').write_bytes(a.screenshot());(OUT/'benchmark.json').write_text(json.dumps({'rom_sha256':SHA,'clock_hz':FREQ,'minimum_frames_per_scenario':3600,'rows':rows},indent=2));print(row,flush=True)
print('Benchmark PASS',flush=True)
