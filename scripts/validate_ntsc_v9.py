from ntsc_v9_common import *
a=connect();pmg=[];sync=[]
for state in ('flight','select7','select15'):
 load(a,state);a.joy(0,'right');a.bp_set(0xa55c)
 for i in range(80):
  a.frame(200);assert a.regs()['PC']=='$a55c';assert a.cart_info()['bank']==2
  prev=a.peek(0x2875,1)[0]
  if 0<prev<56:assert a.peek(0xc97,57)==bytes(0 if j<=prev else 255 for j in range(57)),(state,i,prev)
  pmg.append({'state':state,'i':i,'previous':prev})
 print('PMG',state,'PASS',flush=True)
 load(a,state);a.joy(0,'right');a.bp_set(0x84ac)
 for i in range(40):
  for _ in range(300):
   a.frame(200)
   if a.regs()['PC']=='$84ac' and a.cart_info()['bank']==2:break
  else:raise AssertionError('clear not reached')
  assert a.peek(0x42,1)[0]==0
  sync.append({'state':state,'i':i,'ready':0,'beam_y':a.antic()['beam_y']})
 print('Sync',state,'PASS',flush=True)
load(a);a.bp_set(0x84a6)
for _ in range(400):
 a.frame(200)
 if a.regs()['PC']=='$84a6' and a.cart_info()['bank']==2 and a.peek(0x42,1)[0]:break
else:raise AssertionError('pending wait not reached')
a.bp_clear_all();a.consol(start=True);advance(a,60);a.consol();advance(a,2400);assert a.peek(0x4a,1)[0]==2;signature(a)
(OUT/'validation.json').write_text(json.dumps({'result':'pass','rom_sha256':SHA,'configuration':verify(a),'pmg_checks':pmg,'sync_checks':sync,'start_while_waiting':True},indent=2));print('Validation PASS',flush=True)
