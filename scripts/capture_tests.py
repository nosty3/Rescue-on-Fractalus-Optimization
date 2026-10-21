from session import *
a=connect();a.pause();a.boot(str(ROOT/'original/Rescue on Fractalus!.rom'));a.frame(2)
info=[]
for direction in ['center','right','left','down','up']:
 a.bp_clear_all();a.state_load(str(ROOT/'results/flying.altstate2'));a.joy(0,direction)
 for i in range(8):
  a.frame(70);a.bp_set(0x87d3);a.frame(100);r=a.regs();assert r['PC']=='$87d3';assert a.cart_info()['bank']==2
  name=f'{direction}-{i}'
  mem=b''.join(a.peek(j,16384) for j in range(0,65536,16384));(ROOT/f'tests/fixtures/{name}.bin').write_bytes(mem)
  info.append({'name':name,'regs':r});a.bp_clear_all()
(ROOT/'tests/fixtures/index.json').write_text(json.dumps(info,indent=2));print('Captured',len(info),'terrain pipeline inputs')
