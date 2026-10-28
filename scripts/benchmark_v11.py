"""Frozen four-arm native-boot comparison, presentation counting with timed input."""
from pathlib import Path
import json,hashlib,time,math,sys,argparse
sys.dont_write_bytecode=True
from concurrent.futures import ThreadPoolExecutor,as_completed
import pal_repro_common as pal,ntsc_repro_common as ntsc
R=Path(__file__).resolve().parents[1];O=None
ROMS={'up38':R/'arc/up38/bin/fractalus_up38.car','v11':R/'optimized version/Rescue on Fractalus! - optimized 128KB.car', 'original':pal.ORIGINAL}
HASHES={'up38':'6087e9b314368b95e7885f5634c88a506bbc61d7a4c988db345e7373377253da','v11':'ec01982121b70baca35f04568617965c3164e716e0a5eb3c6ebcbb123566a868'}
HASHES['original']='1eb18e2a1ff31f43871a5e4e21e73f61b7659177d33d2cdbb29f36530b9f4d68'
for v,p in ROMS.items():assert hashlib.sha256(p.read_bytes() if v=='original' else p.read_bytes()[16:]).hexdigest()==HASHES[v]
old=json.loads((R/'results/ntsc_isolated_main/plan.json').read_text());S=[t for t in old['schedule'] if t['variant']=='v9'];assert len(S)==155

def step_and_read(a,command):
 a._sock.sendall((command+'\nEVAL pc+65536*db($4a)\nCLOCK\n').encode('ascii'))
 r=[json.loads(a._recv_line()) for _ in range(3)]
 assert all(x.get('ok') for x in r),r
 return r[1]['value'],r[2]['tick']

def measure(a,api,mode,seconds):
 api.advance(a,170);a.bp_set(0xb516);a.frame(200);assert a.regs()['PC']=='$b516'
 start=a.clock()['tick'];events=[0];cues=[];termination=None;checks={};elapsed=0;nextcue=0
 a.watch_set(0x4a,mode='w')
 while events[-1]<seconds*api.FREQ:
  if mode=='steering':
   if elapsed>=nextcue*api.FREQ:
    direction='n' if nextcue%4==0 else 'c';a.joy(0,direction);cues.append(dict(requested_second=nextcue,tick=elapsed,direction=direction));nextcue+=1 if direction=='n' else 3
   command=f'CYCLES {max(1,math.ceil(nextcue*api.FREQ)-elapsed)}'
  else:command='FRAME 200'
  packed,tick=step_and_read(a,command);game_mode=packed>>16;pc=packed&65535;elapsed=tick-start
  if game_mode!=2:
   termination=dict(mode=game_mode,pc=hex(pc),elapsed_seconds=elapsed/api.FREQ,last_completed_image_seconds=events[-1]/api.FREQ);break
  if pc==0xb516:
   assert elapsed>events[-1];events.append(elapsed)
   for sec in (15,30,60):
    if sec<=seconds and str(sec) not in checks and elapsed>=sec*api.FREQ:checks[str(sec)]=dict(intervals=len(events)-1,ticks=elapsed,seconds=elapsed/api.FREQ,fps=(len(events)-1)*api.FREQ/elapsed,complete_window=True)
  else:assert mode=='steering' and elapsed>=nextcue*api.FREQ,(pc,elapsed,nextcue)
 assert len(events)>1
 for sec in (15,30,60):
  if sec<=seconds and str(sec) not in checks:checks[str(sec)]=dict(intervals=len(events)-1,ticks=events[-1],seconds=events[-1]/api.FREQ,fps=(len(events)-1)*api.FREQ/events[-1],complete_window=False)
 a.bp_clear_all();api.verify(a)
 return dict(checkpoints=checks,termination=termination,events=events,cues=cues,end_ram_sha256=hashlib.sha256(a.memdump(0,0x8000)).hexdigest())

def run(job,seconds=60,prefix='main',reference=False):
 video,version,mode,t=job;api=pal if video=='pal' else ntsc;folder=O/prefix;folder.mkdir(exist_ok=True);name=f'{video}-{version}-{mode}-{t["trial"]:03}';dest=folder/(name+'.json')
 if dest.exists():return json.loads(dest.read_text())
 wall=time.perf_counter()
 with api.Emulator(folder,name) as em:
  a=em.a;a.boot(str(ROMS[version]));a.frame(t['menu_frames']);a.bp_set(0xa32e);a.consol(start=True);a.frame(4000);assert a.regs()['PC']=='$a32e';a.consol();a.bp_clear_all();api.verify(a)
  entry_ram=a.memdump(0,0x8000);entry=hashlib.sha256(entry_ram).hexdigest()
  if prefix.startswith('post'):(folder/(name+'-entry.bin')).write_bytes(entry_ram)
  if reference:m=api.measure(a,'research',folder,name,seconds=(seconds,));m['end_ram_sha256']=hashlib.sha256(a.memdump(0,0x8000)).hexdigest()
  else:m=measure(a,api,mode,seconds)
  if prefix.startswith('post'):(folder/(name+'-end.bin')).write_bytes(a.memdump(0,0x8000))
  if prefix.startswith('pilot'):(folder/(name+'.png')).write_bytes(a.screenshot())
 result=dict(video=video,version=version,mode=mode,trial=t['trial'],block=t['block'],menu_frames=t['menu_frames'],rom_sha256=HASHES[version],entry=entry,measurement=m,wall_seconds=time.perf_counter()-wall)
 temp=dest.with_suffix('.pending');temp.write_text(json.dumps(result,indent=2),encoding='utf-8');temp.replace(dest);return result


def main():
 global O
 p=argparse.ArgumentParser(description='Fresh cold-boot cartridge benchmarks. Never uses save-state transfer.');p.add_argument('--output',required=True,help='New output directory; do not point at published data');p.add_argument('--versions',nargs='+',choices=list(ROMS),default=['original','v11']);p.add_argument('--modes',nargs='+',choices=['straight','steering'],default=['straight','steering']);p.add_argument('--video',nargs='+',choices=['pal','ntsc'],default=['pal','ntsc']);p.add_argument('--workers',type=int,choices=[1,2,3,4],default=4);args=p.parse_args()
 O=Path(args.output).resolve();root=R.resolve();assert O.is_relative_to(root),'Output must be inside repository'
 if O.exists():raise RuntimeError('Choose a new output directory to preserve existing measurements')
 O.mkdir(parents=True)
 plan=dict(seconds=60,warmup_frames=170,workers=args.workers,versions=args.versions,modes=args.modes,video=args.video,schedule=S,rom_sha256=HASHES,emulator_sha256=hashlib.sha256(pal.EXE.read_bytes()).hexdigest())
 (O/'plan.json').write_text(json.dumps(plan,indent=2))
 jobs=[(video,v,mode,t) for t in S for video in args.video for mode in args.modes for v in args.versions]
 start=time.perf_counter()
 with ThreadPoolExecutor(max_workers=args.workers) as pool:
  for i,f in enumerate(as_completed([pool.submit(run,j) for j in jobs]),1):
   f.result()
   if i%10==0:print(f'{i}/{len(jobs)} elapsed={time.perf_counter()-start:.1f}s',flush=True)
 print('COMPLETE',len(jobs))
if __name__=='__main__':main()
