from cpu_test_support import *
orig=(ROOT/'original/Rescue on Fractalus!.rom').read_bytes()
fixtures=json.loads((ROOT/'tests/fixtures/index.json').read_text());diff=[];count=0
for f in fixtures:
 mem=(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes();c=cpu(orig,mem);run(c,0x87d3,f['regs']);m=c.memory;base=int(f['regs']['X'][1:],16)+3
 for col in range(42):
  actual=next((j for j in range(49) if m[0x1010+96*j+base+col]),48)
  heights=m[0x260e+44+4*col:0x260e+48+4*col];pred=max(0,151-max(heights))
  if actual!=pred:diff.append({'fixture':f['name'],'column':col,'actual':actual,'pred':pred,'heights':heights})
  count+=1
print('columns',count,'mismatch',len(diff));print(diff[:25])
(ROOT/'results/optimized/fill_hypothesis.json').write_text(json.dumps({'columns':count,'mismatches':diff},indent=2))
