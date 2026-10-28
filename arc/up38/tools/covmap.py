"""Pokrycie kodu z profilera Altirry (mostek z limitem dumpu podniesionym do 1M, G:/tmp/claude/atari/fractalus/bridge):
sesje boot -> menu -> START -> lot z losowym sterowaniem i strzelaniem; profiler w trybie insns zrzucany co CHUNK
klatek. Klucz miejsca: bank kartridża dla okna $8000-$9FFF (profiler podaje gaddr $80bb_Axxx: bank bb, przesunięcie
w oknie), 'cpu' dla reszty (RAM, stały bank $A000-$BFFF). OS ROM pomijany.
Wynik dopisywany (unia) do OUT.json: {"bank:2": {"8123": liczba, ...}, "cpu": {...}}.
Użycie: covmap.py ROM OUT.json SEED PRESSES FRAMES [VIDEO]"""
import sys, json, os, random
from paths import WORK
from fx import Emu

EXE = os.environ.get("ALTIRRA_BRIDGE_PROFILE_EXE", f"{WORK}/bridge/altirra-bridge-fed7854/AltirraBridgeServer.exe")
# serwer z PROFILE_DUMP do 1048576 wpisów (bridge_commands_debug2.cpp: "if (top > 4096)" podniesione)
rom, out = sys.argv[1], sys.argv[2]
seed, presses, frames = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
video = sys.argv[6] if len(sys.argv) > 6 else "pal"
CHUNK = 50
rnd = random.Random(seed)
cov = json.load(open(out)) if os.path.exists(out) else {}


def num(v):
    return int(v.lstrip("$"), 16) if isinstance(v, str) else v


def absorb(a):
    a.profile_stop()
    d = a.profile_dump(top=1048576)
    for h in d["hot"]:
        g = num(h["gaddr"]); ad = num(h["addr"]); hi = g >> 16
        if hi >> 8 == 0x80:
            key = f"bank:{hi & 0xFF}"; ad = 0x8000 | (ad & 0x1FFF)
        elif hi == 0:
            key = "cpu"
        else:
            continue
        sp = cov.setdefault(key, {})
        sp[f"{ad:04x}"] = sp.get(f"{ad:04x}", 0) + h["insns"]
    a.profile_start("insns")


with Emu(video, exe=EXE) as e:
    a = e.a
    a.boot(rom)
    a.profile_start("insns")
    f = 0; started = False
    menu = 600 + rnd.randrange(3000)
    while f < frames:
        if not started and f >= menu:
            for _ in range(presses):
                a.joy(0, "n"); a.frame(30); a.joy(0, "c"); a.frame(30); f += 60
            a.consol(start=True); a.frame(100); a.consol(); f += 100
            started = True
        if started:
            a.joy(0, rnd.choice(["c", "c", "n", "s", "e", "w", "ne", "nw", "se", "sw"]), fire=rnd.random() < 0.4)
            if rnd.random() < 0.01:
                a.key(rnd.choice(["Space", "Esc", "1", "2", "3", "A", "Return"]))
        a.frame(CHUNK); f += CHUNK
        absorb(a)
    a.profile_stop()

json.dump(cov, open(out, "w"))
print({k: len(v) for k, v in sorted(cov.items())})
