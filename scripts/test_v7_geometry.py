from opt14_cpu import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--base',default='opt14_interpolation');args=p.parse_args();OUT=ROOT/'results/opt14'
old=(ROOT/f'build/{args.base}.rom').read_bytes();new=(ROOT/'build/v7_geometry.rom').read_bytes();mem=(ROOT/'tests/fixtures/center-0.bin').read_bytes();rng=random.Random(83514)
rows=[]
for i in range(1000):
 data=bytearray(mem);table=(0x9a55,0x9a82,0x9aaf,0x9adc)[i%4];data[0x80]=table&255;data[0x81]=table>>8;data[0xb6]=rng.randrange(16)*16
 for at in list(range(0xa0,0xa4))+[0x8b,0x8c,0xb5]:data[at]=rng.randrange(256)
 for at in (0x22a3,0x22d1,0x22ff,0x232d):data[at]=rng.randrange(256)
 a=machine(old,data);b=machine(new,data);regs={'A':f'${rng.randrange(256):02x}','X':f'${rng.randrange(16):02x}','Y':'$ab','P':f'${rng.choice((0x30,0x31,0x70,0x71)):02x}'}
 ca=run(a,0x835e,regs);cb=run(b,0x835e,regs)
 diffs=[hex(j) for j in range(0x8000) if not 0x100<=j<0x200 and a.memory[j]!=b.memory[j]];rd=[k for k in ('a','x','y','p','sp') if getattr(a,k)!=getattr(b,k)]
 assert not diffs and not rd,(i,diffs[:20],rd,hex(a.p),hex(b.p))
 rows.append(ca-cb)
fixtures=json.loads((ROOT/'tests/fixtures/index.json').read_text());scenes=[]
for f in fixtures:
 data=(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes();a=machine(old,data);b=machine(new,data);ca=run(a,0x8309,f['regs']);cb=run(b,0x8309,f['regs'])
 assert all(a.memory[j]==b.memory[j] for j in range(0x8000) if not 0x100<=j<0x200),f['name']
 assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp')),f['name']
 scenes.append({'scene':f['name'],'old_cycles':ca,'new_cycles':cb,'saved':ca-cb})
(OUT/'v7-geometry-tests.json').write_text(json.dumps({'result':'pass','random_cases':len(rows),'random_saved_min':min(rows),'random_saved_max':max(rows),'scenes':scenes},indent=2));print('Geometry PASS',len(rows),len(scenes),'saved',sum(r['saved'] for r in scenes))
