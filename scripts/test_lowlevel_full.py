from test_mountain import *
original=(ROOT/'build/mountain_cull.rom').read_bytes();patched=(ROOT/'build/lowlevel_full.rom').read_bytes()
template=bytearray((ROOT/'tests/fixtures/center-0.bin').read_bytes())
meta=json.loads((ROOT/'results/lowlevel/full-build.json').read_text());wrapper=bytes.fromhex(meta['ram_patch_hex'])
rng=random.Random(0x7eeb);saved=[]
for case in range(1500):
 a=bankcpu(original,template);b=bankcpu(patched,template)
 b.memory[0x7eeb:0x7eeb+len(wrapper)]=wrapper
 for addr in list(range(0x900,0xa00))+list(range(0x27fd,0x2801)):
  a.memory[addr]=b.memory[addr]=rng.randrange(256)
 regs={reg:f'${rng.randrange(256):02x}' for reg in ('A','X','Y')};regs['P']='$30'
 ca=run(a,0x7eeb,regs);cb=run(b,0x7eeb,regs);saved.append(ca-cb)
 assert b.memory.bank==2 and b.memory.switches==2
 assert all(a.memory[j]==b.memory[j] for j in range(0x8000) if not 0x100<=j<0x200 and not 0x7eeb<=j<0x7eeb+len(wrapper)),case
 assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp')),case
out={'result':'pass','cases':1500,'saved_mean':sum(saved)/len(saved),'saved_min':min(saved),'saved_max':max(saved)}
(ROOT/'results/lowlevel/full-equivalence.json').write_text(json.dumps(out,indent=2));print(out)
