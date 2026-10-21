from opt14_cpu import *
import argparse
p=argparse.ArgumentParser();p.add_argument('base');p.add_argument('variant');args=p.parse_args();OUT=ROOT/'results/opt14'
old=(ROOT/f'build/{args.base}.rom').read_bytes();new=(ROOT/f'build/{args.variant}.rom').read_bytes();rows=[]
for f in json.loads((ROOT/'tests/fixtures/index.json').read_text()):
 mem=(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes();a=machine(old,mem);b=machine(new,mem)
 ca=run(a,0x87d3,f['regs']);cb=run(b,0x87d3,f['regs']);a.x=b.x=int(f['regs']['X'][1:],16)+3;ca+=run(a,0x9308);cb+=run(b,0x9308)
 diffs=[hex(i) for i in range(0x8000) if not 0x100<=i<0x200 and a.memory[i]!=b.memory[i]]
 regs=[k for k in ('a','x','y','p','sp') if getattr(a,k)!=getattr(b,k)]
 assert not diffs and not regs,(f['name'],diffs[:15],regs,hex(a.p),hex(b.p))
 rows.append({'scene':f['name'],'old_cycles':ca,'new_cycles':cb,'saved':ca-cb})
(OUT/f'{args.variant}-renderer-tests.json').write_text(json.dumps({'result':'pass','base':args.base,'scenes':rows},indent=2));print('PASS',len(rows),'saved',sum(r['saved'] for r in rows))
