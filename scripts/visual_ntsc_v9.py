from ntsc_v9_common import *
from PIL import Image,ImageChops
import io
a=connect();load(a);a.joy(0,'right');previous=None;candidates=[]
for frame in range(1200):
 a.frame(1);png=a.screenshot();im=Image.open(io.BytesIO(png)).convert('RGB').crop((0,32,300,126))
 if frame%200==0:(OUT/f'visual-{frame}.png').write_bytes(png)
 if previous:
  box=ImageChops.difference(previous[1],im).getbbox()
  if box and box[2]<170 and box[3]-box[1]>5:
   candidates.append({'frame':frame,'bbox':box})
   if len(candidates)<=8:
    (OUT/f'visual-left-{len(candidates)}-before.png').write_bytes(previous[0]);(OUT/f'visual-left-{len(candidates)}-after.png').write_bytes(png)
 previous=(png,im)
verify(a);signature(a)
# Input smoke test: fire plus steering and speed control, without memory edits.
controls=[]
for direction in ('up','down','left','right'):
 load(a);a.joy(0,direction,fire=True);ticks=advance(a,1200);a.joy(0,'center');signature(a)
 controls.append({'direction':direction,'fire':True,'frames':1200,'ticks':ticks,'mode':a.peek(0x4a,1)[0]});(OUT/f'controls-{direction}.png').write_bytes(a.screenshot())
(OUT/'visual-controls.json').write_text(json.dumps({'rom_sha256':SHA,'continuous_frames':1200,'left_change_candidates':candidates,'note':'Left-only changes also include valid terrain/object changes; this detector is not an automatic artifact pass/fail test.','controls':controls,'configuration':verify(a)},indent=2));print('Visual capture and controls done',len(candidates),controls,flush=True)
