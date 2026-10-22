"""Native cold-start flight samples, fresh process per trial, randomized blocks."""
from ntsc_repro_common import *
import argparse, random

p=argparse.ArgumentParser(); p.add_argument('stage',choices=['pilot','main']); p.add_argument('--count',type=int,default=20)
p.add_argument('--seed',type=int,default=2026102301); p.add_argument('--profile-counter',action='store_true'); p.add_argument('--resume',action='store_true'); args=p.parse_args()
if args.profile_counter:
    validation=json.loads((ROOT/'results/ntsc_profile_validation/validation.json').read_text())
    assert len(validation)==6 and all(r['checkpoints_match'] and all(r['ram_match'].values()) and r['terrain_match'] for r in validation)
    from ntsc_profile_measure import measure_profile
assert 1<=args.count<=600 and args.count%5==0
DEST=ROOT/f'results/ntsc_isolated_{args.stage}'; DEST.mkdir(exist_ok=True)
assert args.resume or not (DEST/'benchmark.json').exists(), 'Preserve the existing results before starting another experiment'
rng=random.Random(args.seed)
delays={v:rng.sample(range(3000,3600),args.count) for v in ('original','v9')}
schedule=[]
for block in range(args.count//5):
    pending=[dict(variant=v,trial=i+1,block=block+1,menu_frames=delays[v][i])
             for v in ('original','v9') for i in range(block*5,block*5+5)]
    rng.shuffle(pending); schedule.extend(pending)
metadata=dict(stage=args.stage,seed=args.seed,count_per_version=args.count,clock_hz=FREQ,
    counter='validated-instruction-profile' if args.profile_counter else 'per-image-breakpoint',
    checkpoints_seconds=[15,30,60],warmup_frames=170,
    method='Fresh emulator process for every native ROM boot; no state loads or memory patches. Uniform sampling of menu delays 3000..3599 without replacement within each version. Blocks of five flights per version, randomized order within block. Centered joystick; first A32E entry, 170 video frames warmup, count B516 intervals until >=60 seconds. Checkpoints at >=15 and >=30 seconds are nested, not independent samples.',
    original_sha256=hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),v9_sha256=SHA,
    emulator_sha256=hashlib.sha256(EXE.read_bytes()).hexdigest())
rows=[]
if args.resume:
    saved=json.loads((DEST/'plan.json').read_text())
    assert saved==dict(metadata=metadata,schedule=schedule)
    previous=json.loads((DEST/'benchmark.json').read_text())
    assert previous['metadata']==metadata
    rows=previous['rows']
    assert all(all(r[k]==schedule[i][k] for k in ('variant','trial','block','menu_frames')) for i,r in enumerate(rows))
else:
    (DEST/'plan.json').write_text(json.dumps(dict(metadata=metadata,schedule=schedule),indent=2))
for task in schedule[len(rows):]:
    name=f"b{task['block']:02}-{task['variant']}-{task['trial']:03}"
    with Emulator(DEST,name) as em:
        initial=entry(em.a,task['variant'],task['menu_frames'],DEST,name)
        measured=(measure_profile if args.profile_counter else measure)(em.a,task['variant'],DEST,name,seconds=(15,30,60))
        row=dict(**task,name=name,entry=initial,measurement=measured)
        rows.append(row)
        (DEST/'benchmark.json').write_text(json.dumps(dict(metadata=metadata,rows=rows),indent=2))
        print(json.dumps(dict(completed=len(rows),total=len(schedule),name=name,
            fps={sec:m['fps'] for sec,m in measured['checkpoints'].items()})),flush=True)
print('ISOLATED BENCHMARK COMPLETE',flush=True)
