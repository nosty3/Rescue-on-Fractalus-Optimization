"""Compare fixed-delay repeated BOOT, fresh processes and same-ROM state replay."""
from ntsc_repro_common import *

DEST=ROOT/'results/ntsc_repro_audit'; DEST.mkdir(exist_ok=True)
rows=[]
def save(row):
    rows.append(row)
    (DEST/'audit.json').write_text(json.dumps(dict(delay_frames=3300,warmup_frames=170,
        emulator_sha256=hashlib.sha256(EXE.read_bytes()).hexdigest(),rows=rows),indent=2))
    print(json.dumps(dict(name=row['name'],terrain=row['entry']['terrain_sha256'],
        fps=row['measurement']['checkpoints']['15']['fps'],events=row['measurement']['events_sha256'])),flush=True)

for variant in ('original','v9'):
    with Emulator(DEST,f'persistent-{variant}') as em:
        for i in range(1,4):
            name=f'persistent-{variant}-{i}'
            initial=entry(em.a,variant,3300,DEST,name)
            if i==1: em.a.state_save(str(DEST/f'{variant}-native-entry.altstate2'))
            measured=measure(em.a,variant,DEST,name)
            save(dict(name=name,kind='persistent',variant=variant,trial=i,entry=initial,measurement=measured))
        for i in range(1,3):
            name=f'replay-{variant}-{i}'
            em.a.bp_clear_all(); em.a.state_load(str(DEST/f'{variant}-native-entry.altstate2'))
            assert em.a.regs()['PC']=='$a32e'; em.a.consol(); em.a.joy(0,'center')
            ram=em.a.memdump(0,0x8000)
            assert ram==(DEST/f'persistent-{variant}-1-entry.bin').read_bytes()
            measured=measure(em.a,variant,DEST,name)
            save(dict(name=name,kind='same_version_replay',variant=variant,trial=i,
                entry=dict(terrain_sha256=hashlib.sha256(ram[0x900:0xa00]).hexdigest()),measurement=measured))
    for i in range(1,4):
        name=f'fresh-{variant}-{i}'
        with Emulator(DEST,name) as em:
            initial=entry(em.a,variant,3300,DEST,name)
            measured=measure(em.a,variant,DEST,name)
            save(dict(name=name,kind='fresh',variant=variant,trial=i,entry=initial,measurement=measured))
print('AUDIT COMPLETE',flush=True)
