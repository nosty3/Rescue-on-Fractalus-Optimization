"""Isolated emulator lifecycle and instrumented native-boot flight measurements."""
from pal_v9_common import *
import os, subprocess, time
from altirra_bridge import AltirraBridge

EXE=next((ROOT/'tools/bridge').glob('*/AltirraBridgeServer.exe'))
ORIGINAL=ROOT/'Rescue on Fractalus!.rom'
if not ORIGINAL.exists(): ORIGINAL=ROOT/'original/Rescue on Fractalus!.rom'
assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()=='1eb18e2a1ff31f43871a5e4e21e73f61b7659177d33d2cdbb29f36530b9f4d68'

class Emulator:
    def __init__(self, folder, name):
        self.folder=folder; self.name=name
    def __enter__(self):
        env=os.environ.copy(); env['TEMP']=env['TMP']=str(ROOT/'tools')
        self.log=(self.folder/f'{self.name}-server.log').open('wb')
        self.p=subprocess.Popen([str(EXE),'--bridge=tcp:127.0.0.1:0'],cwd=ROOT,env=env,
            stdout=self.log,stderr=self.log,creationflags=subprocess.CREATE_NO_WINDOW)
        token=ROOT/'tools'/f'altirra-bridge-{self.p.pid}.token'
        for _ in range(200):
            if token.exists():
                try:
                    self.a=AltirraBridge.from_token_file(str(token)); break
                except Exception: pass
            if self.p.poll() is not None: raise RuntimeError('Emulator exited during startup')
            time.sleep(.05)
        else: raise RuntimeError('Emulator startup timeout')
        a=self.a; a.pause(); a.bp_clear_all(); a.consol(); a.joy(0,'center')
        a.config('addons','stock'); a.config('machine','800XL'); a.config('memory','64K')
        a.config('video','pal'); a.config('history','off')
        return self
    def __exit__(self,*exc):
        try: self.a.quit()
        finally:
            try: self.p.wait(timeout=10)
            except subprocess.TimeoutExpired: self.p.terminate(); self.p.wait(timeout=10)
            self.log.close()

def entry(a,variant,delay,folder,name):
    a.bp_clear_all(); a.consol(); a.joy(0,'center')
    path=ORIGINAL if variant=='original' else CART
    a.boot(str(path)); a.frame(delay); verify(a)
    a.bp_set(0xa32e); a.consol(start=True); a.frame(4000)
    regs=a.regs(); assert regs['PC']=='$a32e',regs
    a.consol(); a.bp_clear_all()
    assert a.cart_info()['bank']==2 and a.peek(0x4a,1)[0]==2
    rom=path.read_bytes() if variant=='original' else path.read_bytes()[16:]
    assert a.peek(0x8000,8192)==rom[0x4000:0x6000]
    assert a.peek(0xa000,8192)==rom[-8192:]
    ram=a.memdump(0,0x8000)
    (folder/f'{name}-entry.bin').write_bytes(ram)
    return dict(regs=regs,clock=a.clock(),config=a.config(),cart=a.cart_info(),
        terrain_sha256=hashlib.sha256(ram[0x900:0xa00]).hexdigest(),
        ram_sha256=hashlib.sha256(ram).hexdigest(),zero_page_hex=ram[:256].hex(),
        game_data_sha256=hashlib.sha256(ram[0x200:0x3000]).hexdigest())

def measure(a,variant,folder,name,seconds=(15,)):
    advance(a,170)
    (folder/f'{name}-after-warmup.bin').write_bytes(a.memdump(0,0x8000))
    a.bp_set(0xb516); a.frame(200); assert a.regs()['PC']=='$b516'
    start=a.clock()['tick']; events=[0]; checkpoints={}; modes=set(); termination=None
    a.watch_set(0x4a,mode='w')
    while events[-1]<max(seconds)*FREQ:
        a.frame(200)
        # One read-only expression checks the same PC/mode invariant together.
        packed=a.eval_expr('pc+65536*db($4a)'); mode=packed>>16;pc=packed&65535
        tick=a.clock()['tick']-start
        if mode!=2:
            termination=dict(mode=mode,pc=f'${pc:04x}',elapsed_seconds=tick/FREQ,
                last_completed_image_seconds=events[-1]/FREQ)
            assert len(events)>1,(name,'No measurable flight intervals')
            break
        assert pc==0xb516,(name,a.regs())
        modes.add(2)
        events.append(tick)
        for sec in seconds:
            if str(sec) not in checkpoints and events[-1]>=sec*FREQ:
                n=len(events)-1; ticks=events[-1]
                checkpoints[str(sec)]=dict(intervals=n,ticks=ticks,seconds=ticks/FREQ,fps=n*FREQ/ticks,complete_window=True)
    if termination:
        n=len(events)-1;ticks=events[-1]
        for sec in seconds:
            if str(sec) not in checkpoints:
                checkpoints[str(sec)]=dict(intervals=n,ticks=ticks,seconds=ticks/FREQ,fps=n*FREQ/ticks,complete_window=False)
    a.bp_clear_all(); verify(a)
    if variant=='v9': signature(a)
    (folder/f'{name}-events.json').write_text(json.dumps(events))
    (folder/f'{name}-end.bin').write_bytes(a.memdump(0,0x8000))
    return dict(checkpoints=checkpoints,events_sha256=hashlib.sha256(json.dumps(events).encode()).hexdigest(),modes=list(modes),termination=termination)
