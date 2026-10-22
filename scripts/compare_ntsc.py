"""Paired NTSC benchmark, original and v9 from one safe original entry state."""
from ntsc_v9_common import *
import argparse
p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','benchmark']);args=p.parse_args()
OUT=ROOT/'results/ntsc_comparison';OUT.mkdir(exist_ok=True)
ORIGINAL=ROOT/'Rescue on Fractalus!.rom'
if not ORIGINAL.exists():ORIGINAL=ROOT/'original/Rescue on Fractalus!.rom'
ORIG_SHA=hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
a=connect()
if args.action=='prepare':
 a.bp_clear_all();a.consol();a.joy(0,'center');a.config('addons','stock');a.config('machine','800XL');a.config('memory','64K');a.config('video','ntsc');a.config('history','off');a.boot(str(ORIGINAL));advance(a,3000)
 a.bp_set(0xa32e);a.consol(start=True);a.frame(4000);a.consol();assert a.regs()['PC']=='$a32e' and a.cart_info()['bank']==2;assert a.peek(0x4a,1)[0]==2
 a.bp_clear_all();mem=a.memdump(0,65536);(OUT/'original-entry.bin').write_bytes(mem);a.state_save(str(OUT/'common-entry.altstate2'))
 assert mem[0x8000:0xa000]==ORIGINAL.read_bytes()[0x4000:0x6000]
 (OUT/'preparation.json').write_text(json.dumps({'original_sha256':ORIG_SHA,'v9_sha256':SHA,'configuration':verify(a),'entry':a.regs(),'bank':a.cart_info(),'ready':mem[0x42],'state_sha256':hashlib.sha256((OUT/'common-entry.altstate2').read_bytes()).hexdigest(),'method':'Original cold start, stopped at first main flight loop A32E. Same state for both variants. V9 replaces only its documented 215-byte RAM routine before execution.'},indent=2));print('Common NTSC entry prepared',a.regs(),flush=True)
else:
 rows=[];mem=(OUT/'original-entry.bin').read_bytes();meta=json.loads((ROOT/'results/opt14/pmg_trial-build.json').read_text());assert len(meta['ram_patches'])==1
 for variant,path in [('original',ORIGINAL),('v9',CART)]:
  rom=path.read_bytes() if variant=='original' else path.read_bytes()[16:]
  a.bp_clear_all();a.boot(str(path));a.frame(2)
  for scenario,direction,thrust in [('straight','center',False),('right','right',False),('left','left',False),('fast_right','right',True)]:
   a.bp_clear_all();a.state_load(str(OUT/'common-entry.altstate2'));verify(a);assert a.regs()['PC']=='$a32e';assert a.cart_info()['bank']==2
   assert a.peek(0x8000,8192)==rom[0x4000:0x6000];assert a.peek(0xa000,8192)==rom[-8192:]
   expected=bytearray(mem[:0x8000])
   if variant=='v9':
    for patch in meta['ram_patches']:
     code=bytes.fromhex(patch['hex']);a.memload(patch['address'],code);expected[patch['address']:patch['address']+len(code)]=code
   assert a.memdump(0,0x8000)==expected
   a.joy(0,'center');advance(a,120);a.joy(0,direction)
   if thrust:a.consol(option=True);a.frame(45);a.consol()
   advance(a,50);a.bp_set(0xb516);a.frame(200);assert a.regs()['PC']=='$b516';start=a.clock()['tick'];events=[start]
   while events[-1]-start<3600*FRAME_TICKS:
    a.frame(200);assert a.regs()['PC']=='$b516';assert a.peek(0x4a,1)[0]==2;events.append(a.clock()['tick'])
   a.bp_clear_all();verify(a)
   if variant=='original':assert a.peek(0x7eeb,215)==mem[0x7eeb:0x7fc2]
   else:signature(a)
   ticks=events[-1]-start;n=len(events)-1;row={'variant':variant,'scenario':scenario,'intervals':n,'ticks':ticks,'seconds':ticks/FREQ,'fps':n*FREQ/ticks,'mode':2};rows.append(row)
   (OUT/f'{variant}-{scenario}-ticks.json').write_text(json.dumps(events));(OUT/f'{variant}-{scenario}.png').write_bytes(a.screenshot());(OUT/'benchmark.json').write_text(json.dumps({'original_sha256':ORIG_SHA,'v9_sha256':SHA,'clock_hz':FREQ,'minimum_frames':3600,'rows':rows},indent=2));print(row,flush=True)
 print('Paired benchmark PASS',flush=True)
