from opt14_common import *
import argparse
p=argparse.ArgumentParser();p.add_argument('--variant',default='v7_clipping');p.add_argument('--count',type=int,default=120);args=p.parse_args()
OUT=ROOT/'results/buffer_race';OUT.mkdir(exist_ok=True)
a=connect();a.bp_clear_all();path=ROOT/f'build/{args.variant}.car' if args.variant!='original' else ROOT/'Rescue on Fractalus!.rom';a.boot(str(path));a.frame(2);a.state_load(str(ROOT/'results/flying.altstate2'));patch_state(a,args.variant);a.joy(0,'right');a.frame(50)
a.bp_set(0x9214);rows=[]
for i in range(args.count):
 for _ in range(200):
  a.frame(100);r=a.regs()
  if r['PC']=='$9214' and a.cart_info()['bank']==2:break
 else:raise AssertionError(('clear entry',r,a.cart_info()))
 flag=a.peek(0x42,1)[0];hw=a.antic();row={'i':i,'clock':a.clock(),'x':r['X'],'ready':flag,'antic':hw};rows.append(row)
 if flag and hw['beam_y']<160 and not (OUT/f'{args.variant}-hazard.altstate2').exists():a.state_save(str(OUT/f'{args.variant}-hazard.altstate2'))
 if flag and hw['beam_y']<100 and not (OUT/f'{args.variant}-visible.altstate2').exists():a.state_save(str(OUT/f'{args.variant}-visible.altstate2'))
 if flag and hw['beam_y']<80 and not (OUT/f'{args.variant}-early.altstate2').exists():a.state_save(str(OUT/f'{args.variant}-early.altstate2'))
 if flag and not (OUT/f'{args.variant}-pending.altstate2').exists():
  a.state_save(str(OUT/f'{args.variant}-pending.altstate2'));(OUT/f'{args.variant}-pending.png').write_bytes(a.screenshot());(OUT/f'{args.variant}-dlist.json').write_text(json.dumps(a.dlist(),indent=2))
a.bp_clear_all();(OUT/f'{args.variant}-race.json').write_text(json.dumps(rows,indent=2));print({'variant':args.variant,'clear_entries':len(rows),'pending_presentation':sum(r['ready']!=0 for r in rows),'examples':[r for r in rows if r['ready']][:3]},flush=True)
