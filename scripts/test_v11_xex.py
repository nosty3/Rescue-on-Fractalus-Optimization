"""Native boot, flight, steering/fire and pause/resume for candidate XEX."""
import sys,json,hashlib
sys.dont_write_bytecode=True
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pal_repro_common as pal
R=Path(__file__).resolve().parents[1];O=R/'build/v11-smoke';O.mkdir(parents=True,exist_ok=True);X=R/'optimized version/Rescue on Fractalus! - optimized 320KB-1MB.xex'
def run(job):
 video,memory=job;name=f'smoke-{video}-{memory}'
 with pal.Emulator(O,name) as e:
  a=e.a;a.config('video',video);a.config('memory',memory);a.boot(str(X))
  a.bp_set(0x617a);a.frame(8000);assert a.regs()['PC']=='$617a',a.regs();a.bp_clear_all();a.frame(1665)
  a.bp_set(0x632e);a.consol(start=True);a.frame(4000);assert a.regs()['PC']=='$632e',a.regs();a.consol();a.bp_clear_all();a.frame(350)
  for i in range(3):
   a.key_raw('ESC');a.frame(8);a.key_raw('ESC',down=False);a.frame(25);assert int(a.regs()['PC'][1:],16) in range(0x773a,0x773d),a.regs()
   a.bp_set(0x6b1d);a.key_raw('ESC');a.frame(100);assert a.regs()['PC']=='$6b1d',a.regs();a.key_raw('ESC',down=False);a.bp_clear_all();a.bp_set(0x7516)
   for _ in range(5):a.frame(150);assert a.regs()['PC']=='$7516',a.regs()
   a.bp_clear_all();a.joy(0,['n','e','w'][i],fire=True);a.frame(130);a.joy(0,'c',fire=False)
  # Further flight with descent pulses; check that presentations continue.
  for i in range(12):
   a.joy(0,'n' if i%2==0 else 'c');a.frame(50 if i%2==0 else 150);a.bp_set(0x7516);a.frame(200);assert a.regs()['PC']=='$7516',a.regs();a.bp_clear_all()
  a.joy(0,'c');(O/(name+'.png')).write_bytes(a.screenshot())
  result=dict(video=video,memory=memory,passed=True,pause_resume_cycles=3,steering_and_fire=True,descent_pulses=6,final_mode=a.peek(0x4a,1)[0])
 (O/(name+'.json')).write_text(json.dumps(result,indent=2));print(name,'PASS',flush=True);return result
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(run,[(v,m) for v in ('pal','ntsc') for m in ('320k','576k','1088k')]))
 (O/'smoke.json').write_text(json.dumps(rows,indent=2))
