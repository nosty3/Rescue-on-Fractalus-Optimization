"""Fresh-process reproduction of old minimum/maximum trials in each group."""
from ntsc_repro_common import *
DEST=ROOT/'results/ntsc_repro_audit'
old=json.loads((ROOT/'results/ntsc_cold_20x2/benchmark.json').read_text())['rows']
rows=[]
for variant in ('original','v9'):
    for series in (1,2):
        group=[r for r in old if r['variant']==variant and r['series']==series]
        for label,previous in [('min',min(group,key=lambda r:r['fps'])),('max',max(group,key=lambda r:r['fps']))]:
            name=f'old-{variant}-s{series}-{label}'
            with Emulator(DEST,name) as em:
                initial=entry(em.a,variant,previous['menu_frames'],DEST,name)
                measured=measure(em.a,variant,DEST,name)
                current=measured['checkpoints']['15']
                row=dict(name=name,previous=previous,entry=initial,measurement=measured,
                    terrain_match=initial['terrain_sha256']==previous['terrain_sha256'],
                    intervals_match=current['intervals']==previous['intervals'],ticks_match=current['ticks']==previous['ticks'])
                rows.append(row)
                (DEST/'old-extremes.json').write_text(json.dumps(rows,indent=2))
                print(json.dumps({k:row[k] for k in ('name','terrain_match','intervals_match','ticks_match')}),flush=True)
print('OLD EXTREMES RECHECK COMPLETE',flush=True)
