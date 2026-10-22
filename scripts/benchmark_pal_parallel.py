"""Frozen PAL counterpart of the 155-per-version NTSC native-boot study."""
from pal_repro_common import *
from concurrent.futures import ThreadPoolExecutor
import argparse

p=argparse.ArgumentParser();p.add_argument('--validate',action='store_true');args=p.parse_args()
OUT=ROOT/'results/pal_isolated_main';OUT.mkdir(exist_ok=True)
REF=ROOT/'results/pal_parallel_validation';REF.mkdir(exist_ok=True)
ntsc=json.loads((ROOT/'results/ntsc_isolated_main/plan.json').read_text())
schedule=ntsc['schedule']
metadata=dict(ntsc['metadata'],video='pal',clock_hz=FREQ,workers=4,
    frame_ticks=FRAME_TICKS,natural_flight_end_rule='Retain shortened flights; count complete image intervals before leaving flight mode.',
    size_basis='155 per version fixed before PAL measurement to repeat the NTSC protocol; no separate PAL pilot.',
    method='Fresh isolated emulator for each native boot; original and v9; PAL 800XL 64K stock. Same frozen menu-frame schedule as NTSC (3000..3599), 170 video frames warmup, centered joystick. B516 image intervals until first completed image after 15/30/60 seconds, or natural flight end. No state transfer, no memory patches. Four processes; balanced blocks of five per version.')
plan=dict(metadata=metadata,schedule=schedule)
if (OUT/'plan.json').exists():assert json.loads((OUT/'plan.json').read_text())==plan
else:(OUT/'plan.json').write_text(json.dumps(plan,indent=2))

def run(task,folder=OUT,prefix='',seconds=(15,30,60)):
    name=f"{prefix}b{task['block']:02}-{task['variant']}-{task['trial']:03}"
    with Emulator(folder,name) as em:
        initial=entry(em.a,task['variant'],task['menu_frames'],folder,name)
        measured=measure(em.a,task['variant'],folder,name,seconds=seconds)
    row=dict(**task,name=name,entry=initial,measurement=measured)
    (folder/f'{name}-completed.json').write_text(json.dumps(row,indent=2))
    return row

if args.validate:
    selected=[r for v in ('original','v9') for r in [t for t in schedule if t['variant']==v][:2]]
    sequential=[run(t,REF,'seq-',(15,)) for t in selected]
    with ThreadPoolExecutor(max_workers=4) as pool:
        parallel=list(pool.map(lambda t:run(t,REF,'par-',(15,)),selected))
    checks=[]
    for a,b in zip(sequential,parallel):
        equal=dict(events=a['measurement']==b['measurement'],entry_ram=a['entry']['ram_sha256']==b['entry']['ram_sha256'],
            **{suffix:(REF/f"{a['name']}-{suffix}.bin").read_bytes()==(REF/f"{b['name']}-{suffix}.bin").read_bytes() for suffix in ('entry','after-warmup','end')})
        checks.append(dict(variant=a['variant'],menu_frames=a['menu_frames'],checks=equal,passed=all(equal.values())))
    result=dict(passed=all(r['passed'] for r in checks),workers=4,video='pal',seconds=15,
        emulator_sha256=hashlib.sha256(EXE.read_bytes()).hexdigest(),results=checks)
    (REF/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
    assert result['passed']
else:
    validation=json.loads((REF/'validation.json').read_text())
    assert validation['passed'] and validation['emulator_sha256']==hashlib.sha256(EXE.read_bytes()).hexdigest()
    rows=[]
    if (OUT/'benchmark.json').exists():
        saved=json.loads((OUT/'benchmark.json').read_text());assert saved['metadata']==metadata;rows=saved['rows']
        assert all(all(r[k]==schedule[i][k] for k in ('variant','trial','block','menu_frames')) for i,r in enumerate(rows))
    with ThreadPoolExecutor(max_workers=4) as pool:
        while len(rows)<len(schedule):
            block=schedule[len(rows)]['block']
            pending=[t for t in schedule[len(rows):] if t['block']==block]
            for row in pool.map(run,pending):
                rows.append(row)
                temp=OUT/'benchmark.pending.json';temp.write_text(json.dumps(dict(metadata=metadata,rows=rows),indent=2));temp.replace(OUT/'benchmark.json')
                print(json.dumps(dict(completed=len(rows),total=len(schedule),name=row['name'],fps=row['measurement']['checkpoints']['60']['fps'],shortened=not row['measurement']['checkpoints']['60']['complete_window'])),flush=True)
    print('PAL BENCHMARK COMPLETE',flush=True)
