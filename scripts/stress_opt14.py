from opt14_common import *
OUT=ROOT/'results/opt14';a=connect();a.bp_clear_all();a.config('history','off');rows=[]
name='opt14_interpolation';path=ROOT/f'build/{name}.car'
meta=json.loads((OUT/f'{name}-build.json').read_text());code=bytes.fromhex(meta['ram_patches'][0]['hex']);smc={v+(2 if k in ('high0','low0','high1','low1') else 1) for k,v in meta['smc_labels'].items()}
def advance(frames):
 start=a.clock()['tick'];a.frame(frames);delta=a.clock()['tick']-start
 assert delta>=35568*(frames-2),(frames,a.regs(),delta)
 return delta
def signature():
 ram=a.peek(0x7eeb,len(code));assert all(ram[i]==v for i,v in enumerate(code) if 0x7eeb+i not in smc)
def record(label,frames):
 ticks=advance(frames);signature();r={'name':label,'frames':frames,'ticks':ticks,'mode':a.peek(0x4a,1)[0],'bank':a.cart_info()['bank']};rows.append(r);print(r,flush=True)
 (OUT/f'stress-{label}.png').write_bytes(a.screenshot())
a.boot(str(path));record('cold-title',3000)
a.consol(start=True);advance(60);a.consol();record('cold-flight',2000);assert a.peek(0x4a,1)[0]==2
for label,state in [('level10','level8'),('level26','level16')]:
 for direction in ['left','right','center']:
  a.state_load(str(ROOT/f'results/optimized/{state}.altstate2'));patch_state(a,name);a.joy(0,direction);record(label+'-'+direction,3000)
for bank,entry in [(5,0x982f),(6,0x9863),(8,0x9863),(9,0x930d),(12,0x8000),(14,0x7f20)]:
 a.bp_clear_all();a.state_load(str(ROOT/'results/flying.altstate2'));patch_state(a,name);a.joy(0,'center');a.bp_set(entry)
 for attempt in range(100):
  a.frame(100)
  if a.cart_info()['bank']==bank and a.regs()['PC']==f'${entry:04x}':break
 else:raise AssertionError(('bank not reached',bank))
 a.bp_clear_all();a.consol(start=True);advance(60);a.consol();record(f'start-from-bank{bank}',1000)
a.boot(str(path));advance(3000);a.consol(start=True);advance(60);a.consol();record('restart-flight',2000);assert a.peek(0x4a,1)[0]==2
(OUT/'stress.json').write_text(json.dumps({'result':'pass','rom_sha256':hashlib.sha256(path.read_bytes()[16:]).hexdigest(),'configuration':a.config(),'checks':rows,'note':'Bank guard tested for all extension banks separately; real START tested for listed banks.'},indent=2))
print('Stress PASS',flush=True)
