from opt14_common import *
OUT=ROOT/'results/pmg_audit'; a=connect(); rows=[]
for state in ('level8','level16'):
    for entry in (0x710d,0xa71e):
        a.bp_clear_all(); a.boot(str(ROOT/'build/buffer_sync.car')); a.frame(2)
        a.state_load(str(ROOT/f'results/optimized/{state}.altstate2')); patch_state(a,'buffer_sync'); a.joy(0,'center'); a.bp_set(entry); a.frame(1500)
        reached=a.regs()['PC']==f'${entry:04x}'
        row={'state':state,'entry':f'{entry:04X}','reached':reached,'mode':a.peek(0x4a,1)[0]}
        if reached:
            row['regs']=a.regs(); row['inputs']={f'{at:04X}':a.peek(at,1)[0] for at in (0x2865,0x2866,0x2835,0x286f,0x2826)}
            (OUT/f'special-{state}-{entry:04x}.bin').write_bytes(a.memdump(0,65536))
        rows.append(row); print(row,flush=True)
a.bp_clear_all(); (OUT/'special-paths.json').write_text(json.dumps(rows,indent=2))
