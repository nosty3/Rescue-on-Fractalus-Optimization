"""Fractalus: wspólne narzędzia pomiaru (protokół jak w repo nosty3: zimny start, START po N ramkach
menu, pierwsze wejście $A32E, 170 ramek rozgrzewki, licznik gotowych obrazów w $B516, czas z taktów)."""
import os, re, subprocess, sys, threading, hashlib, json
from paths import WORK, BRIDGE
BRIDGE_DIR = BRIDGE
sys.path.insert(0, f"{BRIDGE_DIR}/sdk/python")
from altirra_bridge import AltirraBridge

REPO = f"{WORK}/repo"
ORIGINAL = f"{REPO}/original/Rescue on Fractalus!.rom"
V101 = f"{REPO}/optimized version/Rescue on Fractalus! - optimized 128KB.car"
FREQ = {"pal": 3546895 / 2, "ntsc": 3579545 / 2}


class Emu:
    def __init__(self, video="pal", exe=None):
        self.video = video
        self.exe = exe or f"{BRIDGE_DIR}/AltirraBridgeServer.exe"

    def __enter__(self):
        self.p = subprocess.Popen([self.exe, "--bridge"], stderr=subprocess.PIPE, text=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
        token = None
        while token is None:
            line = self.p.stderr.readline()
            if not line:
                raise RuntimeError("bridge exited")
            m = re.search(r"token-file:\s*(\S+)", line, re.I)
            if m:
                token = m.group(1)
        threading.Thread(target=lambda: [None for _ in self.p.stderr], daemon=True).start()
        self.a = AltirraBridge.from_token_file(token)
        a = self.a
        a.pause(); a.bp_clear_all(); a.consol(); a.joy(0, "center")
        a.config("addons", "stock"); a.config("machine", "800XL"); a.config("memory", "64K")
        a.config("video", self.video); a.config("history", "off")
        return self

    def __exit__(self, *exc):
        try:
            self.a.quit()
        except Exception:
            pass
        try:
            self.p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.p.kill()


def enter_flight(a, path, menu_frames):
    """Zimny start, menu, START, pierwsze $A32E. Zwraca hash RAM-u na wejściu."""
    a.boot(path)
    a.frame(menu_frames)
    a.bp_set(0xA32E); a.consol(start=True); a.frame(4000)
    assert a.regs()["PC"] == "$a32e", a.regs()
    a.consol(); a.bp_clear_all()
    return hashlib.sha256(bytes(a.memdump(0, 0x8000))).hexdigest()


def measure(a, video, seconds=60, warmup=170, on_event=None):
    """Liczy pełne odstępy między kolejnymi $B516 (gotowy obraz w VBI). Zwraca dict z fps."""
    freq = FREQ[video]
    a.frame(warmup)
    a.bp_set(0xB516); a.frame(200)
    assert a.regs()["PC"] == "$b516"
    start = a.clock()["tick"]; events = [0]; end = None
    while events[-1] < seconds * freq:
        a.frame(200)
        packed = a.eval_expr("pc+65536*db($4a)")
        mode, pc = packed >> 16, packed & 0xFFFF
        tick = a.clock()["tick"] - start
        if mode != 2:
            end = dict(mode=mode, pc=pc, at=tick / freq)
            break
        assert pc == 0xB516, (hex(pc),)
        events.append(tick)
        if on_event:
            on_event(a, tick)
    a.bp_clear_all()
    n = len(events) - 1
    return dict(fps=n * freq / events[-1] if n else 0, intervals=n, seconds=events[-1] / freq,
                end=end, events=events)
