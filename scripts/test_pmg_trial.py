from opt14_cpu import *
import hashlib
OUT=ROOT/'results/pmg_trial';OUT.mkdir(exist_ok=True)
old=(ROOT/'build/buffer_sync.rom').read_bytes();new=(ROOT/'build/pmg_trial.rom').read_bytes();mem=(ROOT/'analysis/flying-ram.bin').read_bytes();rng=random.Random(8317);rows=[]
def check(label,entry,data):
 a=machine(old,data);b=machine(new,data)
 regs={k:f'${rng.randrange(256):02x}' for k in ('A','X','Y')};regs['P']=f'${rng.choice((0x30,0x31,0x70,0x71)):02x}'
 ca=run(a,entry,regs);cb=run(b,entry,regs)
 dif=[hex(j) for j in range(0x8000) if not 0x100<=j<0x200 and a.memory[j]!=b.memory[j]]
 assert not dif,(label,dif[:10]);assert a.memory[0xd000:0xd020]==b.memory[0xd000:0xd020],label
 assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp')),(label,[(k,getattr(a,k),getattr(b,k)) for k in ('a','x','y','p','sp')])
 rows.append({'kind':label.split(':')[0],'old':ca,'new':cb})
for prev in range(56):
 for val in range(56):
  d=bytearray(mem);d[0x2875]=prev;d[0x281a]=val
  for y in range(57):d[0xc97+y]=0 if y<=prev else 255
  check(f'bar:{prev}:{val}',0xa55c,d)
for i in range(300):
 d=bytearray(mem);d[0xb00:0x1000]=bytes(rng.randrange(256) for _ in range(1280));d[0x2875]=rng.choice((0,*range(56,256)));d[0x281a]=rng.randrange(256)
 check('bar-fallback:'+str(i),0xa55c,d)
for i in range(600):
 d=bytearray(mem);d[0xb00:0x1000]=bytes(rng.randrange(256) for _ in range(1280))
 for at in (0x291c,0x2872,0x291d,0x2874,0x2845,0x2846,0x2839,0x283a,0xb9,0x28da,0x28d9):d[at]=rng.randrange(256)
 for entry in (0xa527,0xa8de,0xa94d):check(hex(entry)+':'+str(i),entry,d)
for p in (ROOT/'results/pmg_audit').glob('input-*.bin'):
 entry=int(p.name.split('-')[1],16)
 if entry in (0xa527,0xa55c,0xa94d,0xa8de):check('live:'+p.stem,entry,p.read_bytes())
summary={}
for kind in sorted({r['kind'] for r in rows}):
 rr=[r for r in rows if r['kind']==kind];summary[kind]={'cases':len(rr),'cycles_saved_sum':sum(r['old']-r['new'] for r in rr),'min_saved':min(r['old']-r['new'] for r in rr),'max_saved':max(r['old']-r['new'] for r in rr)}
(OUT/'cpu-tests.json').write_text(json.dumps({'result':'pass','rom_sha256':hashlib.sha256(new).hexdigest(),'cases':len(rows),'summary':summary,'comparison':'all RAM except dead stack, GTIA registers, A/X/Y/P/SP; delta bar requires coherent previous image, fallback covers old=0 or out of range'},indent=2));print(summary)
