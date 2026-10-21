from opt14_common import *
OUT=ROOT/'results/buffer_race';a=connect();a.bp_clear_all();a.boot(str(ROOT/'build/buffer_sync.car'));a.frame(2);a.state_load(str(ROOT/'results/flying.altstate2'));patch_state(a,'buffer_sync');a.joy(0,'right');a.frame(50);a.bp_set(0x84ac);rows=[]
for i in range(240):
 for _ in range(200):
  a.frame(100)
  if a.regs()['PC']=='$84ac' and a.cart_info()['bank']==2:break
 else:raise AssertionError('clear body not reached')
 flag=a.peek(0x42,1)[0];assert flag==0,(i,flag)
 rows.append({'i':i,'ready':flag,'x':a.regs()['X'],'beam_y':a.antic()['beam_y']})
 if i%40==39:print('Validated',i+1,flush=True)
a.bp_clear_all();a.state_load(str(ROOT/'results/flying.altstate2'));patch_state(a,'buffer_sync');a.bp_set(0x84a6)
for _ in range(300):
 a.frame(100)
 if a.regs()['PC']=='$84a6' and a.cart_info()['bank']==2 and a.peek(0x42,1)[0]:break
else:raise AssertionError('pending wait not reached')
a.bp_clear_all();a.consol(start=True);a.frame(60);a.consol();a.frame(1500);assert a.peek(0x4a,1)[0]==2
(OUT/'sync-validation.json').write_text(json.dumps({'result':'pass','clear_checks':rows,'start_while_waiting':True,'rom_sha256':hashlib.sha256((ROOT/'build/buffer_sync.rom').read_bytes()).hexdigest()},indent=2));print('Sync checks PASS',len(rows))
