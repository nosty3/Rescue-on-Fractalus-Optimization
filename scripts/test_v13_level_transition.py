"""Diagnostic return-to-mothership fixture, not a performance benchmark."""
import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from flight_common import pal
HERE=R/'optimized version';O=R/'results/v13/functional';O.mkdir(parents=True,exist_ok=True)
paths={'car':HERE/'Rescue on Fractalus! - optimized 512KB.car','candidate':HERE/'Rescue on Fractalus! - optimized 512KB - 1MB RAM.xex','solo':R/'arc/up38/bin/fractalus_up38_320k-1mb.xex'}
video='ntsc' if '--ntsc' in sys.argv else 'pal';memory=next((x for x in sys.argv if x in ('320k','576k','1088k')),'320k');equal='--equal' in sys.argv;release='--release' in sys.argv
kind=sys.argv[1];fixed='--fix' in sys.argv;name=kind+('-patched' if fixed else '-broken');rel=0 if kind=='car' else 0xc000
if release:name=f'{kind}-release-{video}-{memory}-'+('equal' if equal else 'plus1')
elif kind=='candidate':raise ValueError('For current v11 use candidate --release; use solo to reproduce the historical defect')
with pal.Emulator(O,name) as e:
 a=e.a;a.config('memory',memory);a.config('video',video);a.boot(str(paths[kind]))
 if rel:a.bp_set(0x617a);a.frame(8000);assert a.regs()['PC']=='$617a';a.bp_clear_all();a.frame(1665)
 else:a.frame(3165)
 a.bp_set(0xa32e^rel);a.consol(start=True);a.frame(4000);assert int(a.regs()['PC'][1:],16)==(0xa32e^rel);a.consol();a.bp_clear_all()
 if fixed:
  assert a.peek(0x97d4,1)==bytes([0x57]) and a.peek(0x97da,1)==bytes([0x57])
  a.poke(0x97d4,0x97);a.poke(0x97da,0x97)
 # Set only game data to a completed rescue/return; execute original return code.
 a.poke(0x72,2);a.bp_set(0xa3db^rel);a.frame(400);assert int(a.regs()['PC'][1:],16)==(0xa3db^rel),a.regs()
 a.poke(0x34,0x40);a.poke(0x283b,0x80);a.bp_clear_all();a.bp_set(0x43c4^rel);a.frame(1000);assert int(a.regs()['PC'][1:],16)==(0x43c4^rel),a.regs()
 a.poke(0x6c,1);a.poke(0x060b,1);a.poke(0x0626,2 if equal else 3);a.poke(0x0627,2)
 a.bp_clear_all();a.bp_set(0x467b^rel);a.frame(8000);assert int(a.regs()['PC'][1:],16)==(0x467b^rel),a.regs()
 start_level=a.peek(0x6d,1)[0];before=a.peek(0x0657,6).hex();a.bp_clear_all();a.bp_set(0x4680^rel);a.frame(2000)
 reached=int(a.regs()['PC'][1:],16)==(0x4680^rel)
 result=dict(video=video,memory=memory,equal_quota=equal,kind=kind,patched=fixed,melody_descriptor=before,melody_finished=reached,regs=a.regs(),sound_active=a.peek(0x655,1)[0],level_before=start_level)
 if reached:
  a.bp_clear_all();a.bp_set(0x4738^rel);a.frame(4000);result['level_increment_reached']=int(a.regs()['PC'][1:],16)==(0x4738^rel);result['level_after']=a.peek(0x6d,1)[0]
  a.bp_clear_all();a.bp_set(0x47a7^rel);a.frame(4000);result['launch_screen']=int(a.regs()['PC'][1:],16)==(0x47a7^rel);a.bp_clear_all();a.joy(0,'c',fire=True);a.bp_set(0xa32e^rel);a.frame(8000);a.joy(0,'c',fire=False);result['next_flight']=int(a.regs()['PC'][1:],16)==(0xa32e^rel)
 if release:assert result['melody_finished'] and result['level_increment_reached'] and result['next_flight'],result
 (O/(name+'.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
