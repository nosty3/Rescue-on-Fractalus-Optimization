"""Current cartridge study: 155 mixed flights per video, isolated emulators."""
from pathlib import Path
import sys,json,hashlib,time,datetime,traceback,argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
R=Path(__file__).resolve().parents[1];O=R/'results/new_v12'
from flight_common import pal,ntsc
from flight_transport import measure
EXPECTED='4959a82ab36528a0448a40e6178fdb72d321e5d1e23c258036f5e22e51cfa20e'
CART=R/'optimized version/Rescue on Fractalus! - optimized 128KB.car'
LABEL='v12'
WORKERS=4
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def freeze():
 O.mkdir(parents=True,exist_ok=True);(O/'flights').mkdir(exist_ok=True);(O/'logs').mkdir(exist_ok=True)
 assert CART.read_bytes()[:4]==b'CART' and hashlib.sha256(CART.read_bytes()[16:]).hexdigest()==EXPECTED
 proposed=R/'results/v12/plan.json';base=json.loads(proposed.read_text())
 deps=[Path(__file__),R/'scripts/flight_common.py',R/'scripts/flight_transport.py']
 plan={**base,'status':'APPROVED MIXED PLAN FOR '+LABEL,'version':LABEL,'cartridge':CART.relative_to(R).as_posix(),'rom_sha256':EXPECTED,'car_sha256':sha(CART),'emulator_sha256':sha(pal.EXE),'emulator_binary':str(pal.EXE),'proposal_sha256':sha(proposed),'dependencies_sha256':{p.relative_to(R).as_posix():sha(p) for p in deps},'reference_flights_sha256':sha(R/'results/v11/flights.jsonl'),'workers':WORKERS,'max_batch':16,'transport':'validated bounded packets; per-gate snapshots, presentation BP B516 and game mode watch 4A','publication':'local only'}
 path=O/'plan.json'
 if path.exists():assert json.loads(path.read_text())==plan,'Frozen study settings differ'
 else:path.write_text(json.dumps(plan,indent=2),encoding='utf-8')
 return plan,sha(path)

def run(job,plan_id):
 video,t=job;api=pal if video=='pal' else ntsc;mode=t['mode'];name=f'{video}-{t["execution_order"]:03}-{mode}-seed{t["trial"]:03}'
 dest=O/'flights'/f'{name}.json'
 if dest.exists():
  result=json.loads(dest.read_text());assert result['plan_sha256']==plan_id and result['rom_sha256']==EXPECTED
  return result
 started=utc();wall=time.perf_counter()
 with api.Emulator(O/'logs',name) as em:
  a=em.a;a.boot(str(CART));a.frame(t['menu_frames']);a.bp_set(0xa32e);a.consol(start=True);a.frame(4000)
  assert a.regs()['PC']=='$a32e';a.consol();a.bp_clear_all();cfg=api.verify(a)
  assert a.cart_info()['bank']==2 and a.peek(0x4a,1)[0]==2
  ram=a.memdump(0,0x8000);entry=hashlib.sha256(ram).hexdigest();terrain=hashlib.sha256(ram[0x900:0xa00]).hexdigest()
  flight_start=time.perf_counter();m,transport=measure(a,api,mode,60,max_batch=16);flight_wall=time.perf_counter()-flight_start
 result=dict(version=LABEL,video=video,mode=mode,trial=t['trial'],block=t['block'],execution_order=t['execution_order'],menu_frames=t['menu_frames'],plan_sha256=plan_id,rom_sha256=EXPECTED,entry_ram_sha256=entry,terrain_sha256=terrain,config=cfg,measurement=m,transport=transport,flight_wall_seconds=flight_wall,wall_seconds=time.perf_counter()-wall,started_utc=started,finished_utc=utc())
 pending=dest.with_suffix('.pending');pending.write_text(json.dumps(result,indent=2),encoding='utf-8');pending.replace(dest)
 return result

