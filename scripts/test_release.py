from cpu_test_support import *
orig=(ROOT/'Rescue on Fractalus!.rom').read_bytes();rom=(ROOT/'build/release.rom').read_bytes();fixtures=json.loads((ROOT/'tests/fixtures/index.json').read_text());results=[]
for f in fixtures:
 mem=(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes();a=cpu(orig,mem);b=cpu(rom,mem)
 ca=run(a,0x87d3,f['regs']);cb=run(b,0x87d3,f['regs'])
 # Both halves of the main loop call fill with X=3 or $33.
 a.x=b.x=int(f['regs']['X'][1:],16)+3
 fca=run(a,0x9308);fcb=run(b,0x9308)
 diffs=[hex(i) for i in range(0x8000) if not 0x100<=i<0x200 and a.memory[i]!=b.memory[i]]
 regs=[k for k in ['a','x','y','p','sp'] if getattr(a,k)!=getattr(b,k)]
 results.append({'fixture':f['name'],'cycles_original':ca+fca,'cycles_optimized':cb+fcb,'fill_original':fca,'fill_optimized':fcb,'diff':diffs,'regs':regs})
print('failures',[r for r in results if r['diff'] or r['regs']])
print('fill cycles',sum(r['fill_original'] for r in results),sum(r['fill_optimized'] for r in results))
(ROOT/'results/optimized/release_equivalence.json').write_text(json.dumps(results,indent=2))
assert all(not r['diff'] and not r['regs'] for r in results)


