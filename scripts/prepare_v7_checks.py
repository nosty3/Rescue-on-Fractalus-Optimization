from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=(root/'scripts/stress_opt14.py').read_text().replace("name='opt14_interpolation'","name='v7_clipping'").replace("meta['smc_labels']","json.loads((OUT/'opt14_interpolation-build.json').read_text())['smc_labels']").replace("OUT/f'stress-{label}.png'","OUT/f'v7-stress-{label}.png'").replace("OUT/'stress.json'","ROOT/'results/research_v6/stress.json'")
# Exercise START after saving 9F on the stack, in all geometry banks.
s=s.replace("(12,0x8000)","(10,0x800f),(11,0x800f),(12,0x800f),(13,0x800f)")
s=s.replace("a.joy(0,'center');a.bp_set(entry)","a.joy(0,'center');\n if bank in (10,11,12,13):\n  a.bp_set(0x835e)\n  for _ in range(200):\n   a.frame(100)\n   if a.cart_info()['bank']==2 and a.regs()['PC']=='$835e':break\n  else:raise AssertionError('geometry entry')\n  table=(0x9a55,0x9a82,0x9aaf,0x9adc)[bank-10];a.memload(0x80,bytes([table&255,table>>8]));a.bp_clear_all()\n a.bp_set(entry)")
(root/'scripts/stress_v7.py').write_text(s)
s=(root/'scripts/test_opt14_integration.py').read_text().replace('opt14_width45.rom','opt14_interpolation.rom').replace("new=(ROOT/'build/opt14_interpolation.rom')","new=(ROOT/'build/v7_clipping.rom')").replace("OUT/'integration-tests.json'","ROOT/'results/research_v6/integration-tests.json'").replace('b.memory[0x7eeb:0x7fc2]=patch','a.memory[0x7eeb:0x7fc2]=patch;b.memory[0x7eeb:0x7fc2]=patch')
(root/'scripts/test_v7_integration.py').write_text(s)
