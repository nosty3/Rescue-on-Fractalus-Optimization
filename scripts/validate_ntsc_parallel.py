"""Four isolated 60-second replays against sequential pilot references."""
from ntsc_repro_common import *
from concurrent.futures import ThreadPoolExecutor
import threading

SOURCE=ROOT/'results/ntsc_isolated_pilot'
OUT=ROOT/'results/ntsc_parallel_validation'
OUT.mkdir(exist_ok=True)
data=json.loads((SOURCE/'benchmark.json').read_text())
selected=[]
for variant in ('original','v9'):
    rows=sorted((r for r in data['rows'] if r['variant']==variant),key=lambda r:r['measurement']['checkpoints']['60']['fps'])
    selected.extend((rows[0],rows[-1]))
barrier=threading.Barrier(4)
def run(reference):
    name=reference['name']; variant=reference['variant']
    with Emulator(OUT,name) as em:
        barrier.wait(timeout=30)
        initial=entry(em.a,variant,reference['menu_frames'],OUT,name)
        result=measure(em.a,variant,OUT,name,seconds=(15,30,60))
        checks={
            'entry_ram':initial['ram_sha256']==reference['entry']['ram_sha256'],
            'event_ticks':result['events_sha256']==reference['measurement']['events_sha256'],
            'checkpoints':all(all(result['checkpoints'][s][k]==reference['measurement']['checkpoints'][s][k]
                for k in ('intervals','ticks','seconds','fps')) for s in ('15','30','60')),
            **{suffix:(OUT/f'{name}-{suffix}.bin').read_bytes()==(SOURCE/f'{name}-{suffix}.bin').read_bytes()
               for suffix in ('entry','after-warmup','end')},
        }
        row=dict(name=name,variant=variant,pid=em.p.pid,checks=checks,passed=all(checks.values()))
        print(json.dumps(row),flush=True)
        return row
with ThreadPoolExecutor(max_workers=4) as pool:
    results=list(pool.map(run,selected))
report=dict(workers=4,emulator_sha256=hashlib.sha256(EXE.read_bytes()).hexdigest(),results=results,passed=all(r['passed'] for r in results))
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
assert report['passed'],report
