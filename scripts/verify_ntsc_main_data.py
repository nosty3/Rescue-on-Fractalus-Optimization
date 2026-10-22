"""Offline integrity checks of the complete frozen NTSC experiment."""
from pathlib import Path
import json,hashlib,argparse

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--video',choices=['ntsc','pal'],default='ntsc');args=p.parse_args()
OUT=ROOT/f'results/{args.video}_isolated_main'
plan=json.loads((OUT/'plan.json').read_text())
data=json.loads((OUT/'benchmark.json').read_text())
rows=data['rows'];freq=data['metadata']['clock_hz']
assert data['metadata']==plan['metadata']
assert len(rows)==len(plan['schedule'])==310
for row,task in zip(rows,plan['schedule']):
    assert all(row[k]==task[k] for k in ('variant','trial','block','menu_frames'))
    assert row['entry']['config']['video']==args.video
    name=row['name'];m=row['measurement']
    raw=(OUT/f'{name}-events.json').read_text()
    events=json.loads(raw)
    assert hashlib.sha256(json.dumps(events).encode()).hexdigest()==m['events_sha256']
    assert events[0]==0 and all(a<b for a,b in zip(events,events[1:]))
    assert m['modes']==[2]
    for sec,q in m['checkpoints'].items():
        index=next((i for i,t in enumerate(events) if t>=int(sec)*freq),len(events)-1)
        assert q['intervals']==index and q['ticks']==events[index]
        assert q['seconds']==q['ticks']/freq and q['fps']==index*freq/q['ticks']
        assert q.get('complete_window',True)==(q['ticks']>=int(sec)*freq)
    if m.get('termination'):
        assert events[-1]/freq==m['termination']['last_completed_image_seconds']
        assert m['termination']['elapsed_seconds']>=events[-1]/freq
    for suffix in ('entry','after-warmup','end'):
        ram=(OUT/f'{name}-{suffix}.bin').read_bytes()
        assert len(ram)==32768
        if suffix=='entry':
            assert hashlib.sha256(ram).hexdigest()==row['entry']['ram_sha256']
            assert hashlib.sha256(ram[0x900:0xa00]).hexdigest()==row['entry']['terrain_sha256']
for v in ('original','v9'):
    rr=[r for r in rows if r['variant']==v]
    assert len(rr)==155 and len({r['menu_frames'] for r in rr})==155
result=dict(passed=True,verified_trials=len(rows),benchmark_sha256=hashlib.sha256((OUT/'benchmark.json').read_bytes()).hexdigest(),
    checks=['frozen schedule','155 distinct START delays per version','strictly increasing image ticks',
            'all checkpoint counts and FPS recomputed','early flight endings marked','all event hashes','entry RAM and terrain hashes','32 KB dumps at three points'])
(OUT/'integrity.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
