from session import *
import hashlib
OUT=ROOT/'results/ntsc_v9';OUT.mkdir(exist_ok=True)
CART=ROOT/'build/reference-v9.car'  # Created by rebuild_current.py; historical v9 tools.
SHA='0c8226e1f58ad26b2a103cbf59c4b8b23fdb87caac0e22f2586a83513a859880'
assert hashlib.sha256(CART.read_bytes()[16:]).hexdigest()==SHA
FREQ=3579545/2;FRAME_TICKS=114*262
def verify(a):
 cfg=a.config();assert cfg['video']=='ntsc' and cfg['memory']=='64K' and cfg['machine']=='800XL',cfg
 assert not any(cfg[k] for k in ('rapidus','vbxe','u1mb'))
 return cfg
def setup(a):
 a.bp_clear_all();a.consol();a.joy(0,'center');a.config('addons','stock');a.config('machine','800XL');a.config('memory','64K');a.config('video','ntsc');a.config('history','off');a.boot(str(CART));verify(a)
def load(a,name='flight'):
 a.bp_clear_all();a.state_load(str(OUT/f'{name}.altstate2'));verify(a)
def signature(a):
 meta=json.loads((ROOT/'results/opt14/pmg_trial-build.json').read_text());code=bytes.fromhex(meta['ram_patches'][0]['hex'])
 smc={v+(2 if k in ('high0','low0','high1','low1') else 1) for k,v in json.loads((ROOT/'results/opt14/opt14_interpolation-build.json').read_text())['smc_labels'].items()}
 actual=a.peek(0x7eeb,len(code));assert all(actual[i]==b for i,b in enumerate(code) if 0x7eeb+i not in smc)
def advance(a,n):
 t=a.clock()['tick'];a.frame(n);delta=a.clock()['tick']-t;assert abs(delta-n*FRAME_TICKS)<=FRAME_TICKS,(n,delta);verify(a);return delta
