from session import *
a=connect();info=json.loads((ROOT/'tests/fixtures/index.json').read_text());names={r['name'] for r in info}
for label,state in [('cold_start','cold-flight'),('level10','level8'),('level26','level16')]:
 a.bp_clear_all();a.state_load(str(ROOT/f'results/optimized/{state}.altstate2'));a.joy(0,'center')
 for i in range(6):
  a.frame(40);a.bp_set(0x87d3);a.frame(100);r=a.regs();assert r['PC']=='$87d3';assert a.cart_info()['bank']==2
  name=f'{label}-{i}';mem=b''.join(a.peek(j,16384) for j in range(0,65536,16384));(ROOT/f'tests/fixtures/{name}.bin').write_bytes(mem)
  if name not in names:info.append({'name':name,'regs':r})
  a.bp_clear_all()
(ROOT/'tests/fixtures/index.json').write_text(json.dumps(info,indent=2));print('Fixtures',len(info))
