"""Frozen v10 repeat: 155 flights per standard, original breakpoint counter."""
from pathlib import Path
import json,hashlib,argparse
from concurrent.futures import ThreadPoolExecutor
import pal_repro_common as pal
import ntsc_repro_common as ntsc
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--validate',action='store_true');args=p.parse_args()
CART=ROOT/'optimized version/Rescue on Fractalus! - optimized 128KB.car'
SHA='fde2166f28d768514a933a76654c9c3f9a583d4cdac182ed08aa14d15761bc37'
assert hashlib.sha256(CART.read_bytes()[16:]).hexdigest()==SHA
oldplan=json.loads((ROOT/'results/ntsc_isolated_main/plan.json').read_text())
assert hashlib.sha256(pal.EXE.read_bytes()).hexdigest()==oldplan['metadata']['emulator_sha256']
schedule=[dict(t,variant='v10') for t in oldplan['schedule'] if t['variant']=='v9'];assert len(schedule)==155
OUT=ROOT/'results/v10';OUT.mkdir(exist_ok=True)
completed={}
for video in ('pal','ntsc'):
 folder=OUT/video;folder.mkdir(exist_ok=True)
 plan=dict(metadata=dict(version='v10',video=video,count=155,workers=4,rom_sha256=SHA,emulator_sha256=oldplan['metadata']['emulator_sha256'],warmup_frames=170,seconds=[15,30,60],reference_schedule='ntsc_isolated_main/plan.json: v9 starts',natural_end='Retain all flights; use last complete interval before exit.',counter='per-image-breakpoint'),schedule=schedule)
 if (folder/'plan.json').exists():assert json.loads((folder/'plan.json').read_text())==plan
 else:(folder/'plan.json').write_text(json.dumps(plan,indent=2))
 if (folder/'benchmark.json').exists():
  saved=json.loads((folder/'benchmark.json').read_text());assert saved['metadata']==plan['metadata']
  for t,r in zip(schedule,saved['rows']):
   assert all(t[k]==r[k] for k in ('variant','trial','block','menu_frames'))
   completed[video,r['trial']]=r
def run(video,task,folder,prefix='',seconds=(15,30,60),reference=False):
 api=pal if video=='pal' else ntsc
 name=f"{prefix}b{task['block']:02}-{'v9' if reference else 'v10'}-{task['trial']:03}"
 if not prefix and not reference and (video,task['trial']) in completed:return completed[video,task['trial']]
 done=folder/f'{name}-completed.json'
 if done.exists():return json.loads(done.read_text())
 with api.Emulator(folder,name) as em:
  a=em.a;path=ROOT/'build/reference-v9.car' if reference else CART
  a.boot(str(path));a.frame(task['menu_frames']);api.verify(a)
  a.bp_set(0xa32e);a.consol(start=True);a.frame(4000);assert a.regs()['PC']=='$a32e'
  a.consol();a.bp_clear_all();assert a.cart_info()['bank']==2
  ram=a.memdump(0,0x8000);(folder/f'{name}-entry.bin').write_bytes(ram)
  initial=dict(regs=a.regs(),clock=a.clock(),config=a.config(),ram_sha256=hashlib.sha256(ram).hexdigest(),terrain_sha256=hashlib.sha256(ram[0x900:0xa00]).hexdigest())
  measured=api.measure(a,'baseline',folder,name,seconds=seconds)
  if not reference and task['trial']==155:(folder/f'{name}.png').write_bytes(a.screenshot())
 row=dict(**task,name=name,entry=initial,measurement=measured)
 done.write_text(json.dumps(row,indent=2));return row
if args.validate:
 folder=OUT/'validation';folder.mkdir(exist_ok=True)
 selected=[(video,t) for video in ('pal','ntsc') for t in schedule[:2]]
 seq=[run(v,t,folder,v+'-seq-',(15,)) for v,t in selected]
 with ThreadPoolExecutor(max_workers=4) as pool:par=list(pool.map(lambda q:run(q[0],q[1],folder,q[0]+'-par-',(15,)),selected))
 checks=[]
 for (v,t),a,b in zip(selected,seq,par):
  same=a['measurement']==b['measurement'] and a['entry']['ram_sha256']==b['entry']['ram_sha256'] and all((folder/f"{a['name']}-{s}.bin").read_bytes()==(folder/f"{b['name']}-{s}.bin").read_bytes() for s in ('after-warmup','end'))
  checks.append(dict(video=v,trial=t['trial'],parallel_equal=same));assert same
 # Recheck historical v9 results on the unchanged emulator before reuse.
 refs=[]
 for v in ('pal','ntsc'):
  row=run(v,schedule[0],folder,v+'-reference-',reference=True)
  old=next(r for r in json.loads((ROOT/f'results/{v}_isolated_main/benchmark.json').read_text())['rows'] if r['variant']=='v9' and r['trial']==schedule[0]['trial'])
  old['measurement'].setdefault('termination',None)
  for c in old['measurement']['checkpoints'].values():c.setdefault('complete_window',True)
  equal=row['measurement']==old['measurement'] and row['entry']['ram_sha256']==old['entry']['ram_sha256']
  refs.append(dict(video=v,trial=row['trial'],historical_equal=equal));assert equal,(v,row['measurement'],old['measurement'])
 result=dict(passed=True,parallel=checks,historical=refs,rom_sha256=SHA)
 (folder/'validation.json').write_text(json.dumps(result,indent=2));print(result,flush=True)
else:
 validation=json.loads((OUT/'validation/validation.json').read_text());assert validation['passed'] and validation['rom_sha256']==SHA
 with ThreadPoolExecutor(max_workers=4) as pool:
  for video in ('pal','ntsc'):
   folder=OUT/video;plan=json.loads((folder/'plan.json').read_text());rows=[]
   for block in range(1,32):
    tasks=[t for t in schedule if t['block']==block]
    for row in pool.map(lambda t:run(video,t,folder),tasks):
     rows.append(row);temp=folder/'benchmark.pending.json';temp.write_text(json.dumps(dict(metadata=plan['metadata'],rows=rows),indent=2));temp.replace(folder/'benchmark.json')
     print(video,len(rows),'/155',row['measurement']['checkpoints']['60']['fps'],flush=True)
   assert len(rows)==155
 print('V10 BOTH STANDARDS COMPLETE',flush=True)
