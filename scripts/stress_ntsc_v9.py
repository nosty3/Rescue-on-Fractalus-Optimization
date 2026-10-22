from ntsc_v9_common import *
a=connect();rows=[]
def record(label,frames):
 ticks=advance(a,frames);signature(a);row={'name':label,'frames':frames,'ticks':ticks,'mode':a.peek(0x4a,1)[0],'bank':a.cart_info()['bank']};rows.append(row);(OUT/f'stress-{label}.png').write_bytes(a.screenshot());print(row,flush=True)
setup(a);record('cold-title',3600);a.consol(start=True);advance(a,60);a.consol();record('cold-flight',2400);assert a.peek(0x4a,1)[0]==2
for state in ('select7','select15'):
 for direction in ('left','right','center'):
  load(a,state);a.joy(0,direction);record(state+'-'+direction,3600)
for bank,entry in [(5,0x982f),(6,0x9863),(8,0x9863),(9,0x930d),(10,0x800f),(11,0x800f),(12,0x800f),(13,0x800f),(14,0x7f20)]:
 load(a);a.joy(0,'center')
 if bank in (10,11,12,13):
  a.bp_set(0x835e)
  for _ in range(200):
   a.frame(200)
   if a.cart_info()['bank']==2 and a.regs()['PC']=='$835e':break
  else:raise AssertionError('geometry entry')
  table=(0x9a55,0x9a82,0x9aaf,0x9adc)[bank-10];a.memload(0x80,bytes([table&255,table>>8]));a.bp_clear_all()
 a.bp_set(entry)
 for _ in range(200):
  a.frame(200)
  if a.cart_info()['bank']==bank and a.regs()['PC']==f'${entry:04x}':break
 else:raise AssertionError(('bank not reached',bank))
 a.bp_clear_all();a.consol(start=True);advance(a,60);a.consol();record(f'start-bank{bank}',1800);assert a.peek(0x4a,1)[0]==2
setup(a);advance(a,3600);a.consol(start=True);advance(a,60);a.consol();record('restart-flight',2400);assert a.peek(0x4a,1)[0]==2
(OUT/'stress.json').write_text(json.dumps({'result':'pass','rom_sha256':SHA,'configuration':verify(a),'checks':rows,'geometry_bank_selection':'Explicit test input forces all four orientations for START coverage.'},indent=2));print('Stress PASS',flush=True)
