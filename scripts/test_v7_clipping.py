from opt14_cpu import *
OUT=ROOT/'results/research_v6';old=(ROOT/'build/v7_geometry.rom').read_bytes();new=(ROOT/'build/v7_clipping.rom').read_bytes();rng=random.Random(9627)
rows=[]
for f in json.loads((ROOT/'tests/fixtures/index.json').read_text()):
 mem=(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes();a=machine(old,mem);b=machine(new,mem)
 ca=run(a,0x87d3,f['regs']);cb=run(b,0x87d3,f['regs']);a.x=b.x=int(f['regs']['X'][1:],16)+3;ca+=run(a,0x9308);cb+=run(b,0x9308)
 diff=[hex(i) for i in range(0x8000) if not 0x100<=i<0x200 and a.memory[i]!=b.memory[i]]
 assert not diff,(f['name'],diff[:20]);assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp')),f['name']
 rows.append({'scene':f['name'],'old':ca,'new':cb,'saved':ca-cb})
mem=(ROOT/'tests/fixtures/center-0.bin').read_bytes()
for i in range(3000):
 data=bytearray(mem)
 for at in (0x82,0x84,0x86,0x25b4,0x25f0,0x23e2):data[at]=rng.randrange(256)
 for at in (0x83,0x85,0x25d2,0x24e2):data[at]=0 if i%2 else rng.randrange(256)
 a=machine(old,data);b=machine(new,data);regs={'A':'$00','X':f'${0 if i%3 else rng.randrange(16):02x}','Y':'$35','P':f'${rng.choice((0x30,0x31,0x70,0x71)):02x}'}
 run(a,0x9627,regs);run(b,0x9627,regs)
 diff=[hex(j) for j in range(0x8000) if not 0x100<=j<0x200 and a.memory[j]!=b.memory[j]]
 assert not diff,(i,diff[:20]);assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp')),(i,[(k,getattr(a,k),getattr(b,k)) for k in ('a','x','y','p')])
(OUT/'clipping-tests.json').write_text(json.dumps({'result':'pass','scenes':rows,'random_cases':3000},indent=2));print('Clipping PASS',len(rows),'saved',sum(r['saved'] for r in rows),flush=True)
