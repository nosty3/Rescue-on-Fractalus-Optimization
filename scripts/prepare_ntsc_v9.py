from ntsc_v9_common import *
a=connect();setup(a);advance(a,3000);(OUT/'title.png').write_bytes(a.screenshot());a.state_save(str(OUT/'menu.altstate2'));rows=[]
for label,presses in [('flight',0),('select7',7),('select15',15)]:
 load(a,'menu')
 for i in range(presses):a.consol(select=True);a.frame(12);a.consol();a.frame(12)
 (OUT/f'{label}-menu.png').write_bytes(a.screenshot())
 a.bp_set(0xa32e);a.consol(start=True);a.frame(4000);a.consol();assert a.regs()['PC']=='$a32e',a.regs();a.bp_clear_all();advance(a,120);assert a.peek(0x4a,1)[0]==2
 signature(a);a.state_save(str(OUT/f'{label}.altstate2'));(OUT/f'{label}-start.png').write_bytes(a.screenshot())
 t=a.clock()['tick'];a.frame(120);delta=a.clock()['tick']-t;assert delta==120*FRAME_TICKS
 rows.append({'state':label,'select_pulses':presses,'mode':a.peek(0x4a,1)[0],'timing_probe_frames':120,'timing_probe_ticks':delta,'config':verify(a)});print(label,'PASS',flush=True)
(OUT/'preparation.json').write_text(json.dumps({'result':'pass','rom_sha256':SHA,'clock_hz':FREQ,'ticks_per_frame':FRAME_TICKS,'states':'Fresh native NTSC cold-start states, no PAL states or RAM patching','checks':rows},indent=2))
