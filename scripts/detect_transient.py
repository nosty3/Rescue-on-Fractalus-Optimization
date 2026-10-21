from opt14_common import *
from PIL import Image,ImageChops
import io,argparse
p=argparse.ArgumentParser();p.add_argument('variant');p.add_argument('--frames',type=int,default=600);args=p.parse_args();OUT=ROOT/'results/buffer_race'
a=connect();a.bp_clear_all();a.boot(str(ROOT/f'build/{args.variant}.car'));a.frame(2);a.state_load(str(ROOT/'results/flying.altstate2'));patch_state(a,args.variant);a.joy(0,'right');a.frame(50)
last=[];found=[];changes=[]
for frame in range(args.frames):
 a.frame(1);png=a.screenshot();im=Image.open(io.BytesIO(png)).convert('RGB').crop((0,40,300,134));last.append((png,im))
 if len(last)>3:last.pop(0)
 if len(last)>=2:
  box=ImageChops.difference(last[-2][1],last[-1][1]).getbbox()
  if box:
   changes.append({'frame':frame,'bbox':box})
   if box[2]<170 and box[3]-box[1]>5:
    print('LEFT',frame,box,flush=True)
    for k,(data,_) in enumerate(last[-2:]):(OUT/f'{args.variant}-left-{frame}-{k}.png').write_bytes(data)
 if len(last)==3 and last[0][1].tobytes()==last[2][1].tobytes() and last[0][1].tobytes()!=last[1][1].tobytes():
  box=ImageChops.difference(last[0][1],last[1][1]).getbbox();row={'frame':frame-1,'difference_bbox_in_crop':box};found.append(row)
  if len(found)<=4:
   for k,(data,_) in enumerate(last):(OUT/f'{args.variant}-transient{len(found)}-{k}.png').write_bytes(data)
  print(row,flush=True)
(OUT/f'{args.variant}-transients.json').write_text(json.dumps({'variant':args.variant,'frames':args.frames,'crop':[0,40,300,134],'one_frame_transients':found,'changes':changes},indent=2));print('DONE',args.variant,len(found),'changes',len(changes),flush=True)