def validate(result):
 api=pal if result['video']=='pal' else ntsc;m=result['measurement'];events=m['events'];c=m['checkpoints']['60']
 assert len(events)>1 and events[0]==0 and all(y>x for x,y in zip(events,events[1:]))
 assert c['intervals']==len(events)-1 and c['ticks']==events[-1]
 assert abs(c['fps']-c['intervals']*api.FREQ/c['ticks'])<1e-12
 if m['termination'] is None:assert c['complete_window'] and c['seconds']>=60
 else:assert not c['complete_window'] and m['termination']['elapsed_seconds']>=c['seconds']
 if result['mode']=='straight':assert not m['cues']
 else:
  for cue in m['cues']:
   import math
   assert cue['tick']==math.ceil(cue['requested_second']*api.FREQ)

def main():
 global O,CART,LABEL,EXPECTED,WORKERS
 parser=argparse.ArgumentParser();parser.add_argument('--audit-only',action='store_true');parser.add_argument('--cart',type=Path,default=CART);parser.add_argument('--label',default='v12');parser.add_argument('--output',type=Path,default=O);parser.add_argument('--workers',type=int,default=4,choices=range(1,5));args=parser.parse_args()
 O=args.output.resolve();CART=args.cart.resolve();LABEL=args.label;WORKERS=args.workers;EXPECTED=hashlib.sha256(CART.read_bytes()[16:]).hexdigest()
 plan,plan_id=freeze();jobs=[(video,t) for t in plan['schedule'] for video in ('pal','ntsc')]
 assert len(jobs)==310
 if args.audit_only:
  results=[json.loads(p.read_text()) for p in sorted((O/'flights').glob('*.json'))]
  assert len(results)==310
 else:
  results=[];begin=time.perf_counter();started=utc()
  with ThreadPoolExecutor(max_workers=WORKERS) as pool:
   futures={pool.submit(run,j,plan_id):j for j in jobs}
   for f in as_completed(futures):
    try:result=f.result();validate(result)
    except Exception:
     failure=dict(job=futures[f],error=traceback.format_exc(),time_utc=utc())
     (O/'failure.json').write_text(json.dumps(failure,indent=2))
     for q in futures:q.cancel()
     raise
    results.append(result)
    elapsed=time.perf_counter()-begin
    status=dict(completed=len(results),total=310,elapsed_wall_seconds=elapsed,started_utc=started,updated_utc=utc(),workers=WORKERS,early_ends=sum(r['measurement']['termination'] is not None for r in results))
    (O/'status.json').write_text(json.dumps(status,indent=2))
    if len(results)%8==0 or len(results)==310:print(f'{len(results)}/310 wall={elapsed:.1f}s early={status["early_ends"]}',flush=True)
  (O/'run.json').write_text(json.dumps(dict(started_utc=started,finished_utc=utc(),wall_seconds=time.perf_counter()-begin,plan_sha256=plan_id),indent=2))
 for r in results:validate(r);assert r['plan_sha256']==plan_id
 for video in ('pal','ntsc'):
  selected=[r for r in results if r['video']==video]
  assert len(selected)==155 and len({r['trial'] for r in selected})==155
  assert sum(r['mode']=='straight' for r in selected)==78 and sum(r['mode']=='steering' for r in selected)==77
 results.sort(key=lambda r:(r['execution_order'],r['video']))
 (O/'flights.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in results),encoding='utf-8')
 (O/'integrity.json').write_text(json.dumps(dict(complete=True,flights=310,plan_sha256=plan_id,flights_sha256=sha(O/'flights.jsonl'),no_state_transfer=True,no_outlier_rejection=True,all_cues_exact=True,all_event_counts_and_fps_exact=True),indent=2))
 print(f'COMPLETE: 310 valid independent flights, frozen {LABEL} ROM, mixed 50/50 estimator.',flush=True)

if __name__=='__main__':main()
