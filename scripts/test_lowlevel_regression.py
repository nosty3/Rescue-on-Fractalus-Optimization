from test_mountain import *
old=(ROOT/'build/mountain_cull.rom').read_bytes();new=(ROOT/'build/lowlevel_flag.rom').read_bytes()
fixtures=json.loads((ROOT/'tests/fixtures/index.json').read_text())
for f in fixtures:
 mem=(ROOT/f"tests/fixtures/{f['name']}.bin").read_bytes();a=bankcpu(old,mem);b=bankcpu(new,mem)
 run(a,0x87d3,f['regs']);run(b,0x87d3,f['regs'])
 a.x=b.x=int(f['regs']['X'][1:],16)+3;run(a,0x9308);run(b,0x9308)
 assert all(a.memory[j]==b.memory[j] for j in range(0x8000) if not 0x100<=j<0x200),f['name']
 assert all(getattr(a,k)==getattr(b,k) for k in ('a','x','y','p','sp'))
 assert b.memory.bank==2
# Exercise guard entry and exit around every supported foreground bank.
for bank in (2,5,6):
 c=bankcpu(new,mem);c.memory[0xd500]=bank;c.pc=0xbfda;c.sp=0xf0
 while c.pc!=0xb470:c.step()
 assert c.memory.bank==2
 c.pc=0xbfea
 while c.pc!=0xe462:c.step()
 assert c.memory.bank==bank and c.sp==0xf0
out={'result':'pass','exact_renderer_scenes':len(fixtures),'vbi_restored_banks':[2,5,6]}
(ROOT/'results/lowlevel/regression.json').write_text(json.dumps(out,indent=2));print(out)
