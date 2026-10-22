"""Resume a frozen main plan with four validated isolated emulators."""
from ntsc_repro_common import *
from concurrent.futures import ThreadPoolExecutor

OUT=ROOT/'results/ntsc_isolated_main'
validation=json.loads((ROOT/'results/ntsc_parallel_validation/validation.json').read_text())
assert validation['passed'] and len(validation['results'])==4
assert all(all(r['checks'].values()) for r in validation['results'])
assert validation['emulator_sha256']==hashlib.sha256(EXE.read_bytes()).hexdigest()
plan=json.loads((OUT/'plan.json').read_text())
saved=json.loads((OUT/'benchmark.json').read_text())
assert saved['metadata']==plan['metadata']
rows=saved['rows']; schedule=plan['schedule']
assert all(all(row[k]==schedule[i][k] for k in ('variant','trial','block','menu_frames')) for i,row in enumerate(rows))

def run(task):
    name=f"b{task['block']:02}-{task['variant']}-{task['trial']:03}"
    with Emulator(OUT,name) as em:
        initial=entry(em.a,task['variant'],task['menu_frames'],OUT,name)
        measured=measure(em.a,task['variant'],OUT,name,seconds=(15,30,60))
    row=dict(**task,name=name,entry=initial,measurement=measured)
    # Each worker preserves its own finished trial, even if another worker fails.
    (OUT/f'{name}-completed.json').write_text(json.dumps(row,indent=2))
    return row

with ThreadPoolExecutor(max_workers=4) as pool:
    while len(rows)<len(schedule):
        block=schedule[len(rows)]['block']
        pending=[t for t in schedule[len(rows):] if t['block']==block]
        # map yields in schedule order; only this thread writes the aggregate.
        for row in pool.map(run,pending):
            rows.append(row)
            temp=OUT/'benchmark.pending.json'
            temp.write_text(json.dumps(dict(metadata=saved['metadata'],rows=rows),indent=2))
            temp.replace(OUT/'benchmark.json')
            print(json.dumps(dict(completed=len(rows),total=len(schedule),name=row['name'],
                fps=row['measurement']['checkpoints']['60']['fps'],
                shortened=not row['measurement']['checkpoints']['60'].get('complete_window',True))),flush=True)
print('ISOLATED PARALLEL BENCHMARK COMPLETE',flush=True)
