from opt14_cpu import *
OUT=ROOT/'results/opt14';old=(ROOT/'build/opt14_geometry.rom').read_bytes();new=(ROOT/'build/opt14_interpolation.rom').read_bytes();ram=(ROOT/'tests/fixtures/center-0.bin').read_bytes();rng=random.Random(71414)
meta=json.loads((OUT/'opt14_interpolation-build.json').read_text());patch=bytes.fromhex(meta['ram_patches'][0]['hex']);smc=[v+(2 if k in ('high0','low0','high1','low1') else 1) for k,v in meta['smc_labels'].items()];rows=[]
for i in range(5000):
 data=bytearray(ram);data[0x900:0xa00]=bytes(rng.randrange(256) for _ in range(256))
 for at in range(0x27f0,0x2805):data[at]=rng.randrange(256)
 a=machine(old,data);b=machine(new,data);b.memory[0x7eeb:0x7fc2]=patch
 for at in smc:b.memory[at]=rng.randrange(256)
 regs={'A':f'${rng.randrange(256):02x}','X':f'${rng.randrange(256):02x}','Y':f'${rng.randrange(256):02x}','P':f'${rng.choice((0x30,0x31,0x70,0x71)):02x}'}
 ca=run(a,0x7eeb,regs);cb=run(b,0x7eeb,regs)
 diffs=[hex(j) for j in range(0x8000) if not 0x100<=j<0x200 and not 0x7eeb<=j<0x7fc2 and a.memory[j]!=b.memory[j]];rd=[k for k in ('a','x','y','p','sp') if getattr(a,k)!=getattr(b,k)]
 assert not diffs and not rd and b.memory.bank==2,(i,diffs,rd,hex(a.p),hex(b.p))
 rows.append(ca-cb)
(OUT/'interpolation-tests.json').write_text(json.dumps({'result':'pass','random_cases':len(rows),'poisoned_smc_operands':smc,'saved_min':min(rows),'saved_max':max(rows),'saved_mean':sum(rows)/len(rows),'full_ram_except_code_and_dead_stack':True,'all_registers_flags_match':True},indent=2));print('Interpolation PASS',len(rows),min(rows),max(rows),sum(rows)/len(rows))
