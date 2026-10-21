"""Capture actual v8 PMG routine inputs, measure CPU-only execution separately."""
from opt14_common import *
from opt14_cpu import machine
from collections import Counter
OUT=ROOT/'results/pmg_audit'; OUT.mkdir(exist_ok=True)
a=connect(); a.bp_clear_all(); a.boot(str(ROOT/'build/buffer_sync.car')); a.frame(2)
rows=[]; rom=(ROOT/'build/buffer_sync.rom').read_bytes()
for entry in (0xa527,0xa55c,0xa94d,0xa71e,0xa8de,0x710d):
    a.bp_clear_all(); a.state_load(str(ROOT/'results/flying.altstate2')); patch_state(a,'buffer_sync'); a.joy(0,'right'); a.frame(50)
    a.bp_set(entry)
    for i in range(8):
        a.frame(200)
        if a.regs()['PC']!=f'${entry:04x}':
            rows.append({'entry':f'{entry:04X}','not_reached':True}); break
        regs=a.regs(); data=a.memdump(0,65536)
        (OUT/f'input-{entry:04x}-{i}.bin').write_bytes(data)
        c=machine(rom,data); c.pc=entry; c.sp=0xfd; c.memory[0x1fe]=0xfe; c.memory[0x1ff]=0x3f
        for key,attr in [('A','a'),('X','x'),('Y','y'),('P','p')]: setattr(c,attr,int(regs[key][1:],16))
        writes=[]; pcs=Counter(); steps=0
        while c.pc!=0x3fff:
            pc=c.pc; pcs[pc]+=1; op=c.memory[pc]
            # All PMG stores in these routines use absolute X/Y addressing.
            if op in (0x8d,0x99,0x9d):
                at=c.memory[pc+1]+256*c.memory[pc+2]+(c.y if op==0x99 else c.x if op==0x9d else 0)
                at &= 65535
                if 0xb00<=at<0x1000: writes.append({'pc':f'{pc:04X}','address':f'{at:04X}','old':c.memory[at],'new':c.a})
            c.step(); steps+=1
            assert steps<30000,(entry,hex(c.pc))
        rows.append({'entry':f'{entry:04X}','sample':i,'regs':regs,'mode':data[0x4a],'cycles_cpu_no_dma':c.processorCycles,'pmg_writes':len(writes),'changed_writes':sum(w['old']!=w['new'] for w in writes),'write_sites':dict(Counter(w['pc'] for w in writes)),'key_inputs':{f'{p:04X}':data[p] for p in (0x281a,0x2875,0x2865,0x2866,0x286f,0x2835,0x2826,0x2845,0x2846)}})
        a.bp_clear_all(); a.frame(37); a.bp_set(entry)
    print(hex(entry),'done',flush=True)
a.bp_clear_all()
(OUT/'live-input-observations.json').write_text(json.dumps({'rom_sha256':hashlib.sha256(rom).hexdigest(),'hardware':a.antic(),'samples':rows,'method':'Actual emulator entry states, CPU-only replay with frozen hardware registers. Not a timing profile; random hardware paths are not exact emulator replays.'},indent=2))
print('DONE',flush=True)
