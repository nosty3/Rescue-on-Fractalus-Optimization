"""Check v13 sound/geometry banking, optionally reproducing sustained native turns.

No FPS measurements or private RAM fixtures. Requires py65; --native also
requires AltirraBridge (FRACTALUS_BRIDGE_DIR or tools/bridge).
"""
from pathlib import Path
import argparse, dis, hashlib, json, random, sys
from concurrent.futures import ThreadPoolExecutor

R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'arc/up38/tools'))
from fxsim import Machine

def image(kb):
    return (R/f'optimized version/Rescue on Fractalus! - optimized {kb}KB.rom').read_bytes()

def dispatcher(rom,value):
    ram=bytearray(65536);ram[0x80]=value
    m=Machine(rom,ram,2,dict(a=0,x=7,y=9,p=0x31,sp=255));c=m.cpu;c.pc=0x9863
    for _ in range(20):
        if c.pc==0x9890:
            assert c.a=={0x55:10,0x82:11,0xaf:12}.get(value,13),(value,c.a)
            assert (c.x,c.y,c.sp,m.mem.bank)==(7,9,255,2)
            return
        assert m.mem[c.pc]!=0,(value,'BRK',hex(c.pc))
        c.step()
    raise AssertionError(('dispatcher did not return',value,hex(c.pc)))

def mixer(rom,ram,pc):
    m=Machine(rom,ram,2,dict(a=37,x=7,y=9,p=0x31,sp=255));c=m.cpu
    c.stPushWord(0x3fff);c.pc=pc
    for _ in range(10000):
        if c.pc==0x4000:return bytes(m.mem[:0x8000]),tuple(getattr(c,k) for k in ('a','x','y','p','sp'))
        assert m.mem[c.pc]!=0,('BRK',hex(c.pc))
        c.step()
    raise AssertionError(('mixer did not return',hex(c.pc)))

def static():
    expected=json.loads((R/'src/v13/expected.json').read_text())
    original=(R/'original/Rescue on Fractalus!.rom').read_bytes();roms={kb:image(kb) for kb in (512,1024)}
    for kb,rom in roms.items():
        assert hashlib.sha256(rom).hexdigest()==expected[str(kb)]
        car=(R/f'optimized version/Rescue on Fractalus! - optimized {kb}KB.car').read_bytes()
        assert car[:4]==b'CART' and car[16:]==rom
        assert int.from_bytes(car[8:12],'big')==sum(rom)&0xffffffff
        assert rom[0x5c79:0x5c7c]==bytes.fromhex('4cef9f')
        assert rom[0x5fef:0x5ff2]==bytes.fromhex('8d00d5')
        assert rom[5*8192+0x1ff2:5*8192+0x1ff5]==bytes.fromhex('4c7993')
        assert rom[0x5873:0x587b]==bytes.fromhex('4c9098a90a4c9098')
        for value in range(256):dispatcher(rom,value)
    rng=random.Random(20261029)
    for n in range(1024):
        ram=bytearray(65536);ram[0x650:0x740]=rng.randbytes(0xf0);ram[0x715]=rng.randrange(1,13)
        pc=(0xbb19,0xbb3e)[n&1];reference=mixer(original,ram,pc)
        for rom in roms.values():assert mixer(rom,ram,pc)==reference,(n,hex(pc))
    # Minimal causal regression: occupied channel 11 used to execute BRK $9e51.
    ram=bytearray(65536);ram[0x710]=2;ram[0x676]=7
    for rom in roms.values():assert mixer(rom,ram,0xbb19)==mixer(original,ram,0xbb19)
    return dict(dispatcher_inputs_per_car=256,mixer_cases_per_car=1024,reference='original ROM',channel11_regression=True)

def native(job):
    from flight_common import pal
    kb,video=job;folder=R/'build/v13-sound-fix-native';folder.mkdir(parents=True,exist_ok=True)
    with pal.Emulator(folder,f'{kb}-{video}') as e:
        a=e.a;a.config('machine','130XE');a.config('memory','1088k');a.config('video',video)
        a.boot(str(R/f'optimized version/Rescue on Fractalus! - optimized {kb}KB.car'))
        a.frame(3009);a.bp_set(0xa32e);a.consol(start=True);a.frame(4000)
        assert a.regs()['PC']=='$a32e';a.consol();a.bp_clear_all()
        frame_ticks=114*(312 if video=='pal' else 262)
        def advance(n):
            before=a.clock()['tick'];a.frame(n);delta=a.clock()['tick']-before
            assert abs(delta-n*frame_ticks)<=frame_ticks,('CPU stopped',kb,video,n,delta,a.regs())
            assert int(a.regs()['PC'][1:],16)>=0x4000,a.regs()
            assert a.peek(0x4a,1)[0]==2,a.regs()
        for joy in ('e','w','n','s'):a.joy(0,joy);advance(200)
        a.key_raw('PLUS');advance(8);a.key_raw('PLUS',down=False);advance(30)
        for joy in ('e','w'):
            a.joy(0,joy);before=a.peek(0x88,5)
            for _ in range(8):advance(100)
            assert before!=a.peek(0x88,5),('no movement',kb,video,joy)
            a.bp_set(0xb516);a.frame(200);assert a.regs()['PC']=='$b516';a.bp_clear_all()
    return dict(kb=kb,video=video,machine='130XE',memory_kb=1088,unchanged_map=True,clock_progress=True,render_presentations=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--native',action='store_true');args=p.parse_args()
    report={'version':'v13','static':static()}
    if args.native:
        with ThreadPoolExecutor(max_workers=4) as pool:report['native']=list(pool.map(native,[(k,v) for k in (512,1024) for v in ('pal','ntsc')]))
    dest=R/'build/v13-sound-fix-tests.json';dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
